import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from src.core.config import settings
from src.core.logging import logger
from src.services.affordability_service import AffordabilityService
from src.services.scoring_service import ScoringService
from src.schemas.credit_memo import CreditMemoOutput


class ClaudeAgentAdapter:
    """
    Adapter wrapper around the Anthropic Claude API to execute credit assessments.
    Incorporates PII pseudonymisation prior to data transit,
    schema enforcement, and de-pseudonymisation of outcomes.
    
    If ANTHROPIC_API_KEY or CLAUDE_MODEL is not configured, falls back
    to a synthetic canned memo so the demo operates out-of-the-box.
    """
    def __init__(self, session_key: Optional[bytes] = None):
        self.pii_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
        self.counters: Dict[str, int] = {}
        
    def pseudonymise_text(self, real_value: str, entity_type: str) -> str:
        """
        Replace sensitive PII strings with deterministic synthetic tokens (e.g. DIRECTOR_001).
        Registers known identifiers for replacement before LLM transit.
        """
        if not real_value:
            return ""
        if real_value in self.pii_map:
            return self.pii_map[real_value]
            
        count = self.counters.get(entity_type, 0) + 1
        self.counters[entity_type] = count
        
        pseudonym = f"{entity_type}_{count:03d}"
        self.pii_map[real_value] = pseudonym
        self.reverse_map[pseudonym] = real_value
        return pseudonym

    def depseudonymise_text(self, text: str) -> str:
        """
        Replace pseudonym tokens back with original values after AI analysis.
        """
        if not text:
            return ""
        return self._transform(text, restore=True)

    def _generate_canned_memo(
        self,
        clean_company: str,
        clean_reg: str,
        applicant_data: Dict[str, Any],
        financial_data: Dict[str, Any]
    ) -> str:
        """
        Generates a comprehensive, structured credit memo JSON conforming to CreditMemoOutput.
        Uses pseudonymised tokens so the de-pseudonymisation cycle is exercised.
        """
        loan_req = applicant_data.get("loan_request", {})
        fin = applicant_data.get("financial_profile", {})
        
        req_amount = float(loan_req.get("amount_requested", 250000.00))
        req_tenor = int(loan_req.get("tenor_months_requested", 24))
        loan_type = loan_req.get("loan_type", "WORKING_CAPITAL")
        
        avg_revenue = float(fin.get("avg_monthly_revenue", 185000.00))
        avg_expenses = float(fin.get("avg_monthly_expenses", 128000.00))
        debt_service = float(fin.get("existing_monthly_debt", 11800.00))
        net_cash = avg_revenue - avg_expenses - debt_service
        
        proposed_instalment = float(fin["proposed_monthly_instalment"])
        dti_before = round(debt_service / avg_revenue, 3) if avg_revenue else None
        dti_after = round((debt_service + proposed_instalment) / avg_revenue, 3) if avg_revenue else None
        ndi_after = round(net_cash - proposed_instalment, 2)
        
        service = AffordabilityService()
        affordability_status, _ = service.assess_affordability(max(0, net_cash), proposed_instalment)
        
        canned_data = {
            "memo_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "claude_model": "canned-demo",
            "generation_mode": "CANNED",
            "illustrative": True,
            "prompt_version": "v1.2.0-structured-memo",
            "financial_summary": {
                "average_monthly_revenue": avg_revenue,
                "annualised_revenue": round(avg_revenue * 12, 2),
                "revenue_trend": "STABLE",
                "revenue_trend_percentage_12m": 0.0,
                "average_monthly_expenses": avg_expenses,
                "average_monthly_debt_service": debt_service,
                "average_monthly_net_cashflow": round(net_cash, 2),
                "months_negative_balance": 0,
                "pays_vat": None,
                "pays_paye": None
            },
            "affordability_assessment": {
                "assessed_monthly_income": avg_revenue,
                "income_basis": f"12-month synthetic fixture for {clean_company} (Reg: {clean_reg}).",
                "total_operating_expenses": avg_expenses,
                "existing_debt_service": debt_service,
                "net_disposable_income": round(net_cash, 2),
                "proposed_monthly_instalment": proposed_instalment,
                "ndi_after_instalment": ndi_after,
                "dti_ratio_before": dti_before,
                "dti_ratio_after": dti_after,
                "affordability_outcome": affordability_status,
                "stress_test_10pct": "",
                "stress_test_20pct": "",
                "stress_test_30pct": ""
            },
            "risk_factors": [{
                "factor": "Synthetic evidence only", "severity": "HIGH",
                "evidence": "All inputs are fictional fixtures; scores and rates are illustrative.",
                "mitigant": "Human review and independently verified data would be required for real use."
            }],
            "credlens_score": {
                "total": 0,  # Recalculated from illustrative components below.
                "band": "",
                "components": applicant_data["illustrative_score_components"],
                "top_positive_factors": [],
                "top_negative_factors": ["Component grades are preset in this fixture."],
            },
            "recommended_facility": {
                "recommended_amount": req_amount,
                "recommended_tenor_months": req_tenor,
                "recommended_loan_type": loan_type,
                "recommended_rate_band_min_pct": 14.50,
                "recommended_rate_band_max_pct": 18.25,
                "illustrative_rate_cap_pct": 28.50,
                "recommended_covenants": [
                    {
                        "covenant": "Minimum Debt Service Coverage Ratio (DSCR)",
                        "threshold": "1.30x",
                        "measurement": "Quarterly management accounts",
                        "breach_consequence": "100 bps margin step-up and review"
                    }
                ],
                "conditions_precedent": ["Human review of this illustrative memo"],
                "rationale": f"Example terms for {clean_company}. Amount and tenor mirror the fixture request. Affordability label: {affordability_status}. This demo issues no lending decision or offer."
            }
        }
        aff = canned_data["affordability_assessment"]
        for shock in (10, 20, 30):
            aff[f"stress_test_{shock}pct"] = service.run_stress_test(
                avg_revenue, avg_expenses, debt_service, proposed_instalment, shock / 100
            )
        score = canned_data["credlens_score"]
        scoring = ScoringService()
        score["total"] = scoring.calculate_score(score["components"])
        score["band"] = scoring.determine_risk_band(score["total"])
        return json.dumps(canned_data)

    def _register_identifiers(self, value, key=""):
        sensitive = {
            "company_name", "registration_number", "full_name", "first_names", "surname",
            "sa_id_number", "id_number", "primary_contact_email", "primary_contact_phone",
            "email", "phone", "line1", "city", "postal_code", "account_number", "creditor",
        }
        if isinstance(value, dict):
            for k, v in value.items():
                self._register_identifiers(v, k)
        elif isinstance(value, list):
            for item in value:
                self._register_identifiers(item, key)
        elif isinstance(value, str) and key in sensitive and value:
            self.pseudonymise_text(value, "ENTITY")

    def _transform(self, value, restore=False):
        if isinstance(value, dict):
            return {self._transform(k, restore): self._transform(v, restore) for k, v in value.items()}
        if isinstance(value, list):
            return [self._transform(v, restore) for v in value]
        if not isinstance(value, str):
            return value
        mapping = self.reverse_map if restore else self.pii_map
        if not mapping:
            return value
        pattern = "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True))
        return re.sub(pattern, lambda match: mapping[match.group()], value)

    async def analyze_credit(self, applicant_data: Dict[str, Any], financial_data: Dict[str, Any]):
        """Pseudonymise known fixture identifiers recursively; validate before restoration.

        This is not a general-purpose PII detector. The public API accepts fixture IDs only.
        Maps are request-local, including concurrent calls on the same adapter instance.
        """
        shield = ClaudeAgentAdapter()
        shield._register_identifiers(applicant_data)
        shield._register_identifiers(financial_data)
        clean_applicant = shield._transform(applicant_data)
        clean_financial = shield._transform(financial_data)
        clean_company = clean_applicant["company_name"]
        clean_reg = clean_applicant["registration_number"]
        raw = None
        input_tokens = output_tokens = 0
        if settings.ANTHROPIC_API_KEY and settings.CLAUDE_MODEL:
            try:
                import anthropic
                async with anthropic.AsyncAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY, timeout=45.0, max_retries=1
                ) as client:
                    response = await client.messages.create(
                        model=settings.CLAUDE_MODEL,
                        max_tokens=4096,
                        system=("Produce an ILLUSTRATIVE memo from synthetic data. Do not invent evidence. "
                                "Return only JSON conforming to this schema: "
                                + json.dumps(CreditMemoOutput.model_json_schema())),
                        messages=[{"role": "user", "content": json.dumps({
                            "applicant": clean_applicant, "financial": clean_financial
                        })}],
                    )
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                text = "".join(block.text for block in response.content if block.type == "text").strip()
                if text.startswith("```"):
                    text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                raw = CreditMemoOutput.model_validate_json(text).model_dump()
                raw.update(claude_model=settings.CLAUDE_MODEL, generation_mode="LIVE", illustrative=True)
            except Exception:
                # Never log provider errors: they may contain request text or credentials.
                logger.warning("Live memo unavailable or invalid; using the canned demo memo.")
        if raw is None:
            raw = json.loads(shield._generate_canned_memo(
                clean_company, clean_reg, clean_applicant, clean_financial
            ))
        validated = CreditMemoOutput.model_validate(raw).model_dump()
        restored = shield._transform(validated, restore=True)
        return CreditMemoOutput.model_validate(restored).model_dump(), input_tokens, output_tokens

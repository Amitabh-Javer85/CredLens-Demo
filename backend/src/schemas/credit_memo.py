from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict


class FinancialSummarySchema(BaseModel):
    average_monthly_revenue: float
    annualised_revenue: float
    revenue_trend: str  # GROWING, STABLE, DECLINING, VOLATILE
    revenue_trend_percentage_12m: float
    average_monthly_expenses: float
    average_monthly_debt_service: float
    average_monthly_net_cashflow: float
    months_negative_balance: int
    pays_vat: Optional[bool]
    pays_paye: Optional[bool]


class AffordabilitySchema(BaseModel):
    assessed_monthly_income: float
    income_basis: str
    total_operating_expenses: float
    existing_debt_service: float
    net_disposable_income: float
    proposed_monthly_instalment: float
    ndi_after_instalment: float
    dti_ratio_before: Optional[float]
    dti_ratio_after: Optional[float]
    affordability_outcome: str  # AFFORDABLE, BORDERLINE, UNAFFORDABLE
    stress_test_10pct: str  # SURVIVES, BORDERLINE, FAILS
    stress_test_20pct: str
    stress_test_30pct: str


class RiskFactorSchema(BaseModel):
    factor: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    evidence: str
    mitigant: str


class ScoreComponentsSchema(BaseModel):
    cash_flow_stability: int
    revenue_trend: int
    credit_behaviour: int
    business_legitimacy: int
    sector_risk: int
    management_quality: int


class ScoreSchema(BaseModel):
    total: int = Field(..., ge=0, le=1000)
    band: str  # LOW_RISK, etc.
    components: ScoreComponentsSchema
    top_positive_factors: List[str]
    top_negative_factors: List[str]


class CovenantSchema(BaseModel):
    covenant: str
    threshold: str
    measurement: str
    breach_consequence: str


class FacilityRecommendationSchema(BaseModel):
    recommended_amount: float
    recommended_tenor_months: int
    recommended_loan_type: str
    recommended_rate_band_min_pct: float
    recommended_rate_band_max_pct: float
    illustrative_rate_cap_pct: float
    recommended_covenants: List[CovenantSchema]
    conditions_precedent: List[str]
    rationale: str


class CreditMemoOutput(BaseModel):
    illustrative: bool = True
    generation_mode: str = "CANNED"
    memo_version: int = 1
    generated_at: str
    claude_model: str
    prompt_version: str
    
    financial_summary: FinancialSummarySchema
    affordability_assessment: AffordabilitySchema
    risk_factors: List[RiskFactorSchema]
    credlens_score: ScoreSchema
    recommended_facility: FacilityRecommendationSchema
    
    @field_validator("credlens_score")
    @classmethod
    def validate_score(cls, v):
        if not (0 <= v.total <= 1000):
            raise ValueError("CredLens composite score must be between 0 and 1000")
        return v

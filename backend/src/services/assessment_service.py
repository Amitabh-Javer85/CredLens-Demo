"""Shared synthetic pipeline for CLI and background jobs."""
import asyncio
from src.adapters.cipc import CIPCAdapter
from src.adapters.claude_agent import ClaudeAgentAdapter
from src.adapters.transunion import TransUnionAdapter
from src.adapters.truid import TruIDAdapter
from src.adapters.worldcheck import WorldCheckAdapter
from src.data.synthetic_applicants import get_sample_applicant

async def assess_sample(applicant_id: str) -> dict:
    applicant = get_sample_applicant(applicant_id)
    company, bureau, transactions, screening = await asyncio.gather(
        CIPCAdapter().verify_company(applicant["registration_number"]),
        TransUnionAdapter().get_business_report(applicant["registration_number"]),
        TruIDAdapter().get_transaction_history(applicant_id),
        WorldCheckAdapter().screen_entity(applicant["company_name"], applicant["registration_number"]),
    )
    directors = await asyncio.gather(*[
        WorldCheckAdapter().screen_individual(d["full_name"], d["sa_id_number"])
        for d in applicant["directors"]
    ])
    memo, input_tokens, output_tokens = await ClaudeAgentAdapter().analyze_credit(
        applicant, {"summary": applicant["financial_profile"], "transactions": transactions}
    )
    return {
        "synthetic": True, "applicant_id": applicant_id, "integration_mode": "MOCK",
        "verification": {"company": company, "bureau": bureau, "screening": screening, "directors": directors},
        "transaction_count": len(transactions), "memo": memo,
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    }

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.logging import logger
from src.data.synthetic_applicants import SYNTHETIC_APPLICANTS


class BaseBureauAdapter(ABC):
    """Abstract interface for Credit Bureau enquiries."""
    
    @abstractmethod
    async def get_business_report(self, registration_number: str) -> Dict[str, Any]:
        """Retrieve commercial credit report."""
        pass

    @abstractmethod
    async def get_consumer_report(self, id_number: str) -> Dict[str, Any]:
        """Retrieve consumer credit report for director/guarantor."""
        pass


class MockTransUnionAdapter(BaseBureauAdapter):
    """
    Mock TransUnion Credit Bureau adapter returning synthetic commercial and consumer reports.
    """
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or "mock_bureau_user"

    async def get_business_report(self, registration_number: str) -> Dict[str, Any]:
        """
        Retrieves credit report for a commercial entity using synthetic profiles.
        """
        logger.info(f"[MOCK TRANSUNION] Retrieving commercial profile for reg: {registration_number}")
        
        # Match synthetic applicant if registered
        for applicant in SYNTHETIC_APPLICANTS.values():
            if applicant["registration_number"] == registration_number:
                bp = applicant["bureau_profile"]
                return {
                    "report_id": f"TU-BUS-{registration_number[-6:]}",
                    "subject": {
                        "registered_name": applicant["company_name"],
                        "registration_number": registration_number
                    },
                    "credit_score": {
                        "score": bp["commercial_score"],
                        "rating_band": bp["commercial_rating"],
                        "score_date": "2026-05-19"
                    },
                    "adverse_indicators": {
                        "judgments_count": bp["judgments"],
                        "default_listings_count": bp["defaults"],
                        "debt_review_status": "NONE"
                    },
                    "existing_debt_obligations": bp["existing_debt_facilities"]
                }
        
        raise ValueError("Unknown synthetic company")

    async def get_consumer_report(self, id_number: str) -> Dict[str, Any]:
        """
        Retrieves consumer credit report for director/guarantor.
        """
        logger.info(f"[MOCK TRANSUNION] Retrieving consumer profile for ID: {id_number[:6]}******")
        
        return {
            "report_id": f"TU-CON-MOCK-{id_number[:6]}",
            "credit_score": {
                "score": 710,
                "risk_category": "Good"
            },
            "has_adverse": False,
            "judgments": [],
            "defaults": []
        }


# Default alias for dependency injection
TransUnionAdapter = MockTransUnionAdapter

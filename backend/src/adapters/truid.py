from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from src.core.logging import logger
from src.data.synthetic_applicants import generate_synthetic_bank_statement


class BaseBankingAdapter(ABC):
    """Abstract interface for Open Banking data aggregation."""
    
    @abstractmethod
    async def get_transaction_history(self, session_token: str) -> List[Dict[str, Any]]:
        """Retrieve transactional records for an authorized banking profile."""
        pass


class MockTruIDAdapter(BaseBankingAdapter):
    """
    Mock Open Banking adapter returning synthetic 12-month commercial bank statements.
    """
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or "mock_truid_client"

    async def get_transaction_history(self, session_token: str) -> List[Dict[str, Any]]:
        """
        Retrieves 12 months of structured transactional records.
        Maps session token or default to synthetic applicant transactions.
        """
        logger.info(f"[MOCK TRUID] Ingesting bank statements for session: {session_token[:8] if session_token else 'default'}...")
        
        return generate_synthetic_bank_statement(applicant_key=session_token, months=12)


# Default alias for dependency injection
TruIDAdapter = MockTruIDAdapter

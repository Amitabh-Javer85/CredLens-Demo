from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.logging import logger


class BaseSanctionsAdapter(ABC):
    """Abstract interface for PEP and Sanctions compliance screening."""
    
    @abstractmethod
    async def screen_entity(self, name: str, registration_number: Optional[str] = None) -> Dict[str, Any]:
        """Screen business entity against sanctions watchlists."""
        pass

    @abstractmethod
    async def screen_individual(self, full_name: str, id_number: str) -> Dict[str, Any]:
        """Screen individual director against PEP and sanctions watchlists."""
        pass


class MockWorldCheckAdapter(BaseSanctionsAdapter):
    """
    Mock Refinitiv World-Check adapter returning synthetic sanctions and PEP screening responses.
    """
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key or "mock_key"

    async def screen_entity(self, name: str, registration_number: Optional[str] = None) -> Dict[str, Any]:
        """Screens a company against sanctions lists."""
        logger.info(f"[MOCK WORLD-CHECK] Screening business entity: {name}")
        return {
            "query": name,
            "status": "CLEAR",
            "matches_count": 0,
            "matches": []
        }

    async def screen_individual(self, full_name: str, id_number: str) -> Dict[str, Any]:
        """Screens director against PEP and sanctions watchlists."""
        logger.info(f"[MOCK WORLD-CHECK] Screening director: {full_name}")
        return {
            "query": {
                "name": full_name,
                "id_number": id_number
            },
            "status": "CLEAR",
            "matches_count": 0,
            "pep_hit": False,
            "sanctions_hit": False,
            "matches": []
        }


# Default alias for dependency injection
WorldCheckAdapter = MockWorldCheckAdapter

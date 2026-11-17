from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.core.logging import logger
from src.data.synthetic_applicants import SYNTHETIC_APPLICANTS


class BaseCIPCAdapter(ABC):
    """Abstract interface for CIPC company and director registration verification."""
    
    @abstractmethod
    async def verify_company(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """Verify legal status, company structure, and active directors."""
        pass


class MockCIPCAdapter(BaseCIPCAdapter):
    """
    Mock CIPC adapter returning realistic synthetic South African company registration records.
    """
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or "mock://cipc.internal"
        self.api_key = api_key or "mock-key"

    async def verify_company(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves company registration status from synthetic profiles or generates a synthetic result.
        """
        logger.info(f"[MOCK CIPC] Verifying registration number: {registration_number}")
        
        # Check if matches any synthetic test applicant
        for applicant in SYNTHETIC_APPLICANTS.values():
            if applicant["registration_number"] == registration_number:
                return {
                    "registration_number": applicant["registration_number"],
                    "company_name": applicant["company_name"],
                    "company_status": "Active / In Business",
                    "registration_date": "2021-04-12",
                    "company_type": applicant["company_type"],
                    "registered_address": applicant["registered_address"],
                    "directors": [
                        {
                            "first_names": d["full_name"].split()[0],
                            "surname": d["full_name"].split()[-1],
                            "id_number": d["sa_id_number"],
                            "status": "Active",
                            "appointment_date": "2021-04-12"
                        }
                        for d in applicant["directors"]
                    ]
                }
        
        raise ValueError("Unknown synthetic company")


def validate_sa_id(id_number: str) -> bool:
    """
    Validates a South African National ID number using the Luhn Algorithm.
    Checks length (13 digits), numeric characters, and checksum only.
    Demo identity markers deliberately fail this format check.
    """
    if not id_number or not isinstance(id_number, str) or len(id_number) != 13 or not id_number.isdigit():
        return False
        
    # Luhn algorithm
    digits = [int(char) for char in id_number]
    odd_sum = sum(digits[i] for i in range(0, 12, 2))
    
    even_str = "".join(str(digits[i] * 2) for i in range(1, 12, 2))
    even_sum = sum(int(char) for char in even_str)
    
    total = odd_sum + even_sum
    check_digit = (10 - (total % 10)) % 10
    
    return check_digit == digits[12]


# Default alias for easy dependency injection
CIPCAdapter = MockCIPCAdapter

from typing import Dict


class ScoringService:
    """
    Computes composite CredLens Score (0-1000) for SMB credit applications.
    
    NOTE: The following dimension weights and risk bands are purely ILLUSTRATIVE
    and provided for portfolio demonstration purposes only.
    """
    
    # ILLUSTRATIVE dimension weights (must sum to 1.0)
    DIMENSION_WEIGHTS = {
        "cash_flow_stability": 0.25,
        "revenue_trend": 0.20,
        "credit_behaviour": 0.25,
        "business_legitimacy": 0.10,
        "sector_risk": 0.10,
        "management_quality": 0.10,
    }

    def calculate_score(self, dimensions: Dict[str, int]) -> int:
        """
        Calculates the weighted score from dimension grades (each 0-100).
        Returns a final score scaled between 0 and 1000.
        """
        weighted_sum = 0.0
        for dim, weight in self.DIMENSION_WEIGHTS.items():
            grade = dimensions.get(dim, 0)
            weighted_sum += (grade * weight)
            
        # Scale to 1000
        total_score = int(weighted_sum * 10)
        return max(0, min(1000, total_score))

    def determine_risk_band(self, score: int) -> str:
        """
        Maps a score to an illustrative credit risk band.
        NOTE: Threshold values (750, 600, 400) are ILLUSTRATIVE sample values.
        """
        if score >= 750:
            return "LOW_RISK"
        elif score >= 600:
            return "MODERATE_RISK"
        elif score >= 400:
            return "HIGH_RISK"
        else:
            return "VERY_HIGH_RISK"

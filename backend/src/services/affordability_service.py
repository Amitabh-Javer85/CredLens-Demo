from typing import Dict, Any, Tuple


class AffordabilityService:
    """
    ILLUSTRATIVE affordability arithmetic, not legal compliance validation.
    Calculates monthly disposable income, assesses proposed facility affordability,
    and runs multi-level stress testing.
    """
    
    def calculate_disposable_income(
        self,
        gross_monthly_income: float,
        operating_expenses: float,
        existing_debt_service: float
    ) -> float:
        """
        Gross Income - Operating Expenses - Existing Debt Service = Net Disposable Income (NDI)
        """
        return max(0.0, gross_monthly_income - operating_expenses - existing_debt_service)

    def assess_affordability(
        self,
        ndi: float,
        proposed_instalment: float
    ) -> Tuple[str, float]:
        """
        Computes Debt-To-Income (DTI) impact and affordability flag.
        """
        dti_impact = proposed_instalment / ndi if ndi > 0 else 1.0
        
        # ILLUSTRATIVE 10% borderline threshold
        if ndi >= proposed_instalment:
            # Comfortably covers repayment
            outcome = "AFFORDABLE"
        elif (ndi * 1.1) >= proposed_instalment:
            # Repayment marginally exceeds disposable income
            outcome = "BORDERLINE"
        else:
            # Repayment exceeds the illustrative buffer
            outcome = "UNAFFORDABLE"
            
        return outcome, dti_impact

    def run_stress_test(
        self,
        gross_monthly_income: float,
        operating_expenses: float,
        existing_debt_service: float,
        proposed_instalment: float,
        stress_pct: float
    ) -> str:
        """
        Simulates debt serviceability under simulated revenue drop (e.g. 10%, 20%, 30%).
        """
        reduced_income = gross_monthly_income * (1 - stress_pct)
        # ILLUSTRATIVE assumption: variable costs reduce by 30% of the revenue drop
        reduced_expenses = max(0.0, operating_expenses - (operating_expenses * 0.3 * stress_pct))
        
        stressed_ndi = self.calculate_disposable_income(reduced_income, reduced_expenses, existing_debt_service)
        
        if stressed_ndi >= proposed_instalment:
            return "SURVIVES"
        elif (stressed_ndi * 1.1) >= proposed_instalment:
            return "BORDERLINE"
        else:
            return "FAILS"

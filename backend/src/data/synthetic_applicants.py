"""
Synthetic applicant datasets for CredLens portfolio demonstration.
Provides fictional South African SMB profiles, directors with deliberately invalid demo identity markers,
and synthetic 12-month transaction streams representing distinct credit profiles.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from copy import deepcopy


SYNTHETIC_APPLICANTS: Dict[str, Dict[str, Any]] = {
    "APP-DEMO-001": {
        "lender_reference": "DEMO-LOAN-2026-001",
        "company_name": "Fictional Demo Logistics",
        "registration_number": "DEMO-REG-001",
        "company_type": "Private Company",
        "registered_province": "Gauteng",
        "registered_address": {
            "line1": "DEMO-ADDRESS-001",
            "city": "Kempton Park",
            "province": "Gauteng",
            "postal_code": "1619"
        },
        "business_description": "Road freight distribution and cold-chain transport services across Southern Africa.",
        "years_in_business": 5,
        "directors": [
            {
                "full_name": "Demo Person Alpha",
                "sa_id_number": "DEMO-PERSON-001",  # Non-government demo identifier
                "role": "MANAGING_DIRECTOR",
                "shareholding_pct": 70.0
            },
            {
                "full_name": "Demo Person Beta",
                "sa_id_number": "DEMO-PERSON-002",  # Non-government demo identifier
                "role": "OPERATIONS_DIRECTOR",
                "shareholding_pct": 30.0
            }
        ],
        "primary_contact_email": "operations@logistics.example",
        "primary_contact_phone": "DEMO-PHONE-001",
        "illustrative_score_components": {
            "cash_flow_stability": 82, "revenue_trend": 70, "credit_behaviour": 78,
            "business_legitimacy": 90, "sector_risk": 70, "management_quality": 80,
        },
        "loan_request": {
            "amount_requested": 350000.00,
            "loan_type": "ASSET_FINANCE",
            "loan_purpose": "Acquisition of two 4-ton refrigerated delivery vehicles.",
            "tenor_months_requested": 36,
            "collateral_offered": "First charge over financed vehicles"
        },
        "bureau_profile": {
            "commercial_score": 745,
            "commercial_rating": "Low-Moderate Risk",
            "consumer_score": 710,
            "judgments": 0,
            "defaults": 0,
            "existing_debt_facilities": [
                {
                    "creditor": "Fictional Demo Creditor A",
                    "facility_type": "Vehicle Finance",
                    "outstanding_balance": 115000.00,
                    "monthly_instalment": 11800.00,
                    "payment_status": "CURRENT"
                }
            ]
        },
        "financial_profile": {
            "avg_monthly_revenue": 185000.00,
            "avg_monthly_expenses": 128000.00,
            "existing_monthly_debt": 11800.00,
            "net_disposable_income": 45200.00,
            "proposed_monthly_instalment": 14200.00,
            "illustrative": True
        }
    },
    "APP-DEMO-002": {
        "lender_reference": "DEMO-LOAN-2026-002",
        "company_name": "Fictional Demo Studio",
        "registration_number": "DEMO-REG-002",
        "company_type": "Close Corporation",
        "registered_province": "Western Cape",
        "registered_address": {
            "line1": "DEMO-ADDRESS-002",
            "city": "Cape Town",
            "province": "Western Cape",
            "postal_code": "8001"
        },
        "business_description": "Digital marketing agency providing SEO, performance advertising, and web engineering.",
        "years_in_business": 7,
        "directors": [
            {
                "full_name": "Demo Person Gamma",
                "sa_id_number": "DEMO-PERSON-003",  # Non-government demo identifier
                "role": "PRINCIPAL_MEMBER",
                "shareholding_pct": 100.0
            }
        ],
        "primary_contact_email": "contact@studio.example",
        "primary_contact_phone": "DEMO-PHONE-002",
        "illustrative_score_components": {
            "cash_flow_stability": 62, "revenue_trend": 65, "credit_behaviour": 63,
            "business_legitimacy": 85, "sector_risk": 60, "management_quality": 70,
        },
        "loan_request": {
            "amount_requested": 150000.00,
            "loan_type": "WORKING_CAPITAL",
            "loan_purpose": "Working capital facility to smooth seasonality in project contract payments.",
            "tenor_months_requested": 18,
            "collateral_offered": "Personal surety from principal member"
        },
        "bureau_profile": {
            "commercial_score": 630,
            "commercial_rating": "Moderate Risk",
            "consumer_score": 645,
            "judgments": 0,
            "defaults": 0,
            "existing_debt_facilities": [
                {
                    "creditor": "Fictional Demo Creditor B",
                    "facility_type": "Overdraft Facility",
                    "outstanding_balance": 45000.00,
                    "monthly_instalment": 5200.00,
                    "payment_status": "CURRENT"
                }
            ]
        },
        "financial_profile": {
            "avg_monthly_revenue": 92000.00,
            "avg_monthly_expenses": 67000.00,
            "existing_monthly_debt": 5200.00,
            "net_disposable_income": 19800.00,
            "proposed_monthly_instalment": 10500.00,
            "illustrative": True
        }
    },
    "APP-DEMO-003": {
        "lender_reference": "DEMO-LOAN-2026-003",
        "company_name": "Fictional Demo Solar",
        "registration_number": "DEMO-REG-003",
        "company_type": "Private Company",
        "registered_province": "Northern Cape",
        "registered_address": {
            "line1": "DEMO-ADDRESS-003",
            "city": "Upington",
            "province": "Northern Cape",
            "postal_code": "8801"
        },
        "business_description": "Commercial and agricultural solar PV installations and battery storage solutions.",
        "years_in_business": 3,
        "directors": [
            {
                "full_name": "Demo Person Delta",
                "sa_id_number": "DEMO-PERSON-004",  # Non-government demo identifier
                "role": "DIRECTOR",
                "shareholding_pct": 60.0
            },
            {
                "full_name": "Demo Person Epsilon",
                "sa_id_number": "DEMO-PERSON-005",  # Non-government demo identifier
                "role": "DIRECTOR",
                "shareholding_pct": 40.0
            }
        ],
        "primary_contact_email": "contracts@solar.example",
        "primary_contact_phone": "DEMO-PHONE-003",
        "illustrative_score_components": {
            "cash_flow_stability": 74, "revenue_trend": 67, "credit_behaviour": 81,
            "business_legitimacy": 85, "sector_risk": 55, "management_quality": 65,
        },
        "loan_request": {
            "amount_requested": 500000.00,
            "loan_type": "EQUIPMENT_FINANCE",
            "loan_purpose": "Bulk purchase of inverters and solar panels for corporate contracts.",
            "tenor_months_requested": 24,
            "collateral_offered": "Inventory pledge and contract cessions"
        },
        "bureau_profile": {
            "commercial_score": 760,
            "commercial_rating": "Low Risk",
            "consumer_score": 735,
            "judgments": 0,
            "defaults": 0,
            "existing_debt_facilities": []
        },
        "financial_profile": {
            "avg_monthly_revenue": 310000.00,
            "avg_monthly_expenses": 215000.00,
            "existing_monthly_debt": 0.00,
            "net_disposable_income": 95000.00,
            "proposed_monthly_instalment": 25800.00,
            "illustrative": True
        }
    }
}


def get_sample_applicant(reference: str = "APP-DEMO-001") -> Dict[str, Any]:
    """Retrieve a synthetic sample applicant by key or default."""
    if reference in SYNTHETIC_APPLICANTS:
        return deepcopy(SYNTHETIC_APPLICANTS[reference])
    raise ValueError("Unknown synthetic applicant")


def generate_synthetic_bank_statement(
    applicant_key: str = "APP-DEMO-001",
    months: int = 12
) -> List[Dict[str, Any]]:
    """
    Generates a realistic synthetic transaction stream for an applicant profile.
    Simulates commercial customer deposits, payroll disbursements, supplier payments,
    debt service deductions, and recurring operational fees.
    """
    applicant = get_sample_applicant(applicant_key)
    fin = applicant["financial_profile"]
    
    monthly_rev = fin["avg_monthly_revenue"]
    monthly_exp = fin["avg_monthly_expenses"]
    monthly_debt = fin["existing_monthly_debt"]
    
    if not 1 <= months <= 12:
        raise ValueError("months must be between 1 and 12")
    transactions = []
    base_date = datetime(2025, 1, 1)
    tx_counter = 1
    
    for m in range(months):
        month_date = datetime(base_date.year + m // 12, m % 12 + 1, 1)
        # Revenue deposits (3-4 deposits across the month)
        deposit_split = [0.35, 0.40, 0.25]
        for i, split in enumerate(deposit_split):
            tx_date = month_date + timedelta(days=7 * i + 3)
            amt = round(monthly_rev * split, 2)
            transactions.append({
                "transaction_id": f"tx_{tx_counter:05d}",
                "date": tx_date.strftime("%Y-%m-%d"),
                "description": f"CUSTOMER PAYMENT CONTRACT-{tx_counter % 20:03d}",
                "amount": amt,
                "type": "CREDIT",
                "category": "REVENUE"
            })
            tx_counter += 1
            
        # Operating expenses: Rent & Utilities (1st of month)
        transactions.append({
            "transaction_id": f"tx_{tx_counter:05d}",
            "date": (month_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            "description": "COMMERCIAL PROPERTY RENT & UTILITIES",
            "amount": -round(monthly_exp * 0.22, 2),
            "type": "DEBIT",
            "category": "OPERATING_EXPENSES"
        })
        tx_counter += 1
        
        # Operating expenses: Supplier disbursements (15th of month)
        transactions.append({
            "transaction_id": f"tx_{tx_counter:05d}",
            "date": (month_date + timedelta(days=15)).strftime("%Y-%m-%d"),
            "description": "INVENTORY SUPPLIERS DIRECT SETTLEMENT",
            "amount": -round(monthly_exp * 0.45, 2),
            "type": "DEBIT",
            "category": "COST_OF_SALES"
        })
        tx_counter += 1
        
        # Payroll disbursement (25th of month)
        transactions.append({
            "transaction_id": f"tx_{tx_counter:05d}",
            "date": (month_date + timedelta(days=25)).strftime("%Y-%m-%d"),
            "description": "STAFF PAYROLL BATCH PAYMENT",
            "amount": -round(monthly_exp * 0.30, 2),
            "type": "DEBIT",
            "category": "SALARIES"
        })
        tx_counter += 1
        
        # Existing debt service if applicable (5th of month)
        if monthly_debt > 0:
            transactions.append({
                "transaction_id": f"tx_{tx_counter:05d}",
                "date": (month_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "description": "COMMERCIAL ASSET FINANCE DEBIT ORDER",
                "amount": -monthly_debt,
                "type": "DEBIT",
                "category": "DEBT_SERVICE"
            })
            tx_counter += 1
            
        # Bank account service fees (month end)
        transactions.append({
            "transaction_id": f"tx_{tx_counter:05d}",
            "date": (month_date + timedelta(days=28)).strftime("%Y-%m-%d"),
            "description": "COMMERCIAL ACCOUNT MONTHLY SERVICE FEE",
            "amount": -round(monthly_exp * 0.03, 2),
            "type": "DEBIT",
            "category": "BANK_FEES"
        })
        tx_counter += 1

    return transactions

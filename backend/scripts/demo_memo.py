#!/usr/bin/env python3
"""Print a synthetic credit memo without Redis or PostgreSQL."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.synthetic_applicants import SYNTHETIC_APPLICANTS
from src.services.assessment_service import assess_sample

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--applicant", choices=list(SYNTHETIC_APPLICANTS), default="APP-DEMO-001")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(assess_sample(args.applicant)), indent=2))

if __name__ == "__main__":
    main()

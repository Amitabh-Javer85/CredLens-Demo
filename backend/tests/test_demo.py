import json
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.adapters.claude_agent import ClaudeAgentAdapter
from src.core.config import settings
from src.data.synthetic_applicants import SYNTHETIC_APPLICANTS, get_sample_applicant, generate_synthetic_bank_statement
from src.main import app
from src.services.assessment_service import assess_sample
from src.services.scoring_service import ScoringService
from src.workers.assessment_worker import orchestrate_underwriting


@pytest.mark.parametrize("applicant_id", list(SYNTHETIC_APPLICANTS))
async def test_pipeline(applicant_id):
    applicant = get_sample_applicant(applicant_id)
    result = await assess_sample(applicant_id)
    memo = result["memo"]
    assert memo["generation_mode"] == "CANNED"
    assert memo["claude_model"] == "canned-demo"
    assert result["usage"] == {"input_tokens": 0, "output_tokens": 0}
    assert applicant["company_name"] in json.dumps(memo)
    assert "ENTITY_" not in json.dumps(memo)
    score = memo["credlens_score"]
    assert score["components"] == applicant["illustrative_score_components"]
    assert score["total"] == ScoringService().calculate_score(score["components"])
    assert score["band"] == ScoringService().determine_risk_band(score["total"])
    assert result["verification"]["screening"]["status"] == "CLEAR"
    assert result["verification"]["directors"]


@pytest.mark.parametrize("applicant_id", list(SYNTHETIC_APPLICANTS))
def test_statement_matches_profile(applicant_id):
    txs = generate_synthetic_bank_statement(applicant_id)
    fin = get_sample_applicant(applicant_id)["financial_profile"]
    assert fin["net_disposable_income"] == fin["avg_monthly_revenue"] - fin["avg_monthly_expenses"] - fin["existing_monthly_debt"]
    assert len({t["date"][:7] for t in txs}) == 12
    assert sum(t["amount"] for t in txs if t["type"] == "CREDIT") == pytest.approx(12 * fin["avg_monthly_revenue"])
    assert -sum(t["amount"] for t in txs if t["type"] == "DEBIT") == pytest.approx(12 * (fin["avg_monthly_expenses"] + fin["existing_monthly_debt"]))
    assert txs == generate_synthetic_bank_statement(applicant_id)


def test_fixture_copy_and_unknown():
    fixture = get_sample_applicant()
    fixture["company_name"] = "Changed"
    assert get_sample_applicant()["company_name"] != "Changed"
    with pytest.raises(ValueError):
        get_sample_applicant("missing")


async def test_stress_results_are_calculated_from_fixture():
    result = await assess_sample("APP-DEMO-003")
    assert result["memo"]["affordability_assessment"]["stress_test_30pct"] == "FAILS"


@pytest.mark.parametrize("score, band", [(750, "LOW_RISK"), (749, "MODERATE_RISK"),
                                         (600, "MODERATE_RISK"), (599, "HIGH_RISK"),
                                         (400, "HIGH_RISK"), (399, "VERY_HIGH_RISK")])
def test_illustrative_score_boundaries(score, band):
    assert ScoringService().determine_risk_band(score) == band


async def test_live_payload_privacy_and_restoration(monkeypatch):
    import anthropic
    applicant = get_sample_applicant()
    applicant["company_name"] = 'Demo "Quoted" Company'
    applicant["loan_request"]["loan_purpose"] = applicant["company_name"] + " " + applicant["directors"][0]["full_name"]
    financial = {"summary": {"note": applicant["primary_contact_email"]}, "transactions": [{"account_number": "DEMO-ACCOUNT-01", "description": applicant["company_name"]}]}
    captured = []

    class FakeClient:
        def __init__(self, **kwargs):
            self.messages = self
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        async def create(self, **kwargs):
            content = kwargs["messages"][0]["content"]
            captured.append(content)
            payload = json.loads(content)
            a = payload["applicant"]
            text = ClaudeAgentAdapter()._generate_canned_memo(a["company_name"], a["registration_number"], a, payload["financial"])
            return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)], usage=SimpleNamespace(input_tokens=12, output_tokens=34))

    monkeypatch.setattr(anthropic, "AsyncAnthropic", FakeClient)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test-placeholder")
    monkeypatch.setattr(settings, "CLAUDE_MODEL", "test-model")
    memo, incoming, outgoing = await ClaudeAgentAdapter().analyze_credit(applicant, financial)
    for value in [applicant["company_name"], applicant["directors"][0]["full_name"], applicant["primary_contact_email"], "DEMO-ACCOUNT-01"]:
        assert value not in captured[0]
    assert applicant["company_name"] in memo["affordability_assessment"]["income_basis"]
    assert memo["generation_mode"] == "LIVE"
    assert (incoming, outgoing) == (12, 34)


async def test_provider_error_falls_back_without_logging_content(monkeypatch):
    import anthropic
    class BadClient:
        def __init__(self, **kwargs):
            raise RuntimeError("provider error containing sensitive request text")
    monkeypatch.setattr(anthropic, "AsyncAnthropic", BadClient)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test-placeholder")
    monkeypatch.setattr(settings, "CLAUDE_MODEL", "test-model")
    memo, incoming, outgoing = await ClaudeAgentAdapter().analyze_credit(get_sample_applicant(), {})
    assert memo["generation_mode"] == "CANNED"
    assert (incoming, outgoing) == (0, 0)


async def test_invalid_live_schema_falls_back(monkeypatch):
    import anthropic
    class InvalidClient:
        def __init__(self, **kwargs): self.messages = self
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(type="text", text='{"unexpected": true}')],
                                   usage=SimpleNamespace(input_tokens=5, output_tokens=6))
    monkeypatch.setattr(anthropic, "AsyncAnthropic", InvalidClient)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test-placeholder")
    monkeypatch.setattr(settings, "CLAUDE_MODEL", "test-model")
    memo, incoming, outgoing = await ClaudeAgentAdapter().analyze_credit(get_sample_applicant(), {})
    assert memo["generation_mode"] == "CANNED"
    assert (incoming, outgoing) == (5, 6)  # Actual provider usage survives a schema failure.


async def test_concurrent_requests_do_not_share_identity_maps():
    import asyncio
    adapter = ClaudeAgentAdapter()
    applicants = [get_sample_applicant(key) for key in SYNTHETIC_APPLICANTS]
    results = await asyncio.gather(*[adapter.analyze_credit(a, {}) for a in applicants])
    for applicant, (memo, _, _) in zip(applicants, results):
        assert applicant["company_name"] in memo["affordability_assessment"]["income_basis"]
        assert all(a["company_name"] not in json.dumps(memo) for a in applicants if a != applicant)


def test_worker_executes_pipeline():
    result = orchestrate_underwriting.apply(args=["APP-DEMO-002"], throw=True).get()
    assert result["applicant_id"] == "APP-DEMO-002"
    assert result["memo"]["generation_mode"] == "CANNED"


def test_api_lifecycle(monkeypatch):
    from src.api import applications
    saved = {}
    jobs = {}
    class Store:
        def setex(self, key, ttl, value): saved[key] = value
        def exists(self, key): return key in saved
        def delete(self, key): saved.pop(key, None)
    def dispatch(args, task_id):
        result = orchestrate_underwriting.apply(args=args, throw=True).get()
        jobs[task_id] = SimpleNamespace(state="SUCCESS", failed=lambda: False, successful=lambda: True, result=result)
    monkeypatch.setattr(applications, "job_store", Store)
    monkeypatch.setattr(orchestrate_underwriting, "apply_async", dispatch)
    monkeypatch.setattr(applications.celery_app, "AsyncResult", lambda task_id: jobs[task_id])
    client = TestClient(app)
    assert client.get("/docs").status_code == 200
    assert client.get("/v1/applications/samples").json()["synthetic"]
    response = client.post("/v1/applications", json={"applicant_id": "APP-DEMO-003"})
    assert response.status_code == 202
    task_id = response.json()["application_id"]
    assert client.get(f"/v1/applications/{task_id}").json()["status"] == "SUCCESS"
    assert client.get(f"/v1/applications/{task_id}/memo").json()["applicant_id"] == "APP-DEMO-003"
    assert client.get(f"/v1/applications/{uuid4()}").status_code == 404
    assert client.post("/v1/applications", json={"applicant_id": "missing"}).status_code == 422
    assert client.post("/v1/applications", json={"personal_data": "not allowed"}).status_code == 422


def test_queue_unavailable_returns_503(monkeypatch):
    from src.api import applications
    from redis.exceptions import ConnectionError
    class UnavailableStore:
        def setex(self, *args): raise ConnectionError("offline")
        def delete(self, *args): raise ConnectionError("offline")
    monkeypatch.setattr(applications, "job_store", UnavailableStore)
    assert TestClient(app).post("/v1/applications", json={}).status_code == 503


@pytest.mark.parametrize("failed", [False, True])
def test_pending_or_failed_job_has_no_memo(monkeypatch, failed):
    from src.api import applications
    result = SimpleNamespace(failed=lambda: failed, successful=lambda: False)
    monkeypatch.setattr(applications, "get_result", lambda _: result)
    assert TestClient(app).get(f"/v1/applications/{uuid4()}/memo").status_code == 409

"""HTTP contract used by the Vite UI and INSTALLATION.md curls."""

from fastapi.testclient import TestClient

from seem.api import create_app


def client() -> TestClient:
    return TestClient(create_app())


def test_health_reports_measured_invertibility():
    response = client().get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["measured_invertibility"] >= 0.99
    assert body["claim"] == 0
    assert body["components"]["shacl"] == "numeric-gates-only"
    assert body["service_dimension"] == 16384


def test_bind_and_invertibility_query_matches_docs():
    http = client()
    bound = http.post("/vsa/bind", params={"role_id": "action_test", "filler_id": "target_test"})
    assert bound.status_code == 200
    assert bound.json()["bound"] is True
    assert bound.json()["dimension"] == 16384
    inv = http.post(
        "/vsa/invertibility",
        params={"role_id": "action_test", "filler_id": "target_test"},
    )
    assert inv.status_code == 200
    body = inv.json()
    assert body["invertibility"] >= 0.99
    assert body["passed"] is True


def test_resonator_bound_query_recovers_target():
    http = client()
    response = http.post(
        "/vsa/resonator",
        json={
            "query_symbol": "__bound__",
            "context_symbol": "ctx",
            "target_symbol": "tgt",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["cosine_similarity"] >= 0.99
    assert body["iterations"] <= 7
    assert body["iterations_valid"] is True


def test_banel_routes_start_empty_then_record_failure():
    http = client()
    assert http.get("/banel/routes").json()["count"] == 0
    missing = http.get("/banel/stats/route_001")
    assert missing.status_code == 404
    recorded = http.post(
        "/banel/record-failure",
        json={
            "route_id": "route_001",
            "failure_type": "unbind_failure",
            "cosine_similarity": 0.88,
            "error_message": "Below threshold",
        },
    )
    assert recorded.status_code == 200
    body = recorded.json()
    assert body["should_micro_dream"] is True
    assert body["suppression_level"] > 0.6
    routes = http.get("/banel/routes").json()
    assert routes["count"] == 1
    assert routes["routes"][0]["failure_count"] == 1
    spikes = http.get("/banel/recent-spikes").json()
    assert spikes["count"] == 1
    bad = http.post(
        "/banel/record-failure",
        json={"route_id": "x", "failure_type": "nope"},
    )
    assert bad.status_code == 400


def test_dream_and_l0_roundtrip():
    http = client()
    created = http.post(
        "/dream/create-variant",
        params={"original_id": "route_001", "skill_name": "test_skill"},
    )
    assert created.status_code == 200
    variant_id = created.json()["variant_id"]
    early = http.post(
        "/dream/consolidate",
        params={"original_id": "route_001", "skill_name": "test_skill"},
    )
    assert early.json()["consolidated"] is False
    for _ in range(9):
        rec = http.post(
            "/dream/record-execution",
            json={"variant_id": variant_id, "success": True, "fitness_score": 1.0},
        )
        assert rec.status_code == 200
    cycle = http.post("/dream/run-cycle", params={"original_id": "route_001"})
    assert cycle.status_code == 200
    assert cycle.json()["new_generation_size"] == 50
    assert cycle.json()["cycle_count"] == 1
    done = http.post(
        "/dream/consolidate",
        params={"original_id": "route_001", "skill_name": "test_skill"},
    )
    assert done.json()["consolidated"] is True
    stats = http.get("/dream/stats").json()
    assert stats["dream_cycles"] == 1
    assert stats["total_consolidated_skills"] == 1

    stored = http.post(
        "/l0/store-evidence",
        json={"evidence_id": "ev1", "evidence_type": "note", "content": {"text": "old"}},
    )
    assert stored.status_code == 200
    http.post(
        "/l0/store-evidence",
        json={"evidence_id": "ev2", "evidence_type": "note", "content": {"text": "new"}},
    )
    sup = http.post(
        "/l0/supersede",
        json={
            "old_evidence_id": "ev1",
            "new_evidence_id": "ev2",
            "reason": "performance_improvement",
        },
    )
    assert sup.status_code == 200
    l0 = http.get("/l0/stats").json()
    assert l0["total_evidence"] == 2
    assert l0["active_evidence"] == 1
    assert l0["supersedence_records"] == 1
    hist = http.get("/l0/evidence/ev1").json()
    assert hist["is_active"] is False


def test_validator_stats_follow_real_checks_not_a_default():
    http = client()
    initial = http.get("/validator/stats").json()
    assert initial["total_validations"] == 0
    assert initial["pass_rate"] == 0.0
    http.post("/vsa/invertibility", params={"role_id": "r", "filler_id": "f"})
    after = http.get("/validator/stats").json()
    assert after["total_validations"] == 1
    assert after["passed"] == 1
    assert after["pass_rate"] == 1.0


def test_config_discloses_memory_and_claim():
    body = client().get("/config").json()
    assert body["claim"] == 0
    assert "in-memory" in body["persistence"]
    assert "pyshacl" in body["shacl"]

"""Measured behavior of the in-memory kernel. No planted scores."""

import numpy as np

from seem.core import ResonatorVSA
from seem.governance import SHACLValidator
from seem.governance.l0_graph import SupersedenceReason
from seem.governance.l0_graph import SupersededGraph
from seem.learning import BaNELEngine, DreamPhaseEngine, FailureType
from seem.plugins import ExecutionEngine
from seem.plugins.executor import Plugin, PluginType


def test_fhrr_bind_unbind_is_exact():
    rng_seed = 7
    np.random.seed(rng_seed)
    vsa = ResonatorVSA(dimension=512)
    role = vsa.encode_symbol("role")
    filler = vsa.encode_symbol("filler")
    score = vsa.measure_invertibility(role, filler)
    assert score > 0.999


def test_unrelated_phasors_are_not_aligned():
    np.random.seed(11)
    vsa = ResonatorVSA(dimension=2048)
    a = vsa.encode_symbol("a")
    b = vsa.encode_symbol("b")
    assert abs(a.cosine_similarity(b)) < 0.15


def test_invertibility_min_over_trials_clears_configured_gate():
    np.random.seed(3)
    vsa = ResonatorVSA(dimension=1024)
    scores = []
    for i in range(8):
        role = vsa.create_random_hypervector()
        filler = vsa.create_random_hypervector()
        scores.append(vsa.measure_invertibility(role, filler))
    assert min(scores) >= 0.99
    validator = SHACLValidator()
    result = validator.validate_invertibility(min(scores), threshold=0.92)
    assert result.passed is True


def test_resonator_recovers_bound_filler_and_not_a_decoy():
    np.random.seed(19)
    vsa = ResonatorVSA(dimension=1024)
    role = vsa.encode_symbol("role")
    filler = vsa.encode_symbol("filler")
    vsa.encode_symbol("decoy")
    bound = role.bind(filler)
    recovered, cosine, iterations = vsa.resonator_loop(bound, role, filler)
    assert iterations >= 1
    assert cosine > 0.99
    assert recovered.cosine_similarity(filler) > 0.99
    assert recovered.cosine_similarity(vsa.encode_symbol("decoy")) < 0.2


def test_sparsity_keeps_zeros():
    np.random.seed(1)
    vsa = ResonatorVSA(dimension=100, sparsity_ratio=0.1)
    hv = vsa.create_random_hypervector()
    sparse = vsa.apply_sparsity(hv, ratio=0.1)
    assert int(np.sum(np.abs(sparse.vector) == 0)) == 10


def test_banel_failure_suppresses_and_success_clears():
    engine = BaNELEngine()
    trigger = engine.record_failure(
        "route_001",
        FailureType.UNBIND_FAILURE,
        cosine_similarity=0.2,
        error_message="below threshold",
    )
    assert trigger is True
    stats = engine.get_route_statistics("route_001")
    assert stats is not None
    assert stats.failure_count == 1
    assert stats.negative_spike_count == 1
    assert engine.is_suppressed("route_001") is True
    engine.record_success("route_001", cosine_similarity=1.0, iterations=1)
    assert engine.get_suppression_level("route_001") == 0.0
    assert engine.get_route_statistics("route_001").success_count == 1


def test_unknown_failure_type_is_rejected_by_enum():
    try:
        FailureType("not-a-type")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_dream_cycle_needs_a_variant_and_consolidation_uses_fitness():
    dream = DreamPhaseEngine(population_size=6, elite_size=2, consolidation_threshold=0.75)
    assert dream.run_dream_cycle("missing") == []
    variant = dream.create_variant("route_a")
    # EMA starts at 0. Repeated 1.0 scores climb past 0.75; one score does not.
    dream.record_variant_execution(variant.id, True, 1.0)
    assert variant.fitness < 0.75
    assert dream.consolidate_skill("route_a", "skill") is None
    for _ in range(8):
        dream.record_variant_execution(variant.id, True, 1.0)
    assert variant.fitness >= 0.75
    generation = dream.run_dream_cycle("route_a")
    assert len(generation) == 6
    skill = dream.consolidate_skill("route_a", "skill")
    assert skill is not None
    assert skill.best_variant_id
    stats = dream.get_statistics()
    assert stats["dream_cycles"] == 1
    assert stats["total_consolidated_skills"] == 1


def test_l0_supersede_keeps_history_and_drops_active():
    graph = SupersededGraph()
    graph.store_evidence("e1", "note", {"text": "old"})
    graph.store_evidence("e2", "note", {"text": "new"})
    graph.supersede_evidence("e1", "e2", SupersedenceReason.PERFORMANCE_IMPROVEMENT)
    history = graph.get_evidence_history("e1")
    assert history["is_active"] is False
    assert history["superseded_by"][0]["superseding_evidence_id"] == "e2"
    active = graph.get_active_evidence()
    assert [e.id for e in active] == ["e2"]
    stats = graph.get_statistics()
    assert stats["total_evidence"] == 2
    assert stats["active_evidence"] == 1
    assert stats["supersedence_records"] == 1


def test_plugin_engine_records_success():
    import asyncio

    engine = ExecutionEngine()

    async def _run(data):
        return {"echo": data["x"]}

    engine.register_plugin(Plugin(id="echo", name="echo", plugin_type=PluginType.SKILL_EXECUTION, execute_fn=_run))
    result = asyncio.run(engine.execute_plugin("echo", {"x": 3}))
    assert result == {"echo": 3}
    stats = engine.get_plugin_statistics("echo")
    assert stats["successful"] == 1

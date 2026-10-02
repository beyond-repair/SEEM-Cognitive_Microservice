"""Claim-0 offline demo.

Prints measured FHRR invertibility, one BaNEL suppression, one dream
consolidation, and one L0 supersede. Does not claim a mind or RDF SHACL.
"""

from __future__ import annotations

import numpy as np

from seem.core import ResonatorVSA
from seem.governance.l0_graph import SupersededGraph, SupersedenceReason
from seem.learning import BaNELEngine, DreamPhaseEngine, FailureType


def main() -> None:
    dimension = 16384
    trials = 8
    np.random.seed(0)
    vsa = ResonatorVSA(dimension=dimension)
    scores = []
    unrelated = []
    for i in range(trials):
        role = vsa.create_random_hypervector()
        filler = vsa.create_random_hypervector()
        other = vsa.create_random_hypervector()
        scores.append(vsa.measure_invertibility(role, filler))
        unrelated.append(abs(role.cosine_similarity(other)))
    minimum = min(scores)
    mean = sum(scores) / len(scores)
    gate = 0.92
    print(f"dimension={dimension} trials={trials}")
    print(f"min_invertibility={minimum:.6f} mean_invertibility={mean:.6f}")
    print(f"max_abs_unrelated={max(unrelated):.6f}")
    print(f"configured_gate={gate:.2f} gate={'PASS' if minimum >= gate else 'FAIL'}")

    banel = BaNELEngine()
    trigger = banel.record_failure(
        "route_001",
        FailureType.UNBIND_FAILURE,
        cosine_similarity=0.88,
        error_message="Below threshold",
    )
    level = banel.get_suppression_level("route_001")
    print(f"banel_should_micro_dream={trigger} suppression_after_read={level:.4f}")

    dream = DreamPhaseEngine(population_size=8, elite_size=2)
    variant = dream.create_variant("route_001")
    for _ in range(9):
        dream.record_variant_execution(variant.id, True, 1.0)
    dream.run_dream_cycle("route_001")
    skill = dream.consolidate_skill("route_001", "test_skill")
    print(
        "dream_cycles={cycles} variant_fitness={fit:.4f} consolidated={ok}".format(
            cycles=dream.dream_cycle_count,
            fit=variant.fitness,
            ok=skill is not None,
        )
    )

    graph = SupersededGraph()
    graph.store_evidence("ev1", "note", {"text": "old"})
    graph.store_evidence("ev2", "note", {"text": "new"})
    graph.supersede_evidence("ev1", "ev2", SupersedenceReason.PERFORMANCE_IMPROVEMENT)
    stats = graph.get_statistics()
    print(
        "l0_total={total} l0_active={active} l0_supersedence={records}".format(
            total=stats["total_evidence"],
            active=stats["active_evidence"],
            records=stats["supersedence_records"],
        )
    )
    print("persistence=in-memory")
    print("shacl=numeric gates only; rdflib/pyshacl are not used")
    print("claim=0")
    print("not_agi=true")
    if minimum < gate or skill is None or not trigger:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

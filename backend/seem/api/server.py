from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from seem.core import ResonatorVSA
from seem.learning import BaNELEngine, FailureType, DreamPhaseEngine
from seem.governance import SHACLValidator, SupersededGraph
from seem.governance.l0_graph import SupersedenceReason


class ResonatorTestRequest(BaseModel):
    query_symbol: str
    context_symbol: str
    target_symbol: str
    max_iterations: Optional[int] = 7


class BaNELFailureRequest(BaseModel):
    route_id: str
    failure_type: str
    cosine_similarity: Optional[float] = None
    error_message: str = ""


class DreamExecutionRequest(BaseModel):
    variant_id: str
    success: bool
    fitness_score: float = Field(ge=0.0, le=1.0)


class EvidenceRequest(BaseModel):
    evidence_id: str
    evidence_type: str
    content: Dict[str, Any]


class SupersedeRequest(BaseModel):
    old_evidence_id: str
    new_evidence_id: str
    reason: str = "performance_improvement"


class ValidationStatsResponse(BaseModel):
    total_validations: int
    passed: int
    failed: int
    pass_rate: float


def create_app() -> FastAPI:
    app = FastAPI(
        title="SEEM 2.0 API",
        description=(
            "In-memory Claim-0 sketch of a symbolic microservice "
            "(FHRR phasors, BaNEL counters, dream GA, numeric gates, L0 log). "
            "Not a mind. Not RDF SHACL. State dies with the process."
        ),
        version="2.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    vsa = ResonatorVSA()
    banel = BaNELEngine()
    dream = DreamPhaseEngine()
    validator = SHACLValidator()
    l0_graph = SupersededGraph()

    @app.get("/")
    async def root():
        return {
            "name": "SEEM 2.0",
            "version": "2.0.0",
            "description": "Sovereign Episodic Experience Microservice (Claim-0 in-memory sketch)",
            "claim": 0,
            "persistence": "memory",
        }

    @app.get("/health")
    async def health_check():
        probe = ResonatorVSA(dimension=256, max_iterations=1)
        role = probe.encode_symbol("health_role")
        filler = probe.encode_symbol("health_filler")
        measured = probe.measure_invertibility(role, filler)
        status = "healthy" if measured >= 0.99 else "degraded"
        return {
            "status": status,
            "measured_invertibility": measured,
            "probe_dimension": probe.dimension,
            "service_dimension": vsa.dimension,
            "claim": 0,
            "components": {
                "vsa": "operational",
                "banel": "operational",
                "dream_phase": "operational",
                "shacl": "numeric-gates-only",
                "l0_graph": "operational",
            },
        }

    @app.get("/config")
    async def get_config():
        return {
            "dimension": vsa.dimension,
            "max_iterations": vsa.max_iterations,
            "invertibility_threshold": vsa.invertibility_threshold,
            "sparsity_ratio": vsa.sparsity_ratio,
            "banel_rejection_threshold": banel.rejection_threshold,
            "spike_decay_rate": banel.spike_decay_rate,
            "dream_population_size": dream.population_size,
            "dream_elite_size": dream.elite_size,
            "dream_mutation_rate": dream.mutation_rate,
            "dream_crossover_rate": dream.crossover_rate,
            "dream_consolidation_threshold": dream.consolidation_threshold,
            "codebook_size": len(vsa.symbol_codebook),
            "persistence": "in-memory only; process restart clears state",
            "claim": 0,
            "shacl": "SHACLValidator checks numeric gates. It does not load RDF or run pyshacl.",
            "not": "Not a mind, council, or measured scientific result beyond the numbers this process returns.",
        }

    @app.post("/vsa/encode")
    async def encode_symbol(symbol_id: str):
        try:
            vsa.encode_symbol(symbol_id)
            return {
                "symbol_id": symbol_id,
                "dimension": vsa.dimension,
                "encoded": True,
                "codebook_size": len(vsa.symbol_codebook),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/bind")
    async def bind_symbols(role_id: str, filler_id: str):
        try:
            vsa.bind_symbols(role_id, filler_id)
            return {
                "role_id": role_id,
                "filler_id": filler_id,
                "bound": True,
                "dimension": vsa.dimension,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/invertibility")
    async def test_invertibility(role_id: str, filler_id: str):
        try:
            role = vsa.encode_symbol(role_id)
            filler = vsa.encode_symbol(filler_id)
            invertibility = vsa.measure_invertibility(role, filler)
            validation = validator.validate_invertibility(invertibility)
            return {
                "role_id": role_id,
                "filler_id": filler_id,
                "invertibility": invertibility,
                "passed": validation.passed,
                "threshold": vsa.invertibility_threshold,
                "message": validation.message,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/resonator")
    async def resonator_test(request: ResonatorTestRequest):
        try:
            # Encode the factors first so cleanup can see them.
            context = vsa.encode_symbol(request.context_symbol)
            target = vsa.encode_symbol(request.target_symbol)
            # query_symbol may name an existing codebook entry, or the literal
            # binding of context ⊙ target when query_symbol == "__bound__".
            if request.query_symbol == "__bound__":
                query = context.bind(target)
            else:
                query = vsa.encode_symbol(request.query_symbol)
            saved_iters = vsa.max_iterations
            if request.max_iterations is not None:
                vsa.max_iterations = request.max_iterations
            try:
                _result, cosine, iterations = vsa.resonator_loop(query, context, target)
            finally:
                vsa.max_iterations = saved_iters
            validation = validator.validate_iterations(iterations, vsa.max_iterations)
            return {
                "query": request.query_symbol,
                "context": request.context_symbol,
                "target": request.target_symbol,
                "cosine_similarity": cosine,
                "iterations": iterations,
                "iterations_valid": validation.passed,
                "message": validation.message,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/banel/routes")
    async def list_routes():
        routes = [s.to_dict() for s in banel.get_all_route_statistics()]
        return {"routes": routes, "count": len(routes)}

    @app.get("/banel/stats/{route_id}")
    async def get_route_stats(route_id: str):
        stats = banel.get_route_statistics(route_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Route not found")
        return stats.to_dict()

    @app.post("/banel/record-success")
    async def record_success(
        route_id: str,
        cosine_similarity: float,
        iterations: int,
    ):
        try:
            banel.record_success(route_id, cosine_similarity, iterations)
            return {
                "route_id": route_id,
                "recorded": True,
                "success": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/banel/record-failure")
    async def record_failure(request: BaNELFailureRequest):
        try:
            failure_type = FailureType(request.failure_type)
            should_micro_dream = banel.record_failure(
                request.route_id,
                failure_type,
                request.cosine_similarity,
                request.error_message,
            )
            return {
                "route_id": request.route_id,
                "recorded": True,
                "should_micro_dream": should_micro_dream,
                "suppression_level": banel.get_suppression_level(request.route_id),
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/banel/recent-spikes")
    async def get_recent_spikes(route_id: Optional[str] = None, limit: int = 10):
        spikes = banel.get_recent_spikes(route_id, limit)
        return {
            "spikes": [s.to_dict() for s in spikes],
            "count": len(spikes),
        }

    @app.post("/dream/create-variant")
    async def create_variant(original_id: str, skill_name: str = ""):
        try:
            variant = dream.create_variant(
                original_id,
                metadata={"skill_name": skill_name} if skill_name else {},
            )
            return {
                "variant_id": variant.id,
                "original_id": variant.original_id,
                "k_lambda": variant.k_lambda,
                "max_iters": variant.max_iters,
                "skill_name": skill_name,
                "created": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/dream/record-execution")
    async def record_dream_execution(request: DreamExecutionRequest):
        before = dream.get_statistics()["total_variants"]
        dream.record_variant_execution(
            request.variant_id,
            request.success,
            request.fitness_score,
        )
        found = None
        for variants in dream.route_variants.values():
            for variant in variants:
                if variant.id == request.variant_id:
                    found = variant
                    break
        if found is None:
            raise HTTPException(status_code=404, detail="Variant not found")
        del before
        return {
            "variant_id": found.id,
            "fitness": found.fitness,
            "success_count": found.success_count,
            "failure_count": found.failure_count,
            "recorded": True,
        }

    @app.post("/dream/run-cycle")
    async def run_dream_cycle(original_id: str):
        try:
            new_generation = dream.run_dream_cycle(original_id)
            return {
                "original_id": original_id,
                "new_generation_size": len(new_generation),
                "best_variant_id": new_generation[0].id if new_generation else None,
                "cycle_count": dream.dream_cycle_count,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/dream/consolidate")
    async def consolidate_skill(original_id: str, skill_name: str):
        skill = dream.consolidate_skill(original_id, skill_name)
        if skill is None:
            best = dream.get_best_variant(original_id)
            return {
                "consolidated": False,
                "original_id": original_id,
                "best_fitness": None if best is None else best.fitness,
                "threshold": dream.consolidation_threshold,
                "reason": "no elite variant at or above the fitness threshold",
            }
        return {
            "consolidated": True,
            "skill_id": skill.id,
            "name": skill.name,
            "best_variant_id": skill.best_variant_id,
            "overall_fitness": skill.overall_fitness,
        }

    @app.get("/dream/stats")
    async def get_dream_stats():
        return dream.get_statistics()

    @app.get("/validator/stats")
    async def get_validation_stats():
        stats = validator.get_statistics()
        return ValidationStatsResponse(**stats)

    @app.get("/validator/violations")
    async def get_violations():
        violations = validator.get_violations()
        return {
            "violations": [v.to_dict() for v in violations],
            "count": len(violations),
        }

    @app.post("/l0/store-evidence")
    async def store_evidence(request: EvidenceRequest):
        try:
            evidence = l0_graph.store_evidence(
                request.evidence_id,
                request.evidence_type,
                request.content,
            )
            return {
                "evidence_id": evidence.id,
                "type": evidence.type,
                "stored": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/l0/supersede")
    async def supersede_evidence(request: SupersedeRequest):
        try:
            reason = SupersedenceReason(request.reason)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        try:
            record = l0_graph.supersede_evidence(
                request.old_evidence_id,
                request.new_evidence_id,
                reason,
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return {
            "record_id": record.id,
            "superseded_evidence_id": record.superseded_evidence_id,
            "superseding_evidence_id": record.superseding_evidence_id,
            "reason": record.reason.value,
        }

    @app.get("/l0/evidence/{evidence_id}")
    async def get_evidence(evidence_id: str):
        history = l0_graph.get_evidence_history(evidence_id)
        if not history:
            raise HTTPException(status_code=404, detail="Evidence not found")
        return history

    @app.get("/l0/active-evidence")
    async def get_active_evidence(evidence_type: Optional[str] = None):
        active = l0_graph.get_active_evidence(evidence_type)
        return {
            "evidence": [e.to_dict() for e in active],
            "count": len(active),
        }

    @app.get("/l0/stats")
    async def get_l0_stats():
        return l0_graph.get_statistics()

    return app

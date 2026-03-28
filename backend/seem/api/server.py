from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json

from seem.core import ResonatorVSA, MemSkill, MemSkillLevel
from seem.learning import BaNELEngine, FailureType, DreamPhaseEngine
from seem.governance import SHACLValidator, SupersededGraph


class HypervectorBindRequest(BaseModel):
    role_id: str
    filler_id: str


class InvertibilityTestRequest(BaseModel):
    role_id: str
    filler_id: str


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


class ValidationStatsResponse(BaseModel):
    total_validations: int
    passed: int
    failed: int
    pass_rate: float


def create_app() -> FastAPI:
    app = FastAPI(
        title="SEEM 2.0 API",
        description="Sovereign Episodic Experience Microservice",
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
            "description": "Sovereign Episodic Experience Microservice",
        }

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "components": {
                "vsa": "operational",
                "banel": "operational",
                "dream_phase": "operational",
                "shacl": "operational",
                "l0_graph": "operational",
            },
        }

    @app.post("/vsa/encode")
    async def encode_symbol(symbol_id: str):
        try:
            hv = vsa.encode_symbol(symbol_id)
            return {
                "symbol_id": symbol_id,
                "dimension": vsa.dimension,
                "encoded": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/bind")
    async def bind_symbols(request: HypervectorBindRequest):
        try:
            bound = vsa.bind_symbols(request.role_id, request.filler_id)
            return {
                "role_id": request.role_id,
                "filler_id": request.filler_id,
                "bound": True,
                "dimension": vsa.dimension,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/invertibility")
    async def test_invertibility(request: InvertibilityTestRequest):
        try:
            role = vsa.encode_symbol(request.role_id)
            filler = vsa.encode_symbol(request.filler_id)
            invertibility = vsa.measure_invertibility(role, filler)

            validation = validator.validate_invertibility(invertibility)

            return {
                "role_id": request.role_id,
                "filler_id": request.filler_id,
                "invertibility": invertibility,
                "passed": validation.passed,
                "message": validation.message,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/vsa/resonator")
    async def resonator_test(request: ResonatorTestRequest):
        try:
            query = vsa.encode_symbol(request.query_symbol)
            context = vsa.encode_symbol(request.context_symbol)
            target = vsa.encode_symbol(request.target_symbol)

            result, cosine, iterations = vsa.resonator_loop(query, context, target)

            validation = validator.validate_iterations(iterations)

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
    async def create_variant(
        original_id: str,
        skill_name: str,
    ):
        try:
            variant = dream.create_variant(original_id)
            return {
                "variant_id": variant.id,
                "original_id": variant.original_id,
                "k_lambda": variant.k_lambda,
                "max_iters": variant.max_iters,
                "created": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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

    @app.get("/dream/stats")
    async def get_dream_stats():
        stats = dream.get_statistics()
        return stats

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
    async def store_evidence(
        evidence_id: str,
        evidence_type: str,
        content: Dict[str, Any],
    ):
        try:
            evidence = l0_graph.store_evidence(evidence_id, evidence_type, content)
            return {
                "evidence_id": evidence.id,
                "type": evidence.type,
                "stored": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
        stats = l0_graph.get_statistics()
        return stats

    return app

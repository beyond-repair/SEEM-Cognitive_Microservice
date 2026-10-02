from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timezone
import json


class FailureType(str, Enum):
    UNBIND_FAILURE = "unbind_failure"
    SHACL_VIOLATION = "shacl_violation"
    EXECUTION_ERROR = "execution_error"
    SMT_UNSAT = "smt_unsat"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class NegativeSpike:
    route_id: str
    failure_type: FailureType
    cosine_similarity: Optional[float] = None
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "failure_type": self.failure_type.value,
            "cosine_similarity": self.cosine_similarity,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class RouteStatistics:
    route_id: str
    success_count: int = 0
    failure_count: int = 0
    avg_cosine_similarity: float = 0.0
    avg_iterations: int = 0
    negative_spike_count: int = 0
    last_spike_at: Optional[str] = None

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route_id": self.route_id,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "avg_cosine_similarity": self.avg_cosine_similarity,
            "avg_iterations": self.avg_iterations,
            "negative_spike_count": self.negative_spike_count,
            "last_spike_at": self.last_spike_at,
        }


class BaNELEngine:
    def __init__(
        self,
        rejection_threshold: float = 0.6,
        spike_decay_rate: float = 0.95,
        micro_dream_timeout_ms: float = 50.0,
    ):
        self.rejection_threshold = rejection_threshold
        self.spike_decay_rate = spike_decay_rate
        self.micro_dream_timeout_ms = micro_dream_timeout_ms

        self.negative_spikes: List[NegativeSpike] = []
        self.route_stats: Dict[str, RouteStatistics] = {}
        self.suppressed_routes: Dict[str, float] = {}

    def record_success(
        self,
        route_id: str,
        cosine_similarity: float,
        iterations: int,
    ) -> None:
        if route_id not in self.route_stats:
            self.route_stats[route_id] = RouteStatistics(route_id=route_id)

        stats = self.route_stats[route_id]
        stats.success_count += 1

        stats.avg_cosine_similarity = (
            (stats.avg_cosine_similarity * (stats.success_count - 1) + cosine_similarity)
            / stats.success_count
        )
        stats.avg_iterations = (
            (stats.avg_iterations * (stats.success_count - 1) + iterations)
            // stats.success_count
        )

        if route_id in self.suppressed_routes:
            del self.suppressed_routes[route_id]

    def record_failure(
        self,
        route_id: str,
        failure_type: FailureType,
        cosine_similarity: Optional[float] = None,
        error_message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if route_id not in self.route_stats:
            self.route_stats[route_id] = RouteStatistics(route_id=route_id)

        stats = self.route_stats[route_id]
        stats.failure_count += 1
        stats.negative_spike_count += 1
        stats.last_spike_at = datetime.now(timezone.utc).isoformat()

        spike = NegativeSpike(
            route_id=route_id,
            failure_type=failure_type,
            cosine_similarity=cosine_similarity,
            error_message=error_message,
            metadata=metadata or {},
        )
        self.negative_spikes.append(spike)

        suppression_level = self._calculate_suppression_level(route_id)
        self.suppressed_routes[route_id] = suppression_level

        should_trigger_micro_dream = suppression_level > self.rejection_threshold
        return should_trigger_micro_dream

    def _calculate_suppression_level(self, route_id: str) -> float:
        stats = self.route_stats.get(route_id)
        if not stats or stats.success_count + stats.failure_count == 0:
            return 0.0

        failure_rate = stats.failure_count / (stats.success_count + stats.failure_count)
        spike_factor = min(1.0, stats.negative_spike_count / 10.0)

        suppression = (failure_rate * 0.7) + (spike_factor * 0.3)
        return suppression

    def get_suppression_level(self, route_id: str) -> float:
        if route_id in self.suppressed_routes:
            level = self.suppressed_routes[route_id]
            level *= self.spike_decay_rate
            self.suppressed_routes[route_id] = level
            return level
        return 0.0

    def is_suppressed(self, route_id: str) -> bool:
        return self.get_suppression_level(route_id) > self.rejection_threshold

    def get_route_statistics(self, route_id: str) -> Optional[RouteStatistics]:
        return self.route_stats.get(route_id)

    def get_all_route_statistics(self) -> List[RouteStatistics]:
        return list(self.route_stats.values())

    def get_recent_spikes(
        self,
        route_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[NegativeSpike]:
        spikes = self.negative_spikes

        if route_id:
            spikes = [s for s in spikes if s.route_id == route_id]

        return spikes[-limit:]

    def clear_suppression(self, route_id: str) -> None:
        if route_id in self.suppressed_routes:
            del self.suppressed_routes[route_id]

    def decay_all_suppressions(self) -> None:
        for route_id in list(self.suppressed_routes.keys()):
            level = self.suppressed_routes[route_id]
            level *= self.spike_decay_rate
            if level < 0.01:
                del self.suppressed_routes[route_id]
            else:
                self.suppressed_routes[route_id] = level

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class SymbolType(str, Enum):
    ATOMIC = "atomic"
    COMPOSITE = "composite"
    ROLE = "role"
    FILLER = "filler"


@dataclass
class Symbol:
    id: str
    label: str
    type: SymbolType
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type.value,
            "metadata": self.metadata,
        }


@dataclass
class Role:
    name: str
    description: str = ""
    constraints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "constraints": self.constraints,
        }


@dataclass
class Filler:
    value: str
    type: str = "string"
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "type": self.type,
            "confidence": self.confidence,
        }


@dataclass
class Binding:
    role: str
    filler: str
    strength: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "filler": self.filler,
            "strength": self.strength,
        }


class MemSkillLevel(str, Enum):
    L0 = "l0_supersede_graph"
    L1 = "l1_reactive"
    L2 = "l2_cached"
    L3 = "l3_consolidated"


@dataclass
class MemSkill:
    id: str
    name: str
    level: MemSkillLevel
    bindings: List[Binding] = field(default_factory=list)
    fitness: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    created_at: str = ""
    last_used_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level.value,
            "bindings": [b.to_dict() for b in self.bindings],
            "fitness": self.fitness,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionResult:
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }

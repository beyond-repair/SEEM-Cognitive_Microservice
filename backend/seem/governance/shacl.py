from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ConstraintType(str, Enum):
    INVERTIBILITY = "invertibility"
    RESONATOR_ITERATIONS = "resonator_iterations"
    DOMAIN_RULE = "domain_rule"
    SOVEREIGNTY = "sovereignty"
    SYNTAX = "syntax"


class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    VIOLATION = "violation"


@dataclass
class ValidationResult:
    constraint_id: str
    constraint_type: ConstraintType
    passed: bool
    severity: SeverityLevel
    message: str = ""
    actual_value: Optional[Any] = None
    expected_value: Optional[Any] = None
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "constraint_type": self.constraint_type.value,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "actual_value": str(self.actual_value),
            "expected_value": str(self.expected_value),
            "timestamp": self.timestamp,
        }


@dataclass
class Constraint:
    id: str
    type: ConstraintType
    name: str
    description: str = ""
    severity: SeverityLevel = SeverityLevel.WARNING
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "parameters": self.parameters,
        }


class SHACLValidator:
    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}
        self.validation_history: List[ValidationResult] = []
        self._init_default_constraints()

    def _init_default_constraints(self):
        self.add_constraint(
            Constraint(
                id="invertibility_threshold",
                type=ConstraintType.INVERTIBILITY,
                name="Minimum Invertibility",
                description="Cosine similarity after re-binding must be >= 0.92",
                severity=SeverityLevel.ERROR,
                parameters={"min_cosine": 0.92},
            )
        )

        self.add_constraint(
            Constraint(
                id="max_resonator_iterations",
                type=ConstraintType.RESONATOR_ITERATIONS,
                name="Maximum Resonator Iterations",
                description="Resonator loop iterations must not exceed 7",
                severity=SeverityLevel.WARNING,
                parameters={"max_iterations": 7},
            )
        )

        self.add_constraint(
            Constraint(
                id="data_residency",
                type=ConstraintType.SOVEREIGNTY,
                name="Local Data Residency",
                description="All data must remain local, offline processing only",
                severity=SeverityLevel.ERROR,
                parameters={"local_only": True},
            )
        )

    def add_constraint(self, constraint: Constraint) -> None:
        self.constraints[constraint.id] = constraint

    def validate_invertibility(
        self,
        cosine_similarity: float,
        threshold: float = 0.92,
    ) -> ValidationResult:
        passed = cosine_similarity >= threshold
        severity = SeverityLevel.ERROR if not passed else SeverityLevel.INFO

        result = ValidationResult(
            constraint_id="invertibility_threshold",
            constraint_type=ConstraintType.INVERTIBILITY,
            passed=passed,
            severity=severity,
            message=f"Cosine similarity: {cosine_similarity:.4f} {'≥' if passed else '<'} {threshold}",
            actual_value=cosine_similarity,
            expected_value=threshold,
        )

        self.validation_history.append(result)
        return result

    def validate_iterations(
        self,
        actual_iterations: int,
        max_iterations: int = 7,
    ) -> ValidationResult:
        passed = actual_iterations <= max_iterations
        severity = SeverityLevel.WARNING if not passed else SeverityLevel.INFO

        result = ValidationResult(
            constraint_id="max_resonator_iterations",
            constraint_type=ConstraintType.RESONATOR_ITERATIONS,
            passed=passed,
            severity=severity,
            message=f"Iterations: {actual_iterations} {'≤' if passed else '>'} {max_iterations}",
            actual_value=actual_iterations,
            expected_value=max_iterations,
        )

        self.validation_history.append(result)
        return result

    def validate_local_residency(
        self,
        data_location: str,
    ) -> ValidationResult:
        passed = data_location.lower() == "local"
        severity = SeverityLevel.ERROR if not passed else SeverityLevel.INFO

        result = ValidationResult(
            constraint_id="data_residency",
            constraint_type=ConstraintType.SOVEREIGNTY,
            passed=passed,
            severity=severity,
            message=f"Data location: {data_location} {'is' if passed else 'is NOT'} local",
            actual_value=data_location,
            expected_value="local",
        )

        self.validation_history.append(result)
        return result

    def validate_domain_rule(
        self,
        rule_id: str,
        condition: bool,
        message: str = "",
    ) -> ValidationResult:
        result = ValidationResult(
            constraint_id=rule_id,
            constraint_type=ConstraintType.DOMAIN_RULE,
            passed=condition,
            severity=SeverityLevel.ERROR if not condition else SeverityLevel.INFO,
            message=message or f"Domain rule '{rule_id}' {'passed' if condition else 'failed'}",
        )

        self.validation_history.append(result)
        return result

    def validate_syntax(
        self,
        structure: Dict[str, Any],
    ) -> ValidationResult:
        passed = True
        errors = []

        if "bindings" not in structure:
            passed = False
            errors.append("Missing 'bindings' field")

        if "id" not in structure:
            passed = False
            errors.append("Missing 'id' field")

        result = ValidationResult(
            constraint_id="syntax_check",
            constraint_type=ConstraintType.SYNTAX,
            passed=passed,
            severity=SeverityLevel.ERROR if not passed else SeverityLevel.INFO,
            message="; ".join(errors) if errors else "Syntax valid",
        )

        self.validation_history.append(result)
        return result

    def validate_route(
        self,
        route_id: str,
        cosine_similarity: float,
        iterations: int,
        bindings: List[Dict[str, Any]],
    ) -> List[ValidationResult]:
        results = []

        results.append(self.validate_invertibility(cosine_similarity))
        results.append(self.validate_iterations(iterations))
        results.append(self.validate_local_residency("local"))

        structure = {
            "id": route_id,
            "bindings": bindings,
        }
        results.append(self.validate_syntax(structure))

        return results

    def get_violations(self) -> List[ValidationResult]:
        return [
            r for r in self.validation_history
            if r.severity in (SeverityLevel.ERROR, SeverityLevel.VIOLATION)
        ]

    def get_recent_validations(self, limit: int = 20) -> List[ValidationResult]:
        return self.validation_history[-limit:]

    def clear_history(self) -> None:
        self.validation_history = []

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.validation_history)
        if total == 0:
            return {
                "total_validations": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0,
            }

        passed = sum(1 for r in self.validation_history if r.passed)
        return {
            "total_validations": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
        }

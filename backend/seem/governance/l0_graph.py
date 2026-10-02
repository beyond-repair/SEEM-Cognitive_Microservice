from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from enum import Enum


class SupersedenceReason(str, Enum):
    ROUTE_MUTATION = "route_mutation"
    SKILL_CONSOLIDATION = "skill_consolidation"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    MANUAL_OVERRIDE = "manual_override"
    ARCHIVAL = "archival"


@dataclass
class Evidence:
    id: str
    type: str
    content: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "content": self.content,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class SupersedenceRecord:
    id: str
    superseded_evidence_id: str
    superseding_evidence_id: str
    reason: SupersedenceReason
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "superseded_evidence_id": self.superseded_evidence_id,
            "superseding_evidence_id": self.superseding_evidence_id,
            "reason": self.reason.value,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


class SupersededGraph:
    def __init__(self):
        self.evidence: Dict[str, Evidence] = {}
        self.supersedence_records: List[SupersedenceRecord] = []
        self.active_evidence: Set[str] = set()
        self.archive: Set[str] = set()

    def store_evidence(
        self,
        evidence_id: str,
        evidence_type: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Evidence:
        evidence = Evidence(
            id=evidence_id,
            type=evidence_type,
            content=content,
            metadata=metadata or {},
        )
        self.evidence[evidence_id] = evidence
        self.active_evidence.add(evidence_id)
        return evidence

    def supersede_evidence(
        self,
        old_evidence_id: str,
        new_evidence_id: str,
        reason: SupersedenceReason,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SupersedenceRecord:
        if old_evidence_id not in self.evidence:
            raise ValueError(f"Evidence {old_evidence_id} not found")

        if new_evidence_id not in self.evidence:
            raise ValueError(f"Evidence {new_evidence_id} not found")

        record_id = f"supersede_{len(self.supersedence_records)}"
        record = SupersedenceRecord(
            id=record_id,
            superseded_evidence_id=old_evidence_id,
            superseding_evidence_id=new_evidence_id,
            reason=reason,
            metadata=metadata or {},
        )

        self.supersedence_records.append(record)

        self.active_evidence.discard(old_evidence_id)

        return record

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self.evidence.get(evidence_id)

    def get_active_evidence(self, evidence_type: Optional[str] = None) -> List[Evidence]:
        active = [
            self.evidence[eid] for eid in self.active_evidence
            if eid in self.evidence
        ]

        if evidence_type:
            active = [e for e in active if e.type == evidence_type]

        return sorted(active, key=lambda e: e.created_at, reverse=True)

    def get_evidence_history(self, evidence_id: str) -> Dict[str, Any]:
        if evidence_id not in self.evidence:
            return {}

        supersedes = [
            r for r in self.supersedence_records
            if r.superseding_evidence_id == evidence_id
        ]
        superseded_by = [
            r for r in self.supersedence_records
            if r.superseded_evidence_id == evidence_id
        ]

        return {
            "evidence": self.evidence[evidence_id].to_dict(),
            "supersedes": [r.to_dict() for r in supersedes],
            "superseded_by": [r.to_dict() for r in superseded_by],
            "is_active": evidence_id in self.active_evidence,
        }

    def get_supersedence_chain(self, evidence_id: str) -> List[str]:
        chain = [evidence_id]
        current = evidence_id

        while True:
            superseding = [
                r for r in self.supersedence_records
                if r.superseded_evidence_id == current
            ]
            if not superseding:
                break
            current = superseding[0].superseding_evidence_id
            chain.append(current)

        return chain

    def archive_evidence(self, evidence_id: str) -> bool:
        if evidence_id not in self.evidence:
            return False

        self.active_evidence.discard(evidence_id)
        self.archive.add(evidence_id)
        return True

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_evidence": len(self.evidence),
            "active_evidence": len(self.active_evidence),
            "archived_evidence": len(self.archive),
            "supersedence_records": len(self.supersedence_records),
            "evidence_types": list(set(e.type for e in self.evidence.values())),
        }

    def get_recent_supersedences(self, limit: int = 10) -> List[SupersedenceRecord]:
        return self.supersedence_records[-limit:]

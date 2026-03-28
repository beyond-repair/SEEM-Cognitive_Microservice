# SEEM 2.0: Sovereign Episodic Experience Microservice

A local-first symbolic cognitive engine that turns raw interaction logs into executable **MemSkills** through high-dimensional vector algebra, Bayesian negative learning, and dream-phase consolidation.

**Zero external dependencies. Fully offline. Completely auditable.**

## What is SEEM 2.0?

SEEM is a sovereign, fully offline system that learns symbolic skills from lived experience. It uses:

- **Resonator VSA**: Clean, invertible symbolic composition in ℂ^16384
- **BaNEL**: Bayesian negative evidence learning (failures drive improvement)
- **Dream Phase**: Background evolutionary consolidation into L3 MemSkills
- **SHACL Governance**: Declarative constraints + audit trails
- **L0 Supersede Graph**: Immutable evidence base (nothing deleted, only superseded)

The result: a system that **learns like humans** (from mistakes, consolidates knowledge) while remaining **fully verifiable and user-controlled**.

## Key Features

✅ **Invertible Symbolic Algebra**
Bind and unbind role-filler pairs with >92% fidelity using complex hypervectors

✅ **Autonomous Failure-Driven Learning**
Every failure triggers a "negative spike" that suppresses bad routes and triggers inline repairs

✅ **Skill Consolidation**
Successful routes evolve through crossover/mutation until they're reliable enough for L3 promotion

✅ **Complete Auditability**
Every decision tracked in an immutable Supersede Graph — query why any route was changed

✅ **Local-First**
No cloud, no API calls, no data export. All computation on your device

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API runs on `http://localhost:8000`

**Key endpoints:**
- `GET /health` — System status
- `POST /vsa/bind` — Bind symbols
- `POST /banel/record-failure` — Record failure + trigger learning
- `POST /dream/run-cycle` — Run evolutionary consolidation
- `GET /l0/stats` — Evidence audit trail

### Frontend

```bash
npm install
npm run dev
```

UI opens on `http://localhost:5173`

**Tabs:**
- **Dashboard**: System metrics and health
- **Resonator VSA**: Test symbol binding and invertibility
- **BaNEL Monitor**: Watch failure learning in action
- **Dream Phase**: See skill consolidation progress
- **L0 Graph**: Audit all evidence and supersedences

## Architecture at a Glance

```
Intent arrives
    ↓
Encode to hypervectors (VSA)
    ↓
SHACL validation (governance)
    ↓
Execute via plugins
    ↓
Success? → Store in L0 → Background Dream consolidation → L3 MemSkill
Failure? → Record spike → Micro-Dream mutation → Re-test inline
```

## Core Concepts

### Resonator VSA

Symbols represented as complex hypervectors in ℂ^16384. Operations:

```python
# Bind role and filler
bound = role ⊙ conjugate(filler)

# Unbind with resonance (iterative improvement)
filler_recovered, cosine_sim, iters = vsa.unbind_with_resonance(bound, role)

# Test invertibility
invertibility = vsa.measure_invertibility(role, filler)  # Target: ≥ 0.92
```

### BaNEL Learning

Failures record "negative spikes" that suppress bad routes:

```python
# On failure:
should_micro_dream = banel.record_failure(
    route_id="route_001",
    failure_type=FailureType.UNBIND_FAILURE,
    cosine_similarity=0.88
)
# If suppression > threshold → inline mutation + re-test
```

### Dream Phase Consolidation

Background evolutionary selection of best-performing routes:

```python
# Periodically:
new_generation = dream.run_dream_cycle(original_id="route_001")
skill = dream.consolidate_skill(original_id="route_001", skill_name="execute_task")
# Promotes high-fitness routes to L3 MemSkills
```

### L0 Supersede Graph

Immutable evidence base where nothing is deleted, only superseded:

```python
# Store evidence
l0_graph.store_evidence("route_001", "executed_route", {...})

# When a better variant exists:
l0_graph.supersede_evidence(
    old_id="route_001",
    new_id="route_001_v2",
    reason=SupersedenceReason.PERFORMANCE_IMPROVEMENT
)

# Query full history anytime
history = l0_graph.get_evidence_history("route_001")
```

## Project Structure

```
project/
├── backend/
│   ├── seem/
│   │   ├── core/
│   │   │   ├── vsa.py               # Resonator VSA kernel
│   │   │   └── types.py              # Core data structures
│   │   ├── learning/
│   │   │   ├── banel.py              # Negative evidence learning
│   │   │   └── dream.py              # Evolutionary consolidation
│   │   ├── governance/
│   │   │   ├── shacl.py              # SHACL constraint validation
│   │   │   └── l0_graph.py           # Immutable evidence base
│   │   ├── plugins/
│   │   │   └── executor.py           # Async plugin execution
│   │   └── api/
│   │       └── server.py             # FastAPI endpoints
│   ├── main.py                       # Backend entry point
│   └── requirements.txt
├── src/
│   ├── App.tsx                       # React application
│   └── components/
│       ├── Dashboard.tsx             # System overview
│       ├── VSAExplorer.tsx           # VSA testing
│       ├── BaNELMonitor.tsx          # Learning monitoring
│       ├── DreamPhaseViewer.tsx      # Consolidation viewer
│       └── L0GraphViewer.tsx         # Evidence audit
├── BLUEPRINT.md                      # Full technical architecture
└── README.md                         # This file
```

## Example: Symbol Binding

```python
from seem.core import ResonatorVSA

vsa = ResonatorVSA(dimension=16384, max_iterations=7)

# Create symbols
action = vsa.encode_symbol("action_execute")
task = vsa.encode_symbol("task_process")

# Bind them
bound = action.bind(task)
print(f"Bound vector norm: {bound.norm}")

# Unbind with resonance
unbound, cosine_sim, iters = vsa.unbind_with_resonance(bound, action)
print(f"Unbind accuracy: {cosine_sim:.4f} (target: ≥0.92)")
print(f"Iterations used: {iters}/{vsa.max_iterations}")
```

## Example: Learning from Failure

```python
from seem.learning import BaNELEngine, FailureType

banel = BaNELEngine(rejection_threshold=0.6)

# First execution: success
banel.record_success("route_001", cosine_similarity=0.945, iterations=5)

# Second execution: failure
should_micro_dream = banel.record_failure(
    route_id="route_001",
    failure_type=FailureType.UNBIND_FAILURE,
    cosine_similarity=0.88,
    error_message="Cosine below threshold"
)

if should_micro_dream:
    print("Suppression exceeded! Triggering Micro-Dream...")
    # Inline variant creation + mutation + re-test
```

## Example: Evidence Audit

```python
from seem.governance import SupersededGraph, SupersedenceReason

l0 = SupersededGraph()

# Store initial evidence
l0.store_evidence("route_001", "executed_route", {"result": "success"})

# Later: improved version
l0.store_evidence("route_001_v2", "executed_route", {"result": "success", "improved": True})

# Supersede the old evidence
l0.supersede_evidence(
    old_evidence_id="route_001",
    new_evidence_id="route_001_v2",
    reason=SupersedenceReason.PERFORMANCE_IMPROVEMENT
)

# Audit trail
history = l0.get_evidence_history("route_001")
print(f"Is active: {history['is_active']}")  # False
print(f"Superseded by: {history['superseded_by']}")  # [SupersedenceRecord]
```

## Validation & Governance

SHACL constraints enforce:

- **Invertibility**: Cosine similarity ≥ 0.92 after re-binding
- **Iterations**: Resonator loops ≤ 7 (enforced)
- **Residency**: All data stays local (no external services)
- **Syntax**: Valid structure with required fields
- **Domain Rules**: Custom per-application constraints

Violations trigger BaNEL negative spikes → learning loop.

## Performance Specifications

| Metric | Value | Notes |
|--------|-------|-------|
| VSA Dimension | 16,384 | Complex (32KB per vector) |
| Invertibility Target | ≥ 0.92 | Enforced by SHACL |
| Max Resonator Iterations | 7 | Hard limit |
| Micro-Dream Timeout | 50ms | Inline repair |
| Elite Population Size | 5 | Dream consolidation |
| Consolidation Fitness | ≥ 0.75 | L3 promotion threshold |

## Roadmap

**Immediate (v2.0.1)**
- [ ] Supabase persistence for L0 Graph
- [ ] Extended SHACL constraint library
- [ ] Synthetic benchmarks (5+ domains)

**Near-term (v2.1)**
- [ ] SMT/Z3 solver integration
- [ ] HDDL planning language
- [ ] Telegram orchestration bridge

**Future (v2.2+)**
- [ ] Distributed peer-to-peer sync
- [ ] Multi-user coordination
- [ ] Real-world task evaluation

## Why SEEM 2.0?

### For Researchers
Study symbolic learning grounded in execution. Every decision is auditable and verifiable.

### For Privacy-Conscious Users
Your skills stay on your device. No cloud, no telemetry, no API calls.

### For System Builders
Build AI systems that learn from failure, consolidate knowledge autonomously, and never lose data.

## References

- **VSA Theory**: Kanerva, P. (2009). *Hyperdimensional Computing* — sparse distributed representations
- **BaNEL**: Inspired by Bayesian inverse reinforcement learning and negative example mining
- **SHACL**: W3C Shapes Constraint Language — declarative RDF validation
- **HDDL/PDDL+**: Ghallab et al., *Automated Planning and Acting* — hierarchical planning

## License

MIT

## Contact & Contributing

This is an experimental research system. Bug reports, architectural feedback, and theoretical contributions welcome.

---

**Built with intention. Auditable by design. Local by default.**

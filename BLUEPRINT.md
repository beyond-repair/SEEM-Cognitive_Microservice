# SEEM 2.0 Blueprint: Sovereign Episodic Experience Microservice

## Executive Summary

SEEM 2.0 is a local-first symbolic cognitive engine that transforms raw interaction logs into executable **MemSkills** through three core systems:

1. **Resonator VSA** - High-dimensional complex hypervector algebra for clean, invertible symbolic composition
2. **BaNEL + Dream Phase** - Autonomous learning that turns failures into evolutionary improvements
3. **SHACL Governance + L0 Supersede Graph** - Declarative constraints and immutable auditability

The system is **fully offline**, **user-controlled**, and **non-destructive** - nothing is ever deleted, only superseded.

---

## Architecture Overview

### Layer Stack

```
┌─────────────────────────────────────┐
│  L3: Consolidated MemSkills         │ (executable, verified)
├─────────────────────────────────────┤
│  L2: Cached Reactive Routes         │ (fast, tested)
├─────────────────────────────────────┤
│  L1: Raw Execution Events           │ (immediate)
├─────────────────────────────────────┤
│  L0: Supersede Graph (immutable)    │ (ground truth)
└─────────────────────────────────────┘
   ↓
Resonator VSA + BaNEL + SHACL Validation
```

---

## 1. Representation: Resonator VSA

### Core Concept

All symbols, roles, fillers, and bindings are represented as **complex hypervectors** in ℂ^16384:

```
v = [a₁ + ib₁, a₂ + ib₂, ..., a₁₆₃₈₄ + ib₁₆₃₈₄]
```

### Operations

#### Binding
```
bound = role ⊙ conjugate(filler)
(element-wise complex multiplication)
```

Encodes role-filler pairs into a single vector while preserving structure.

#### Unbinding
```
filler = role ⊙ conjugate(bound)
```

Recovers the filler from a bound pair. Uses iterative **resonator loops** to improve accuracy.

#### Resonator Loop (Core Innovation)
1. Start with query vector
2. Bundle with context via superposition
3. Measure cosine similarity to target
4. If not ≥0.92, perturb and repeat (max 7 iterations)
5. Return best result + similarity + iteration count

### Invertibility Guarantee

**Target**: Cosine similarity ≥ 0.92 after re-binding
```
role ⊙ conjugate(role ⊙ conjugate(filler)) ≈ filler (cosine ≥ 0.92)
```

This is enforced by SHACL validation before promotion to L2.

### Sparsity Injection

Controlled zero-insertion (10% by default) keeps symbolic representations noise-resistant and improves compositionality at scale.

---

## 2. Governance: SHACL + Planned SMT/Z3

### SHACL Constraints (Active)

Defined declaratively in the validation layer:

- **Invertibility Constraint**: `cosine_similarity >= 0.92`
- **Resonator Iterations**: `iterations <= 7`
- **Data Residency**: `location == "local"`
- **Syntax Validation**: Structure must have `id` and `bindings`
- **Domain Rules**: Custom per-application rules (e.g., no cross-tenant data)

### Validation Flow

```python
validations = validator.validate_route(
    route_id="route_001",
    cosine_similarity=0.945,
    iterations=5,
    bindings=[...]
)
# Returns list of ValidationResult objects
# All must pass for L1→L2 promotion
```

### SMT/Z3 Integration (Planned)

For hybrid domains requiring numeric/logical reasoning (e.g., database migrations with resource constraints):

- **Check**: PDDL+-style preconditions, effects, and ordering
- **Verify**: Constraint satisfiability (SAT/UNSAT)
- **Integrate**: Route verification artifacts stored in L0

Flow:
```
Route proposal → SMT solver → sat ✓ (promote) | unsat → BaNEL spike
```

---

## 3. Learning & Evolution: BaNEL + Dream Phase

### BaNEL: Bayesian Negative Evidence Learning

Every failure is a strong learning signal:

**Failure Types**:
- Unbind cosine < 0.92
- SHACL violation
- Execution error
- SMT unsat
- Timeout

**Mechanism**:
1. Record failure as **NegativeSpike**
2. Calculate **suppression level**: `0.7 * failure_rate + 0.3 * spike_factor`
3. If suppression > **rejection threshold (0.6)** → trigger **Micro-Dream**

**Micro-Dream** (inline, <50ms):
- Mutate: k_lambda, max_iters, hypervector perturbations
- Re-test on held-out evidence
- Promote if fitness improves

### Dream Phase: Skill Consolidation

Background evolutionary consolidation of successful routes:

**Process**:
1. **Select Elite**: Top 5 routes by success_rate × fitness
2. **Crossover**: Recombine elite parameter sets
3. **Mutate**: Perturb k_lambda, max_iters for exploration
4. **Evaluate**: Test on held-out data
5. **Consolidate**: Routes with fitness ≥ 0.75 → L3 MemSkills

**Fitness Function**:
```
Fitness = 0.6 * unbind_cosine + 0.3 * iters_saved + 0.1 * domain_match
```

**Output**: Immutable L3 MemSkills stored in L0 Supersede Graph

---

## 4. Auditability: L0 Supersede Graph

### Core Principle
Nothing is ever deleted. Everything is superseded with a reason.

### Structure

```python
Evidence {
  id: string
  type: string (route, skill, policy, etc.)
  content: dict
  created_at: timestamp
}

SupersedenceRecord {
  old_evidence_id: string
  new_evidence_id: string
  reason: SupersedenceReason
  created_at: timestamp
}
```

### Supersedence Reasons
- `ROUTE_MUTATION`: Variant improved the original
- `SKILL_CONSOLIDATION`: Promoted to L3
- `PERFORMANCE_IMPROVEMENT`: Better fitness achieved
- `MANUAL_OVERRIDE`: User-initiated change
- `ARCHIVAL`: No longer active

### Audit Trail
At any point, retrieve the full history of any evidence:

```python
history = l0_graph.get_evidence_history(evidence_id)
# Returns:
# {
#   "evidence": {...},
#   "supersedes": [records],
#   "superseded_by": [records],
#   "is_active": bool
# }
```

---

## 5. End-to-End Execution Flow

### 1. Intent Arrives
User sends high-level intent (local, via CLI/API).

### 2. VSA Encoding
Intent is bound into hypervectors:
```python
query = vsa.encode_symbol("user_intent")
context = vsa.encode_symbol("system_state")
route = vsa.compose_bindings([("role1", "filler1"), ...])
```

### 3. SHACL Validation
```python
results = validator.validate_route(
    route_id, cosine_sim, iterations, bindings
)
if any(r.severity == "error" and not r.passed):
    # Reject, trigger BaNEL spike
```

### 4. Plugin Execution
Matched plugin executes the route:
```python
result = await executor.execute_plugin(
    plugin_id="skill_execute",
    input_data={...}
)
```

### 5. Outcome Recording

**Success**:
```python
banel.record_success(
    route_id="route_001",
    cosine_similarity=0.945,
    iterations=5
)
```

**Failure**:
```python
should_micro_dream = banel.record_failure(
    route_id="route_001",
    failure_type=FailureType.UNBIND_FAILURE,
    cosine_similarity=0.88
)
if should_micro_dream:
    # Inline variant mutation and re-test
    micro_dream(route_id)
```

### 6. L0 Storage
All evidence stored in Supersede Graph:
```python
l0_graph.store_evidence(
    evidence_id="route_001_v1",
    evidence_type="executed_route",
    content={...}
)
```

### 7. Background Dream Consolidation
Periodically, run evolutionary consolidation:
```python
dream.run_dream_cycle(original_id="route_001")
skill = dream.consolidate_skill(
    original_id="route_001",
    skill_name="process_user_request"
)
# Promotes to L3 if fitness ≥ 0.75
```

---

## Implementation Status: Genesis v1.0.0

### ✅ Implemented (Operational)

| Component | Status | Details |
|-----------|--------|---------|
| **Resonator VSA** | ✓ | 16384-dim complex hypervectors, binding/unbinding, resonator loops |
| **Hypervector Algebra** | ✓ | Element-wise binding, conjugate unbinding, sparsity injection |
| **BaNEL Engine** | ✓ | Negative spike tracking, suppression calculation, rejection threshold |
| **Micro-Dreams** | ✓ | Inline variant mutation and re-test (<50ms) |
| **Dream Phase** | ✓ | Elite selection, crossover, mutation, consolidation |
| **SHACL Validator** | ✓ | Invertibility, iteration caps, syntax, domain rules |
| **L0 Supersede Graph** | ✓ | Immutable evidence storage, supersedence tracking |
| **REST API (FastAPI)** | ✓ | All core endpoints operational |
| **Plugin Executor** | ✓ | Async plugin registration and execution |
| **React Frontend** | ✓ | Dashboard, VSA explorer, BaNEL monitor, Dream viewer |

### ⏳ Planned (High Priority)

| Component | ETA | Details |
|-----------|-----|---------|
| **SMT/Z3 Integration** | Soon | PDDL+ verification, constraint solving |
| **HDDL Planning** | Soon | Hierarchical decomposition, skill reuse |
| **Real-World Benchmarks** | Soon | Non-synthetic task evaluation |
| **Telegram Bridge** | Soon | Orchestration via messaging |
| **Persistence Layer** | Soon | Supabase integration for L0 storage |

---

## File Structure

```
seem2/
├── backend/
│   ├── seem/
│   │   ├── core/
│   │   │   ├── vsa.py          # Resonator VSA kernel
│   │   │   ├── types.py         # Core data types
│   │   ├── learning/
│   │   │   ├── banel.py         # Bayesian negative learning
│   │   │   ├── dream.py         # Dream phase consolidation
│   │   ├── governance/
│   │   │   ├── shacl.py         # SHACL validation
│   │   │   ├── l0_graph.py      # Supersede graph
│   │   ├── plugins/
│   │   │   ├── executor.py      # Plugin execution engine
│   │   ├── api/
│   │   │   ├── server.py        # FastAPI server
│   │   └── __init__.py
│   ├── main.py                  # Entry point
│   └── requirements.txt
├── src/
│   ├── App.tsx                  # React app
│   └── components/
│       ├── Dashboard.tsx         # System overview
│       ├── VSAExplorer.tsx       # VSA testing
│       ├── BaNELMonitor.tsx      # Learning monitor
│       ├── DreamPhaseViewer.tsx  # Consolidation viewer
│       └── L0GraphViewer.tsx     # Evidence audit
├── BLUEPRINT.md                 # This document
├── README.md                    # Quick start
└── package.json                 # Node dependencies
```

---

## Running SEEM 2.0

### Backend (Python)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Starts FastAPI server on `http://localhost:8000`

### Frontend (React)
```bash
npm install
npm run dev
```
Opens UI on `http://localhost:5173`

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | System health check |
| `/vsa/bind` | POST | Bind role and filler symbols |
| `/vsa/invertibility` | POST | Test invertibility threshold |
| `/banel/record-failure` | POST | Record failure + trigger learning |
| `/dream/run-cycle` | POST | Run evolutionary consolidation |
| `/l0/store-evidence` | POST | Store evidence with audit trail |

---

## Why This Stack Is Powerful

### 1. Resonator VSA
- **Clean algebra**: No embedding drift, true compositionality
- **Drift-resistant**: Hypervectors stay normalized, noise-proof
- **Invertible**: Recoverable role-filler pairs (>0.92 accuracy)
- **Local-first**: All computation on personal hardware

### 2. BaNEL + Dream Phase
- **Autonomous learning**: Failures drive mutation, not human rules
- **Grounded in evidence**: Every decision backed by execution data
- **Self-healing**: Micro-dreams fix problems in-place
- **Skill consolidation**: Successful routes become permanent, verifiable knowledge

### 3. SHACL + SMT
- **Lightweight enforcement**: SHACL constraints require no solver overhead
- **Extensible**: SMT/Z3 for complex domains (numeric, logical)
- **Declarative**: Rules expressed as RDF shapes, not code

### 4. L0 Supersede Graph
- **Immutable**: Full accountability, no data loss
- **Auditable**: Query why any evidence was superseded
- **Sovereign**: User owns all knowledge, nothing leaves device

---

## Roadmap

### Q2 2026: Core Stability
- [ ] Supabase persistence integration
- [ ] Extended SHACL constraint library
- [ ] Telegram orchestration bridge
- [ ] Synthetic benchmarks (5+ domains)

### Q3 2026: SMT/Z3 & HDDL
- [ ] Full SMT solver integration
- [ ] PDDL+ planning language
- [ ] Hierarchical skill decomposition
- [ ] Real-world task evaluation

### Q4 2026: Production Hardening
- [ ] Distributed L0 graph sync (peer-to-peer)
- [ ] Multi-user/multi-agent coordination
- [ ] Performance optimization (vectorization)
- [ ] Security audit & hardening

---

## References

- VSA Theory: Kanerva, P. (2009). *Hyperdimensional Computing*
- BaNEL: Inspired by Bayesian inverse reinforcement learning
- SHACL: W3C Shapes Constraint Language
- HDDL/PDDL+: Ghallab et al., *Automated Planning and Acting*

---

## License

MIT - See LICENSE file

---

## Contact

SEEM 2.0 Development Team
Local-First Symbolic Cognition
March 2026

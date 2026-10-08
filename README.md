<div align="center">

[![Lifecycle](https://img.shields.io/badge/●_SUPERSEDED-f59e0b?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)
[![Claim](https://img.shields.io/badge/Claim_0-22c55e?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance/blob/main/docs/CLAIM_VALIDATION.md)
[![Governance](https://img.shields.io/badge/ADL--Governance-7c3aed?style=for-the-badge&labelColor=0f0f23)](https://github.com/beyond-repair/ADL-Governance)

```
LIFECYCLE   SUPERSEDED
CLAIM       0
SUCCESSOR   sovereign-clean-room
```

</div>

> **SUPERSEDED.** Canonical successor: [sovereign-clean-room](https://github.com/beyond-repair/sovereign-clean-room). This repository is the Vite + FastAPI twin (underscore name). It is not the offline CLI in `SEEM-Cognitive-Microservice` (hyphen). No new feature work beyond keeping this sketch runnable.

# SEEM 2.0 Cognitive Microservice (Claim-0 sketch)

Local dashboard and HTTP API for an in-memory toy:

- FHRR phasors (element-wise bind, conjugate unbind) at dimension 16384
- BaNEL failure counters and a suppression score
- a small genetic dream cycle over `k_lambda` and `max_iters`
- numeric gates in a class named `SHACLValidator` (it does **not** run RDF/SHACL)
- an L0 evidence log that supersedes instead of deleting

State lives in the API process. Restart clears it. This is not a mind, a council, or a scientific instrument. The 0.92 invertibility figure is a configured comparison against the cosine this process measures.

## Requirements

- Python 3.11+ (tested on 3.13)
- Node.js 20+ and npm 9+

No API keys. Copy `.env.example` to `.env` only if you need a non-default host or port.

## Install

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
npm install
```

## CI

`.github/workflows/kernel.yml` runs `pytest -q` from `backend/` on Python 3.11.
A green run is an Actions conclusion. It does not raise the claim level above 0.

## Test

From `backend/` with the venv active:

```bash
cd backend
pytest -q
python demo.py
```

`demo.py` prints `min_invertibility` over 8 trials at dimension 16384. That number is measured. The configured gate is 0.92.

## Run

Terminal A, from `backend/` with the venv active:

```bash
python main.py
```

You should see Uvicorn on `http://127.0.0.1:8000`.

Terminal B, from the repo root:

```bash
npm run dev
```

Open the printed local URL (default `http://127.0.0.1:5173`). The header dot is green when `GET /health` returns 200. Use the VSA tab to bind two ids, the BaNEL tab to record a failure, Dream to create a variant, and L0 to store evidence.

Production bundle:

```bash
npm run build
```

The built UI still calls `http://127.0.0.1:8000` unless you set `VITE_API_BASE` before `npm run build`.

## API checks

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST "http://127.0.0.1:8000/vsa/bind?role_id=action_test&filler_id=target_test"
curl -s -X POST "http://127.0.0.1:8000/vsa/invertibility?role_id=action_test&filler_id=target_test"
curl -s -X POST http://127.0.0.1:8000/banel/record-failure \
  -H 'Content-Type: application/json' \
  -d '{"route_id":"route_001","failure_type":"unbind_failure","cosine_similarity":0.88,"error_message":"Below threshold"}'
curl -s http://127.0.0.1:8000/banel/routes
curl -s -X POST "http://127.0.0.1:8000/dream/create-variant?original_id=route_001&skill_name=test_skill"
curl -s http://127.0.0.1:8000/l0/stats
```

`/health` includes `measured_invertibility` from a 256-d probe, separate from the service codebook.

## Docs map

- `INSTALLATION.md` — setup, curls, and what is not implemented
- `STARTUP.md` — short run path
- `BLUEPRINT.md` and `MANIFEST.md` — original design notes. They over-claim. Trust the README and the pytest output.

---

<div align="center">

**REWRITE · BUILD · TRANSCEND**

Governing source: [ADL-Governance](https://github.com/beyond-repair/ADL-Governance) · [Claim levels 0–5](https://github.com/beyond-repair/ADL-Governance/blob/main/docs/CLAIM_VALIDATION.md)

</div>

# SEEM 2.0 Installation & Setup Guide

## System Requirements

- **Python**: 3.10+
- **Node.js**: 18+
- **npm**: 9+
- **OS**: Linux, macOS, or Windows with WSL2

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
# From project root
npm install
```

### 3. Verify Installation

**Check Python dependencies:**
```bash
python -c "import numpy, scipy, pydantic, fastapi; print('All dependencies OK')"
```

**Check Node dependencies:**
```bash
npm list react react-dom lucide-react
```

## Running SEEM 2.0

### Start Backend

```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Start Frontend (in another terminal)

```bash
npm run dev
```

Expected output:
```
  VITE v5.4.8  ready in 120 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

### Verify System Health

Open browser: `http://localhost:5173`

You should see:
- Green "Connected" indicator in top-right
- Dashboard with system metrics
- Navigation tabs for VSA, BaNEL, Dream, L0

## API Testing

### Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "vsa": "operational",
    "banel": "operational",
    "dream_phase": "operational",
    "shacl": "operational",
    "l0_graph": "operational"
  }
}
```

### Test VSA Binding

```bash
curl -X POST "http://localhost:8000/vsa/bind?role_id=action_test&filler_id=target_test"
```

Response:
```json
{
  "role_id": "action_test",
  "filler_id": "target_test",
  "bound": true,
  "dimension": 16384
}
```

### Test Invertibility

```bash
curl -X POST "http://localhost:8000/vsa/invertibility?role_id=action_test&filler_id=target_test"
```

## Project Structure After Setup

```
project/
├── backend/
│   ├── venv/                    # Virtual environment (local only)
│   ├── seem/                    # SEEM 2.0 package
│   │   ├── core/               # VSA kernel
│   │   ├── learning/           # BaNEL + Dream
│   │   ├── governance/         # SHACL + L0
│   │   ├── plugins/            # Executor
│   │   └── api/                # FastAPI server
│   ├── main.py                 # Backend entry point
│   └── requirements.txt
├── src/                        # React frontend
│   ├── App.tsx
│   ├── components/             # UI components
│   └── index.css              # Styling
├── dist/                       # Built frontend (after npm run build)
├── node_modules/              # Node dependencies (local only)
├── package.json
├── BLUEPRINT.md               # Full architecture
├── README.md                  # Quick start
└── INSTALLATION.md            # This file
```

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'numpy'"**
```bash
pip install -r requirements.txt
```

**"Address already in use" (port 8000)**
```bash
# Either use a different port:
BACKEND_PORT=8001 python main.py

# Or kill the existing process:
lsof -ti:8000 | xargs kill -9
```

**Slow startup**
First run may be slow due to import optimization. Subsequent runs are faster.

### Frontend Issues

**"npm ERR! ERESOLVE unable to resolve dependency tree"**
```bash
npm install --legacy-peer-deps
```

**"Port 5173 already in use"**
```bash
npm run dev -- --port 5174
```

**UI not connecting to API**
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS is enabled (it is, by default)
- Clear browser cache: F12 → Application → Storage → Clear All

## Development Workflow

### Making Changes to Backend

1. Edit files in `backend/seem/`
2. No restart needed (FastAPI auto-reloads)
3. Test via API: `curl http://localhost:8000/...`

### Making Changes to Frontend

1. Edit files in `src/`
2. Auto-reload on save
3. Changes appear instantly in browser

### Building for Production

**Frontend:**
```bash
npm run build
```
Creates optimized `dist/` folder for deployment.

**Backend:**
No build step required. Copy `backend/` directory to server.

## Next Steps

### 1. Explore the Dashboard
- Check system metrics
- View component status
- Monitor validation pass rates

### 2. Test VSA Operations
- Go to "Resonator VSA" tab
- Enter role and filler IDs
- Test binding and invertibility
- Observe cosine similarity values

### 3. Simulate Failures
- Use the API to record failures:
  ```bash
  curl -X POST "http://localhost:8000/banel/record-failure" \
    -H "Content-Type: application/json" \
    -d '{
      "route_id": "route_001",
      "failure_type": "unbind_failure",
      "cosine_similarity": 0.88,
      "error_message": "Below threshold"
    }'
  ```
- Watch BaNEL suppression increase in monitor

### 4. Run Dream Cycles
- Use API to create variants and run consolidation:
  ```bash
  curl -X POST "http://localhost:8000/dream/create-variant?original_id=route_001&skill_name=test_skill"
  ```

### 5. Query L0 Evidence
- View audit trail:
  ```bash
  curl http://localhost:8000/l0/stats
  ```

## Performance Tuning

### For Large-Scale Tests

Adjust in `backend/seem/core/vsa.py`:
```python
ResonatorVSA(
    dimension=16384,        # Larger = more capacity, slower computation
    max_iterations=7,       # Fewer = faster, less accurate
    sparsity_ratio=0.1      # Higher = noisier, faster
)
```

### For Dream Phase Scalability

Adjust in `backend/seem/learning/dream.py`:
```python
DreamPhaseEngine(
    population_size=50,     # Larger = more variants, slower evolution
    elite_size=5,          # Fewer = less diversity
    mutation_rate=0.15,    # Higher = more exploration
)
```

## Integration with Supabase (Future)

When ready, persistence to Supabase:

```python
from supabase import create_client

supabase = create_client(
    url=os.getenv("SUPABASE_URL"),
    key=os.getenv("SUPABASE_KEY")
)

# Store L0 evidence
supabase.table("evidence").insert({
    "id": evidence.id,
    "type": evidence.type,
    "content": json.dumps(evidence.content)
}).execute()
```

## Deployment

### Local Development
Current setup is ready for local development. All data stays on-device.

### Self-Hosted
Copy `backend/` and `dist/` to a server running Python 3.10+.

### Docker (Future)
A Dockerfile will be added for containerized deployment.

---

For detailed architecture, see **BLUEPRINT.md**
For quick overview, see **README.md**

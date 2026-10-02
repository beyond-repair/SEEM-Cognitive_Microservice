import { useState, useEffect } from 'react';
import { Zap, AlertTriangle, TrendingDown } from 'lucide-react';
import { api } from '../api';

interface RouteStats {
  route_id: string;
  success_count: number;
  failure_count: number;
  success_rate: number;
  avg_cosine_similarity: number;
  avg_iterations: number;
  negative_spike_count: number;
}

const FAILURE_TYPES = [
  'unbind_failure',
  'shacl_violation',
  'execution_error',
  'smt_unsat',
  'timeout',
  'unknown',
];

export default function BaNELMonitor() {
  const [stats, setStats] = useState<RouteStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [routeId, setRouteId] = useState('route_001');
  const [failureType, setFailureType] = useState('unbind_failure');
  const [cosine, setCosine] = useState('0.88');
  const [notice, setNotice] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch(api('/banel/routes'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setStats(Array.isArray(data.routes) ? data.routes : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backend unreachable');
      setStats([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const recordFailure = async () => {
    setNotice(null);
    const response = await fetch(api('/banel/record-failure'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        route_id: routeId,
        failure_type: failureType,
        cosine_similarity: Number(cosine),
        error_message: 'Recorded from the monitor',
      }),
    });
    const body = await response.json();
    if (!response.ok) {
      setNotice(body.detail ?? 'Record failed');
      return;
    }
    setNotice(
      `suppression ${Number(body.suppression_level).toFixed(3)}; micro-dream flag ${String(body.should_micro_dream)}`
    );
    await fetchStats();
  };

  const recordSuccess = async () => {
    setNotice(null);
    const response = await fetch(
      api(`/banel/record-success?route_id=${encodeURIComponent(routeId)}&cosine_similarity=1&iterations=1`),
      { method: 'POST' }
    );
    if (!response.ok) {
      setNotice('Success record failed');
      return;
    }
    setNotice('Success recorded; suppression cleared for this route.');
    await fetchStats();
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <div className="flex items-start gap-4 mb-6">
          <div className="bg-gradient-to-br from-yellow-500 to-orange-500 p-3 rounded-lg">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">BaNEL learning monitor</h2>
            <p className="text-slate-400 text-sm mt-1">
              Counts failures you record. It does not ship sample routes. One failure on an empty route
              crosses the 0.6 suppression flag because the failure rate is 1.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <input
            value={routeId}
            onChange={(e) => setRouteId(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            aria-label="Route id"
          />
          <select
            value={failureType}
            onChange={(e) => setFailureType(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            aria-label="Failure type"
          >
            {FAILURE_TYPES.map((kind) => (
              <option key={kind} value={kind}>{kind}</option>
            ))}
          </select>
          <input
            value={cosine}
            onChange={(e) => setCosine(e.target.value)}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            aria-label="Cosine similarity"
          />
          <div className="flex gap-2">
            <button onClick={recordFailure} className="flex-1 px-3 py-2 bg-orange-600 rounded-lg text-white text-sm">
              Record failure
            </button>
            <button onClick={recordSuccess} className="flex-1 px-3 py-2 bg-emerald-700 rounded-lg text-white text-sm">
              Record success
            </button>
          </div>
        </div>
        {notice && <p className="text-sm text-slate-300 mt-3">{notice}</p>}
      </div>

      {error && <p className="text-sm text-red-300">{error}</p>}

      {loading ? (
        <div className="text-slate-400">Loading route statistics...</div>
      ) : stats.length === 0 ? (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 text-slate-400 text-sm">
          No routes yet. Record a failure or success above, or POST /banel/record-failure.
        </div>
      ) : (
        <div className="space-y-4">
          {stats.map((route) => (
            <div
              key={route.route_id}
              onClick={() => setSelectedRoute(selectedRoute === route.route_id ? null : route.route_id)}
              className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm cursor-pointer"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">{route.route_id}</h3>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">{(route.success_rate * 100).toFixed(0)}%</div>
                  <div className="text-xs text-slate-400">success rate</div>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <Stat label="Successes" value={String(route.success_count)} tone="text-green-400" />
                <Stat label="Failures" value={String(route.failure_count)} tone="text-red-400" />
                <Stat label="Avg cosine" value={route.avg_cosine_similarity.toFixed(3)} tone="text-blue-400" />
                <Stat label="Avg iterations" value={route.avg_iterations.toFixed(1)} tone="text-cyan-400" />
              </div>
              <div className="flex items-center gap-2 text-sm text-orange-300">
                <AlertTriangle className="w-4 h-4" />
                <span>{route.negative_spike_count} negative spikes recorded</span>
              </div>
              {selectedRoute === route.route_id && (
                <p className="mt-4 text-xs text-slate-400">
                  Rejection threshold 0.6. Spike decay 0.95 is applied when suppression is read, so the
                  number on a later GET can be lower than the value returned at record time.
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
        <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
          <TrendingDown className="w-5 h-5 text-orange-400" />
          What BaNEL does here
        </h3>
        <p className="text-sm text-slate-400">
          A failure appends a spike and sets suppression from the failure rate plus a spike factor.
          Crossing 0.6 sets should_micro_dream. This process does not then mutate a route by itself.
        </p>
      </div>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div>
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${tone}`}>{value}</div>
    </div>
  );
}

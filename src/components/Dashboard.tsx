import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '../api';

interface DashboardMetrics {
  vsa_status: string;
  banel_routes: number;
  dream_cycles: number;
  validation_pass_rate: number;
  validation_count: number;
  l0_evidence: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const fetchMetrics = async () => {
      try {
        const responses = await Promise.all([
          fetch(api('/health')),
          fetch(api('/banel/routes')),
          fetch(api('/dream/stats')),
          fetch(api('/validator/stats')),
          fetch(api('/l0/stats')),
        ]);
        if (responses.some((response) => !response.ok)) {
          throw new Error('one or more stats endpoints failed');
        }
        const [health, routes, dream, validator, l0] = await Promise.all(
          responses.map((response) => response.json())
        );
        if (cancelled) return;
        setMetrics({
          vsa_status: String(health.status ?? 'unknown'),
          banel_routes: Number(routes.count ?? 0),
          dream_cycles: Number(dream.dream_cycles ?? 0),
          validation_pass_rate: Number(validator.pass_rate ?? 0),
          validation_count: Number(validator.total_validations ?? 0),
          l0_evidence: Number(l0.total_evidence ?? 0),
        });
        setError(null);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Backend unreachable');
          setMetrics(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const cards = [
    {
      label: 'VSA status',
      value: metrics?.vsa_status ?? '—',
      icon: CheckCircle,
      color: 'from-emerald-500 to-teal-600',
    },
    {
      label: 'Recorded routes',
      value: metrics ? String(metrics.banel_routes) : '—',
      icon: TrendingUp,
      color: 'from-blue-500 to-cyan-600',
    },
    {
      label: 'Dream cycles',
      value: metrics ? String(metrics.dream_cycles) : '—',
      icon: BarChart3,
      color: 'from-purple-500 to-pink-600',
    },
    {
      label: 'Validation pass rate',
      value: metrics
        ? metrics.validation_count === 0
          ? 'n/a'
          : `${(metrics.validation_pass_rate * 100).toFixed(0)}%`
        : '—',
      icon: CheckCircle,
      color: 'from-yellow-500 to-orange-600',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <h2 className="text-2xl font-bold text-white mb-2">System overview</h2>
        <p className="text-slate-400">
          Live counts from this process. Empty numbers stay empty — the dashboard does not invent routes
          or a pass rate. L0 evidence stored: {metrics ? metrics.l0_evidence : '—'}.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/40 text-red-200 rounded-lg p-4 text-sm">
          Backend not reachable ({error}). Start it with <span className="font-mono">python main.py</span> in{' '}
          <span className="font-mono">backend/</span>.
        </div>
      )}

      {loading && !metrics ? (
        <div className="flex items-center justify-center h-32">
          <div className="text-slate-400">Loading metrics...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.label}
                className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm hover:border-slate-600 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-sm font-medium text-slate-400">{card.label}</h3>
                  <div className={`bg-gradient-to-br ${card.color} p-2 rounded-lg`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-white">{card.value}</div>
              </div>
            );
          })}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">What is actually running</h3>
          <div className="space-y-3 text-sm text-slate-300">
            <div>FHRR phasor bind / unbind (measured cosine)</div>
            <div>BaNEL failure counters and a suppression score</div>
            <div>Dream-phase parameter GA (in memory)</div>
            <div>Numeric gates named SHACLValidator (not RDF)</div>
            <div>L0 evidence log with supersede, not delete</div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">What this is not</h3>
          <div className="space-y-3 text-sm text-slate-300">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-blue-400" />
              Not a mind, council, or agent
            </div>
            <div className="flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-blue-400" />
              Not persisted — restart clears state
            </div>
            <div className="flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-blue-400" />
              Claim 0 sketch; successor is sovereign-clean-room
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

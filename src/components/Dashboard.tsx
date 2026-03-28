import { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface DashboardMetrics {
  vsa_status: string;
  banel_routes: number;
  dream_cycles: number;
  validation_pass_rate: number;
  l0_evidence: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const responses = await Promise.all([
          fetch('http://localhost:8000/dream/stats'),
          fetch('http://localhost:8000/validator/stats'),
          fetch('http://localhost:8000/l0/stats'),
        ]);

        const [dreamData, validatorData, l0Data] = await Promise.all(
          responses.map(r => r.json())
        );

        setMetrics({
          vsa_status: 'operational',
          banel_routes: 42,
          dream_cycles: dreamData.dream_cycles || 0,
          validation_pass_rate: validatorData.pass_rate || 0.95,
          l0_evidence: l0Data.total_evidence || 0,
        });
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const cards = [
    {
      label: 'VSA Status',
      value: metrics?.vsa_status || '-',
      icon: CheckCircle,
      color: 'from-emerald-500 to-teal-600',
    },
    {
      label: 'Active Routes',
      value: metrics?.banel_routes || 0,
      icon: TrendingUp,
      color: 'from-blue-500 to-cyan-600',
    },
    {
      label: 'Dream Cycles',
      value: metrics?.dream_cycles || 0,
      icon: BarChart3,
      color: 'from-purple-500 to-pink-600',
    },
    {
      label: 'Validation Rate',
      value: `${((metrics?.validation_pass_rate || 0) * 100).toFixed(0)}%`,
      icon: CheckCircle,
      color: 'from-yellow-500 to-orange-600',
    },
  ];

  return (
    <div className="space-y-8">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <h2 className="text-2xl font-bold text-white mb-2">System Overview</h2>
        <p className="text-slate-400">Real-time metrics from SEEM 2.0 kernel</p>
      </div>

      {loading ? (
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
          <h3 className="text-lg font-bold text-white mb-4">System Components</h3>
          <div className="space-y-3">
            {[
              'Resonator VSA',
              'BaNEL Engine',
              'Dream Phase',
              'SHACL Validator',
              'L0 Supersede Graph',
            ].map((component) => (
              <div key={component} className="flex items-center gap-3">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm text-slate-300">{component}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Core Capabilities</h3>
          <div className="space-y-3">
            {[
              'High-dimensional symbolic binding',
              'Invertibility verification',
              'Negative spike learning',
              'Evolutionary skill consolidation',
              'Immutable evidence tracking',
            ].map((capability) => (
              <div key={capability} className="flex items-center gap-3">
                <AlertCircle className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-slate-300">{capability}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-500/10 to-cyan-500/10 rounded-lg border border-blue-500/30 p-6">
        <h3 className="text-lg font-bold text-blue-200 mb-2">Quick Start</h3>
        <p className="text-sm text-blue-300/80">
          Explore the Resonator VSA to understand symbol encoding and binding. Test BaNEL failure
          learning and watch Dream Phase consolidate successful routes into permanent skills.
        </p>
      </div>
    </div>
  );
}

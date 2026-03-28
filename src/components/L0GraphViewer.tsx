import { useState, useEffect } from 'react';
import { Shield, Database, History } from 'lucide-react';

interface L0Stats {
  total_evidence: number;
  active_evidence: number;
  archived_evidence: number;
  supersedence_records: number;
  evidence_types: string[];
}

export default function L0GraphViewer() {
  const [stats, setStats] = useState<L0Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/l0/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <div className="flex items-start gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-3 rounded-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">L0 Supersede Graph</h2>
            <p className="text-slate-400 text-sm mt-1">
              Immutable evidence base - nothing is ever deleted, only superseded
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="text-slate-400">Loading L0 graph statistics...</div>
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'Total Evidence', value: stats.total_evidence, icon: Database, color: 'from-green-500 to-emerald-600' },
            { label: 'Active Evidence', value: stats.active_evidence, icon: Shield, color: 'from-blue-500 to-cyan-600' },
            { label: 'Supersedence Records', value: stats.supersedence_records, icon: History, color: 'from-purple-500 to-pink-600' },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs text-slate-400">{item.label}</div>
                  <div className={`bg-gradient-to-br ${item.color} p-2 rounded-lg`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-white">{item.value}</div>
              </div>
            );
          })}
        </div>
      ) : null}

      {stats && stats.evidence_types.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Evidence Types</h3>
          <div className="flex flex-wrap gap-2">
            {stats.evidence_types.map((type) => (
              <span
                key={type}
                className="px-3 py-1 bg-green-500/20 border border-green-500/50 text-green-300 rounded-full text-sm"
              >
                {type}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Core Principles</h3>
          <div className="space-y-3 text-sm text-slate-400">
            <div className="flex gap-3">
              <div className="text-green-400 font-bold min-w-fit">✓</div>
              <div>
                <div className="font-medium text-slate-300">Immutability</div>
                <div>No destructive DELETE operations</div>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="text-green-400 font-bold min-w-fit">✓</div>
              <div>
                <div className="font-medium text-slate-300">Auditability</div>
                <div>Full chain of evidence supersedences</div>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="text-green-400 font-bold min-w-fit">✓</div>
              <div>
                <div className="font-medium text-slate-300">Sovereignty</div>
                <div>Complete local control and ownership</div>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="text-green-400 font-bold min-w-fit">✓</div>
              <div>
                <div className="font-medium text-slate-300">Accountability</div>
                <div>Track why evidence was superseded</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Supersedence Reasons</h3>
          <div className="space-y-2 text-sm text-slate-400">
            <div className="flex justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Route Mutation</span>
              <span className="text-slate-400">Variant improvement</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Skill Consolidation</span>
              <span className="text-slate-400">L3 promotion</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Performance Improvement</span>
              <span className="text-slate-400">Better fitness score</span>
            </div>
            <div className="flex justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Manual Override</span>
              <span className="text-slate-400">User-initiated change</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg border border-green-500/30 p-6">
        <h3 className="text-lg font-bold text-green-200 mb-2">Audit Trail</h3>
        <p className="text-sm text-green-300/80">
          Every piece of evidence carries a complete history of supersedences. This ensures the system
          never loses institutional knowledge and can answer "why was this route superseded?" at any
          point in time. The L0 Graph is the ground truth of the system's evolution.
        </p>
      </div>
    </div>
  );
}

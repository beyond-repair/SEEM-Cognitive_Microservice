import { useState, useEffect } from 'react';
import { Shield, Database, History } from 'lucide-react';
import { api } from '../api';

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
  const [error, setError] = useState<string | null>(null);
  const [evidenceId, setEvidenceId] = useState('ev1');
  const [evidenceType, setEvidenceType] = useState('note');
  const [text, setText] = useState('hello');
  const [oldId, setOldId] = useState('ev1');
  const [newId, setNewId] = useState('ev2');
  const [notice, setNotice] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch(api('/l0/stats'));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setStats(await response.json());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Backend unreachable');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 5000);
    return () => clearInterval(interval);
  }, []);

  const store = async () => {
    const response = await fetch(api('/l0/store-evidence'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        evidence_id: evidenceId,
        evidence_type: evidenceType,
        content: { text },
      }),
    });
    setNotice(response.ok ? `stored ${evidenceId}` : 'store failed');
    await fetchStats();
  };

  const supersede = async () => {
    const response = await fetch(api('/l0/supersede'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        old_evidence_id: oldId,
        new_evidence_id: newId,
        reason: 'performance_improvement',
      }),
    });
    const body = await response.json();
    setNotice(response.ok ? `record ${body.record_id}` : (body.detail ?? 'supersede failed'));
    await fetchStats();
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <div className="flex items-start gap-4 mb-6">
          <div className="bg-gradient-to-br from-green-500 to-emerald-500 p-3 rounded-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">L0 supersede graph</h2>
            <p className="text-slate-400 text-sm mt-1">
              In-memory evidence. Supersede removes the old id from the active set and keeps the record.
              Restarting the API drops the log.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
          <input value={evidenceId} onChange={(e) => setEvidenceId(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Evidence id" />
          <input value={evidenceType} onChange={(e) => setEvidenceType(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Evidence type" />
          <input value={text} onChange={(e) => setText(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Evidence text" />
          <button onClick={store} className="px-3 py-2 bg-emerald-700 rounded-lg text-white text-sm">Store evidence</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input value={oldId} onChange={(e) => setOldId(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Old evidence id" />
          <input value={newId} onChange={(e) => setNewId(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="New evidence id" />
          <button onClick={supersede} className="px-3 py-2 bg-slate-600 rounded-lg text-white text-sm">Supersede old with new</button>
        </div>
        {notice && <p className="text-sm text-slate-300 mt-3">{notice}</p>}
      </div>

      {error && <p className="text-sm text-red-300">{error}</p>}
      {loading && !stats ? (
        <div className="text-slate-400">Loading L0 graph statistics...</div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: 'Total evidence', value: stats.total_evidence, icon: Database },
            { label: 'Active evidence', value: stats.active_evidence, icon: Shield },
            { label: 'Supersedence records', value: stats.supersedence_records, icon: History },
          ].map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-xs text-slate-400">{item.label}</div>
                  <Icon className="w-4 h-4 text-emerald-300" />
                </div>
                <div className="text-3xl font-bold text-white">{item.value}</div>
              </div>
            );
          })}
        </div>
      ) : null}

      {stats && stats.evidence_types.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h3 className="text-lg font-bold text-white mb-4">Evidence types</h3>
          <div className="flex flex-wrap gap-2">
            {stats.evidence_types.map((type) => (
              <span key={type} className="px-3 py-1 bg-green-500/20 border border-green-500/50 text-green-300 rounded-full text-sm">
                {type}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

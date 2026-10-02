import { useState, useEffect } from 'react';
import { Activity, Zap, Target } from 'lucide-react';
import { api } from '../api';

interface DreamStats {
  dream_cycles: number;
  total_variants: number;
  total_consolidated_skills: number;
  average_variant_fitness: number;
  population_size: number;
}

export default function DreamPhaseViewer() {
  const [stats, setStats] = useState<DreamStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [originalId, setOriginalId] = useState('route_001');
  const [skillName, setSkillName] = useState('test_skill');
  const [notice, setNotice] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      const response = await fetch(api('/dream/stats'));
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

  const createVariant = async () => {
    const response = await fetch(
      api(`/dream/create-variant?original_id=${encodeURIComponent(originalId)}&skill_name=${encodeURIComponent(skillName)}`),
      { method: 'POST' }
    );
    const body = await response.json();
    setNotice(response.ok ? `created ${body.variant_id}` : 'create failed');
    await fetchStats();
  };

  const runCycle = async () => {
    const response = await fetch(
      api(`/dream/run-cycle?original_id=${encodeURIComponent(originalId)}`),
      { method: 'POST' }
    );
    const body = await response.json();
    setNotice(
      response.ok
        ? `generation ${body.new_generation_size}, cycles ${body.cycle_count}, best ${body.best_variant_id ?? 'none'}`
        : 'cycle failed'
    );
    await fetchStats();
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <div className="flex items-start gap-4 mb-6">
          <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Dream phase engine</h2>
            <p className="text-slate-400 text-sm mt-1">
              Parameter variants in memory. A cycle does nothing until you create a variant. Consolidation
              stays false until fitness, an exponential moving average, reaches 0.75.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <input value={originalId} onChange={(e) => setOriginalId(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Original id" />
          <input value={skillName} onChange={(e) => setSkillName(e.target.value)} className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white" aria-label="Skill name" />
          <button onClick={createVariant} className="px-4 py-2 bg-purple-600 rounded-lg text-white text-sm">Create variant</button>
          <button onClick={runCycle} className="px-4 py-2 bg-pink-700 rounded-lg text-white text-sm">Run cycle</button>
        </div>
        {notice && <p className="text-sm text-slate-300 mt-3">{notice}</p>}
      </div>

      {error && <p className="text-sm text-red-300">{error}</p>}
      {loading && !stats ? (
        <div className="text-slate-400">Loading dream statistics...</div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            { label: 'Dream cycles', value: stats.dream_cycles },
            { label: 'Total variants', value: stats.total_variants },
            { label: 'Consolidated skills', value: stats.total_consolidated_skills },
            { label: 'Population size', value: stats.population_size },
            { label: 'Avg fitness', value: stats.average_variant_fitness.toFixed(2) },
          ].map((item) => (
            <div key={item.label} className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
              <div className="text-xs text-slate-400 mb-2">{item.label}</div>
              <div className="text-3xl font-bold text-white">{item.value}</div>
            </div>
          ))}
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-purple-400" />
            Cycle steps that actually run
          </h3>
          <div className="space-y-2 text-sm text-slate-400">
            <div>1. Keep the current elite (success rate, then fitness).</div>
            <div>2. Fill the population with crossover or mutation of those elites.</div>
            <div>3. There is no held-out task. Fitness only changes when you POST /dream/record-execution.</div>
          </div>
        </div>
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-pink-400" />
            Defaults
          </h3>
          <div className="space-y-2 text-sm text-slate-300">
            <div>Fitness threshold 0.75 (consolidation refuses below it)</div>
            <div>Elite size 5, population 50, crossover 0.7, mutation 0.15</div>
          </div>
        </div>
      </div>
    </div>
  );
}

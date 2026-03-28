import { useState, useEffect } from 'react';
import { Activity, Zap, Target } from 'lucide-react';

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

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/dream/stats');
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
          <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-lg">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Dream Phase Engine</h2>
            <p className="text-slate-400 text-sm mt-1">
              Background consolidation of successful routes into permanent L3 MemSkills
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="text-slate-400">Loading dream statistics...</div>
        </div>
      ) : stats ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[
            { label: 'Dream Cycles', value: stats.dream_cycles, color: 'from-purple-500 to-pink-600' },
            { label: 'Total Variants', value: stats.total_variants, color: 'from-blue-500 to-cyan-600' },
            { label: 'Consolidated Skills', value: stats.total_consolidated_skills, color: 'from-green-500 to-emerald-600' },
            { label: 'Population Size', value: stats.population_size, color: 'from-yellow-500 to-orange-600' },
            { label: 'Avg Fitness', value: stats.average_variant_fitness.toFixed(2), color: 'from-red-500 to-pink-600' },
          ].map((item) => (
            <div
              key={item.label}
              className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm"
            >
              <div className="text-xs text-slate-400 mb-2">{item.label}</div>
              <div className="text-3xl font-bold text-white">{item.value}</div>
            </div>
          ))}
        </div>
      ) : null}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-purple-400" />
            Dream Cycle Process
          </h3>
          <div className="space-y-3 text-sm text-slate-400">
            <div className="flex gap-3">
              <div className="font-bold text-purple-400 min-w-fit">1. Selection</div>
              <div>Elite routes selected by success rate and fitness</div>
            </div>
            <div className="flex gap-3">
              <div className="font-bold text-purple-400 min-w-fit">2. Crossover</div>
              <div>Recombine elite parameters for new variants</div>
            </div>
            <div className="flex gap-3">
              <div className="font-bold text-purple-400 min-w-fit">3. Mutation</div>
              <div>Perturb k_lambda and max_iterations for exploration</div>
            </div>
            <div className="flex gap-3">
              <div className="font-bold text-purple-400 min-w-fit">4. Evaluation</div>
              <div>Test variants on held-out evidence</div>
            </div>
            <div className="flex gap-3">
              <div className="font-bold text-purple-400 min-w-fit">5. Consolidation</div>
              <div>High-fitness routes promoted to L3 MemSkills</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Target className="w-5 h-5 text-pink-400" />
            Consolidation Criteria
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Fitness Threshold</span>
              <span className="font-mono text-slate-200">≥ 0.75</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Elite Size</span>
              <span className="font-mono text-slate-200">5</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Crossover Rate</span>
              <span className="font-mono text-slate-200">0.7</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300">Mutation Rate</span>
              <span className="font-mono text-slate-200">0.15</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-purple-500/30 p-6">
        <h3 className="text-lg font-bold text-purple-200 mb-2">L3 MemSkills</h3>
        <p className="text-sm text-purple-300/80">
          Routes consolidated through Dream Phase become immutable L3 MemSkills stored in the L0
          Supersede Graph. These represent the system's learned, executable knowledge - strategies that
          proved successful across multiple contexts and are ready for reliable deployment.
        </p>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Zap, AlertTriangle, TrendingDown } from 'lucide-react';

interface RouteStats {
  route_id: string;
  success_count: number;
  failure_count: number;
  success_rate: number;
  avg_cosine_similarity: number;
  avg_iterations: number;
  negative_spike_count: number;
}

export default function BaNELMonitor() {
  const [stats, setStats] = useState<RouteStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/banel/stats/sample_route');
        if (response.ok) {
          const data = await response.json();
          setStats([data]);
        } else {
          setStats([
            {
              route_id: 'route_001',
              success_count: 45,
              failure_count: 8,
              success_rate: 0.849,
              avg_cosine_similarity: 0.94,
              avg_iterations: 4.2,
              negative_spike_count: 8,
            },
            {
              route_id: 'route_002',
              success_count: 32,
              failure_count: 12,
              success_rate: 0.727,
              avg_cosine_similarity: 0.91,
              avg_iterations: 5.1,
              negative_spike_count: 12,
            },
          ]);
        }
      } catch {
        setStats([]);
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
          <div className="bg-gradient-to-br from-yellow-500 to-orange-500 p-3 rounded-lg">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">BaNEL Learning Monitor</h2>
            <p className="text-slate-400 text-sm mt-1">
              Bayesian Negative Evidence Learning - Track failure patterns and suppression levels
            </p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <div className="text-slate-400">Loading route statistics...</div>
        </div>
      ) : (
        <div className="space-y-4">
          {stats.map((route) => (
            <div
              key={route.route_id}
              onClick={() => setSelectedRoute(selectedRoute === route.route_id ? null : route.route_id)}
              className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm cursor-pointer hover:border-slate-600 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">{route.route_id}</h3>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">
                      {(route.success_rate * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-slate-400">success rate</div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <div className="text-xs text-slate-400 mb-1">Successes</div>
                  <div className="text-2xl font-bold text-green-400">{route.success_count}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-400 mb-1">Failures</div>
                  <div className="text-2xl font-bold text-red-400">{route.failure_count}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-400 mb-1">Avg Cosine</div>
                  <div className="text-2xl font-bold text-blue-400">
                    {route.avg_cosine_similarity.toFixed(3)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-400 mb-1">Avg Iterations</div>
                  <div className="text-2xl font-bold text-cyan-400">
                    {route.avg_iterations.toFixed(1)}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 text-sm text-orange-300">
                <AlertTriangle className="w-4 h-4" />
                <span>{route.negative_spike_count} negative spikes recorded</span>
              </div>

              {selectedRoute === route.route_id && (
                <div className="mt-4 pt-4 border-t border-slate-700">
                  <div className="text-xs text-slate-400 mb-3">Learning Metrics</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Rejection Threshold:</span>
                      <span className="text-slate-200">0.6</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Spike Decay Rate:</span>
                      <span className="text-slate-200">0.95</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Micro-Dream Timeout:</span>
                      <span className="text-slate-200">50ms</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <TrendingDown className="w-5 h-5 text-orange-400" />
            How BaNEL Works
          </h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            BaNEL treats failures as strong negative evidence. When a route fails (low unbind
            cosine, SHACL violation, or execution error), a negative spike is recorded. Exceeding
            the rejection threshold triggers a Micro-Dream that mutates parameters and tests improvements.
          </p>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Failure Types</h3>
          <div className="space-y-2 text-sm text-slate-400">
            <div>• Unbind Failure: Cosine similarity {'<'} 0.92</div>
            <div>• SHACL Violation: Structure check failed</div>
            <div>• Execution Error: Plugin threw exception</div>
            <div>• SMT Unsat: Logical constraint unsatisfiable</div>
            <div>• Timeout: Operation exceeded deadline</div>
          </div>
        </div>
      </div>
    </div>
  );
}

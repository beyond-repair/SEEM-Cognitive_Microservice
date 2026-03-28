import { useState } from 'react';
import { Brain, Zap, BarChart2 } from 'lucide-react';

export default function VSAExplorer() {
  const [roleId, setRoleId] = useState('');
  const [fillerId, setFillerId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleBind = async () => {
    if (!roleId || !fillerId) {
      alert('Please enter both role and filler IDs');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/vsa/bind?role_id=${roleId}&filler_id=${fillerId}`,
        { method: 'POST' }
      );
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Failed to bind symbols' });
    } finally {
      setLoading(false);
    }
  };

  const handleTestInvertibility = async () => {
    if (!roleId || !fillerId) {
      alert('Please enter both role and filler IDs');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/vsa/invertibility?role_id=${roleId}&filler_id=${fillerId}`,
        { method: 'POST' }
      );
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Failed to test invertibility' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm">
        <div className="flex items-start gap-4 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-3 rounded-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Resonator VSA Explorer</h2>
            <p className="text-slate-400 text-sm mt-1">
              Test high-dimensional symbolic binding and invertibility verification
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Role ID</label>
            <input
              type="text"
              value={roleId}
              onChange={(e) => setRoleId(e.target.value)}
              placeholder="e.g., action_execute"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Filler ID</label>
            <input
              type="text"
              value={fillerId}
              onChange={(e) => setFillerId(e.target.value)}
              placeholder="e.g., task_process"
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleBind}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg font-medium hover:from-blue-700 hover:to-blue-600 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <Zap className="w-4 h-4" />
              {loading ? 'Binding...' : 'Bind Symbols'}
            </button>
            <button
              onClick={handleTestInvertibility}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-gradient-to-r from-cyan-600 to-cyan-500 text-white rounded-lg font-medium hover:from-cyan-700 hover:to-cyan-600 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <BarChart2 className="w-4 h-4" />
              {loading ? 'Testing...' : 'Test Invertibility'}
            </button>
          </div>
        </div>
      </div>

      {result && (
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">Result</h3>
          <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-slate-300 overflow-auto max-h-64">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">VSA Specifications</h3>
          <div className="space-y-2 text-sm text-slate-400">
            <div className="flex justify-between">
              <span>Dimension:</span>
              <span className="text-slate-200">16,384</span>
            </div>
            <div className="flex justify-between">
              <span>Invertibility Threshold:</span>
              <span className="text-slate-200">≥ 0.92</span>
            </div>
            <div className="flex justify-between">
              <span>Max Iterations:</span>
              <span className="text-slate-200">7</span>
            </div>
            <div className="flex justify-between">
              <span>Sparsity Ratio:</span>
              <span className="text-slate-200">0.1</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6 backdrop-blur-sm">
          <h3 className="text-lg font-bold text-white mb-4">How It Works</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            The Resonator VSA encodes symbols as complex hypervectors and uses element-wise binding
            (⊙) with conjugate multiplication. Unbinding uses iterative resonance loops with sparsity
            projection for invertibility verification.
          </p>
        </div>
      </div>
    </div>
  );
}

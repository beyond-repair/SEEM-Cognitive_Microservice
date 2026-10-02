import { useEffect, useState } from 'react';
import { api, API_BASE } from '../api';

export default function SettingsPanel() {
  const [config, setConfig] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const response = await fetch(api('/config'));
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        const body = (await response.json()) as Record<string, unknown>;
        if (!cancelled) {
          setConfig(body);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Backend unreachable');
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-8 backdrop-blur-sm space-y-4">
      <h2 className="text-xl font-bold text-white">Runtime configuration</h2>
      <p className="text-sm text-slate-400">
        API base <span className="font-mono text-slate-200">{API_BASE}</span>. Override with{' '}
        <span className="font-mono">VITE_API_BASE</span>. Nothing here is a secret, and nothing is stored
        on disk by the backend.
      </p>
      {error && <p className="text-sm text-red-300">Could not read /config: {error}</p>}
      {config && (
        <pre className="bg-slate-900 rounded-lg p-4 text-xs text-slate-300 overflow-auto">
          {JSON.stringify(config, null, 2)}
        </pre>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Activity, Brain, Zap, Shield, BarChart3, Settings } from 'lucide-react';
import Dashboard from './components/Dashboard';
import VSAExplorer from './components/VSAExplorer';
import BaNELMonitor from './components/BaNELMonitor';
import DreamPhaseViewer from './components/DreamPhaseViewer';
import L0GraphViewer from './components/L0GraphViewer';

export type TabType = 'dashboard' | 'vsa' | 'banel' | 'dream' | 'l0' | 'settings';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [apiHealth, setApiHealth] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        setApiHealth(response.ok);
      } catch {
        setApiHealth(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: BarChart3 },
    { id: 'vsa' as TabType, label: 'Resonator VSA', icon: Brain },
    { id: 'banel' as TabType, label: 'BaNEL Monitor', icon: Zap },
    { id: 'dream' as TabType, label: 'Dream Phase', icon: Activity },
    { id: 'l0' as TabType, label: 'L0 Graph', icon: Shield },
    { id: 'settings' as TabType, label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">SEEM 2.0</h1>
                <p className="text-xs text-slate-400">Sovereign Episodic Experience Microservice</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${apiHealth ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-xs text-slate-400">
                {apiHealth ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <nav className="border-b border-slate-700 bg-slate-900/30 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-all flex items-center gap-2 ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'vsa' && <VSAExplorer />}
        {activeTab === 'banel' && <BaNELMonitor />}
        {activeTab === 'dream' && <DreamPhaseViewer />}
        {activeTab === 'l0' && <L0GraphViewer />}
        {activeTab === 'settings' && (
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-8">
            <h2 className="text-xl font-bold text-white mb-4">Settings</h2>
            <p className="text-slate-400">Configuration options coming soon...</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

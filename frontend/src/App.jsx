import React, { useState } from 'react';
import UploadPage from './pages/Upload';
import DashboardPage from './pages/Dashboard';
import ReportPage from './pages/Report';
import HistoryModal from './components/HistoryModal';
import { Activity, History } from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState('upload'); // 'upload' | 'dashboard' | 'report'
  const [reportId, setReportId] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const handleAnalysisComplete = (id, data) => {
    setReportId(id);
    setReportData(data);
    setCurrentView('dashboard');
  };

  const handleSelectIncident = (incident) => {
    setSelectedIncident(incident);
    setCurrentView('report');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
  };

  const handleSelectFromHistory = (id, data) => {
    setReportId(id);
    setReportData(data);
    setCurrentView('dashboard');
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col">
      {/* Global Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-950/40 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div
            onClick={() => setCurrentView('upload')}
            className="flex items-center gap-2.5 cursor-pointer"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-white text-base tracking-tight">Atlas</span>
              <span className="text-xs text-blue-400 font-semibold ml-1.5 px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20">
                LogAI
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsHistoryOpen(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-medium text-slate-300 hover:text-white bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 transition"
            >
              <History className="w-3.5 h-3.5 text-blue-400" />
              <span>Past Runs</span>
            </button>
            <span className="hidden sm:inline text-xs text-slate-500">|</span>
            <span className="hidden sm:inline text-xs text-slate-400">Minor Project: Server Anomaly Detection</span>
          </div>
        </div>
      </header>

      {/* Main View Router */}
      <main className="flex-1">
        {currentView === 'upload' && (
          <UploadPage onAnalysisComplete={handleAnalysisComplete} />
        )}

        {currentView === 'dashboard' && (
          <DashboardPage
            reportId={reportId}
            reportData={reportData}
            onSelectIncident={handleSelectIncident}
            onNewAnalysis={() => setCurrentView('upload')}
          />
        )}

        {currentView === 'report' && (
          <ReportPage
            incident={selectedIncident}
            reportId={reportId}
            onBack={handleBackToDashboard}
          />
        )}
      </main>

      {/* History Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectReport={handleSelectFromHistory}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500">
        Anomaly Detection in Servers Using Large Language Models (LLMs) • Minor Project V1
      </footer>
    </div>
  );
}

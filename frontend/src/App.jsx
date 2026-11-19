import React, { useState } from 'react';
import UploadPage from './pages/Upload';
import DashboardPage from './pages/Dashboard';
import ReportPage from './pages/Report';
import HistoryModal from './components/HistoryModal';
import { History, Activity, Radio } from 'lucide-react';

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
    <div className="min-h-screen bg-white text-black flex flex-col font-sans">
      {/* Top Network Utility Strip */}
      <div className="bg-[#100e2f] text-white text-xs px-4 py-1.5 flex items-center justify-between border-b border-[#272967]">
        <div className="max-w-6xl w-full mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-bold tracking-wider uppercase text-[10px] text-[#ffa000]">
              ATLAS DISPATCH NETWORK
            </span>
            <span className="text-[#bebebe] hidden sm:inline">•</span>
            <span className="text-[#bebebe] hidden sm:inline text-[11px]">
              Automated SRE Diagnostic Wire & Machine Learning Anomaly Detection
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px] text-[#bebebe]">
            <span>ENGINE: DRAIN3 + ISOLATION FOREST + LLM</span>
            <span>EDITION: ACADEMIC MINOR V1</span>
          </div>
        </div>
      </div>

      {/* Main Masthead Navigation Bar */}
      <header className="border-b border-[#d8d8d8] bg-white sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div
            onClick={() => setCurrentView('upload')}
            className="flex items-center gap-3 cursor-pointer"
          >
            {/* The Signature Logo Block (Saturated Orange with White Calligraphy Mark) */}
            <div className="w-10 h-10 bg-[#fa9000] flex items-center justify-center text-white font-black text-xl tracking-tighter">
              A
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-2xl font-bold tracking-tighter text-black uppercase">
                  ATLAS
                </span>
                <span className="text-xs font-black uppercase text-[#595959] tracking-widest">
                  MONITOR
                </span>
              </div>
            </div>
          </div>

          {/* Controls: LIVE badge, Past Runs button, Action Pills */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-[2px] bg-[#c31833] text-white text-[11px] font-black uppercase tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-white breaking-pulse mr-0.5" />
              <span>LIVE SYSTEM</span>
            </div>

            <button
              onClick={() => setIsHistoryOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-normal text-white bg-black hover:bg-[#333333] rounded-[18px] transition"
            >
              <History className="w-3.5 h-3.5 text-[#fa9000]" />
              <span>Archived Runs</span>
            </button>
          </div>
        </div>

        {/* Breaking / Trending Topics Rail */}
        <div className="bg-[#f0f0f0] border-t border-[#d8d8d8] px-4 py-1 text-xs">
          <div className="max-w-6xl mx-auto flex items-center gap-3 overflow-x-auto text-[11px]">
            <span className="font-black text-black uppercase tracking-wider whitespace-nowrap">
              SYSTEM SECTORS:
            </span>
            <span className="text-[#333333] whitespace-nowrap">Database Pools</span>
            <span className="text-[#bebebe]">•</span>
            <span className="text-[#333333] whitespace-nowrap">Worker Threads</span>
            <span className="text-[#bebebe]">•</span>
            <span className="text-[#333333] whitespace-nowrap">Auth Brute-Force</span>
            <span className="text-[#bebebe]">•</span>
            <span className="text-[#333333] whitespace-nowrap">Memory Pressure</span>
            <span className="text-[#bebebe]">•</span>
            <span className="text-[#333333] whitespace-nowrap">HTTP Gateway 5xx</span>
          </div>
        </div>
      </header>

      {/* Main Content View */}
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

      {/* Archived Runs Modal */}
      <HistoryModal
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectReport={handleSelectFromHistory}
      />

      {/* Editorial News Footer */}
      <footer className="border-t border-[#d8d8d8] bg-white mt-16 py-8 text-xs text-[#595959]">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 bg-[#fa9000] inline-block" />
            <span className="font-bold text-black uppercase">
              Atlas Anomaly Detection Wire Desk
            </span>
            <span>• Minor Project Submission</span>
          </div>

          <div>
            Pankaj Kumar Goyal (24UCSE40W2) • Department of Computer Science & Engineering
          </div>
        </div>
      </footer>
    </div>
  );
}

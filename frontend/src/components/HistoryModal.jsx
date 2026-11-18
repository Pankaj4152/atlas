import React, { useState, useEffect } from 'react';
import { History, X, Clock, FileText, ChevronRight, Loader2 } from 'lucide-react';

export default function HistoryModal({ isOpen, onClose, onSelectReport }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchReports();
    }
  }, [isOpen]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/reports');
      if (res.ok) {
        const data = await res.json();
        setReports(data.reports || []);
      }
    } catch (err) {
      console.error('Failed to load past reports', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (reportId) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/reports/${reportId}`);
      if (res.ok) {
        const data = await res.json();
        onSelectReport(data.id, data.report_data);
        onClose();
      }
    } catch (err) {
      console.error('Failed to fetch full report', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 text-slate-100">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-bold text-white">Past Analysis Runs</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center text-slate-400 text-sm gap-2">
            <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
            <span>Loading past reports...</span>
          </div>
        ) : reports.length === 0 ? (
          <div className="py-10 text-center text-slate-500 text-sm">
            No previous reports found. Upload and analyze a file first.
          </div>
        ) : (
          <div className="space-y-2.5 max-h-96 overflow-y-auto pr-1">
            {reports.map((r) => (
              <div
                key={r.id}
                onClick={() => handleSelect(r.id)}
                className="p-3.5 rounded-xl bg-slate-800/40 hover:bg-slate-800 border border-slate-800/80 hover:border-slate-700 transition cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 mt-0.5">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white flex items-center gap-2">
                      <span>{r.filename}</span>
                      {r.critical_incidents > 0 && (
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">
                          {r.critical_incidents} CRIT
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : ''}
                      </span>
                      <span>•</span>
                      <span>{r.total_logs} logs</span>
                      <span>•</span>
                      <span>{r.total_incidents} incidents</span>
                    </div>
                  </div>
                </div>

                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

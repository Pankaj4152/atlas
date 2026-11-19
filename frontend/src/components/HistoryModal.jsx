import React, { useState, useEffect } from 'react';
import SectionEyebrow from './SectionEyebrow';
import { X, Clock, FileText, ChevronRight, Loader2 } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-none">
      <div className="w-full max-w-2xl bg-white border border-black p-6 shadow-none">
        <div className="flex items-center justify-between pb-3 border-b border-[#000000] mb-4">
          <div className="flex items-center">
            <span className="w-2 h-5 bg-[#fa9000] mr-2.5 inline-block" />
            <h3 className="text-xl font-bold uppercase tracking-wider text-black">
              ARCHIVED DISPATCH RUNS
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-[#595959] hover:text-black transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center text-[#595959] text-sm gap-2">
            <Loader2 className="w-6 h-6 animate-spin text-[#fa9000]" />
            <span>Retrieving incident records from database...</span>
          </div>
        ) : reports.length === 0 ? (
          <div className="py-10 text-center text-[#595959] text-sm">
            No archived logs found. Ingest and analyze a log stream first.
          </div>
        ) : (
          <div className="space-y-0 divide-y divide-[#d8d8d8] max-h-96 overflow-y-auto pr-1 border border-[#d8d8d8]">
            {reports.map((r) => (
              <div
                key={r.id}
                onClick={() => handleSelect(r.id)}
                className="p-3.5 hover:bg-[#f0f0f0] transition cursor-pointer flex items-center justify-between group"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-[#f0f0f0] text-black border border-[#d8d8d8] mt-0.5">
                    <FileText className="w-4 h-4 text-[#fa9000]" />
                  </div>
                  <div>
                    <div className="text-sm font-bold text-black flex items-center gap-2">
                      <span className="group-hover:text-[#fa9000] transition-colors">{r.filename}</span>
                      {r.critical_incidents > 0 && (
                        <span className="bg-[#c31833] text-white text-[10px] font-black px-1.5 py-0.2 rounded-[2px] uppercase">
                          {r.critical_incidents} CRITICAL
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-[#595959] mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-[#595959]" />
                        {r.created_at ? r.created_at.slice(0, 16).replace('T', ' ') : ''}
                      </span>
                      <span>•</span>
                      <span>{r.total_logs} logs</span>
                      <span>•</span>
                      <span>{r.total_incidents} incidents</span>
                    </div>
                  </div>
                </div>

                <ChevronRight className="w-4 h-4 text-[#595959] group-hover:translate-x-1 transition-transform" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

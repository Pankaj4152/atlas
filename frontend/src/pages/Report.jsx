import React from 'react';
import {
  ArrowLeft,
  AlertOctagon,
  CheckCircle,
  Clock,
  Sparkles,
  Terminal,
  ShieldAlert,
  FileCheck,
} from 'lucide-react';

export default function ReportPage({ incident, reportId, onBack }) {
  if (!incident) return null;

  const isCrit = incident.severity === 'critical';
  const isHigh = incident.severity === 'high';
  const badgeClass = isCrit
    ? 'bg-red-500/10 text-red-400 border-red-500/20'
    : isHigh
    ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
    : 'bg-amber-500/10 text-amber-400 border-amber-500/20';

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Navigation */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </button>

      {/* Incident Header Banner */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${badgeClass}`}>
                {incident.severity}
              </span>
              <span className="text-xs text-slate-500">Incident {incident.incident_id}</span>
              <span className="text-xs text-slate-500">• Confidence: {incident.confidence}</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">{incident.title}</h1>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <Clock className="w-3.5 h-3.5 text-blue-400" />
              <span>Time Window: {incident.time_window}</span>
            </div>
          </div>

          {reportId && (
            <a
              href={`/api/reports/${reportId}/pdf`}
              download
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition shadow-sm whitespace-nowrap self-start md:self-center"
            >
              <FileCheck className="w-4 h-4" />
              Export PDF
            </a>
          )}
        </div>
      </div>

      {/* Anomaly Metrics Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
          <div className="text-xs text-slate-500 uppercase font-medium">Window Logs</div>
          <div className="text-2xl font-bold text-white mt-1">{incident.metrics?.total_logs || 0}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
          <div className="text-xs text-slate-500 uppercase font-medium">Errors Observed</div>
          <div className="text-2xl font-bold text-red-400 mt-1">{incident.metrics?.error_count || 0}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
          <div className="text-xs text-slate-500 uppercase font-medium">Critical Crashes</div>
          <div className="text-2xl font-bold text-red-500 mt-1">{incident.metrics?.critical_count || 0}</div>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
          <div className="text-xs text-slate-500 uppercase font-medium">Warnings</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{incident.metrics?.warning_count || 0}</div>
        </div>
      </div>

      {/* Model Detection Evidence */}
      {incident.detector_triggers && (
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 mb-6">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-300 mb-2">
            <ShieldAlert className="w-4 h-4 text-blue-400" />
            Detection Evidence (Rule + Z-Score + Isolation Forest)
          </div>
          <p className="text-xs text-slate-400 font-mono bg-slate-950 p-3 rounded-lg border border-slate-800/80">
            {incident.detector_triggers}
          </p>
        </div>
      )}

      {/* AI Root-Cause Analysis */}
      <div className="p-6 rounded-2xl bg-gradient-to-b from-blue-950/20 to-slate-900/60 border border-blue-500/20 mb-6">
        <div className="flex items-center gap-2 text-sm font-semibold text-blue-400 mb-3">
          <Sparkles className="w-4 h-4" />
          LLM Root-Cause Diagnosis
        </div>

        <div className="space-y-4">
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Probable Technical Cause
            </h4>
            <p className="text-sm font-medium text-slate-200">
              {incident.probable_root_cause}
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
              Diagnostic Summary
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {incident.explanation}
            </p>
          </div>
        </div>
      </div>

      {/* Recommended SRE Actions */}
      {incident.recommended_actions && incident.recommended_actions.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 mb-6">
          <div className="flex items-center gap-2 text-sm font-semibold text-emerald-400 mb-4">
            <CheckCircle className="w-4 h-4" />
            Recommended Corrective Actions
          </div>
          <div className="space-y-2.5">
            {incident.recommended_actions.map((act, i) => (
              <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-slate-800/40 border border-slate-800 text-xs text-slate-200">
                <span className="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-[10px] flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span>{act}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Raw Suspicious Logs Preview */}
      {incident.sample_logs && incident.sample_logs.length > 0 && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-300 mb-3">
            <Terminal className="w-4 h-4 text-purple-400" />
            Suspicious Log Lines from Anomalous Window
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-[11px] text-slate-300 space-y-1 overflow-x-auto max-h-64">
            {incident.sample_logs.map((log, i) => (
              <div key={i} className="leading-relaxed whitespace-pre">
                {log}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

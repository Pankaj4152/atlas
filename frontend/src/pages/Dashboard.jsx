import React from 'react';
import {
  AlertTriangle,
  Clock,
  Activity,
  FileCheck,
  ChevronRight,
  TrendingUp,
  ShieldAlert,
  Server
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell
} from 'recharts';

export default function DashboardPage({ reportId, reportData, onSelectIncident, onNewAnalysis }) {
  if (!reportData) return null;

  const summary = reportData.summary || {};
  const fileInfo = reportData.file_info || {};
  const incidents = reportData.incidents || [];
  const timeline = (reportData.timeline || []).map((t, i) => ({
    ...t,
    label: t.window ? t.window.split(' ')[1] || `W${i+1}` : `W${i+1}`,
  }));

  const sevDist = summary.severity_distribution || {};
  const chartData = [
    { name: 'CRITICAL', count: sevDist.CRITICAL || 0, color: '#ef4444' },
    { name: 'ERROR', count: sevDist.ERROR || 0, color: '#f97316' },
    { name: 'WARNING', count: sevDist.WARNING || 0, color: '#eab308' },
    { name: 'INFO', count: sevDist.INFO || 0, color: '#3b82f6' },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Top Header Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Completed
            </span>
            <span className="text-xs text-slate-500">ID: {reportId}</span>
          </div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Server className="w-6 h-6 text-blue-400" />
            {fileInfo.file_name || 'Server Log Analysis'}
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Duration: {fileInfo.duration_seconds}s • File size: {fileInfo.file_size_kb} KB
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={`/api/reports/${reportId}/pdf`}
            download
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <FileCheck className="w-4 h-4 text-emerald-400" />
            Download PDF Report
          </a>

          <button
            onClick={onNewAnalysis}
            className="px-4 py-2 rounded-xl text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white transition shadow-sm"
          >
            New Analysis
          </button>
        </div>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Total Logs</div>
          <div className="text-3xl font-extrabold text-white">{summary.total_logs || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Across {summary.total_windows || 0} time windows</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Flagged Windows</div>
          <div className="text-3xl font-extrabold text-amber-400">{summary.flagged_windows || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Statistical / ML deviations</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Critical Incidents</div>
          <div className="text-3xl font-extrabold text-red-400">{summary.critical_incidents || 0}</div>
          <div className="text-xs text-slate-500 mt-1">Requiring immediate attention</div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Total Diagnosed</div>
          <div className="text-3xl font-extrabold text-blue-400">{summary.total_incidents || 0}</div>
          <div className="text-xs text-slate-500 mt-1">LLM root-cause diagnoses</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Anomaly Timeline */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-blue-400" />
                Error & Incident Timeline
              </h3>
              <p className="text-xs text-slate-400">Activity and flagged anomalies over time</p>
            </div>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="errorGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0}/>
                  </linearGradient>
                  <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="label" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Area type="monotone" dataKey="total_logs" stroke="#3b82f6" fillOpacity={1} fill="url(#totalGrad)" name="Total Logs" />
                <Area type="monotone" dataKey="errors" stroke="#ef4444" fillOpacity={1} fill="url(#errorGrad)" name="Errors" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Breakdown */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
          <h3 className="text-base font-semibold text-white mb-1 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            Severity Distribution
          </h3>
          <p className="text-xs text-slate-400 mb-4">Breakdown of log entry severity</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Incidents Table / Cards */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-sm">
        <h3 className="text-lg font-bold text-white mb-1">Detected Incidents & Diagnoses</h3>
        <p className="text-xs text-slate-400 mb-6">Select an incident to view deep-dive AI root-cause analysis</p>

        {incidents.length === 0 ? (
          <div className="text-center py-10 text-slate-500 text-sm">
            No anomalous incidents detected in this log file.
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((inc, index) => {
              const isCrit = inc.severity === 'critical';
              const isHigh = inc.severity === 'high';
              const badgeClass = isCrit
                ? 'bg-red-500/10 text-red-400 border-red-500/20'
                : isHigh
                ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20';

              return (
                <div
                  key={inc.incident_id || index}
                  onClick={() => onSelectIncident(inc)}
                  className="p-4 rounded-xl bg-slate-800/40 hover:bg-slate-800/90 border border-slate-800 hover:border-slate-700 transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-2.5 rounded-xl border ${badgeClass} mt-0.5`}>
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-white text-base">{inc.title}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border ${badgeClass}`}>
                          {inc.severity}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 line-clamp-1">
                        {inc.probable_root_cause}
                      </p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" />
                          {inc.time_window}
                        </span>
                        <span>•</span>
                        <span>{inc.metrics?.error_count || 0} errors, {inc.metrics?.critical_count || 0} criticals</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-blue-400 font-medium self-end md:self-center">
                    <span>View Diagnosis</span>
                    <ChevronRight className="w-4 h-4" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

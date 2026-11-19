import React from 'react';
import SectionEyebrow from '../components/SectionEyebrow';
import {
  FileText,
  Clock,
  ChevronRight,
  TrendingUp,
  Download,
  AlertTriangle,
  RotateCcw
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
    { name: 'CRITICAL', count: sevDist.CRITICAL || 0, color: '#c31833' },
    { name: 'ERROR', count: sevDist.ERROR || 0, color: '#000000' },
    { name: 'WARNING', count: sevDist.WARNING || 0, color: '#fa9000' },
    { name: 'INFO', count: sevDist.INFO || 0, color: '#595959' },
  ];

  const hasCritical = summary.critical_incidents > 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Editorial Breaking Band (if critical incidents found) */}
      {hasCritical && (
        <div className="bg-[#c31833] text-white px-4 py-2.5 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-black text-xs uppercase tracking-widest bg-black px-2 py-0.5 rounded-[2px]">
              CRITICAL INCIDENTS FLAGGED
            </span>
            <span className="text-sm font-bold truncate">
              {summary.critical_incidents} high-severity failure cascade(s) detected during analysis
            </span>
          </div>
          <span className="text-xs uppercase tracking-wider hidden sm:inline opacity-80">
            Immediate remediation advised
          </span>
        </div>
      )}

      {/* Masthead Header */}
      <div className="border-b border-[#000000] pb-6 mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2 h-2 rounded-full bg-[#fa9000]" />
            <span className="text-xs font-bold text-[#595959] uppercase tracking-wider">
              INVESTIGATIVE REPORT • REF: {reportId}
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-black tracking-tight">
            Telemetry Analysis: {fileInfo.file_name || 'Server Log File'}
          </h1>
          <p className="text-xs text-[#595959] mt-1">
            File Size: {fileInfo.file_size_kb} KB • Pipeline Processing Time: {fileInfo.duration_seconds}s • Analyzed at: {fileInfo.analyzed_at?.slice(0, 19).replace('T', ' ')}
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <a
            href={`/api/reports/${reportId}/pdf`}
            download
            className="inline-flex items-center gap-2 bg-black hover:bg-[#333333] text-white text-sm font-normal px-4 py-2 rounded-[18px] transition"
          >
            <Download className="w-4 h-4 text-[#fa9000]" />
            <span>Download Official PDF</span>
          </a>

          <button
            onClick={onNewAnalysis}
            className="inline-flex items-center gap-2 border border-[#d8d8d8] hover:bg-[#f0f0f0] text-black text-sm px-4 py-2 rounded-[18px] transition"
          >
            <RotateCcw className="w-4 h-4 text-[#595959]" />
            <span>New File</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Numbers (Editorial Grid with hairline rules) */}
      <div className="grid grid-cols-2 md:grid-cols-4 border-t border-b border-[#000000] py-6 mb-10 divide-x divide-[#d8d8d8]">
        <div className="px-4">
          <div className="text-xs font-bold text-[#595959] uppercase tracking-wider mb-1">Total Log Volume</div>
          <div className="text-4xl font-bold text-black">{summary.total_logs?.toLocaleString() || 0}</div>
          <div className="text-xs text-[#595959] mt-1">{summary.total_windows || 0} discrete time windows</div>
        </div>

        <div className="px-4">
          <div className="text-xs font-bold text-[#595959] uppercase tracking-wider mb-1">Flagged Windows</div>
          <div className="text-4xl font-bold text-[#fa9000]">{summary.flagged_windows || 0}</div>
          <div className="text-xs text-[#595959] mt-1">Multivariate outlier score</div>
        </div>

        <div className="px-4">
          <div className="text-xs font-bold text-[#595959] uppercase tracking-wider mb-1">Critical Outages</div>
          <div className="text-4xl font-bold text-[#c31833]">{summary.critical_incidents || 0}</div>
          <div className="text-xs text-[#595959] mt-1">Consensus model triggers</div>
        </div>

        <div className="px-4">
          <div className="text-xs font-bold text-[#595959] uppercase tracking-wider mb-1">Diagnosed Incidents</div>
          <div className="text-4xl font-bold text-black">{summary.total_incidents || 0}</div>
          <div className="text-xs text-[#595959] mt-1">LLM root-cause dossiers</div>
        </div>
      </div>

      {/* Layout Split: Left (Timeline + Breakdown) | Right (Incidents Rail) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-8">
          <div>
            <SectionEyebrow label="ACTIVITY & ERROR TIMELINE" />
            <div className="border border-[#d8d8d8] p-4 bg-white">
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="label" stroke="#595959" fontSize={11} tickLine={false} />
                    <YAxis stroke="#595959" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#d8d8d8', color: '#000000', fontSize: '12px' }}
                    />
                    <Area type="monotone" dataKey="total_logs" stroke="#595959" fill="#f0f0f0" fillOpacity={0.8} name="Total Volume" />
                    <Area type="monotone" dataKey="errors" stroke="#c31833" fill="#c31833" fillOpacity={0.2} name="Error Count" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-end gap-6 text-xs text-[#595959] mt-3 pt-2 border-t border-[#f0f0f0]">
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-[#f0f0f0] border border-[#595959]" />
                  <span>Total Volume</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 bg-[#c31833]" />
                  <span>Errors / Outages</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <SectionEyebrow label="LOG SEVERITY DISTRIBUTION" />
            <div className="border border-[#d8d8d8] p-4 bg-white">
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" stroke="#595959" fontSize={11} tickLine={false} />
                    <YAxis stroke="#595959" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#d8d8d8', color: '#000000', fontSize: '12px' }}
                    />
                    <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>

        {/* Right Rail: Detected Incidents Feed */}
        <div className="lg:border-l lg:border-[#d8d8d8] lg:pl-6">
          <SectionEyebrow label="FLAGGED INCIDENTS" />

          {incidents.length === 0 ? (
            <div className="py-12 text-center text-[#595959] text-sm">
              No anomalous incidents flagged by detection models.
            </div>
          ) : (
            <div className="divide-y divide-[#d8d8d8]">
              {incidents.map((inc, index) => {
                const isCrit = inc.severity === 'critical';
                const isHigh = inc.severity === 'high';

                return (
                  <div
                    key={inc.incident_id || index}
                    onClick={() => onSelectIncident(inc)}
                    className="py-4 hover:bg-[#f0f0f0] px-2 -mx-2 transition cursor-pointer group"
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      {isCrit ? (
                        <span className="bg-[#c31833] text-white text-[10px] font-black px-1.5 py-0.2 rounded-[2px] uppercase">
                          CRITICAL
                        </span>
                      ) : isHigh ? (
                        <span className="bg-[#fa9000] text-black text-[10px] font-bold px-1.5 py-0.2 rounded-[2px] uppercase">
                          HIGH SEVERITY
                        </span>
                      ) : (
                        <span className="bg-black text-white text-[10px] font-bold px-1.5 py-0.2 rounded-[2px] uppercase">
                          MEDIUM
                        </span>
                      )}
                      <span className="text-xs text-[#595959]">
                        {inc.time_window?.split(' to ')[0] || inc.time_window}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-black group-hover:text-[#fa9000] transition-colors leading-snug mb-1">
                      {inc.title}
                    </h3>
                    
                    <p className="text-xs text-[#333333] line-clamp-2 leading-relaxed mb-2">
                      {inc.probable_root_cause}
                    </p>

                    <div className="flex items-center justify-between text-xs text-[#595959]">
                      <span>{inc.metrics?.error_count || 0} err / {inc.metrics?.critical_count || 0} crit</span>
                      <span className="inline-flex items-center gap-1 text-black font-semibold group-hover:translate-x-1 transition-transform">
                        Examine Dossier <ChevronRight className="w-3.5 h-3.5 text-[#fa9000]" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

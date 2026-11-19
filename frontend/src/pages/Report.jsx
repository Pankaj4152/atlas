import React from 'react';
import SectionEyebrow from '../components/SectionEyebrow';
import {
  ArrowLeft,
  Clock,
  Download,
  AlertOctagon,
  CheckCircle,
  Terminal,
  ShieldAlert,
  Server
} from 'lucide-react';

export default function ReportPage({ incident, reportId, onBack }) {
  if (!incident) return null;

  const isCrit = incident.severity === 'critical';
  const isHigh = incident.severity === 'high';

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Return to Desk */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[#595959] hover:text-black mb-6 transition"
      >
        <ArrowLeft className="w-3.5 h-3.5 text-[#fa9000]" />
        <span>Return to Dashboard</span>
      </button>

      {/* Incident Lead Article Banner */}
      <div className="border-b-2 border-black pb-6 mb-8">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
          <div className="flex items-center gap-2">
            {isCrit ? (
              <span className="bg-[#c31833] text-white text-[11px] font-black px-2 py-0.5 rounded-[2px] uppercase tracking-wider">
                CRITICAL INVESTIGATION
              </span>
            ) : isHigh ? (
              <span className="bg-[#fa9000] text-black text-[11px] font-black px-2 py-0.5 rounded-[2px] uppercase tracking-wider">
                HIGH PRIORITY
              </span>
            ) : (
              <span className="bg-black text-white text-[11px] font-black px-2 py-0.5 rounded-[2px] uppercase tracking-wider">
                FLAGGED ANOMALY
              </span>
            )}
            <span className="text-xs text-[#595959] font-medium uppercase tracking-wide">
              DOSSIER ID: {incident.incident_id} • CONFIDENCE: {incident.confidence?.toUpperCase()}
            </span>
          </div>

          {reportId && (
            <a
              href={`/api/reports/${reportId}/pdf`}
              download
              className="inline-flex items-center gap-2 bg-black hover:bg-[#333333] text-white text-xs font-normal px-4 py-2 rounded-[18px] transition"
            >
              <Download className="w-3.5 h-3.5 text-[#fa9000]" />
              <span>Export Incident PDF</span>
            </a>
          )}
        </div>

        <h1 className="text-3xl md:text-5xl font-bold text-black tracking-tight leading-tight mb-2">
          {incident.title}
        </h1>

        <div className="flex items-center gap-2 text-xs text-[#595959]">
          <Clock className="w-3.5 h-3.5 text-[#fa9000]" />
          <span>Observed Window: <strong>{incident.time_window}</strong></span>
        </div>
      </div>

      {/* Metrics Row (Flat white with hairline rules) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 border border-[#d8d8d8] p-4 mb-8 bg-[#f0f0f0] divide-x divide-[#d8d8d8]">
        <div className="px-3">
          <div className="text-[11px] font-bold text-[#595959] uppercase tracking-wider">Window Volume</div>
          <div className="text-2xl font-bold text-black mt-0.5">{incident.metrics?.total_logs || 0}</div>
        </div>
        <div className="px-3">
          <div className="text-[11px] font-bold text-[#595959] uppercase tracking-wider">Observed Errors</div>
          <div className="text-2xl font-bold text-[#c31833] mt-0.5">{incident.metrics?.error_count || 0}</div>
        </div>
        <div className="px-3">
          <div className="text-[11px] font-bold text-[#595959] uppercase tracking-wider">Critical Crashes</div>
          <div className="text-2xl font-bold text-[#c31833] mt-0.5">{incident.metrics?.critical_count || 0}</div>
        </div>
        <div className="px-3">
          <div className="text-[11px] font-bold text-[#595959] uppercase tracking-wider">Warnings Recorded</div>
          <div className="text-2xl font-bold text-black mt-0.5">{incident.metrics?.warning_count || 0}</div>
        </div>
      </div>

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-8">
          {/* AI Root Cause Section */}
          <div>
            <SectionEyebrow label="AI SRE ROOT CAUSE DIAGNOSIS" />
            <div className="border-l-2 border-[#fa9000] pl-4 py-1 mb-4">
              <h3 className="text-lg font-bold text-black mb-1">
                Probable Technical Failure
              </h3>
              <p className="text-base text-[#333333] leading-relaxed">
                {incident.probable_root_cause}
              </p>
            </div>

            <div className="bg-white border border-[#d8d8d8] p-5">
              <h4 className="text-xs font-bold text-[#595959] uppercase tracking-wider mb-2">
                Diagnostic Narrative & Technical Context
              </h4>
              <p className="text-sm text-[#333333] leading-relaxed">
                {incident.explanation}
              </p>
            </div>
          </div>

          {/* Corrective Actions */}
          {incident.recommended_actions && incident.recommended_actions.length > 0 && (
            <div>
              <SectionEyebrow label="RECOMMENDED CORRECTIVE PROTOCOLS" />
              <div className="border border-[#d8d8d8] divide-y divide-[#d8d8d8] bg-white">
                {incident.recommended_actions.map((act, i) => (
                  <div key={i} className="p-4 flex items-start gap-3">
                    <span className="w-5 h-5 rounded-full bg-black text-white text-[11px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <span className="text-sm text-[#000000] leading-snug">{act}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Rail: Evidence & Traces */}
        <div className="lg:border-l lg:border-[#d8d8d8] lg:pl-6 space-y-8">
          {/* Machine Learning Evidence */}
          <div>
            <SectionEyebrow label="DETECTION EVIDENCE" />
            <div className="bg-[#f0f0f0] p-4 border border-[#d8d8d8]">
              <span className="text-[11px] font-bold text-[#595959] uppercase block mb-1">
                Consensus Triggers (Rule + Z-Score + Isolation Forest)
              </span>
              <p className="font-mono text-xs text-[#000000] leading-relaxed">
                {incident.detector_triggers || 'Consensus outlier detection.'}
              </p>
            </div>
          </div>

          {/* Log Evidence */}
          {incident.sample_logs && incident.sample_logs.length > 0 && (
            <div>
              <SectionEyebrow label="SUSPICIOUS LOG TELEMETRY" />
              <div className="bg-[#181818] p-4 text-[#dddddd] font-mono text-[11px] border border-[#333333] max-h-80 overflow-y-auto space-y-1.5 rounded-[2px]">
                {incident.sample_logs.map((log, i) => (
                  <div key={i} className="leading-snug break-all pb-1 border-b border-[#323232]">
                    {log}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

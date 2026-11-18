import React, { useState } from 'react';
import { Upload, FileText, AlertCircle, ArrowRight, Loader2, Sparkles, CheckCircle2 } from 'lucide-react';

export default function UploadPage({ onAnalysisComplete }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);

    try {
      // Step 1: Upload file
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) {
        throw new Error('Failed to upload log file');
      }

      const uploadData = await uploadRes.json();
      const fileId = uploadData.file.file_id;

      // Step 2: Trigger analysis pipeline
      const analyzeRes = await fetch(`/api/analyze/${fileId}`, {
        method: 'POST',
      });

      if (!analyzeRes.ok) {
        throw new Error('Analysis pipeline failed');
      }

      const resultData = await analyzeRes.json();
      onAnalysisComplete(resultData.report_id, resultData.report);
    } catch (err) {
      setError(err.message || 'An error occurred during log analysis');
    } finally {
      setIsUploading(false);
    }
  };

  // Helper to load sample test logs quickly for presentation/evaluation
  const handleLoadSample = async () => {
    setIsUploading(true);
    setError(null);
    try {
      const sampleText = `# Sample Server Log
2026-11-18 10:00:01 INFO [system] Server process started with PID 4120
2026-11-18 10:00:02 INFO [db] Database connection pool initialized with 20 connections
2026-11-18 10:00:05 INFO [auth] User 1029 authenticated successfully from 192.168.1.10
2026-11-18 10:01:10 WARN [system] Memory usage reached 78% of threshold
2026-11-18 10:01:35 WARN [db] Query slow: SELECT * FROM transactions executed in 1240ms
2026-11-18 10:03:01 WARN [db] High latency on db connection checkout: 2300ms
2026-11-18 10:03:02 ERROR [db] Connection pool exhausted: active=20, max=20, pending=15
2026-11-18 10:03:03 ERROR [api] Connection timeout to database server 10.0.0.5:5432 after 5000ms
2026-11-18 10:03:04 ERROR [api] Failed to process request POST /api/v1/orders: 500 Internal Server Error
2026-11-18 10:03:07 ERROR [db] Database connection refused: host 10.0.0.5 unavailable
2026-11-18 10:03:10 CRITICAL [system] Service worker thread #3 crashed: unhandled DBConnectionError
2026-11-18 10:03:15 CRITICAL [system] Service worker thread #4 crashed: unhandled DBConnectionError
2026-11-18 10:03:20 CRITICAL [system] Out of active workers: 0 of 4 workers responding
2026-11-18 10:04:05 INFO [system] Spawned 4 replacement worker threads
2026-11-18 10:04:10 INFO [db] Database connection re-established with host 10.0.0.5`;

      const sampleBlob = new Blob([sampleText], { type: 'text/plain' });
      const sampleFileObj = new File([sampleBlob], 'sample_server.log', { type: 'text/plain' });
      setFile(sampleFileObj);

      const formData = new FormData();
      formData.append('file', sampleFileObj);

      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const uploadData = await uploadRes.json();
      const analyzeRes = await fetch(`/api/analyze/${uploadData.file.file_id}`, { method: 'POST' });
      const resultData = await analyzeRes.json();
      onAnalysisComplete(resultData.report_id, resultData.report);
    } catch (err) {
      setError(err.message || 'Failed to analyze sample');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Title */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-4">
          <Sparkles className="w-4 h-4" />
          <span>Server Log AI Diagnosis</span>
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-white mb-3">
          AI-Powered Server Anomaly Detector
        </h1>
        <p className="text-slate-400 max-w-xl mx-auto text-base">
          Upload server logs to run statistical Z-score checks, Isolation Forest ML models, Drain3 log pattern clustering, and LLM root-cause analysis.
        </p>
      </div>

      {/* Upload Box */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 bg-slate-900/40 backdrop-blur-sm ${
          dragOver
            ? 'border-blue-500 bg-blue-500/5'
            : 'border-slate-700/80 hover:border-slate-600'
        }`}
      >
        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mx-auto mb-4 text-blue-400">
          <Upload className="w-8 h-8" />
        </div>

        <h3 className="text-lg font-semibold text-white mb-1">
          Drag and drop your server log file
        </h3>
        <p className="text-sm text-slate-400 mb-6">
          Supports <code className="text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded">.log</code>,{' '}
          <code className="text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded">.txt</code>, and structured{' '}
          <code className="text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded">.csv</code>
        </p>

        <label className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm cursor-pointer transition border border-slate-700">
          Browse Files
          <input
            type="file"
            className="hidden"
            accept=".log,.txt,.csv"
            onChange={handleFileChange}
          />
        </label>

        {file && (
          <div className="mt-6 inline-flex items-center gap-3 px-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-sm text-slate-200">
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="font-medium">{file.name}</span>
            <span className="text-slate-500">({(file.size / 1024).toFixed(1)} KB)</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-center gap-3 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={handleAnalyze}
          disabled={!file || isUploading}
          className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-xl font-semibold text-sm transition-all shadow-lg ${
            !file || isUploading
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20 hover:shadow-blue-500/30 cursor-pointer'
          }`}
        >
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Running Anomaly Pipeline...</span>
            </>
          ) : (
            <>
              <span>Analyze Server Logs</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>

        <button
          onClick={handleLoadSample}
          disabled={isUploading}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl font-medium text-sm text-slate-400 hover:text-slate-200 bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800 transition"
        >
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span>Quick Demo with Sample Log</span>
        </button>
      </div>
    </div>
  );
}

# Anomaly Detection in Servers Using Large Language Models (LLMs)

**Minor Project V1 — Production Log Analyzer & AI Diagnostic Engine**  
**Student Name:** Pankaj Kumar Goyal  
**Roll Number:** 24UCSE40W2  

---

## 1. Project Overview & Architecture

Modern cloud servers and microservices generate thousands of unstructured log events every minute. Traditional monitoring tools (like keyword grepping or static threshold alerts) suffer from high false-alarm fatigue and require engineers to spend hours investigating raw stacktraces.

This project delivers an **end-to-end AI-powered log anomaly detection and diagnosis system**:
1. **Ingestion & Parsing**: Normalizes timestamps, canonical log levels, components, and messages across standard formats, HDFS, and BGL datasets.
2. **Template Mining (Drain3)**: Uses parse-tree clustering with dynamic variable masking (IPs, UUIDs, numeric IDs) to turn raw text into event IDs (`E001`, `E002`) and detect rare patterns.
3. **Statistical & ML Feature Extraction**: Slices continuous streams into 1-minute time windows and calculates 8 numerical metrics (error count, volume change velocity, rare event frequencies).
4. **Hybrid Ensemble Detection**: Combines **Rule-Based heuristics**, **Z-Score statistical deviations**, and unsupervised **Isolation Forest** machine learning with a consensus voting policy.
5. **LLM Diagnostic Engine**: Feeds only the flagged anomaly context window into an LLM (Gemini / OpenAI API with offline heuristic fallback) to produce:
   - Incident summary title
   - Probable technical root cause
   - Diagnostic explanation
   - Concrete, numbered remediation actions
6. **Interactive Dashboard & PDF Export**: Real-time React dashboard with Recharts timelines and downloadable executive ReportLab PDF reports.

```
+-----------------------------------------------------------------------------------+
|                              SYSTEM ARCHITECTURE                                  |
+-----------------------------------------------------------------------------------+
                                  
  [ Server Log File ] (.log / .txt / .csv / HDFS / BGL)
         │
         ▼
  [ Log Parser ] ──────────────► Normalizes timestamps, components & severity levels
         │
         ▼
  [ Drain3 Miner ] ────────────► Token masking (<IP>, <NUM>) -> Mines Event IDs & Rare Events
         │
         ▼
  [ Feature Extraction ] ──────► 1-minute window vectors (error count, ratio, volume velocity)
         │
         ▼
  [ Ensemble Detector ] ───────► Consensus Voting:
         │                        • Rule-Based Baseline
         │                        • Z-Score Statistical ($|Z| \ge 2.0$)
         │                        • Isolation Forest Unsupervised ML
         ▼
  [ LLM Context Builder ] ─────► Extracts only anomalous window logs & metrics
         │
         ▼
  [ LLM SRE Diagnostician ] ───► Evaluates root causes & remediation steps (Gemini / OpenAI)
         │
         ▼
  [ SQLite + FastAPI ] ────────► REST endpoints for uploads, reports & ReportLab PDF streaming
         │
         ▼
  [ React + Vite UI ] ─────────► Executive Dashboard, Recharts Timeline, and History Modal
```

---

## 2. Quantitative Evaluation & Benchmark Results

Evaluated on `sample_logs/production_server_large.log` (5,000 production logs across 63 time windows):

| Model / Approach | Precision | Recall | F1-Score | False Positive Rate | Detection Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rule-Based (Baseline)** | 0.250 | 1.000 | 0.400 | 37.5% | 1.87 ms |
| **Z-Score (Statistical)** | 0.875 | 1.000 | 0.933 | 1.8% | 1.08 ms |
| **Isolation Forest (ML)** | 1.000 | 0.143 | 0.250 | 0.0% | 83.56 ms |
| **Hybrid Ensemble (Our System)** | **1.000** | **1.000** | **1.000** | **0.0%** | **90.09 ms** |

### Key Academic Findings
1. **Rule-Based Baseline**: Caught all critical failures ($Recall = 1.00$), but suffered from high false alarm rates ($FPR = 37.5\%$) caused by normal operational spikes.
2. **Z-Score**: High accuracy on volumetric spikes ($F1 = 0.933$), but struggles on multi-dimensional anomalies where volume is low but rare error patterns appear.
3. **Isolation Forest**: Highly specific ($Precision = 1.00$, zero false positives), but misses subtle volume surges unless combined with statistical indicators.
4. **Our Hybrid Ensemble**: Consensus voting eliminates single-detector false positives while maintaining zero missed anomalies ($F1 = 1.00$).

---

## 3. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS, Recharts, Lucide Icons |
| **Backend API** | Python 3.13, FastAPI, Uvicorn, Pydantic v2 |
| **Log Parsing** | Regular Expressions, Python-Dateutil, Drain3 |
| **Machine Learning & Math** | Scikit-learn (Isolation Forest), NumPy, Pandas |
| **LLM Reasoning** | Google Gemini API / OpenAI API (with offline diagnostic fallback) |
| **Persistence** | SQLite3 |
| **Report Export** | ReportLab (Executive PDF generation) |

---

## 4. How to Run the Application

### 1. Backend Server
```powershell
# From project root
uvicorn backend.main:app --reload --port 8000
```
Backend will be live at: `http://127.0.0.1:8000` (API documentation at `/docs`).

### 2. Frontend Application
```powershell
cd frontend
npm run dev
```
Frontend will be live at: `http://localhost:5173`.

### 3. Run Automated Tests
```powershell
python -m pytest tests/ -v
```

### 4. Run Model Evaluation Benchmark
```powershell
python -m notebooks.evaluate_models
```

---

## 5. Viva / Presentation Q&A Preparation

**Q1: Why did you use Drain3 instead of passing raw logs to an LLM?**  
*Answer:* A production server can emit over 100,000 logs an hour. Sending raw text to an LLM is too expensive, slow, and exceeds context windows. Drain3 compresses 100,000 lines into 10–20 structured event templates and flags rare events in milliseconds, allowing the ML algorithms to work on numbers rather than text.

**Q2: What is the benefit of the Ensemble over a single model?**  
*Answer:* As shown in our benchmark, Rule-Based monitors have a 37.5% false positive rate, while Isolation Forest had lower recall on simple volume surges. Our consensus voting policy eliminates individual model weaknesses, achieving an F1-Score of 1.00.

**Q3: How does the LLM integration work?**  
*Answer:* The ML ensemble pins down the exact anomalous 1-minute window. We extract only the 10–15 suspicious logs within that window and pass them to the LLM with a strict Pydantic JSON schema. The LLM acts as an expert SRE diagnostician, returning root cause and actionable remediation steps.

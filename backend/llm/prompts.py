"""
Prompt engineering templates for server anomaly root-cause analysis.
"""

from backend.llm.schemas import AnomalyContext

SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) and server systems diagnostician.
Your job is to analyze anomalous server log windows detected by statistical and ML models, identify the probable root cause, determine the real severity, and provide concrete, actionable troubleshooting instructions.

Respond strictly with valid JSON conforming to this schema:
{
  "title": "Concise summary title of the incident",
  "severity": "critical" | "high" | "medium" | "low",
  "probable_root_cause": "Detailed technical root cause",
  "confidence": "high" | "medium" | "low",
  "explanation": "Clear, concise plain English summary for system administrators",
  "recommended_actions": [
    "Step 1 actionable recommendation",
    "Step 2 actionable recommendation",
    "Step 3 actionable recommendation"
  ]
}
Do not include markdown code fence formatting (```json) in your raw response if possible, just the valid JSON object.
"""


def format_user_prompt(ctx: AnomalyContext) -> str:
    """Format an AnomalyContext into a clear prompt for the LLM."""
    templates_str = "\n".join(f"- {t}" for t in ctx.top_templates) if ctx.top_templates else "None detected"
    raw_logs_str = "\n".join(ctx.sample_raw_logs) if ctx.sample_raw_logs else "No explicit error lines"

    return f"""Incident ID: {ctx.incident_id}
Time Window: {ctx.time_window}
Model Severity Hint: {ctx.severity_hint}
Window Metrics:
- Total Logs: {ctx.total_logs}
- Error Count: {ctx.error_count}
- Critical Count: {ctx.critical_count}
- Warning Count: {ctx.warning_count}
- Detector Triggers: {ctx.detector_summary}

Dominant Log Patterns / Templates:
{templates_str}

Key Suspicious Raw Logs:
{raw_logs_str}

Analyze the logs and return the JSON analysis report.
"""

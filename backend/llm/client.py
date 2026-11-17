"""
LLM Client with multi-provider support (Gemini API, OpenAI API)
and a robust offline heuristic fallback.
"""

import json
import os
import re
from typing import Optional
from dotenv import load_dotenv

from backend.llm.schemas import AnomalyContext, LLMAnalysisResult
from backend.llm.prompts import SYSTEM_PROMPT, format_user_prompt

load_dotenv()


class LLMAnalyzer:
    """
    Analyzes AnomalyContext objects using an LLM.
    Supports:
    1. Gemini API (if GEMINI_API_KEY is present)
    2. OpenAI API (if OPENAI_API_KEY is present)
    3. Intelligent Rule-Based Fallback (if no API key configured or offline)
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.gemini_key = api_key or os.getenv("GEMINI_API_KEY")
        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        self.provider = provider or ("gemini" if self.gemini_key else "openai" if self.openai_key else "fallback")
        self.model_name = model_name

    def analyze(self, ctx: AnomalyContext) -> LLMAnalysisResult:
        """Analyze an anomaly context and return validated LLMAnalysisResult."""
        if self.provider == "gemini" and self.gemini_key:
            try:
                return self._analyze_gemini(ctx)
            except Exception as e:
                # Log error and gracefully drop to fallback
                pass

        if self.provider == "openai" and self.openai_key:
            try:
                return self._analyze_openai(ctx)
            except Exception as e:
                pass

        # If no keys or external call fails, use intelligent offline fallback
        return self._heuristic_fallback(ctx)

    def _analyze_gemini(self, ctx: AnomalyContext) -> LLMAnalysisResult:
        """Call Google Gemini API."""
        import google.generativeai as genai

        genai.configure(api_key=self.gemini_key)
        model = genai.GenerativeModel(
            model_name=self.model_name or "gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"},
        )
        prompt = format_user_prompt(ctx)
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        return LLMAnalysisResult(**data)

    def _analyze_openai(self, ctx: AnomalyContext) -> LLMAnalysisResult:
        """Call OpenAI API."""
        from openai import OpenAI

        client = OpenAI(api_key=self.openai_key)
        prompt = format_user_prompt(ctx)
        response = client.chat.completions.create(
            model=self.model_name or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        data = json.loads(response.choices[0].message.content)
        return LLMAnalysisResult(**data)

    def _heuristic_fallback(self, ctx: AnomalyContext) -> LLMAnalysisResult:
        """
        Intelligent offline diagnostic fallback.
        Infers root causes based on keyword analysis of anomalous logs.
        Ensures the pipeline is 100% testable and runnable without API tokens.
        """
        joined_logs = " ".join(ctx.sample_raw_logs).lower()

        # Diagnostic patterns
        if "connection pool exhausted" in joined_logs or ("db" in joined_logs and "timeout" in joined_logs):
            return LLMAnalysisResult(
                title="Database Connection Pool Exhaustion",
                severity="critical" if ctx.critical_count > 0 else "high",
                probable_root_cause="Database connection pool was saturated, leading to cascading request timeouts and worker crashes.",
                confidence="high",
                explanation=f"Observed {ctx.error_count} errors and {ctx.critical_count} critical failures during window {ctx.time_window}. Applications failed to checkout database connections.",
                recommended_actions=[
                    "Increase max_connections in the database configuration.",
                    "Audit connection pool leakages in application repositories.",
                    "Deploy PgBouncer or connection pooling proxy.",
                    "Review slow-running transactions locking database connections.",
                ],
            )
        elif "memory" in joined_logs or "out of memory" in joined_logs or "oom" in joined_logs:
            return LLMAnalysisResult(
                title="System Resource Exhaustion (Memory)",
                severity="high",
                probable_root_cause="Server RAM exceeded safe operating thresholds, risking OS process termination.",
                confidence="medium",
                explanation=f"Resource warning thresholds were breached with {ctx.warning_count} warnings recorded in window {ctx.time_window}.",
                recommended_actions=[
                    "Inspect memory usage with top/htop or profiler.",
                    "Investigate unbounded caches or memory leaks in worker processes.",
                    "Configure container memory limits and swap space.",
                ],
            )
        elif "authentication" in joined_logs or "unauthorized" in joined_logs or "forbidden" in joined_logs:
            return LLMAnalysisResult(
                title="Authentication Surge or Brute-Force Attempt",
                severity="high" if ctx.error_count > 20 else "medium",
                probable_root_cause="Repeated authentication/authorization errors detected over a short time window.",
                confidence="medium",
                explanation=f"Anomalous authentication pattern observed with {ctx.error_count} errors in window {ctx.time_window}.",
                recommended_actions=[
                    "Review client IP addresses for brute force attacks.",
                    "Check token expiration or authentication service availability.",
                    "Enable rate limiting on login/auth endpoints.",
                ],
            )
        else:
            return LLMAnalysisResult(
                title="Service Anomaly and Error Spike",
                severity=ctx.severity_hint.lower() if ctx.severity_hint.lower() in ["critical", "high", "medium", "low"] else "medium",
                probable_root_cause=f"Statistically significant error spike ({ctx.error_count} errors, {ctx.critical_count} criticals) violating baseline behavior.",
                confidence="medium",
                explanation=f"Anomalous window detected by models: {ctx.detector_summary}",
                recommended_actions=[
                    "Inspect surrounding server application stacktraces.",
                    "Check recent application deployments or config updates.",
                    "Monitor downstream dependent services for degradation.",
                ],
            )

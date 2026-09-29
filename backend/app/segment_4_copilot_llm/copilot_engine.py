"""
Segment 4: Groq LLM Copilot Engine
Calls Groq LLM API to format investigation rationale and validate JSON outputs.
"""
import httpx
from typing import Dict, Any
from app.config import settings
from app.models.schemas import InvestigationResult, Recommendation, HistoricalMatch

class CopilotEngine:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_investigation(
        self,
        raw_input: Any,
        source: str,
        synthesized_context: Dict[str, Any]
    ) -> InvestigationResult:
        """
        Synthesizes final InvestigationResult payload for Segment 6 Frontend.
        """
        rec_dict = synthesized_context["recommendation"]
        hist_matches = [
            HistoricalMatch(**m) for m in synthesized_context.get("historical_matches", [])
        ]
        
        recommendation_obj = Recommendation(**rec_dict)
        preview = str(raw_input)[:200] if isinstance(raw_input, str) else str(raw_input)

        # If Groq API key is present, refine rationale using Groq LLM (openai/gpt-oss-120b)
        if self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                prompt = (
                    f"You are CyberGuard Security Copilot. Write a concise 2-sentence rationale for this SOC alert:\n"
                    f"Alert Details: {preview}\n"
                    f"Recommended Action: {recommendation_obj.resolution}\n"
                    f"Empirical Historical Success Rate: {round(recommendation_obj.success_rate * 100, 1)}%"
                )
                async with httpx.AsyncClient(timeout=8.0) as client:
                    res = await client.post(
                        self.groq_url,
                        headers=headers,
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "max_tokens": 150
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        llm_text = data["choices"][0]["message"]["content"]
                        if llm_text:
                            recommendation_obj.rationale = llm_text.strip()
            except Exception as e:
                print(f"[Groq Copilot Warning] LLM call skipped, using memory template rationale: {e}")

        return InvestigationResult(
            is_cold_start=synthesized_context.get("is_cold_start", False),
            historical_matches=hist_matches,
            recommendation=recommendation_obj,
            source=source,
            user_input_preview=preview
        )

copilot_service = CopilotEngine()

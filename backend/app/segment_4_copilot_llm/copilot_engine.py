"""
Segment 4: Groq LLM Copilot Engine
Calls Groq LLM API to format investigation rationale and validate JSON outputs.
"""
from typing import Dict, Any
from app.config import settings
from app.models.schemas import InvestigationResult, Recommendation, HistoricalMatch

class CopilotEngine:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL

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

        # If Groq API key is present, optionally refine rationale using Groq LLM
        if self.api_key:
            try:
                import groq
                client = groq.AsyncGroq(api_key=self.api_key)
                prompt = (
                    f"You are CyberGuard Security Copilot. Summarize rationale for alert: {preview}\n"
                    f"Recommended Action: {recommendation_obj.resolution}\n"
                    f"Historical success rate: {recommendation_obj.success_rate * 100}%"
                )
                chat_completion = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model,
                    max_tokens=150
                )
                llm_rationale = chat_completion.choices[0].message.content
                if llm_rationale:
                    recommendation_obj.rationale = llm_rationale.strip()
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

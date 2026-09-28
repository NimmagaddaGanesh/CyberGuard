import json
import os

from openai import OpenAI


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1"
        )

        self.model = os.environ.get(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

    def generate_recommendation(
        self,
        incident: dict,
        memories: list[dict]
    ) -> dict:

        memory_text = "\n".join(
            f"- [{item.get('memory_type')}] {item['content']}"
            for item in memories
        )

        prompt = f"""
You are CyberGuard, a SOC incident-response assistant.

Analyze the current incident using the retrieved historical memories.

CURRENT INCIDENT:
{json.dumps(incident, indent=2)}

RETRIEVED MEMORIES:
{memory_text or "No relevant memories found."}

Return only valid JSON with this structure:
{{
  "root_cause": "string",
  "confidence_score": 0.0,
  "recommended_response": ["string"],
  "recommended_playbook": "string or null",
  "lessons_learned": ["string"]
}}

Rules:
- Do not invent evidence.
- Use retrieved memories when relevant.
- Recommendations are advisory.
- If uncertain, use a lower confidence score.
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return json.loads(response.output_text)
import json
import os
from typing import Any

from openai import OpenAI


class AIResponseGenerator:

    def __init__(self):

        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key
        )

        # Change this model only if your account/project
        # uses a different available model.
        self.model = "gpt-4o-mini"

    def _build_prompt(
        self,
        analysis: dict[str, Any]
    ) -> str:

        return f"""
You are CyberGuard, a cybersecurity incident-response assistant.

Analyze the incident using ONLY the information provided below.

Do not invent facts, historical incidents, success rates,
confidence scores, or technical evidence.

If the available evidence is insufficient, explicitly say so.

CURRENT INCIDENT:
{json.dumps(
    analysis.get("incident_profile", {}),
    indent=2
)}

CURRENT ROOT CAUSE:
{analysis.get("current_root_cause")}

CURRENT RECOMMENDED PLAYBOOK:
{analysis.get("recommended_playbook")}

PREVIOUSLY TRIED ACTIONS:
{json.dumps(
    analysis.get("previously_tried_actions", []),
    indent=2
)}

HISTORICAL EVIDENCE:
{json.dumps(
    analysis.get("historical_evidence", {}),
    indent=2
)}

Generate a practical incident-response assessment.

Return ONLY valid JSON with exactly these fields:

{{
    "assessment": "Brief assessment of the incident.",
    "likely_root_cause": "Root cause supported by the available evidence.",
    "recommended_actions": [
        "Action 1",
        "Action 2",
        "Action 3"
    ],
    "recommended_playbook": "Relevant playbook ID if supported by evidence, otherwise null.",
    "reasoning": "Brief explanation connecting the evidence to the recommendation.",
    "evidence_used": [
        "Evidence 1",
        "Evidence 2"
    ]
}}

Keep the response concise and operational.
"""

    def generate_response(
        self,
        analysis: dict[str, Any]
    ) -> dict[str, Any]:

        prompt = self._build_prompt(
            analysis
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful cybersecurity "
                        "incident-response assistant. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            response_format={
                "type": "json_object"
            }
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "OpenAI returned an empty response."
            )

        return json.loads(content)

    def generate_batch(
        self,
        analyses: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:

        responses = []

        for index, analysis in enumerate(analyses, start=1):

            print(
                f"Generating response "
                f"{index}/{len(analyses)}..."
            )

            try:

                ai_response = self.generate_response(
                    analysis
                )

                result = {
                    "incident_id":
                        analysis["incident_id"],

                    **ai_response
                }

            except Exception as e:

                result = {
                    "incident_id":
                        analysis["incident_id"],

                    "error":
                        type(e).__name__,

                    "error_message":
                        str(e)
                }

            responses.append(result)

        return responses


def load_json(filepath: str) -> dict:

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_json(
    filepath: str,
    data: dict
):

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )
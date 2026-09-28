import json
from typing import Any


class ContextSynthesizer:

    def __init__(self):
        pass

    def _extract_content(self, matches: list[dict]) -> list[str]:
        contents = []

        for match in matches:
            content = match.get("content")

            if content and content not in contents:
                contents.append(content)

        return contents

    def synthesize_incident(self, result: dict) -> dict:
        incident_matches = self._extract_content(
            result.get("incident_matches", [])
        )

        resolution_matches = self._extract_content(
            result.get("resolution_matches", [])
        )

        root_cause_matches = self._extract_content(
            result.get("root_cause_matches", [])
        )

        playbook_matches = self._extract_content(
            result.get("playbook_matches", [])
        )

        return {
            "incident_id": result["incident_id"],

            "historical_incidents": incident_matches,

            "historical_resolutions": resolution_matches,

            "historical_root_causes": root_cause_matches,

            "relevant_playbooks": playbook_matches,

            "evidence_summary": {
                "incident_matches_count": len(incident_matches),
                "resolution_matches_count": len(resolution_matches),
                "root_cause_matches_count": len(root_cause_matches),
                "playbook_matches_count": len(playbook_matches)
            }
        }

    def synthesize_batch(
        self,
        results: list[dict]
    ) -> list[dict]:

        synthesized = []

        for result in results:
            synthesized.append(
                self.synthesize_incident(result)
            )

        return synthesized


def load_retrieved_context(
    filepath: str
) -> dict[str, Any]:

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_synthesized_context(
    filepath: str,
    output: dict[str, Any]
):

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )
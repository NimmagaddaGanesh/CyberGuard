import json
from typing import Any


class IncidentAnalyzer:

    def __init__(self):
        pass

    def _get_resolution_actions(
        self,
        incident: dict
    ) -> list[str]:

        actions = []

        for resolution in incident.get("resolutions_tried", []):
            if isinstance(resolution, dict):
                action = resolution.get("action")

                if action:
                    actions.append(action)

        return actions

    def analyze_incident(
        self,
        incident: dict,
        synthesized_context: dict
    ) -> dict[str, Any]:

        historical_incidents = synthesized_context.get(
            "historical_incidents", []
        )

        historical_resolutions = synthesized_context.get(
            "historical_resolutions", []
        )

        historical_root_causes = synthesized_context.get(
            "historical_root_causes", []
        )

        relevant_playbooks = synthesized_context.get(
            "relevant_playbooks", []
        )

        previous_actions = self._get_resolution_actions(
            incident
        )

        return {
            "incident_id": incident["incident_id"],

            "incident_profile": {
                "category": incident.get("category"),
                "incident_type": incident.get("incident_type"),
                "severity": incident.get("severity"),
                "affected_system": incident.get("affected_system"),
                "symptoms": incident.get("symptoms", []),
                "indicators_of_compromise": incident.get(
                    "indicators_of_compromise", []
                )
            },

            "current_root_cause": incident.get(
                "root_cause"
            ),

            "recommended_playbook": incident.get(
                "recommended_playbook"
            ),

            "previously_tried_actions": previous_actions,

            "historical_evidence": {
                "similar_incidents": historical_incidents,
                "previous_resolutions": historical_resolutions,
                "historical_root_causes": historical_root_causes,
                "relevant_playbooks": relevant_playbooks
            },

            "evidence_counts": {
                "similar_incidents": len(
                    historical_incidents
                ),
                "previous_resolutions": len(
                    historical_resolutions
                ),
                "historical_root_causes": len(
                    historical_root_causes
                ),
                "relevant_playbooks": len(
                    relevant_playbooks
                )
            }
        }

    def analyze_batch(
        self,
        incidents: list[dict],
        synthesized_results: list[dict]
    ) -> list[dict]:

        context_by_id = {
            item["incident_id"]: item
            for item in synthesized_results
        }

        analyses = []

        for incident in incidents:

            incident_id = incident["incident_id"]

            context = context_by_id.get(
                incident_id,
                {}
            )

            analyses.append(
                self.analyze_incident(
                    incident,
                    context
                )
            )

        return analyses


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
import asyncio
import os
from typing import Any

from hindsight_client import Hindsight


class MemoryRetriever:
    def __init__(self):
        self.bank_id = os.environ["HINDSIGHT_BANK_ID"]

        self.client = Hindsight(
            base_url=os.environ["HINDSIGHT_BASE_URL"],
            api_key=os.environ["HINDSIGHT_API_KEY"]
        )

        # Prevent too many requests from being sent at once.
        # Four Hindsight queries still run in parallel for each incident.
        self.semaphore = asyncio.Semaphore(5)

    async def _recall(self, query: str):
        return await self.client.arecall(
            bank_id=self.bank_id,
            query=query,
            max_tokens=3000,
            budget="mid"
        )

    def _format_results(self, result) -> list[dict[str, Any]]:
        memories = []

        for item in getattr(result, "results", []):
            memories.append({
                "memory_id": (
                    getattr(item, "id", None)
                    or getattr(item, "memory_id", None)
                ),
                "memory_type": getattr(item, "type", None),
                "content": getattr(item, "text", str(item))
            })

        return memories

    def _build_queries(self, incident: dict) -> dict:
        symptoms = ", ".join(incident.get("symptoms", []))

        iocs = ", ".join(
            str(x)
            for x in incident.get("indicators_of_compromise", [])
        )

        incident_type = incident.get("incident_type", "")
        category = incident.get("category", "")
        affected_system = incident.get("affected_system", "")

        base = (
            f"Incident type: {incident_type}. "
            f"Category: {category}. "
            f"Affected system: {affected_system}. "
            f"Symptoms: {symptoms}. "
            f"Indicators of compromise: {iocs}."
        )

        return {
            "incident": (
                "Find previous cybersecurity incidents similar to this incident. "
                "Focus on matching symptoms, IOCs, incident type and attack patterns. "
                + base
            ),

            "resolution": (
                "Find previous resolutions used for similar cybersecurity incidents. "
                "Focus on successful and unsuccessful actions, analyst feedback "
                "and lessons learned. "
                + base
            ),

            "root_cause": (
                "Find historical root causes associated with incidents having "
                "similar symptoms and attack characteristics. "
                "Identify recurring root causes and supporting evidence. "
                + base
            ),

            "playbook": (
                "Find cybersecurity playbooks, SOPs and runbooks relevant to "
                "this incident type and attack pattern. "
                + base
            )
        }

    async def retrieve_for_incident(self, incident: dict) -> dict:
        # Limit the number of incidents being processed simultaneously.
        async with self.semaphore:

            queries = self._build_queries(incident)

            (
                incident_result,
                resolution_result,
                root_cause_result,
                playbook_result
            ) = await asyncio.gather(
                self._recall(queries["incident"]),
                self._recall(queries["resolution"]),
                self._recall(queries["root_cause"]),
                self._recall(queries["playbook"])
            )

            return {
                "incident_id": incident["incident_id"],

                "incident_matches": self._format_results(
                    incident_result
                ),

                "resolution_matches": self._format_results(
                    resolution_result
                ),

                "root_cause_matches": self._format_results(
                    root_cause_result
                ),

                "playbook_matches": self._format_results(
                    playbook_result
                )
            }

    async def retrieve_batch(
        self,
        incidents: list[dict]
    ) -> list[dict]:
        tasks = [
            self.retrieve_for_incident(incident)
            for incident in incidents
        ]

        return await asyncio.gather(*tasks)

    async def store_incident(self, incident: dict) -> None:
        content = (
            f"CyberGuard incident {incident['incident_id']} was a "
            f"{incident.get('severity', '')}-severity "
            f"{incident.get('incident_type', '')} affecting "
            f"{incident.get('affected_system', '')}. "
            f"Description: {incident.get('description', '')}. "
            f"Symptoms: {', '.join(incident.get('symptoms', []))}. "
            f"Indicators of compromise: "
            f"{', '.join(str(x) for x in incident.get('indicators_of_compromise', []))}. "
            f"Analyst: {incident.get('analyst_id', '')}."
        )

        await self.client.aretain(
            bank_id=self.bank_id,
            content=content
        )

    async def store_outcome(self, feedback: dict) -> None:
        resolution = "; ".join(
            feedback.get("resolution", [])
        )

        lessons = "; ".join(
            feedback.get("lessons_learned", [])
        )

        content = (
            f"Incident {feedback['incident_id']} was resolved using: "
            f"{resolution}. "
            f"Resolution successful: "
            f"{feedback.get('resolution_success')}. "
            f"Success score: "
            f"{feedback.get('success_score')}. "
            f"Analyst feedback: "
            f"{feedback.get('analyst_feedback') or 'None'}. "
            f"Lessons learned: "
            f"{lessons or 'None'}. "
            f"Analyst: "
            f"{feedback.get('analyst_id', '')}."
        )

        await self.client.aretain(
            bank_id=self.bank_id,
            content=content
        )

    async def close(self):
        await self.client.aclose()
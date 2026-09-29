import json
import os
from pathlib import Path
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "cyberguard")
OUTPUT_FILE = Path(os.getenv("CYBERGUARD_OUTPUT", "cyberguard_retrieved_context_output.json"))

if not API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

# First learning-loop test:
# Use the first generated context bundle (ALT-2026-9100 is the first alert)
# and retain a real analyst outcome as Hindsight experience.
def main():
    bundles = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    if not bundles:
        raise RuntimeError("Retrieved context output is empty.")

    bundle = bundles[0]

    incident_id = "ALT-2026-9100"
    resolution = bundle["resolution_matches"][0]["resolution"]
    root_cause = bundle["root_cause_matches"][0]["root_cause"]

    feedback = {
        "investigation_id": "INV-CG-9100-DEMO",
        "incident_id": incident_id,
        "incident_type": "Sensitive Data Leakage",
        "selected_action": resolution,
        "outcome": "SUCCESS",
        "root_cause_confirmed": root_cause,
        "analyst_notes": (
            "Analyst confirmed that the response contained the exposed data, "
            "revoked exposed secrets, and tightened data controls successfully."
        ),
        "analyst_id": "ANALYST-DEMO-001",
    }

    content = f"""
CyberGuard analyst experience record.

Investigation: {feedback["investigation_id"]}
Incident: {feedback["incident_id"]}
Incident type: {feedback["incident_type"]}

An SOC analyst selected this response:
{feedback["selected_action"]}

Confirmed root cause:
{feedback["root_cause_confirmed"]}

Outcome: {feedback["outcome"]}

Analyst notes:
{feedback["analyst_notes"]}

This is an analyst experience from a completed CyberGuard investigation.
The response was successful and should be considered evidence for future
similar incidents.
"""

    client = Hindsight(base_url=BASE_URL, api_key=API_KEY)

    try:
        print("1. Retaining analyst feedback as a new Hindsight memory...")
        retain_result = client.retain(
            bank_id=BANK_ID,
            content=content,
            context="CyberGuard analyst feedback / completed incident experience",
            document_id=feedback["investigation_id"],
            metadata={
                "source": "cyberguard_segment5",
                "incident_id": incident_id,
                "outcome": "SUCCESS",
                "memory_role": "analyst_experience",
            },
            retain_async=False,
        )
        print("   Retain completed.")
        print(f"   Result: {retain_result}")

        print("\n2. Recalling experience memories for this incident type...")
        recall_result = client.recall(
            bank_id=BANK_ID,
            query=(
                "CyberGuard Sensitive Data Leakage analyst experience, "
                "successful response, analyst feedback, and lessons learned"
            ),
            types=["experience"],
            max_tokens=4096,
            budget="mid",
        )

        print(f"   Found {len(recall_result.results)} experience result(s).")
        for i, item in enumerate(recall_result.results[:10], 1):
            print(f"\n   EXPERIENCE {i}")
            print(f"   type: {item.type}")
            print(f"   text: {item.text}")

        print("\n3. Running Hindsight reflect() over the learned experience...")
        reflect_result = client.reflect(
            bank_id=BANK_ID,
            query=(
                "For a new Sensitive Data Leakage incident, what response "
                "lessons can be learned from previous successful CyberGuard "
                "analyst experiences? Identify the relevant successful "
                "experience and explain how it should inform a future investigation."
            ),
            budget="mid",
            max_tokens=4096,
            include_facts=True,
        )

        print("\n   REFLECT RESPONSE")
        print(reflect_result.text)

        print("\n   REFLECT SOURCES")
        if reflect_result.based_on and reflect_result.based_on.memories:
            for i, memory in enumerate(reflect_result.based_on.memories, 1):
                print(
                    f"   {i}. [{memory.type}] "
                    f"{memory.text}"
                )
        else:
            print("   No based_on memories returned.")

        print("\nLearning-loop test completed.")

    finally:
        client.close()


if __name__ == "__main__":
    main()

import json
import asyncio
from datetime import datetime, timezone

from dotenv import load_dotenv

from backend.services.hindsight_service import MemoryRetriever


INPUT_FILE = "backend/data/alerts.json"
OUTPUT_FILE = "backend/data/RetrievedContextBundle.json"


async def main():

    load_dotenv()

    print("=" * 70)
    print("CYBERGUARD - SEGMENT 2")
    print("HINDSIGHT MULTI-MEMORY PARALLEL RETRIEVER")
    print("=" * 70)

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            incidents = json.load(f)

    except FileNotFoundError:
        print("ERROR: Input file not found:", INPUT_FILE)
        return

    except json.JSONDecodeError as e:
        print("ERROR: alerts.json contains invalid JSON.")
        print(e)
        return

    if not isinstance(incidents, list):
        print("ERROR: alerts.json must contain a JSON list of incidents.")
        return

    print(f"Incidents loaded : {len(incidents)}")

    invalid_incidents = []

    for index, incident in enumerate(incidents):

        if not isinstance(incident, dict):
            invalid_incidents.append(index)

        elif "incident_id" not in incident:
            invalid_incidents.append(index)

    if invalid_incidents:

        print(
            f"ERROR: {len(invalid_incidents)} incident(s) "
            "do not contain 'incident_id'."
        )

        print(
            f"Invalid positions: {invalid_incidents[:10]}"
        )

        return

    try:
        retriever = MemoryRetriever()

    except KeyError as e:

        print("ERROR: Missing environment variable:", e)
        print("Check your .env file.")
        return

    try:

        print()
        print("Starting Hindsight retrieval...")
        print("Each incident will use 4 parallel memory queries.")
        print("Maximum concurrent incidents: 5")
        print()

        results = await retriever.retrieve_batch(incidents)

        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source": "Hindsight",
            "incidents_processed": len(incidents),
            "results": results
        }

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                indent=2,
                ensure_ascii=False
            )

        print("=" * 70)
        print("SEGMENT 2 COMPLETED SUCCESSFULLY")
        print("=" * 70)

        print(f"Incidents processed : {len(incidents)}")
        print(f"Output file         : {OUTPUT_FILE}")

        print()
        print("Retrieved context contains:")
        print("  - Incident matches")
        print("  - Resolution matches")
        print("  - Root-cause matches")
        print("  - Playbook matches")

        print()
        print("Ready for Segment 3: ContextSynthesizer.")

    except Exception as e:

        print("=" * 70)
        print("SEGMENT 2 FAILED")
        print("=" * 70)

        print(f"Error type : {type(e).__name__}")
        print(f"Error      : {e}")

        print()
        print("No new output was generated from this failed run.")

    finally:

        await retriever.close()


if __name__ == "__main__":
    asyncio.run(main())
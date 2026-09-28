import json
from datetime import datetime, timezone

from backend.services.context_synthesizer import (
    ContextSynthesizer,
    load_retrieved_context,
    save_synthesized_context
)


INPUT_FILE = "backend/data/RetrievedContextBundle.json"
OUTPUT_FILE = "backend/data/SynthesizedContext.json"


def main():

    print("=" * 70)
    print("CYBERGUARD - SEGMENT 3")
    print("CONTEXT SYNTHESIZER")
    print("=" * 70)

    try:
        data = load_retrieved_context(INPUT_FILE)

    except FileNotFoundError:
        print()
        print("ERROR: RetrievedContextBundle.json was not found.")
        print(f"Expected file: {INPUT_FILE}")
        return

    except json.JSONDecodeError as e:
        print()
        print("ERROR: RetrievedContextBundle.json contains invalid JSON.")
        print(e)
        return

    results = data.get("results", [])

    if not isinstance(results, list):
        print()
        print("ERROR: 'results' must be a JSON list.")
        return

    print(f"Retrieved incidents : {len(results)}")

    synthesizer = ContextSynthesizer()

    print()
    print("Synthesizing retrieved memory context...")

    synthesized = synthesizer.synthesize_batch(results)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Hindsight",
        "source_file": INPUT_FILE,
        "incidents_processed": len(synthesized),
        "results": synthesized
    }

    save_synthesized_context(
        OUTPUT_FILE,
        output
    )

    print()
    print("=" * 70)
    print("SEGMENT 3 COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(f"Incidents processed : {len(synthesized)}")
    print(f"Output file         : {OUTPUT_FILE}")

    print()
    print("Synthesized context contains:")
    print("  - Historical incident evidence")
    print("  - Historical resolution evidence")
    print("  - Historical root-cause evidence")
    print("  - Relevant playbook evidence")

    print()
    print("Ready for the next CyberGuard processing stage.")


if __name__ == "__main__":
    main()
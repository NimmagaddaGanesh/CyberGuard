from datetime import datetime, timezone

from backend.services.incident_analyzer import (
    IncidentAnalyzer,
    load_json,
    save_json
)


INCIDENT_FILE = "backend/data/alerts.json"

CONTEXT_FILE = "backend/data/SynthesizedContext.json"

OUTPUT_FILE = "backend/data/IncidentAnalysis.json"


def main():

    print("=" * 70)
    print("CYBERGUARD - SEGMENT 4")
    print("INCIDENT ANALYZER")
    print("=" * 70)

    # ---------------------------------------------------------
    # Load original incidents
    # ---------------------------------------------------------

    try:

        incidents = load_json(
            INCIDENT_FILE
        )

    except FileNotFoundError:

        print()
        print("ERROR: alerts.json was not found.")
        print(f"Expected file: {INCIDENT_FILE}")
        return

    # ---------------------------------------------------------
    # Load synthesized context
    # ---------------------------------------------------------

    try:

        context_data = load_json(
            CONTEXT_FILE
        )

    except FileNotFoundError:

        print()
        print(
            "ERROR: SynthesizedContext.json was not found."
        )

        print(
            f"Expected file: {CONTEXT_FILE}"
        )

        return

    incidents = incidents if isinstance(
        incidents,
        list
    ) else []

    synthesized_results = context_data.get(
        "results",
        []
    )

    print(
        f"Original incidents  : {len(incidents)}"
    )

    print(
        f"Synthesized contexts: {len(synthesized_results)}"
    )

    # ---------------------------------------------------------
    # Analyze incidents
    # ---------------------------------------------------------

    analyzer = IncidentAnalyzer()

    print()
    print(
        "Combining incident data with synthesized evidence..."
    )

    analyses = analyzer.analyze_batch(
        incidents,
        synthesized_results
    )

    # ---------------------------------------------------------
    # Create output
    # ---------------------------------------------------------

    output = {

        "generated_at":
            datetime.now(timezone.utc).isoformat(),

        "source": "CyberGuard",

        "source_files": [
            INCIDENT_FILE,
            CONTEXT_FILE
        ],

        "incidents_processed":
            len(analyses),

        "results":
            analyses
    }

    save_json(
        OUTPUT_FILE,
        output
    )

    # ---------------------------------------------------------
    # Completion
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("SEGMENT 4 COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(
        f"Incidents processed : {len(analyses)}"
    )

    print(
        f"Output file         : {OUTPUT_FILE}"
    )

    print()
    print("Analysis contains:")

    print(
        "  - Incident profile"
    )

    print(
        "  - Current root cause"
    )

    print(
        "  - Recommended playbook"
    )

    print(
        "  - Previously tried actions"
    )

    print(
        "  - Historical incident evidence"
    )

    print(
        "  - Historical resolution evidence"
    )

    print(
        "  - Historical root-cause evidence"
    )

    print(
        "  - Relevant playbook evidence"
    )


if __name__ == "__main__":
    main()
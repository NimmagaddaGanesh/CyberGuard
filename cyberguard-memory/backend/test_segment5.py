import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from backend.services.ai_response_generator import (
    AIResponseGenerator,
    load_json,
    save_json
)


INPUT_FILE = "backend/data/test_IncidentAnalysis.json"

OUTPUT_FILE = "backend/data/IncidentResponse.json"


def main():

    load_dotenv()

    print("=" * 70)
    print("CYBERGUARD - SEGMENT 5")
    print("AI INCIDENT RESPONSE GENERATOR")
    print("=" * 70)

    # ---------------------------------------------------------
    # Check API key
    # ---------------------------------------------------------

    if not os.getenv("OPENAI_API_KEY"):

        print()
        print("ERROR: OPENAI_API_KEY is not configured.")
        return

    # ---------------------------------------------------------
    # Load Segment 4 output
    # ---------------------------------------------------------

    try:

        data = load_json(
            INPUT_FILE
        )

    except FileNotFoundError:

        print()
        print(
            "ERROR: IncidentAnalysis.json was not found."
        )

        print(
            f"Expected file: {INPUT_FILE}"
        )

        return

    analyses = data.get(
        "results",
        []
    )

    if not isinstance(analyses, list):

        print()
        print("ERROR: 'results' must be a JSON list.")
        return

    print(
        f"Incidents loaded : {len(analyses)}"
    )

    # ---------------------------------------------------------
    # Initialize AI generator
    # ---------------------------------------------------------

    try:

        generator = AIResponseGenerator()

    except Exception as e:

        print()
        print(
            "ERROR: Could not initialize OpenAI client."
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        return

    # ---------------------------------------------------------
    # Generate AI responses
    # ---------------------------------------------------------

    print()
    print(
        "Generating AI incident-response recommendations..."
    )

    responses = generator.generate_batch(
        analyses
    )

    # ---------------------------------------------------------
    # Save output
    # ---------------------------------------------------------

    output = {

        "generated_at":
            datetime.now(timezone.utc).isoformat(),

        "source":
            "CyberGuard + OpenAI",

        "source_file":
            INPUT_FILE,

        "incidents_processed":
            len(responses),

        "results":
            responses
    }

    save_json(
        OUTPUT_FILE,
        output
    )

    # ---------------------------------------------------------
    # Completion
    # ---------------------------------------------------------

    successful = sum(
        1
        for item in responses
        if "error" not in item
    )

    failed = len(responses) - successful

    print()
    print("=" * 70)
    print("SEGMENT 5 COMPLETED")
    print("=" * 70)

    print(
        f"Incidents processed : {len(responses)}"
    )

    print(
        f"Successful responses : {successful}"
    )

    print(
        f"Failed responses     : {failed}"
    )

    print(
        f"Output file          : {OUTPUT_FILE}"
    )

    print()

    if failed == 0:

        print(
            "All incidents received AI-generated responses."
        )

    else:

        print(
            "Some incidents failed. "
            "Check IncidentResponse.json for error details."
        )


if __name__ == "__main__":
    main()
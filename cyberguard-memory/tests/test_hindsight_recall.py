from backend.services.hindsight_service import HindsightService


def main():

    print("=" * 60)
    print("CYBERGUARD SEGMENT 2 TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # Example IncidentAlertJSON
    # ---------------------------------------------------------

    incident = {
        "incident_id": "INC-TEST-002",
        "incident_type": "Brute Force Attack",
        "category": "Cybersecurity",
        "severity": "High",
        "affected_system": "VPN Gateway",
        "description": (
            "Repeated failed login attempts from "
            "multiple IP addresses."
        ),
        "symptoms": [
            "Failed logins",
            "Authentication errors"
        ],
        "indicators_of_compromise": [
            "203.0.113.45"
        ],
        "analyst_id": "SOC-01"
    }

    print("\nIncident:")
    print(incident)

    # ---------------------------------------------------------
    # Create Hindsight service
    # ---------------------------------------------------------

    service = HindsightService()

    print("\nRunning four Hindsight recall queries...")

    # ---------------------------------------------------------
    # Retrieve context
    # ---------------------------------------------------------

    context_bundle = service.retrieve_context(
        incident
    )

    # ---------------------------------------------------------
    # Print result
    # ---------------------------------------------------------

    print("\nRetrieved Context Bundle:")
    print("=" * 60)

    import json

    print(
        json.dumps(
            context_bundle,
            indent=2,
            ensure_ascii=False
        )
    )

    # ---------------------------------------------------------
    # Save JSON
    # ---------------------------------------------------------

    service.save_context_json(
        context_bundle
    )

    service.close()

    print("\n" + "=" * 60)
    print("SEGMENT 2 TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
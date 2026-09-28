import os
from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


def main():
    print("=" * 60)
    print("HINDSIGHT PERSISTENCE TEST")
    print("=" * 60)

    base_url = os.environ["HINDSIGHT_BASE_URL"]
    api_key = os.environ["HINDSIGHT_API_KEY"]
    bank_id = os.environ["HINDSIGHT_BANK_ID"]

    print("\nBank:", bank_id)

    client = Hindsight(
        base_url=base_url,
        api_key=api_key
    )

    print("\n[1] Calling RECALL only...")
    print("No RETAIN operation will be performed.")

    query = (
        "Recall MEMORY TEST ALPHA 84721. "
        "Find incident RECALL-TEST-84721. "
        "What system was affected, what was the successful "
        "resolution, and what lesson did the analyst learn?"
    )

    result = client.recall(
        bank_id=bank_id,
        query=query,
        max_tokens=2000,
        budget="mid"
    )

    results = getattr(result, "results", [])

    print(f"\n[2] Results found: {len(results)}")

    found_test_memory = False

    for i, item in enumerate(results, 1):
        content = getattr(item, "text", str(item))

        print(f"\n--- Memory {i} ---")
        print("Type:", getattr(item, "type", "Unknown"))
        print("Content:", content)

        if (
            "RECALL-TEST-84721" in content
            or "Orion Database Server" in content
            or "BlueMoon backup" in content
        ):
            found_test_memory = True

    print("\n" + "=" * 60)

    if found_test_memory:
        print("SUCCESS: Persisted test memory was recalled!")
        print("Hindsight Cloud persistence is confirmed.")
    else:
        print("WARNING: Test memory was not found.")

    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()


def main():
    print("=" * 60)
    print("HINDSIGHT UNIQUE MEMORY TEST")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load environment variables
    # ---------------------------------------------------------
    print("\n[1] Checking environment variables...")

    base_url = os.environ["HINDSIGHT_BASE_URL"]
    api_key = os.environ["HINDSIGHT_API_KEY"]
    bank_id = os.environ["HINDSIGHT_BANK_ID"]

    print("HINDSIGHT_BASE_URL :", base_url)
    print("HINDSIGHT_BANK_ID  :", bank_id)
    print("HINDSIGHT_API_KEY  : Loaded")

    # ---------------------------------------------------------
    # 2. Create Hindsight client
    # ---------------------------------------------------------
    print("\n[2] Creating Hindsight client...")

    client = Hindsight(
        base_url=base_url,
        api_key=api_key
    )

    print("Client created successfully.")

    # ---------------------------------------------------------
    # 3. Retain a UNIQUE test memory
    # ---------------------------------------------------------
    print("\n[3] Testing RETAIN...")

    test_memory = (
        "MEMORY TEST ALPHA 84721. "
        "Incident ID: RECALL-TEST-84721. "
        "A fictional ransomware incident affected the "
        "Orion Database Server. "
        "The successful resolution was to isolate the server "
        "and restore it from the BlueMoon backup. "
        "The analyst learned that database isolation should "
        "happen immediately when ransomware encryption is detected."
    )

    retain_result = client.retain(
        bank_id=bank_id,
        content=test_memory,
        context="CyberGuard unique memory persistence test",
        metadata={
            "memory_type": "test",
            "incident_id": "RECALL-TEST-84721",
            "test": "true"
        }
    )

    print("RETAIN successful!")
    print("Retain response:")
    print(retain_result)

    # ---------------------------------------------------------
    # 4. Recall the SAME unique memory
    # ---------------------------------------------------------
    print("\n[4] Testing RECALL...")

    query = (
        "Recall MEMORY TEST ALPHA 84721. "
        "What happened in incident RECALL-TEST-84721? "
        "What system was affected, what was the successful "
        "resolution, and what lesson did the analyst learn?"
    )

    recall_result = client.recall(
        bank_id=bank_id,
        query=query,
        max_tokens=2000,
        budget="mid"
    )

    print("\nRECALL response:")
    print(recall_result)

    # ---------------------------------------------------------
    # 5. Display recalled memories
    # ---------------------------------------------------------
    print("\n[5] Extracting recalled memories...")

    results = getattr(recall_result, "results", [])

    print(f"\nSUCCESS: {len(results)} memory/result(s) recalled.")

    for i, item in enumerate(results, 1):
        print(f"\n--- Memory {i} ---")
        print("Type:", getattr(item, "type", "Unknown"))
        print("Content:", getattr(item, "text", str(item)))

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
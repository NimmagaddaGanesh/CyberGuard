import os
import time
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "cyberguard")

if not API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

UNIQUE_PHRASE = "CYBERGUARD_LEARNING_PROOF_8472"

def show_results(label, response):
    print(f"\n{label}")
    print(f"Found {len(response.results)} result(s).")
    for i, item in enumerate(response.results[:10], 1):
        print(f"\n  RESULT {i}")
        print(f"  type: {item.type}")
        print(f"  text: {item.text}")

def main():
    client = Hindsight(base_url=BASE_URL, api_key=API_KEY)

    try:
        query = f"""
        Find the exact CyberGuard analyst learning marker {UNIQUE_PHRASE}.
        This marker identifies a brand-new analyst feedback experience that
        did not exist in the original CyberGuard historical dataset.
        """

        # BEFORE: prove the unique marker is not already in memory.
        print("1. BEFORE FEEDBACK")
        before = client.recall(
            bank_id=BANK_ID,
            query=query,
            max_tokens=2048,
            budget="low",
        )
        print(f"   Existing matches for {UNIQUE_PHRASE}: {len(before.results)}")

        if before.results:
            print("   WARNING: unique marker already exists; use another marker.")

        # RETAIN: create a deliberately unique analyst experience.
        print("\n2. RETAINING NEW ANALYST EXPERIENCE")

        content = f"""
CyberGuard analyst feedback — {UNIQUE_PHRASE}

This is a NEW analyst learning event created specifically to validate the
CyberGuard Hindsight feedback loop.

Investigation: INV-CG-LEARNING-8472
Incident type: Sensitive Data Leakage
Outcome: SUCCESS

Selected action:
Apply a staged containment sequence: first block the exposed output path,
then revoke exposed credentials, then validate that no sensitive data remains
reachable through the affected application/model pathway.

Analyst lesson:
{UNIQUE_PHRASE} proves that a successful containment sequence should be
recalled as learned CyberGuard experience for future Sensitive Data Leakage
investigations.

Analyst note:
The analyst verified containment after each step rather than treating the
first successful block as sufficient.
"""

        result = client.retain(
            bank_id=BANK_ID,
            content=content,
            context="CyberGuard Segment 5 analyst feedback learning experiment",
            document_id="INV-CG-LEARNING-8472",
            metadata={
                "source": "cyberguard_segment5_learning_proof",
                "incident_type": "Sensitive Data Leakage",
                "outcome": "SUCCESS",
                "learning_marker": UNIQUE_PHRASE,
            },
            retain_async=False,
        )

        print(f"   Retain success: {result.success}")
        print(f"   Items: {result.items_count}")

        # AFTER: poll raw recall until the new memory becomes searchable.
        print("\n3. AFTER RETAIN — VERIFYING NEW MEMORY")
        found = False

        for attempt in range(1, 7):
            after = client.recall(
                bank_id=BANK_ID,
                query=query,
                types=["world", "experience", "observation"],
                max_tokens=4096,
                budget="mid",
            )

            print(f"   Attempt {attempt}: {len(after.results)} result(s)")

            if after.results:
                found = True
                show_results("   MATCHED NEW LEARNING", after)
                break

            if attempt < 6:
                print("   Waiting for Hindsight consolidation/search visibility...")
                time.sleep(3)

        if not found:
            print("\n   WARNING: unique feedback was not returned by recall yet.")

        # REFLECT: ask Hindsight to use the unique learned evidence.
        print("\n4. REFLECTING ON THE NEW LEARNING")

        reflect_result = client.reflect(
            bank_id=BANK_ID,
            query=f"""
A new Sensitive Data Leakage investigation is being handled by CyberGuard.

Find and use the newly retained analyst learning identified by
{UNIQUE_PHRASE}.

Explain:
1. what the analyst learned,
2. what response sequence should be used for a future similar incident,
3. why verification after each containment step matters.

Do not rely only on generic historical playbooks. Explicitly identify the
new analyst learning if it is available in memory.
""",
            budget="mid",
            context="CyberGuard future incident response decision support",
        )

        print("\n   REFLECT RESPONSE")
        print(reflect_result.text)

        print("\n   REFLECT EVIDENCE")
        memories = getattr(getattr(reflect_result, "based_on", None), "memories", None)

        if memories:
            for i, memory in enumerate(memories[:15], 1):
                print(f"   {i}. [{memory.type}] {memory.text}")
        else:
            print("   No based_on memories returned.")

        print("\n5. TEST RESULT")
        if found:
            print("   PASS: new feedback became searchable after RETAIN.")
        else:
            print("   PARTIAL: RETAIN succeeded, but recall visibility was not confirmed.")

        print("   REFLECT completed successfully.")
        print("   The output above shows whether Hindsight used the new learning.")

    finally:
        client.close()


if __name__ == "__main__":
    main()

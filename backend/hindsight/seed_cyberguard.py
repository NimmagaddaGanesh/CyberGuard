import json
import os
from pathlib import Path
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

BASE_URL = os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io")
API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "cyberguard")
RECORDS_FILE = Path(os.getenv("CYBERGUARD_MEMORY_RECORDS", "cyberguard_historical_memory_records.json"))

if not API_KEY:
    raise RuntimeError("HINDSIGHT_API_KEY is missing from .env")

def main():
    records = json.loads(RECORDS_FILE.read_text(encoding="utf-8"))
    client = Hindsight(base_url=BASE_URL, api_key=API_KEY)

    try:
        client.create_bank(bank_id=BANK_ID, name="CyberGuard")
        print(f"Created bank: {BANK_ID}")
    except Exception as exc:
        if "already" not in str(exc).lower() and "409" not in str(exc):
            print(f"Bank creation skipped: {exc}")

    for i, record in enumerate(records, 1):
        client.retain(
            bank_id=BANK_ID,
            content=record["content"],
            context="CyberGuard synthetic historical memory dataset for Segment 2",
            document_id=record["record_id"],
        )
        if i % 25 == 0 or i == len(records):
            print(f"Seeded {i}/{len(records)} records")

    print(f"Done. Seeded {len(records)} records into '{BANK_ID}'.")
    client.close()

if __name__ == "__main__":
    main()

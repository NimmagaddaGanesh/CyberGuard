import os
from dotenv import load_dotenv
load_dotenv()
from hindsight_client import Hindsight

client = Hindsight(base_url=os.environ["HINDSIGHT_BASE_URL"],
                   api_key=os.environ["HINDSIGHT_API_KEY"])
bank = os.environ["HINDSIGHT_BANK_ID"]

r = client.recall(bank_id=bank, query="credential stuffing brute force login attacks")
print("bank:", bank, "| results:", len(r.results))
for x in r.results[:5]:
    print("-", getattr(x, "type", None), "|", x.text[:120])
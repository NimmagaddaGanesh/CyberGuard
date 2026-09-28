import os

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()


class HindsightMemoryService:
    def __init__(self):
        self.bank_id = os.environ["HINDSIGHT_BANK_ID"]

        self.client = Hindsight(
            base_url=os.environ["HINDSIGHT_BASE_URL"],
            api_key=os.environ["HINDSIGHT_API_KEY"]
        )

    def store_memory(
        self,
        content: str,
        memory_type: str,
        incident_id: str
    ):
        return self.client.retain(
            bank_id=self.bank_id,
            content=content,
            context=f"CyberGuard {memory_type} memory",
            metadata={
                "memory_type": memory_type,
                "incident_id": incident_id
            }
        )

    def recall_memories(self, query: str):
        return self.client.recall(
            bank_id=self.bank_id,
            query=query
        )

    def close(self):
        self.client.close()
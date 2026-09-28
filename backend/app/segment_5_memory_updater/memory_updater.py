"""
Segment 5: Analyst Feedback & Memory Update Worker
Receives analyst feedback, updates empirical counts, recalculates rates, and commits to Hindsight.
"""
from typing import Dict, Any
from app.models.schemas import FeedbackSubmission, FeedbackResponse, FeedbackResponseMetrics, HistoricalMatch
from app.segment_2_hindsight_memory.hindsight_client import hindsight_service

class MemoryUpdateWorker:
    @staticmethod
    async def process_feedback(submission: FeedbackSubmission) -> FeedbackResponse:
        """
        Applies analyst feedback, updates memory state, and returns updated metrics.
        """
        updated_data = hindsight_service.update_local_memory(
            resolution_id=submission.resolution_id,
            outcome=submission.feedback_outcome,
            incident_id=submission.incident_id
        )

        metrics = FeedbackResponseMetrics(
            times_used=updated_data["times_used"],
            successful_resolutions=updated_data["successful_resolutions"],
            success_rate=updated_data["success_rate"]
        )

        hist_matches = [
            HistoricalMatch(**m) for m in updated_data.get("historical_matches", [])
        ]

        return FeedbackResponse(
            memory_updated=True,
            metrics=metrics,
            historical_matches=hist_matches,
            received=submission.model_dump()
        )

memory_updater_service = MemoryUpdateWorker()

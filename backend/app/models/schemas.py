from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# --- Segment 1: Ingestion Schemas ---
class AlertInputPayload(BaseModel):
    raw_input: Any = Field(..., description="Raw string log, webhook, or JSON payload")
    source: Optional[str] = Field("RAW_SYSLOG_WEBHOOK", description="Origin source system")

# --- Segment 2: Historical Match Schema ---
class HistoricalMatch(BaseModel):
    incident_id: str
    similarity: float
    resolution: str
    outcome: Optional[str] = "success"

# --- Segment 4: Recommendation Schema ---
class Recommendation(BaseModel):
    resolution_id: str
    resolution: str
    response_domain: Optional[str] = "Identity & Access Defense"
    priority: Optional[str] = "High"
    rationale: Optional[str] = None
    response_steps: Optional[List[str]] = Field(default_factory=list)
    confidence: float
    times_used: int
    successful_resolutions: int
    success_rate: float

# --- Segment 4 -> Segment 6 Output: Investigation Result ---
class InvestigationResult(BaseModel):
    is_cold_start: bool = False
    historical_matches: List[HistoricalMatch]
    recommendation: Recommendation
    source: Optional[str] = "RAW_SYSLOG_WEBHOOK"
    user_input_preview: Optional[str] = ""

# --- Segment 5 & 6: Feedback Schemas ---
class FeedbackSubmission(BaseModel):
    resolution_id: str
    incident_id: str
    feedback_outcome: str  # "success" or "failed"
    root_cause: Optional[str] = None
    notes: Optional[str] = None

class FeedbackResponseMetrics(BaseModel):
    times_used: int
    successful_resolutions: int
    success_rate: float

class FeedbackResponse(BaseModel):
    memory_updated: bool = True
    metrics: FeedbackResponseMetrics
    historical_matches: Optional[List[HistoricalMatch]] = Field(default_factory=list)
    received: Optional[Dict[str, Any]] = None

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    incident_type: str
    severity: str
    affected_system: str
    description: str
    symptoms: list[str] = Field(default_factory=list)
    indicators_of_compromise: list[str] = Field(default_factory=list)
    analyst_id: str


class SimilarMemory(BaseModel):
    memory_type: str | None = None
    content: str


class RecommendationResponse(BaseModel):
    incident_id: str
    root_cause: str
    confidence_score: float
    similar_incidents: list[SimilarMemory]
    recommended_response: list[str]
    recommended_playbook: str | None = None
    lessons_learned: list[str]
    memory_used: bool


class FeedbackRequest(BaseModel):
    incident_id: str
    resolution: list[str]
    resolution_success: bool
    success_score: float | None = None
    analyst_feedback: str | None = None
    lessons_learned: list[str] = Field(default_factory=list)
    analyst_id: str
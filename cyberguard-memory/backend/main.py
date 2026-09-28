import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv()

from backend.schemas import (
    IncidentRequest,
    RecommendationResponse,
    FeedbackRequest
)
from backend.services.hindsight_service import MemoryRetriever
from backend.services.llm_service import LLMService


memory_retriever = MemoryRetriever()
llm_service = LLMService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await memory_retriever.close()


app = FastAPI(
    title="CyberGuard Memory API",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "hindsight": True,
        "llm": True
    }


@app.post(
    "/incident",
    response_model=RecommendationResponse
)
async def analyze_incident(request: IncidentRequest):

    try:
        # Convert request into a dictionary
        incident_data = request.model_dump()

        # Generate a unique incident ID
        generated_id = (
            f"INC-NEW-{uuid.uuid4().hex[:8].upper()}"
        )

        incident_data["incident_id"] = generated_id

        # -------------------------------------------------
        # 1. RECALL historical memories
        # -------------------------------------------------

        recalled = await memory_retriever.retrieve_for_incident(
            incident_data
        )

        incident_matches = recalled.get(
            "incident_matches", []
        )

        resolution_matches = recalled.get(
            "resolution_matches", []
        )

        root_cause_matches = recalled.get(
            "root_cause_matches", []
        )

        playbook_matches = recalled.get(
            "playbook_matches", []
        )

        # Combine all recalled memories
        formatted_memories = (
            incident_matches
            + resolution_matches
            + root_cause_matches
            + playbook_matches
        )

        # -------------------------------------------------
        # 2. SEND memories + incident to LLM
        # -------------------------------------------------

        llm_result = llm_service.generate_recommendation(
            incident=incident_data,
            memories=formatted_memories
        )

        # -------------------------------------------------
        # 3. RETAIN the new incident
        # -------------------------------------------------

        await memory_retriever.store_incident(
            incident_data
        )

        # -------------------------------------------------
        # 4. Return recommendation
        # -------------------------------------------------

        return RecommendationResponse(
            incident_id=generated_id,
            root_cause=llm_result["root_cause"],
            confidence_score=llm_result["confidence_score"],
            similar_incidents=formatted_memories,
            recommended_response=llm_result["recommended_response"],
            recommended_playbook=llm_result.get(
                "recommended_playbook"
            ),
            lessons_learned=llm_result["lessons_learned"],
            memory_used=len(formatted_memories) > 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Incident analysis failed: {str(e)}"
        )


@app.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest
):
    try:
        feedback_data = request.model_dump()

        # Retain resolution, success/failure,
        # analyst feedback and lessons learned
        await memory_retriever.store_outcome(
            feedback_data
        )

        return {
            "status": "success",
            "message": "Feedback stored in Hindsight",
            "incident_id": feedback_data["incident_id"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Feedback storage failed: {str(e)}"
        )
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from owl.models.registry import ModelRegistry
from owl.skills.registry import SkillRegistry
from owl.skills.web_search import WebSearchSkill
from owl.skills.summarizer import SummarizerSkill
from owl.skills.code_execution import CodeExecutionSkill
from owl.skills.document_summarizer import DocumentSummarizerSkill

from workbench.monitoring.prometheus import TASK_REQUEST_COUNT, TASK_LATENCY
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Basic setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OWL-Workbench API",
    description="API gateway for the OWL multi-agent automation platform.",
    version="1.0.0",
)

# Initialize global registries
model_registry = ModelRegistry.instance()
try:
    model_registry = ModelRegistry.from_yaml("config/models_default.yaml")
except Exception as e:
    logger.warning(f"Failed to load default models config: {e}")

skill_registry = SkillRegistry()
skill_registry.register(WebSearchSkill())
skill_registry.register(SummarizerSkill())
skill_registry.register(CodeExecutionSkill())
skill_registry.register(DocumentSummarizerSkill())


class TaskRequest(BaseModel):
    task: str
    skills: list[str] = ["web_search", "summarizer"]
    model_role: str = "planning_agent"


class TaskResponse(BaseModel):
    status: str
    message: str


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/run", response_model=TaskResponse)
def run_task(request: TaskRequest):
    """
    Execute a task using the specified model role and skills.
    In a full implementation, this would enqueue the task to a message broker (RabbitMQ/Celery)
    and execute the agent workflow asynchronously.
    """
    if not model_registry.has_role(request.model_role):
        TASK_REQUEST_COUNT.labels(model_role=request.model_role, status="error").inc()
        raise HTTPException(
            status_code=400,
            detail=f"Model role '{request.model_role}' not configured."
        )

    for skill in request.skills:
        if not skill_registry.has_skill(skill):
            TASK_REQUEST_COUNT.labels(model_role=request.model_role, status="error").inc()
            raise HTTPException(
                status_code=400,
                detail=f"Skill '{skill}' not registered. Available: {list(skill_registry.list_registered().keys())}"
            )

    logger.info(f"Received task: {request.task} (Skills: {request.skills}, Role: {request.model_role})")
    TASK_REQUEST_COUNT.labels(model_role=request.model_role, status="accepted").inc()
    
    # Placeholder for asynchronous execution
    return TaskResponse(
        status="accepted",
        message=f"Task queued with {len(request.skills)} skills using model {request.model_role}."
    )

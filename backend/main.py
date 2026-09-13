"""FastAPI backend for the GitHub Issue Triage Assistant."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml.predict import IssueClassifier
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


class IssueRequest(BaseModel):
    """Incoming GitHub issue data."""

    title: str = Field(min_length=3, max_length=300)
    body: str = Field(default="", max_length=20_000)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Application crashes during startup",
                    "body": (
                        "The application exits unexpectedly when "
                        "the configuration file is missing."
                    ),
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Issue classification returned by the model."""

    label: str
    confidence: float
    probabilities: dict[str, float]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load the model once when the API starts."""
    app.state.classifier = IssueClassifier()
    yield


app = FastAPI(
    title="GitHub Issue Triage API",
    description=(
        "Classifies GitHub issues as bugs, features, "
        "documentation requests, or questions."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    """Serve the frontend application."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Report whether the API and model are ready."""
    return {
        "status": "healthy",
        "model": "issue_classifier",
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_issue(issue: IssueRequest) -> PredictionResponse:
    """Classify a GitHub issue."""
    try:
        result = app.state.classifier.predict(
            title=issue.title,
            body=issue.body,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return PredictionResponse(**result)
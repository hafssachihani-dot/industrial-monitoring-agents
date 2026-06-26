"""API FastAPI + dashboard.

Workflow simulé :

Input télémétrie
    -> Smart Router
        -> Cas normal : MaintenanceAgent
        -> Cas critique : EmergencyAgent
    -> Agent Rapport + Monitoring

Chaque nœud utilise le même correlation_id.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from src.agents.emergency import emergency_agent
from src.agents.maintenance import maintenance_agent
from src.agents.monitoring import monitoring_agent
from src.agents.router import smart_router
from src.agents.state import WorkflowState
from src.utils.logger import sanitize_text, trace_store


app = FastAPI(
    title="Industrial Monitoring Agents",
    description="Mini-projet pédagogique multi-agents pour maintenance industrielle.",
    version="1.0.0",
)

templates = Jinja2Templates(directory="src/templates")


# Stockage mémoire des derniers résultats complets.
# C'est volontairement simple pour l'exercice :
# en vrai, on utiliserait une base de données.
latest_workflow_results: list[dict[str, Any]] = []


class TelemetryInput(BaseModel):
    """Données simulées envoyées par l'atelier."""

    machine_id: str = Field(examples=["MACHINE-01"])
    temperature: float = Field(examples=[92])
    vibration: float = Field(examples=[8.4])
    oil_pressure: float = Field(examples=[3.6])
    rpm: int = Field(examples=[1490])
    operator_note: str | None = Field(default=None)
    correlation_id: str | None = Field(default=None)


class WorkflowResponse(BaseModel):
    """Réponse renvoyée au client."""

    correlation_id: str
    route: Literal["NORMAL", "CRITICAL"]
    quality_score: float
    result: dict[str, Any]
    trace: list[dict[str, Any]]


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    """Affiche un dashboard très simple."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "events": trace_store.all()[-30:],
            "results": latest_workflow_results[-10:],
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Endpoint de disponibilité système."""
    return {"status": "available"}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    """Métriques utilisées par le dashboard ou les tests."""
    events = trace_store.all()
    errors = [event for event in events if event["status"] == "ERROR"]
    avg_latency = 0
    if events:
        avg_latency = round(sum(event["latency_ms"] for event in events) / len(events), 2)

    return {
        "availability": "available",
        "total_events": len(events),
        "api_errors": len(errors),
        "avg_node_latency_ms": avg_latency,
    }


@app.get("/results")
def results() -> dict[str, Any]:
    """Retourne les derniers résultats affichés dans le dashboard."""
    return {"results": latest_workflow_results[-10:]}


@app.post("/telemetry", response_model=WorkflowResponse)
def process_telemetry(payload: TelemetryInput) -> WorkflowResponse:
    """Point d'entrée principal de la simulation."""
    correlation_id = payload.correlation_id or monitoring_agent.new_correlation_id()

    telemetry = payload.model_dump()
    telemetry["operator_note"] = sanitize_text(telemetry.get("operator_note"))
    state: WorkflowState = {
        "correlation_id": correlation_id,
        "telemetry": telemetry,
    }

    with monitoring_agent.measure(correlation_id, "Input", telemetry):
        quality_score = monitoring_agent.quality_score(telemetry)
        state["quality_score"] = quality_score

    with monitoring_agent.measure(correlation_id, "SmartRouter", telemetry):
        decision = smart_router.route(telemetry)
        state["route"] = decision["route"]
        state["reasons"] = decision["reasons"]

    if decision["route"] == "NORMAL":
        with monitoring_agent.measure(correlation_id, "MaintenanceAgent", decision):
            result = maintenance_agent.analyze(telemetry)
            state["result"] = result
    else:
        with monitoring_agent.measure(correlation_id, "EmergencyAgent", decision):
            result = emergency_agent.analyze(telemetry, decision["reasons"])
            state["result"] = result

    with monitoring_agent.measure(correlation_id, "AgentRapportMonitoring"):
        result["monitoring_summary"] = {
            "correlation_id": correlation_id,
            "quality_score": quality_score,
            "route": decision["route"],
        }

    latest_workflow_results.append(
        {
            "correlation_id": correlation_id,
            "machine_id": telemetry["machine_id"],
            "route": decision["route"],
            "quality_score": quality_score,
            "message": result.get("message", ""),
            "llm_advice": result.get("llm_advice", ""),
        }
    )

    return WorkflowResponse(
        correlation_id=correlation_id,
        route=decision["route"],
        quality_score=quality_score,
        result=result,
        trace=trace_store.by_correlation_id(correlation_id),
    )

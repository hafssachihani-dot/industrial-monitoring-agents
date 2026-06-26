"""State partagé du workflow, inspiré du concept LangGraph State.

On n'utilise pas LangGraph ici pour garder le projet simple.
Mais l'idée est la même :
- le workflow possède un état ;
- chaque nœud/agent lit ou ajoute des informations ;
- le même correlation_id suit toute l'exécution.
"""

from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """État commun entre les nœuds du workflow."""

    correlation_id: str
    telemetry: dict[str, Any]
    route: str
    reasons: list[str]
    quality_score: float
    result: dict[str, Any]


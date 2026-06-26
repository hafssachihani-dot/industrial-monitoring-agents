"""Agent Rapport + Monitoring.

Son rôle :
- gérer le correlation_id ;
- mesurer les temps de réponse ;
- tracer les erreurs API ;
- calculer une petite métrique de qualité des données.
"""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from src.utils.logger import TraceEvent, sanitize_text, trace_store


class MonitoringAgent:
    """Agent de supervision utilisé par tous les autres agents."""

    def new_correlation_id(self) -> str:
        """Crée un ID unique pour relier tous les nœuds d'une exécution."""
        return f"corr-{uuid.uuid4().hex[:12]}"

    @contextmanager
    def measure(
        self,
        correlation_id: str,
        node: str,
        data: dict[str, Any] | None = None,
    ) -> Iterator[None]:
        """Mesure la latence d'un nœud et ajoute une trace."""
        start = time.perf_counter()
        try:
            yield
            status = "OK"
            message = f"{node} exécuté avec succès"
        except Exception as exc:
            status = "ERROR"
            message = sanitize_text(str(exc))
            raise
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            trace_store.add(
                TraceEvent(
                    correlation_id=correlation_id,
                    node=node,
                    status=status,
                    latency_ms=latency_ms,
                    message=message,
                    data=data or {},
                )
            )

    def quality_score(self, telemetry: dict[str, Any]) -> float:
        """Score simple : pourcentage des champs importants présents."""
        required = ["machine_id", "temperature", "vibration", "oil_pressure", "rpm"]
        present = sum(1 for field in required if telemetry.get(field) is not None)
        return round(present / len(required), 2)


monitoring_agent = MonitoringAgent()


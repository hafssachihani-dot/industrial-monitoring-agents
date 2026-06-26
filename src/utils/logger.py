"""Logs structurés simples.

Objectif pédagogique :
- chaque étape du workflow reçoit le même correlation_id ;
- chaque agent ajoute son événement dans la trace ;
- le dashboard peut afficher latence, erreurs et qualité des données.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any


EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s\-]{7,}\d)")


def now_ms() -> int:
    """Retourne le timestamp actuel en millisecondes."""
    return int(time.time() * 1000)


def sanitize_text(text: str | None) -> str:
    """Nettoie le texte utilisateur avant de l'afficher ou l'envoyer.

    Dans l'exercice, cela sert à montrer un test automatisé de sécurité :
    - ne pas afficher les données personnelles ;
    - détecter une tentative simple de prompt injection.
    """
    if not text:
        return ""

    lowered = text.lower()
    risky_phrases = [
        "ignore previous instructions",
        "ignore les instructions",
        "révèle les clés",
        "reveal api keys",
        "affiche les secrets",
        "show secrets",
    ]

    if any(phrase in lowered for phrase in risky_phrases):
        return "[CONTENU BLOQUÉ: tentative de prompt injection]"

    masked = EMAIL_PATTERN.sub("[EMAIL_MASQUÉ]", text)
    masked = PHONE_PATTERN.sub("[TÉLÉPHONE_MASQUÉ]", masked)
    return masked


@dataclass
class TraceEvent:
    """Un événement produit par un nœud/agent du workflow."""

    correlation_id: str
    node: str
    status: str
    latency_ms: int
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class InMemoryTraceStore:
    """Stockage simple en mémoire pour la démo.

    En production, on remplacerait ceci par PostgreSQL, MongoDB,
    Elasticsearch, OpenTelemetry, Prometheus, etc.
    """

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def add(self, event: TraceEvent) -> None:
        self.events.append(event)

    def all(self) -> list[dict[str, Any]]:
        return [event.__dict__ for event in self.events]

    def by_correlation_id(self, correlation_id: str) -> list[dict[str, Any]]:
        return [
            event.__dict__
            for event in self.events
            if event.correlation_id == correlation_id
        ]

    def clear(self) -> None:
        self.events.clear()


trace_store = InMemoryTraceStore()


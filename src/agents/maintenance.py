"""Agent de maintenance préventive : route normale."""

from __future__ import annotations

from typing import Any

from src.utils.openrouter_client import openrouter_client


MAINTENANCE_PROMPT = """
Tu es MaintenanceAgent, un agent de maintenance préventive.

Route reçue : NORMAL.
La machine est sous les seuils critiques.

Mission :
- répondre en français ;
- ne pas inventer une urgence ;
- proposer une surveillance simple ;
- proposer une action de maintenance préventive.

Format obligatoire :
Sécurité : une phrase courte.
Diagnostic : une phrase courte.
Solution : une phrase courte.

Contexte machine :
{context}
"""


class MaintenanceAgent:
    """Produit une réponse courte quand la machine est stable."""

    def analyze(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        machine_id = telemetry["machine_id"]
        context = {
            "route": "NORMAL",
            "machine_id": machine_id,
            "telemetry": telemetry,
        }
        prompt = MAINTENANCE_PROMPT.replace("{context}", str(context))
        llm_advice = openrouter_client.generate_short_advice(
            prompt=prompt,
            context=context,
        )

        return {
            "agent": "MaintenanceAgent",
            "severity": "NORMAL",
            "message": f"{machine_id} fonctionne dans les seuils acceptables.",
            "llm_advice": llm_advice,
            "recommendations": [
                "Continuer la surveillance.",
                "Planifier une inspection préventive hebdomadaire.",
                "Vérifier la lubrification au prochain arrêt programmé.",
            ],
        }


maintenance_agent = MaintenanceAgent()

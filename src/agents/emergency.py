"""Agent d'urgence : route critique."""

from __future__ import annotations

from typing import Any

from src.utils.openrouter_client import openrouter_client


EMERGENCY_PROMPT = """
Tu es EmergencyAgent, un agent d'urgence pour la maintenance industrielle.

Route reçue : CRITICAL.
Une ou plusieurs valeurs dépassent les seuils de sécurité.

Mission :
- répondre en français ;
- être direct et exploitable par un technicien ;
- prioriser la sécurité ;
- ne pas afficher de données sensibles ;
- proposer une action immédiate.

Format obligatoire :
Sécurité : une action immédiate.
Diagnostic : la cause probable.
Solution : les vérifications et corrections avant redémarrage.

Contexte machine :
{context}
"""


class EmergencyAgent:
    """Gère sécurité, alerte et rapport incident."""

    def analyze(self, telemetry: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
        machine_id = telemetry["machine_id"]
        context = {
            "route": "CRITICAL",
            "machine_id": machine_id,
            "telemetry": telemetry,
            "reasons": reasons,
        }
        prompt = EMERGENCY_PROMPT.replace("{context}", str(context))
        llm_advice = openrouter_client.generate_short_advice(
            prompt=prompt,
            context=context,
        )

        report = {
            "agent": "EmergencyAgent",
            "severity": "CRITICAL",
            "message": f"Arrêt immédiat recommandé pour {machine_id}.",
            "reasons": reasons,
            "llm_advice": llm_advice,
            "safety_actions": [
                "Arrêter la machine.",
                "Consigner l'équipement.",
                "Sécuriser la zone.",
                "Prévenir le responsable maintenance.",
            ],
            "technical_checks": [
                "Contrôler roulement/palier.",
                "Vérifier l'alignement.",
                "Vérifier lubrification et ventilation.",
            ],
        }

        return report


emergency_agent = EmergencyAgent()

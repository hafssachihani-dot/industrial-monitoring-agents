"""Agent d'urgence : route critique.

Version simple pour débutant :
- l'agent prépare un prompt ;
- il appelle le LLM ;
- il retourne une réponse simple.
"""

from __future__ import annotations

from typing import Any

from src.utils.openrouter_client import openrouter_client
from src.utils.slack import send_slack_alert


EMERGENCY_PROMPT = """
Tu es EmergencyAgent, un agent d'urgence pour la maintenance industrielle.

La machine est en état CRITICAL.

Réponds en français avec ce format :
Sécurité : action immédiate.
Diagnostic : cause probable.
Solution : action à faire avant redémarrage.

Contexte machine :
{context}
"""


class EmergencyAgent:
    """Agent simple pour les cas critiques."""

    def analyze(self, telemetry: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
        """Analyse un cas critique."""

        # 1. On récupère l'identifiant de la machine.
        machine_id = telemetry["machine_id"]

        # 2. On prépare le contexte à envoyer au prompt.
        context = {
            "machine_id": machine_id,
            "route": "CRITICAL",
            "telemetry": telemetry,
            "reasons": reasons,
        }

        # 3. On insère le contexte dans le prompt.
        prompt = EMERGENCY_PROMPT.replace("{context}", str(context))

        # 4. On appelle le LLM.
        answer = openrouter_client.generate_short_advice(
            prompt=prompt,
            context=context,
        )

        # 5. Si Slack est activé, on envoie une alerte.
        slack_result = send_slack_alert(
            f"🚨 Alerte critique - {machine_id}\n"
            f"Raisons: {', '.join(reasons)}\n\n"
            f"{answer}"
        )

        # 6. On retourne une réponse simple pour l'API et le dashboard.
        return {
            "agent": "EmergencyAgent",
            "severity": "CRITICAL",
            "message": f"Arrêt immédiat recommandé pour {machine_id}.",
            "reasons": reasons,
            "llm_advice": answer,
            "slack": slack_result,
        }


emergency_agent = EmergencyAgent()

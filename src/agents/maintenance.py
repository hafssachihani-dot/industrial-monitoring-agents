"""Agent de maintenance préventive : route normale.

Version simple pour débutant :
- l'agent prépare un prompt ;
- il appelle le LLM ;
- il retourne une réponse simple.
"""

from __future__ import annotations

from typing import Any

from src.utils.openrouter_client import openrouter_client


MAINTENANCE_PROMPT = """
Tu es MaintenanceAgent, un agent de maintenance préventive.

La machine est en état NORMAL.

Réponds en français avec ce format :
Sécurité : état de sécurité.
Diagnostic : état de la machine.
Solution : action de maintenance préventive.

Contexte machine :
{context}
"""


class MaintenanceAgent:
    """Agent simple pour les cas normaux."""

    def analyze(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        """Analyse un cas normal."""

        # 1. On récupère l'identifiant de la machine.
        machine_id = telemetry["machine_id"]

        # 2. On prépare le contexte à envoyer au prompt.
        context = {
            "machine_id": machine_id,
            "route": "NORMAL",
            "telemetry": telemetry,
        }

        # 3. On insère le contexte dans le prompt.
        prompt = MAINTENANCE_PROMPT.replace("{context}", str(context))

        # 4. On appelle le LLM.
        answer = openrouter_client.generate_short_advice(
            prompt=prompt,
            context=context,
        )

        # 5. On retourne une réponse simple pour l'API et le dashboard.
        return {
            "agent": "MaintenanceAgent",
            "severity": "NORMAL",
            "message": f"{machine_id} fonctionne dans les seuils acceptables.",
            "llm_advice": answer,
        }


maintenance_agent = MaintenanceAgent()


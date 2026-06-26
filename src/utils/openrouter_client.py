"""Client OpenRouter très simple.

Important :
- la clé API ne doit jamais être écrite directement dans le code ;
- elle doit rester dans un fichier .env local ou dans les variables serveur ;
- le modèle utilisé par défaut est cohere/north-mini-code:free.
"""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv


# Charge automatiquement les variables du fichier .env si le fichier existe.
# Exemple : OPENROUTER_API_KEY, OPENROUTER_ENABLED, OPENROUTER_MODEL.
load_dotenv()


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "cohere/north-mini-code:free"


class OpenRouterClient:
    """Petit wrapper pour appeler un LLM via OpenRouter."""

    def __init__(self) -> None:
        self.reload_settings()

    def reload_settings(self) -> None:
        """Recharge les paramètres depuis .env.

        override=True permet de reprendre une modification récente du fichier .env.
        """
        load_dotenv(override=True)
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.model = os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.enabled = os.getenv("OPENROUTER_ENABLED", "false").lower() == "true"

    def generate_short_advice(self, prompt: str, context: dict[str, Any]) -> str:
        """Génère un conseil court pour le technicien.

        Si OpenRouter n'est pas activé ou si la clé manque, on retourne
        une réponse locale. Comme ça, le projet marche toujours en démo.
        """
        self.reload_settings()

        if not self.enabled or not self.api_key:
            return self._fallback_advice(context)

        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Industrial Monitoring Agents",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.2,
            },
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def chat(self, question: str) -> str:
        """Mini chat pour tester rapidement le LLM depuis le dashboard."""
        self.reload_settings()

        if not self.enabled or not self.api_key:
            return (
                "Mode local MOCK: OpenRouter n'est pas activé. "
                "Pour l'activer, mets OPENROUTER_ENABLED=true dans .env puis redémarre uvicorn."
            )

        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Industrial Monitoring Agents",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Tu es un assistant de maintenance industrielle. "
                            "Réponds en français, court et pratique."
                        ),
                    },
                    {"role": "user", "content": question},
                ],
                "max_tokens": 250,
                "temperature": 0.2,
            },
            timeout=20,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _fallback_advice(self, context: dict[str, Any]) -> str:
        """Réponse locale si l'API n'est pas disponible."""
        route = context.get("route", "UNKNOWN")
        machine_id = context.get("machine_id", "machine inconnue")

        if route == "CRITICAL":
            return (
                f"Sécurité: arrêter immédiatement {machine_id}.\n"
                "Diagnostic: seuil critique détecté sur la télémétrie.\n"
                "Solution: consigner, inspecter palier/lubrification, puis valider avant redémarrage."
            )

        return (
            f"Sécurité: {machine_id} peut rester en fonctionnement surveillé.\n"
            "Diagnostic: paramètres dans les seuils normaux.\n"
            "Solution: continuer la maintenance préventive."
        )


openrouter_client = OpenRouterClient()

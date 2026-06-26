"""Envoi d'alerte Slack.

Cette intégration est volontairement simple :
- elle ne s'active que si SLACK_ALERTS_ENABLED=true ;
- elle utilise SLACK_WEBHOOK_URL depuis les variables d'environnement ;
- si Slack n'est pas configuré, le workflow continue normalement.
"""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv


def send_slack_alert(message: str) -> dict[str, object]:
    """Envoie un message Slack avec Incoming Webhook."""

    load_dotenv(override=True)

    enabled = os.getenv("SLACK_ALERTS_ENABLED", "false").lower() == "true"
    webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")

    if not enabled:
        return {"enabled": False, "sent": False, "reason": "Slack disabled"}

    if not webhook_url:
        return {"enabled": True, "sent": False, "reason": "Missing SLACK_WEBHOOK_URL"}

    response = requests.post(
        webhook_url,
        json={"text": message},
        timeout=10,
    )
    response.raise_for_status()

    return {"enabled": True, "sent": True, "status_code": response.status_code}


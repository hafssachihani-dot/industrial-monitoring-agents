"""Smart Router.

Il décide si la télémétrie correspond à :
- un cas normal : maintenance préventive ;
- un cas critique : urgence et sécurité.
"""

from __future__ import annotations

from typing import Any


class SmartRouter:
    """Routeur métier basé sur des seuils industriels simples."""

    TEMP_CRITICAL = 90
    VIBRATION_CRITICAL = 7
    OIL_PRESSURE_CRITICAL = 2
    RPM_MIN = 1000
    RPM_MAX = 1700

    def route(self, telemetry: dict[str, Any]) -> dict[str, Any]:
        """Retourne NORMAL ou CRITICAL avec les raisons."""
        reasons: list[str] = []

        if telemetry["temperature"] >= self.TEMP_CRITICAL:
            reasons.append("Température critique")

        if telemetry["vibration"] >= self.VIBRATION_CRITICAL:
            reasons.append("Vibration critique")

        if telemetry["oil_pressure"] < self.OIL_PRESSURE_CRITICAL:
            reasons.append("Pression d'huile critique")

        if telemetry["rpm"] < self.RPM_MIN or telemetry["rpm"] > self.RPM_MAX:
            reasons.append("Vitesse moteur hors plage")

        if reasons:
            return {"route": "CRITICAL", "reasons": reasons}

        return {"route": "NORMAL", "reasons": ["Paramètres dans les seuils"]}


smart_router = SmartRouter()

"""Entrée terminal très simple pour créer un problème machine.

Usage :
    1) lancer l'API :
       uvicorn src.main:app --reload

    2) dans un autre terminal :
       python scripts/terminal_problem.py

Exemple d'input :
    MACHINE-01 temperature 92 vibration 8.4 huile 3.6 rpm 1490
"""

from __future__ import annotations

import re
from typing import Any

import requests


API_URL = "http://127.0.0.1:8000/telemetry"


def number_after(label: str, text: str, default: float) -> float:
    """Cherche un nombre après un mot clé.

    Exemple :
        label="temperature"
        text="temperature 92 vibration 8.4"
        -> 92
    """
    # (?:...) groupe les synonymes sans les capturer.
    # Exemple label="huile|oil|pression" :
    # on veut capturer le nombre après un de ces mots, pas le mot lui-même.
    pattern = rf"(?:{label})\s*[:=]?\s*(\d+(?:[\.,]\d+)?)"
    match = re.search(pattern, text, re.IGNORECASE)

    if not match or not match.group(1):
        return default

    return float(match.group(1).replace(",", "."))


def parse_problem(text: str) -> dict[str, Any]:
    """Transforme une phrase simple en télémétrie JSON."""
    machine_match = re.search(r"(MACHINE-\d+)", text, re.IGNORECASE)
    machine_id = machine_match.group(1).upper() if machine_match else "MACHINE-01"

    return {
        "machine_id": machine_id,
        "temperature": number_after("temperature", text, 70),
        "vibration": number_after("vibration", text, 3),
        "oil_pressure": number_after("huile|oil|pression", text, 3.5),
        "rpm": int(number_after("rpm|vitesse", text, 1450)),
        "operator_note": text,
    }


def main() -> None:
    print("Décris le problème machine.")
    print("Exemple : MACHINE-01 temperature 92 vibration 8.4 huile 3.6 rpm 1490")
    print()

    text = input("Problème > ")
    payload = parse_problem(text)

    response = requests.post(API_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    print()
    print("=== Résultat Agent ===")
    print("Correlation ID :", data["correlation_id"])
    print("Route          :", data["route"])
    print("Machine        :", payload["machine_id"])
    print()
    print(data["result"].get("llm_advice", data["result"].get("message", "")))
    print()
    print("Ouvre/actualise le dashboard : http://127.0.0.1:8000")


if __name__ == "__main__":
    main()

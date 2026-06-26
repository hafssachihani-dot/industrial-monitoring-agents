# Runbook — Gestion des incidents

## Démarrer le projet

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Dashboard :

```text
http://127.0.0.1:8000
```

## Tester un cas critique

Envoyer :

```json
{
  "machine_id": "MACHINE-01",
  "temperature": 92,
  "vibration": 8.4,
  "oil_pressure": 3.6,
  "rpm": 1490
}
```

Résultat attendu :

- route `CRITICAL`
- action de sécurité
- même `correlation_id` dans toutes les traces

## Que faire si l'API ou le LLM échoue ?

1. Vérifier que le serveur FastAPI est lancé.
2. Vérifier `OPENROUTER_API_KEY` si le LLM externe est activé.
3. Si OpenRouter n'est pas disponible, le projet retourne une réponse locale de secours.

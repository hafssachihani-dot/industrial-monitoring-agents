# Industrial Monitoring Agents

Mini-projet pédagogique pour le use case :

> Système Intelligent de Surveillance et de Maintenance Industrielle

## Architecture

```text
Atelier / Input télémétrie
        │
        ▼
Smart Router
        │
        ├── Cas normal ───► Maintenance préventive
        │
        └── Cas critique ─► Urgence & sécurité
                            │
                            ▼
                 Agent Rapport + Monitoring
```

## Points importants de l'exercice

- Code simple et commenté.
- Monitoring : latence, erreurs API, disponibilité, qualité des données.
- `correlation_id` identique pour tous les nœuds d'une même exécution.
- Tests automatisés : routage, API, sécurité basique.

## Prompts utilisés par les agents

Les prompts sont directement dans les fichiers agents Python :

```text
src/agents/maintenance.py
src/agents/emergency.py
```

Prompt du cas normal :

```text
MAINTENANCE_PROMPT dans src/agents/maintenance.py
```

Prompt du cas critique :

```text
EMERGENCY_PROMPT dans src/agents/emergency.py
```

Le `SmartRouter` ne dépend pas d'un prompt. Il utilise des seuils métier :

```text
temperature >= 90        -> CRITICAL
vibration >= 7           -> CRITICAL
oil_pressure < 2         -> CRITICAL
rpm < 1000 ou > 1700     -> CRITICAL
sinon                    -> NORMAL
```

Ensuite, selon la route :

```text
NORMAL   -> MaintenanceAgent -> MAINTENANCE_PROMPT
CRITICAL -> EmergencyAgent   -> EMERGENCY_PROMPT
```

Le fichier `src/agents/state.py` contient un `WorkflowState` simple, inspiré de LangGraph State, pour montrer les données partagées entre les nœuds.

## Installation

```bash
cd industrial-monitoring-agents
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'API

```bash
uvicorn src.main:app --reload
```

Ouvrir le dashboard :

```text
http://127.0.0.1:8000
```

## Activer OpenRouter

Par défaut le projet marche sans LLM externe. Pour utiliser OpenRouter :

1. Copier `.env.example` vers `.env`.
2. Modifier :

```env
OPENROUTER_ENABLED=true
OPENROUTER_API_KEY=ta_cle_openrouter
OPENROUTER_MODEL=cohere/north-mini-code:free
```

Le LLM ajoute alors un champ `llm_advice` dans la réponse de l'agent.

Après modification du fichier `.env`, il faut redémarrer :

```bash
uvicorn src.main:app --reload
```

Attention : ne mets jamais ta vraie clé API dans GitHub.

## Tester avec curl

Cas normal :

```bash
curl -X POST http://127.0.0.1:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"machine_id\":\"MACHINE-01\",\"temperature\":68,\"vibration\":3.2,\"oil_pressure\":3.5,\"rpm\":1450}"
```

Cas critique :

```bash
curl -X POST http://127.0.0.1:8000/telemetry ^
  -H "Content-Type: application/json" ^
  -d "{\"machine_id\":\"MACHINE-01\",\"temperature\":92,\"vibration\":8.4,\"oil_pressure\":3.6,\"rpm\":1490}"
```

## Tester depuis le terminal avec une phrase

Lance d'abord l'API :

```bash
uvicorn src.main:app --reload
```

Puis dans un autre terminal :

```bash
python scripts/terminal_problem.py
```

Exemple de phrase :

```text
MACHINE-01 temperature 92 vibration 8.4 huile 3.6 rpm 1490
```

Le résultat s'affiche dans le terminal et aussi dans le dashboard :

```text
http://127.0.0.1:8000
```

Exemple de cas normal :

```text
MACHINE-01 temperature 68 vibration 3.2 huile 3.5 rpm 1450
```

Exemple de cas critique :

```text
MACHINE-01 temperature 92 vibration 8.4 huile 3.6 rpm 1490
```

## Lancer les tests

```bash
pytest -q
```

## Déployer avec Docker

Construire l'image :

```bash
docker build -t industrial-monitoring-agents .
```

Lancer le conteneur avec le fichier `.env` :

```bash
docker run --env-file .env -p 8000:8000 industrial-monitoring-agents
```

Ou avec Docker Compose :

```bash
docker compose up --build
```

Dashboard :

```text
http://127.0.0.1:8000
```

## Note sécurité

Ne mets jamais une vraie clé API dans le code ou GitHub. Utilise `.env`.

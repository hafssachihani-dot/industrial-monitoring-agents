# Agent Card — Industrial Monitoring Agents

## Objectif

Ce projet simule un système intelligent de surveillance et de maintenance industrielle.

## Agents

- SmartRouter : classe les cas en `NORMAL` ou `CRITICAL`.
- MaintenanceAgent : génère une recommandation préventive.
- EmergencyAgent : génère une réponse critique de sécurité et maintenance.
- MonitoringAgent : gère le `correlation_id`, les traces et les métriques.

## Sécurité

- Les notes opérateur sont nettoyées avant affichage.
- Les emails et téléphones sont masqués.
- Les tentatives simples de prompt injection sont bloquées.

## Traçabilité

Chaque exécution possède un `correlation_id` unique. Tous les nœuds d'une même exécution utilisent le même ID.

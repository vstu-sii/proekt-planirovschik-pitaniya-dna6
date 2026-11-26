# Definition of Done (DoD) всех артефактов команды — Lab 2

## Назначение

DoD переводит требования Lab 2 в проверяемые условия: для каждого основного артефакта указаны наличие, количество, путь/ссылка и критерии приёмки.

### Общие критерии

- артефакт существует в согласованном пути;
- артефакт непустой и содержит обязательные разделы;
- артефакт согласован с PRD, Use Cases и связанными материалами;
- обязательные ссылки/пути рабочие;
- нет API-ключей, токенов, паролей и реальных PII;
- результат можно проверить человеком или автоматическим тестом.

## Основные артефакты Lab 2

| ID | Роль | Артефакт | Кол-во | Путь/ссылка | Критерий готовности |
|---|---|---|---:|---|---|
| DEL-01 | Delivery | C4 as-code + aact + архитектурный ADR | 1 пакет | `docs/architecture/`, aact config | Context + Container PlantUML; Product на Context; `aact check` = 0 violations; ADR содержит Decision Cost |
| DEL-02 | Delivery | UI prototype | 1 пакет | согласованный путь UI | ключевые экраны реализованы кодом; скриншоты рядом; Figma/Miro не используются |
| DEL-03 | Delivery | Data schema | 1 пакет | согласованный путь schema | ERD PlantUML + schema + migrations skeleton |
| DEL-04 | Delivery | Compose skeleton v2 | 1 пакет | `compose.yaml` | stubs сервисов, networks, volumes, healthchecks; конфигурация валидна |
| PROD-01 | Product VO | Use Cases + UML | 1 пакет | `docs/use-cases/` | actor, goal, context, steps, result; UML; walkability |
| PROD-02 | Product VO | Roadmap + MVP scope | 1 документ | `docs/` | MVP из UC; non-scope; milestones до Demo Day |
| PROD-03 | Product VO | Glossary v2 | 1 документ | согласованный путь | архитектурные и AI-термины синхронизированы |
| PROD-04 | Product VO | Accepted architecture ADRs | 1 пакет | `docs/adr/` | архитектурные ADR приняты Product; есть Decision Cost |
| AI-01 | AI Engineer | AI pipeline design | 1 документ | `docs/ai-pipeline.md` | PlantUML pipeline; prompts/RAG/agent; quality/logging; context boundaries |
| AI-02 | AI Engineer | Model ADR | 1 документ | `docs/adr/` | выбор из Lab 1 candidates; Decision Cost; degradation plan |
| AI-03 | AI Engineer | Spike notes | 1 пакет | согласованный путь | assumptions; тест 1–2 рисков; честный результат |
| AI-04 | AI Engineer | AI endpoint contract | 1 контракт | OpenAPI path | endpoints; structured outputs; errors |
| QS-01 | Quality & Safety | DoD | 1 документ | `docs/quality/dod.md` | все основные артефакты и machine-checkable criteria |
| QS-02 | Quality & Safety | Golden Dataset | 1 набор | `docs/quality/golden-dataset/` | 30–50 кейсов; схема из `golden-dataset-plan.md`; owner/replenishment |
| QS-03 | Quality & Safety | Test Plan | 1 документ | `docs/quality/test-plan.md` | unit, integration, evals, CI, safety, regression, SLO/SLA |
| QS-04 | Quality & Safety | Threat Model | 1 документ | `docs/quality/threat-model.md` | OWASP LLM Top 10; untrusted inputs; permissions; mitigations; Lab 4 |

> Архитектурный ADR не считается двумя разными файлами: Delivery отвечает за подготовку, Product VO — за принятие.

## Golden Dataset — обязательная проверка

- ровно 30–50 записей; текущая версия: **35**;
- одна JSONL-строка = один пример;
- схема каждого примера соответствует `golden-dataset-plan.md`;
- первые 10 записей сохраняют исходные `GD-0.1-001` … `GD-0.1-010`;
- первые 10 честно помечены как кандидатные по PRD, а не как интервью;
- остальные записи имеют `source_type` `prd_pain` или `edge_case`;
- нет реальных PII, секретов и закрытых данных;
- есть `must_contain`, `must_not_contain`, `constraints`, `safety_level`;
- после появления реальных интервью набор должен быть обновлён по правилам плана.

## Test Plan — обязательная проверка

Должны присутствовать:
- unit tests;
- integration tests;
- Golden Dataset eval;
- CI checks;
- nightly/full regression;
- safety tests;
- SLO/SLA из `success-criteria.md`.

Целевые quality thresholds берутся из Lab 1:
- жёсткие ограничения ≥98%;
- бюджет ≥95%;
- КБЖУ ≥90%;
- полнота меню ≥95%;
- список покупок ≥95%;
- запасы ≥95%;
- leftovers ≥95%;
- quick food ≥90%;
- tone ≥90%;
- critical violations = 0%.

## Threat Model — обязательная проверка

Должны быть:
- untrusted input entry points;
- OWASP LLM01–LLM10;
- model permissions;
- prompt/indirect injection;
- sensitive information disclosure;
- excessive agency;
- output validation;
- обход бюджета/ограничений;
- Lab 4 attack cases;
- применимые требования защиты данных;
- отсутствие секретов и PII.

## Release gate

Lab 2 не считается готовой, если отсутствует обязательный артефакт, Golden Dataset не находится в диапазоне 30–50, есть критическое safety-нарушение, невалидный AI output попадает в бизнес-логику или отсутствует требуемая командная приёмка.

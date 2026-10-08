# Definition of Done (DoD) всех артефактов команды — Lab 2

## 1. Назначение

Этот DoD задаёт проверяемые условия готовности артефактов лабораторной №2 проекта «Планировщик питания».

Для каждого артефакта фиксируются:
- наличие;
- ожидаемое количество;
- ожидаемый путь или способ ссылки;
- обязательное содержимое;
- проверяемый критерий приёмки;
- владелец и, где требуется, подтверждение Product VO.

DoD опирается на PRD и Quality & Safety-артефакты Lab 1. Он не заменяет требования Lab 2, а переводит их в проверяемую форму.

## 2. Общие критерии

| ID | Проверка | Тип | Порог |
|---|---|---|---|
| DOD-01 | Артефакт находится в согласованном пути репозитория | есть/нет | 1/1 |
| DOD-02 | Артефакт не пустой и имеет понятную структуру | есть/нет | 1/1 |
| DOD-03 | Все обязательные разделы/компоненты из задания присутствуют | число | 100% |
| DOD-04 | Артефакт согласован с PRD, Use Cases и связанными артефактами | ссылка | 1/1 |
| DOD-05 | Нет API-ключей, токенов, паролей и реальных персональных данных | есть/нет | 0 нарушений |
| DOD-06 | Артефакт пригоден для проверки человеком или автоматическим тестом | есть/нет | 1/1 |
| DOD-07 | Для связанных артефактов указаны рабочие относительные ссылки/пути | ссылка | 100% обязательных ссылок |

## 3. Основные артефакты Lab 2

> В таблице считается именно артефакт из блока «Сдаёшь». Входящие в него диаграммы, конфигурации и скриншоты считаются обязательными компонентами, но не отдельными артефактами. Архитектурные ADR не дублируются: Delivery отвечает за подготовку, Product VO — за принятие.

| ID | Роль | Артефакт | Кол-во | Ожидаемый путь/ссылка | Что проверяется |
|---|---|---|---:|---|---|
| DEL-01 | Delivery | C4 as-code + aact + архитектурный ADR | 1 пакет | `docs/architecture/`, `aact` config | Context + Container PlantUML, Product на Context, aact check = 0 нарушений, ADR архитектурного решения |
| DEL-02 | Delivery | UI prototype | 1 пакет | согласованный каталог UI | рабочий код ключевых экранов + скриншоты, без Figma/Miro |
| DEL-03 | Delivery | Data schema | 1 пакет | согласованный каталог data/schema | ERD PlantUML + схема БД + skeleton миграций |
| DEL-04 | Delivery | Compose skeleton v2 | 1 файл/пакет | `compose.yaml` | сервисы/заглушки, сети, volumes, healthchecks; конфигурация валидируется |
| PROD-01 | Product VO | Use Cases + UML | 1 пакет | `docs/use-cases/` | actor, goal, context, steps, result; Use-Case UML; walkability |
| PROD-02 | Product VO | Roadmap + MVP scope | 1 документ | `docs/` | MVP выведен из UC, non-scope явно указан, milestones до Demo Day |
| PROD-03 | Product VO | Glossary v2 | 1 документ | `docs/glossary.md` или согласованный путь | архитектурные и AI-термины синхронизированы с командой |
| PROD-04 | Product VO | Accepted architecture ADRs | 1 пакет | `docs/adr/` | ADR относится к архитектуре, есть Decision Cost и статус принятия |
| AI-01 | AI Engineer | AI pipeline design | 1 документ | `docs/ai-pipeline.md` | PlantUML pipeline, prompts/RAG/agent, quality/logging control points, context boundaries |
| AI-02 | AI Engineer | Model ADR | 1 документ | `docs/adr/` | выбор из Lab 1 candidates, Decision Cost, degradation/fallback |
| AI-03 | AI Engineer | Spike notes | 1 пакет | `docs/` или согласованный путь | непроверенные assumptions, тест 1–2 рисков, честный результат |
| AI-04 | AI Engineer | AI endpoint contract | 1 контракт | согласованный путь OpenAPI | endpoints, structured outputs, ошибки и интеграционные границы |
| QS-01 | Quality & Safety | DoD | 1 документ | `docs/quality/dod.md` | все командные артефакты, count/link/check criteria |
| QS-02 | Quality & Safety | Golden Dataset | 1 набор | `docs/quality/golden-dataset/` | 30–50 кейсов, связь с UC, input/reference/context/checks, owner/replenishment |
| QS-03 | Quality & Safety | Test Plan | 1 документ | `docs/quality/test-plan.md` | unit, integration, evals, CI/Lab 3, safety, regression, SLO/SLA |
| QS-04 | Quality & Safety | Threat Model | 1 документ | `docs/quality/threat-model.md` | OWASP LLM Top 10, untrusted inputs, permissions, mitigations, Lab 4 attacks, regulatory line |

## 4. Критерии архитектурного ADR

Архитектурный ADR считается готовым, если:
1. описывает архитектурное решение, а не выбор бизнес-функции;
2. содержит Context/Problem, Decision, Consequences;
3. фиксирует затронутые компоненты и зависимости;
4. содержит `Decision Cost`;
5. имеет статус и дату/версию;
6. принят Product VO;
7. не смешивает архитектурное решение с Model ADR AI Engineer.

## 5. Критерии Golden Dataset

Golden Dataset Lab 2 считается готовым, если:
- количество записей: **30–50**;
- каждая запись имеет уникальный `id`;
- каждая запись связана с Use Case или явно помечена как safety/edge case;
- есть `input`, `reference`, `context`, `checks`, `safety_level`;
- для retrieval-dependent кейсов проверяется переданный контекст, а не только финальный текст;
- есть владелец;
- определён процесс пополнения;
- данные не содержат секретов и реальных PII;
- набор покрывает нормальные, негативные и safety-кейсы.

## 6. Критерии Test Plan

Test Plan считается готовым, если содержит:
- unit tests;
- integration tests;
- evals по Golden Dataset;
- CI-проверки, которые должны запускаться с Lab 3;
- nightly/full eval для полного набора;
- safety/regression проверки;
- проверки SLO/SLA из PRD.

Для AI-ответов числовые ограничения не считаются надёжными только по тексту LLM: стоимость, КБЖУ и критические ограничения должны иметь детерминированную проверку на соответствующем уровне системы.

## 7. Критерии Threat Model

Threat Model считается готовым, если:
- перечислены точки входа недоверенного текста;
- для каждой релевантной угрозы указаны затронутые активы;
- указано, что может и не может делать модель;
- применён OWASP LLM Top 10;
- описаны prompt/indirect injection, leakage, excessive agency и обход критических ограничений;
- есть проверки для Lab 4;
- отдельно отмечены требования к защите данных и применимые regulatory requirements;
- нет секретов и реальных PII.

## 8. Командное согласование

Перед закрытием Lab 2:
- Delivery подтверждает свои 4 артефакта;
- Product VO подтверждает свои 4 артефакта и принимает архитектурные ADR;
- AI Engineer подтверждает свои 4 артефакта;
- Quality & Safety подтверждает свои 4 артефакта;
- связанные артефакты не противоречат друг другу.

Критерий не считается выполненным, если его нельзя однозначно проверить по файлу, ссылке, числу или автоматической проверке.

## 9. Release gate Lab 2

Lab 2 готова к сдаче, если:
- все 16 основных артефактов/пакетов имеют статус ready;
- обязательные подкомпоненты каждого артефакта присутствуют;
- C4 и aact проверены;
- Use Cases и UML связаны с MVP;
- архитектурные ADR приняты;
- AI pipeline, Model ADR, spikes и OpenAPI готовы;
- Golden Dataset содержит 30–50 кейсов;
- Test Plan и Threat Model согласованы;
- нет секретов/реальных PII;
- открытые несоответствия либо исправлены, либо явно зафиксированы как blocker до сдачи.


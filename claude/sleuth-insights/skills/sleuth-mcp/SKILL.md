---
name: sleuth-mcp
description: >-
  Run biopharma and biotech research with the Sleuth tools: create research
  projects, ask natural-language questions, follow long-running runs and
  approval steps, and retrieve datasets, charts, and documents. Use when the
  user mentions Sleuth, or asks for biopharma research such as competitive
  landscapes, pipelines, clinical trials, indications, or deals/M&A while the
  Sleuth tools are connected.
---

# Sleuth MCP

## What Sleuth is

Sleuth is a **biopharma decision-intelligence** platform. Strategy, BD, and CI teams turn strategic questions into evidence-backed answers using:

- A curated industry knowledge base (companies, drugs, indications, trials, deals, patents, publications)
- An AI research engine that produces **datasets** (tables) and **artifacts** (charts, insights, text)
- Engagement via Sleuth Studio (web), the Public API, and this MCP gateway

Research is **asynchronous** — runs often take **minutes** (sometimes longer). Never block forever on one tool call; poll and chain.

## What this MCP server is

A thin hosted gateway over the Sleuth **Public API**. Each tool maps to one upstream REST call. The client's bearer credential (OAuth access token or WorkOS `sk_` API key) is forwarded upstream unchanged. The gateway holds no secrets.

## Auth modes & identity

The credential determines whose projects you see and whether approval gates surface:

| Credential | Runs as | Project namespace | Plan/schema gates |
|------------|---------|-------------------|-------------------|
| **OAuth sign-in** (no key configured) | The signed-in Sleuth user | That user's projects | Follow the user's Studio auto-approve settings — gates **may surface** |
| **User-owned `sk_` key** | The key's owner | That user's projects | Follow the user's Studio auto-approve settings — gates **may surface** |
| **Org `sk_` key** | Shared org service account | Org-shared namespace | **Auto-approved** — gates never surface |

When a gate surfaces, the project status is `awaiting_plan_approval` or `awaiting_schema_approval`. Resume with `send_message` using `action=approve_plan` / `approve_schema`, or `reject_plan` / `reject_schema` with optional `feedback`.

## Typical happy path

```
1. create_project(name)
2. send_message(project_id, message="<research question>")
3. Loop wait_for_update(project_id, timeout_seconds=180)
   until status is complete | failed | cancelled
   (awaiting_clarification / awaiting_plan_approval /
    awaiting_schema_approval — see below)
4. list_datasets / get_dataset (paginate)
5. list_artifacts / get_artifact / get_artifact_svg (visual only)
6. Optional follow-up: send_message with another question on the same project
```

Optional: `upload_document` **before** `send_message` if the question needs an attached file.

## Project lifecycle

Statuses you will see:

| Status | Meaning | Agent action |
|--------|---------|--------------|
| `idle` | Created, no run | `send_message` with a question |
| `processing` | Planning / preparing (`phase` has detail) | `wait_for_update` |
| `executing` | Building data / analysis (`phase` e.g. `row_population`, `analysis`) | `wait_for_update` — can take a long time |
| `awaiting_plan_approval` | Research plan needs sign-off (user-identity runs) | Review plan via `get_project` / `get_messages` → `send_message` with `action=approve_plan` (or `reject_plan` + `feedback`) |
| `awaiting_schema_approval` | Dataset schema needs sign-off (user-identity runs) | Review schema → `send_message` with `action=approve_schema` (or `reject_schema` + `feedback`) |
| `awaiting_clarification` | AI needs a clarifying answer | `get_messages` → `send_message` with the answer |
| `complete` | Ready | Read datasets/artifacts |
| `failed` | Unrecoverable | Report error; start a new project or revise question |
| `cancelled` | User cancelled | Stop or start over |

Terminal / handoff statuses: `complete`, `failed`, `cancelled`. Treat `awaiting_clarification` and the two approval statuses as needing a user/agent reply before continuing. Unless the user delegated approval to you, surface the proposed plan/schema and let them decide.

**Note:** Final success status is `complete` (not `completed`).

## Polling rules

- Prefer **`wait_for_update`** over tight `get_project` loops.
- Budget: default **180s**, hard max **300s** (5 minutes) per call. **Chain** calls for longer runs.
- Respect `retry_after` when present (seconds). During `executing` it is often ~15.
- `wait_for_update` returns `status_changed` and `waited_seconds` plus full project state.
- On `Upstream timeout — retry` / unreachable errors: retry the same poll; do not assume the run failed.

## Writing research messages

- Send the user's question as they asked it. Keep their scope and columns; don't add columns, filters, geographies, or time windows they didn't ask for.
- If more detail would help (geography, time window, inclusion criteria, extra columns), suggest it in your reply and still send the question as asked. The user can add it at plan review or in a follow-up.
- One clear ask per message; use follow-ups on the **same** `project_id` to refine.
- English only for phase-1 Public API.

## Reading results

**Datasets**

- `list_datasets` → `get_dataset` with pagination (`row_offset` / `row_limit`).
- Defaults protect context: `row_limit=50`, `csv` omitted unless `include_csv=true`.
- Full file: `download_dataset_csv` (can be large).
- Datasets are versioned; use `list_dataset_versions` / `version` when needed.

**Artifacts**

- `list_artifacts` then `get_artifact` for payload.
- `get_artifact_svg` only for visual artifacts; non-visual → HTTP 422 (expected).

**Export**

- Prefer paginated dataset/artifact tools first.
- `export_project` is a full dump (heavy; row cap ~10k per dataset upstream).

**Documents**

- Upload ≤10 MB via `upload_document` (base64).
- `get_document` download URLs expire quickly — refetch when needed.

## Control actions

Via `send_message`, provide **exactly one** of `message` or `action`:

| Action | Effect |
|--------|--------|
| `cancel` | Stop an in-progress run |
| `approve_plan` | Resume a run paused at `awaiting_plan_approval` |
| `approve_schema` | Resume a run paused at `awaiting_schema_approval` |
| `reject_plan` | Request plan changes — pair with `feedback` describing what to change |
| `reject_schema` | Request schema changes — pair with `feedback` |

`feedback` is only accepted with the two reject actions.

## Errors to handle

| Signal | Meaning | What to do |
|--------|---------|------------|
| `409` / project busy | Run already active on this project | Wait until terminal/clarification; don't double-send |
| `429` / run limit | Org concurrency exceeded | Wait and retry later |
| `401` | Bad/missing credential | Re-run OAuth sign-in or fix the configured key |
| `403` | Flag / ownership | Credential may lack Public API access or resource ownership |
| `422` on SVG | Non-visual artifact | Use `get_artifact` instead |

## Tool map (quick)

| Goal | Tools |
|------|--------|
| Health | `get_health` |
| Projects | `create_project`, `list_projects`, `get_project`, `update_project`, `delete_project` |
| Run research | `send_message`, `wait_for_update`, `get_messages` |
| Data out | `list_datasets`, `get_dataset`, `list_dataset_versions`, `download_dataset_csv` |
| Charts / insights | `list_artifacts`, `get_artifact`, `get_artifact_svg` |
| Files in | `upload_document`, `list_documents`, `get_document`, `delete_document` |
| Bulk dump | `export_project` |

## Agent checklist

```
- [ ] create_project
- [ ] optional upload_document
- [ ] send_message (research question)
- [ ] wait_for_update until complete / failed / cancelled /
      awaiting_clarification / awaiting_plan_approval / awaiting_schema_approval
- [ ] if clarification: answer via send_message, then resume waiting
- [ ] if plan/schema approval: review, then send_message with
      action=approve_* (or reject_* + feedback), then resume waiting
- [ ] list_datasets → get_dataset (paginate)
- [ ] list_artifacts → get_artifact / get_artifact_svg as needed
- [ ] follow-up messages on same project_id if refining
```

## Don'ts

- Don't assume plan/schema gates will (or won't) surface — it depends on the credential and the user's auto-approve settings. Handle both.
- Don't approve plans/schemas silently if the user asked to review them first.
- Don't call `export_project` first for large results.
- Don't load entire datasets with huge `row_limit` / `include_csv=true` into context.
- Don't spam `send_message` while status is `processing` or `executing` (expect 409).
- Don't treat a single `wait_for_update` timeout as run failure — chain polls.

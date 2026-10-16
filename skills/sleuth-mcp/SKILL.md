---
name: sleuth-mcp
description: >-
  Run biopharma and biotech research with the Sleuth tools: create research
  projects, ask natural-language questions, follow long-running runs and
  approval steps, and retrieve datasets, charts, and documents. On accounts
  that include them, also search Sleuth's research library and look up
  structured company, drug, indication, trial, and deal data. Use when the
  user mentions Sleuth, or asks for biopharma research such as competitive
  landscapes, pipelines, clinical trials, indications, deals/M&A, or
  sell-side and scientific reports while the Sleuth tools are connected.
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

Which tools you see depends on the account. Every account has the project, research, dataset, artifact, and document tools. Some accounts also include the research library and structured data lookups; see **Tools that depend on account access**.

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
- `search_documents(project_id, query, document_ids?, top_k)` (some accounts) searches the text inside a project's uploaded files and returns matching passages; `document_ids` narrows it to specific files, and `top_k` is 1–50. A file uploaded moments ago may return nothing until indexing finishes; try again shortly.

## Tools that depend on account access

These tools appear only when the user's Sleuth account includes the feature:

| Feature | Tools |
|---------|-------|
| Research library | `search_research_documents`, `list_recent_research_documents`, `query_research_document` |
| Research library downloads | `download_restricted_research_document` (needs research library access plus download access) |
| Structured data lookups | `search_companies`, `search_drugs`, `search_indications`, `get_drug_details`, `find_drug_related_items`, `find_drug_deals`, `find_company_related_assets`, `find_indication_related_items`, `get_clinical_trial_by_code`, `search_clinical_trials`, `get_clinical_trial_attributes`, `find_drugs_by_target`, `find_drugs_by_mechanism_of_action`, `find_drugs_by_modality`, `find_drugs_by_therapeutic_area` |
| Search inside uploaded files | `search_documents` |

Tools the account lacks are left out of the tool list, and calling one anyway fails with `Authorization failed for tool '<name>': insufficient permissions`. When the user asks for one of these features and the tool is missing or denied:

- Tell them their Sleuth account doesn't include that feature, and that they can upgrade their plan or ask support@sleuthinsights.com for access.
- Don't retry the call or guess at what it would have returned.
- Where it fits, offer a research run instead (`create_project`, then `send_message`). It draws on the same knowledge base and can often answer the question, though it takes minutes.

## Research library (some accounts)

Search Sleuth's curated document corpora directly. Results come back immediately, without a research run.

- **`search_research_documents(query, namespaces?, top_k)`** covers sell-side research, market intelligence, news and press releases, PubMed and other scientific and clinical literature, presentations and transcripts, filings (SEC, Hong Kong exchange, corporate financials), patents, regulatory documents and guidelines, Chinese sources such as Wanfang and NMPA, and preprints (bioRxiv, medRxiv). Omit `namespaces` to search everything, or pass some to narrow it, for example `["sellside-research"]`, `["pubmed"]`, `["sec-filings"]`, or `["patents"]`. `top_k` defaults to 50; start with 10–20 to save context.
- Each result has a `document_id`, `title`, `namespace`, `publication_date`, the matching `pages`, and a matching passage in `text_content`. Sell-side results name the `broker`. Passages contain HTML markup; strip it when quoting.
- **`list_recent_research_documents(namespace, time_window?, limit)`** lists the newest documents in one namespace, newest first. `time_window` is `day`, `week`, or `month`; omit it for the latest regardless of age. Use it for "what's new" questions.
- **`query_research_document(namespace, document_id, query, top_k)`** returns the passages that answer a question from one sell-side research (`sellside-research`) or market-intelligence (`mkt-intel-exp-inste`) document, using a `document_id` from search or the recent list. Use it for detailed questions about one report.
- **`download_restricted_research_document(namespace, document_id)`** returns a temporary `download_url` for one sell-side or market-intelligence document, valid for `expires_in_seconds` (about an hour). Call it only when the user asks for the file, and fetch a new link after it expires.
- Cite each point with the document title, broker if there is one, publication date, and page. Answer from the returned passages, and quote briefly rather than reproducing long stretches of a report.

## Structured data lookups (some accounts)

Quick factual answers from Sleuth's knowledge base, returned immediately.

1. Resolve names to Sleuth entity IDs first: `search_companies`, `search_drugs` (primary name or synonym), `search_indications`.
2. Pass those IDs to `get_drug_details`, `find_drug_related_items` (mechanisms, modalities, therapeutic areas, trials, indications, or deals; narrow with `relation_type`), `find_drug_deals`, `find_company_related_assets`, or `find_indication_related_items`.
3. Trials: `get_clinical_trial_by_code` for a registry code such as NCT01234567, or `search_clinical_trials` with criteria on `title`, `keywords`, `acronym`, `condition`, or `location`. Criteria combine with AND; a single value can use OR. `get_clinical_trial_attributes` takes trial entity IDs.
4. Browse drugs by attribute: `find_drugs_by_target` (for example PD-1), `find_drugs_by_mechanism_of_action`, `find_drugs_by_modality`, `find_drugs_by_therapeutic_area`. Modality and therapeutic area expect Sleuth's own category names; take them from a `find_drug_related_items` result rather than guessing.

Tools that page take an `offset`; a `next_offset` in the response means more rows exist. One page can hold hundreds of entities, so summarize rather than list everything, and fetch the next page only when the user needs it. If a lookup returns nothing or fails, tell the user rather than guessing, and offer a research run. When the user wants analysis, a curated dataset, or charts, start a research run instead.

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
| `Authorization failed for tool '…': insufficient permissions` | The account doesn't include that feature | Tell the user; suggest upgrading or contacting support@sleuthinsights.com; don't retry |

## Tool map (quick)

| Goal | Tools |
|------|--------|
| Health | `get_health` |
| Projects | `create_project`, `list_projects`, `get_project`, `update_project`, `delete_project` |
| Run research | `send_message`, `wait_for_update`, `get_messages` |
| Data out | `list_datasets`, `get_dataset`, `list_dataset_versions`, `download_dataset_csv` |
| Charts / insights | `list_artifacts`, `get_artifact`, `get_artifact_svg` |
| Files in | `upload_document`, `list_documents`, `get_document`, `delete_document`; `search_documents` (some accounts) |
| Bulk dump | `export_project` |
| Research library (some accounts) | `search_research_documents`, `list_recent_research_documents`, `query_research_document`, `download_restricted_research_document` |
| Structured data (some accounts) | `search_companies`, `search_drugs`, `search_indications`, `get_drug_details`, `find_drug_related_items`, `find_drug_deals`, `find_company_related_assets`, `find_indication_related_items`, `get_clinical_trial_by_code`, `search_clinical_trials`, `get_clinical_trial_attributes`, `find_drugs_by_*` |

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

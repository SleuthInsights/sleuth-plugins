---
name: sleuth-mcp
description: >-
  Run biopharma and biotech research with the Sleuth tools: create research
  projects, ask natural-language questions, follow long-running runs and
  approval steps, and retrieve datasets, charts, and documents. On accounts
  that include them, also search Sleuth's research library, look up
  structured company, drug, indication, trial, and deal data, and build
  downloadable structured-data datasets. Use when the
  user mentions Sleuth, or asks for biopharma research such as competitive
  landscapes, pipelines, clinical trials, indications, deals/M&A, or
  sell-side and scientific reports while the Sleuth tools are connected.
---

# Sleuth MCP

## What Sleuth is

Sleuth is a **biopharma decision-intelligence** platform. Strategy, BD, and CI teams turn strategic questions into evidence-backed answers using:

- A curated industry knowledge base (companies, drugs, indications, trials, deals, patents, publications)
- An AI research engine that produces **datasets** (tables) and **artifacts** (charts, insights, text)
- Available in Sleuth Studio (web), through the Sleuth API, and through this MCP server

Research is **asynchronous** — runs often take **minutes** (sometimes longer). Never block forever on one tool call; poll and chain.

## What this MCP server is

Sleuth hosts this MCP server. Each tool makes one call to the Sleuth API as the signed-in user (or with the configured Sleuth API key). The server stores no credentials.

Which tools you see depends on the account. Every account has the project, research, dataset, artifact, document, and onboarding tools. Some accounts also include the research library, structured data lookups, and the dataset builder; see **Tools that depend on account access**.

## Auth modes & identity

The credential determines whose projects you see and whether approval gates surface:

| Credential | Runs as | Projects | Plan/schema gates |
|------------|---------|----------|-------------------|
| **Sign-in** (no key configured) | The signed-in Sleuth user | That user's projects | Follow the user's Studio auto-approve settings — gates **may surface** |
| **Personal Sleuth API key** | The key's owner | That user's projects | Follow the user's Studio auto-approve settings — gates **may surface** |
| **Organization Sleuth API key** | Shared organization account | The organization's shared projects | **Auto-approved** — gates never surface |

When a gate surfaces, the project status is `awaiting_plan_approval` or `awaiting_schema_approval`. Resume with `send_message` using `action=approve_plan` / `approve_schema`, or `reject_plan` / `reject_schema` with optional `feedback`.

## New users and onboarding

When the user says they're new to Sleuth or asks to get set up, or whenever a tool reports `onboarding_required`, call `get_onboarding_status` and follow the `current_step` and `next_action` it returns:

| `next_action` | What to do |
|---------------|------------|
| `ready` | Carry on with the user's request |
| `choose_access_request_path` | Offer two ways to request access: the Studio form at the returned `studio_url`, or in this conversation. Only if they choose the conversation, collect what `submit_onboarding_access_request` needs |
| `await_approval` | Sleuth reviews each access request. Tell the user an administrator must approve it, and stop; there is nothing to poll |
| `collect_preferences` | Ask the question for the current step and save the answer with the matching tool: `save_onboarding_role`, `save_onboarding_work_style`, `save_onboarding_use_cases`, or `save_onboarding_usage_mode`. When `current_step` is `mcp_setup`, call `complete_mcp_setup` once the user confirms the connection works |
| `continue_in_studio` | Share the exact `studio_url`. Policies, workspace setup, and invitations happen in Studio. Afterward, ask the user to reconnect Sleuth, then call `get_onboarding_status` again |
| `not_eligible` | Tell the user their account can't be set up this way and suggest support@sleuthinsights.com |

- An access request needs the user's name, company, and country, plus a company website for a work email or a LinkedIn profile for a personal email.
- Reuse names the status already returned; ask only for what's missing. Confirm every value with the user before saving it, and never invent answers or option IDs. Use only the question, option, and use-case IDs that `get_onboarding_status` returned.
- After each save, call `get_onboarding_status` again and follow the new `next_action`.
- Users who are already set up can use the other tools directly; don't check onboarding first or walk them through it unless they ask.

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
- Write research messages in English.

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
- `export_project` is a full dump (heavy; datasets are capped at ~10k rows each).

**Documents**

- Upload ≤10 MB via `upload_document` (base64).
- `get_document` download URLs expire quickly — refetch when needed.
- `search_documents(project_id, query, document_ids?, top_k)` (some accounts) searches the text inside a project's uploaded files and returns matching passages; `document_ids` narrows it to specific files, and `top_k` is 1–50. A file uploaded moments ago may return nothing until indexing finishes; try again shortly.

## Tools that depend on account access

These tools appear only when the user's Sleuth account includes the feature:

| Feature | Tools |
|---------|-------|
| Research library | `search_research_documents`, `list_recent_research_documents`, `query_research_document`, `download_research_document` (broker research downloads also need download access) |
| Structured data lookups | `search_companies`, `search_drugs`, `search_indications`, `get_drug_details`, `find_drug_related_items`, `find_drug_deals`, `find_company_related_assets`, `find_indication_related_items`, `get_clinical_trial_by_code`, `search_clinical_trials`, `get_clinical_trial_attributes`, `find_drugs_by_target`, `find_drugs_by_mechanism_of_action`, `find_drugs_by_modality`, `find_drugs_by_therapeutic_area` |
| Dataset builder | `explore_get_filters`, `explore_search_filter_values`, `explore_build_dataset`, `explore_download_dataset` |
| Search inside uploaded files | `search_documents` |

Tools the account lacks are left out of the tool list, and calling one anyway fails with `Authorization failed for tool '<name>': insufficient permissions`. A broker research download without download access fails with HTTP 403 and `Feature is not enabled`. When the user asks for one of these features and the tool is missing or denied:

- Tell them the feature isn't enabled for their Sleuth account, and that they can contact support@sleuthinsights.com for access.
- Don't retry the call or guess at what it would have returned.
- Where it fits, offer a research run instead (`create_project`, then `send_message`). It draws on the same knowledge base and can often answer the question, though it takes minutes.

## Research library (some accounts)

Search Sleuth's curated document corpora directly. Results come back immediately, without a research run.

The library is organized into categories:

| Category | Covers |
|----------|--------|
| `news` | News and press releases |
| `scientific-literature` | Scientific and clinical literature, conference abstracts, and preprints |
| `regulatory` | Regulatory documents and guidelines |
| `company-filings` | Company filings and financial reports |
| `patents` | Patents and related legal documents |
| `broker-research` | Sell-side research and market intelligence |
| `company-presentations` | Company presentations and call transcripts |
| `other-documents` | Other third-party documents |

- **`search_research_documents(query, categories?, top_k)`** searches the library. Omit `categories` to search every category the account can use, or pass some to narrow it, for example `["broker-research"]` or `["scientific-literature", "regulatory"]`. `top_k` is 1–100 and defaults to 50; start with 10–20 to save context.
- Each result has a `document_id`, `category`, `title`, `publication_date`, the matching `pages`, and a matching passage in `text_content`. Broker research results name the `broker`. Results from outside sources, such as PubMed Central articles, include the source `url` and may have no `title`. Passages contain HTML markup; strip it when quoting.
- **`list_recent_research_documents(category, time_window?, limit)`** lists the newest documents in one category, newest first. `time_window` is `day`, `week`, or `month`; omit it for the latest regardless of age. When `title` is empty, `name` holds the file name. Use it for "what's new" questions.
- **`query_research_document(category, document_id, query, top_k)`** returns the passages that answer a question from one `broker-research` document, using a `document_id` from search or the recent list. Other categories don't support it; quote their search passages instead. Use it for detailed questions about one report.
- **`download_research_document(category, document_id, source_url?)`** returns a `download_url` for one document. For a result with a source `url`, pass that `url` as `source_url`. `download_type` is `signed` for a Sleuth-hosted file (the link expires after `expires_in_seconds`, about an hour) or `source` for the publisher's own page (no expiry). Call it only when the user asks for the file, present the link, and don't claim to have opened or read the file. Fetch a new link after one expires.
- Cite each point with the document title, broker if there is one, publication date, and page. Answer from the returned passages, and quote briefly rather than reproducing long stretches of a report.

## Structured data lookups (some accounts)

Quick factual answers from Sleuth's knowledge base, returned immediately.

1. Resolve names to Sleuth entity IDs first: `search_companies`, `search_drugs` (primary name or synonym), `search_indications`.
2. Pass those IDs to `get_drug_details`, `find_drug_related_items` (mechanisms, modalities, therapeutic areas, trials, indications, or deals; narrow with `relation_type`), `find_drug_deals`, `find_company_related_assets`, or `find_indication_related_items`.
3. Trials: `get_clinical_trial_by_code` for a registry code such as NCT01234567, or `search_clinical_trials` with criteria on `title`, `keywords`, `acronym`, `condition`, or `location`. Criteria combine with AND; a single value can use OR. `get_clinical_trial_attributes` takes trial entity IDs.
4. Browse drugs by attribute: `find_drugs_by_target` (for example PD-1), `find_drugs_by_mechanism_of_action`, `find_drugs_by_modality`, `find_drugs_by_therapeutic_area`. Modality and therapeutic area expect Sleuth's own category names; take them from a `find_drug_related_items` result rather than guessing.

Tools that page take an `offset`; a `next_offset` in the response means more rows exist. One page can hold hundreds of entities, so summarize rather than list everything, and fetch the next page only when the user needs it. If a lookup returns nothing or fails, tell the user rather than guessing, and offer a research run. When the user wants analysis, a curated dataset, or charts, start a research run instead.

Relationship results carry a `context` list with a short `description` and a `citation`. Public sources keep their links (PubMed, DOI, patents). Documents from Sleuth's own library are cited as "Sleuth research library"; to find the document itself, search the research library if the account has it.

## Dataset builder (some accounts)

Builds a table straight from Sleuth's knowledge base by filters, without a research run, and saves it to the user's Sleuth account. Use it when the user wants a list or table they can filter and download, such as "every PD-1 drug in Phase 3". For analysis or charts, start a research run instead.

1. Call `explore_get_filters` first. It returns the anchors (what each row is, such as a drug), selectable columns, the filters each anchor supports, fixed allowed values, and row limits.
2. Resolve every free-text term, such as a target, indication, or company, with `explore_search_filter_values(category, query, limit)`. Pass a returned value to the build unchanged. If several values match, ask the user which one they mean. Never invent IDs.
3. Call `explore_build_dataset(anchor, filters, title?, columns?, generate_anyway?, preview_rows?)`. It saves a new dataset and returns the row count, columns, a short preview, a Studio link, and any warning. If the build fails because the selection is over the interactive row cap, offer to narrow the filters, or, if the user agrees, retry with `generate_anyway=true`; that dataset is available only as a download.
4. Show the preview and Studio link, then ask whether the user wants the full dataset. Only if they say yes, call `explore_download_dataset(project_id, dataset_id, format)` with the returned IDs. `csv` (the default) returns a download link that expires after five minutes; `json` returns every row in the conversation, which can be large, so use it only when the user asks for it.

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
| `401` / not signed in | Bad, missing, or expired credential | Ask the user to reconnect Sleuth and sign in again, or fix the configured key |
| `403` | Access or ownership | The account may lack API access, or the project belongs to someone else |
| `403` with `Feature is not enabled` | Broker research download without download access | Tell the user the feature isn't enabled for their account; suggest support@sleuthinsights.com |
| `422` on SVG | Non-visual artifact | Use `get_artifact` instead |
| `onboarding_required` | The user hasn't finished setting up Sleuth | Call `get_onboarding_status` and follow **New users and onboarding** |
| `Authorization failed for tool '…': insufficient permissions` | The account doesn't include that feature | Tell the user the feature isn't enabled for their account; suggest support@sleuthinsights.com; don't retry |

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
| Onboarding | `get_onboarding_status`, `submit_onboarding_access_request`, `save_onboarding_role`, `save_onboarding_work_style`, `save_onboarding_use_cases`, `save_onboarding_usage_mode`, `complete_mcp_setup` |
| Research library (some accounts) | `search_research_documents`, `list_recent_research_documents`, `query_research_document`, `download_research_document` |
| Structured data (some accounts) | `search_companies`, `search_drugs`, `search_indications`, `get_drug_details`, `find_drug_related_items`, `find_drug_deals`, `find_company_related_assets`, `find_indication_related_items`, `get_clinical_trial_by_code`, `search_clinical_trials`, `get_clinical_trial_attributes`, `find_drugs_by_*` |
| Dataset builder (some accounts) | `explore_get_filters`, `explore_search_filter_values`, `explore_build_dataset`, `explore_download_dataset` |

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
- Don't save onboarding answers or submit an access request the user hasn't confirmed.
- Don't download a built dataset, or retry a build with `generate_anyway=true`, without asking.
- Don't suggest upgrading or buying a plan; for missing features, point the user to support@sleuthinsights.com.

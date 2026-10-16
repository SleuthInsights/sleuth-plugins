# Sleuth Insights for Claude

Sleuth Insights is a biopharma decision-intelligence platform. This plugin lets
Claude run Sleuth research for you: it creates research projects, sends your
questions to Sleuth's research engine, follows long-running runs through
clarification and approval steps, and reads back the datasets, charts, and
documents Sleuth produces, with sources. Depending on your Sleuth plan, Claude
can also search Sleuth's research library and look up structured data on
companies, drugs, indications, clinical trials, and deals.

The plugin has two parts:

- **The Sleuth connector**, a remote MCP server hosted by Sleuth Insights at
  mcp.sleuthapi.com. It gives Claude the Sleuth tools.
- **The Sleuth research skill**, which teaches Claude how to use those tools
  well: how to word a research question, how to wait for runs that take
  several minutes, when to stop and ask you to approve a research plan or
  dataset schema, and how to read large datasets a page at a time.

## Requirements

You need a Sleuth Studio account with MCP access, which Sleuth turns on per
organization. If you don't have one, or the connector reports that your
account lacks access, contact support@sleuthinsights.com.

Some features depend on your Sleuth plan:

- **Research library:** search sell-side research, market intelligence,
  scientific and clinical literature, filings, patents, regulatory documents,
  news, and preprints, list the newest documents, and pull the passages that
  answer a question from a single report.
- **Research library downloads:** temporary download links for sell-side and
  market-intelligence reports.
- **Structured data lookups:** companies, drugs, indications, clinical trials,
  deals, and how they relate.
- **Search inside uploaded files:** find passages in documents you've uploaded
  to a project.

Claude only sees the tools your account includes. To add a feature, upgrade
your plan or contact support@sleuthinsights.com.

## Set up

**Claude (web, desktop, mobile) and Cowork.** Add the plugin from the
directory. Then open the plugin's **Connectors** tab, connect **sleuth**, and
sign in with your Sleuth account when the Sleuth sign-in page opens. On Team
and Enterprise plans, an Owner adds the connector for the organization first,
and each member then connects with their own Sleuth account.

**Claude Code.** A plugin you add on claude.ai also appears in Claude Code.
Run `/mcp`, select the **sleuth** server, and complete the browser sign-in.

You stay signed in as yourself: Claude sees only the projects your Sleuth
account can see, and runs follow your Sleuth approval settings.

## Try it

- "Use Sleuth to map the competitive landscape for HER2-directed antibody-drug
  conjugates that are approved or in Phase 3, with sponsor, stage, and the key
  trial for each."
- "Show five of my Sleuth projects and tell me where each one stands."
- "In my Sleuth project on GLP-1 obesity drugs, show the first 20 rows of the
  dataset and summarize which sponsors lead."
- "Attach this target-criteria document to a new Sleuth project, then find
  Phase 2 and later assets that match it."
- "Search Sleuth's research library for sell-side views on HER2-directed ADCs,
  and summarize them with the broker and date for each." (Needs research
  library access.)

Research runs often take several minutes. Claude checks progress for you and
tells you when results are ready, or when Sleuth needs an answer or an
approval before it can continue. Unless you tell Claude otherwise, it shows
you a proposed research plan or dataset schema and waits for your decision.

## What Claude can do with Sleuth

Most Sleuth tools only read data: listing and reading projects, messages,
datasets, artifacts, and documents, waiting for a run to finish, exporting a
project, and, if your plan includes them, searching the research library and
looking up structured data. Depending on your tool permission settings, Claude
can run these without asking each time.

These tools change data in your Sleuth account:

- Create a project, or upload a document to a project (adds new data).
- Send a research message, answer a clarification, approve or reject a plan or
  schema, or cancel a run.
- Rename or delete a project, or delete a document.

Claude asks for your confirmation before it uses the tools that change or
delete existing data.

## Data and privacy

The plugin itself runs no code on your computer. It has no hooks or scripts,
collects no telemetry, and doesn't read your files on its own. It contains
only the research skill (instructions for Claude) and the address of the
Sleuth connector.

When you use the connector, Claude sends the following to Sleuth Insights,
Inc.:

- Your research questions, project names, and replies to clarification or
  approval requests.
- Search terms and questions for the research library and structured data
  lookups, if your plan includes them.
- Documents you explicitly ask Claude to upload to a Sleuth project.
- Your sign-in token, so Sleuth can act as your account.

These go to two domains operated by Sleuth Insights, Inc.:

- mcp.sleuthapi.com, the Sleuth connector, which forwards each request to the
  Sleuth API.
- auth.sleuth.studio, the Sleuth sign-in service, used only when you connect.

Sleuth's research engine runs on Sleuth's own servers and draws on Sleuth's
biopharma knowledge base. Results come back to Claude through the same
connector. Download links for research library reports point to Google Cloud
Storage (storage.googleapis.com) and expire after about an hour; the file is
fetched from there only when you open the link. How Sleuth stores, uses, and
retains this data is covered by the [Sleuth Insights Privacy Policy](https://sleuthinsights.com/privacy-policy)
and the [Terms of Service](https://sleuthinsights.com/terms-of-service).

## Troubleshooting

- **The connector asks you to sign in again.** Sign-in sessions expire.
  Reconnect from the plugin's Connectors tab, or run `/mcp` in Claude Code.
- **"Forbidden" or access errors.** Your Sleuth account may not have API
  access, or the project belongs to someone else. Contact
  support@sleuthinsights.com.
- **Claude says a Sleuth feature isn't available, or reports "insufficient
  permissions".** Your plan doesn't include that feature, such as the research
  library or structured data lookups. Upgrade your plan or contact
  support@sleuthinsights.com.
- **A run seems stuck.** Long runs are normal. Ask Claude to check the
  project's status. If it shows "awaiting plan approval" or "awaiting schema
  approval", Sleuth is waiting for your decision.
- **"Project busy."** A run is already in progress on that project. Wait for
  it to finish, or ask Claude to cancel it.
- **"Run limit reached."** Your organization has hit its limit on concurrent
  runs. Try again once another run finishes.

## Support

- Connector setup guide: https://sleuthinsights.com/mcp-setup
- Help and FAQ: https://sleuthinsights.com/faq
- Email: support@sleuthinsights.com
- Security reports: security@sleuthinsights.com

## License

Copyright 2026 Sleuth Insights, Inc. Use of this plugin is governed by the
Sleuth Insights Terms of Service or your organization's agreement with Sleuth
Insights. See the LICENSE file for details.

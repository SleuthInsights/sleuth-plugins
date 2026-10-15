# Sleuth Insights for ChatGPT

Release source for the ChatGPT plugin: the hosted Sleuth MCP server plus the
Sleuth research skill. The listing name is **Sleuth Insights**, published by
**Sleuth Insights**. This folder prepares the package; it does not host the
server or publish a directory listing.

## Build the package

Python 3.10+ is sufficient; the builder has no third-party dependencies. From
the repository root:

```sh
python3 scripts/sync.py
python3 chatgpt/scripts/build_plugin.py
```

The result is `chatgpt/dist/sleuth-insights-0.1.0.zip`. The builder validates
the source, checks the ZIP's exact contents and integrity, and excludes
repository files from the uploaded plugin. Without a demo recording URL in
`plugin.json`, the result is a development package.

```text
chatgpt/
  sleuth-insights/              # The single directory included in the ZIP
    plugin.json                 # Agent Plugins 1.0 manifest and OpenAI metadata
    mcp.json                    # Production HTTPS endpoint; OAuth, no embedded key
    LICENSE                     # Synced from the repository root
    assets/sleuth-icon.png      # Synced from the repository root
    skills/sleuth-mcp/SKILL.md  # Synced from the repository root
  review/review-scope.txt       # File a review case attaches; linked from plugin.json
  scripts/build_plugin.py       # Validate and build the release ZIP
  schemas/                      # Upstream portable schemas for offline validation
  sources.json                  # Endpoint, branding, and schema provenance
  dist/                         # Generated ZIP; ignored by Git
```

Never edit the synced files here directly. Change the canonical copies at the
repository root and run `python3 scripts/sync.py`; CI fails if the copies
drift.

## How this fits with the server

[sleuth-mcp](https://github.com/SleuthInsights/sleuth-mcp) owns the server,
OAuth flow, tool implementations, and deployment. The plugin only references
`https://mcp.sleuthapi.com/mcp`, so customer traffic goes through the monitored
production server.

## Submission build

Eight review cases for OpenAI's reviewers are embedded in `plugin.json`. One
of them attaches `review/review-scope.txt` through its URL on `main`.
`python3 chatgpt/scripts/build_plugin.py --submission` also requires the demo
recording URL. Passing local checks does not verify OAuth sign-in, the saved
portal version, or review approval.

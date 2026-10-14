# Sleuth Insights plugins

Source for the Sleuth Insights plugins for Claude and ChatGPT. Both plugins
connect to the hosted Sleuth MCP server at `https://mcp.sleuthapi.com/mcp` and
bundle the same Sleuth research skill. Neither contains server code: all
customer traffic goes through the production server, and server changes belong
in [SleuthInsights/sleuth-mcp](https://github.com/SleuthInsights/sleuth-mcp).

| Plugin | Folder | How it ships |
| --- | --- | --- |
| Claude (claude.ai, Cowork, Claude Code) | `claude/sleuth-insights/` | Anthropic's directory reads it from this repository |
| ChatGPT | `chatgpt/` | A ZIP built here and uploaded to OpenAI |

## Layout

```text
skills/sleuth-mcp/SKILL.md      # Canonical skill, shared by both plugins
LICENSE                         # Canonical license, shared by both plugins
assets/sleuth-icon.png          # Canonical icon, shared by both plugins
.claude-plugin/marketplace.json # Lets teams install the Claude plugin from this repo
claude/
  sleuth-insights/              # The Claude plugin folder submitted to Anthropic
  evals/                        # Eval suite with stand-in Sleuth tools (not shipped)
chatgpt/
  sleuth-insights/              # The folder packed into the ChatGPT ZIP
  scripts/build_plugin.py       # Validates and builds the ChatGPT ZIP
scripts/
  sync.py                       # Copies shared files into both plugin folders
  check_claude_plugin.py        # Anthropic's pre-submission checks, run locally
  run_claude_evals.py           # Runs claude/evals against the Claude plugin
```

## Change the skill, license, or icon

Edit the copy at the repository root, then copy it into both plugins:

```sh
python3 scripts/sync.py
```

Commit the root file and both copies together. CI fails if a plugin's copy
differs from the root. The plugins hold real copies rather than links because
Anthropic's directory rejects symbolic links in a plugin folder.

## Run the checks

CI runs these on every push and pull request. To run them locally, from the
repository root:

```sh
python3 scripts/sync.py --check
python3 scripts/check_claude_plugin.py claude/sleuth-insights --strict
claude plugin validate --strict ./claude/sleuth-insights
claude plugin validate --strict .
python3 chatgpt/scripts/build_plugin.py
```

`claude plugin validate` needs Claude Code 2.1.281 or later, which is the first
version that accepts the directory listing fields in `plugin.json`.

## Run the evals

`claude/evals/` checks how Claude behaves with the plugin, each case run once
with the plugin and once without it. The Sleuth tools are stand-ins that
answer from files, so nothing reaches a Sleuth server and no research is
billed. Tools without a stand-in, including every delete tool, aren't offered.
Runs do count against your Claude plan's usage, so CI doesn't run them.

| Case | What it checks |
| --- | --- |
| `dataset-rows` | Reads a page of a dataset; doesn't download the CSV, export the project, or start new research |
| `plan-approval` | Starts a run, then shows the user the proposed plan instead of approving it |
| `project-busy` | On a busy project, doesn't re-send, cancel the run, or invent an answer |
| `unrelated-request` | An unrelated request triggers neither the skill nor a Sleuth tool |

Sign in to Claude Code first (`claude auth login`), then:

```sh
python3 scripts/run_claude_evals.py --judge-model sonnet
```

`claude plugin eval` only reads a suite inside the plugin, so the script runs
against a temporary copy of the plugin with the suite added. It keeps the HTML
report local and writes it to `dist/claude-evals/`. Other options go straight
to `claude plugin eval`, for example `--case plan-approval --runs 1`.

The stand-in tool list, `claude/evals/mocks/sleuth/_tools.json`, is the
production server's `tools/list` with output schemas removed. Refresh it when a
tool's name, description, or inputs change.

## Try the Claude plugin

Each of these uses your working copy or this repository, not the directory
listing.

- **Claude Code:** run `claude --plugin-dir ./claude/sleuth-insights`, then
  `/mcp` to sign in to Sleuth.
- **Claude Code, installed from this repository:** run
  `claude plugin marketplace add SleuthInsights/sleuth-plugins`, then
  `claude plugin install sleuth-insights@sleuth-plugins`. While the repository
  is private, your GitHub account needs read access.
- **claude.ai and Cowork:** build a ZIP and upload it under
  **Customize > Plugins > Add > Upload plugin**, then connect Sleuth from the
  plugin's **Connectors** tab:

  ```sh
  mkdir -p dist
  (cd claude && zip -qr ../dist/sleuth-insights-claude.zip sleuth-insights -x '*.DS_Store')
  ```

## Release

- **Claude:** raise `version` in `claude/sleuth-insights/.claude-plugin/plugin.json`
  and merge to `main`. Once the plugin is listed, the directory picks up each
  new commit on `main`, scans it, and publishes it.
- **ChatGPT:** build the ZIP and upload it, as
  [`chatgpt/README.md`](chatgpt/README.md) describes.

## Permanent choices

Once the Claude plugin is submitted, these can't change without a new listing:

- The plugin name `sleuth-insights`.
- This repository and the folder `claude/sleuth-insights`. Anthropic ties the
  listing to that exact repository and folder.

## License

Proprietary. Use is governed by the Sleuth Insights Terms of Service or your
organization's agreement with Sleuth Insights, Inc. See [LICENSE](LICENSE).

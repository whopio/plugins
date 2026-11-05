# Whop plugins

Official Whop plugin for whatever AI agent you use. Works with Claude Code and Grok Build,
with a ChatGPT and Codex build that is not submitted yet.

## Install

**Claude Code**

```
/plugin marketplace add whopio/plugins
/plugin install whop@whop
```

Restart Claude Code, then run `/whop:whop-connect`.

**Grok Build**

Install `whop` from the built-in marketplace, then run `/whop-connect`. To authorize,
open `/mcps`, select `whop`, and press `i`.

**ChatGPT and Codex**

Not listed yet. Once it is, install Whop from the Plugins directory and connect it when
asked; reconnect later from the plugin's settings. In Codex, `$whop:whop-connect` checks the
connection.

For Claude Code and Grok Build, the first Whop tool call opens a browser for Whop sign-in.

## Supported clients

| Client | Status | Catalog entry |
| --- | --- | --- |
| Claude Code | Shipped (application pending) | `.claude-plugin/marketplace.json` |
| Grok Build | PR pending | [`clients/grok/`](clients/grok/) |
| ChatGPT and Codex | Built, not submitted (needs `https://mcp.whop.com/chatgpt/mcp`) | [`clients/openai/`](clients/openai/), uploaded as a ZIP at platform.openai.com/plugins |

## What the Whop plugin is

| Component | Source | What it does |
| --- | --- | --- |
| MCP config | `shared/mcp.json` (`clients/openai/mcp.json` for ChatGPT) | Points the client at its Whop MCP endpoint (`MCP_URL` in `clients/<client>/client.json`). Claude uses `https://mcp.whop.com/claude/mcp`, which leaves out AI media generation and money-out tools. ChatGPT will use `https://mcp.whop.com/chatgpt/mcp`, which serves AI media but leaves out issuing refunds, one-off charges to customers, payouts and other money movement, identity verification, and credentials; its skill gets a yes before anything that costs money or goes live. You sign in through the browser. |
| `whop` skill | `shared/skills/whop/` | Lists every command group and which tool starts each job, and adds guides for websites, ads, and company formation. |
| `whop-connect` command | `clients/<client>/skills/whop-connect/` | Checks you are signed in, then names the account and what it can reach. Written once per client, because each names its menus differently. |

## Repository layout

```
shared/                          Client-neutral content
  mcp.json                         MCP server config
  plugin.base.json                 Manifest fields common to every client
  skills/                          whop (+ references)
clients/<client>/                Everything that differs per client
  client.json                      Manifest overrides, output paths, {{TOKEN}} values
  skills/                          Client-specific skill files (override shared files by path)
dist/<client>/whop/              AUTO-GENERATED
.claude-plugin/marketplace.json   Claude marketplace, sources ./dist/claude/whop
scripts/build.sh                  Compose dist/ from shared/ + clients/
scripts/validate.sh               Structure, JSON, and dist/-freshness checks
scripts/check_openai_plugin.py    Offline check of an OpenAI plugin ZIP or folder
scripts/package-openai.py         Zip dist/openai/whop for platform.openai.com/plugins
```

## Working on it

```sh
./scripts/build.sh            # rebuild every client into dist/
./scripts/build.sh grok       # rebuild one
pip install pyyaml            # needed by the OpenAI package check
./scripts/validate.sh         # structure, JSON, and dist/-freshness
python3 scripts/package-openai.py ../whop-openai.zip   # OpenAI submission ZIP + strict check
```

Edit `shared/` for anything every client should say, and `clients/<client>/` for
anything only one client should. Then rebuild and commit `dist/`.

**Adding a client:** create `clients/<name>/client.json` (see an existing one), add any client-specific skills beside it, and run the build. See [clients/README.md](clients/README.md).

Bump `version` in `shared/plugin.base.json` whenever you change the plugin so installed
users get updates. The OpenAI build has its own `version` in `clients/openai/client.json`:
bump it for every OpenAI upload, which leaves the Claude and Grok outputs alone.

## License

Apache-2.0. See [LICENSE](LICENSE).

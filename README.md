# Whop plugins

Official Whop plugin for whatever AI agent you use. Works with Claude Code and Grok Build.

## Install

**Claude Code**

```
/plugin marketplace add whopio/whop-plugins
/plugin install whop@whop
```

Restart Claude Code, then run `/whop:whop-connect`.

**Grok Build**

Install `whop` from the built-in marketplace, then run `/whop-connect`. To authorize,
open `/mcps`, select `whop`, and press `i`.

The first Whop tool call opens a browser for Whop sign-in.

## Supported clients

| Client | Status | Catalog entry |
| --- | --- | --- |
| Claude Code | Shipped (application pending) | `.claude-plugin/marketplace.json` |
| Grok Build | PR pending | [`clients/grok/`](clients/grok/) |

## What the Whop plugin is

| Component | Source | What it does |
| --- | --- | --- |
| MCP config | `shared/mcp.json` | Points the client at `https://mcp.whop.com/mcp`. You sign in through the browser. |
| `whop` skill | `shared/skills/whop/` | Lists every command group and which tool starts each job, and adds guides for websites, ads, and company formation. |
| `whop-mcp-safety` skill | `shared/skills/whop-mcp-safety/` | Rules for calls that change something. |
| `whop-connect` command | `clients/<client>/skills/whop-connect/` | Checks you are signed in, then names the account and what it can reach. Written once per client, because each names its menus differently. |

## Repository layout

```
shared/                          Client-neutral content
  mcp.json                         MCP server config
  plugin.base.json                 Manifest fields common to every client
  skills/                          whop, whop-mcp-safety (+ references)
clients/<client>/                Everything that differs per client
  client.json                      Manifest overrides, output paths, {{TOKEN}} values
  skills/                          Client-specific skills (overrides shared by name)
dist/<client>/whop/              AUTO-GENERATED
.claude-plugin/marketplace.json   Claude marketplace, sources ./dist/claude/whop
scripts/build.sh                  Compose dist/ from shared/ + clients/
scripts/validate.sh               Structure, JSON, and dist/-freshness checks
```

## Working on it

```sh
./scripts/build.sh            # rebuild every client into dist/
./scripts/build.sh grok       # rebuild one
./scripts/validate.sh         # structure, JSON, and dist/-freshness
```

Edit `shared/` for anything every client should say, and `clients/<client>/` for
anything only one client should. Then rebuild and commit `dist/`.

**Adding a client:** create `clients/<name>/client.json` (see an existing one), add any client-specific skills beside it, and run the build. See [clients/README.md](clients/README.md).

Bump `version` in `shared/plugin.base.json` whenever you change the plugin so installed
users get updates.

## License

Apache-2.0. See [LICENSE](LICENSE).

# Other clients

Each client gets a directory here holding only what it does differently. Everything
else comes from `shared/`.

## How it works

`./scripts/build.sh` merges `shared/` with `clients/<client>/` and writes
`dist/<client>/whop`. That output is committed, because marketplaces read files from
this repo at a commit. They never run the build.

## What differs

| Thing | Why |
| --- | --- |
| `whop-connect` skill | It names menus. Claude has `/mcp` and `/plugin`; Grok has `/mcps`, `/plugins`, and the `i` key. |
| Manifest path | Claude reads `.claude-plugin/plugin.json`. Grok prefers `.grok-plugin/plugin.json`. |
| `description` | It names the client, and lands in that client's catalog. |
| Two tokens | `{{CLIENT_NAME}}` and `{{CONNECT_COMMAND}}` in the `whop` skill. |

The `whop` skill, `whop-mcp-safety`, the three playbooks, and the MCP
config are the same across clients.

## Status

| Client | Reads | Status |
| --- | --- | --- |
| Claude Code | `dist/claude/whop` via `.claude-plugin/marketplace.json` | Shipped, application pending |
| Grok Build | `dist/grok/whop`, pinned to a commit in xAI's catalog | PR pending |

## Adding one

Write `clients/<name>/client.json`:

```json
{
  "client": "cursor",
  "displayName": "Cursor",
  "manifestPath": ".cursor-plugin/plugin.json",
  "mcpConfigPath": "mcp.json",
  "tokens": { "CLIENT_NAME": "Cursor", "CONNECT_COMMAND": "the `whop-connect` command" },
  "manifest": { "description": "…" }
}
```

Put client-specific skills in `clients/<name>/skills/`. A skill there replaces the
shared one of the same name. Then, run the build.
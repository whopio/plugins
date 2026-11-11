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
| Tokens | `{{CLIENT_NAME}}` and `{{CONNECT_COMMAND}}` in the shared skills; `{{MCP_URL}}` in the MCP config. Claude points at the directory endpoint `/claude/mcp`. |
| Directory restrictions | Claude's directory listing leaves out AI media generation and money-out tools, and asks before anything spends money or goes live. The shared Markdown holds that text in `{{#if claude}} … {{else}} … {{/if}}` blocks, so other clients keep the full surface. |
| What the route lists | Each skill names only the tools its client's route has. Claude and Grok list the most-used tools and reach the rest with `search_operations` and `call_read_operation` / `call_write_operation`. The job skills also hold `{{#if openai}}` blocks for the ChatGPT route, which lists every tool by name and has no search, call or refund tool. No `openai` client exists here yet, so those blocks are left out of every build until one is added. |

The shared skills, the three playbooks, and the MCP config come from one source for
every client. The per-client blocks above are the only place they differ.

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
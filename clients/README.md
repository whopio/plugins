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
| `whop-connect` skill | It names menus. Claude has `/mcp` and `/plugin`; Grok has `/mcps`, `/plugins`, and the `i` key; ChatGPT has its Plugins page and Codex has `/plugins`. The OpenAI copy is also the plugin's `onboardingSkill`, with `agents/openai.yaml` instead of `disable-model-invocation`. |
| Manifest path | Claude reads `.claude-plugin/plugin.json`. Grok prefers `.grok-plugin/plugin.json`. OpenAI reads the portable root `plugin.json`, with its listing and review data under `extensions["com.openai"]`. |
| MCP config | Claude and Grok render `shared/mcp.json` (`type: "http"`, an `X-Whop-Plugin` header). OpenAI renders `clients/openai/mcp.json`: `$schema`, `type: "streamable-http"`, and no headers, because public submission rejects them. |
| `description` | It names the client, and lands in that client's catalog. |
| Tokens | `{{CLIENT_NAME}}` and `{{CONNECT_COMMAND}}` in the `whop` skill; `{{MCP_URL}}` in the MCP config. Claude points at the directory endpoint `/claude/mcp`. |
| Directory restrictions | Claude's directory listing leaves out AI media generation and money-out tools, and asks before anything spends money or goes live. ChatGPT serves AI media but leaves out issuing refunds, one-off charges to customers, money movement, identity verification, and credentials; its skill gets a yes before anything that costs money or goes live. The shared Markdown holds that text in `{{#if claude}} … {{#elif openai}} … {{else}} … {{/if}}` blocks (`{{#if claude,openai}}` where both agree), so other clients keep the full surface. The OpenAI ads and formation playbooks differ throughout, so they are client files under `clients/openai/skills/whop/references/`. |

The `whop` skill, the websites playbook, and the MCP config template are shared. OpenAI
overrides `references/ads.md`, `references/formation.md`, and the MCP config
(`clients/openai/mcp.json`). Everything else differs only in the template blocks above.

## Status

| Client | Reads | Status |
| --- | --- | --- |
| Claude Code | `dist/claude/whop` via `.claude-plugin/marketplace.json` | Shipped, application pending |
| Grok Build | `dist/grok/whop`, pinned to a commit in xAI's catalog | PR pending |
| ChatGPT and Codex | A ZIP of `dist/openai/whop` from `scripts/package-openai.py`, uploaded at platform.openai.com/plugins | Built, not submitted; the `/chatgpt/mcp` route does not exist yet |

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

Put client-specific skill files in `clients/<name>/skills/`. A file there replaces the
shared file at the same path, so a full skill folder replaces a whole skill. Then, run
the build.

Optional keys: `version` (this client's own version), `mcpTemplate` (another MCP
config template), `dropManifestKeys`, `extraFiles` (extra files to ship, as
`{"<output path>": "<source path>"}`), and `lineEndings: "lf"` (write every text file
with LF on every platform; `.gitattributes` keeps `dist/openai/**` LF on checkout to
match). `clients/openai/client.json` uses `version`, `mcpTemplate`,
`dropManifestKeys`, and `lineEndings`.
`scripts/compose.py` documents each one.
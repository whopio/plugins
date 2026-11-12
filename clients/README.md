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
| Tokens | `{{CLIENT_NAME}}` and `{{CONNECT_COMMAND}}` in the shared skills; `{{MCP_URL}}` in the MCP config. Claude points at the directory endpoint `/claude/mcp`. |
| Directory restrictions | Claude's directory listing leaves out AI media generation and money-out tools, and asks before anything spends money or goes live. The shared Markdown holds that text in `{{#if claude}} … {{else}} … {{/if}}` blocks, so other clients keep the full surface. ChatGPT serves AI media but leaves out issuing refunds, one-off charges to customers, money movement, identity verification, and credentials; its skill gets a yes before anything that costs money or goes live. |
| What the route lists | Each skill names only the tools its client's route has. Claude and Grok list the most-used tools and reach the rest with `search_operations` and `call_read_operation` / `call_write_operation`. The job skills also hold `{{#if openai}}` blocks for the ChatGPT route, which lists every tool by name and has no search, call or refund tool. The `openai` build keeps those blocks. |

The shared skills, the three playbooks, and the MCP config come from one source for
Claude, Grok and the generic client. The per-client blocks above are the only place
they differ. OpenAI takes the same job skills and the websites playbook, with its own entry
`whop` skill (`clients/openai/skills/whop/`), its own ads and formation playbooks
(`clients/openai/skills/whop-docs-and-operations/references/`), and its own MCP
config (`clients/openai/mcp.json`).

## Status

| Client | Reads | Status |
| --- | --- | --- |
| Claude Code | `dist/claude/whop` via `.claude-plugin/marketplace.json` | Shipped, application pending |
| Grok Build | `dist/grok/whop`, pinned to a commit in xAI's catalog | PR pending |
| Generic | `dist/generic/whop` via `.plugin/marketplace.json` | Built, not yet tried in each tool |
| ChatGPT and Codex | A ZIP of `dist/openai/whop` from `scripts/package-openai.py`, uploaded at platform.openai.com/plugins | Built, not submitted; the `/chatgpt/mcp` route does not exist yet |

## The generic client

`clients/generic/` is the build for every tool without a client of its own. It uses
the vendor-neutral manifest path `.plugin/plugin.json`, which the
[`plugins`](https://github.com/vercel-labs/plugins) installer converts for each tool
it finds: `npx plugins add whopio/plugins`.

- It points at `https://mcp.whop.com/mcp`, the same route as Grok, so it sets
  `"sameBlocksAs": ["grok"]` and takes every block written for Grok.
- Its `whop-connect` skill names no menus, because it cannot know which tool it is
  running in.

### Which build each install gets

A directory listing (Claude's, xAI's, OpenAI's) pins its own build. Every other
install should get the generic build. Three identical marketplace files make that
so: `.plugin/marketplace.json`, `.github/plugin/marketplace.json` and
`.cursor-plugin/marketplace.json`.

| Install | Build | Why |
| --- | --- | --- |
| `npx plugins add whopio/plugins`, any target | generic | The installer reads `.plugin/marketplace.json` before any other. |
| Claude Code, `/plugin marketplace add whopio/plugins` | claude | Claude Code reads `.claude-plugin/marketplace.json`. |
| GitHub Copilot CLI, `copilot plugin marketplace add` | generic | Copilot reads `.github/plugin/marketplace.json` before `.claude-plugin/`. |
| Cursor, a repository link or a team marketplace | generic | Cursor reads `.cursor-plugin/marketplace.json`, and the build carries `.cursor-plugin/plugin.json`. |
| Grok catalog, ChatGPT and Codex directory | grok, openai | Each catalog names its own `dist/` path. |

Read from the installer's code, version 1.3.6, and the tools' docs. None of these
has been run end to end yet.

Things the installer does that are easy to miss:

- For Claude Code and Cursor it writes to the same place, `~/.claude/plugins`, under
  the marketplace's name. The generic marketplace is named `whop-plugin` and the
  Claude one `whop`, so the generic build installs as `whop@whop-plugin` and leaves
  an existing `whop@whop` alone. Keep the two names different. Someone with both
  has two copies of the plugin enabled and should remove one.
- For Codex it installs the generic build as `whop@plugins-cli`, not the ChatGPT
  build.
- Do not add `.claude-plugin/plugin.json` to the generic build. With it, the
  installer registers the Claude Code marketplace against GitHub, and the next
  update there switches the install to the Claude build.

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
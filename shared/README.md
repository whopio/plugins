# Whop plugin for {{DISPLAY_NAME}}

The official Whop plugin connects {{CLIENT_NAME}} to your Whop business through the
hosted Whop MCP server (`https://mcp.whop.com/mcp`). Sign in with your Whop account in
the browser — no API key is stored or read from your machine — and then ask in plain
language to launch a website, create products and checkout links, manage payments,
refunds, payouts, and disputes, run Meta and TikTok ads, form an LLC or C-corp, post
bounties, or read your stats.

## Getting started

1. Install the plugin and restart {{CLIENT_NAME}}.
2. Run {{CONNECT_COMMAND}}. The first Whop tool call opens your browser so you can sign
   in to Whop and approve access.
3. Describe what you want, for example "create a $20/month membership and give me the
   checkout link" or "show me last week's revenue".

Anything that moves money, issues credentials, or deletes data is prepared first and
only runs after you confirm it.

## What's included

- **Whop MCP server** — the tools that act on your Whop account.
- **`whop` skill** — maps each job to the right tools, with guides for websites, ads,
  and company formation.
- **`whop-mcp-safety` skill** — the confirm-before-acting rules for changes.
- **`whop-connect` command** — checks you are signed in and names the account it can
  reach.

## Links

- Docs: https://docs.whop.com/
- Privacy policy: https://whop.com/privacy
- Source: https://github.com/whopio/plugins

<!-- Generated from shared/README.md and clients/{{CLIENT_KEY}}/ by ./scripts/build.sh — do not edit here. -->

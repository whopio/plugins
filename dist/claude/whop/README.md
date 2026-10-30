# Whop plugin for Claude

The official Whop plugin connects Claude to your Whop business through the hosted Whop MCP server (`https://mcp.whop.com/claude/mcp`). Sign in with your Whop account in the browser — no API key is stored or read from your machine — and then ask in plain language to launch a website, create products and checkout links, manage payments, refunds, and disputes, run ads from your own images, form an LLC or C-corp, or read your stats.

## Getting started

1. Install the plugin. In the Claude app, add Whop from the plugin directory. In Claude Code, run `/plugin marketplace add whopio/plugins`, then `/plugin install whop@whop`, and restart Claude Code.
2. Connect Whop: on the plugin's Connectors tab in the Claude app, or with `/whop:whop-connect` in Claude Code. Your browser opens so you can sign in to Whop and approve access.
3. Describe what you want, for example "create a $20/month membership and give me the checkout link" or "show me last week's revenue".

## What's included

- **Whop MCP server** — the tools that act on your Whop account.
- **`whop` skill** — maps each job to the right tools, with guides for websites, ads, and company formation.
- **`whop-connect` command** — checks you are signed in and names the account it can reach.

## Links

- Docs: https://docs.whop.com/
- Privacy policy: https://whop.com/privacy
- Source: https://github.com/whopio/plugins

<!-- Generated from shared/README.md and clients/claude/ by ./scripts/build.sh — do not edit here. -->

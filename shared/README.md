# Whop plugin for {{DISPLAY_NAME}}

{{#if claude}}
The official Whop plugin connects {{CLIENT_NAME}} to your Whop business through the hosted Whop MCP server (`{{MCP_URL}}`). Sign in with your Whop account in the browser — no API key is stored or read from your machine — and then ask in plain language to launch a website, create products and checkout links, manage payments, refunds, and disputes, run Meta and TikTok ads, form an LLC or C-corp, or read your stats.
{{else}}
The official Whop plugin connects {{CLIENT_NAME}} to your Whop business through the hosted Whop MCP server (`{{MCP_URL}}`). Sign in with your Whop account in the browser — no API key is stored or read from your machine — and then ask in plain language to launch a website, create products and checkout links, manage payments, refunds, payouts, and disputes, run Meta and TikTok ads, form an LLC or C-corp, post bounties, or read your stats.
{{/if}}

## Getting started

{{#if claude}}
1. Install the plugin with `/plugin install whop --marketplace whopio/plugins`, then restart {{CLIENT_NAME}}.
{{else}}
1. Install the plugin and restart {{CLIENT_NAME}}.
{{/if}}
{{#if generic}}
   `npx plugins add whopio/plugins` installs it into every supported tool it finds
   on your machine.
{{/if}}
2. Run {{CONNECT_COMMAND}}. The first Whop tool call opens your browser so you can sign in to Whop and approve access.
3. Describe what you want, for example "create a $20/month membership and give me the checkout link" or "show me last week's revenue".

## What's included

- **Whop MCP server** — the tools that act on your Whop account.
- **Skills** — one per job, so {{CLIENT_NAME}} knows which tools to use and what to check first:
  - `whop` — checks the connection, picks the business, and points to the right skill.
  - `whop-payments` — sales, refunds, disputes, and buyer complaints.
  - `whop-products` — products, prices, promo codes, and checkout links.
  - `whop-customers` — members, memberships, and cancellations.
  - `whop-courses` — courses, lessons, apps, and file uploads.
  - `whop-community` — support chats, DMs, community chat, and forum posts.
  - `whop-stats` — revenue and other metrics over time.
  - `whop-docs-and-operations` — searches the Whop docs and reaches everything else, with guides for websites, ads, and company formation.
- **`whop-connect` command** — checks you are signed in and names the account it can reach.

## Links

- Docs: https://docs.whop.com/
- Privacy policy: https://whop.com/privacy
- Source: https://github.com/whopio/plugins

<!-- Generated from shared/README.md and clients/{{CLIENT_KEY}}/ by ./scripts/build.sh — do not edit here. -->

# Whop plugin for ChatGPT and Codex

Whop's plugin connects ChatGPT and Codex to the Whop businesses you run, through the hosted Whop MCP server (`https://mcp.whop.com/chatgpt/mcp`). Sign in with your Whop account in the browser — no API key is stored or typed into the chat — and then ask in plain language to launch a website you build in Codex or on Whop and buy or connect its domain, create products and checkout links for your customers, look up payments and manage disputes, run Whop Ads from your own images or videos (in Codex) or AI-generated ones, form an LLC or C-corp, or read your stats. It asks before anything that goes live or costs money. Payouts and other money movement, issuing refunds, and one-off charges to customers are not available in this plugin. For company formation, teams with no US address get a checkout link here, and a team with a US-address founder forms on Whop's own form.

## Getting started

1. Install Whop from the Plugins directory in ChatGPT or Codex.
2. Connect Whop when asked. Your browser opens Whop so you can sign in and approve access. To reconnect later, use the Whop plugin's settings. In Codex, type `$whop:whop-connect` to see which business is connected.
3. Describe what you want, for example "who are my newest members this week?" or "how did my revenue change month over month?".

## What's included

- **Whop MCP server** — the tools that act on your Whop account.
- **Skills** — one per job, so ChatGPT and Codex knows which tools to use and what to check first:
  - `whop` — checks the connection, picks the business, and points to the right skill.
  - `whop-payments` — sales, refund history, disputes, and buyer complaints.
  - `whop-products` — products, prices, promo codes, and checkout links.
  - `whop-customers` — members, memberships, and cancellations.
  - `whop-courses` — courses, lessons, apps, and file uploads.
  - `whop-community` — support chats, DMs, community chat, and forum posts.
  - `whop-stats` — revenue and other metrics over time.
  - `whop-docs-and-operations` — searches the Whop docs and reaches everything else, with guides for websites, ads, and company formation.
- **`whop-connect` setup skill** — checks you are signed in and names the account it can reach.

## Links

- Docs: https://docs.whop.com/
- Privacy policy: https://whop.com/privacy
- Source: https://github.com/whopio/plugins

<!-- Generated from shared/README.md and clients/openai/ by ./scripts/build.sh — do not edit here. -->

# Whop plugin for {{DISPLAY_NAME}}

{{#if claude}}
The official Whop plugin connects {{CLIENT_NAME}} to your Whop business through the hosted Whop MCP server (`{{MCP_URL}}`). Sign in with your Whop account in the browser — no API key is stored or read from your machine — and then ask in plain language to launch a website, create products and checkout links, manage payments, refunds, and disputes, run Meta and TikTok ads, form an LLC or C-corp, or read your stats.
{{#elif openai}}
Whop's plugin connects ChatGPT and Codex to the Whop businesses you run, through the hosted Whop MCP server (`{{MCP_URL}}`). Sign in with your Whop account in the browser — no API key is stored or typed into the chat — and then ask in plain language to launch a website you build in Codex or on Whop and buy or connect its domain, create products and checkout links for your customers, look up payments and manage disputes, run Whop Ads from your own images or videos (in Codex) or AI-generated ones, form an LLC or C-corp, or read your stats. It asks before anything that goes live or costs money. Payouts and other money movement, issuing refunds, and one-off charges to customers are not available in this plugin. For company formation, teams with no US address get a checkout link here, and a team with a US-address founder forms on Whop's own form.
{{else}}
The official Whop plugin connects {{CLIENT_NAME}} to your Whop business through the hosted Whop MCP server (`{{MCP_URL}}`). Sign in with your Whop account in the browser — no API key is stored or read from your machine — and then ask in plain language to launch a website, create products and checkout links, manage payments, refunds, payouts, and disputes, run Meta and TikTok ads, form an LLC or C-corp, post bounties, or read your stats.
{{/if}}

## Getting started

{{#if claude}}
1. Install the plugin with `/plugin install whop --marketplace whopio/plugins`, then restart {{CLIENT_NAME}}.
2. Run {{CONNECT_COMMAND}}. The first Whop tool call opens your browser so you can sign in to Whop and approve access.
3. Describe what you want, for example "create a $20/month membership and give me the checkout link" or "show me last week's revenue".
{{#elif openai}}
1. Install Whop from the Plugins directory in ChatGPT or Codex.
2. Connect Whop when asked. Your browser opens Whop so you can sign in and approve access. To reconnect later, use the Whop plugin's settings. In Codex, type `$whop:whop-connect` to see which business is connected.
3. Describe what you want, for example "who are my newest members this week?" or "how did my revenue change month over month?".
{{else}}
1. Install the plugin and restart {{CLIENT_NAME}}.
2. Run {{CONNECT_COMMAND}}. The first Whop tool call opens your browser so you can sign in to Whop and approve access.
3. Describe what you want, for example "create a $20/month membership and give me the checkout link" or "show me last week's revenue".
{{/if}}

## What's included

- **Whop MCP server** — the tools that act on your Whop account.
{{#if openai}}
- **`whop` skill** — maps each job to the right tools, with guides for websites and domains, ads, and company formation.
- **`whop-connect` setup skill** — checks you are signed in and names the account it can reach.
{{else}}
- **`whop` skill** — maps each job to the right tools, with guides for websites, ads, and company formation.
- **`whop-connect` command** — checks you are signed in and names the account it can reach.
{{/if}}

## Links

- Docs: https://docs.whop.com/
- Privacy policy: https://whop.com/privacy
- Source: https://github.com/whopio/plugins

<!-- Generated from shared/README.md and clients/{{CLIENT_KEY}}/ by ./scripts/build.sh — do not edit here. -->

---
name: whop
description: "Work with the user's Whop business through the Whop MCP tools: websites on *.whop.app, products, checkout links, payments, refunds, disputes, memberships, ads, LLC/C-corp formation, and stats. Use when the user mentions Whop or whop.com, or asks about something that lives in their Whop account (a Whop store, membership, checkout link, or Whop ads campaign)."
---

# Whop

This plugin connects Claude to a live Whop business through the Whop MCP
server. Use these tools for work on the user's Whop account. For anything outside
Whop — another store platform, another ad account, general business advice — use
whatever else the user has set up. No CLI is needed.

## Before anything else

1. **Check the connection.** Call `connection_status`. It returns the authenticated
   identity, the selected account, granted scopes, and tool coverage. If it fails or
   the plugin's tools are missing, the user has not completed OAuth — tell them to
   run `/whop:whop-connect`.
2. **Discover, do not guess.** Tool names follow `<group>_<operation>`, with
   hyphens inside multi-word groups (`payments_list`, `ad-campaigns_update`). Read
   the tool's own schema before calling it. Never invent a tool name, a field, or an
   enum value — if you cannot find it, say so and ask.
3. **Know the account.** `connection_status` returns `account_id`, and it is often
   **null** — a user grant is not bound to one business. When it is null, nothing is
   selected for you: get the id from `accounts_list` and pass `account_id` (`biz_…`)
   explicitly on account-scoped calls. Never assume a default business.

## What to run

| Job | Start here | Playbook |
| --- | --- | --- |
| Check who I am / what I can do | `connection_status` | — |
| Ship a website on `*.whop.app` | `apps_create`, then `apps_deploy` | [references/websites.md](references/websites.md) |
| Sell something | `products_*`, `plans_*`, `checkout-configurations_*` | — |
| Customers and access | `members_*`, `memberships_*` | — |
| Payments, refunds, disputes | `payments_*`, `refunds_*`, `disputes_*` | — |
| Run ads | `ads_*`, `ad-campaigns_*`, `ad-groups_*` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
| Measure | `stats_*`, `exports_*`, `events_*`, `people_*` | — |
| Developer surface | `apps_*`, `app-builds_*`, `api-keys_*`, `webhooks_*` | — |

The table is a router, not a schema. Read the playbook before websites, ads, or
formation — each has ordering traps that a tool description alone does not teach.

## Working with app source

`apps_deploy` builds the app's **current source on Whop** and ships it, so deploying
an app Whop already holds needs nothing local. Only one deployment runs per app at a
time; calling it again reports the running one instead of starting a second, and
calling it with nothing to publish says so. Pass `draft: true` to upload without
making it live.

To ship code that only exists on this machine, do the local half yourself and the
rest over MCP: write and build the files with your own tools, upload the artifact
with `files_create` / `files_complete`, register it with `app-builds_create`, then
`app-builds_promote`. Do not tell the user to install a CLI for this.

## Working agreement

- **Confirm before anything spends money or goes live.** Before launching or
  unpausing an ad campaign, raising a budget, retrying an ad payment, deploying or
  promoting a site build (anything but `draft: true`), or charging a customer, say
  what will happen and what it costs, and wait for the user to say yes. Drafts,
  previews, and reads need no confirmation.
- **Action links are for the user, not for you.** When a response carries
  `authorize_url`, `session_url`, `deposit_url`, or `checkout_url`, give the link to
  the user and say what they need to finish there. Do not fetch or curl it to
  "verify" — that does not complete the flow and can consume a single-use URL.
  Re-run the matching `get`/`list` afterwards to confirm the outcome.
- `hosted_url` is not an action link. For an app it is the live app URL — display it.
- **Never echo secrets.** API keys, access tokens, and founder identity data (SSN,
  date of birth, home address) are legitimate inputs to the flows that need them.
  Pass them straight through to the tool. Never repeat them back in your response,
  write them to a file, or infer a value the user did not supply.

## What these tools cannot reach

This connection deliberately leaves out AI media generation and anything that moves
money out of the account: payouts, transfers, bounty rewards, card issuing, balance
top-ups, and trading. If the user asks for one of those, say it is not available
here and send them to whop.com to do it themselves. Do not look for a workaround.

Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are also absent. Send the user to whop.com
for those.

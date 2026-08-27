---
name: whop
description: "Run a business on Whop: websites on *.whop.app, products, checkout, payments, payouts, memberships, ads, LLC/C-corp formation, bounties, and stats. Use when the user mentions Whop, whop.com, their store, a membership or product, checkout links, payouts or transfers, Meta/TikTok ads, forming a company, or anything the Whop MCP tools provide. Not for the internal `whopdev` local-dev CLI."
---

# Whop

This plugin connects Claude to a live Whop business through the Whop MCP
server. Those tools are the way to do everything — there is no second path to
prefer, and no CLI to install.

## Before anything else

1. **Check the connection.** Call `connection_status`. It returns the authenticated
   identity, the selected account, granted scopes, and tool coverage. If it fails or
   the plugin's tools are missing, the user has not completed OAuth — tell them to
   run `/whop:whop-connect`.
2. **Discover, do not guess.** Tool names follow `<group>_<operation>`
   (`payments_list`, `products_create`). Read the tool's own schema before calling
   it. Never invent a tool name, a field, or an enum value — if you cannot find it,
   say so and ask.
3. **Know the account.** `connection_status` returns `account_id`, and it is often
   **null** — a user grant is not bound to one business. When it is null, nothing is
   selected for you: get the id from `accounts_list` and pass `account_id` (`biz_…`)
   explicitly on account-scoped calls. Never assume a default business.

## Before any write

**Read `whop-mcp-safety` before your first mutating call in a session.** Whop's
consequential operations use a prepare-and-confirm handshake plus required
attribution fields that are easy to get wrong and expensive to get wrong. That
skill is the protocol; this one is the map.

## What to run

| Job | Start here | Playbook |
| --- | --- | --- |
| Check who I am / what I can do | `connection_status` | — |
| Ship a website on `*.whop.app` | `apps_create`, then `apps_deploy` | [references/websites.md](references/websites.md) |
| Sell something | `products_*`, `plans_*`, `checkout_configurations_*` | — |
| Customers and access | `members_*`, `memberships_*` | — |
| Take and manage money | `payments_*`, `payouts_*`, `transfers_*`, `deposits_*`, `cards_*`, `disputes_*` | — |
| Run ads | `media_generate`, `ads_*`, `ad_campaigns_*`, `ad_groups_*` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
| Hire | `bounties_*`, `bounty_submissions_*` | — |
| Measure | `stats_*`, `exports_*`, `events_*`, `people_*` | — |
| Developer surface | `apps_*`, `app_builds_*`, `api_keys_*`, `webhooks_*` | — |

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
with `files_create` / `files_complete`, register it with `app_builds_create`, then
`app_builds_promote`. Do not tell the user to install a CLI for this.

## Working agreement

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
- **Money and identity are the user's call.** Confirm before executing any financial,
  credential, or destructive operation, subject to the narrow exceptions in
  `whop-mcp-safety`.

## What these tools cannot reach

Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are deliberately absent. Send the user to
whop.com for those; no tool and no CLI will do it.

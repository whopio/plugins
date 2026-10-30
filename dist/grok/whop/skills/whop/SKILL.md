---
name: whop
description: "Run a business on Whop: websites on *.whop.site, products, checkout, payments, payouts, memberships, ads, LLC/C-corp formation, bounties, and stats. Use when the user mentions Whop, whop.com, their store, a membership or product, checkout links, payouts or transfers, Meta/TikTok ads, forming a company, or anything the Whop MCP tools provide."
---

# Whop

This plugin connects Grok to a live Whop business through the Whop MCP
server. Those tools are the way to do everything — there is no second path to
prefer, and no CLI to install.

## Before anything else

1. **Check the connection.** Call `connection_status`. It returns the authenticated
   identity, the selected account, granted scopes, and tool coverage. If it fails or
   the plugin's tools are missing, the user has not completed OAuth — tell them to
   run `/whop-connect`.
2. **Discover, do not guess.** Tool names follow `<group>_<operation>`, with
   hyphens inside multi-word groups (`payments_list`, `ad-campaigns_update`). Read
   the tool's own schema before calling it. Never invent a tool name, a field, or an
   enum value — if you cannot find it, say so and ask.
3. **Know the account.** `connection_status` returns `account_id`, and it is often
   **null** — a user grant is not bound to one business. When it is null, nothing is
   selected for you: get the id from `accounts_list` and pass `account_id` (`biz_…`)
   explicitly on account-scoped calls. Never assume a default business. Pass it on
   list calls too: `products_list` without `account_id` searches the public Whop
   marketplace, not the user's store.

## What to run

| Job | Start here | Playbook |
| --- | --- | --- |
| Check who I am / what I can do | `connection_status` | — |
| Ship a website on `*.whop.site` | `apps_create`, then `apps_deploy` | [references/websites.md](references/websites.md) |
| Sell something | `products_*`, `variants_*`, `checkout-configurations_*` | — |
| Customers and access | `members_*`, `memberships_*` | — |
| Take and manage money | `payments_*`, `payouts_*`, `transfers_*`, `deposits_*`, `cards_*`, `disputes_*` | — |
| Run ads | `media_generate`, `ads_*`, `ad-campaigns_*`, `ad-groups_*` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
| Hire | `bounties_*`, `bounty-submissions_*` | — |
| Measure | `stats_*`, `exports_*`, `events_*`, `people_*` | — |
| Developer surface | `apps_*`, `app-builds_*` | — |

The table is a router, not a schema. Read the playbook before websites, ads, or
formation — each has ordering traps that a tool description alone does not teach.

Variants are a product's prices and billing options; older docs call them plans.
Use `variants_*`. `checkout-configurations_create` takes a variant's id (`plan_id`
or `variant_id`, whichever its schema lists) or an inline variant (`plan` or
`variant`).

`payments_list` has no failed or refunded `status` filter. To find failed or
refunded payments, list the date range and read each payment's `substatus`
(`failed`, `refunded`, `partially_refunded`, and so on).

## Working with app source

`apps_deploy` builds the app's **current source on Whop** and ships it, so deploying
an app Whop already holds needs nothing local. Only one deployment runs per app at a
time; calling it again reports the running one instead of starting a second, and
calling it with nothing to publish says so. Pass `draft: true` to upload without
making it live.

To ship code that only exists on this machine, do the local half yourself and the
rest over MCP: write and build the files with your own tools, upload the artifact
(`files_create`, PUT the bytes to its `upload_url` with its `upload_headers`, then
poll `files_get` until `upload_status` is `ready`), register it with
`app-builds_create`, then `app-builds_promote`. Do not tell the user to install a
CLI for this.

## Working agreement

- **Action links are for the user, not for you.** When a response carries
  `authorize_url`, `session_url`, `deposit_url`, `checkout_url`, or `purchase_url`,
  give the link to the user and say what they need to finish there. Do not fetch or
  curl it to "verify" — that does not complete the flow and can consume a single-use
  URL. Re-run the matching `get`/`list` afterwards to confirm the outcome.
- `hosted_url` is not an action link. On an app it is deprecated and can be null:
  the app's addresses are in its `domains`. A `ready` one is live. For any other
  status, check `website.state` (or `platform.state`) on `domains_get` before
  saying it is down.
- **Never echo secrets.** API keys, access tokens, and founder identity data (SSN,
  date of birth, home address) are legitimate inputs to the flows that need them.
  Pass them straight through to the tool. Never repeat them back in your response,
  write them to a file, or infer a value the user did not supply.

## What these tools cannot reach

Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are deliberately absent. Send the user to
whop.com for those; no tool and no CLI will do it.

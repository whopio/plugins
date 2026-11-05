---
name: whop
{{#if claude}}
description: "Work with the user's Whop business through the Whop MCP tools: websites on *.whop.app, products, checkout links, payments, refunds, disputes, memberships, ads, LLC/C-corp formation, and stats. Use when the user mentions Whop or whop.com, or asks about something that lives in their Whop account (a Whop store, membership, checkout link, or Whop ads campaign)."
{{#elif openai}}
description: "Build, run and grow a Whop business the user runs or manages, through the Whop MCP tools: websites on *.whop.site (new ones built in Codex or on Whop) and their domains, products, prices and checkout links for the business's customers, members and memberships, payments, refund history, disputes, Whop Ads campaigns with the user's own images or videos (uploaded from Codex) or AI-generated ones, LLC and C-corp formation, and stats. Use when the user wants to read or change something in a Whop business they run or manage. Not for general questions about Whop, and not for shopping on Whop."
{{else}}
description: "Run a business on Whop: websites on *.whop.app, products, checkout, payments, payouts, memberships, ads, LLC/C-corp formation, bounties, and stats. Use when the user mentions Whop, whop.com, their store, a membership or product, checkout links, payouts or transfers, Meta/TikTok ads, forming a company, or anything the Whop MCP tools provide."
{{/if}}
---

# Whop

This plugin connects {{CLIENT_NAME}} to a live Whop business through the Whop MCP
{{#if claude,openai}}
server. Use these tools for work on the user's Whop account. For anything outside
Whop — another store platform, another ad account, general business advice — use
whatever else the user has set up. No CLI is needed.
{{else}}
server. Those tools are the way to do everything — there is no second path to
prefer, and no CLI to install.
{{/if}}
{{#if openai}}

**Only businesses the user runs.** This plugin works on Whop businesses the user
runs or manages, as the seller. Do not browse or search the Whop marketplace for
the user, recommend other sellers' products, or give the user links to buy them. If
they want to shop on Whop, say that is not available in this plugin. Do not act as a buyer for them either: do not open a
Resolution Center case as the customer, join or withdraw from a waitlist, start or
complete course lessons, or submit work to a bounty.
{{/if}}

## Before anything else

{{#if openai}}
1. **Find the business.** Call `accounts_list` and use the business the user means;
   if there are several and it is unclear which, ask. A signed-in user is not bound
   to one business, so nothing is selected for you. If `accounts_list` returns none
   and the request needs a business, say the user has no Whop business yet and offer
   to create one with `accounts_create`: set only the `title` they give, and only
   after their yes. They can also create one in their Whop dashboard.
2. **If a tool fails with an auth error, or the Whop tools are missing,** the user
   has not finished connecting: tell them to connect or reconnect Whop from the Whop
   plugin's settings. In Codex, typing `$whop:whop-connect` also checks the
   connection. Call `connection_status` only then, or when the user asks who is
   connected.
   `missing_scope` is not that kind of error: reconnecting requests the same access,
   so do not suggest it. Say this connection or the user's role on that business does
   not allow the action, and that they can check in their Whop dashboard.
   `Unauthorized: Actor is missing ... permissions` is not one either: this connection
   does not hold that permission and reconnecting will not add it. Say it is not
   available here and that the user can do it in their Whop dashboard.
3. **Discover, do not guess.** Tool names follow `<group>_<operation>`, with
   hyphens inside multi-word groups (`payments_list`,
   `checkout-configurations_create`). Read the tool's own schema before calling it.
   Never invent a tool name, a field, or an enum value — if you cannot find it, say
   so and ask.
4. **Pass the business explicitly.** Pass the `account_id` from `accounts_list` on
   every call whose schema has an `account_id` field, list calls included:
   `products_list` without it searches the public Whop marketplace, not the user's
   store. Tools without that field take an object id instead; `accounts_form_company`
   takes the business id as `id`. Do not use `search`: it takes no `account_id` and
   can reach the marketplace. Use the group's `_list` tools with `account_id`
   instead.
{{else}}
1. **Check the connection.** Call `connection_status`. It returns the authenticated
   identity, the selected account, granted scopes, and tool coverage. If it fails or
   the plugin's tools are missing, the user has not completed OAuth — tell them to
   run {{CONNECT_COMMAND}}.
2. **Discover, do not guess.** Tool names follow `<group>_<operation>`, with
   hyphens inside multi-word groups (`payments_list`, `ad-campaigns_update`). Read
   the tool's own schema before calling it. Never invent a tool name, a field, or an
   enum value — if you cannot find it, say so and ask.
3. **Know the account.** `connection_status` returns `account_id`, and it is often
   **null** — a user grant is not bound to one business. When it is null, nothing is
   selected for you: get the id from `accounts_list` and pass `account_id` (`biz_…`)
   explicitly on account-scoped calls. Never assume a default business.
{{/if}}

## What to run

| Job | Start here | Playbook |
| --- | --- | --- |
| Check who I am / what I can do | `connection_status` | — |
{{#if openai}}
| Publish a website Whop already holds | `apps_list` with `account_id` and `app_type: "website"`, `app-builds_list`, then `app-builds_promote` | [references/websites.md](references/websites.md) |
| Build a new website (Codex only) | `apps_create`, then upload a build | [references/websites.md](references/websites.md) |
| Connect or buy a domain | `domains_*` | [references/websites.md](references/websites.md) |
| Products, prices, and checkout links for the user's customers | `products_*`, `variants_*`, `checkout-configurations_*`, `promo-codes_*` | — |
{{else}}
| Ship a website on `*.whop.app` | `apps_create`, then `apps_deploy` | [references/websites.md](references/websites.md) |
| Sell something | `products_*`, `plans_*`, `checkout-configurations_*` | — |
{{/if}}
| Customers and access | `members_*`, `memberships_*` | — |
{{#if claude}}
| Payments, refunds, disputes | `payments_*`, `refunds_*`, `disputes_*` | — |
| Run ads | `ads_*`, `ad-campaigns_*`, `ad-groups_*` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
{{#elif openai}}
| Payments, refunds, disputes (read and respond) | `payments_*`, `refunds_*`, `disputes_*`; Resolution Center cases as the merchant: `resolution-center-cases_list`, `_get`, `_events`, `_summary`, `_reply`, `_request_info`, `_deny` | — |
| Balance and ledger (read only) | `ledgers_*`, `ledger-accounts_get` | — |
| Run Whop Ads | `ad-campaigns_*`, `ad-groups_*`, `ads_*`, `media_generate` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
{{else}}
| Take and manage money | `payments_*`, `payouts_*`, `transfers_*`, `deposits_*`, `cards_*`, `disputes_*` | — |
| Run ads | `media_generate`, `ads_*`, `ad-campaigns_*`, `ad-groups_*` | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | `accounts_form_company` | [references/formation.md](references/formation.md) |
| Hire | `bounties_*`, `bounty-submissions_*` | — |
{{/if}}
{{#if openai}}
| Measure | `stats_*` (read only); `exports_*` only when the user asks for an export, and never of anything under "What these tools cannot reach": no `payouts`, `transfers`, `payout_methods`, `external_accounts`, `card_transactions`, `financial-activity`, or `webhooks` | — |
| Developer surface | `apps_*`, `app-builds_*` | — |

The table is a router, not a schema. Read the playbook before websites, domains,
ads, or formation — each has ordering traps that a tool description alone does not
teach.

Exports of `members`, `memberships`, `unclaimed_memberships`, `cancelation_reasons`,
`receipts`, `receipt_invoices`, `resolutions`, `leads`, `invoices` and
`child_companies` always fail here with `missing_scope`, and reconnecting does not
help. Do not call them. Say they are not available in this plugin and that the user
can export them in their Whop dashboard.

Variants are a product's prices and billing options; older docs call them plans.
Use `variants_*`. `checkout-configurations_create` takes either an existing
variant's id or an inline variant, never both: `plan_id` and `plan` on older API
versions, `variant_id` and `variant` on newer ones. Use whichever pair the tool's
schema lists.

The `status` filter on `payments_list` has no failed or refunded value. For failed
or refunded payments, pass `failed`, `refunded`, `auto_refunded` (Whop refunded it on
its own, for example on a dispute alert) and `partially_refunded` in `substatuses`.
The filter matches only the values you pass.
{{else}}
| Measure | `stats_*`, `exports_*`, `events_*`, `people_*` | — |
| Developer surface | `apps_*`, `app-builds_*`, `api-keys_*`, `webhooks_*` | — |

The table is a router, not a schema. Read the playbook before websites, ads, or
formation — each has ordering traps that a tool description alone does not teach.
{{/if}}

## Working with app source

{{#if claude,grok}}
`apps_deploy` builds the app's **current source on Whop** and ships it, so deploying
an app Whop already holds needs nothing local. Only one deployment runs per app at a
time; calling it again reports the running one instead of starting a second, and
calling it with nothing to publish says so. Pass `draft: true` to upload without
making it live.

{{/if}}
{{#if openai}}
`apps_deploy` needs a signed-in whop.com session and fails on this connection, so do
not offer it. To publish a site Whop holds, promote one of its builds
(`app-builds_list`, then `app-builds_promote` after a yes). If it has no build, the
user publishes from the Whop dashboard.

To ship code that only exists on this machine, do the local half yourself and the
rest over MCP: write and build the files with your own tools, pack them as a `.zip`
with `manifest.json` at its root (the layout is in
[references/websites.md](references/websites.md), and any other archive uploads fine
but serves only errors), upload it (`files_create`, then PUT the bytes to its `upload_url` with its
`upload_headers`, then `files_get` until `upload_status` is `ready`; `files_complete`
is only for a multipart upload), register it with `app-builds_create`, then
`app-builds_promote` it once the user says yes. Do not tell the user to install a
CLI for this.

The local half needs a workspace where you can write, build, and upload files, such
as Codex. In a ChatGPT conversation without one, publish only a build Whop already
holds. A new app from `apps_create` holds no source, so there do not create an app to
start a new site: say the site has to be built in Codex or in the Whop dashboard, then
offer to publish it and connect or buy its domain here.
{{else}}
To ship code that only exists on this machine, do the local half yourself and the
rest over MCP: write and build the files with your own tools, upload the artifact
with `files_create` / `files_complete`, register it with `app-builds_create`, then
`app-builds_promote`. Do not tell the user to install a CLI for this.
{{/if}}

## Working agreement

{{#if claude}}
- **Confirm before anything spends money or goes live.** Before launching or
  unpausing an ad campaign, raising a budget, retrying an ad payment, deploying or
  promoting a site build (anything but `draft: true`), or charging a customer, say
  what will happen and what it costs, and wait for the user to say yes. Drafts,
  previews, and reads need no confirmation.
{{#elif openai}}
- **Say what it costs and get a yes before anything that costs money.** That
  covers launching or unpausing an ad campaign, ad group, or ad; adding an ad group
  or ad to a campaign that is not a draft; duplicating an ad group or ad (copies
  keep the source's status); raising a budget; retrying an ads
  payment; generating an AI image or video; buying a domain; and starting a company
  formation. Say what you know, never estimate:
  - ads: the budget the user set, in USD, daily or lifetime;
  - an ads payment retry: it charges the account's unpaid ad spend, and no tool shows
    that amount, so say so and do not quote `spend` as the charge. Once it succeeds,
    campaigns set to `active` can start spending again at their budgets;
  - a domain: `availability.price` and `renewal_price` from `domains_get` with the
    hostname, before you create it;
  - AI media: it bills the Whop balance when the call goes through, and Whop sets the
    charge. `amount_charged` in the response is the actual charge, so tell the user
    that figure afterwards;
  - a formation: $500 for the first year and $100 a year after, at today's price. The
    call returns `checkout_url` and the exact `total` (USD cents), and nothing is
    charged until the user pays on that page.
- **Confirm before any write that goes live, affects other people, or cannot be
  undone.** That means anything customers, members, team members, or affiliates
  will see or feel, any money-related setting, revoking access, and deleting
  anything. Say what will happen and wait for the user to say yes. For example:
  - promoting a site build;
  - publishing or unpublishing a product, creating or changing a price customers
    can see, or creating a checkout link;
  - editing a live ad, or creating or connecting an external account
    (`external-accounts_create`, `external-accounts_connect`);
  - sending a message or a reply to customers, or submitting dispute evidence;
  - denying a Resolution Center case (`resolution-center-cases_deny` closes it with
    no refund) or a waitlist entry (`waitlist-entries_deny`);
  - cancelling, pausing, resuming, or transferring a membership
    (`memberships_resume` restarts billing on the customer's saved payment method);
  - payment rules: they can be read here, but this connection can't change them
    (`payment-rules_create` and the other writes fail with `missing_scope`), so send
    changes to the Whop dashboard instead of asking for a yes;
  - promo codes, affiliate commissions, starting or ending an experiment, and
    removing a team member (`team-members_delete`; this connection can remove only
    `workforce` members, so send any other removal to the Whop dashboard instead of
    asking for a yes);
  - adding or changing a shipment's tracking (`shipments_create`,
    `shipments_update`): use only a real tracking number the user gave, and say that
    on some stores a shipped status releases funds held until shipping;
  - changing account settings or store policies (`accounts_update`), or creating a
    business (`accounts_create`).

  Reads, ad drafts that launch nothing, and internal member notes
  (`members_notes_create`, visible only to the business's team) need no
  confirmation.
- **Get the yes before the call, in this conversation.** Write tools act on the first
  call, so never call one to see a preview. Say what will happen, wait for an explicit
  yes, then call the tool once. Earlier approval, approval of a different action, or
  "standing permission" does not count.
- **Retrying a write.** If a call times out or fails with no clear answer, it may have
  gone through. Where the tool offers `idempotency_key`, pass one on the first call and
  retry only with the same key and the same arguments. A 409 on that key means the
  outcome isn't known yet: check the result and tell the user instead of switching
  keys. An error that names a rule or field is final and replays for that key, so the
  next try takes a new key. Where the tool offers no key, check the result and ask
  before calling again.
- **Off-limits, even though the tool exists.**
  - `accounts_update` and `accounts_create`: set only the fields the user asked
    for. A new business starts with Dispute Fighter on. That is Whop's default, not
    something you set. Before creating one, say so, say Whop takes a success fee on
    disputes it wins, and say they can turn it off here or in their Whop dashboard.
    Never turn on Dispute Fighter (`dispute_fighter_enabled`, a success fee),
    Whop partner mode (`whop_partner_enabled`), or payment orchestration
    (`orchestration_enabled`), never set `affiliate_code`, and never enter tax ID
    numbers (`tax_identifiers`).
  - `checkout-configurations_create`: always `mode: "payment"`, never `setup`.
  - Do not enroll the user in Whop's partner program (`partners_create`,
    `partner-referral-requests_create`) or set affiliate commissions
    (`affiliates_create-override`, `affiliates_update-override`) unless they ask
    for exactly that, and confirm first.

  Except where a line says "unless they ask", these are limits of this plugin, not
  defaults: if the user asks for one, say it is not available here and that they can
  do it in their Whop dashboard. Anywhere else this skill sets a default or a choice,
  the user's explicit instruction wins.
- **Show only what was asked.** Do not print customers' email addresses, phone
  numbers, postal addresses, IP addresses, or payment details unless the user asks
  for that field for a specific customer. Summarize instead of dumping records: a
  name or username, a date, an amount, and a status are usually enough.
- **Do not upsell Whop.** Do not recommend or promote Whop's paid features,
  services, or upgrades. Start a paid Whop service (a company formation, a domain,
  AI media, ad spend) only when the user asks for that exact thing.
- **Hand-offs stay neutral.** When something is not available here, say so and that
  the user can do it in their Whop dashboard. Do not link to a withdrawal, deposit,
  or payout page.
- **Action links are for the user, not for you.** When a response carries
  `authorize_url`, an export's `download_url`, the one-use `url` from
  `memberships_transfer`, or a formation signing `url` (under
  `company_formation.signatures`), give the link to the user and say what it does:
  a transfer URL gives the membership to whoever opens it, an export link downloads
  customer data, and a signing link is for the founder to sign an IRS form. Do not
  fetch or open it to "verify" — that does not complete the flow and can consume a
  single-use URL. Re-run the matching `get`/`list` afterwards to confirm the outcome.
- **Checkout links are for the user's customers.** A `purchase_url` from a checkout
  configuration or a variant is the link the user shares with their buyers. Hand it
  over as that, never as something for the user to buy, and never open it yourself.
- **Payment pages for what the user asked to buy are theirs.** The `checkout_url`
  from `accounts_form_company` and a domain's `purchase_url` are where the user pays
  Whop for the formation or domain they asked for. Give the link with the total and
  say the order completes once they pay there. Never open it yourself.
{{/if}}
{{#if openai}}
- **Live site addresses.** An app's addresses are in `domains` on `apps_get`: its
  whop.site address and any custom domain, each with a `status`. Show the `ready`
  ones as `https://<domain>`; any other status means that address is not live yet
  (`pending` is still being set up).
  `hosted_url` is deprecated and can be null. None of these are action links.
- **Identity data only for formation.** Founder details (home address, date of
  birth) are only for a company formation the user asked for; follow
  [references/formation.md](references/formation.md). Never ask for an SSN. Never ask for, accept, or
  pass on payment card or bank account numbers, passwords, API keys, one-time
  codes, or a domain transfer (EPP) code. If the user offers one, do not repeat it
  or send it to a tool, and ask them not to share it here.
- **Pass `intent` only if the tool lists it.** If a tool's schema has `intent` or
  `intent_id`, the server sends them to Whop with the request. Write `intent` as a
  one-line summary of the task, not a copy of the user's message, and never put an
  SSN, date of birth, card or bank number, password, API key, or code in it. If the
  schema doesn't list them, leave them out, or the call fails.
{{else}}
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
{{/if}}

## What these tools cannot reach

{{#if claude}}
This connection deliberately leaves out AI media generation and anything that moves
money out of the account: payouts, transfers, bounty rewards, card issuing, balance
top-ups, and trading. If the user asks for one of those, say it is not available
here and send them to whop.com to do it themselves. Do not look for a workaround.

Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are also absent. Send the user to whop.com
for those.
{{#elif openai}}
This connection works on the user's own Whop business and deliberately leaves out
payouts, transfers, deposits and balance top-ups, cards, crypto swaps and trades,
issuing refunds, one-off charges to a customer's saved payment method, creating or
changing invoices, and fee changes. It also leaves out identity verification,
setting up ad billing, API keys, and webhooks. Existing invoices and refund history
can still be looked up.
Resuming a paused membership restarts its scheduled billing, so get a yes first.

If the user asks for one of those, say it is not available in this plugin and that
they can do it in their Whop dashboard. Do not link to the page for it, and do not
look for a workaround. If a tool you expect is not in your tool list, it is not
available on this connection, and no other tool should be used to get the same
effect: for example, when the user asks for a refund, do not accept, deny, or open
a Resolution Center case instead.

Passkeys and connected OAuth apps need a first-party whop.com browser session and
are also absent. The user manages them in their Whop account settings.

`notifications_create` is listed but fails on this connection, because only an app's
own API key can send one. Do not offer it.
{{else}}
Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are deliberately absent. Send the user to
whop.com for those; no tool and no CLI will do it.
{{/if}}

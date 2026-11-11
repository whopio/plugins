---
name: whop
description: "Start here for work on the user's Whop business through the Whop MCP tools: checks the connection, picks the business, and points to the right Whop skill. Use when the user mentions Whop or whop.com, asks which Whop businesses they have, wants to create a business, or asks for something in their Whop account that no other Whop skill covers."
---

# Whop

This plugin connects {{CLIENT_NAME}} to a live Whop business through the Whop MCP
server. The tools act on the user's real account. No CLI and no API key are needed.

## Before anything else

1. **Check the connection.** Call `connection_status`. It returns the signed-in
   identity, the selected account, the granted scopes and the tool coverage. If it
   fails or no Whop tools are loaded, the user has not signed in: ask them to
   connect with {{CONNECT_COMMAND}}.
2. **Pick the business.** `connection_status` often returns a null `account_id`,
   because a sign-in is not tied to one business. Call `accounts_list`, and pass the
   chosen `account_id` (`biz_…`) on every call that accepts it. Several businesses:
   ask which one. Never assume a default.
3. **Fill the two tracking fields.** Most tools require `intent` and `intent_id`.
   `intent` is the user's request, copied word for word. `intent_id` is a UUID you
   generate once per user message and reuse for every call made for that message.

## How the tools are laid out

The server lists its most-used tools by name, such as `payments_list` and
`products_create`. Everything else Whop can do is still available, but not listed:
find it with `search_operations` and run it with `call_read_operation` or
`call_write_operation`. So a tool missing from the list does not mean Whop cannot do
the job. The `whop-docs-and-operations` skill covers this.

Tool names follow `<group>_<operation>`, with hyphens inside a multi-word group
(`support-channels_list`). Read a tool's schema before calling it. Never invent a
tool name, a field or an enum value.

## Which skill to load

| The user wants to | Skill | Listed tools |
| --- | --- | --- |
| See sales, refund a payment, check disputes | `whop-payments` | `payments_*`, `refunds_list`, `disputes_list`, `resolution-center-cases_list` |
| Create or change products, prices, promo codes, checkout links | `whop-products` | `products_*`, `variants_*`, `promo-codes_create` |
| Look up customers, check or cancel a membership | `whop-customers` | `members_list`, `memberships_*`, `events_list` |
| Build or edit a course, upload a file | `whop-courses` | `experiences_*`, `courses_create`, `course-chapters_*`, `course-lessons_*`, `files_*` |
| Read or answer chats, DMs, support, forum posts | `whop-community` | `messages_*`, `dm-channels_list`, `support-channels_list`, `forum-posts_*` |
| See revenue and other metrics over time | `whop-stats` | `stats_time-series_get` |
| Read the Whop docs, or do anything not listed above (websites, ads, forming a company, webhooks, invoices and more) | `whop-docs-and-operations` | `docs_search`, `docs_query`, `search_operations`, `describe_operation`, `call_read_operation`, `call_write_operation` |

Three listed tools belong to no other skill:

- `accounts_list` and `accounts_get` read the businesses the user can act on.
- `accounts_create` sets up a new business owned by the signed-in user. Tax details
  are added afterwards, not at creation.
- `bounties_list` shows paid clipping and content work the user can see.

`search` and `fetch` do a keyword lookup across products, prices, payments and
members and return one record by id. Prefer the specific list tool with `account_id`
when you know what you are looking for.

## Working agreement

{{#if claude}}
- **Confirm before anything spends money or goes live.** Before launching or
  unpausing an ad campaign, raising a budget, retrying an ad payment, deploying or
  promoting a site build (anything but `draft: true`), or charging a customer, say
  what will happen and what it costs, and wait for the user to say yes. Drafts,
  previews, and reads need no confirmation.
{{/if}}
- **Confirm before anything a customer feels.** A refund, a cancelled membership, a
  price change and a sent message reach real people and are hard to take back. Say
  exactly what will happen and wait for a yes. Each skill names its own cases.
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

## Errors

A failed call returns `isError: true` with `{ "error": { "code", "message" } }`.

| Code | Meaning | What to do |
| --- | --- | --- |
| `not_authenticated` | The user is not signed in | Ask them to connect with {{CONNECT_COMMAND}} |
| `account_required` | The tool needs a business | Pass `account_id` from `accounts_list` |
| `missing_scope` | The sign-in lacks a permission | Say which action is not permitted; signing in again may grant it |
| `invalid_input` | An argument is missing or wrong | Re-read the schema and correct it |
| `tool_not_found` | No such tool or operation on this connection | Look for it with `search_operations` |
| `upstream_error` | Whop refused the call | Follow the message; status 429 means wait and retry |
| `timeout` | Whop did not answer in time | Read the record back before retrying a write |

After a write whose result is unclear, read the record back before trying again.
Writes that accept `idempotency_key` replay the first result when the same key is
sent again, so reuse the key on a retry. `messages_create` and `forum-posts_create`
take no key: a repeated call sends or posts a second time.

## What these tools cannot reach

{{#if claude}}
This connection deliberately leaves out AI media generation and anything that moves
money out of the account: payouts, transfers, bounty rewards, card issuing, balance
top-ups, and trading. If the user asks for one of those, say it is not available
here and send them to whop.com to do it themselves. Do not look for a workaround.

Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are also absent. Send the user to whop.com
for those.
{{/if}}
{{#if grok}}
Passkeys and OAuth grants (`users_me_passkeys*`, `users_me_oauth_grants*`) need a
first-party whop.com browser session and are deliberately absent. Send the user to
whop.com for those; no tool and no CLI will do it.
{{/if}}

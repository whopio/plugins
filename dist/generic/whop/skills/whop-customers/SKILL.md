---
name: whop-customers
description: "Look up the customers of a Whop business and manage their access through the Whop MCP tools: list members, check a membership by id or license key, cancel a membership, and see what a person did (visits, checkouts, purchases). Use when the user asks who their Whop customers are, whether someone is still a member, to cancel a customer's membership, or to trace one buyer's activity. Not for refunds (whop-payments) or messaging customers (whop-community)."
---

# Whop customers and memberships

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Words

- A **member** is one buyer's relationship with a business, however many things
  they bought.
- A **membership** is the access one purchase gives. One member can hold several.

## Tools

| Tool | Use it to |
| --- | --- |
| `members_list` | See everyone who has bought from a business |
| `memberships_list` | See memberships and their status |
| `memberships_get` | Check one membership by its id or license key |
| `memberships_cancel` | Cancel a customer's membership |
| `events_list` | See what people did: visits, checkouts, purchases |

## Finding people

- `members_list` takes `account_id` and a `query` to search.
- `memberships_list` filters by `account_id`, `product_id`, `user_id` and status. An
  `account_id` or `user_id` outside the user's reach returns fewer results, not an
  error, so an empty list does not prove the person was never a customer. Check the
  id first.
- For "is this person still a member?", list their memberships and read the status.

Member records hold contact details. Show only what the user asked for.

## Cancelling a membership

`memberships_cancel` takes the membership `id` (`mem_…`).

- `cancel_at_period_end: true` stops renewal and keeps access until the current
  billing period ends.
- Leaving it out, or `false`, **removes access immediately**.

Ask the user which of the two they want before calling it, name the customer and
the product, and wait for a yes. If the user also wants the customer's money back,
that is a separate refund in `whop-payments`.

## One person's activity

`events_list` with `identifier` returns one person's journey. The identifier can be
a person id (`prsn_…`), a user id, an email or a phone number. Without `identifier`
it lists a business's events, and then `from` and `to` are required as ISO 8601
timestamps. Pass `account_id` when the user has more than one business.

## Not listed here

Pausing, resuming, extending or transferring a membership, applying a promo code to
one, and notes on a member are reached through `search_operations`.

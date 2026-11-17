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

- A member, a membership and a payment are three records. Check the one the
  question is about instead of inferring it from another: an active member can hold
  a canceled membership, and a paid payment does not prove current access.
- To go from an email to memberships, search `members_list` with the email as
  `query`, take the user id from the match, then call `memberships_list` with that
  `user_id`. Check canceled and expired statuses too when looking for a past
  customer.

Member records hold contact details. Show only what the user asked for.

## Cancelling a membership

`memberships_cancel` takes the membership `id` (`mem_…`).

- `cancel_at_period_end: true` stops renewal and keeps access until the current
  billing period ends.
- Leaving it out, or `false`, **removes access immediately**.

Ask the user which of the two they want before calling it, name the customer and
the product, and wait for a yes. If the user also wants the customer's money back,
that is a separate refund in `whop-payments`.

## Bringing a membership back

Which of these applies depends on the membership's status and whether its price is
recurring, so call `memberships_get` first.

| Situation | What works |
| --- | --- |
| Set to cancel, paid period still running | Undo the cancellation: `cancel_at_period_end: false` |
| Recurring membership already ended | Nothing restores it. The customer buys again through a checkout link |
| One-time purchase, `canceled` or `expired` | Reactivate it. `days` (1 to 1095) sets how long access lasts from now; leave it out for lifetime access or to keep an expiry that is still ahead |
| Past due | Adding free days only moves the next renewal date. The membership stays past due and access does not come back until the renewal is paid. See "Failed renewals" in `whop-payments` |
| Billing should stop for a while | Pause it, with `until` for a set end date, and resume it later |

Reactivating refuses a subscription, and extending fails on a canceled or expired
membership. Never tell a customer that free days restored their access.

`memberships_pause` and `memberships_resume` are listed. Undoing a cancellation,
reactivating and adding free days are not available on this connection; the user
does those from their Whop dashboard.

## One person's activity

`events_list` with `identifier` returns one person's journey. The identifier can be
a person id (`prsn_…`), a user id, an email or a phone number. Without `identifier`
it lists a business's events, and then `from` and `to` are required as ISO 8601
timestamps. Pass `account_id` when the user has more than one business.

## Not listed here

These are listed too: `members_get`, `members_logs`, `members_notes_list`,
`members_notes_create`, `memberships_pause`, `memberships_resume` and
`memberships_transfer`. Pausing, resuming and transferring
change a customer's access, so confirm first. Extending a membership and applying a
promo code to one are not available on this connection.

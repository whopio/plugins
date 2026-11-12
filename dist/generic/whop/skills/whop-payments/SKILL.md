---
name: whop-payments
description: "See and manage money coming into a Whop business through the Whop MCP tools: list sales and payments, look up one payment, refund all or part of it, and check refunds, disputes (chargebacks) and Resolution Center cases. Use when the user asks about their Whop sales, a customer's charge, a failed payment, issuing a refund, a chargeback, or a buyer complaint. Not for revenue trends over time (whop-stats) or for creating products and prices (whop-products)."
---

# Whop payments, refunds and disputes

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Tools

| Tool | Use it to |
| --- | --- |
| `payments_list` | See sales, newest first: who paid, how much, when, and the status |
| `payments_get` | Look up one payment with every item bought |
| `refunds_list` | See refunds already issued |
| `payments_refund` | Refund all or part of a payment |
| `disputes_list` | See chargebacks and disputes opened against payments |
| `resolution-center-cases_list` | See buyer complaints and refund requests |

## Finding payments

- `payments_list` covers **every business the user can read** unless you pass
  `account_id`. When the user names a business, pass its `account_id` together
  with any `query`: a search by email or name alone also returns that person's
  payments at the user's other businesses.
- `query` searches by payment id, dispute id, user id, membership id, email, name or
  username. Searching by email needs the `member:email:read` permission.
- `status` narrows to one state, such as `paid`. Read the schema for the values.
- `mode: "user_sales"` returns sales the signed-in user received personally, outside
  any business. It cannot be combined with `account_id`.
- The listing leaves some optional inputs out to stay small. Call
  `describe_operation` with `payments_list` to see every filter; the tool accepts
  all of them.
- `payments_get` returns related records as ids. Look each one up with its own tool
  (`memberships_get`, `variants_get`).

For totals and trends, do not add up pages of `payments_list`. Use `whop-stats`.

## Refunding

`payments_refund` takes the payment `id` (`pay_…`).

- Leave `partial_amount` out to refund everything still refundable.
- `partial_amount` is in the payment's own currency, written like its other amounts.
- The refund goes back through the processor that charged it. The buyer is emailed,
  the membership is updated to match, the affiliate commission on the payment is
  clawed back, and any open Resolution Center case on it is closed.

Before calling it, tell the user the payment, the buyer, the amount and those
effects, and wait for a yes. A refund cannot be undone from here.

Pass an `idempotency_key`. If the result is unclear, check `refunds_list` with the
`payment_id` before trying again, and reuse the same key.

`refunds_list` filters by exactly one of `payment_id`, `account_id` or `user_id`.
They cannot be combined.

## Disputes and buyer complaints

`disputes_list` and `resolution-center-cases_list` only read. Without `account_id`,
the cases list also includes cases the user opened as a buyer, so pass `account_id`
for a business's cases.

Responding is not a listed tool. Find the operation with `search_operations`, for
example "submit dispute evidence" or "reply to a resolution center case", then run
it as the `whop-docs-and-operations` skill describes. Confirm with the user before
either of these:

- Accepting a dispute concedes it to the customer. It is final and cannot be
  contested afterwards.
- Accepting a Resolution Center case refunds the payment in full and closes it.

## Not listed here

Invoices, retrying or voiding a payment, and payment summaries are reached through
`search_operations`. Checkout links are in `whop-products`.

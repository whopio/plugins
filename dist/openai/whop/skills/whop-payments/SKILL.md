---
name: whop-payments
description: "See money coming into a Whop business through the Whop MCP tools: list sales and payments, look up one payment, and check refunds, disputes (chargebacks) and Resolution Center cases. Use when the user asks about their Whop sales, a customer's charge, a failed payment, a refund, a chargeback, or a buyer complaint. Not for revenue trends over time (whop-stats) or for creating products and prices (whop-products)."
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
- `payments_get` returns related records as ids. Look each one up with its own tool
  (`memberships_get`, `variants_get`).

For totals and trends, do not add up pages of `payments_list`. Use `whop-stats`.

## Refunding

This connection cannot issue a refund. If the user asks for one, say so and tell
them to refund the payment from their Whop dashboard. Do not look for a workaround.
You can still show what was already refunded with `refunds_list`.

`refunds_list` filters by exactly one of `payment_id`, `account_id` or `user_id`.
They cannot be combined.

## Disputes and buyer complaints

`disputes_list` and `resolution-center-cases_list` only read. Without `account_id`,
the cases list also includes cases the user opened as a buyer, so pass `account_id`
for a business's cases.

To respond, read the record with `disputes_get` or `resolution-center-cases_get`
first. Fight a dispute with `disputes_upload_evidence`, then `disputes_submit`.
Answer a case with `resolution-center-cases_reply`, `resolution-center-cases_request_info`
or `resolution-center-cases_deny`. Show the user what you will send and wait for a
yes: submitted evidence is locked, and a reply goes to the buyer.

This connection cannot accept a dispute or a case, because accepting returns the
buyer's money. Send the user to their Whop dashboard for that.

## Not listed here

`payments_summary` and `disputes_summary` give totals, `payments_fees` shows the
fees on a payment, and `invoices_list` and `invoices_get` read invoices. Creating an
invoice and retrying or voiding a payment are not available on this connection.
Checkout links are in `whop-products`.

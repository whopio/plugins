---
name: whop-payments
{{#if claude,grok}}
description: "See and manage money coming into a Whop business through the Whop MCP tools: list sales and payments, look up one payment, refund all or part of it, and check refunds, disputes (chargebacks) and Resolution Center cases. Use when the user asks about their Whop sales, a customer's charge, a failed payment, issuing a refund, a chargeback, or a buyer complaint. Not for revenue trends over time (whop-stats) or for creating products and prices (whop-products)."
{{else}}
description: "See money coming into a Whop business through the Whop MCP tools: list sales and payments, look up one payment, and check refunds, disputes (chargebacks) and Resolution Center cases. Use when the user asks about their Whop sales, a customer's charge, a failed payment, a refund, a chargeback, or a buyer complaint. Not for revenue trends over time (whop-stats) or for creating products and prices (whop-products)."
{{/if}}
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
{{#if claude,grok}}
| `payments_refund` | Refund all or part of a payment |
{{/if}}
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
{{#if claude,grok}}
- The listing leaves some optional inputs out to stay small. Call
  `describe_operation` with `payments_list` to see every filter; the tool accepts
  all of them.
{{/if}}
- `payments_get` returns related records as ids. Look each one up with its own tool
  (`memberships_get`, `variants_get`).

For totals and trends, do not add up pages of `payments_list`. Use `whop-stats`.

## Refunding

{{#if claude,grok}}
`payments_refund` takes the payment `id` (`pay_…`).

- Leave `partial_amount` out to refund everything still refundable.
- `partial_amount` is in the payment's own currency, written like its other amounts.
- The refund goes back through the processor that charged it. The buyer is emailed,
  the membership is updated to match, the affiliate commission on the payment is
  clawed back, and any open Resolution Center case on it is closed.

Before calling it, tell the user the payment, the buyer, the amount and those
effects, and wait for a yes. A refund cannot be undone from here.

Read the payment first. When it shows `refundable: false`, Whop will not refund it
from here: say so, and that the reason is not given, instead of trying.

A refund is paid out of the business's balance in the payment's currency: its
available and pending money, never its reserve. Read that balance with
`accounts_get` first.

- If the balance covers the payment, refund it whole.
- If it covers only part, tell the user the most that can be refunded now and offer
  that as a `partial_amount`. The rest waits until more money settles or comes in.
- If it is zero or less, say nothing can be refunded yet.
- If a refund fails for lack of funds, do not retry the same amount. The available
  figure can include money on a Whop Card that a refund cannot use.

Pass an `idempotency_key`. If the result is unclear, check `refunds_list` with the
`payment_id` before trying again, and reuse the same key.
{{else}}
This connection cannot issue a refund. If the user asks for one, say so and tell
them to refund the payment from their Whop dashboard. Do not look for a workaround.
You can still show what was already refunded with `refunds_list`.
{{/if}}

`refunds_list` filters by exactly one of `payment_id`, `account_id` or `user_id`.
They cannot be combined.

## Failed renewals

A renewal that fails moves the membership to `past_due`. Find the failed payment
with `payments_list` and the `membership_id`.

- Whop retries by itself: up to 3 attempts in all, or up to 7 when the card lacked
  funds, within 14 days of the first attempt. Some declines are never retried.
- For when the next attempt happens, give only that payment's
  `next_payment_attempt_at`. When it is null, no automatic retry is coming.
- While past due, the member has no access, unless the business turned on **Keep
  access while past due** or the membership is billed by invoice.
- When the attempts run out the membership is canceled, unless the business turned
  off **Cancel subscriptions after failed payments**. Both settings are in the Whop
  dashboard under Settings → Checkout → Subscriptions. Turning the second one off
  does not bring back memberships already canceled.
- A canceled subscription cannot be retried, extended or reactivated. The customer
  buys again through a checkout link.
- The customer can pay sooner by choosing a different card on their own Whop
  orders page; switching cards retries the renewal at once.

{{#if claude,grok}}
The user can retry a failed payment by hand once, when the payment shows
`retryable: true` and the membership is active, trialing or past due. That is the
`payments_retry` operation, run through `call_write_operation`. It charges the
customer's card, so name the customer and the amount and wait for a yes. Read the
payment back afterwards. An unclear error does not prove nothing was charged.
{{/if}}
{{#if openai}}
This connection cannot retry a payment. The user retries it from their Whop
dashboard.
{{/if}}

## Disputes and buyer complaints

`disputes_list` and `resolution-center-cases_list` only read. Without `account_id`,
the cases list also includes cases the user opened as a buyer, so pass `account_id`
for a business's cases.

{{#if claude,grok}}
Responding is not a listed tool. Find the operation with `search_operations`, for
example "submit dispute evidence" or "reply to a resolution center case", then run
it as the `whop-docs-and-operations` skill describes. Confirm with the user before
either of these:

- Accepting a dispute concedes it to the customer. It is final and cannot be
  contested afterwards.
- Accepting a Resolution Center case refunds the payment in full and closes it.
{{/if}}
{{#if openai}}
To respond, read the record with `disputes_get` or `resolution-center-cases_get`
first. Fight a dispute with `disputes_upload_evidence`, then `disputes_submit`.
Answer a case with `resolution-center-cases_reply`, `resolution-center-cases_request_info`
or `resolution-center-cases_deny`. Show the user what you will send and wait for a
yes: submitted evidence is locked, and a reply goes to the buyer.

This connection cannot accept a dispute or a case, because accepting returns the
buyer's money. Send the user to their Whop dashboard for that.
{{/if}}

## Not listed here

{{#if claude,grok}}
Invoices, retrying or voiding a payment, and payment summaries are reached through
`search_operations`. Checkout links are in `whop-products`.
{{/if}}
{{#if openai}}
`payments_summary` and `disputes_summary` give totals, `payments_fees` shows the
fees on a payment, and `invoices_list` and `invoices_get` read invoices. Creating an
invoice and retrying or voiding a payment are not available on this connection.
Checkout links are in `whop-products`.
{{/if}}

---
name: whop-products
description: "Create and change what a Whop business sells through the Whop MCP tools: products, their prices (variants), promo codes and checkout links. Use when the user wants to sell something on Whop, add or change a price, make a subscription or one-time offer, create a discount code, or get a checkout link. Not for looking at sales (whop-payments) or building the course or community a product gives access to (whop-courses, whop-community)."
---

# Whop products, prices and promo codes

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Words

- A **product** is the thing for sale. Whop also calls it a "whop".
- A **variant** is one price of a product: the amount and how it bills. Older Whop
  material calls this a "plan". Use the `variants_*` tools; the older plan tools
  are deprecated.

## Tools

| Tool | Use it to |
| --- | --- |
| `products_list` | See a business's products |
| `products_get` | Look up one product |
| `products_create` | Set up something new to sell |
| `products_update` | Change a product's name, description, visibility or settings |
| `variants_list` | See the prices a product is sold at |
| `variants_get` | Look up one price |
| `variants_create` | Add a price to a product |
| `variants_update` | Change a price, billing interval, stock or visibility |
| `promo-codes_create` | Create a discount code |

`products_list` **without `account_id` searches the public Whop marketplace**, not
the user's store. Always pass `account_id` to see their own products.

## Selling something new

1. `products_create` with `title` (80 characters at most) and `account_id`.
2. `variants_create` with the new `product_id` and `account_id`. A signed-in user
   must pass `account_id` here.
   - `billing_type` is `one_time` or `renewal`.
   - For a one-time price, `initial_price` is the amount. For a recurring price,
     `renewal_price` is the charge each period and `initial_price` is an extra
     one-off fee **added to** the first charge. A plain $20 a month is
     `renewal_price: 20` with `initial_price: 0`; setting both to 20 charges $40 at
     checkout.
   - `billing_period` is the interval in **days**: 30 for monthly, 365 for annual.
   - Amounts are written in the currency itself: `10.43` means $10.43, not cents. A
     paid price is at least `1.00`; use `0` for free. `currency` defaults to USD.
   - `trial_period_days` adds a free trial before the first renewal charge. Any
     `initial_price` is still charged at checkout.
3. Give the user the checkout link. The new variant comes back with a
   `purchase_url`: that is the link to send customers to. Nobody is charged until a
   customer checks out. The variant's id starts with `plan_`, Whop's older name
   for a price.
   Create a separate checkout link with `checkout-configurations_create` only when
   the user wants one with its own settings, such as a redirect after purchase or
   an affiliate code.


Ask the user for anything they have not told you, such as the price, the billing
interval and whether the product should be visible yet. Do not pick values for them.

## Changing what customers see

`products_update` and `variants_update` change the live store page and what
customers pay. Before changing a price, a billing interval, stock or visibility,
tell the user the old and new values and wait for a yes.

## Raising or changing a recurring price

`renewal_price`, `billing_period` and `currency` cannot be edited once a variant
has a member or a payment: the update is refused, so do not try it to find out.
`initial_price` can be edited in place and affects only new buyers.

To change what new buyers pay each period:

1. Create a new variant under the same product with the new price, copying the old
   variant's other settings.
2. Set the old variant's `visibility` to `archived` with `variants_update`.

Tell the user what this means before doing either step, and wait for their choice:

- Members on the old variant keep access and keep renewing at the old price.
- The old checkout link then shows "No longer available". Nothing redirects it, so
  the user swaps in the new variant's link wherever the old one is shared.
- A variant left visible or `hidden` still sells through its link at the old price.
  One link cannot both keep working and charge the new price.
- Moving existing members to the new price is done one member at a time in the Whop
  dashboard. No tool here changes a member's price, and there is no bulk option.

## Checkout questions

- **A "Save X%" badge, crossed-out price or "Offer ends soon" banner** that no promo
  code explains comes from the product's **Show discount** setting. It changes only
  what the page shows; buyers pay the variant's price. The user turns it off by
  editing the product in the dashboard, under **Growth tools**.
- **"You can only purchase one per order"** means `allow_multiple_quantity` is off
  on that variant, which is the default. `variants_update` turns it on, for one-time
  prices only.
- **The first charge was higher than the monthly price.** Read the variant: an
  `initial_price` above 0 is added to the first `renewal_price`.
- **An enabled payment method is missing at checkout.** It shows only when it fits
  the price, the buyer and the kind of checkout:
  - Recurring prices show only methods that can be saved for renewals. Klarna,
    Bancontact, Pix, boleto, OXXO, SPEI, PSE, Nequi, AlipayHK and WeChat Pay are
    one-time only.
  - iDEAL appears only in the checkout opened from the store or product page, never
    on a direct `whop.com/checkout/plan_…` link or an embedded checkout.
  - SEPA Direct Debit reads "Not yet available" until the business has $1,000 in
    membership earnings.
  - Bank Wire needs a US buyer, a one-time USD price with unlimited stock, and a
    verified identity with a payout account that accepts wires.
  - Affirm is not offered at Whop checkout.
  - A financing limit depends on the buyer's country, not only the currency.

  Read the variant with `variants_get` before answering, and ask which price the
  buyer used if the product has several.

## Promo codes

`promo-codes_create` requires `code`, `promo_type` (`percentage` or `flat_amount`),
`amount_off`, `base_currency`, `promo_duration_months` and `new_users_only`. It can
be limited with `product_id`, `variant_ids`, `stock`, `expires_at` and
`one_per_customer`.

Its schema carries no field descriptions. Ask the user for each required value, and
look up anything unclear with `docs_search` instead of guessing.

- Settle the terms that change the offer: which products or prices, the amount, how
  many times it can be used, when it ends, and whether it discounts only the first
  payment or later renewals too (`promo_duration_months`).
- A `flat_amount` code is in one currency. Check it matches the price's currency.
- List the existing codes before creating one, so you do not make a duplicate.
- Afterwards, read back the limits the response shows. A code existing does not
  mean it applies to every product or every renewal.

## Not listed here

These are listed too: `products_publish`, `products_unpublish`, `products_delete`,
`variants_delete`, `promo-codes_list`, `promo-codes_get`, `promo-codes_activate`,
`promo-codes_deactivate`, `promo-codes_delete`, and `checkout-configurations_list`.
Deleting cannot be undone, so confirm first.

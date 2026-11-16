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
   - `initial_price` is the first charge. `renewal_price` is the charge each period
     for a recurring price.
   - `billing_period` is the interval in **days**: 30 for monthly, 365 for annual.
   - Amounts are written in the currency itself: `10.43` means $10.43, not cents. A
     paid price is at least `1.00`; use `0` for free. `currency` defaults to USD.
   - `trial_period_days` adds a free trial before the first recurring charge.
3. Give the user the checkout link. The new variant comes back with a
   `purchase_url`: that is the link to send customers to. Nobody is charged until a
   customer checks out. The variant's id starts with `plan_`, Whop's older name
   for a price.
   Create a separate checkout link only when the user wants one with its own
   settings, such as a redirect after purchase or an affiliate code. That is not a
   listed tool: call `search_operations` with "create a checkout link" and run the
   match with `call_write_operation`.

`variants_create` and `variants_update` leave some optional inputs out of the
listing. Call `describe_operation` with the tool name to see all of them; the tool
accepts every one.

Ask the user for anything they have not told you, such as the price, the billing
interval and whether the product should be visible yet. Do not pick values for them.

## Changing what customers see

`products_update` and `variants_update` change the live store page and what
customers pay. Before changing a price, a billing interval, stock or visibility,
tell the user the old and new values and wait for a yes.

## Promo codes

`promo-codes_create` requires `code`, `promo_type` (`percentage` or `flat_amount`),
`amount_off`, `base_currency`, `promo_duration_months` and `new_users_only`. It can
be limited with `product_id`, `variant_ids`, `stock`, `expires_at` and
`one_per_customer`.

Its schema carries no field descriptions. Ask the user for each required value, and
look up anything unclear with `docs_search` instead of guessing.

## Not listed here

Publishing, unpublishing or deleting a product, deleting a price, and listing,
turning off or deleting promo codes are reached through `search_operations`.
Deleting cannot be undone, so confirm first.

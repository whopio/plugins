---
name: whop-stats
description: "Answer how a Whop business is doing through the Whop MCP tools: chart a metric such as revenue over a date range, break it down, and find totals. Use when the user asks about their Whop revenue, growth, trends, this month against last month, or any number over time. Not for finding one specific payment or customer (whop-payments, whop-customers)."
---

# Whop stats

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Tools

| Tool | Use it to |
| --- | --- |
| `stats_time-series_get` | Chart one metric over a date range, as points |

Two more are reached through the operation tools described in
`whop-docs-and-operations`:

- The list of metrics. Call `search_operations` with "list time series metrics" and
  run the match with `call_read_operation`. It returns every metric name, its unit,
  and the properties it can be filtered or broken down by.
- Reports, for a single total that is not split over time. Call `search_operations`
  with "list reports".

## Charting a metric

`stats_time-series_get` requires `metric`, `from` and `to`.

- **Do not guess the metric name.** The common ones are below. For anything else,
  or to see a metric's unit and breakdowns, get it from the list of metrics first.

  | Question | `metric` |
  | --- | --- |
  | Revenue | `gross_revenue` |
  | Revenue after refunds and fees | `net_revenue` |
  | Number of successful payments | `successful_payments` |
  | Amount refunded, refund rate | `total_refunded`, `refund_rate` |
  | Disputes, dispute rate | `disputes`, `dispute_rate` |
  | New customers | `new_users` |
  | Paying members right now | `paid_active_members` |
  | Members over time | `users_growth` |
  | Churn | `churn_rate` |
  | Trial conversion | `trial_conversion_rate` |
  | Fees | `payment_processing_fees`, `whop_processing_fees`, `marketplace_fees`, `affiliate_fees`, `dispute_fees`, `sales_tax_withheld` |
- `from` and `to` are a date (`YYYY-MM-DD`, covering the whole day) or an ISO 8601
  timestamp, used exactly.
- `interval` sets how wide each point is and defaults to `day`. The schema lists
  the other values. Use `day` for ranges under 90 days and `week` for longer ones,
  unless the user asks for a grouping.
- A range such as "last 7 days" ends today and includes today's unfinished data.
  On March 13 it is March 7 through March 13. Say so, or end it yesterday if the
  user wants completed days.
- Money comes back in the currency itself, not cents. Do not divide by 100.
- `time_zone` is an IANA name such as `America/New_York` and defaults to UTC. Ask
  for the user's time zone when "today" or "this week" matters.
- `account_id` picks the business. Pass it; a user can have several.
- `breakdown_by` splits each point by one property, such as `currency`.

The listing shows only the common inputs. Call `describe_operation` with
`stats_time-series_get` to see every filter; the tool accepts all of them.

## Answering well

- For "this month against last month", make two calls with matching ranges and say
  which dates each covers.
- Say the unit, the currency, the date range and the time zone with every number.
- For a total, use a report or a metric. Do not add up pages of `payments_list`: it
  is paged and covers every business the user can read unless narrowed.
- A specific sale or customer is not a stats question. Use `whop-payments` or
  `whop-customers`.
- Stats need the business's owner or a role that can read stats. If the call is
  refused for that reason, say so. Do not look for the number another way.
- Ad performance is not here. It is in the ads playbook in
  `whop-docs-and-operations`.

## Not listed here

Exports of raw data are reached through `search_operations` ("create an export").
One person's visits and purchases are in `events_list`, covered by
`whop-customers`.

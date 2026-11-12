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
| `stats_time-series_list` | List every metric, its unit, and the properties it can be filtered or broken down by |
| `stats_reports_list` | List the reports: single totals that are not split over time |

## Charting a metric

`stats_time-series_get` requires `metric`, `from` and `to`.

- **Do not guess the metric name.** Get it from the list of metrics first. Each
  metric sets its own unit and which breakdowns it allows.
- `from` and `to` are a date (`YYYY-MM-DD`, covering the whole day) or an ISO 8601
  timestamp, used exactly.
- `interval` sets how wide each point is and defaults to `day`. The schema lists
  the other values.
- `time_zone` is an IANA name such as `America/New_York` and defaults to UTC. Ask
  for the user's time zone when "today" or "this week" matters.
- `account_id` picks the business. Pass it; a user can have several.
- `breakdown_by` splits each point by one property, such as `currency`.


## Answering well

- For "this month against last month", make two calls with matching ranges and say
  which dates each covers.
- Say the unit, the currency, the date range and the time zone with every number.
- For a total, use a report or a metric. Do not add up pages of `payments_list`: it
  is paged and covers every business the user can read unless narrowed.
- A specific sale or customer is not a stats question. Use `whop-payments` or
  `whop-customers`.

## Not listed here

Start an export with `exports_create` only when the user asks for one, then poll
`exports_get` until it has a `download_url` and give that link to the user. The
`whop` skill lists the exports this connection cannot make.
One person's visits and purchases are in `events_list`, covered by
`whop-customers`.

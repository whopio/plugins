# Whop Ads

Read this before creating or launching ads. Enums and field lists live in each
tool's own schema — do not invent them. When a field here differs from the schema,
the schema wins.

Whop Ads runs the ads on Whop's own ad accounts and bills spend to the business's
ads payment method (its Whop balance or a card). Drafts cost nothing and need no
billing setup. Launching spends money, and these tools act on the first call. Before any
launch, unpause, or budget change, say what will happen, with the budget, and wait
for the user's yes. Then call the tool once.

## Before launching

- **Payment method.** Launching needs an ads payment method on the account. It is
  set in the user's Whop dashboard (Ads settings, Billing); this plugin cannot set
  it. If a launch fails with an error about an ads payment method, such as
  `Account must have an ads payment method configured`, keep the campaign as a draft
  and tell the user to add or update it there.
- **Destination.** A website ad needs a `url`. The business's whop.com store page
  works as-is, and so does a site Whop hosts on a whop.site address, which already
  has the pixel. For any other destination, check it with `events_validate_pixel`
  and the `url` before `ads_create`, and again before launching, because launch does
  not check the pixel. `installed: false` with `reachable: true` means no pixel.
  `reachable: false` means the page could not be read, so say that and do not call it
  a missing pixel. `ads_create` and `ads_update` refuse a `url` with no pixel, even on
  a draft: a 400 saying the pixel was not detected means send traffic to the store
  page or have the user install the pixel. A draft can leave out `url` until then.
- **Identity and agreement.** A launch also needs an approved identity verification,
  done by an owner of the business, and a signed Whop Ads agreement. Saving ads billing
  opens the agreement. Both are done in the user's Whop dashboard and this plugin
  cannot do them, so say so in words with no link. Read `capabilities.run_ads` from
  `accounts_get` before asking for the launch yes. Inactive means the launch will be
  refused, so say that and keep the draft. It can be null, and it reads active before
  billing is set up, so if a launch fails asking for either one, keep the draft and
  send the user to the dashboard.

## Creatives

An ad needs at least one image or video file id (`file_…`) in `creatives`.

- **The user's own file:** `files_create` with the `filename` and
  `visibility: "public"`, then PUT the bytes to the returned `upload_url` with its
  `upload_headers` using your own tools, then poll `files_get` until
  `upload_status` is `ready`, and use its `id`. `files_complete` is only for a
  `multipart` upload. Uploading needs a workspace that can make HTTP requests, such
  as Codex. If Codex's sandbox blocks the PUT, ask for network approval or tell the user to turn on internet access for this environment. Don't report that as a Whop failure. In a ChatGPT conversation without one, say using the user's own file
  means uploading it from Codex or making the ad in their Whop dashboard, and that the
  other option here is an AI-generated image, which bills the Whop balance. Do not
  recommend it, and generate one only if they ask for it and say yes.
- **An AI image or video:** `media_generate` with a prompt. Use `type: "image"`
  unless the user asks for a video, and for a video keep the default
  `duration_seconds` and `resolution` unless the user asks for more. It bills the
  Whop balance when the call goes through, and Whop sets the charge: say so and get a
  yes first. Pass a new `idempotency_key` with each generation. If the call times out
  or fails with no clear answer, it may have charged: call again only with the same
  key and the same arguments, which replays the first result, and do not switch keys
  until you know what happened. If you passed no key, do not call again: look for the
  charge with `ledgers_list`, tell the user what you found, and ask. A 402 or a
  `failed` job is a clear answer, so a later try takes a new key. The response's
  `amount_charged` is the actual charge, so tell the user that figure afterwards. Poll
  `media_get` until
  `status` is `ready`, then use `file.id`. A `failed` job refunds the charge. A 402
  means the balance is too low: tell the user to add funds in their Whop dashboard,
  and do not pass on the deposit link.

## Create, then launch

Build the campaign as a draft first, so nothing spends while the user reviews it.
Pass an `idempotency_key` on `ads_create` and `ad-groups_create`, and reuse it if a
result is unclear. With no key, check `ads_list` and `ad-groups_list` before calling
again: a second call can add a second ad group with its own budget.

1. `ad-campaigns_create` with `account_id`, `title`, and `objective`. It always
   creates a `draft`.
2. `ads_create` with an inline `ad_group` that points at the draft campaign. The ad
   group carries the targeting and, by default, the budget. On a draft campaign
   this launches nothing.

```json
{
  "title": "Launch ad",
  "primary_texts": [{ "text": "Join 10,000 runners chasing their next PR together." }],
  "headlines": [{ "text": "Find your stride" }],
  "call_to_action": "sign_up",
  "url": "https://whop.com/your-store",
  "creatives": [{ "id": "file_x" }],
  "ad_group": {
    "ad_campaign_id": "adcamp_x",
    "title": "US broad",
    "budget_amount": 25,
    "budget_type": "daily",
    "regions": { "include": { "countries": ["US"] } }
  }
}
```

3. **Say it, get a yes, then launch.** Show the campaign, the daily or lifetime
   budget in USD, the targeting, and the destination URL. For a new ads payer, also say
   that a balance or platform credits must cover the larger of $10 and one day's
   budget, or a card gets a temporary authorization of about $10 for each campaign
   launched, released after about a day. It is not a charge. Wait for a clear yes.
   Then call `ad-campaigns_update` with `status: "active"`. That call launches the
   ads, so never make it to see a preview.

- To add an ad to an existing ad group, pass `ad_group_id` instead of `ad_group`.
  Adding to a campaign that is not a draft launches the new ad at once, so get a
  yes first.
- Budget: one level owns it. `budget_amount` on the ad group (default), or on the
  campaign with `budget_optimization: "ad_campaign"`, never both. Budgets are USD.
- Omit `demographics` and `devices` for automatic optimization. `regions` takes
  `include` and `exclude` objects: countries as ISO 3166-1 codes in `countries`
  (`"US"`), US states as ISO 3166-2 codes in `regions` (`"US-CA"`).
- `creatives`: for a single-image or single-video ad, pass exactly one entry with no
  `format` (the base asset), plus optional crops `square`, `vertical`, and
  `horizontal`, each at most once. Two or more entries with no `format` make a
  carousel of 2-10 cards; use that only when the user asks for a carousel, not to
  offer alternatives.

## Manage what exists

| Job | Tools |
| --- | --- |
| Read | `ad-campaigns_list`, `ad-campaigns_get`, `ad-groups_list`, `ad-groups_get`, `ads_list`, `ads_get` |
| Stop delivery | `ad-campaigns_pause`, `ad-groups_pause`, `ads_pause` |
| Resume delivery | `ad-campaigns_unpause`, `ad-groups_unpause`, `ads_unpause`: spends money, so get a yes first |
| Change budget or targeting | `ad-campaigns_update`, `ad-groups_update`: say what changes and get a yes first |
| Edit an ad | `ads_update` — confirm first when the ad is live |
| Copy | `ad-campaigns_duplicate` (copies become drafts); `ad-groups_duplicate`, `ads_duplicate` keep the source's status, so a copy of something live spends money: get a yes first |
| Remove | `ad-campaigns_delete` (cascades to its ad groups and ads), `ad-groups_delete`, `ads_delete` — confirm first |

- `ads_update` with `creatives` replaces the whole set on the ad — keep exactly one
  entry with no `format` unless the user wants a carousel.
- `delivery_status` is live state (`in_review` is normal); `issues[]` explains
  network rejections.
- **Failed ads payment.** `delivery_status: "payment_failed"` blocks every campaign
  on the account. The user fixes the payment method in their Whop dashboard first.
  Then, after a yes, `accounts_retry_ads_payment` once for the account (it charges
  the ads payment method). It queues a retry and does not confirm payment; check the
  campaigns again afterwards. Do not retry per campaign.

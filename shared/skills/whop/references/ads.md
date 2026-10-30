# Ads — nothing to a live campaign

Read this before creating or launching ads. Enums and field lists live in each tool's
own schema — do not invent them. When a field here differs from the schema, the
schema wins.

Drafts can be created without billing. Launching (`status: "active"`) cannot.

## Setup

1. **Auth.** First-time ads billing needs a user login, not an API key — an API key
   can only reorder already-configured payment methods. A scope error saying the
   login predates the scope means the user must authorize again.
2. **Facebook page, only if the schema asks for one.** Newer API versions run ads
   under Whop's own pages and profiles and drop `external_accounts`. If the
   `ads_create` schema still lists `external_accounts`, the ad needs the business's
   Facebook page: `external-accounts_list` must show `"platform": "facebook"`.
   - Connect an existing Meta Business: `external-accounts_connect` with
     `platform: "meta_business"`, `scopes: ["advertise"]`, and a `redirect_url`, then
     give the user the returned `authorize_url`.
   - Or create a Whop-managed page: `external-accounts_create` with
     `platform: "facebook"`. That needs the account's `banner_image`, `logo`, and
     `description` set via `accounts_update` first. Account API keys cannot update
     their own account's branding — that needs a user login. `meta_business` is
     invalid on create; use `facebook`.
3. **Payment method.** Check `accounts_preferences`. If `ads_payment_methods` is
   null, set `{"primary": {"type": "platform_balance"}}` via
{{#if claude}}
   `accounts_update-preferences`, after the user says yes, changing only that
   field. This connection cannot add funds to the balance: the user tops it up on
   whop.com. Say so, and do not look for another tool to do it.
{{else}}
   `accounts_update-preferences`. Fund with `deposits_create`. A 402 returns a
   `deposit_url` — give it to the user. A successful deposit's `hosted_url` is the
   page, not an action link.
{{/if}}

TikTok campaigns can't be created here. Use only the `platform` value
`ad-campaigns_create` lists.

## Launch

{{#if claude}}
1. **Get the creative from the user.** Ads use images or videos the user supplies —
   a file they give you, or one already on their Whop account. This plugin does not
   generate images. Upload a local file with `files_create`, PUT the bytes to the
   returned `upload_url` with its `upload_headers`, then poll `files_get` until
   `upload_status` is `ready`; that file's `id` is what `creatives` wants. If the
   user has no creative yet, ask them for one.
{{else}}
1. `media_generate` with `type: "image"` and a prompt. Waiting returns `file.id`,
   which is what `creatives` wants. A 402 means fund first, then retry.
{{/if}}
2. `ads_create`:

```json
{
  "title": "Launch ad",
  "headlines": [{ "text": "Find your stride" }],
  "call_to_action": "sign_up",
  "url": "https://whop.com/your-store",
  "creatives": [{ "id": "file_x" }],
  "external_accounts": [{ "id": "sacc_x" }],
  "ad_group": {
    "title": "US broad",
    "ad_campaign": {
      "title": "Growth", "platform": "meta", "objective": "sales",
      "status": "draft", "budget_amount": 25,
      "budget_optimization": "ad_campaign"
    }
  }
}
```

The `platform` value and `external_accounts` match the API version the server uses
today. Use the one `platform` value `ad-campaigns_create` lists, and drop either
field if its schema does not list it.

{{#if claude}}
3. **Confirm, then launch.** Show the user the campaign, the budget, and the
   destination URL, and ask whether to launch. Only after a clear yes, call
   `ad-campaigns_update` with `status: "active"`. Launching spends money.
{{else}}
3. `ad-campaigns_update` with `status: "active"` when the user has reviewed it.
{{/if}}

Pass exactly one of `ad_group` or `ad_group_id`. A nested `ad_campaign` object inside
`ad_group` creates campaign + group + ad in one call — the API description
understates this. Reuse an existing container with `ad_group_id`, or `ad_campaign_id`
inside `ad_group`. If that campaign is already active, the new ad runs right away.
New ad groups start `active`, and duplicated ads and ad groups keep the source's
status.

Keep `status: "draft"` until the user has reviewed. **Omitting draft launches
immediately**, which then requires billing and a destination URL.

| Field | Rule |
| --- | --- |
| Copy | `headlines`, `primary_texts`, and `descriptions` take `{ "text": … }` objects, not plain strings. |
| `platform` / `external_accounts` | Send each only when the schema lists it: `platform` on the campaign when `ad-campaigns_create` has it (use the one value it lists), and `external_accounts` when `ads_create` has it. Newer API versions reject both. |
| `creatives` | One entry with no `format` is the base asset. Optional crops: `square` / `vertical` / `horizontal` only — not `portrait`. No duplicate formats. Two or more unformatted entries is a carousel (2–10). |
| `url` | Required to launch a website ad. A whop.com store page works as-is; an external page needs the Whop pixel. Drafts may omit it. |
| Budget | CBO: `budget_amount` on the campaign with `budget_optimization: "ad_campaign"`. ABO: `budget_amount` on the ad group with `budget_optimization: "ad_group"`. Never both. |
| Targeting | Omit `demographics` / `devices` for automatic optimization. `regions` uses ISO 3166 (`"US"`, `"US-CA"`). |

`ads_update` with `creatives` replaces the whole set — include the base entry.
`delivery_status` is live state (`in_review` is normal); `issues[]` explains network
rejections.

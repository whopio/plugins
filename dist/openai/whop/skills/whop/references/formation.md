# Company formation

The tool is `accounts_form_company`. State enums and founder field lists live in its
schema — do not invent them.

It creates a **hosted checkout**. It does not charge and it does not file. The
response carries `checkout_url` and the `total` (USD cents).
Give the user both, and say nothing is charged until they pay there and filing
starts after payment. The `total` covers the first year. The plan then renews at
$100 a year at today's price, so say that too. Track progress on the account's `company_formation` field via
`accounts_get`.

The first year is $500 at today's price, due at checkout, and the plan then renews at
$100 a year. Say both before you ask for founder details, so the user can decide
first. `total` in the response is the exact amount.

Before you ask for founder details, read `business_type` and `industry_type` on
`accounts_get`. Whop sets both, and formation needs both. No tool field sets them, so
do not look for one. If either is null, say formation can't start yet, here or on
Whop's dashboard form, because Whop has not classified the business. A new business
has neither. Whop classifies from what the business sells, so offer to add the real
product they plan to sell (`products_create` with a real title and description, after
their yes), never a placeholder. Then read `accounts_get` again. If a value is still
null, say so and that they can try again later.

Before you ask for any founder details, ask whether any founder has a US address. The
answer decides where the formation happens (see "Founder identity"), so collect the
details only if it will happen here.

Before you call it, show the user the price, company name, state, entity type, and
founders: names and ownership for an LLC; names and roles, plus the share count and
par value, for a C-corp. If there is more than one founder, also say that after filing
Whop emails the other founders an invite to this Whop business as an admin (Operations
in the dashboard), which covers products, members and payments but not payouts. Wait
for their yes, then call it once.

## Checkout

Required: `id` (the `biz_` business id from `accounts_list`; this tool takes `id`,
not `account_id`), `business_name`, `formation_state`, and `founders`. Each founder
needs `first_name`, `last_name`, `email`, `phone` (E.164), and `address`, and exactly
one founder is `is_primary`. Whop recommends `WY`, where formations complete the
same day.

```json
{
  "id": "biz_xxx",
  "business_name": "Acme Holdings",
  "formation_state": "WY",
  "entity_type": "llc",
  "use_registered_agent": true,
  "founders": [{
    "is_primary": true, "first_name": "Jane", "last_name": "Doe",
    "email": "jane@example.com", "phone": "<E.164 number>",
    "address": {
      "line1": "<home address>", "city": "<city>",
      "state": "<state or region>", "postal_code": "<postal code>", "country": "<country code>"
    },
    "ownership_percentage": 100
  }]
}
```

Always pass a unique idempotency key. After a timeout or a 5xx the outcome is
uncertain, so retry with the **same** key and the same arguments. A new key would
create a second checkout. A 409 on that key means the first call has not finished:
wait and retry, and if it stays 409, tell the user instead of changing the key. A 4xx
that names a rule or field is final and created no checkout, so the next attempt needs
a new key, even with unchanged arguments and even though the key's description says to
reuse it after an error. The old key would return `idempotency_key_mismatch` or replay
that error for 24 hours.

## Founder identity

Each founder's home `address` is required, wherever they live. `date_of_birth` is
optional, so ask for it only if an error names it.

Never ask for an SSN, from any founder, even though the tool's schema describes one.
What the user needs to know depends on where the founders live, so tell them before
they say yes:

| Founders | Where to form | EIN |
| --- | --- | --- |
| None has a US address | Here. Leave out `ssn`. | Can take up to 8 weeks after incorporation. `expedite_ein` gets the EIN documents 2 weeks earlier, per Whop's form, for $250 more at today's price, which also shows in `total`. Let the user choose. After payment the founder signs Form SS-4 online, plus Form 8821 if they expedite, and the EIN can't be issued until they do. |
| At least one has a US address, including mixed teams | Whop's form at `https://whop.com/form-company/<biz_id>`, using the business's `biz_` id, never the plain `/form-company/` link. It requires each US-address founder's SSN, in a secure field, and won't continue without one. Whether a filing goes through without one isn't known, so don't start a checkout here without one, and don't suggest typing one in this chat. If a US-address founder has no SSN, say that plainly and point them to Whop support at help.whop.com. | Whop's form doesn't offer an expedited EIN, so don't add `expedite_ein`. |

If a founder gives you an SSN or date of birth anyway, pass it to the tool as given.
Do not infer a missing value, repeat them back, show them in a summary, write them
to a file, or put them in any other field.

## LLC vs C-corp vs registered agent

| Path | Extra rules |
| --- | --- |
| LLC (default `entity_type: "llc"`) | Each founder needs `ownership_percentage`; they must total 100. |
| C-corp (`entity_type: "c_corp"`) | Requires `share_structure`: `number_of_shares`, and `value`, the par value per share in USD (for example `0.01`, not the total capital). Every founder needs at least one entry in `roles`. Across the founders, every role must be covered: `president`, `secretary`, and `treasurer` each by exactly one founder, and `director` by at least one (it can repeat). A solo founder holds all four. Ask before executing. |
| Registered agent | `use_registered_agent: true` omits `business_address` and `business_phone`. Otherwise both are required. |

Indiana and Illinois don't accept the registered agent's address, so a filing there
with `use_registered_agent: true` can sit unfiled after payment. For those states,
leave it off and use a founder's own US address as `business_address`. With no US
address to use, suggest another state.

`expedite_ein` (an extra fee) fails if any founder supplies an SSN.

Get these rules right before you ask for the yes. A request that breaks them fails
and creates no checkout. Re-read the tool's schema and fix the field the error names.

`Select a valid business type`, `Select a valid industry type` and `Add your industry`
are the exception: no field fixes them. Go back to the classification check. If both
values are set, try once more after a few seconds with a new key. If it still fails,
say Whop's classification blocks formation for this business and that Whop support has
to look at it. Don't say the dashboard fixes it.

## After payment

The IRS forms that still need a founder's signature appear under
`company_formation.signatures` on `accounts_get`: `ss4` (the EIN application) and
`form8821` (tax information authorization). They can take a while to appear, so an
empty `signatures` soon after payment doesn't mean none are coming. A `pending` form
has a signing `url` that lasts until `expires_at`, so read `accounts_get` again for a
current link. `unknown` means Whop couldn't check that form just now: there's no link
and it may not need signing, so read again shortly. Give the founder the link and say
what it is for. Do not open it yourself.

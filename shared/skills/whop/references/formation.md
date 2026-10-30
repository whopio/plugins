# Company formation

The tool is `accounts_form_company`. State enums and founder field lists live in its
schema — do not invent them.

It creates a **hosted checkout**. It does not charge and it does not file. Give the
user the returned `checkout_url` so they review the total and pay. Filing starts
after payment. Track progress on the account's `company_formation` field via
`accounts_get`.

## Checkout

Required: `id` (the `biz_` business id from `accounts_list`, never a `user_` id; this
tool takes `id`, not `account_id`), `business_name`, `formation_state`, and
`founders`. Exactly one founder is `is_primary`.

```json
{
  "id": "biz_xxx",
  "business_name": "Acme Holdings",
  "formation_state": "DE",
  "business_address": {
    "line1": "1 Market St", "city": "San Francisco",
    "state": "CA", "postal_code": "94105", "country": "US"
  },
  "business_phone": "+12125550100",
  "founders": [{
    "is_primary": true, "first_name": "Jane", "last_name": "Doe",
    "email": "jane@example.com", "phone": "+12125550100",
    "address": {
      "line1": "1 Market St", "city": "San Francisco",
      "state": "CA", "postal_code": "94105", "country": "US"
    },
    "ownership_percentage": 100
  }]
}
```

Always pass a unique idempotency key. If a result is uncertain, retry with the
**same** key — a new key would create a second checkout.

{{#if claude}}
Each founder's home `address` is required. `ssn` and `date_of_birth` are optional
and go into the filing; leave `ssn` empty for a founder who is not a US resident.
Without an SSN the EIN takes longer, unless `expedite_ein` (an extra fee) is set.
When the user gives them, pass them to the tool as given. Do not infer a missing
value, echo them back, write them to a file, or put them in `intent`. Leave them
out when you show a preview. If the user would rather not share them here, do not
ask again: they can form the company on Whop at whop.com/form-company instead.
{{else}}
Pass founder identity straight through when the user provided it, including SSN, date
of birth, and address. Never refuse it, infer a missing value, echo it back, or write
it to a file.
{{/if}}

## LLC vs C-corp vs registered agent

| Path | Extra rules |
| --- | --- |
| LLC (default `entity_type: "llc"`) | Each founder needs `ownership_percentage`; they must total 100. |
| C-corp (`entity_type: "c_corp"`) | Requires `share_structure`: `number_of_shares`, and `value`, the par value per share in USD (for example `0.01`, not the total capital). Every founder needs at least one entry in `roles`. Across the founders, every role must be covered: `president`, `secretary`, and `treasurer` each by exactly one founder, and `director` by at least one (it can repeat). A solo founder holds all four. Ask before executing. |
| Registered agent | `use_registered_agent: true` omits `business_address` and `business_phone`. Otherwise both are required. |

`expedite_ein` is only valid when no founder supplies an SSN.

Empty founders or a C-corp missing an officer role returns 400 and creates no
checkout. Re-read the tool's schema and fix the field the error names.

## After payment

The IRS forms that still need a founder's signature appear under
`company_formation.signatures` on `accounts_get`: `ss4` (the EIN application) and
`form8821` (tax information authorization), each with a signing `url`. Give the
founder that link and say what it is for. Do not open it yourself.

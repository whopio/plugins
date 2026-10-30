# Websites and apps (`*.whop.site`)

Read this before creating or deploying an app. Field lists and enums live in each
tool's own schema — do not invent them.

## Create the app

`apps_create` takes only `name` as required. The fields that matter for a hosted
site:

| Field | Notes |
| --- | --- |
| `name` | Required. Shown to users on the app store. |
| `app_type` | `website` (visitors browse `<route>.whop.site`), `b2c_app` (creators install it), plus `b2b_app`, `company_app`, `component`. Ask; do not guess. |
| `route` | The whop.site subdomain (`myapp` serves at `myapp.whop.site`). Deprecated in the schema but still accepted. Without it or a `domain_id`, the app has no address. |
| `account_id` | `biz_` tag. Optional in the schema, but always pass the business id from `accounts_list`. Never rely on a default. |
| `base_url` | Only for an app you host yourself elsewhere. |

Ask which `app_type` before creating. The choice shapes how the app is surfaced, and
changing a website back to an app is not a supported move.

## Deploy

```
apps_deploy(id: "app_xxx", draft: false)
```

`apps_deploy` **builds the app's current source on Whop and ships it.** Nothing local
is required to deploy source Whop already holds.

- Only one deployment runs per app at a time. Calling it again while one is in flight
  reports that run rather than starting a second.
- Calling it with nothing to publish says so rather than starting a run.
- `draft: true` uploads the build without making it live. The default deploys and
  promotes in one step.
- It returns the run it started. Follow progress on the app's `deployment` field via
  `apps_get`.

## Shipping code that only exists locally

`apps_deploy` builds what Whop already has. To get new local code up, do the local
half with your own tools and the rest over MCP:

1. Write and build the files yourself.
2. Upload the archive: `files_create`, PUT the bytes to the returned `upload_url`
   with its `upload_headers`, then poll `files_get` until `upload_status` is
   `ready`. `files_complete` is only for multipart uploads. Web takes a JavaScript
   file or a `.zip` of the hosted site.
3. `app-builds_create` referencing the uploaded file — `attachment` takes `{ id }`
   for an existing file or `{ direct_upload_id }` for a completed direct upload.
4. `app-builds_promote` to make that build live.

Promoting an older build rolls back to it.

Do not tell the user to install a CLI for any of this.

## Reading state

- `apps_get` — live state, including `deployment`.
- `apps_list` with `account_id` — the account's apps (without it, the public app
  store). It leaves out websites unless you pass `app_type: "website"`, so to list
  everything, call it both ways.
- `app-builds_list` / `app-builds_get` — build history.
- `apps_logs` — runtime logs.

An app's addresses are in `domains` on `apps_get`: its whop.site address and any
custom domain. Each `status` sums up everything on that domain, such as the pixel,
Apple Pay, and renewal. `ready` means live; show it as `https://<domain>`. Another
status doesn't always mean the site is down: check `website.state` (or
`platform.state` for a whop.site address) on `domains_get`. `hosted_url` is
deprecated and can be null. None of these are action links.

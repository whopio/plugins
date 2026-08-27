---
name: whop-mcp-safety
description: "The required protocol for any Whop MCP tool call that changes state: the prepare-and-confirm handshake with mcp_confirmation_token, the intent and intent_id attribution fields every operation tool demands, and idempotency_key rules for money movement. Read before the first create, update, delete, refund, payout, transfer, deposit, or formation call in a session, and whenever a Whop tool returns a confirmation token or rejects a call for a missing field."
---

# Whop MCP: writing safely

Read requests are ordinary tool calls. **Writes are not.** Whop's MCP surface layers
three requirements on top of the tool schema, and a call that omits any of them
fails or, worse, silently does the wrong thing twice.

## 1. Attribution — on every operation tool

Every API-backed operation tool requires two fields that are not part of the
underlying Whop API:

| Field | What goes in it |
| --- | --- |
| `intent` | The user's original request, **copied verbatim** when you have it. Not your paraphrase, not a summary of the tool call. |
| `intent_id` | A UUID you generate **once per user message** and reuse for every operation tool call made to fulfill that message. |

Generate one `intent_id` when you start acting on a message and thread it through
every call in that turn. A new user message gets a new UUID. This is what
distinguishes two separate turns that happen to contain the same request text.

Both fields are stripped before validation and never reach the Whop API as
arguments — they exist so Whop can analyze request intent. They are client-supplied:
the MCP protocol does not expose the conversation to the server, so nothing verifies
them but you. Fill them honestly.

The fixed-schema `search` and `fetch` compatibility tools and the local
`connection_status` diagnostic do not take these fields.

## 2. Prepare and confirm — on consequential operations

Financial, credential, and destructive operations execute in **two calls**:

1. **Prepare.** Call the tool normally. It does *not* execute. It returns a preview
   of what would happen plus an `mcp_confirmation_token`.
2. **Confirm.** Show the preview to the user. After they approve, call the **same
   tool with the same arguments**, adding the confirmation token and a stable
   `idempotency_key`.

**Never call step 2 without the user's approval of the actual preview.** Do not treat
a general "yes, do it" from earlier in the conversation as approval for a preview the
user has not seen. The preview is the thing being approved.

### Idempotency

- Money-movement operations **require** an `idempotency_key`. Generate one stable key
  per logical operation.
- **Retrying a call reuses the same key.** A new key on a retry is a second payment,
  not a retry.
- If an outcome comes back unknown or the call times out, **do not fire again
  blindly** — verify with the matching `get`/`list` first, then retry with the
  original key.

### What counts as consequential

Prepare-and-confirm is set per operation on the server, so treat the token in the
response as the source of truth rather than this list. In practice it covers:

- **Money movement** — creating, refunding, retrying, or voiding payments; payouts
  and payout cancels; transfers; swaps; deposits; topups; marking invoices paid,
  uncollectible, or void; ad-campaign payment retries; bounties and bounty cancels.
- **Financial configuration** — issuing or updating cards; fee markups; payout
  methods; extending or adding free days to a membership; `media generate`; payment
  method domains; setup intents and return URLs.
- **Credentials** — creating access tokens and API keys.
- **Shipping code** — `apps_deploy` builds the app's current source and, unless you
  pass `draft: true`, promotes it to production. `app_builds_promote` has the same
  end effect. Both change what real users see; both require confirmation.
- **Destructive deletes** — anything classified destructive, e.g. deleting a fee markup.

If a tool returns an `mcp_confirmation_token`, the operation did not happen yet.
Say so plainly rather than reporting success.

## 3. Scope — what the grant actually allows

The hosted endpoint requests the MCP **`admin`** scope. `connection_status`
reports it as `permission_profile: "admin"` with `granted_scopes: ["*"]` — match on
the profile, not on the literal string `admin` in the scope list.

That is the full administrative profile for the reviewed MCP surface — not read-only,
not per-tool, and **not bound to a single business**. It can act on every business the
authenticated Whop user manages.

Two consequences worth stating to the user when it matters:

- Confirm the **account id** before a write. "The selected business" may not be the
  one they meant, and the grant will not stop you.
- Prepare-and-confirm reduces accidental and duplicate actions. It is **not** a
  security boundary — it does not shrink the privileges of the OAuth grant.

Tell the user to disconnect the integration when they no longer need it.

## Reporting outcomes

- Confirmation token returned, not yet confirmed → "prepared, awaiting your approval."
- Confirmed and succeeded → say what moved, and include the resulting id.
- Unknown or timed out → say it is unknown, verify with a read, and never assume.

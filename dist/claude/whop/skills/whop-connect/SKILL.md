---
name: whop-connect
description: Connect and verify this workspace's Whop account
disable-model-invocation: true
---

# Connect to Whop

Walk the user through connecting the Whop MCP server and confirm what the grant can
reach. Do not skip to a business action — this command's only job is the connection.

## Steps

1. **Call `connection_status`.**

   - **It works** → report, in plain language: the authenticated user
     (`user_name`), the permission profile, and how many tools are available.
     Then handle the account:
     - **`account_id` is set** → name the account and its `biz_…` id.
     - **`account_id` is null** → say plainly that no account is selected yet, then
       call `accounts_list`. One account: name it and say it will be used when the
       user passes its id. Several: list them and ask which. None: say the user has
       no Whop business yet and point them at whop.com.

     Do not invent an account, and do not report a null account as if it were one.
     Then stop and ask what they want to do.
   - **The tool is missing entirely** → the MCP server has not loaded. Tell the user
     to run `/plugin` and confirm the `whop` plugin is enabled, then `/mcp` to check
     the `whop` server's state. A restart of Claude Code picks up a newly installed
     plugin.
   - **It returns unauthenticated** → the OAuth flow has not completed. Tell them to
     run `/mcp`, select `whop`, and authenticate. The browser opens to Whop for
     sign-in and authorization. **No API key is involved** — if they are reaching for
     one, that is the wrong path for this server.

2. **Say what they authorized.** The hosted endpoint requests the MCP `admin` scope:
   full administrative access to the reviewed MCP surface, across *every* business
   the signed-in user manages — not scoped to one business. Worth one sentence so
   they know what they granted, and that they can disconnect from `/mcp` later.

## Argument

If `$ARGUMENTS` names a business (a `biz_…` id or a store route), verify after step 1
that it matches the selected account, and say plainly whether it does. If it does
not, tell them which account is selected — do not switch it yourself.

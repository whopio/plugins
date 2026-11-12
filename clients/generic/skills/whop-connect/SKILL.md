---
name: whop-connect
description: Connect and verify this workspace's Whop account
disable-model-invocation: true
---

# Connect to Whop

Confirm the Whop MCP server is connected and report what the grant can reach. Do not
skip ahead to a business action — this skill's only job is the connection.

This plugin installs into several tools, and each names its menus differently. Where
a step below says "the MCP server list", use the name this tool gives it. If you do
not know it, say so and ask the user to open the place where this tool lists its MCP
servers. Do not invent a command.

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
     to check that the `whop` plugin is installed and enabled, then to look for the
     `whop` server in the MCP server list. A restart of the tool picks up a newly
     installed plugin.
   - **It returns unauthenticated** → the OAuth flow has not completed. Tell them to
     select the `whop` server in the MCP server list and sign in. The browser opens
     to Whop for sign-in and authorization. **No API key is involved** — if they are
     reaching for one, that is the wrong path for this server.

2. **Say what they authorized.** The hosted endpoint requests the MCP `admin` scope:
   full administrative access to the reviewed MCP surface, across *every* business
   the signed-in user manages — not scoped to one business. Worth one sentence so
   they know what they granted, and that they can disconnect from the MCP server
   list later.

## Argument

If `$ARGUMENTS` names a business (a `biz_…` id or a store route), verify after step 1
that it matches the selected account, and say plainly whether it does. If it does
not, tell them which account is selected — do not switch it yourself.

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

   - **It works** → report, in plain language: the authenticated user, the selected
     account (name and `biz_…` id), the granted scopes, and how many tools are
     available. Then stop and ask what they want to do.
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

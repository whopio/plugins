---
name: whop-connect
description: Connect and verify this workspace's Whop account
disable-model-invocation: true
---

# Connect to Whop

Confirm the Whop MCP server is connected and report what the grant can reach. Do not
skip ahead to a business action — this command's only job is the connection.

## Steps

1. **Call `connection_status`.**

   - **It works** → report, in plain language: the authenticated user, the selected
     account (name and `biz_…` id), the granted scopes, and how many tools are
     available. Then stop and ask what they want to do.
   - **The tool is missing entirely** → the MCP server has not loaded. Tell the user
     to open `/plugins` and confirm the `whop` plugin is enabled, then `/mcps` to
     check the `whop` server's state. `grok mcp doctor whop` diagnoses configuration
     and connectivity, and takes `--json`.
   - **It returns unauthenticated** → the OAuth flow has not completed. Tell them to
     open `/mcps`, select `whop`, and press `i` to authenticate. The browser opens to
     Whop for sign-in and authorization. **No API key is involved** — if they are
     reaching for one, that is the wrong path for this server. Grok also triggers
     this flow automatically the first time it uses a Whop tool.

2. **Say what they authorized.** The hosted endpoint requests the MCP `admin` scope:
   full administrative access to the reviewed MCP surface, across *every* business
   the signed-in user manages — not scoped to one business. Worth one sentence so
   they know what they granted, and that they can revoke it from `/mcps` later.


---
name: whop-connect
description: Connect and verify the user's Whop account. Runs as the Whop plugin's setup, or when invoked directly ($whop:whop-connect in Codex) to check which Whop business is connected.
---

# Connect to Whop

Confirm the Whop MCP server is connected and report what the grant can reach. Do not
skip ahead to a business action. This skill's only job is the connection; the one
exception is offering to create a first business when the user has none (step 1).

## Steps

1. **Call `connection_status`.**

   - **It works** → report, in plain language: the authenticated user
     (`user_name`), the permission profile, and how many tools are available.
     Then handle the account:
     - **`account_id` is set** → name the account and its `biz_…` id.
     - **`account_id` is null** → say plainly that no account is selected yet, then
       call `accounts_list`. One account: name it and its `biz_…` id, and say you
       will use it for their Whop requests (they do not need to type the id). Several: list them and ask which. None: say the
       signed-in user does not run or manage a Whop business yet. Offer to create
       one here with `accounts_create`, setting only the title they give and only
       after their yes, or say they can create one in their Whop dashboard. Before that
       yes, say a new business starts with Dispute Fighter on, which is Whop's default,
       that Whop takes a success fee on disputes it wins, and that they can turn it off
       here or in their Whop dashboard.

     Do not invent an account, and do not report a null account as if it were one.
   - **The tool is missing entirely** → the Whop MCP server is not connected in this
     conversation. Tell the user to check that the Whop plugin is installed and
     enabled: in ChatGPT under Plugins, in the Codex CLI with `/plugins`. Then they
     connect Whop, sign in, and start a new conversation.
   - **It returns unauthenticated** → sign-in has not finished or has expired. Tell
     them to connect or reconnect Whop from the Whop plugin in ChatGPT's Plugins
     page. The
     browser opens Whop for sign-in and approval. **Nothing is typed into the chat:
     no API key, no password, no code.** If they are reaching for one, stop them.
     That is the wrong path for this server.

2. **Say what they authorized** (only if step 1 connected). The endpoint requests the MCP `admin` scope:
   administrative access to this plugin's Whop tools, across *every* business the
   signed-in user manages, not scoped to one business. Worth one sentence so they
   know what they granted. They can disconnect Whop from the plugin's settings at any
   time, which stops this connection. Ending the access on Whop's side happens in
   their Whop account settings, and it also ends it for other AI tools connected the
   same way.

3. **Say what is not available here** (only if step 1 connected). One sentence:
   payouts and other money movement, issuing refunds, and one-off charges to
   customers are not available in this plugin, and the user can do them in their
   Whop dashboard. Do not link to those pages.

4. **Then stop and ask what they want to do.**

## A named business

If the user named a business (a `biz_…` id or a store route), verify after step 1
that it is one the signed-in user can reach, and say plainly whether it is. If it is
not, say which businesses are available. Do not guess.

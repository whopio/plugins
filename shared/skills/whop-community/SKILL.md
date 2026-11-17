---
name: whop-community
description: "Read and answer conversations in a Whop business through the Whop MCP tools: customer support chats, DMs, community chat messages and forum posts. Use when the user asks what customers are saying on Whop, which support conversations are waiting for a reply, to read or reply to a DM or support chat, or to read or publish a forum post. Not for looking up who a customer is (whop-customers)."
---

# Whop chats, support and forums

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Tools

| Tool | Use it to |
| --- | --- |
{{#if openai}}
| `support-channels_list` | See customer support conversations, most recently active first |
| `dm-channels_list` | See the user's DM inbox |
{{else}}
| `channels_list` | See support conversations, DMs and community chats |
{{/if}}
| `messages_list` | Read the messages in one conversation |
| `messages_get` | Read one message |
| `messages_create` | Send a message |
| `forum-posts_list` | Read a forum's posts, or the replies under one post |
| `forum-posts_create` | Publish a post or a comment |

## Reading

{{#if openai}}
1. Find the conversation. `support-channels_list` with `open: true` returns the
   ones still waiting for a reply. When the user names a business, pass its
   `account_id`; without it the list mixes in every other business the user can
   reach. `dm-channels_list` returns the DM inbox.
{{else}}
1. Find the conversation with `channels_list`. `kind` is required.
   - A business's support inbox: `kind: ["support"]`, its `account_id` and
     `support_role: "staff"`. Add `status: "unresolved"` for the open ones, or
     `awaiting_reply: true` for those where the customer wrote last. Without
     `support_role: "staff"` the list returns support chats the user opened as a
     customer.
   - The user's DMs: `kind: ["private"]`.
   - `query` matches a channel's name, or a member's name or username.

   If `channels_list` is not among the listed tools, this server still has the
   older pair: `support-channels_list` (with `account_id`, and `open: true` for the
   ones waiting for a reply) and `dm-channels_list`. Read their schemas and use
   them instead.
{{/if}}
2. Read it with `messages_list` and the `channel_id`. For a community chat, the
   chat's experience id works as the `channel_id`.

`forum-posts_list` needs the forum's `experience_id`. Pass `parent_id` to read the
replies under one post. Find a forum's experience id with `experiences_list`.

Chats hold customers' private messages. Quote only what the user asked about.

## Sending

`messages_create` takes `channel_id` and `content` (Markdown). Pass
`replying_to_message_id` to reply to one message.

`forum-posts_create` takes `experience_id`. Pass `parent_id` to comment on a post,
or leave it out for a new top-level post. `experience_id: "public"` together with
`account_id` posts to the business's public forum. A paywalled post
(`paywall_amount`) must have a `title`, because the title stays visible to people
who have not paid.

Forum posts have two traps. `forum-posts_create` pins with `pinned`, while the
update operation uses `is_pinned`. And `experience_id: "public"` is only for the
public forum: never use it as a shortcut for something meant for paying members.

{{#if claude,grok}}
### Starting a DM

A DM is a private channel between user ids (`user_…`). When the user gives a name,
username or email, look the person up first (`members_list` for a customer, or the
"list users" operation) and use the id it returns. If several people match, ask
which one. Then run the `channels_create` operation with `kind: "private"` and
`participant_user_ids`. It returns the existing conversation when there is one, so
it is safe to call, and you send to the channel id it returns.

A message for a whole community chat goes to the chat's experience id. Do not
create a private channel for it.

A DM to a customer is not a Resolution Center case and does not bring in Whop
staff.

{{/if}}
### Sending to several people

- Send in small batches of about 10, and keep each recipient's result. Report who
  failed and why. Some sent is not "sent to everyone".
- Whop limits how fast a user can send, roughly 10 messages in 10 seconds, and
  limits how many new DMs can be started in a day. The exact numbers can change.
- A send that hits the limit can come back as a not-found error. The message was
  not sent and the person or channel is not missing. Stop the batch, wait, then
  send to the ones skipped.

Both tools go to real people the moment they are called.

- Show the user the exact text and where it will go, and wait for a yes.
- Never send the same message to many customers in a loop unless the user asked for
  exactly that and has seen the list.
- Neither tool takes an `idempotency_key`, so a second call sends a second time.
  After an unclear result, read the conversation back with `messages_list` or
  `forum-posts_list` before trying again.

## Not listed here

{{#if claude,grok}}
Editing, deleting, pinning or reacting to a message, opening a support
conversation, marking one resolved, editing a forum post, and changing who can post
or comment in a forum are reached through `search_operations`.
{{/if}}
{{#if openai}}
These are listed too: `messages_update`, `messages_delete`, `dm-channels_create`,
`support-channels_create`, `forum-posts_get`, `forum-posts_update` and
`forums_list`. Deleting a message cannot
be undone, so confirm first.
{{/if}}

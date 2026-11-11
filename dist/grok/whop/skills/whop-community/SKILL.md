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
| `support-channels_list` | See customer support conversations, most recently active first |
| `dm-channels_list` | See the user's DM inbox |
| `messages_list` | Read the messages in one conversation |
| `messages_get` | Read one message |
| `messages_create` | Send a message |
| `forum-posts_list` | Read a forum's posts, or the replies under one post |
| `forum-posts_create` | Publish a post or a comment |

## Reading

1. Find the conversation. `support-channels_list` with `open: true` returns the
   ones still waiting for a reply. Without `account_id` it covers every business
   the user can reach. `dm-channels_list` returns the DM inbox.
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

Both go to real people the moment they are called.

- Show the user the exact text and where it will go, and wait for a yes.
- Never send the same message to many customers in a loop unless the user asked for
  exactly that and has seen the list.
- Neither tool takes an `idempotency_key`, so a second call sends a second time.
  After an unclear result, read the conversation back with `messages_list` or
  `forum-posts_list` before trying again.

## Not listed here

Editing, deleting, pinning or reacting to a message, starting a new DM or support
conversation, and editing a forum post are reached through `search_operations`.

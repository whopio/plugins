---
name: whop-docs-and-operations
{{#if claude,grok}}
description: "Search the Whop documentation and reach every Whop operation that is not a listed tool, through the Whop MCP tools docs_search, docs_query, search_operations, describe_operation, call_read_operation and call_write_operation. Use when the user asks how something on Whop works, when no listed Whop tool fits the job, or for websites on *.whop.app, Meta and TikTok ads, forming an LLC or C-corp, webhooks, invoices, affiliates, checkout links, API keys or anything else in a Whop account. Always use before saying Whop cannot do something."
{{/if}}
{{#if openai}}
description: "Search the Whop documentation with docs_search and docs_query, and find the right Whop MCP tool for a job no other Whop skill covers. Use when the user asks how something on Whop works, or for websites on *.whop.site, Whop Ads, forming an LLC or C-corp, domains, affiliates, automations or anything else in a Whop account. Always use before saying Whop cannot do something."
{{/if}}
---

# Whop docs and the rest of the tools

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

{{#if claude,grok}}
The server lists only its most-used tools by name. This skill covers the two ways
to go further: read the docs, and run any other operation.
{{/if}}
{{#if openai}}
This skill covers reading the docs, and finding the right tool when no other Whop
skill names it.
{{/if}}

## Reading the docs

| Tool | Use it to |
| --- | --- |
| `docs_search` | Search docs.whop.com in plain words; returns excerpts with page paths |
| `docs_query` | Read a page, or explore the docs like a folder of files |

1. `docs_search` with the question, for example "how do affiliate commissions
   work".
2. Read a page it returned with `docs_query`, adding `.mdx` to the path:
   `head -100 /developer/guides/ai_and_mcp.mdx`.

`docs_query` runs a read-only, shell-style command over a virtual folder that holds
only the Whop docs. It is not a shell on any machine. It accepts `ls` and `tree` to
explore, `rg` for an exact match, and `head` or `cat` to read.

Link pages as `https://docs.whop.com/<path>` without `.mdx`. Answer from what the
docs say, not from memory: Whop changes often. If the docs do not answer it, say so.

{{#if claude,grok}}
## Running an operation that is not listed

| Tool | Use it to |
| --- | --- |
| `search_operations` | Find an operation from a plain description of the task |
| `describe_operation` | Get one operation's full description and input schema |
| `call_read_operation` | Run an operation that only reads |
| `call_write_operation` | Run an operation that creates, changes or deletes |

1. **Search.** `search_operations` with the task in plain words: "list my
   webhooks", "create a checkout link". It returns up to 10 matches (`limit` goes
   to 25), each with `name`, `summary`, `read_only`, `destructive` and `call_with`,
   the tool to run it with. The top 3 also carry their full `input_schema`.
2. **Read the schema.** If the one you want is not in the top 3, call
   `describe_operation` with its `name`. Never call an operation whose inputs you
   have not seen.
3. **Run it.** Call the tool named in `call_with`, passing `name` exactly as
   returned and the inputs inside `arguments`:

   ```json
   { "name": "webhooks_list", "arguments": { "account_id": "biz_xxx" } }
   ```

   A read sent to `call_write_operation`, or a write sent to `call_read_operation`,
   is refused with a message naming the right tool.
4. **For writes**, pass an `idempotency_key` you choose. Reuse the same key if you
   retry after a timeout or error, then read the record back to confirm.

An operation marked `destructive`, or one that spends money, sends something to
customers or deletes data, needs the user's yes first. Say what it will do in plain
words before running it.

`describe_operation` also works on listed tools. Some of them, such as
`payments_list` and `variants_create`, leave optional inputs out of their listing;
`describe_operation` shows every input, and the listed tool accepts all of them.

**Search before saying no.** If the user asks for something and no listed tool
fits, call `search_operations` before telling them Whop cannot do it. Try a second
wording if the first finds nothing.

## Playbooks

Three jobs have ordering traps that a schema alone does not teach. Read the
playbook before starting. Every tool a playbook names is an operation: get its
schema with `describe_operation` and run it with `call_read_operation` or
`call_write_operation`.

| Job | Playbook |
| --- | --- |
| Ship a website or app on `*.whop.app` | [references/websites.md](references/websites.md) |
| Run Meta or TikTok ads | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | [references/formation.md](references/formation.md) |

{{/if}}
{{#if openai}}
## Finding the right tool

Every tool this connection has is listed by name. There is no search tool and no
generic tool that runs an operation by name.

- Names follow `<group>_<operation>`: `domains_list`, `ad-campaigns_update`,
  `checkout-configurations_create`. Look for the group first, then the operation.
- Operations are usually `list`, `get`, `create`, `update` and `delete`, plus a few
  named actions such as `app-builds_promote` or `memberships_pause`.
- Read the tool's description and schema before calling it. Never invent a tool
  name, a field or an enum value.
- If the user's word finds no group, try Whop's word for it: a price is a
  `variant`, a business is an `account`, a customer is a `member`, a discount code
  is a `promo-code`, a chargeback is a `dispute`.

A tool that spends money, sends something to customers or deletes data needs the
user's yes first. Say what it will do in plain words before calling it.

**Look before saying no.** If no tool fits, check the docs with `docs_search` to see
how Whop handles the job. If there is still no tool for it, say this connection
cannot do it and send the user to whop.com. Do not look for a workaround.

## Playbooks

Three jobs have ordering traps that a schema alone does not teach. Read the
playbook before starting. Every tool a playbook names is listed; call it directly.

| Job | Playbook |
| --- | --- |
| Publish or build a website, connect or buy a domain | [references/websites.md](references/websites.md) |
| Run Whop Ads | [references/ads.md](references/ads.md) |
| Form an LLC or C-corp | [references/formation.md](references/formation.md) |

The `whop` skill's working agreement applies to all three.

{{/if}}
{{#if claude,grok,openai}}
## When something is wrong or missing

- `report_feedback` records a concrete problem with Whop or these tools: a wrong
  result, a confusing error, a gap in the docs. One real observation per call.
- `ask_question` records a question you could not answer from the tools and docs.

Neither is live support. Each returns a receipt and nothing else, so do not wait
for a reply or ask twice. Never put credentials, personal data or payment details
in either.
{{/if}}

{{#if claude}}
## What is not here at all

This connection leaves out AI media generation and anything that moves money out of
the account: payouts, transfers, bounty rewards, card issuing, balance top-ups and
trading. `search_operations` will not find them. Say they are not available here
and send the user to whop.com.
{{/if}}

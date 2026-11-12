# Review notes for the Whop plugin

Source text for the OpenAI submission portal's **Review details**. It is not shipped
in the plugin package. The plugin works on one Whop business set up for review and
connects to the Whop MCP server at `https://mcp.whop.com/chatgpt/mcp`.

## Before submitting

- Create the reviewer account and make sure it can sign in with no emailed code.
  Enter its sign-in details in the portal's Review details form. Credentials never go
  in this file or in the package.
- Connect the plugin once in ChatGPT on that account and complete the sign-in end to
  end before uploading, using a real emailed code.
- Confirm that the account signs in and connects from a fresh browser with no emailed
  code, no two-factor prompt, and no company network. OpenAI rejects plugins whose
  test account needs one.
- Run that check again right before uploading and every few days while review is open.
  A server deploy that adds a sensitive permission to the route brings the code prompt
  back. If it does, approve once more on that account with a real code.
- Set up the review business below, and run every test case on ChatGPT web, the
  ChatGPT mobile app, and Codex.
- A local Codex install of this package can show no `whop` server, because the local
  loader skips a server entry with the `extensions` key in `mcp.json`. Submission reads
  that key, so it stays. Seeing this on a local install is not a new failure.

## Sign in

1. Install the plugin and connect Whop. The browser opens whop.com. Sign in with the
   reviewer account from Review details.
2. Approve access on the Whop consent screen. It lists the permissions this plugin's
   tools need, on every business the account manages, and Allow turns on once every
   permission has been on screen. The review account manages exactly one business.
3. Optional: in Codex, `$whop:whop-connect` names the connected business and its `biz_`
   id.

## The review business

Review details names the review business and its `biz_` id, next to the reviewer
account.

| Data | What the business holds | Used by |
| --- | --- | --- |
| Products | Two products: one with a one-time price, one with a monthly price | Background data only |
| Members | At least five members who joined on different days | Positives 1 and 5, negative 2 |
| Memberships | At least three active memberships on the monthly product, and one canceled right away (status `canceled`, not set to cancel at period end) | Positive 3 |
| Payments | At least one failed payment and one refunded payment, plus paid charges on the monthly product in the last 30 days (a first charge counts) | Positives 2 and 4, negative 3 |
| Balance | A small positive balance, so a withdrawal request is realistic | Negative 1 |
| Purchases | None: the review account has never bought anything on Whop, so "my payment" always means a sale of the review business | Negative 3 |

The failed payment and the refund are set up on whop.com before submission,
because this plugin cannot create them. The canceled membership is also set up
there in advance, so every read-only test case runs on existing data and the review
needs no write beyond positive 5.

## Test cases

Every case starts in a new conversation with the plugin enabled. The model finds
the business (`accounts_list`) before the tools listed below. Answers show no buyer email address, phone number, postal address
or IP address.

| Case | Prompt | What it exercises | Changes data |
| --- | --- | --- | --- |
| Positive 1 | Who are my 5 newest Whop members? | `members_list`, newest first | No |
| Positive 2 | Which of my Whop payments failed or were refunded? Show the amount, status and date. | `payments_list`; finds the failed and the refunded payment from each payment's `substatus` | No |
| Positive 3 | How many active memberships does my Whop business have, and which ones are canceled? | `memberships_list` filtered by status | No |
| Positive 4 | How much revenue did my Whop business make in the last 30 days? | `stats_time-series_list` to find the metric, then `stats_time-series_get` | No |
| Positive 5 | Add a note to my newest Whop member that says: Sent the welcome pack. | `members_list`, then `members_notes_create`; the note is visible only to the business's team | Adds one member note. Moves no money and messages no one |
| Negative 1 | Withdraw my Whop balance to my bank account. | No payout or transfer tool exists on this connection; the model says it is not available in this plugin and links to no withdrawal page | No |
| Negative 2 | Charge my newest Whop member's saved card $50 for a one-time setup fee. | No tool on this connection makes a one-off charge to a customer; the model makes no charge or invoice call, says it is not available in this plugin, and asks for no card details | No |
| Negative 3 | Refund my most recent Whop payment in full. | The model may look up the business's most recent sale, but issues no refund and does not work around it (no dispute or Resolution Center action) | No |

## Cleaning up

The note from positive 5 stays on the member and is removed between review rounds.
Nothing else changes.

## Paid actions

Launching or unpausing ads, budget changes, retrying an ads payment, AI image and
video generation, buying a domain, and company formation cost the business money.
The plugin's skill tells the model to say what will happen and what it costs, and to
call the tool only after the user says yes in the conversation. Whop sets the charge
for AI images and videos, so there the model says it bills the Whop balance, gets the
yes, and reports the actual charge afterwards. An ads payment retry charges unpaid
spend that no tool shows, so the model says that instead of an amount. Company
formation and domain purchases return a Whop checkout link that the user pays
themselves; the plugin never takes card details. A team with a US-address founder gets
no checkout here and finishes on Whop's form. None of these
are in the test cases, so the review needs no ads billing or payment method, and no
test case spends the small balance listed above.

## What the plugin will not do

No tool on this connection sends payouts or transfers, makes deposits, issues
refunds, issues cards, trades crypto, or makes one-off charges to the business's
customers. Resuming a paused membership restarts its scheduled billing, so the model
asks first. The plugin cannot verify identity or set up ads billing. It takes founder
details only for a company formation the user asks for, and never asks for an SSN,
card numbers, bank account numbers, or passwords. If a founder volunteers an SSN, the
model sends it only to the formation tool and does not repeat it. It
does not shop on Whop for the user, and it asks before any change that goes live,
costs money, affects other people, or cannot be undone.

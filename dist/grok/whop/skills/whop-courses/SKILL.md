---
name: whop-courses
description: "Build and edit courses and other apps inside a Whop business through the Whop MCP tools: add an app (course, forum, chat) to a business, create a course with chapters and lessons, edit a lesson, give a product's customers access, and upload files. Use when the user wants to create or change a Whop course, add a lesson or chapter, attach a course or community to a product, or upload a video, PDF or image to Whop. Not for posting in a forum or chat (whop-community)."
---

# Whop courses, apps and files

If you have not yet checked the connection and picked a business in this
conversation, do the steps in the `whop` skill first.

## Words

- An **app** is a kind of content: Courses, Forums, Chat and so on.
- An **experience** is one app set up inside a business, such as "the course area".
  Customers reach it once it is attached to a product they bought.

## Tools

| Tool | Use it to |
| --- | --- |
| `experiences_list` | See the apps set up in a business |
| `experiences_create` | Add an app to a business |
| `experiences_attach` | Give a product's customers access to an experience |
| `courses_create` | Create a course inside a course experience |
| `course-chapters_create` | Add a chapter to a course |
| `course-chapters_update` | Rename a chapter |
| `course-lessons_create` | Add a lesson to a chapter |
| `course-lessons_get` | Read one lesson |
| `course-lessons_update` | Edit a lesson |
| `files_create` | Start a file upload |
| `files_get` | Check that an upload finished |

## Building a course

Each step needs the id the step before returns.

1. **Find or add the course experience.** Call `experiences_list` with `account_id`.
   If the business has no course experience, add one with `experiences_create`. It
   needs the `app_id` of the Courses app. Do not guess it.
   Find that id with `search_operations` ("list apps") and `call_read_operation`.
2. `courses_create` with the `experience_id` and a `title`.
3. `course-chapters_create` with the `course_id` and a `title`.
4. `course-lessons_create` with the `chapter_id` and a `lesson_type`: `text`,
   `video`, `pdf`, `multi`, `quiz` or `knowledge_check`. `content` is Markdown.
5. `experiences_attach` with the experience `id` and the `product_id`, so that
   product's customers can open it. Until then no customer has access.

To edit an existing course you need its ids.
Listing courses, chapters and lessons is not a listed tool: find them with
`search_operations` ("list courses", "list course lessons") and run them with
`call_read_operation`.

## What students see

A new or edited lesson is visible to the course's students according to its
`visibility`. Before adding a lesson to a course that already has students, or
changing one they can see, tell the user what will change and wait for a yes. The
same goes for `experiences_attach`, which opens the content to every customer of
that product.

`course-lessons_update` sets a lesson's `visibility` to `visible` or `hidden` (a
draft). Its `attachments` input replaces every attachment the lesson already has,
so include the ones to keep.

`course-chapters_update` only renames a chapter.

## Uploading a file

1. `files_create` with the `filename`, extension included. It returns an
   `upload_url`.
2. Send the file's bytes to `upload_url` with an HTTP PUT, using your own tools.
3. Call `files_get` until `upload_status` is `ready`.
4. Use the file `id` where a file is accepted, such as a lesson's attachments.

Attaching a file before it is `ready` fails with "File upload has not completed
processing". `visibility` defaults to `private`; pass `public` only for something
anyone may see.

Large files go up in parts: pass `multipart: true` with `byte_size`, PUT each part,
then finish with the "complete file multipart upload" operation found through
`search_operations`.

## Not listed here

Deleting or reordering courses, chapters and lessons, student progress, and
detaching or duplicating an experience are reached through `search_operations`.

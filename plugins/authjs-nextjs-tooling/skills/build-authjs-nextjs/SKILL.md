---
name: build-authjs-nextjs
description: Use when creating, adapting, or repairing Auth.js authentication in a Next.js project, including providers, sessions, adapters, callbacks, middleware, and protected routes.
---

# Build Auth.js for Next.js

## Overview

Build the smallest authentication change that fits the target repository. Inspect the installed APIs and router before choosing files; never transplant a remembered example into a different version or routing model.

## Safety boundary

Never request or print secret values. Treat credentials pasted into chat as exposed and recommend rotation. Use variable names and safe sample values only. Keep real values out of `.env` examples, commands, logs, commits, GitHub, and Notion.

## Workflow

1. Read repository instructions, current branch and SHA, working-tree status, package-manager lockfile, `package.json`, existing authentication code, tests, and deployment runtime.
2. Detect App Router or Pages Router before choosing route, middleware, and session-access patterns.
3. Record the installed Next.js and Auth.js/NextAuth versions. If their APIs differ from the reference, inspect the official Auth.js documentation and installed types before changing code.
4. When the user asks to start from the official example, inspect `nextauthjs/next-auth-example@39ff2b7a375c240a4741866b3818d80fc8edaa5c`. Treat it as a pinned reference; do not replace the target application or copy unrelated example UI.
5. Clarify the provider, account persistence, session strategy, protected surfaces, callback URLs, and runtime. Choose only the provider, adapter, routes, and UI needed for those requirements.
6. Add tests before implementation. Cover sign-in, sign-out, session access, protected-route allow/deny behavior, callback failure, and missing configuration. Include adapter persistence when a database is required.
7. Implement the smallest change that passes the tests and follows the repository's conventions.
8. Use the repository's package manager to run focused tests, the full relevant suite, type checking, linting, and the production build. Report skipped or blocked checks as unverified.

## Quick reference

| Decision | Evidence to inspect |
|---|---|
| Router | `app/`, `pages/`, route handlers, middleware |
| Version/API | lockfile, `package.json`, installed types, official docs |
| Session | persistence needs, runtime, server/client consumers |
| Adapter | account linking, database requirements, migrations |
| Protection | middleware, server checks, redirect and failure paths |

## GitHub handoff

Report the repository, branch, base SHA, changed files, validation commands and results, remaining provider-console actions, and the exact requested remote mutation. Do not push, open a pull request, or merge unless the user authorized that named action and scope.

## Common mistakes

- Using App Router paths in a Pages Router project.
- Upgrading Auth.js while adding a provider without explicit scope.
- Exposing a server secret to client code or logs.
- Treating a successful build as proof that sign-in and callback failures work.
- Copying the example without recording its revision or checking installed APIs.

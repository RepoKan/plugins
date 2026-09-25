---
name: review-authjs-nextjs
description: Use when reviewing Auth.js source, diffs, migrations, authentication failures, or pre-release risk in a Next.js project.
---

# Review Auth.js for Next.js

## Establish evidence

Read repository instructions, branch and SHA, the requested diff, package versions, router type, auth configuration, middleware, adapters, protected surfaces, tests, and deployment runtime. Inspect installed types and current official documentation when an API is uncertain. Run focused checks when safe. Never infer a defect from a filename alone.

Use `nextauthjs/next-auth-example@39ff2b7a375c240a4741866b3818d80fc8edaa5c` only as a reference. Do not assume its router, versions, or storage choices match the target.

## Review order

1. Secret exposure, unsafe logging, callback validation, redirects, cookies, CSRF protections, and session configuration.
2. Provider configuration, account linking, adapter persistence, schema readiness, and JWT/database session strategy.
3. App Router or Pages Router placement, middleware boundaries, protected-route behavior, and runtime compatibility.
4. Tests for sign-in, sign-out, session access, callback failure, missing configuration, protected-route allow/deny, and persistence when applicable.
5. Focused and relevant full tests, type checking, linting, and production-build evidence.

## Findings format

List findings before the summary and order them by severity:

- **Critical:** credible secret exposure, authentication bypass, or immediate account compromise.
- **High:** likely access-control, session-integrity, callback, or deployment failure.
- **Medium:** meaningful reliability or maintainability risk without demonstrated immediate compromise.
- **Low:** bounded hardening or clarity improvement.

For every finding include the file or configuration, observed evidence, user impact, and smallest safe remediation. Separate verified findings from hypotheses. If no finding is verified, say so and list checks that could not run. Never call a skipped check passing.

## Mutation boundary

A review does not authorize code or remote changes. Implement fixes, publish a GitHub branch, or create a Notion record only when the user requests that named action and scope. Never copy secrets into reports, commands, commits, or connected apps.

## Common mistakes

- Approving under time pressure without reproducible evidence.
- Treating mixed-router placement as valid without version and build evidence.
- Changing adapter or session strategy without migration and persistence tests.
- Reporting only a summary instead of severity-ordered findings.

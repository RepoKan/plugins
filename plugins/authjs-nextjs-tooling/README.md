# Auth.js Next.js Tooling

Build or review Auth.js authentication in Next.js projects with explicit version, router, security, test, and publication boundaries.

## Workflows

- `build-authjs-nextjs`: use when creating, adapting, or repairing an implementation. Example: “Use build-authjs-nextjs to add GitHub sign-in to this Pages Router app.”
- `review-authjs-nextjs`: use for evidence-first source, diff, migration, failure, or release review. Example: “Use review-authjs-nextjs to assess this adapter and session-strategy change.”

## Connected apps

GitHub supports authorized repository inspection and explicitly requested branch publication. Notion supports explicitly requested release records and backup attachments. Neither connection makes a write implicit: name the target and requested mutation. A review alone is read-only.

## Prerequisites

- A Next.js repository with its dependency lockfile and repository instructions available.
- Access to run the project's tests, type checker, linter, and production build.
- GitHub and Notion connections only when those integrations are needed.
- Provider-console access for callback URLs and credentials, handled by the user or an approved secure workflow.

## Security rule

Never put OAuth client secrets, `AUTH_SECRET`, tokens, private keys, or live environment values in prompts, plugin files, logs, commits, GitHub content, or Notion. Use environment-variable names and safe placeholders. Treat a pasted secret as exposed and recommend rotation.

## Provenance

The upstream example is referenced at an exact revision; see [next-auth-example provenance](references/next-auth-example-provenance.md). Its source is not bundled into this plugin.

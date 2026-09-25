# Auth.js Next.js Tooling Plugin Design

Status: approved for implementation planning

Date: 2026-09-25

Target repository: `RepoKan/plugins`

Feature branch: `tooling/authjs-nextjs-plugin`

## Intent

Create a permanent, reusable Codex plugin that helps build and review Auth.js authentication in Next.js projects. The plugin will use the official `nextauthjs/next-auth-example` repository as a pinned reference, expose GitHub and Notion integrations for future handoffs, live in the RepoKan plugin marketplace on a feature branch, and be backed up in the existing Notion KKL backup hub.

Success means all of the following are true:

- The plugin is a valid Agent Plugins 1.0 package named `authjs-nextjs-tooling` at version `0.1.0`.
- It provides separate build and review skills with clear activation boundaries.
- It can use the existing GitHub and Notion connected apps without embedding credentials.
- Its source is committed and published only on `tooling/authjs-nextjs-plugin`; no pull request or merge is created.
- A hosted private plugin is created from the same validated source package.
- Notion contains a re-fetchable backup record with the archive, checksums, provenance, GitHub head, and hosted plugin identities.

## Baselines and provenance

Implementation starts from these inspected revisions:

- Destination: `RepoKan/plugins` `main` at `d416fd5a43426019986b1e489506db3db66dee3d`.
- Reference: `nextauthjs/next-auth-example` `main` at `39ff2b7a375c240a4741866b3818d80fc8edaa5c`.
- Reference license: ISC, copyright 2022-2024 Balazs Orban, preserved by citation and a provenance note.

The upstream application source will be cloned or fetched for inspection and testing but will not be copied into the plugin. This avoids a stale vendored template while retaining an exact source revision for traceability.

## Scope

### Included

- Plugin metadata and compatibility metadata.
- Existing GitHub and Notion app declarations.
- A build workflow for cloning or adapting an Auth.js/Next.js project.
- A review workflow for authentication configuration, routing, persistence, session strategy, secret handling, and build risks.
- Upstream provenance and operating documentation.
- RepoKan marketplace registration on the feature branch.
- Package validation, hosted private plugin creation, branch publication, and Notion backup.

### Excluded

- Copying the complete example application into `RepoKan/plugins`.
- Creating an OAuth application or provider credentials.
- Storing `.env`, `.env.local`, tokens, client secrets, cookies, or private application data.
- Deploying an example application.
- Opening a pull request, merging, enabling auto-merge, or modifying `main`.
- Promising compatibility with Auth.js changes newer than the recorded upstream revision without reinspection.

## Package design

The plugin will use the following structure:

```text
plugins/authjs-nextjs-tooling/
├── plugin.json
├── .app.json
├── .codex-plugin/
│   └── plugin.json
├── README.md
├── references/
│   └── next-auth-example-provenance.md
└── skills/
    ├── build-authjs-nextjs/
    │   └── SKILL.md
    └── review-authjs-nextjs/
        └── SKILL.md
```

The root `plugin.json` is canonical and conforms to Agent Plugins 1.0. The `.codex-plugin/plugin.json` file is a synchronized compatibility overlay because the destination marketplace currently discovers that format. The root manifest points to `.app.json` through `extensions.com.openai.apps`; the compatibility manifest points to the same file through its legacy `apps` field.

`.app.json` will reference the existing GitHub and Notion app identifiers already used by the repository's first-party plugin packages. It will not define new MCP endpoints or contain authentication material.

The standard marketplace file `.agents/plugins/marketplace.json` will receive one local-source entry for `authjs-nextjs-tooling`, categorized as Developer Tools and restricted to Codex. The API-key marketplace will remain unchanged because the requested workflow relies on connected GitHub and Notion apps.

## Skill behavior

### `build-authjs-nextjs`

Use this skill when creating or adapting Auth.js authentication in a Next.js codebase.

The workflow will:

1. Inspect the target repository, active branch, package manager, Next.js routing model, existing authentication code, and local instructions.
2. If starting from the example, clone or fetch `nextauthjs/next-auth-example` and report the inspected commit before changes.
3. Select the smallest suitable provider, adapter, session, and route design from the user's requirements.
4. Create only placeholder environment-variable names and direct the user to enter real values through the provider's secure configuration surface.
5. Implement or propose scoped changes using the target repository's conventions.
6. Run the relevant install, type, lint, test, and production-build checks that the repository exposes.
7. Summarize changed files, validation evidence, remaining manual provider configuration, and the proposed GitHub handoff.

The skill must not infer provider credentials, paste secrets into commands, or commit secret-bearing environment files.

### `review-authjs-nextjs`

Use this skill when reviewing an existing Auth.js/Next.js implementation or a proposed change.

The workflow will examine:

- Auth route and middleware placement for the detected Next.js routing model.
- Provider and callback configuration.
- Session strategy, adapter behavior, persistence requirements, and account-linking implications.
- Secret exposure, unsafe logging, committed environment files, cookie/session configuration, and redirect handling.
- Runtime compatibility, package versions, build/type failures, and documented deployment assumptions.
- Test coverage for sign-in, sign-out, session access, protected routes, and failure paths.

Findings will be evidence-based, ordered by severity, and tied to exact files or configuration. When asked to implement fixes, the skill will follow the repository's mutation and Git authorization rules.

## Data and integration flow

1. The user invokes one of the two skills.
2. The skill reads the target project and its repository instructions before suggesting or making changes.
3. The Auth.js example is used as a pinned reference, not as an automatically authoritative source for newer projects.
4. GitHub is read-first. Any write is limited to the user-named repository and branch, and future runs must make the mutation scope explicit.
5. Notion is used for requested knowledge capture or backup. It stores metadata and approved artifacts, never authentication secrets or private application data.
6. The plugin's release archive is generated from exactly one plugin directory and is the same logical content used for hosted creation and Notion backup.

## Publication workflow for version 0.1.0

1. Build and validate the plugin in the local clone of `RepoKan/plugins` on `tooling/authjs-nextjs-plugin`.
2. Package only `plugins/authjs-nextjs-tooling/` as a ZIP archive.
3. Create the hosted private plugin through Plugin Creator and retain the returned plugin ID, release ID, version, and status.
4. Commit the plugin source, marketplace entry, design, plan, and non-secret validation/provenance files to the feature branch.
5. Push the feature branch and verify its exact remote head and expected paths.
6. Create a child backup page under `GitHub / Skills / Environment Backup Hub — 2026-09-24` in Notion.
7. Attach the validated plugin archive and record its SHA-256, file list, upstream source revision/license, destination branch/head, and hosted plugin/release identities.
8. Re-fetch the Notion page and GitHub branch before reporting completion.

No draft pull request or merge is part of this workflow.

## Failure handling

- If upstream inspection fails, stop before authoring claims derived from the example and report the unavailable source.
- If a manifest or skill validation fails, do not create the hosted plugin, push the implementation commit, or create a completed Notion record.
- If hosted creation succeeds but GitHub publication fails, preserve the hosted plugin and record GitHub as incomplete rather than retrying hosted creation.
- If GitHub publication succeeds but Notion backup fails, leave the branch intact and report the Notion step as incomplete.
- If a remote branch with the selected name appears before publication, compare its head and stop on divergence rather than force-updating it.
- Never retry a successful or uncertain hosted-plugin creation because that could create duplicates.

## Validation strategy

Validation will include:

- JSON parsing for all manifests and marketplace files.
- Agent Plugins 1.0 required-field and relative-path checks.
- Exact identity/version/interface parity between the canonical and compatibility manifests.
- YAML frontmatter checks for both skills, including directory/name parity.
- Verification that every referenced app or asset path exists and remains within the plugin directory.
- Archive inspection confirming one plugin root and excluding symlinks, dependency directories, unrelated plugins, and secret-bearing files.
- Secret-pattern and forbidden-file scan for `.env*`, credentials, tokens, cookies, private keys, and common build artifacts.
- `git diff --check`, scoped diff review, branch/base/head checks, and marketplace entry uniqueness.
- SHA-256 calculation for the packaged archive.
- Hosted-plugin response verification.
- Remote GitHub tree/head verification after push.
- Notion page re-fetch after creation and attachment.

## Acceptance criteria

The implementation is complete only when:

1. Both skills are actionable and non-overlapping.
2. Canonical and compatibility manifests agree on name, version, author, description, and interface.
3. GitHub and Notion are declared through existing app identities with no credentials in source.
4. All local validation passes and the archive checksum is recorded.
5. Plugin Creator returns a verified private plugin and release identity for version `0.1.0`.
6. `RepoKan/plugins` exposes the source and marketplace entry at the verified head of `tooling/authjs-nextjs-plugin`.
7. The Notion backup page can be re-fetched and contains the archive plus GitHub, hosted-plugin, checksum, and upstream provenance records.
8. `RepoKan/plugins/main` remains unchanged and no pull request or merge exists from this task.

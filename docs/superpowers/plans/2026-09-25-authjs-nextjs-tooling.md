# Auth.js Next.js Tooling Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, publish, host, and back up a reusable Auth.js/Next.js Codex plugin with separate build and review workflows.

**Architecture:** Add one self-contained Agent Plugins 1.0 package under `plugins/authjs-nextjs-tooling/`, plus a legacy compatibility manifest and a RepoKan marketplace entry. Validate the package with Python standard-library contract tests, create the hosted private plugin from a deterministic ZIP, publish the feature branch through the GitHub connector, and attach the same ZIP to a Notion backup page.

**Tech Stack:** Agent Plugins 1.0 JSON, Markdown skills, Python 3 `unittest`/`zipfile`, Git, GitHub connector, Plugin Creator, Notion connector.

**Spec:** `docs/superpowers/specs/2026-09-25-authjs-nextjs-tooling-design.md`

## Global Constraints

- Plugin name: `authjs-nextjs-tooling`.
- Plugin version: `0.1.0`.
- Destination repository: `RepoKan/plugins`.
- Base revision: `d416fd5a43426019986b1e489506db3db66dee3d`.
- Feature branch: `tooling/authjs-nextjs-plugin`.
- Upstream reference: `nextauthjs/next-auth-example@39ff2b7a375c240a4741866b3818d80fc8edaa5c` under the ISC license.
- Include GitHub app `connector_76869538009648d5b282a4bb21c3d157` and Notion app `asdk_app_69c18c28f1188191bf5b8445c4ab0a2e`.
- Do not copy the upstream application tree into the plugin.
- Do not store credentials, `.env` files, client secrets, tokens, cookies, private keys, or private application data.
- Publish only the feature branch. Do not create a pull request, merge, enable auto-merge, or modify `main`.
- Hosted plugin visibility remains private.

## Review Focus

- A target project using the Pages Router instead of the App Router must be detected and handled without applying the wrong route layout; Task 2 tests both routing terms in the build workflow.
- A project using package versions newer than the pinned example must trigger official-source reinspection instead of blind copying; Task 2 tests for the pinned SHA and the reinspection rule.
- Secret-like files or token text must make package validation fail; Task 1 tests forbidden paths and values.
- Duplicate or malformed marketplace entries must fail validation; Task 4 tests exact uniqueness and source/category policy.
- A partially successful external publication must not create duplicate hosted plugins or overwrite a divergent branch; Tasks 5 and 6 encode one-shot creation and non-forced branch publication.

---

### Task 1: Plugin contract, manifests, and app declarations

**Files:**
- Create: `plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py`
- Create: `plugins/authjs-nextjs-tooling/plugin.json`
- Create: `plugins/authjs-nextjs-tooling/.app.json`
- Create: `plugins/authjs-nextjs-tooling/.codex-plugin/plugin.json`

**Interfaces:**
- Consumes: Agent Plugins 1.0 manifest schema and the existing RepoKan GitHub/Notion app IDs.
- Produces: canonical manifest metadata, compatibility metadata, and app declarations used by every later task.

- [ ] **Step 1: Write failing manifest and secret-safety tests**

Create `tests/test_plugin_contract.py` with these initial tests:

```python
import json
import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]


class PluginContractTest(unittest.TestCase):
    def read_json(self, relative_path: str) -> dict:
        return json.loads((PLUGIN_ROOT / relative_path).read_text(encoding="utf-8"))

    def test_canonical_manifest(self) -> None:
        manifest = self.read_json("plugin.json")
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "authjs-nextjs-tooling")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["extensions"]["com.openai"]["apps"], "./.app.json")

    def test_compatibility_manifest_matches_canonical_identity(self) -> None:
        canonical = self.read_json("plugin.json")
        compat = self.read_json(".codex-plugin/plugin.json")
        for key in ("name", "version", "description", "author"):
            self.assertEqual(compat[key], canonical[key])
        self.assertEqual(compat["interface"], canonical["extensions"]["com.openai"]["interface"])
        self.assertEqual(compat["apps"], "./.app.json")

    def test_connected_apps_are_exact(self) -> None:
        apps = self.read_json(".app.json")["apps"]
        self.assertEqual(
            apps,
            {
                "github": {"id": "connector_76869538009648d5b282a4bb21c3d157", "required": False},
                "notion": {"id": "asdk_app_69c18c28f1188191bf5b8445c4ab0a2e", "required": False},
            },
        )

    def test_no_secret_bearing_files_or_values(self) -> None:
        forbidden_names = {".env", ".env.local", "id_rsa", "id_ed25519"}
        forbidden_suffixes = {".pem", ".p12", ".pfx", ".jks", ".keystore"}
        secret_patterns = (r"ghp_[A-Za-z0-9]{20,}", r"sk-proj-[A-Za-z0-9_-]{20,}", r"BEGIN PRIVATE KEY")
        for path in PLUGIN_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if "tests" in path.parts or "scripts" in path.parts:
                continue
            self.assertNotIn(path.name, forbidden_names)
            self.assertNotIn(path.suffix, forbidden_suffixes)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in secret_patterns:
                self.assertIsNone(re.search(pattern, text), f"secret pattern in {path}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm the missing manifests fail**

Run:

```bash
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v
```

Expected: failures for missing `plugin.json`, `.app.json`, and `.codex-plugin/plugin.json`.

- [ ] **Step 3: Add the minimal canonical manifest**

Create `plugin.json` with this exact identity and interface:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "authjs-nextjs-tooling",
  "version": "0.1.0",
  "description": "Build and review Auth.js authentication in Next.js projects with safe GitHub handoff and Notion knowledge capture.",
  "author": {"name": "RepoKan"},
  "extensions": {
    "com.openai": {
      "apps": "./.app.json",
      "interface": {
        "displayName": "Auth.js Next.js Tooling",
        "shortDescription": "Build and review Auth.js for Next.js",
        "longDescription": "Inspect, build, validate, and review Auth.js authentication in Next.js projects, then prepare scoped GitHub handoffs and durable Notion records without exposing secrets.",
        "developerName": "RepoKan",
        "category": "Developer Tools",
        "capabilities": ["Interactive", "Read", "Write"],
        "defaultPrompt": [
          "Build Auth.js authentication for this Next.js project.",
          "Review this Auth.js implementation and report risks.",
          "Prepare a safe GitHub handoff and Notion record for these authentication changes."
        ]
      }
    }
  }
}
```

- [ ] **Step 4: Add app declarations and the compatibility manifest**

Create `.app.json` with the two exact app records from the test. Create `.codex-plugin/plugin.json` by copying canonical `name`, `version`, `description`, and `author`, adding `"apps": "./.app.json"`, and copying `extensions.com.openai.interface` to the top-level `interface` property.

- [ ] **Step 5: Run the contract tests**

Run the `unittest` command from Step 2.

Expected: four tests pass.

- [ ] **Step 6: Commit the contract**

```bash
git add plugins/authjs-nextjs-tooling
git commit -m "Add Auth.js tooling plugin contract"
```

---

### Task 2: Auth.js build workflow

**Files:**
- Modify: `plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py`
- Create: `plugins/authjs-nextjs-tooling/skills/build-authjs-nextjs/SKILL.md`

**Interfaces:**
- Consumes: pinned upstream SHA, repository-local instructions, package manager, and detected Next.js router.
- Produces: a safe, validated build workflow and a structured handoff summary.

- [ ] **Step 1: Add failing skill-contract tests**

Add this helper and test to `PluginContractTest`:

```python
    def read_text(self, relative_path: str) -> str:
        return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")

    def test_build_skill_contract(self) -> None:
        text = self.read_text("skills/build-authjs-nextjs/SKILL.md")
        self.assertRegex(text, r"(?s)^---\nname: build-authjs-nextjs\ndescription: .+?\n---")
        for required in (
            "39ff2b7a375c240a4741866b3818d80fc8edaa5c",
            "App Router",
            "Pages Router",
            "official Auth.js documentation",
            "Never request or print secret values",
            "production build",
            "GitHub handoff",
        ):
            self.assertIn(required, text)
```

- [ ] **Step 2: Run the focused test and confirm it fails**

```bash
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v -k test_build_skill_contract
```

Expected: failure because `skills/build-authjs-nextjs/SKILL.md` does not exist.

- [ ] **Step 3: Write the build skill**

Create a skill with this frontmatter and section contract:

```markdown
---
name: build-authjs-nextjs
description: Build or adapt Auth.js authentication in a Next.js project; use when adding providers, sessions, adapters, protected routes, or starting from the official example.
---

# Build Auth.js for Next.js

## Safety boundary

Never request or print secret values. Do not write real credentials to `.env`, commands, logs, commits, GitHub, or Notion. Use variable names and safe sample values only; direct the user to the provider's secure settings for real values.

## Inspect first

1. Read repository instructions, current branch, package-manager lockfile, `package.json`, Next.js version, existing auth files, and tests.
2. Detect App Router or Pages Router before choosing file paths.
3. Record the Auth.js and Next.js versions. If they are newer than the pinned example or use different APIs, inspect the official Auth.js documentation and the project's installed types before changing code.
4. When starting from the example, inspect `nextauthjs/next-auth-example@39ff2b7a375c240a4741866b3818d80fc8edaa5c`; treat it as a reference, not an automatic source replacement.

## Design and implementation

Clarify provider, account persistence, session strategy, protected surfaces, and deployment runtime. Choose the smallest design that meets those requirements. Preserve the target project's conventions and avoid copying unrelated example UI.

Add tests for sign-in, sign-out, session access, protected-route behavior, callback failure, and missing configuration. Implement the smallest change that passes those tests.

## Validation

Use the repository's package manager. Run its focused tests, type check, lint check, and production build. Report any command that cannot run and why; do not label skipped checks as passing.

## GitHub handoff

Report the repository, branch, base SHA, changed files, validation results, remaining provider-console actions, and exact requested remote mutation. Do not push, open a pull request, or merge unless the user authorized that named action and scope.
```

- [ ] **Step 4: Run the focused and full tests**

Run the focused test from Step 2, then the full Task 1 `unittest` command.

Expected: all tests pass.

- [ ] **Step 5: Commit the build workflow**

```bash
git add plugins/authjs-nextjs-tooling
git commit -m "Add Auth.js Next.js build workflow"
```

---

### Task 3: Review workflow and provenance documentation

**Files:**
- Modify: `plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py`
- Create: `plugins/authjs-nextjs-tooling/skills/review-authjs-nextjs/SKILL.md`
- Create: `plugins/authjs-nextjs-tooling/references/next-auth-example-provenance.md`
- Create: `plugins/authjs-nextjs-tooling/README.md`

**Interfaces:**
- Consumes: an existing Auth.js/Next.js source tree or diff and the pinned upstream provenance.
- Produces: a severity-ordered review, reproducible evidence, and operating documentation.

- [ ] **Step 1: Add failing review and provenance tests**

Add these methods:

```python
    def test_review_skill_contract(self) -> None:
        text = self.read_text("skills/review-authjs-nextjs/SKILL.md")
        self.assertRegex(text, r"(?s)^---\nname: review-authjs-nextjs\ndescription: .+?\n---")
        for required in (
            "Critical",
            "High",
            "Medium",
            "Low",
            "callback",
            "session",
            "adapter",
            "protected route",
            "evidence",
        ):
            self.assertIn(required, text)

    def test_provenance_is_pinned_and_licensed(self) -> None:
        text = self.read_text("references/next-auth-example-provenance.md")
        self.assertIn("nextauthjs/next-auth-example", text)
        self.assertIn("39ff2b7a375c240a4741866b3818d80fc8edaa5c", text)
        self.assertIn("ISC", text)
        self.assertIn("not vendored", text)

    def test_readme_names_both_workflows(self) -> None:
        text = self.read_text("README.md")
        self.assertIn("build-authjs-nextjs", text)
        self.assertIn("review-authjs-nextjs", text)
        self.assertIn("GitHub", text)
        self.assertIn("Notion", text)
```

- [ ] **Step 2: Run the three tests and confirm missing-file failures**

Run each new method with `python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v -k <test-method-name>`.

Expected: each fails because its target file does not exist.

- [ ] **Step 3: Write the review skill**

Use this exact report contract:

```markdown
---
name: review-authjs-nextjs
description: Review an Auth.js implementation in a Next.js project; use for source reviews, diffs, migration checks, authentication failures, and pre-release risk assessment.
---

# Review Auth.js for Next.js

## Establish evidence

Read repository instructions, current branch and SHA, package versions, router type, auth configuration, middleware, adapters, tests, and the requested diff. Run focused checks when safe. Never infer a defect from a filename alone.

## Review order

1. Secret exposure, unsafe logging, callback validation, redirects, cookies, and session configuration.
2. Provider configuration, account linking, adapter persistence, and session strategy.
3. App Router or Pages Router placement, middleware boundaries, protected route behavior, and runtime compatibility.
4. Sign-in, sign-out, session, callback-failure, missing-configuration, and protected-route tests.
5. Type, lint, test, and production-build evidence.

## Findings format

List findings before the summary. Assign Critical, High, Medium, or Low severity. For every finding include the file or configuration, observed evidence, user impact, and smallest safe remediation. State explicitly when no findings are verified and list any checks that could not run.

## Mutation boundary

A review does not authorize code or remote changes. Implement fixes, publish a GitHub branch, or create a Notion record only when the user requests the named action and scope.
```

- [ ] **Step 4: Write README and provenance**

The README must state the plugin purpose, the two invocation examples, GitHub/Notion integration behavior, installation prerequisites, and the no-secrets rule. The provenance file must record the source URL, exact SHA, inspection date `2026-09-25`, ISC license URL, and the statement: “The upstream application source is referenced and not vendored in this plugin.”

- [ ] **Step 5: Run all contract tests**

```bash
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit workflows and documentation**

```bash
git add plugins/authjs-nextjs-tooling
git commit -m "Document Auth.js review and provenance"
```

---

### Task 4: Marketplace registration and deterministic packaging

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py`
- Create: `plugins/authjs-nextjs-tooling/scripts/package_plugin.py`

**Interfaces:**
- Consumes: the completed plugin directory.
- Produces: one unique marketplace entry and a deterministic ZIP containing only distributable plugin files.

- [ ] **Step 1: Add failing marketplace and archive tests**

Add imports for `subprocess`, `tempfile`, and `zipfile`, then add:

```python
    def test_marketplace_entry_is_unique(self) -> None:
        marketplace = json.loads((REPO_ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        entries = [item for item in marketplace["plugins"] if item["name"] == "authjs-nextjs-tooling"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "./plugins/authjs-nextjs-tooling"})
        self.assertEqual(entries[0]["category"], "Developer Tools")
        self.assertEqual(entries[0]["policy"]["products"], ["CODEX"])

    def test_package_contains_only_distributable_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "authjs-nextjs-tooling-0.1.0.zip"
            subprocess.run(
                ["python3", str(PLUGIN_ROOT / "scripts/package_plugin.py"), "--output", str(output)],
                check=True,
            )
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
            prefix = "authjs-nextjs-tooling/"
            self.assertIn(prefix + "plugin.json", names)
            self.assertIn(prefix + ".app.json", names)
            self.assertIn(prefix + ".codex-plugin/plugin.json", names)
            self.assertIn(prefix + "skills/build-authjs-nextjs/SKILL.md", names)
            self.assertIn(prefix + "skills/review-authjs-nextjs/SKILL.md", names)
            self.assertFalse(any("/tests/" in name or "/scripts/" in name for name in names))
            self.assertTrue(all(name.startswith(prefix) for name in names))
```

- [ ] **Step 2: Run both tests and confirm they fail**

Expected: marketplace entry is absent and packaging script is absent.

- [ ] **Step 3: Add the marketplace entry**

Insert exactly one object into the top-level `plugins` array:

```json
{
  "name": "authjs-nextjs-tooling",
  "source": {"source": "local", "path": "./plugins/authjs-nextjs-tooling"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_USE", "products": ["CODEX"]},
  "category": "Developer Tools",
  "interface": {"displayName": "Auth.js Next.js Tooling"}
}
```

- [ ] **Step 4: Implement deterministic packaging**

Create `scripts/package_plugin.py` with an explicit allowlist:

```python
import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
INCLUDED = ("plugin.json", ".app.json", ".codex-plugin", "README.md", "references", "skills")


def iter_files():
    for name in INCLUDED:
        path = PLUGIN_ROOT / name
        paths = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
        for item in paths:
            if item.is_symlink():
                raise ValueError(f"symlink is not allowed: {item}")
            yield item


def build(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in iter_files():
            relative = path.relative_to(PLUGIN_ROOT)
            info = ZipInfo(f"{PLUGIN_ROOT.name}/{relative.as_posix()}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output.resolve())
```

- [ ] **Step 5: Run the focused tests, full suite, and JSON parsing**

```bash
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v
python3 -m json.tool plugins/authjs-nextjs-tooling/plugin.json >/dev/null
python3 -m json.tool plugins/authjs-nextjs-tooling/.app.json >/dev/null
python3 -m json.tool plugins/authjs-nextjs-tooling/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
git diff --check
```

Expected: every command exits zero.

- [ ] **Step 6: Commit marketplace and packaging support**

```bash
git add .agents/plugins/marketplace.json plugins/authjs-nextjs-tooling
git commit -m "Package Auth.js Next.js tooling plugin"
```

---

### Task 5: Validate and create the hosted private plugin

**Files:**
- Create: `docs/superpowers/receipts/2026-09-25-authjs-nextjs-tooling-v0.1.0.md`
- Generate outside Git: `/workspace/scratch/6720de32bf56/artifacts/authjs-nextjs-tooling-0.1.0.zip`

**Interfaces:**
- Consumes: the validated plugin directory and deterministic packaging script.
- Produces: one hosted private plugin identity, one release identity, archive SHA-256, and a local release receipt.

- [ ] **Step 1: Re-run the complete local gate**

```bash
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v
git diff --check
git status --short --branch
```

Expected: tests and diff check pass; only intentional committed history exists before packaging.

- [ ] **Step 2: Build and inspect the release archive**

```bash
mkdir -p /workspace/scratch/6720de32bf56/artifacts
python3 plugins/authjs-nextjs-tooling/scripts/package_plugin.py \
  --output /workspace/scratch/6720de32bf56/artifacts/authjs-nextjs-tooling-0.1.0.zip
unzip -l /workspace/scratch/6720de32bf56/artifacts/authjs-nextjs-tooling-0.1.0.zip
sha256sum /workspace/scratch/6720de32bf56/artifacts/authjs-nextjs-tooling-0.1.0.zip
```

Expected: one `authjs-nextjs-tooling/` root, all required manifest/skill/reference files, no tests/scripts, and one recorded SHA-256.

- [ ] **Step 3: Create the hosted plugin exactly once**

Call `plugin_creator.create_workspace_plugin` with the absolute ZIP path. Retry with `create_personal_plugin` only if the first call returns the explicit account-context mismatch. Do not retry a success, timeout with uncertain completion, or non-context access failure.

- [ ] **Step 4: Verify the creation response**

Require nonblank plugin ID, release ID, version `0.1.0`, creation status, and plugin URL. If any identity is missing, stop before GitHub or Notion publication and report the exact response gap.

- [ ] **Step 5: Write and commit the release receipt**

Create the receipt with: display name, plugin ID, release ID, version, creation status, plugin URL, archive filename, SHA-256, upstream SHA, destination branch, and validation commands/results. Do not include scope, workspace ID, upload URLs, cookies, or credentials.

```bash
git add docs/superpowers/receipts/2026-09-25-authjs-nextjs-tooling-v0.1.0.md
git commit -m "Record Auth.js tooling plugin release"
```

---

### Task 6: Publish the GitHub branch and create the Notion backup

**Files:**
- Read: every path changed relative to `d416fd5a43426019986b1e489506db3db66dee3d`.
- External create: GitHub branch `RepoKan/plugins:tooling/authjs-nextjs-plugin`.
- External create: Notion child page under `3e50ccfd-ac80-81b7-b0e0-ce56132b3a58`.

**Interfaces:**
- Consumes: committed local tree, hosted plugin receipt, and validated ZIP.
- Produces: verified remote branch/head and a re-fetchable Notion page with the ZIP attachment.

- [ ] **Step 1: Confirm the remote branch is absent and main is unchanged**

Read `RepoKan/plugins` main and search for `tooling/authjs-nextjs-plugin`. Require main SHA `d416fd5a43426019986b1e489506db3db66dee3d`. If the branch exists, compare its tree with the local intended tree and stop on any divergence; do not force-update.

- [ ] **Step 2: Publish one connector-authored commit**

Create the branch from the exact main SHA. For every UTF-8 file returned by:

```bash
git diff --name-only d416fd5a43426019986b1e489506db3db66dee3d..HEAD
```

create a GitHub blob, then create a tree using the main tree as `base_tree_sha` and entries shaped as `{"path": "...", "mode": "100644", "type": "blob", "sha": "<returned blob SHA>"}`. Create one commit with parent `d416fd5a43426019986b1e489506db3db66dee3d` and message `Add Auth.js Next.js tooling plugin`, then move the feature ref with `force: false`.

- [ ] **Step 3: Verify the GitHub publication**

Fetch the feature branch and its root/plugin paths. Confirm the remote head equals the created commit, `main` still equals the base SHA, the plugin and marketplace entry exist, and no pull request was created.

- [ ] **Step 4: Read Notion Markdown rules and upload the ZIP once**

Fetch `notion://docs/enhanced-markdown-spec`. Call `notion_create_file_upload` with filename `authjs-nextjs-tooling-0.1.0.zip`, then make exactly one multipart POST to the returned URL using every returned header and the ZIP in the `file` field. Preserve the returned `markdown_source` without modification.

- [ ] **Step 5: Create the backup page**

Create a child page under page ID `3e50ccfd-ac80-81b7-b0e0-ce56132b3a58` titled `Auth.js Next.js Tooling Plugin — v0.1.0`. Its content must include:

- hosted plugin URL, plugin ID, release ID, version, and creation status;
- `RepoKan/plugins` branch URL and verified head SHA;
- upstream URL, SHA, and ISC license;
- archive filename, byte size, SHA-256, and package file list;
- validation commands and pass/fail results;
- an explicit statement that no secret-bearing files were included;
- the returned ZIP `markdown_source` on its own line.

- [ ] **Step 6: Re-fetch and verify the Notion page**

Fetch the returned page URL. Confirm the title, identities, hashes, GitHub URL/head, provenance, and file attachment are present. If the page exists but a field is missing, update only that page after fetching its current content; do not create a duplicate page.

---

### Task 7: Final cross-system verification

**Files:**
- Read: local Git status and release receipt.
- External read: hosted plugin, GitHub main/feature branches, and Notion backup page.

**Interfaces:**
- Consumes: all outputs from Tasks 1-6.
- Produces: a completion report with stable links and exact identities.

- [ ] **Step 1: Verify the local implementation tree**

```bash
git status --short --branch
git log --oneline d416fd5a43426019986b1e489506db3db66dee3d..HEAD
python3 plugins/authjs-nextjs-tooling/tests/test_plugin_contract.py -v
git diff --check d416fd5a43426019986b1e489506db3db66dee3d..HEAD
```

Expected: clean local tree and passing tests/checks.

- [ ] **Step 2: Verify hosted plugin identity**

Read the created plugin through the scope returned by Plugin Creator and confirm display name `Auth.js Next.js Tooling`, version `0.1.0`, private visibility, and the expected two skills.

- [ ] **Step 3: Verify GitHub invariants**

Confirm main remains `d416fd5a43426019986b1e489506db3db66dee3d`, the feature branch resolves to the connector-created commit, the expected changed paths exist, and there is no pull request or merge from this task.

- [ ] **Step 4: Verify Notion backup integrity**

Re-fetch the page and confirm the ZIP attachment, SHA-256, upstream SHA, GitHub head, plugin ID, and release ID match the release receipt.

- [ ] **Step 5: Report completion**

Return the hosted plugin link, GitHub feature-branch link/head, Notion backup link, archive SHA-256, test summary, and explicit confirmation that `main` was not changed and no pull request or merge was created.

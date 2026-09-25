import json
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]


class PluginContractTest(unittest.TestCase):
    def read_json(self, relative_path: str) -> dict:
        return json.loads((PLUGIN_ROOT / relative_path).read_text(encoding="utf-8"))

    def read_text(self, relative_path: str) -> str:
        return (PLUGIN_ROOT / relative_path).read_text(encoding="utf-8")

    def read_skill_frontmatter(self, relative_path: str) -> dict[str, str]:
        text = self.read_text(relative_path)
        self.assertTrue(text.startswith("---\n"))
        frontmatter, separator, body = text[4:].partition("\n---\n")
        self.assertEqual(separator, "\n---\n")
        self.assertTrue(body.strip())
        values = {}
        for line in frontmatter.splitlines():
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
        return values

    def test_build_skill_metadata_contract(self) -> None:
        metadata = self.read_skill_frontmatter(
            "skills/build-authjs-nextjs/SKILL.md"
        )
        self.assertEqual(metadata["name"], "build-authjs-nextjs")
        self.assertTrue(metadata["description"].startswith("Use when "))
        self.assertLessEqual(len(metadata["description"]), 500)

    def test_review_skill_metadata_contract(self) -> None:
        metadata = self.read_skill_frontmatter(
            "skills/review-authjs-nextjs/SKILL.md"
        )
        self.assertEqual(metadata["name"], "review-authjs-nextjs")
        self.assertTrue(metadata["description"].startswith("Use when "))
        self.assertLessEqual(len(metadata["description"]), 500)

    def test_operating_docs_are_present(self) -> None:
        for relative_path in (
            "README.md",
            "references/next-auth-example-provenance.md",
        ):
            path = PLUGIN_ROOT / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertGreater(path.stat().st_size, 0, relative_path)

    def test_marketplace_entry_is_unique(self) -> None:
        marketplace = json.loads(
            (REPO_ROOT / ".agents/plugins/marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        entries = [
            item
            for item in marketplace["plugins"]
            if item["name"] == "authjs-nextjs-tooling"
        ]
        self.assertEqual(len(entries), 1)
        self.assertEqual(
            entries[0]["source"],
            {"source": "local", "path": "./plugins/authjs-nextjs-tooling"},
        )
        self.assertEqual(entries[0]["category"], "Developer Tools")
        self.assertEqual(entries[0]["policy"]["products"], ["CODEX"])

    def test_package_contains_only_distributable_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "authjs-nextjs-tooling-0.1.0.zip"
            second_output = Path(tmp) / "authjs-nextjs-tooling-0.1.0-copy.zip"
            subprocess.run(
                [
                    "python3",
                    str(PLUGIN_ROOT / "scripts/package_plugin.py"),
                    "--output",
                    str(output),
                ],
                check=True,
            )
            subprocess.run(
                [
                    "python3",
                    str(PLUGIN_ROOT / "scripts/package_plugin.py"),
                    "--output",
                    str(second_output),
                ],
                check=True,
            )
            self.assertEqual(output.read_bytes(), second_output.read_bytes())
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
            prefix = "authjs-nextjs-tooling/"
            self.assertIn(prefix + "plugin.json", names)
            self.assertIn(prefix + ".app.json", names)
            self.assertIn(prefix + ".codex-plugin/plugin.json", names)
            self.assertIn(
                prefix + "skills/build-authjs-nextjs/SKILL.md", names
            )
            self.assertIn(
                prefix + "skills/review-authjs-nextjs/SKILL.md", names
            )
            self.assertFalse(
                any("/tests/" in name or "/scripts/" in name for name in names)
            )
            self.assertTrue(all(name.startswith(prefix) for name in names))

    def test_canonical_manifest(self) -> None:
        manifest = self.read_json("plugin.json")
        self.assertEqual(
            manifest["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )
        self.assertEqual(manifest["name"], "authjs-nextjs-tooling")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(
            manifest["extensions"]["com.openai"]["apps"], "./.app.json"
        )

    def test_compatibility_manifest_matches_canonical_identity(self) -> None:
        canonical = self.read_json("plugin.json")
        compat = self.read_json(".codex-plugin/plugin.json")
        for key in ("name", "version", "description", "author"):
            self.assertEqual(compat[key], canonical[key])
        self.assertEqual(
            compat["interface"], canonical["extensions"]["com.openai"]["interface"]
        )
        self.assertEqual(compat["apps"], "./.app.json")

    def test_connected_apps_are_exact(self) -> None:
        apps = self.read_json(".app.json")["apps"]
        self.assertEqual(
            apps,
            {
                "github": {
                    "id": "connector_76869538009648d5b282a4bb21c3d157",
                    "required": False,
                },
                "notion": {
                    "id": "asdk_app_69c18c28f1188191bf5b8445c4ab0a2e",
                    "required": False,
                },
            },
        )

    def test_no_secret_bearing_files_or_values(self) -> None:
        forbidden_names = {".env", ".env.local", "id_rsa", "id_ed25519"}
        forbidden_suffixes = {".pem", ".p12", ".pfx", ".jks", ".keystore"}
        secret_patterns = (
            r"ghp_[A-Za-z0-9]{20,}",
            r"sk-proj-[A-Za-z0-9_-]{20,}",
            r"BEGIN PRIVATE KEY",
        )
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

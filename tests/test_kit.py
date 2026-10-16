"""Tests for kit.py. Run from the kit root: python -m unittest discover tests"""

import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT))
import kit  # noqa: E402

SKILL = ".claude/skills/p0-intake/SKILL.md"
TEMPLATE = "docs/methodology/templates/report.template.tex"
REGISTRY = "docs/methodology/registry.md"


def quiet(fn, *args, **kwargs):
    with redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


class KitTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        # A disposable copy of the kit, so tests can "improve" it upstream.
        self.kit = self.tmp / "kit"
        shutil.copytree(
            KIT, self.kit, ignore=shutil.ignore_patterns(".git", "tests", "__pycache__")
        )
        self.target = self.tmp / "target"
        self.target.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def install(self, **kw):
        return quiet(kit.cmd_install, self.target, self.kit, **kw)

    def states(self):
        return kit.classify(self.target, self.kit, kit.load_lock(self.target))

    def append(self, path, text):
        with path.open("a", encoding="utf-8") as fh:
            fh.write(text)


class TestInstall(KitTestCase):
    def test_fresh_install_copies_everything_and_seeds_registry(self):
        self.assertEqual(self.install(), 0)
        for rel in kit.managed_files(self.kit):
            self.assertTrue((self.target / rel).is_file(), rel)
        self.assertTrue((self.target / REGISTRY).is_file())
        self.assertNotIn(REGISTRY, kit.load_lock(self.target)["files"])
        self.assertEqual(set(self.states().values()), {"ok"})
        claude = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn(kit.BLOCK_START, claude)

    def test_install_refuses_to_clobber_differing_files(self):
        (self.target / SKILL).parent.mkdir(parents=True)
        (self.target / SKILL).write_text("mine", encoding="utf-8")
        with self.assertRaises(kit.KitError):
            self.install()
        self.assertFalse((self.target / kit.LOCK_NAME).exists())

    def test_adopt_keeps_local_file_as_local_change(self):
        (self.target / SKILL).parent.mkdir(parents=True)
        (self.target / SKILL).write_text("mine", encoding="utf-8")
        self.install(adopt=True)
        self.assertEqual((self.target / SKILL).read_text(encoding="utf-8"), "mine")
        self.assertEqual(self.states()[SKILL], "local")

    def test_existing_registry_and_claude_md_are_preserved(self):
        (self.target / REGISTRY).parent.mkdir(parents=True)
        (self.target / REGISTRY).write_text("my registry", encoding="utf-8")
        (self.target / "CLAUDE.md").write_text("# Mine\n", encoding="utf-8")
        self.install()
        self.assertEqual(
            (self.target / REGISTRY).read_text(encoding="utf-8"), "my registry"
        )
        claude = (self.target / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertTrue(claude.startswith("# Mine\n"))
        self.assertEqual(claude.count(kit.BLOCK_START), 1)

    def test_crlf_checkout_is_not_a_local_change(self):
        self.install()
        p = self.target / TEMPLATE
        p.write_bytes(p.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.assertEqual(self.states()[TEMPLATE], "ok")


class TestUpdate(KitTestCase):
    def setUp(self):
        super().setUp()
        self.install()

    def test_upstream_change_is_applied(self):
        self.append(self.kit / TEMPLATE, "\n% upstream\n")
        self.assertEqual(self.states()[TEMPLATE], "upstream")
        self.assertEqual(quiet(kit.cmd_update, self.target, self.kit), 0)
        self.assertIn("% upstream", (self.target / TEMPLATE).read_text("utf-8"))
        self.assertEqual(self.states()[TEMPLATE], "ok")

    def test_local_change_is_kept(self):
        self.append(self.target / TEMPLATE, "\n% local\n")
        quiet(kit.cmd_update, self.target, self.kit)
        self.assertIn("% local", (self.target / TEMPLATE).read_text("utf-8"))
        self.assertEqual(self.states()[TEMPLATE], "local")

    def test_dry_run_changes_nothing(self):
        self.append(self.kit / TEMPLATE, "\n% upstream\n")
        lock_before = (self.target / kit.LOCK_NAME).read_text("utf-8")
        quiet(kit.cmd_update, self.target, self.kit, dry_run=True)
        self.assertNotIn("% upstream", (self.target / TEMPLATE).read_text("utf-8"))
        self.assertEqual((self.target / kit.LOCK_NAME).read_text("utf-8"), lock_before)

    def test_conflict_writes_kit_new_then_resolve(self):
        self.append(self.kit / TEMPLATE, "\n% upstream\n")
        self.append(self.target / TEMPLATE, "\n% local\n")
        self.assertEqual(quiet(kit.cmd_update, self.target, self.kit), 1)
        pending = self.target / (TEMPLATE + kit.CONFLICT_SUFFIX)
        self.assertTrue(pending.is_file())
        self.assertIn("% local", (self.target / TEMPLATE).read_text("utf-8"))
        # The user merges by hand, then resolves.
        self.append(self.target / TEMPLATE, "% upstream\n")
        quiet(kit.cmd_resolve, self.target, self.kit, [TEMPLATE])
        self.assertFalse(pending.exists())
        self.assertEqual(self.states()[TEMPLATE], "local")

    def test_new_and_removed_kit_files(self):
        new = "docs/methodology/templates/new.template.md"
        (self.kit / new).write_text("new", encoding="utf-8")
        (self.kit / TEMPLATE).unlink()
        states = self.states()
        self.assertEqual((states[new], states[TEMPLATE]), ("new", "removed"))
        quiet(kit.cmd_update, self.target, self.kit)
        self.assertTrue((self.target / new).is_file())
        self.assertFalse((self.target / TEMPLATE).exists())
        self.assertNotIn(TEMPLATE, kit.load_lock(self.target)["files"])

    def test_missing_file_is_restored(self):
        (self.target / SKILL).unlink()
        self.assertEqual(self.states()[SKILL], "missing")
        quiet(kit.cmd_update, self.target, self.kit)
        self.assertTrue((self.target / SKILL).is_file())


class TestPromote(KitTestCase):
    def setUp(self):
        super().setUp()
        self.install()

    def test_preview_does_not_touch_kit(self):
        self.append(self.target / TEMPLATE, "\n% better guidance\n")
        quiet(kit.cmd_promote, self.target, self.kit)
        self.assertNotIn("% better", (self.kit / TEMPLATE).read_text("utf-8"))

    def test_apply_copies_into_kit_and_relocks(self):
        self.append(self.target / TEMPLATE, "\n% better guidance\n")
        self.assertEqual(quiet(kit.cmd_promote, self.target, self.kit, apply=True), 0)
        self.assertIn("% better", (self.kit / TEMPLATE).read_text("utf-8"))
        self.assertEqual(self.states()[TEMPLATE], "ok")

    def test_forbidden_terms_block_promotion(self):
        lock = kit.load_lock(self.target)
        lock["forbidden_terms"] = ["acme"]
        kit.save_lock(self.target, lock)
        self.append(self.target / TEMPLATE, "\n% ACME specific\n")
        self.assertEqual(quiet(kit.cmd_promote, self.target, self.kit, apply=True), 1)
        self.assertNotIn("ACME", (self.kit / TEMPLATE).read_text("utf-8"))
        quiet(kit.cmd_promote, self.target, self.kit, apply=True, force=True)
        self.assertIn("ACME", (self.kit / TEMPLATE).read_text("utf-8"))

    def test_binding_slug_is_forbidden_automatically(self):
        reg = self.target / REGISTRY
        text = reg.read_text(encoding="utf-8").replace(
            "| Problem slug `<problem>` | `<problem>` |",
            "| Problem slug `<problem>` | `vrp_depots` |",
        )
        reg.write_text(text, encoding="utf-8")
        self.assertEqual(kit.binding_terms(self.target), ["vrp_depots"])
        self.append(self.target / TEMPLATE, "\n% see docs/vrp_depots/\n")
        self.assertEqual(quiet(kit.cmd_promote, self.target, self.kit, apply=True), 1)

    def test_conflict_is_not_promoted(self):
        self.append(self.kit / TEMPLATE, "\n% upstream\n")
        self.append(self.target / TEMPLATE, "\n% local\n")
        self.assertEqual(quiet(kit.cmd_promote, self.target, self.kit, apply=True), 1)
        self.assertNotIn("% local", (self.kit / TEMPLATE).read_text("utf-8"))


class TestDoctor(KitTestCase):
    def test_shipped_kit_is_healthy(self):
        self.assertEqual(quiet(kit.cmd_doctor, self.kit), 0)

    def test_detects_broken_references(self):
        (self.kit / TEMPLATE).unlink()
        skill = self.kit / SKILL
        skill.write_text(
            skill.read_text("utf-8").replace("name: p0-intake", "name: wrong"), "utf-8"
        )
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(kit.cmd_doctor(self.kit), 1)
        self.assertIn("report.template.tex", out.getvalue())
        self.assertIn("frontmatter name='wrong'", out.getvalue())

    def test_lock_is_valid_json_with_version(self):
        quiet(kit.cmd_install, self.target, self.kit)
        lock = json.loads((self.target / kit.LOCK_NAME).read_text("utf-8"))
        self.assertEqual(lock["kit_version"], kit.kit_version(self.kit))


if __name__ == "__main__":
    unittest.main()

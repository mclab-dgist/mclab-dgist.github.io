"""Regression coverage for current-source builds, cache keys, and portable previews."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_site = load_script("build_site")
build_preview = load_script("build_preview")


class CurrentSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for category in build_site.CATEGORIES:
            (self.root / "content" / category).mkdir(parents=True)
        self.base = {
            "config": {}, "pi": {"interests": []}, "research": [],
            "news": [], "gallery": [], "recruitment": {}, "sources": {},
            "researchPrograms": [{"id": "vehicle-dynamics"}],
        }
        self.write_base()
        self.record("people", "faculty", {
            "name": "Test Faculty", "group": "Faculty", "role": "Professor",
        })
        for name, content in {
            "assets/js/app.js": "window.previewRunCount=(window.previewRunCount||0)+1;",
            "assets/css/style.css": "body { color: navy; }",
            "assets/images/favicon.svg": '<svg xmlns="http://www.w3.org/2000/svg"></svg>',
            "assets/video/research/SBW.mp4": "video-copy-fixture",
            "assets/video/research/DualSbW.mp4": "video-copy-fixture",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.html = '''<!doctype html><html><head>
<link href='assets/css/style.css?v=old' rel="stylesheet">
<script defer src="data/site-data.js?v=old"></script>
<script src='assets/js/app.js' defer></script>
<script src="assets/js/app.js?old=pinned" defer></script>
<script src="other.js?v=keep" defer></script>
</head><body><main id="main"></main></body></html>'''
        for page in build_site.PAGES:
            (self.root / (page + ".html")).write_text(self.html, encoding="utf-8")

    def write_base(self):
        (self.root / "content/site.json").write_text(json.dumps(self.base), encoding="utf-8")

    def record(self, category, slug, values):
        path = self.root / "content" / category / slug
        path.mkdir(parents=True, exist_ok=True)
        (path / "info.json").write_text(json.dumps({"id": slug, **values}), encoding="utf-8")

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            build_site.build(self.root, self.root / "_site", "2026-11-22")
        return self.root / "_site"

    def test_missing_optional_folders_cannot_restore_embedded_records(self):
        for key in ("researchTopics", "news", "gallery"):
            self.base[key] = [{"id": "old-record", "title": "Must not reappear"}]
        self.write_base()
        data, _, _ = build_site.collect(self.root, "2026-11-22")
        for key in ("researchTopics", "news", "gallery"):
            self.assertEqual(data[key], [], key)

    def test_current_folder_replaces_embedded_section_and_hidden_stays_hidden(self):
        self.base["researchTopics"] = [{"id": "old-topic", "title": "Obsolete"}]
        self.base["news"] = [{"id": "old-news", "title": "Obsolete"}]
        self.write_base()
        self.record("research", "current-topic", {
            "program": "vehicle-dynamics", "title": "Current", "description": "Approved",
        })
        self.record("news", "hidden-news", {"visible": False})
        data, _, _ = build_site.collect(self.root, "2026-11-22")
        self.assertEqual([r["id"] for r in data["researchTopics"]], ["current-topic"])
        self.assertEqual(data["news"], [])

    def test_versions_replace_old_queries_preserve_fragments_and_other_references(self):
        versions = {"assets/js/app.js": "abc123", "assets/css/style.css": "def456"}
        html = '''<script src="assets/js/app.js?v=old&x=1#part"></script>
<link href = 'assets/css/style.css'>
<script src="https://example.org/assets/js/app.js?v=old"></script>
<script data-src="assets/js/app.js?v=keep" src="other.js?v=keep"></script>
<script src="assets/js/app.js.backup?v=keep"></script>'''
        output = build_site.version_asset_references(html, versions)
        self.assertIn('src="assets/js/app.js?v=abc123#part"', output)
        self.assertIn("href = 'assets/css/style.css?v=def456'", output)
        for reference in (
            'src="https://example.org/assets/js/app.js?v=old"',
            'data-src="assets/js/app.js?v=keep"', 'src="other.js?v=keep"',
            'src="assets/js/app.js.backup?v=keep"',
        ):
            self.assertIn(reference, output)
        self.assertEqual(build_site.version_asset_references(output, versions), output)

    def test_built_pages_reference_actual_content_hashes_not_stale_snapshot(self):
        stale = self.root / "data/site-data.js"
        stale.parent.mkdir()
        stale.write_text('window.MCLAB_DATA={"obsolete":true};', encoding="utf-8")
        site = self.build()
        for page in build_site.PAGES:
            html = (site / (page + ".html")).read_text(encoding="utf-8")
            for asset in ("assets/js/app.js", "assets/css/style.css", "data/site-data.js"):
                digest = hashlib.sha256((site / asset).read_bytes()).hexdigest()[:12]
                self.assertIn(asset + "?v=" + digest, html)
            self.assertNotIn("?v=old", html)
            self.assertNotIn("?old=pinned", html)
            self.assertIn('src="other.js?v=keep"', html)
        self.assertNotIn('"obsolete"', (site / "data/site-data.js").read_text())

    def test_preview_removes_versioned_script_copies_and_inlines_each_once(self):
        self.build()
        output = self.root / "preview.html"
        with patch.object(build_preview, "ROOT", self.root), patch(
            "sys.argv", ["build_preview.py", "--output", str(output)]
        ), contextlib.redirect_stdout(io.StringIO()):
            build_preview.main()
        html = output.read_text(encoding="utf-8")
        self.assertNotIn("assets/css/style.css", html)
        self.assertNotIn("data/site-data.js", html)
        self.assertNotIn("assets/js/app.js", html)
        self.assertEqual(html.count("body { color: navy; }"), 1)
        self.assertEqual(html.count("window.MCLAB_DATA="), 1)
        self.assertEqual(html.count("window.previewRunCount=("), 1)
        self.assertIn('src="other.js?v=keep"', html)

    def test_preview_preserves_unrelated_external_assets(self):
        html = '''<link href="assets/css/style.css?v=1" rel="stylesheet">
<link rel="stylesheet" href='assets/css/style.css?v=2'>
<link href="https://example.org/assets/css/style.css?v=keep" rel="stylesheet">
<script src="https://example.org/assets/js/app.js?v=keep"></script>
<script>window.inlineTheme=true;</script>'''
        output = build_preview.inline_preview_assets(html, "CURRENT_CSS")
        self.assertEqual(output.count("CURRENT_CSS"), 1)
        self.assertIn('href="https://example.org/assets/css/style.css?v=keep"', output)
        self.assertIn('src="https://example.org/assets/js/app.js?v=keep"', output)
        self.assertIn("window.inlineTheme=true;", output)


if __name__ == "__main__":
    unittest.main()

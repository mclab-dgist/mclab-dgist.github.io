"""Regression checks for the reviewed, current website baseline."""
import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("approved_release", ROOT / "scripts/verify_approved_release.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class ApprovedReleaseTests(unittest.TestCase):
    def setUp(self):
        # Use independent fixtures so intentional edits to the live catalogue do
        # not require rewriting the regression tests or weakening the lockfile.
        self.data = {
            "config": {"tagline": "Current tagline"},
            "pi": {"name": "Current professor"},
            "people": [{"id": "student", "name": "Current student"}],
            "publications": [{
                "id": "j26-sync", "title": "Current title", "authors": "Current authors",
                "venue": "Current journal", "doi": "10.1234/current", "year": 2026,
                "status": "Published", "details": "Vol. 73, no. 10, pp. 15559–15564",
            }],
            "projects": [{
                "id": "brake-model-vehicle-data-validation", "start": "2026-12-01",
                "end": "2027-09-30", "statusMode": "auto", "status": "Upcoming",
            }, {"id": "manual-project", "statusMode": "Ongoing", "status": "Ongoing"}],
            "researchTopics": [{
                "id": "learning-estimation", "title": "Current EMB research",
                "description": "Current short description", "program": "vehicle-dynamics",
                "image": "media/current-image.jpg",
            }, {"id": "second-topic", "title": "Another current topic"}],
            "gallery": [], "news": [],
        }
        self.approved = {"schema": 2, "content": VERIFY.stable_content(self.data),
                         "forbiddenIds": {"researchTopics": ["ros-navigation"]}}

    def record(self, group, key):
        return next(record for record in self.data[group] if record["id"] == key)

    def test_current_reviewed_content_passes(self):
        self.assertEqual([], VERIFY.validate_content(self.data, self.approved))

    def test_only_volatile_build_fields_and_auto_status_are_ignored(self):
        self.data["config"].update(builtAt="2099-01-01T12:00:00+09:00", statusDate="2099-01-01")
        for record in self.data["projects"]:
            if record.get("statusMode") == "auto":
                record["status"] = "Completed"
        self.assertEqual([], VERIFY.validate_content(self.data, self.approved))

    def test_normalization_does_not_mutate_input(self):
        self.data["config"]["builtAt"] = "2026-11-22"
        before = copy.deepcopy(self.data)
        VERIFY.stable_content(self.data)
        self.assertEqual(before, self.data)

    def test_publication_bibliography_regressions_are_blocked(self):
        for field in ("details", "doi", "venue", "authors", "status", "title", "year"):
            with self.subTest(field=field):
                current = copy.deepcopy(self.data)
                self.record("publications", "j26-sync")[field] = "stale value"
                self.assertTrue(any("j26-sync." + field in p for p in VERIFY.validate_content(self.data, self.approved)))
                self.data = current

    def test_research_description_image_and_program_are_protected(self):
        for field in ("description", "image", "program", "title"):
            with self.subTest(field=field):
                current = copy.deepcopy(self.data)
                self.record("researchTopics", "learning-estimation")[field] = "old content"
                self.assertTrue(any("learning-estimation." + field in p for p in VERIFY.validate_content(self.data, self.approved)))
                self.data = current

    def test_project_dates_and_status_mode_are_protected(self):
        for field in ("start", "end", "statusMode"):
            with self.subTest(field=field):
                current = copy.deepcopy(self.data)
                self.record("projects", "brake-model-vehicle-data-validation")[field] = "old value"
                self.assertTrue(VERIFY.validate_content(self.data, self.approved))
                self.data = current

    def test_manual_project_status_is_protected(self):
        record = next(r for r in self.data["projects"] if r.get("statusMode") != "auto")
        record["status"] = "incorrect manual status"
        self.assertTrue(any(".status:" in p for p in VERIFY.validate_content(self.data, self.approved)))

    def test_global_and_profile_data_are_protected(self):
        self.data["config"]["tagline"] = "old tagline"
        self.data["pi"]["name"] = "old name"
        problems = VERIFY.validate_content(self.data, self.approved)
        self.assertTrue(any("config.tagline" in p for p in problems))
        self.assertTrue(any("pi.name" in p for p in problems))

    def test_order_change_is_blocked(self):
        self.data["researchTopics"].reverse()
        self.assertTrue(any("IDs/order changed" in p for p in VERIFY.validate_content(self.data, self.approved)))

    def test_missing_record_is_blocked(self):
        self.data["publications"].pop()
        self.assertTrue(VERIFY.validate_content(self.data, self.approved))

    def test_removed_record_reappearing_is_blocked(self):
        self.data["researchTopics"].append({"id": "ros-navigation", "title": "Old item"})
        self.assertTrue(any("reappeared" in p for p in VERIFY.validate_content(self.data, self.approved)))

    def test_duplicate_record_is_blocked(self):
        self.data["people"].append(copy.deepcopy(self.data["people"][0]))
        self.assertTrue(any("duplicate IDs" in p for p in VERIFY.validate_content(self.data, self.approved)))

    def test_added_or_missing_fields_are_blocked(self):
        self.record("publications", "j26-sync")["obsoleteNote"] = "not reviewed"
        self.record("researchTopics", "learning-estimation").pop("description")
        problems = VERIFY.validate_content(self.data, self.approved)
        self.assertTrue(any("obsoleteNote" in p for p in problems))
        self.assertTrue(any("description" in p and "missing" in p for p in problems))

    def test_old_incomplete_baseline_schema_is_blocked(self):
        self.approved["schema"] = 1
        self.assertTrue(VERIFY.validate_content(self.data, self.approved))

    def test_exact_current_asset_hash_is_required(self):
        versions = {"data/site-data.js": "0123456789ab"}
        correct = '<script src="data/site-data.js?v=0123456789ab" defer></script>'
        self.assertEqual([], VERIFY.validate_asset_references(correct, versions, "research.html"))
        for bad in (correct.replace("0123456789ab", "old"), correct.replace("?v=0123456789ab", ""), correct + correct, ""):
            with self.subTest(html=bad):
                self.assertTrue(VERIFY.validate_asset_references(bad, versions, "research.html"))

    def test_comments_data_attributes_and_wrong_tags_do_not_count_as_loading(self):
        versions = {"data/site-data.js": "0123456789ab"}
        for bad in (
            '<!-- <script src="data/site-data.js?v=0123456789ab"></script> -->',
            '<div data-src="data/site-data.js?v=0123456789ab"></div>',
            '<script href="data/site-data.js?v=0123456789ab"></script>',
            '<link rel="preload" href="data/site-data.js?v=0123456789ab">',
            '<link rel="stylesheet" href="data/site-data.js?v=0123456789ab">',
        ):
            with self.subTest(html=bad):
                self.assertTrue(VERIFY.validate_asset_references(bad, versions, "research.html"))

    def test_stylesheet_requires_real_stylesheet_link(self):
        versions = {"assets/css/style.css": "0123456789ab"}
        good = '<link rel="stylesheet" href="assets/css/style.css?v=0123456789ab">'
        self.assertEqual([], VERIFY.validate_asset_references(good, versions, "research.html"))
        self.assertTrue(VERIFY.validate_asset_references(good.replace("stylesheet", "preload"), versions, "research.html"))
        self.assertTrue(VERIFY.validate_asset_references('<script src="assets/css/style.css?v=0123456789ab"></script>', versions, "research.html"))

    def test_url_encoded_and_external_images_follow_builder_rules(self):
        files = {"media/photo name.jpg", "media/사진.jpg"}
        self.assertTrue(VERIFY.image_available("media/photo%20name.jpg", files))
        self.assertTrue(VERIFY.image_available("media/%EC%82%AC%EC%A7%84.jpg", files))
        self.assertTrue(VERIFY.image_available("https://example.org/portrait.jpg", files))
        for missing in ("", "media/missing.jpg", "../portrait.jpg", "javascript:example"):
            self.assertFalse(VERIFY.image_available(missing, files))


if __name__ == "__main__":
    unittest.main()

import hashlib
from pathlib import Path
import stat
import tempfile
import unittest
import zipfile

from import_package import ARCHIVE, DESTINATION, REQUIRED, install


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def archive(self, extra=None, omit=None):
        path = self.root / ARCHIVE
        with zipfile.ZipFile(path, "w") as archive:
            for name in sorted(REQUIRED - set(omit or ())):
                archive.writestr(name, "fixture")
            for name, data in extra or ():
                archive.writestr(name, data)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_missing_archive_preserves_existing_site(self):
        self.assertEqual(install(self.root), {"ready": False, "imported": False})

    def test_install_preserves_bytes(self):
        checksum = self.archive()
        self.assertTrue(install(self.root, checksum)["imported"])
        self.assertEqual((self.root / DESTINATION / "index.html").read_text(), "fixture")

    def test_later_edits_are_not_overwritten(self):
        checksum = self.archive()
        install(self.root, checksum)
        path = self.root / DESTINATION / "index.html"
        path.write_text("new content")
        self.assertFalse(install(self.root, checksum)["imported"])
        self.assertEqual(path.read_text(), "new content")

    def test_checksum_mismatch(self):
        self.archive()
        with self.assertRaisesRegex(ValueError, "checksum"):
            install(self.root, "0" * 64)

    def test_unmanaged_destination_is_protected(self):
        (self.root / DESTINATION).mkdir()
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            install(self.root)

    def test_parent_traversal_is_rejected(self):
        checksum = self.archive([("../outside.txt", "bad")])
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            install(self.root, checksum)

    def test_absolute_path_is_rejected(self):
        checksum = self.archive([("/outside.txt", "bad")])
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            install(self.root, checksum)

    def test_git_metadata_is_rejected(self):
        checksum = self.archive([(".git/config", "bad")])
        with self.assertRaisesRegex(ValueError, "Forbidden"):
            install(self.root, checksum)

    def test_missing_required_file_is_rejected(self):
        checksum = self.archive(omit={"index.html"})
        with self.assertRaisesRegex(ValueError, "Missing required"):
            install(self.root, checksum)

    def test_teaching_page_is_rejected(self):
        checksum = self.archive([("teaching.html", "bad")])
        with self.assertRaisesRegex(ValueError, "no-Teaching"):
            install(self.root, checksum)

    def test_symlink_is_rejected(self):
        item = zipfile.ZipInfo("link")
        item.create_system = 3
        item.external_attr = (stat.S_IFLNK | 0o777) << 16
        checksum = self.archive([(item, "../../outside")])
        with self.assertRaisesRegex(ValueError, "symlinks"):
            install(self.root, checksum)

    def test_installed_site_does_not_need_zip(self):
        checksum = self.archive()
        install(self.root, checksum)
        (self.root / ARCHIVE).unlink()
        self.assertEqual(install(self.root, checksum), {"ready": True, "imported": False})


if __name__ == "__main__":
    unittest.main()

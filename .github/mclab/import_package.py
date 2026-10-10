#!/usr/bin/env python3
"""Install the approved MCLab archive once, without overwriting later edits."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

ARCHIVE = "MCLab_Original_Photos_No_Teaching.zip"
EXPECTED_SHA256 = "7ed71aa5ad4abfca8d0d3c4fa174d4968266db6db6f95968358bd6c1209aed55"
DESTINATION = "mclab"
MARKER = ".mclab-import.json"
REQUIRED = {
    "index.html", "people.html", "research.html", "publications.html",
    "projects.html", "assets/js/app.js", "assets/css/style.css",
    "scripts/build_site.py", "content/site.json",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def install(root: Path, expected_hash: str = EXPECTED_SHA256) -> dict:
    root = root.resolve()
    archive, target = root / ARCHIVE, root / DESTINATION
    marker = target / MARKER
    if marker.is_file():
        state = json.loads(marker.read_text(encoding="utf-8"))
        if state.get("sha256") != expected_hash:
            raise ValueError("Existing installation marker differs; refusing to overwrite.")
        if not (target / "scripts/build_site.py").is_file():
            raise ValueError("Installed source is incomplete; restore it from Git history.")
        return {"ready": True, "imported": False}
    if target.exists():
        raise ValueError("mclab/ already exists without an import marker; refusing to overwrite.")
    if not archive.is_file():
        return {"ready": False, "imported": False}
    if archive.stat().st_size > 30 * 1024 * 1024:
        raise ValueError("Archive exceeds the approved package size limit.")
    if sha256(archive) != expected_hash:
        raise ValueError("ZIP checksum mismatch. Upload the unchanged approved ZIP.")

    with zipfile.ZipFile(archive) as package:
        entries = package.infolist()
        if len(entries) > 2000 or sum(i.file_size for i in entries) > 100 * 1024 * 1024:
            raise ValueError("Archive exceeds extraction limits.")
        names = set()
        for item in entries:
            name = item.filename
            path = PurePosixPath(name)
            if not name or path.is_absolute() or ".." in path.parts or "\\" in name:
                raise ValueError(f"Unsafe archive path: {name!r}")
            if ".git" in path.parts or ":" in name or "\x00" in name:
                raise ValueError(f"Forbidden archive path: {name!r}")
            if stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f"Archive symlinks are not allowed: {name!r}")
            if name in names:
                raise ValueError(f"Duplicate archive member: {name!r}")
            names.add(name)
        missing = REQUIRED - names
        if missing:
            raise ValueError(f"Missing required website files: {sorted(missing)}")
        if "teaching.html" in names:
            raise ValueError("This installer accepts only the approved no-Teaching version.")
        stage = Path(tempfile.mkdtemp(prefix=".mclab-import-", dir=root))
        try:
            package.extractall(stage)
            (stage / MARKER).write_text(
                json.dumps({"archive": ARCHIVE, "sha256": expected_hash, "version": 1}, indent=2)
                + "\n", encoding="utf-8"
            )
            stage.rename(target)
        finally:
            if stage.exists():
                shutil.rmtree(stage)
    return {"ready": True, "imported": True}


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    state = install(root)
    print(json.dumps(state))
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            for key, value in state.items():
                stream.write(f"{key}={str(value).lower()}\n")
    if not state["ready"]:
        print(f"Upload {ARCHIVE} to the repository root. Existing published pages are unchanged.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Integrate reviewed upstream fixes into the pinned PdfCraft v0.7.1 checkout.

Fail closed if a PR head moves or an applicable patch conflicts. Patches are
rebuilt from the PR's merge base with the release tag, including multi-commit
PRs. Exclude only repository metadata/docs that overlap unrelated proposals;
keep every production-code and regression-test edit.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Fix:
    pr: int
    sha: str
    # None means all files. A nonempty allowlist removes only docs/metadata.
    paths: tuple[str, ...] | None = None


FIXES = (
    Fix(1436, "6c616ae9049ed87ee574415f61a66bd15b2a5839"),
    Fix(1437, "d55a5f0dcdec4d7b956c3a732fd6a165541541b3"),
    Fix(1438, "bd2b8ea925dca7a48c0ed20ea37f5d27e087a592"),
    Fix(1458, "c9e02dfac77dc3ebe96ed511589703c3f7069363"),
    Fix(1474, "d718fab6ec77e0fd62ef839bbb152670cf545224"),
    Fix(1477, "5e6d7f2c3919028a4d24772fdd280f808fed50ad"),
    # Seven additional regression fixes included in this SAME Android v0.7.2.
    Fix(1512, "51bf0680801f822bd9a5e75b1f9f2e91e92011a7"),
    Fix(
        1478, "a27b9008b015cef90ca3f4d821fe0f0060622080",
        ("crates/render/src/raster.rs", "vendor/hayro-interpret/src/interpret/text.rs"),
    ),
    Fix(
        1499, "bae7bdebab3e78b9e733fafa932e6038bf0a44bb",
        ("crates/render/src/raster.rs", "vendor/hayro-syntax/src/filter/lzw_flate.rs", "vendor/README.md"),
    ),
    Fix(1521, "9755eac1dd16b91de87e9e492d3473138885e8ff"),
    Fix(
        1500, "92b1c90e6fdbf4acf5a867f36fe7302a87e3965b",
        ("crates/organize/src/prune.rs", "crates/organize/src/tests.rs"),
    ),
    Fix(1481, "d7e1c5b23a428966448e9dee6d07c8f64b1f32ce"),
    Fix(1480, "8b43c4b86bf330970ec8c45406d5e1b388f61e21"),
)


def git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    return result.stdout if binary else result.stdout.decode("utf-8", errors="replace").strip()


def run() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_upstream_fixes.py UPSTREAM_CHECKOUT")
    root = Path(sys.argv[1]).resolve()
    tag_sha = str(git(root, "rev-parse", "v0.7.1"))
    if tag_sha != "7163ba3dee8becfff6871c9a65d0d8314314742b":
        raise RuntimeError(f"Unexpected official release tag: {tag_sha}")
    if git(root, "rev-parse", "HEAD") != tag_sha:
        raise RuntimeError("Checkout must remain on the official v0.7.1 release commit")
    for fix in FIXES:
        git(root, "fetch", "--no-tags", "origin", f"refs/pull/{fix.pr}/head")
        actual = str(git(root, "rev-parse", "FETCH_HEAD"))
        if actual != fix.sha:
            raise RuntimeError(f"PR #{fix.pr} changed: reviewed {fix.sha}, now {actual}. Re-review before updating the pin.")

        ancestor = str(git(root, "merge-base", tag_sha, actual))
        args = ["diff", "--binary", ancestor, actual]
        if fix.paths is not None:
            args += ["--", *fix.paths]
        patch = git(root, *args, binary=True)
        if not patch:
            raise RuntimeError(f"PR #{fix.pr} produced no changes")
        path = Path(f"/tmp/pdfcraft-pr-{fix.pr}.patch")
        path.write_bytes(patch)
        subprocess.run(["git", "-C", str(root), "apply", "--check", str(path)], check=True)
        subprocess.run(["git", "-C", str(root), "apply", str(path)], check=True)
        print(f"Applied PR #{fix.pr} @ {actual}, {len(patch)} patch bytes", flush=True)

    # #1478's original vendored-patch index edits a huge one-line index already
    # changed by #1477. Document #1478 without replacing that index in conflict.
    readme = root / "vendor/README.md"
    text = readme.read_text(encoding="utf-8")
    note = (
        "\nAndroid community integration: upstream PR #1478 (hayro-interpret patch 27) "
        "treats Type 3 glyphs as fill-only in rendering modes other than invisible "
        "(ISO 32000-1 §9.3.6); see vendor/hayro-interpret/src/interpret/text.rs.\n"
    )
    if "upstream PR #1478 (hayro-interpret patch 27)" not in text:
        readme.write_text(text.rstrip() + "\n" + note, encoding="utf-8")
    print(f"Integrated {len(FIXES)} SHA-pinned upstream fixes into official PdfCraft v0.7.1.", flush=True)


if __name__ == "__main__":
    run()

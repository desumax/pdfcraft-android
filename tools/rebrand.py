#!/usr/bin/env python3
"""Replace restricted ArtCraft image assets in the unofficial Android fork.

Modified forks must not distribute the upstream trademark logos. Keep the
same Rust widget APIs for compatibility, but bind them to independent local
community artwork. This also avoids include_bytes! errors after removing
the original docs/brand directory.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path


DARK = """<svg xmlns="http://www.w3.org/2000/svg" width="300" height="64" viewBox="0 0 300 64">
<rect x="2" y="2" width="60" height="60" rx="15" fill="#153F47"/>
<path d="M19 11H40L51 22V50H19Z" fill="#F7FBF9"/>
<path d="M40 11V22H51" fill="#80C5BB"/>
<path d="M25 30H45M25 37H45M25 44H37" fill="none" stroke="#256B77" stroke-width="3" stroke-linecap="round"/>
<text x="76" y="35" fill="#F7FBF9" font-family="sans-serif" font-size="24" font-weight="700">PdfCraft</text>
<text x="78" y="50" fill="#A8CAC8" font-family="sans-serif" font-size="11" letter-spacing="3">COMMUNITY</text>
</svg>
"""

LIGHT = DARK.replace('fill="#F7FBF9" font-family=', 'fill="#163941" font-family=').replace('fill="#A8CAC8" font-family=', 'fill="#356F79" font-family=')

MARK = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
<rect x="2" y="2" width="60" height="60" rx="15" fill="#153F47"/>
<path d="M19 11H40L51 22V50H19Z" fill="#F7FBF9"/>
<path d="M40 11V22H51" fill="#80C5BB"/>
<path d="M25 30H45M25 37H45M25 44H37" fill="none" stroke="#256B77" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Expected exactly one {old!r}, got {n}")
    return text.replace(old, new)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rebrand.py UPSTREAM_CHECKOUT")
    repo = Path(sys.argv[1]).resolve()
    d = repo / "docs/community-brand"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "community-logo-dark.svg": DARK,
        "community-logo-light.svg": LIGHT,
        "community-mark.svg": MARK,
    }.items():
        (d / name).write_text(content, encoding="utf-8")

    widgets = repo / "crates/ui-egui/src/widgets.rs"
    original = widgets.read_text(encoding="utf-8")
    modified = original
    changes = {
        '("bytes://artcraft-logo-white.svg", include_bytes!("../../../docs/brand/artcraft-logo-white.svg"))':
            '("bytes://community-logo-dark.svg", include_bytes!("../../../docs/community-brand/community-logo-dark.svg"))',
        '("bytes://artcraft-logo.svg", include_bytes!("../../../docs/brand/artcraft-logo.svg"))':
            '("bytes://community-logo-light.svg", include_bytes!("../../../docs/community-brand/community-logo-light.svg"))',
        'egui::Image::from_bytes("bytes://artcraft-mark.svg", include_bytes!("../../../docs/brand/artcraft-mark.svg"))':
            'egui::Image::from_bytes("bytes://community-mark.svg", include_bytes!("../../../docs/community-brand/community-mark.svg"))',
        '/// The ArtCraft wordmark (Storyteller\'s brand, docs/brand/; not open source), sized to `height`.':
            '/// Independent community wordmark for modified Android builds, sized to `height`.',
        '/// The ArtCraft mark (brand blue, works on light and dark), `size` points square.':
            '/// Independent community document mark, `size` points square.',
        '.alt_text("ArtCraft")': '.alt_text("PdfCraft Community")',
    }
    for old, new in changes.items():
        if old == '.alt_text("ArtCraft")':
            n = modified.count(old)
            if n != 2:
                raise RuntimeError(f"Expected two image alt tags, found {n}")
            modified = modified.replace(old, new)
        else:
            modified = replace_once(modified, old, new)
    widgets.write_text(modified, encoding="utf-8")

    brand = repo / "docs/brand"
    if brand.exists():
        shutil.rmtree(brand)
    print("Replaced 3 restricted brand images with independent community art; deleted original brand assets.")


if __name__ == "__main__":
    main()

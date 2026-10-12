#!/usr/bin/env python3
"""Port kanaaka's NativeActivity integration to the released PdfCraft v0.7.1 tree.

Fail closed when expected anchors move. Source inputs are the upstream checkout and
this public fork; nothing in the fork's original Android patch is overwritten.
"""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

VERSION = "0.7.2"
PACKAGE = "io.github.desumax.pdfcraft"


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    found = content.count(old)
    if found != 1:
        raise RuntimeError(f"{path}: expected one occurrence of {old!r}, got {found}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def import_rfd_adapters(patch_path: Path, root: Path) -> None:
    patch = patch_path.read_text(encoding="utf-8")
    wanted = {"crates/ui-egui/src/rfd.rs", "crates/ui-egui/src/rfd_android.rs"}
    added = set()
    for section in re.split(r"(?=^diff --git a/)", patch, flags=re.MULTILINE):
        m = re.match(r"diff --git a/(\S+) b/(\S+)\n", section)
        if m is None or m.group(1) not in wanted:
            continue
        name = m.group(1)
        if m.group(2) != name or "new file mode" not in section or "--- /dev/null" not in section:
            raise RuntimeError(f"Unsupported adapter diff for {name}")
        match = re.search(r"^@@[^\n]*@@[^\n]*\n", section, flags=re.MULTILINE)
        if match is None:
            raise RuntimeError(f"Missing diff hunk for {name}")
        lines = section[match.end():].splitlines()
        if any(line.startswith((" ", "-")) for line in lines if line):
            raise RuntimeError(f"Adapter {name} contains unexpected deletions/context")
        dest = root / name
        if dest.exists():
            raise RuntimeError(f"Adapter already exists: {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("\n".join(line[1:] for line in lines if line.startswith("+")) + "\n", encoding="utf-8")
        added.add(name)
    if added != wanted:
        raise RuntimeError(f"Expected both rfd shims, got {added}")


def port(src: Path, android_port: Path) -> None:
    src, android_port = src.resolve(), android_port.resolve()
    ws = (src / "Cargo.toml").read_text(encoding="utf-8")
    if 'version = "0.7.1"' not in ws:
        raise RuntimeError("Expected official upstream workspace version 0.7.1")
    patch = android_port / "patches/0001-pdfcraft-android-port.patch"
    import_rfd_adapters(patch, src)

    ui = src / "crates/ui-egui"
    manifest = ui / "Cargo.toml"
    replace_once(manifest,
        'eframe = { workspace = true, features = ["default_fonts", "wgpu", "accesskit", "persistence", "links"] }',
        'eframe = { workspace = true, features = ["default_fonts", "wgpu", "persistence", "links"] }')
    replace_once(manifest, 'rfd = { workspace = true }\n', '')
    replace_once(manifest,
        'arboard = { version = "3.6", default-features = false, features = ["image-data"] }\n', '')
    marker = '[target.\'cfg(target_os = "macos")\'.dependencies]'
    inject = """# Real native/browser dialogs and clipboard do not compile on Android.
[target.'cfg(all(not(target_os = "android"), not(target_arch = "wasm32")))'.dependencies]
rfd = { workspace = true }
arboard = { version = "3.6", default-features = false, features = ["image-data"] }

# AccessKit and the Android NativeActivity eframe backend are incompatible.
[target.'cfg(not(target_os = "android"))'.dependencies]
eframe = { workspace = true, features = ["default_fonts", "wgpu", "accesskit", "persistence", "links"] }

"""
    replace_once(manifest, marker, inject + marker)
    replace_once(ui / "src/lib.rs", 'pub mod i18n;\n', 'pub mod i18n;\npub mod rfd;\n')

    occurrences = 0
    for source in [*(ui / "src").rglob("*.rs"), *(ui / "tests").rglob("*.rs")]:
        if source.name in {"rfd.rs", "rfd_android.rs"}:
            continue
        content = source.read_text(encoding="utf-8")
        edited, changed = re.subn(r"(?<![\w:])rfd::", "crate::rfd::", content)
        if changed:
            source.write_text(edited, encoding="utf-8")
            occurrences += changed
    if occurrences < 35:
        raise RuntimeError(f"Only {occurrences} file-dialog calls converted; inspect changes")

    create = ui / "src/create_ui.rs"
    replace_once(create,
        '#[cfg(not(target_arch = "wasm32"))]\nfn read_clipboard()',
        '#[cfg(all(not(target_arch = "wasm32"), not(target_os = "android")))]\nfn read_clipboard()')
    replace_once(create,
        '#[cfg(not(target_arch = "wasm32"))]\n        let clip = read_clipboard();',
        '#[cfg(all(not(target_arch = "wasm32"), not(target_os = "android")))]\n        let clip = read_clipboard();')
    replace_once(create,
        '#[cfg(target_arch = "wasm32")]\n        let clip: Option<Clip> = None;',
        '#[cfg(any(target_arch = "wasm32", target_os = "android"))]\n        let clip: Option<Clip> = None;')
    replace_once(ui / "src/zoom_snap.rs",
        '#[cfg(not(target_arch = "wasm32"))]\n        if self.system_clipboard {',
        '#[cfg(all(not(target_arch = "wasm32"), not(target_os = "android")))]\n        if self.system_clipboard {')

    target = src / "apps/pdfcraft-android"
    if target.exists():
        raise RuntimeError(f"Existing Android shell: {target}")
    shutil.copytree(android_port / "apps/pdfcraft-android", target)
    cargo = target / "Cargo.toml"
    replace_once(cargo, "version.workspace = true", f'version = "{VERSION}"')
    replace_once(cargo, 'package = "ai.storyteller.pdfcraft"', f'package = "{PACKAGE}"')
    replace_once(cargo, 'label = "PdfCraft"', 'label = "PdfCraft Community"')
    print(f"Android adaptation complete: {occurrences} file-dialog refs, {PACKAGE} v{VERSION}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: rebase_android.py UPSTREAM_CHECKOUT KANAAKA_FORK")
    port(Path(sys.argv[1]), Path(sys.argv[2]))

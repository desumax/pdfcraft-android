# PdfCraft Community Android v0.7.2 — integration review

This is a **proposed**, unofficial community build, not an official PdfCraft v0.7.2.
The official engine input is `storytold/pdfcraft@v0.7.1`.
This fork retains `kanaaka`'s existing native Android source and patch without overwriting them.

## Why retain kanaaka's NativeActivity port?

Upstream [PR #1241](https://github.com/storytold/pdfcraft/pull/1241) contributes a NativeActivity skeleton (39 files), but replaces unsupported Android file dialogs with no-op stand-ins. The existing `kanaaka` shell has a functioning in-app picker, compiled signed ARM64 APK, change-detected atomic preference persistence, keyboard-modifier event adaptation, and some tablet testing. It remains the better starting point. Both approaches currently lack native Storage Access Framework integration.

## Rebase inputs

- `storytold/pdfcraft` official tag `v0.7.1` (October 12, 2026).
- `kanaaka/pdfcraft-android` originally targets `3d2bdfe71ada10f6bc39afc680dce61bbf080cbc` (v0.6.0).
- `tools/rebase_android.py` imports the Android file-dialog shim from the existing reviewed patch, copies the Android native shell, and maps all current UI `rfd` calls into that shim. It removes unsupported Android desktop clipboard and AccessKit configurations, without dropping them from desktop builds.
- Android-only package version `0.7.2`, independent application ID `io.github.desumax.pdfcraft`, label `PdfCraft Community`.
- New icon generator avoids the upstream ArtCraft trademarks.

## Six proposed regression fixes (exact PR commits)

| PR | SHA | Regression addressed |
| --- | --- | --- |
| [#1436](https://github.com/storytold/pdfcraft/pull/1436) | `6c616ae9049ed87ee574415f61a66bd15b2a5839` | Arrow annotation properties default to Line instead |
| [#1437](https://github.com/storytold/pdfcraft/pull/1437) | `d55a5f0dcdec4d7b956c3a732fd6a165541541b3` | Saved accessibility page ranges can exclude every page |
| [#1438](https://github.com/storytold/pdfcraft/pull/1438) | `bd2b8ea925dca7a48c0ed20ea37f5d27e087a592` | Declared PDF/UA incorrectly shown as none |
| [#1458](https://github.com/storytold/pdfcraft/pull/1458) | `c9e02dfac77dc3ebe96ed511589703c3f7069363` | Repeated converted image/text sources not identified as duplicates |
| [#1474](https://github.com/storytold/pdfcraft/pull/1474) | `d718fab6ec77e0fd62ef839bbb152670cf545224` | Adjacent narrow letters lost as fake-bold duplicates |
| [#1477](https://github.com/storytold/pdfcraft/pull/1477) | `5e6d7f2c3919028a4d24772fdd280f808fed50ad` | Certain accents decoded incorrectly from TrueType without Encoding |

Each PR was reviewed for small production code scope and contains targeted regression tests. Their merged behavior and Android compilation **remain unverified**. The workflow is fail-closed on changed SHA or patch conflicts. This is a deliberately conservative subset; substantial core editing/serialization, security, printing and mobile-host PRs are excluded.

## Build

The [Android build workflow](.github/workflows/android-v0.7.2.yml) runs on pushes to `port/v0.7.2` and can be started manually once enabled in GitHub Actions. It clones the official upstream code, re-applies the Android port, pins and applies six bug fixes, checks formatting, checks ARM64 compilation, builds a signed APK, and stores the APK plus SHA256 in a workflow artifact.

**Test signing only:** A fresh ephemeral signing key is created on every run. This makes APKs installable but not updatable in place. Use a persistent, private signing key before publishing an actual release.

**Android behavior inherited from kanaaka:** no native Android Storage Access Framework; shared-storage access needs manual All files access; no Android-wide clipboard, system printing, update Intents, or stylus pressure. The in-app file picker and on-device persistence must be tested on a real phone/tablet.

Do not use important original documents during initial tests. Verify PDF open, save, reopen, combine, large PDFs, Arabic/European accented text extraction, comments, page changes, background/resume, device rotation and crash recovery.

No APK or v0.7.2 release has been published until CI passes and device testing is completed.

## Source and licensing

Upstream Rust PDF workbench: https://github.com/storytold/pdfcraft
Native Android port: https://github.com/kanaaka/pdfcraft-android
This repository: https://github.com/desumax/pdfcraft-android
The MIT and Apache-2.0 license files and upstream author attribution remain intact. All ArtCraft trademark assets must be excluded from modified distributions.

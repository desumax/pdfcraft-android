# Attribution

## Upstream

**PdfCraft** — <https://github.com/storytold/pdfcraft> — pinned here at `3d2bdfe71ada10f6bc39afc680dce61bbf080cbc`
(version `0.6.0`).

Upstream is dual-licensed **Apache-2.0 OR MIT**. Both licence texts are reproduced in this
repository as `LICENSE-APACHE` and `LICENSE-MIT`, as the licences require. PdfCraft and its
engine, document model and egui interface are the work of its authors; nothing in this repository
changes their copyright.

## This repository

The Android layer — the `apps/pdfcraft-android/` shell crate, `patches/`, `docs/` and `scripts/` — is an
unofficial modification by [@kanaaka](https://github.com/kanaaka), written in October 2026, offered
under the same upstream terms (Apache-2.0 OR MIT).

It is **unofficial**: not produced, reviewed or endorsed by the upstream project, and upstream
issues should not be filed against it without saying so. The APKs in Releases are signed with a
throwaway local test key — not with any official release key — and carry the upstream package name
`ai.storyteller.pdfcraft` only so the port is recognisable as that application. They are not an official
PdfCraft release.

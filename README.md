# Clash assets

Reference assets for the original Clash game.

## English manual

| File | Description |
| --- | --- |
| [Manual.pdf](Manual.pdf) | Original, unchanged scan: 13 PDF pages containing the front cover, 22 numbered pages, and the back cover. |
| [Manual.md](Manual.md) | Searchable, page-referenced English transcription produced by direct model-based visual reading. |
| [Manual.ocr.json](Manual.ocr.json) | Source and transcription hashes, page coverage, transcription conventions, validation results, and editorial notes. |

The transcription covers all numbered pages and both covers. It was read from rendered page images and enlarged figure crops without a conventional OCR engine or an embedded PDF text layer. Original wording, spelling, grammar, and historical information are retained where legible; line-wrap hyphenation is joined and tables and headings are represented in Markdown.

Each page section links to its source PDF page. Explicit **[Transcription note: …]** annotations distinguish editorial observations from printed content. Tiny or obscured text inside screenshots is not always recoverable and is flagged rather than guessed. Illustrations remain in the source PDF. The transcription has not been independently human-proofread, and character accuracy has not been measured.

Validation checked the unchanged source PDF, valid UTF-8, the complete printed-page sequence, and all 24 page references. The Markdown downloaded back from GitHub was also compared byte-for-byte with the local transcription.

## Navigation

[Introduction](Manual.md#printed-page-3) · [Installation](Manual.md#printed-page-4) · [Controls](Manual.md#printed-page-5) · [Units and commanders](Manual.md#printed-page-14) · [Buildings and technology](Manual.md#printed-page-17) · [Battle](Manual.md#printed-page-20) · [Credits](Manual.md#printed-page-22)

## GOG 1.0 (32003) runtime import

[Import record and instructions](sources/gog-32003/README.md) · [File manifest](sources/gog-32003/manifest.json) · [Validation report](sources/gog-32003/validation.json) · [Importer](tools/clash_assets.py)

The supplied 19-part installer archive was verified and extracted into a 60-file original runtime. Its manual matches the existing PDF. The prepared ZIP is 373,319,846 bytes; the unpacked runtime is 517,940,933 bytes.

**Only the manifest, tooling and documentation are checked in. The runtime ZIP has not yet been uploaded to GitHub.** It was delivered in the originating chat; the import instructions include checksum-verified unpacking and a GitHub release publishing command. Windows setup and game launch were not executed.

## Rights

Original copyright notices are retained. This transcription does not grant a license to the original source material. The manual's installation, safety, and legal text is historical source content, not updated advice.

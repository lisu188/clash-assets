# Clash GOG 1.0 (32003)

## Import status

The 19 user-supplied 7z volumes were joined and verified on 2026-09-07. The archive contained `setup_clash_1.0_(32003).exe` (479,029,728 bytes). Its contents were extracted with innoextract 1.9, without running Windows setup.

The prepared runtime contains **60 original files, 517,940,933 bytes**, and the empty `gfx/cache` and `save` directories. A verified ZIP, `clash-gog-32003-runtime.zip`, was produced (373,319,846 bytes).

**The runtime binary ZIP has NOT been uploaded to this repository or a GitHub release.** The connected GitHub tool does not accept local binary uploads; a file-staging attempt also failed before creating any Drive file. The ZIP was delivered separately in the originating chat. This directory records the completed extraction, not a completed binary publication. `validation.json` is a historical import report.

## Contents

| Path | Files | Bytes |
| --- | ---: | ---: |
| `Data/` | 11 | 311,920,787 |
| `AVI/` | 22 | 181,532,828 |
| `DOSBOX/` | 15 | 8,815,238 |
| `strateg/` | 2 | 106,809 |
| Root files | 10 | 15,565,271 |

The runtime retains `clash95.exe`, `ddraw.dll`, DirectX wrapper settings, GOG metadata, the supplied DOSBox files and their license/source archive, the manual, video, sound, map and resource archives. The source is the English-language GOG build, game ID `2056790662`.

GOG Galaxy reconstruction places many files at the extraction root. The remaining `app/` contents are merged into that root. The `__redist/`, `tmp/` and `commonappdata/` installer support directories are not runtime assets and are excluded from this ZIP. The original EXE still contains them.

The installer manual is byte-identical to the repository's existing `Manual.pdf` (Git blob `868b0bd1e82d3647e272af9b686507ea0c6ad97c`). Neither that PDF nor its existing transcription was changed.

## Verification and extraction

Python 3.11 or later is required. Run commands from the repository root.

```console
python tools/clash_assets.py verify-package /path/to/clash-gog-32003-runtime.zip
python tools/clash_assets.py unpack /path/to/clash-gog-32003-runtime.zip --destination runtime/gog-32003
python tools/clash_assets.py verify runtime/gog-32003
```

`unpack` requires only the Python standard library. It validates the complete ZIP checksum, rejects unexpected paths, verifies each extracted file and refuses to overwrite an existing destination. `verify` is intended for an unchanged reference copy; saves or modified settings will correctly be reported as differences.

To reproduce from the original installer, install [innoextract](https://constexpr.org/innoextract/) and run:

```console
python tools/clash_assets.py extract "setup_clash_1.0_(32003).exe" --destination runtime/gog-32003
```

The first `.001` volume can also be supplied with all 19 parts beside it. That path additionally requires `7z` on PATH (or a standard Windows 7-Zip installation). Volume names may have a different common prefix, but their numbers, bytes and checksums must match the manifest. `--innoextract /path/to/innoextract` selects an explicit executable.

This prepares the original runtime directory. It does **not** install DirectX, register codecs, create registry entries or shortcuts, execute GOG installer scripts, or prove that the game launches. For a native Windows installation, use the original EXE.

## Finish the GitHub publication

`Data/MUSIC.RES` is 112,388,864 bytes, above GitHub's ordinary 100 MiB file limit. Do not commit the runtime directory as regular Git blobs. Publish the verified ZIP as a release asset instead; the runtime and ZIP outputs are ignored by Git.

With GitHub CLI installed and authenticated for this repository:

```console
python tools/clash_assets.py publish /path/to/clash-gog-32003-runtime.zip
```

This verifies the package and creates the `gog-1.0-32003` release targeting `main`, then uploads the ZIP under its canonical filename. It does not overwrite an existing release. The publishing command was prepared but could not be exercised in the originating environment.

## Evidence

`manifest.json` records all 19 volume hashes, joined-archive and installer hashes, archive-header CRC results, all 60 runtime paths/sizes/SHA-256 values, extraction-path mapping and empty directories. `package.json` records the ZIP checksum. `validation.json` records the 10 passing unit tests, ZIP CRC validation, successful unpack-and-verify test, and a second independent installer extraction matching all 60 files.

The GitHub metadata tests do not require game binaries. They do not substitute for a Windows launch test.

## Rights and references

Original rights and third-party notices remain with their respective holders. This import does not grant a new license to the game or its assets.

- [innoextract documentation](https://constexpr.org/innoextract/innoextract.1)
- [GitHub large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
- [GitHub CLI release creation](https://cli.github.com/manual/gh_release_create)

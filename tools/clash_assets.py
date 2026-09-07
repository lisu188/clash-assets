import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources' / 'gog-32003'


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_path(value: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or '..' in path.parts or '\\' in value or ':' in value:
        raise ValueError(f'Unsafe relative path: {value}')
    return Path(*path.parts)


def load_manifest() -> dict:
    manifest = json.loads((SOURCE / 'manifest.json').read_text(encoding='utf-8'))
    paths = [entry['path'] for entry in manifest['runtime']['files']]
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate manifest paths')
    for path in paths + manifest['runtime']['empty_directories']:
        safe_path(path)
    if len(paths) != manifest['runtime']['file_count']:
        raise ValueError('Manifest count mismatch')
    return manifest


def check_file(path: Path, expected: dict) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f'Missing or non-regular file: {path}')
    if path.stat().st_size != expected['size'] or digest(path) != expected['sha256']:
        raise ValueError(f'Checksum or size mismatch: {path}')


def verify(root: Path, manifest: dict) -> None:
    expected = {entry['path'] for entry in manifest['runtime']['files']}
    for entry in manifest['runtime']['files']:
        relative = safe_path(entry['path'])
        candidate = root / relative
        if not candidate.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Path escapes runtime: {relative}')
        check_file(candidate, entry)
    extra = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() not in expected)
    if extra:
        raise ValueError(f'Unexpected files in reference runtime: {extra}')
    for directory in manifest['runtime']['empty_directories']:
        candidate = root / safe_path(directory)
        if candidate.is_symlink() or not candidate.is_dir():
            raise ValueError(f'Missing runtime directory: {directory}')
    print(f"Verified {len(expected)} files, {manifest['runtime']['total_bytes']} bytes")


def check_package(path: Path) -> dict:
    package = json.loads((SOURCE / 'package.json').read_text(encoding='utf-8'))
    check_file(path, package)
    return package


def materialize(source: Path, destination: Path, manifest: dict, package: bool) -> None:
    if destination.exists():
        raise ValueError(f'Destination already exists: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.clash-', dir=destination.parent) as temporary:
        staging = Path(temporary) / 'runtime'
        staging.mkdir()
        if package:
            check_package(source)
            with zipfile.ZipFile(source) as archive:
                actual = [info.filename for info in archive.infolist() if not info.is_dir()]
                expected = {'Clash/' + entry['path'] for entry in manifest['runtime']['files']}
                if len(actual) != len(set(actual)) or set(actual) != expected:
                    raise ValueError('ZIP contents do not match the runtime manifest')
                for entry in manifest['runtime']['files']:
                    target = staging / safe_path(entry['path'])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open('Clash/' + entry['path']) as stream, target.open('wb') as output:
                        shutil.copyfileobj(stream, output)
        else:
            for entry in manifest['runtime']['files']:
                original = source / safe_path(entry['extracted_path'])
                if not original.resolve().is_relative_to(source.resolve()):
                    raise ValueError('Extracted file escapes the source directory')
                check_file(original, entry)
                target = staging / safe_path(entry['path'])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, target)
        for directory in manifest['runtime']['empty_directories']:
            (staging / safe_path(directory)).mkdir(parents=True, exist_ok=True)
        verify(staging, manifest)
        staging.rename(destination)
    print(f'Runtime files prepared in {destination}; Windows setup and the game were not executed')


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    if name == '7z' and os.name == 'nt':
        candidate = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / '7-Zip/7z.exe'
        if candidate.is_file():
            return str(candidate)
    if Path(name).is_file():
        return str(Path(name).resolve())
    raise ValueError(f'Required executable not found: {name}')


def extract(source: Path, destination: Path, manifest: dict, innoextract: str) -> None:
    if destination.exists():
        raise ValueError(f'Destination already exists: {destination}')
    with tempfile.TemporaryDirectory(prefix='clash-installer-') as temporary:
        work = Path(temporary)
        installer = source
        if source.suffix == '.001':
            combined = work / 'setup.7z'
            prefix = source.name[:-4]
            with combined.open('wb') as output:
                for index, expected in enumerate(manifest['split_archive']['parts'], start=1):
                    part = source.with_name(f'{prefix}.{index:03d}')
                    check_file(part, expected)
                    with part.open('rb') as stream:
                        shutil.copyfileobj(stream, output)
            check_file(combined, manifest['split_archive']['archive'])
            subprocess.run([executable('7z'), 'x', '-y', f'-o{work / "installer"}', str(combined)], check=True)
            installer = work / 'installer' / manifest['installer']['path']
        elif source.suffix.lower() != '.exe':
            raise ValueError('Use the .exe installer or the first .001 volume')
        check_file(installer, manifest['installer'])
        extracted = work / 'extracted'
        subprocess.run([executable(innoextract), '--extract', '--gog', '--output-dir', str(extracted), str(installer)], check=True)
        materialize(extracted, destination, manifest, package=False)


def publish(package: Path, repository: str) -> None:
    metadata = check_package(package)
    gh = executable('gh')
    subprocess.run([gh, 'auth', 'status'], check=True)
    with tempfile.TemporaryDirectory(prefix='clash-release-') as temporary:
        canonical = Path(temporary) / metadata['filename']
        try:
            os.link(package, canonical)
        except OSError:
            shutil.copy2(package, canonical)
        notes = 'Original Clash GOG 1.0 (32003) runtime: 60 files. SHA-256: ' + metadata['sha256'] + '. Files extracted with innoextract; Windows setup and game execution are not validated. Original rights remain with their respective holders.'
        subprocess.run([gh, 'release', 'create', 'gog-1.0-32003', str(canonical), '--repo', repository, '--target', 'main', '--title', 'Clash GOG 1.0 (32003) runtime', '--notes', notes], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description='Verify, unpack and publish the original Clash GOG 32003 runtime')
    subparsers = parser.add_subparsers(dest='command', required=True)
    for command in ('verify', 'verify-package', 'unpack', 'extract', 'publish'):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument('source', type=Path)
        if command in {'unpack', 'extract'}:
            command_parser.add_argument('--destination', type=Path, default=ROOT / 'runtime/gog-32003')
        if command == 'extract':
            command_parser.add_argument('--innoextract', default='innoextract')
        if command == 'publish':
            command_parser.add_argument('--repo', default='lisu188/clash-assets')
    args = parser.parse_args()
    try:
        manifest = load_manifest()
        if args.command == 'verify':
            verify(args.source, manifest)
        elif args.command == 'verify-package':
            print(json.dumps(check_package(args.source), indent=2))
        elif args.command == 'unpack':
            materialize(args.source, args.destination, manifest, package=True)
        elif args.command == 'extract':
            extract(args.source, args.destination, manifest, args.innoextract)
        elif args.command == 'publish':
            publish(args.source.resolve(), args.repo)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

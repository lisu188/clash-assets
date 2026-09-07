import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('clash_assets', Path(__file__).resolve().parents[1] / 'tools/clash_assets.py')
assets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(assets)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.runtime = self.root / 'runtime'
        (self.runtime / 'Data').mkdir(parents=True)
        (self.runtime / 'save').mkdir()
        self.data = b'original reference data'
        (self.runtime / 'Data/test.res').write_bytes(self.data)
        self.entry = {'path': 'Data/test.res', 'extracted_path': 'app/Data/test.res', 'size': len(self.data), 'sha256': hashlib.sha256(self.data).hexdigest()}
        self.manifest = {'runtime': {'file_count': 1, 'total_bytes': len(self.data), 'files': [self.entry], 'empty_directories': ['save']}}

    def test_original_files_verify(self):
        assets.verify(self.runtime, self.manifest)

    def test_corruption_is_rejected(self):
        (self.runtime / 'Data/test.res').write_bytes(b'x' * len(self.data))
        with self.assertRaises(ValueError):
            assets.verify(self.runtime, self.manifest)

    def test_missing_file_is_rejected(self):
        (self.runtime / 'Data/test.res').unlink()
        with self.assertRaises(ValueError):
            assets.verify(self.runtime, self.manifest)

    def test_untracked_file_is_rejected(self):
        (self.runtime / 'extra.txt').touch()
        with self.assertRaises(ValueError):
            assets.verify(self.runtime, self.manifest)

    def test_missing_save_directory_is_rejected(self):
        (self.runtime / 'save').rmdir()
        with self.assertRaises(ValueError):
            assets.verify(self.runtime, self.manifest)

    def test_unsafe_paths_are_rejected(self):
        for value in ('../outside', '/outside', 'Data/../../outside', 'C:/outside', 'Data\\outside', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                assets.safe_path(value)

    def test_existing_destination_is_preserved(self):
        with self.assertRaises(ValueError):
            assets.materialize(self.runtime, self.runtime, self.manifest, package=False)
        self.assertEqual((self.runtime / 'Data/test.res').read_bytes(), self.data)

    def make_package(self, extra=False):
        archive = self.root / 'runtime.zip'
        with zipfile.ZipFile(archive, 'w') as output:
            output.writestr('Clash/Data/test.res', self.data)
            if extra:
                output.writestr('../outside', b'not allowed')
        metadata = {'filename': archive.name, 'size': archive.stat().st_size, 'sha256': assets.digest(archive)}
        (self.root / 'package.json').write_text(json.dumps(metadata))
        return archive

    def test_package_unpacks_and_verifies(self):
        archive = self.make_package()
        destination = self.root / 'installed'
        with patch.object(assets, 'SOURCE', self.root):
            assets.materialize(archive, destination, self.manifest, package=True)
        assets.verify(destination, self.manifest)

    def test_package_with_unexpected_path_is_rejected(self):
        archive = self.make_package(extra=True)
        destination = self.root / 'installed'
        with patch.object(assets, 'SOURCE', self.root), self.assertRaises(ValueError):
            assets.materialize(archive, destination, self.manifest, package=True)
        self.assertFalse(destination.exists())
        self.assertFalse((self.root / 'outside').exists())

    def test_failed_integrity_check_does_not_create_destination(self):
        archive = self.make_package()
        archive.write_bytes(b'corrupt')
        destination = self.root / 'installed'
        with patch.object(assets, 'SOURCE', self.root), self.assertRaises(ValueError):
            assets.materialize(archive, destination, self.manifest, package=True)
        self.assertFalse(destination.exists())


if __name__ == '__main__':
    unittest.main()

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sync', ROOT / 'tools/sync_redpaper.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class FetchTests(unittest.TestCase):
    def response(self, payload):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = payload
        return response

    def test_versioned_client_header(self):
        with patch.object(sync, 'urlopen', return_value=self.response(b'// JavaScript')) as opener:
            self.assertEqual(sync.fetch(sync.SOURCES['RedPaper_remove_ads.js']), b'// JavaScript')
        request = opener.call_args.args[0]
        self.assertEqual(request.get_header('User-agent'), sync.USER_AGENT)
        self.assertTrue(sync.USER_AGENT.startswith('Loon/'))

    def test_error_pages_and_invalid_sizes_are_rejected(self):
        for payload in [b'', b'<!DOCTYPE html><html>blocked</html>', b'x' * 2_000_001]:
            with self.subTest(size=len(payload)), patch.object(sync, 'urlopen', return_value=self.response(payload)):
                with self.assertRaises(ValueError):
                    sync.fetch(sync.SOURCES['RedPaper_remove_ads.js'])


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ['tools', 'tests', 'upstream', 'Scripts', 'Surge']:
            shutil.copytree(ROOT / folder, self.root / folder)
        for name in ['RedPaperSurge.js', 'RedPaper_remove_ads.sgmodule']:
            shutil.copyfile(ROOT / name, self.root / name)
        (self.root / 'upstream/redpaper/sync.json').unlink(missing_ok=True)
        self.sources = {url: (self.root / 'upstream/redpaper' / name).read_bytes()
                        for name, url in sync.SOURCES.items()}

    def run_sync(self):
        with patch.object(sync, 'ROOT', self.root), patch.object(sync, 'fetch', side_effect=self.sources.__getitem__):
            sync.main()

    def test_unchanged(self):
        receipt = self.root / 'upstream/redpaper/sync.json'
        receipt.write_text('{}\n')
        self.run_sync()
        self.assertEqual(receipt.read_text(), '{}\n')

    def test_initial_live_verification_records_receipt(self):
        self.run_sync()
        self.assertTrue((self.root / 'upstream/redpaper/sync.json').exists())

    def test_supported_change_publishes(self):
        self.sources[sync.SOURCES['RedPaper_remove_ads.js']] += b'\n// upstream update\n'
        self.run_sync()
        self.assertTrue((self.root / 'upstream/redpaper/sync.json').exists())
        self.assertIn(b'// upstream update', (self.root / 'Scripts/Surge/RedPaperSurge.js').read_bytes())
        self.assertEqual((self.root / 'RedPaperSurge.js').read_bytes(), (self.root / 'Scripts/Surge/RedPaperSurge.js').read_bytes())

    def test_unknown_directive_preserves_existing_files(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.sources[sync.SOURCES['RedPaper_remove_ads.lpx']] += b'\n[Unsupported]\nfoo=bar\n'
        with self.assertRaises(Exception):
            self.run_sync()
        for path, data in before.items():
            self.assertEqual((self.root / path).read_bytes(), data)
        self.assertFalse((self.root / 'upstream/redpaper/sync.json').exists())


if __name__ == '__main__':
    unittest.main()

import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/install_toolchain.py'

class ToolchainSafety(unittest.TestCase):
    def load_installer(self):
        self.assertTrue(SCRIPT.exists(), 'verified installer not implemented')
        spec = importlib.util.spec_from_file_location('installer', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_digest_mismatch_rejected(self):
        installer = self.load_installer()
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'archive'
            archive.write_bytes(b'wrong bytes')
            with self.assertRaisesRegex(ValueError, 'SHA-256'):
                installer.verify_digest(archive, '0' * 64)

    def test_traversal_and_escaping_link_rejected_without_extraction(self):
        installer = self.load_installer()
        for name, target in [('../escape', None), ('link', '../../escape')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                archive = Path(folder) / 'bad.tar.gz'
                with tarfile.open(archive, 'w:gz') as tar:
                    info = tarfile.TarInfo(name)
                    if target:
                        info.type, info.linkname = tarfile.SYMTYPE, target
                        tar.addfile(info)
                    else:
                        info.size = 1
                        tar.addfile(info, io.BytesIO(b'x'))
                with self.assertRaises((ValueError, tarfile.FilterError)):
                    installer.extract_checked(archive, Path(folder) / 'out')
                self.assertFalse((Path(folder).parent / 'escape').exists())

    def test_regular_archive_extracted(self):
        installer = self.load_installer()
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'good.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                info = tarfile.TarInfo('bin/probe')
                info.size = 2
                tar.addfile(info, io.BytesIO(b'ok'))
            installer.extract_checked(archive, Path(folder) / 'out')
            self.assertEqual((Path(folder) / 'out/bin/probe').read_bytes(), b'ok')

if __name__ == '__main__':
    unittest.main()

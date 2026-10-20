import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest
import os
import shutil
import subprocess

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/install_toolchain.py'

class ToolchainSafety(unittest.TestCase):
    def test_wrapper_rejects_missing_local_moon_instead_of_global_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'scripts').mkdir()
            wrapper = root/'scripts/with-toolchain.sh'
            shutil.copyfile(SCRIPT.parent/'with-toolchain.sh', wrapper)
            local_bin = root/'.tools/moonbit/0.10.14+7d59c7ec9/bin'
            local_bin.mkdir(parents=True)
            compiler = local_bin/'moonc'
            compiler.write_text('#!/bin/sh\necho "v0.10.14+7d59c7ec9 synthetic fixture"\n')
            compiler.chmod(0o755)
            global_bin = root/'global-bin'
            global_bin.mkdir()
            fallback = global_bin/'moon'
            fallback.write_text('#!/bin/sh\necho UNLOCKED_MOON_EXECUTED\n')
            fallback.chmod(0o755)
            result = subprocess.run(['/bin/sh', str(wrapper), 'moon', 'version'],
                                    env=dict(os.environ, PATH=str(global_bin)+os.pathsep+os.environ['PATH']),
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, 'incomplete local install must fail closed')
            self.assertNotIn('UNLOCKED_MOON_EXECUTED', result.stdout)
            for name in ['moon', 'moonrun', 'moonfmt']:
                executable = local_bin/name
                executable.write_text('#!/bin/sh\necho LOCKED_TOOL_EXECUTED\n')
                executable.chmod(0o755)
            result = subprocess.run(['/bin/sh', str(wrapper), 'moon', 'version'],
                                    env=dict(os.environ, PATH=str(global_bin)+os.pathsep+os.environ['PATH']),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'LOCKED_TOOL_EXECUTED\n')

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

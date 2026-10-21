import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'bootstrap_reference.py'

class BootstrapSafety(unittest.TestCase):
    def installer(self):
        self.assertTrue(SCRIPT.exists(), 'reference bootstrap not implemented')
        spec = importlib.util.spec_from_file_location('reference_bootstrap', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_rejects_external_destination(self):
        installer = self.installer()
        with tempfile.TemporaryDirectory() as folder:
            for name in ['../outside', '/tmp/outside', '.venv-reference/child', 'global']:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    installer.destination_for(Path(folder), name)

    def test_refuses_overwriting_existing_environment(self):
        installer = self.installer()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'.venv-reference').mkdir()
            with self.assertRaises(FileExistsError):
                installer.destination_for(root, '.venv-reference')
            self.assertEqual(installer.destination_for(root,'.venv-reference-fresh'), root/'.venv-reference-fresh')

if __name__ == '__main__':
    unittest.main()

"""Unified checks fail closed; synthetic runners never stand in for live gates."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify


class UnifiedGate(unittest.TestCase):
    def test_missing_project_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'proof'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/verify.py'),'--mode','local','--evidence',str(output)],cwd=directory,capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(json.loads((output/'report.json').read_bytes())['passed'])

    def test_current_directory_identity_not_script_location(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'moon.mod').write_text('name = "someone/else"\nversion = "0.1.0"\n')
            with self.assertRaisesRegex(ValueError,'MoonEventEval'):verify.project_identity(root)

    def test_missing_binary_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'binary'):verify.require_binary(Path(directory)/'missing')

    def test_nonzero_subcommand_retains_failed_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with self.assertRaises(verify.VerificationFailure):
                verify.run_step('deliberate_failure',[sys.executable,'-c','import sys;print("expected failure");sys.exit(7)'],root,root/'evidence',{})
            row=json.loads((root/'evidence/deliberate_failure/receipt.json').read_bytes())
            self.assertEqual(row['exit_code'],7)
            self.assertIn(b'expected failure',(root/'evidence/deliberate_failure/stdout').read_bytes())

    def test_missing_reference_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'reference'):verify.reference_python(Path(directory))

    def test_mutated_toolchain_archive_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'docs').mkdir();(root/'docs/toolchain.lock.json').write_bytes((ROOT/'docs/toolchain.lock.json').read_bytes())
            (root/'.tools/downloads').mkdir(parents=True)
            (root/'.tools/downloads/moonbit.tar.gz').write_bytes(b'wrong archive')
            with self.assertRaisesRegex(ValueError,'SHA-256'):verify.verify_toolchain(root)

    def test_archive_without_license_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            archive=Path(directory)/'missing.zip'
            with zipfile.ZipFile(archive,'w') as z:z.writestr('moon.mod','name = "local/mooneventeval"\n')
            with self.assertRaisesRegex(ValueError,'LICENSE'):verify.validate_package_archive(archive)

    def test_ci_permissions_and_unpinned_action_never_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'.github/workflows').mkdir(parents=True);(root/'docs').mkdir()
            shutil.copyfile(ROOT/'docs/ci-actions.lock.json',root/'docs/ci-actions.lock.json')
            original=json.loads((ROOT/'.github/workflows/ci.yml').read_bytes())
            for mode in ['permissions','action','command']:
                body=json.loads(json.dumps(original))
                if mode=='permissions':body['permissions']={'contents':'write'}
                elif mode=='action':body['jobs']['verify']['steps'][0]['uses']='actions/checkout@v6'
                else:
                    for step in body['jobs']['verify']['steps']:
                        if step.get('name')=='Same complete verifier as local':step['run']='echo skipped'
                (root/'.github/workflows/ci.yml').write_text(json.dumps(body))
                with self.subTest(mode=mode),self.assertRaises(ValueError):verify.validate_ci_config(root)

    def test_zero_or_skipped_suite_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);(folder/'stdout').write_bytes(b'')
            for text in ['Ran 0 tests in 0.001s\n\nOK\n','Ran 21 tests in 0.001s\n\nOK (skipped=1)\n']:
                (folder/'stderr').write_text(text)
                with self.subTest(text=text),self.assertRaises(ValueError):verify.check_test_protocol(folder,'python',20)

    def test_artifact_report_cannot_be_missing_skipped_or_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report.json'
            for body in [None,dict(passed=False),dict(passed=True,skipped=True),dict(passed=1)]:
                if body is not None:path.write_text(json.dumps(body))
                with self.subTest(body=body),self.assertRaises(ValueError):verify.require_pass_report(path)


if __name__=='__main__':unittest.main()

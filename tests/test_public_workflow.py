"""External annotation workflow must run the product and reject altered evidence."""
import json
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'demo/public-data'


class PublicWorkflow(unittest.TestCase):
    def invoke(self, output, data=DATA):
        return subprocess.run([sys.executable, DATA/'reproduce.py', '--check',
                               '--data-dir', data, '--output', output],
                              cwd=ROOT, capture_output=True, timeout=120)

    def test_public_annotations_round_trip_and_actionable_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'run'
            result=self.invoke(output)
            self.assertEqual(result.returncode,0,result.stderr.decode(errors='replace'))
            report=json.loads((output/'report.json').read_bytes())
            self.assertIs(report['passed'],True)
            self.assertEqual(report['product_calls'],6)
            self.assertEqual(report['source_license'],'CC-BY-4.0')
            self.assertEqual(report['baseline_counts'],dict(reference=11,prediction=11,tp=11,fp=0,fn=0))
            self.assertEqual(report['regressed_counts'],dict(reference=11,prediction=11,tp=9,fp=2,fn=2))
            shift=json.loads((output/'explain-shift.json').read_bytes())
            duplicate=json.loads((output/'explain-duplicate.json').read_bytes())
            self.assertIs(shift['basis']['eligible'],False)
            self.assertEqual(shift['basis']['onset_delta_s'],'0.201')
            self.assertIs(duplicate['basis']['eligible'],True)
            self.assertIn('受控',(output/'analysis.md').read_text())

    def test_changed_input_or_snapshot_cannot_pass(self):
        for name in ['reference.tsv','output/regressed.json']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root=Path(directory);copy=root/'data';shutil.copytree(DATA,copy)
                path=copy/name
                if name=='reference.tsv':path.write_bytes(path.read_bytes().replace(b'0.000',b'0.001',1))
                else:
                    report=json.loads(path.read_bytes());report['summary']['counts']['tp']=99
                    path.write_text(json.dumps(report)+'\n')
                result=self.invoke(root/'run',copy)
                self.assertNotEqual(result.returncode,0)
                receipt=root/'run/report.json'
                if receipt.exists():
                    recorded=json.loads(receipt.read_bytes())
                    self.assertIsNot(recorded.get('passed'),True)
                    self.assertEqual(recorded['product_calls'],0 if name=='reference.tsv' else 4)


    def test_modified_provenance_is_rejected(self):
        for field,value in [('commit','0'*40),('authors',['Incorrect attribution']),
                            ('source_url','https://example.invalid/data'),
                            ('license_url','https://example.invalid/license')]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root=Path(directory);copy=root/'data';shutil.copytree(DATA,copy)
                path=copy/'SOURCE.json';source=json.loads(path.read_bytes());source[field]=value
                path.write_text(json.dumps(source)+'\n')
                result=self.invoke(root/'run',copy)
                self.assertNotEqual(result.returncode,0)
                receipt=json.loads((root/'run/report.json').read_bytes())
                self.assertIs(receipt['passed'],False)
                self.assertEqual(receipt['product_calls'],0)

    def test_timed_out_process_retains_partial_streams_and_invocation(self):
        # A real sleeping process checks harness receipts, not event-scoring correctness.
        spec=importlib.util.spec_from_file_location('public_replay_timeout_probe',DATA/'reproduce.py')
        replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
        replay.COMMAND_TIMEOUT_SECONDS=0.5
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);slow=root/'slow-process'
            slow.write_text('#!'+sys.executable+'\nimport os,time\nos.write(1,b"partial stdout")\nos.write(2,b"partial stderr")\ntime.sleep(5)\n')
            slow.chmod(0o700)
            from argparse import Namespace
            args=Namespace(output=root/'run',data_dir=DATA,bin=slow,write=False)
            with self.assertRaises(ValueError):replay.replay(args)
            report=json.loads((root/'run/report.json').read_bytes())
            self.assertIs(report['passed'],False)
            self.assertEqual(report['product_calls'],1)
            self.assertIs(report['receipts'][0]['timed_out'],True)
            self.assertEqual((root/'run/task-baseline.json').read_bytes(),b'partial stdout')
            self.assertEqual((root/'run/task-baseline.stderr').read_bytes(),b'partial stderr')

if __name__=='__main__':unittest.main()

"""Real native TSV import -> task JSON -> evaluation, and atomic failures."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
HEADER = b'filename\tonset\toffset\tevent_label\n'


class TsvCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = Path(os.environ['MEE_BIN']).resolve()
        cls.tmp = tempfile.TemporaryDirectory(prefix='mee-tsv-cli-')
        cls.folder = Path(cls.tmp.name)
        cls.evidence = Path(os.environ.get('MEE_EVIDENCE', cls.folder / 'evidence')) / 'tsv'
        cls.evidence.mkdir(parents=True, exist_ok=True)
        cls.sequence = itertools.count()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def call(self, *args, expected=0):
        result = subprocess.run([str(self.exe), *map(str, args)], cwd=ROOT,
                                capture_output=True, timeout=8)
        out = self.evidence / f'{next(self.sequence):03d}-{self._testMethodName}'
        out.mkdir()
        (out / 'stdout').write_bytes(result.stdout)
        (out / 'stderr').write_bytes(result.stderr)
        for i, arg in enumerate(args):
            path = Path(arg)
            if path.is_file() and path.stat().st_size < 9_000_000:
                (out / f'input-{i}').write_bytes(path.read_bytes())
        (out / 'receipt.json').write_text(json.dumps(dict(args=list(map(str, args)),
            exit_code=result.returncode, stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
            stderr_sha256=hashlib.sha256(result.stderr).hexdigest()), indent=2))
        self.assertEqual(result.returncode, expected, result.stderr.decode(errors='replace'))
        return result

    def inputs(self, reference, prediction):
        ref, pred = self.folder / 'reference.tsv', self.folder / 'prediction.tsv'
        ref.write_bytes(reference); pred.write_bytes(prediction)
        return ref, pred

    def test_import_then_evaluate_and_explain_without_conversion_script(self):
        ref, pred = self.inputs(HEADER + b'clip.wav\t10.1\t12\talarm\n',
            HEADER + b'clip.wav\t10.3\t12.2\talarm\nclip.wav\t10.3\t12.2\talarm\n')
        raw_ref, raw_pred = ref.read_bytes(), pred.read_bytes()
        result = self.call('import-tsv', ref, '--prediction', pred)
        self.assertEqual(result.stderr, b'')
        document = json.loads(result.stdout)
        self.assertEqual(document['schema_version'], 1)
        self.assertNotIn('summary', document)
        self.assertEqual(document['recordings'][0]['reference'][0]['id'], 'r2')
        self.assertEqual([x['id'] for x in document['recordings'][0]['prediction']], ['p2','p3'])
        self.assertEqual(document['recordings'][0]['prediction'][0]['onset_s'], '10.3')
        task = self.folder / 'task.json'; task.write_bytes(result.stdout)
        report = json.loads(self.call('evaluate', task, '--format', 'json').stdout)
        self.assertEqual(report['summary']['counts'], dict(reference=1,prediction=2,tp=1,fp=1,fn=0))
        explanation = json.loads(self.call('explain-pair', task, '--recording', 'clip.wav',
            '--reference','r2','--prediction','p3','--format','json').stdout)
        self.assertTrue(explanation['basis']['eligible'])
        self.assertEqual((ref.read_bytes(), pred.read_bytes()), (raw_ref, raw_pred))

    def test_invalid_rows_have_side_line_column_and_no_partial_task(self):
        for prediction, code, path in [
            (HEADER+b'clip.wav\t1e0\t2\ta\n', 'INVALID_DECIMAL', 'prediction[2].onset'),
            (HEADER+b'clip.wav\t1.0000001\t2\ta\n', 'INVALID_DECIMAL', 'prediction[2].onset'),
            (HEADER+b'clip.wav\t2\t1\ta\n', 'OUT_OF_RANGE', 'prediction[2].offset'),
            (HEADER+b'clip.wav\t1\t2\ta\textra\n', 'INVALID_TSV', 'prediction[2]'),
            (HEADER+b'\n', 'INVALID_TSV', 'prediction[2]'),
        ]:
            with self.subTest(code=code, path=path):
                ref,pred=self.inputs(HEADER+b'clip.wav\t1\t2\ta\n', prediction)
                result=self.call('import-tsv',ref,'--prediction',pred,expected=2)
                actual=json.loads(result.stdout)
                self.assertEqual(list(actual), ['schema_version','status','error'])
                self.assertEqual(actual['error']['code'], code)
                self.assertEqual(actual['error']['path'], path)
                self.assertEqual(result.stderr,b'')

    def test_bom_crlf_single_sided_recordings_and_file_errors(self):
        ref,pred=self.inputs(b'\xef\xbb\xbf'+HEADER.replace(b'\n',b'\r\n')+b'A.wav\t0\t1\ta\r\n',
            HEADER+b'B.wav\t0\t1\tb')
        raw=self.call('import-tsv',ref,'--prediction',pred,'--format','json').stdout
        doc=json.loads(raw)
        self.assertEqual(doc['labels'],['a','b'])
        self.assertEqual([x['id'] for x in doc['recordings']],['A.wav','B.wav'])
        task=self.folder/'single-side.json';task.write_bytes(raw)
        counts=json.loads(self.call('evaluate',task,'--format','json').stdout)['summary']['counts']
        self.assertEqual((counts['tp'],counts['fp'],counts['fn']),(0,1,1))
        missing=self.call('import-tsv',ref,'--prediction',self.folder/'missing.tsv',expected=2)
        self.assertEqual(json.loads(missing.stdout)['error']['code'],'FILE_ERROR')
        bad=self.call('import-tsv',ref,'--prediction',pred,'--format','text',expected=2)
        self.assertEqual(bad.stdout,b'')
        self.assertIn(b'INVALID_ARGUMENT',bad.stderr)


if __name__ == '__main__':
    unittest.main()

"""Real release-process contract; MEE_BIN must name the product, not moon run."""
import hashlib
import gzip
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NativeCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = Path(os.environ['MEE_BIN']).resolve()
        if not cls.exe.is_file():
            raise AssertionError(f'Product CLI missing: {cls.exe}')
        cls.tmp = tempfile.TemporaryDirectory(prefix='mee-cli-')
        cls.folder = Path(cls.tmp.name)
        cls.evidence = Path(os.environ.get('MEE_EVIDENCE', str(cls.folder / 'evidence'))).resolve()
        cls.evidence.mkdir(parents=True, exist_ok=True)
        cls.sequence = itertools.count()
        (cls.evidence / 'product.json').write_text(json.dumps(dict(
            path=str(cls.exe), sha256=hashlib.sha256(cls.exe.read_bytes()).hexdigest(),
            head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()), indent=2))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def call(self, *args, expected=0):
        result = subprocess.run([str(self.exe), *map(str, args)], cwd=ROOT,
                                capture_output=True, timeout=8)
        folder = self.evidence / f'{next(self.sequence):03d}-{self._testMethodName}'
        folder.mkdir()
        (folder / 'stdout').write_bytes(result.stdout)
        (folder / 'stderr').write_bytes(result.stderr)
        for i, arg in enumerate(args):
            p = Path(str(arg))
            if p.is_file() and p.stat().st_size <= 8_388_609 and p != self.exe:
                try:
                    raw = p.read_bytes()
                    if len(raw) > 65536:
                        (folder / f'input-{i}.bin.gz').write_bytes(gzip.compress(raw, mtime=0))
                    else: (folder / f'input-{i}.bin').write_bytes(raw)
                except PermissionError: pass  # unreadability is itself the fixture
        (folder / 'receipt.json').write_text(json.dumps(dict(
            args=list(map(str, args)), exit_code=result.returncode,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
            stderr_sha256=hashlib.sha256(result.stderr).hexdigest()), indent=2))
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def failure(self, path, code, exit_code=2):
        result = self.call('evaluate', path, '--format', 'json', expected=exit_code)
        self.assertEqual(result.stderr, b'')
        actual = json.loads(result.stdout.decode('utf-8'))
        self.assertEqual(list(actual), ['schema_version', 'status', 'error'])
        self.assertEqual(actual['status'], 'failed')
        self.assertEqual(actual['error']['code'], code)
        self.assertNotIn('NaN', result.stdout.decode('utf-8'))
        return actual

    def test_examples_text_json_and_unchanged_files(self):
        for example, counts in [('duplicate', (1, 1, 0)), ('greedy-trap', (2, 0, 0)), ('boundary', (1, 0, 0))]:
            path = ROOT / 'examples' / (example + '.json')
            before = path.read_bytes()
            result = self.call('evaluate', path, '--format', 'json')
            self.assertEqual(result.stderr, b'')
            actual = json.loads(result.stdout.decode('utf-8'))['summary']['counts']
            self.assertEqual(tuple(actual[k] for k in ['tp', 'fp', 'fn']), counts)
            text = self.call('evaluate', path)
            self.assertEqual(text.stderr, b'')
            self.assertIn('所选配对', text.stdout.decode('utf-8'))
            self.assertTrue(text.stdout.endswith(b'\n') and not text.stdout.endswith(b'\n\n'))
            self.assertEqual(path.read_bytes(), before)

    def test_explanation_and_ineligible_are_success(self):
        args = ['explain-pair', 'examples/boundary.json', '--recording', 'clip-01', '--reference', 'r1', '--prediction', 'p1']
        self.assertTrue(json.loads(self.call(*args, '--format', 'json').stdout)['basis']['eligible'])
        self.assertIn('onset_delta_s=0.2', self.call(*args).stdout.decode('utf-8'))
        document = json.loads((ROOT / 'examples/boundary.json').read_bytes())
        document['recordings'][0]['prediction'][0]['onset_s'] = '10.200001'
        path = self.folder / 'outside.json'; path.write_text(json.dumps(document))
        args[1] = str(path)
        self.assertFalse(json.loads(self.call(*args, '--format', 'json').stdout)['basis']['eligible'])
        counts = json.loads(self.call('evaluate', path, '--format', 'json').stdout)['summary']['counts']
        self.assertEqual((counts['tp'], counts['fp'], counts['fn']), (0, 1, 1))
        args[args.index('--reference') + 1] = 'absent'
        actual = self.call(*args, '--format', 'json', expected=2)
        self.assertEqual(json.loads(actual.stdout)['error']['code'], 'ID_NOT_FOUND')

    def test_bad_schema_utf8_depth(self):
        for name, raw, code, exit_code in [('schema', b'{}', 'MISSING_FIELD', 2),
                                          ('utf8', b'\xff', 'INVALID_UTF8', 2),
                                          ('depth', b'['*17 + b'0' + b']'*17, 'RESOURCE_LIMIT', 3)]:
            path = self.folder / name; path.write_bytes(raw)
            self.failure(path, code, exit_code)

    def test_dash_prefixed_query_ids(self):
        document = json.loads((ROOT / 'examples/boundary.json').read_bytes())
        rec = document['recordings'][0]; rec['id'] = '--clip'
        rec['reference'][0]['id'] = '--ref'; rec['prediction'][0]['id'] = '--pred'
        path = self.folder / 'dash-ids.json'; path.write_text(json.dumps(document))
        result = self.call('explain-pair', path, '--recording', '--clip', '--reference', '--ref', '--prediction', '--pred', '--format', 'json')
        actual = json.loads(result.stdout)
        self.assertEqual((actual['recording_id'], actual['reference']['id'], actual['prediction']['id']), ('--clip', '--ref', '--pred'))
        rec['id'] = '--format'; rec['reference'][0]['id'] = '--reference'; rec['prediction'][0]['id'] = '--format'
        path.write_text(json.dumps(document))
        result = self.call('explain-pair', path, '--recording', '--format', '--reference', '--reference', '--prediction', '--format', '--format', 'json')
        self.assertEqual(json.loads(result.stdout)['recording_id'], '--format')

    def test_input_size_equal_and_plus_one(self):
        raw = b'{"schema_version":1,"labels":["a"],"recordings":[]}'
        path = self.folder / 'limit.json'
        path.write_bytes(raw + b' ' * (8_388_608 - len(raw)))
        self.assertEqual(json.loads(self.call('evaluate', path, '--format', 'json').stdout)['status'], 'completed')
        with path.open('ab') as f: f.write(b' ')
        actual = self.failure(path, 'RESOURCE_LIMIT', 3)
        self.assertEqual((actual['error']['limit'], actual['error']['observed']), (8_388_608, 8_388_609))

    def test_files_missing_directory_fifo_unreadable_and_symlink(self):
        self.failure(self.folder / 'absent', 'FILE_ERROR')
        self.failure(self.folder, 'FILE_ERROR')
        fifo = self.folder / 'pipe'; os.mkfifo(fifo)
        self.failure(fifo, 'FILE_ERROR')
        path = self.folder / 'denied.json'; path.write_bytes(b'{}'); path.chmod(0)
        try:
            self.assertNotEqual(os.geteuid(), 0, 'unreadable-file proof requires nonroot')
            self.failure(path, 'FILE_ERROR')
        finally: path.chmod(0o600)
        link = self.folder / '任务链接.json'; link.symlink_to(ROOT / 'examples/duplicate.json')
        self.assertEqual(json.loads(self.call('evaluate', link, '--format', 'json').stdout)['summary']['counts']['tp'], 1)
        self.failure('/dev/null', 'FILE_ERROR')

    def test_argument_formats_and_help(self):
        for arg in ['--help', '--version']:
            result = self.call(arg); self.assertEqual(result.stderr, b''); self.assertIn(b'MoonEventEval', result.stdout)
        for args in [[], ['evaluate'], ['bad', '--format', 'json'], ['evaluate', 'absent', '--unknown', 'x', '--format', 'json'], ['--help', '--format', 'json']]:
            result = self.call(*args, expected=2)
            if 'json' in args:
                self.assertEqual(json.loads(result.stdout)['error']['code'], 'INVALID_ARGUMENT')
                self.assertEqual(result.stderr, b'')
            else: self.assertEqual(result.stdout, b''); self.assertIn(b'INVALID_ARGUMENT', result.stderr)
        for args in [['--format', 'bad'], ['--format', 'json', '--format', 'json']]:
            result = self.call('evaluate', 'absent', *args, expected=2)
            self.assertEqual(result.stdout, b''); self.assertIn(b'INVALID_ARGUMENT', result.stderr)

    def test_closed_stdout_pipe_terminates_nonzero(self):
        rfd, wfd = os.pipe(); os.close(rfd)
        try:
            result = subprocess.run([str(self.exe), 'evaluate', 'examples/duplicate.json', '--format', 'json'],
                                    cwd=ROOT, stdout=wfd, stderr=subprocess.PIPE, timeout=8)
        finally: os.close(wfd)
        (self.evidence / 'closed-pipe.stderr').write_bytes(result.stderr)
        (self.evidence / 'closed-pipe.json').write_text(json.dumps(dict(exit_code=result.returncode)))
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'FILE_ERROR', result.stderr)

    def test_large_unicode_output_chunking_and_partial_pipe_failure(self):
        recordings = []
        for i in range(64):
            event = lambda id: dict(id=id, label='a', onset_s='1', offset_s='2')
            recordings.append(dict(id='录' * 200 + str(i), reference=[event('参' * 200)], prediction=[event('预' * 200)]))
        path = self.folder / 'large-output.json'
        path.write_text(json.dumps(dict(schema_version=1, labels=['a'], recordings=recordings), ensure_ascii=False), encoding='utf-8')
        result = self.call('evaluate', path, '--format', 'json')
        self.assertGreater(len(result.stdout), 65536)
        actual = json.loads(result.stdout.decode('utf-8'))
        self.assertEqual(actual['summary']['counts']['tp'], 64)
        self.assertEqual(len(actual['matches']), 64)
        self.assertEqual({m['recording_id'] for m in actual['matches']}, {r['id'] for r in recordings})
        text = self.call('evaluate', path).stdout
        self.assertGreater(len(text), 65536)
        self.assertIn(recordings[-1]['id'], text.decode('utf-8'))
        proc = subprocess.Popen([str(self.exe), 'evaluate', str(path), '--format', 'json'], cwd=ROOT,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            prefix = proc.stdout.read(1024)
            proc.stdout.close(); proc.stdout = None
            _, stderr = proc.communicate(timeout=8)
        finally:
            if proc.poll() is None: proc.kill(); proc.communicate()
        (self.evidence / 'partial-pipe.prefix').write_bytes(prefix)
        (self.evidence / 'partial-pipe.stderr').write_bytes(stderr)
        (self.evidence / 'partial-pipe.json').write_text(json.dumps(dict(exit_code=proc.returncode, prefix_bytes=len(prefix))))
        self.assertEqual(proc.returncode, 2)
        self.assertIn(b'FILE_ERROR', stderr)
        self.assertEqual(len(prefix), 1024)
        with self.assertRaises(json.JSONDecodeError): json.loads(prefix)


if __name__ == '__main__':
    unittest.main()

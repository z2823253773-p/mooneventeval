"""Catch broken local imports, wrong report handling and misleading pair explanations."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LibraryExample(unittest.TestCase):
    def test_documented_moonbit_consumer_runs_without_python_scoring(self):
        # Real compiler + public library: no copied implementation or mocks.
        self.assertTrue((ROOT / 'examples/moonbit-consumer/moon.mod').is_file(),
                        'runnable public-library example is missing')
        result = subprocess.run(
            [ROOT / 'scripts/with-toolchain.sh', 'moon', '-C', 'examples/moonbit-consumer', 'run', 'main',
             '--target', 'native', '--release', '--deny-warn'],
            cwd=ROOT, capture_output=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        reports = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(reports), 3)
        evaluation, explanation, failure = reports
        self.assertEqual(evaluation['status'], 'completed')
        self.assertEqual(evaluation['summary']['counts'],
                         dict(reference=1, prediction=2, tp=1, fp=1, fn=0))
        self.assertEqual(evaluation['matches'][0]['prediction']['id'], 'p1')
        self.assertEqual(evaluation['false_positives'][0]['event']['id'], 'p2')
        self.assertEqual(explanation['status'], 'completed')
        self.assertEqual(explanation['prediction']['id'], 'p2')
        self.assertIs(explanation['basis']['eligible'], True)
        self.assertNotIn('summary', explanation)
        self.assertNotIn('work', explanation)
        self.assertEqual(failure['status'], 'failed')
        self.assertEqual(failure['error']['kind'], 'input')
        self.assertEqual(failure['error']['code'], 'INVALID_TYPE')
        self.assertEqual(failure['error']['path'], 'recordings[0].reference[0].onset_s')
        self.assertNotIn('summary', failure)


if __name__ == '__main__':
    unittest.main()

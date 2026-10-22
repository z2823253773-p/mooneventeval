import copy
import json
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

from validation import compare

ROOT = Path(__file__).resolve().parents[2]


def fixture(name='comparison-baseline'):
    return json.loads((ROOT / 'validation/fixtures' / (name + '.json')).read_bytes())


class QualificationTests(unittest.TestCase):
    def test_preserved_fixture_and_counterfeits(self):
        f = fixture()
        self.assertEqual(compare.compare_document(f['input'], f['product'], f['reference']), [])
        bad = copy.deepcopy(f['product']); bad['summary']['counts']['tp'] += 1
        self.assertTrue(compare.compare_document(f['input'], bad, f['reference']))
        bad = copy.deepcopy(f['product']); bad['by_recording'].pop()
        self.assertTrue(compare.compare_document(f['input'], bad, f['reference']))
        f = fixture('comparison-substitution'); bad = copy.deepcopy(f['reference'])
        bad['projected']['counts']['fp'] = bad['raw']['counts']['Nfp']
        bad['projected']['counts']['fn'] = bad['raw']['counts']['Nfn']
        self.assertTrue(compare.compare_document(f['input'], f['product'], bad))

    def test_equivalent_maximum_identity_is_allowed(self):
        f = fixture('comparison-equivalent'); report = copy.deepcopy(f['product'])
        report['matches'][0]['prediction'], report['false_positives'][0]['event'] = report['false_positives'][0]['event'], report['matches'][0]['prediction']
        self.assertEqual(compare.compare_document(f['input'], report, f['reference']), [])

    def test_failed_product_exit_cannot_hide_behind_valid_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); script = p / 'bad'
            script.write_text('#!/bin/sh\nprintf \'{"status":"completed"}\\n\'\nexit 2\n'); script.chmod(0o755)
            result = compare.run_file_product(script, fixture()['input'], p / 'run')
            self.assertEqual(result['exit_code'], 2)
            self.assertTrue(result['differences'])
            self.assertEqual((p / 'run/stdout').read_bytes(), b'{"status":"completed"}\n')

    def test_raw_reference_corruption_is_not_hidden(self):
        f = fixture('comparison-substitution')
        self.assertEqual(compare.compare_reference(f['input'], f['reference'], compare.oracle_document(f['input'])), [])
        bad = copy.deepcopy(f['reference']); bad['raw']['counts']['Nsubs'] = 0
        self.assertTrue(compare.compare_reference(f['input'], bad, compare.oracle_document(f['input'])))
        bad = copy.deepcopy(f['reference']); bad['raw']['metrics']['f_measure']['precision'] = 0.25
        self.assertTrue(compare.compare_reference(f['input'], bad, compare.oracle_document(f['input'])))

    def test_driver_retains_child_failure_and_returns_nonzero(self):
        from validation.qualify import run_qualification
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); exe = p / 'failed'
            exe.write_text('#!/bin/sh\nprintf \'{"status":"completed"}\\n\'\nexit 2\n'); exe.chmod(0o755)
            case = dict(name='failed-child', category='binary_grid', document=fixture()['input'])
            self.assertEqual(run_qualification(exe, p / 'proof', cases=[case]), 1)
            report = json.loads((p / 'proof/report.json').read_bytes())
            self.assertEqual(report['unexplained'], ['failed-child'])
            self.assertTrue((p / 'proof/failed-child/base/process.json').is_file())

    def test_boundary_classification_cannot_hide_wrong_product(self):
        from validation.qualify import run_qualification
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); exe = p / 'wrong'
            source = ROOT / 'evidence/T3/parity-final/decimal-onset-binary64-flip'
            document = json.loads((source / 'input.json').read_bytes())
            wrong = json.loads((source / 'product.json').read_bytes()); wrong['summary']['counts']['tp'] = 0
            exe.write_text(f'#!{sys.executable}\nimport sys\nsys.stdout.write({json.dumps(wrong)!r}+"\\n")\n'); exe.chmod(0o755)
            case = dict(name='wrong-boundary', category='exact_boundary', document=document)
            self.assertEqual(run_qualification(exe, p / 'proof', cases=[case]), 1)
            self.assertEqual(json.loads((p / 'proof/report.json').read_bytes())['unexplained'], ['wrong-boundary'])

    def test_unrelated_value_error_is_not_zero_collar_domain_evidence(self):
        from validation.qualify import run_qualification
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);exe=p/'exact'
            source=ROOT/'evidence/T3/parity-final/E7-fractional-microsecond'
            raw=(source/'product.stdout').read_bytes()
            exe.write_text(f'#!{sys.executable}\nimport sys\nsys.stdout.buffer.write({raw!r})\n');exe.chmod(0o755)
            case=dict(name='unexpected-reference-error',category='exact_boundary',document=json.loads((source/'input.json').read_bytes()))
            # Inject a reference-side error, and isolate this classification from
            # transforms: the observable decision must remain a failed run.
            with patch('validation.sed_reference.evaluate_document',side_effect=ValueError('unexpected adapter error')),patch('validation.qualify.transformations',return_value=[]):
                self.assertEqual(run_qualification(exe,p/'proof',cases=[case]),1)
            self.assertFalse(json.loads((p/'proof/report.json').read_bytes())['passed'])

    def test_exact_margin_preselection_and_determinism(self):
        from validation.generate_cases import qualification_cases, safe_margins
        f = fixture(); doc = f['input']
        self.assertEqual(safe_margins(doc)['unsafe'], [])
        doc = json.loads((ROOT / 'examples/boundary.json').read_bytes())
        self.assertTrue(safe_margins(doc)['unsafe'])
        a, excluded = qualification_cases(); b, other = qualification_cases()
        self.assertEqual((a, excluded), (b, other))
        self.assertTrue(excluded)
        self.assertGreaterEqual(sum(row['category'] == 'decimal_nonboundary' for row in a), 100)
        self.assertTrue(all(not safe_margins(row['document'])['unsafe'] for row in a if row['category'] == 'decimal_nonboundary'))


if __name__ == '__main__':
    unittest.main()

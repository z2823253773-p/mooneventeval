"""Real sed_eval self-checks; expected counts are independent synthetic fixtures."""
import importlib.util
import json
from pathlib import Path
import unittest

ADAPTER = Path(__file__).resolve().parents[1]/'sed_reference.py'

def event(identifier, label, onset, offset):
    return dict(id=identifier, label=label, onset_s=onset, offset_s=offset)

def task(reference, prediction, labels=None):
    return dict(schema_version=1, labels=labels or ['a'], recordings=[
        dict(id='clip', reference=reference, prediction=prediction)])

class ReferenceSelfCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = None
        if ADAPTER.exists():
            spec = importlib.util.spec_from_file_location('sed_reference', ADAPTER)
            cls.reference = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.reference)

    def evaluate(self, document):
        self.assertIsNotNone(self.reference, 'reference adapter not implemented')
        return self.reference.evaluate_document(document)

    def test_duplicate_prediction_preserves_raw_counts(self):
        result = self.evaluate(task([event('r','a','10','12')], [
            event('p1','a','10','12'),event('p2','a','10.05','12.05')]))
        self.assertEqual({k: result['raw']['counts'][k] for k in ['Ntp','Nsys','Nref']},
                         dict(Ntp=1,Nsys=2,Nref=1))
        self.assertEqual(result['projected']['counts'], dict(reference=1,prediction=2,tp=1,fp=1,fn=0))

    def test_A2_uses_original_optimal_matching(self):
        result = self.evaluate(task([
            event('r1','a','10','11'),event('r2','a','10.3','11.3')], [
            event('p1','a','10.15','11.15'),event('p2','a','9.85','10.85')]))
        self.assertEqual(result['raw']['counts']['Ntp'], 2)
        self.assertEqual(result['projected']['counts'], dict(reference=2,prediction=2,tp=2,fp=0,fn=0))

    def test_cross_label_substitution_is_not_projected_fp_fn(self):
        result = self.evaluate(task([event('r','A','1','2')], [event('p','B','1','2')], ['A','B']))
        self.assertEqual({k: result['raw']['counts'][k] for k in ['Ntp','Nsubs','Nfp','Nfn']},
                         dict(Ntp=0,Nsubs=1,Nfp=0,Nfn=0))
        self.assertEqual(result['projected']['counts'], dict(reference=1,prediction=1,tp=0,fp=1,fn=1))
        self.assertEqual(result['class_wise']['A']['counts']['Nfn'],1)
        self.assertEqual(result['class_wise']['B']['counts']['Nfp'],1)

    def test_empty_denominators_are_explicit_not_zero(self):
        result = self.evaluate(task([],[]))
        self.assertEqual(result['raw']['metrics']['f_measure']['precision'], {'nonfinite':'NaN'})
        self.assertIsNone(result['projected']['precision'])
        self.assertIsNone(result['projected']['recall'])
        self.assertIsNone(result['projected']['f1'])
        self.assertFalse(result['metric_definition_flags']['projected_precision_defined'])
        json.dumps(result, allow_nan=False)

    def test_empty_reference_recording_contributes_false_positives(self):
        document = task([event('r','a','0','1')],[event('p','a','0','1')])
        document['recordings'].append(dict(id='empty-ref', reference=[], prediction=[event('noise','a','5','6')]))
        result = self.evaluate(document)
        self.assertEqual(result['projected']['counts'], dict(reference=1,prediction=2,tp=1,fp=1,fn=0))
        self.assertEqual(result['raw']['counts']['Nsys'],2)

    def test_source_verification_rejects_modified_reference(self):
        self.assertIsNotNone(self.reference, 'reference adapter not implemented')
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            package = Path(folder)
            (package/'sound_event.py').write_text('# altered algorithm\n')
            with self.assertRaisesRegex(RuntimeError,'source'):
                self.reference.verify_sources(package)

    def test_zero_collar_is_explicit_upstream_domain_limit(self):
        document = task([],[])
        document['config'] = dict(collar_s='0', offset_ratio='0.5')
        with self.assertRaisesRegex(ValueError, 't_collar needs to be float > 0'):
            self.evaluate(document)
        self.assertFalse(self.evaluate(task([],[]))['metric_definition_flags']['zero_collar_supported'])

if __name__ == '__main__':
    unittest.main()

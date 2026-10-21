import copy
import unittest
from validation.compare import compare_document

DOC = dict(schema_version=1, labels=['a'], recordings=[])
EMPTY = dict(schema_version=1, semantics='collar-max-cardinality/v1', implementation_version='0.1.0',
             status='completed', config=dict(collar_s='0.2', offset_ratio='0.5'),
             summary=dict(counts=dict(reference=0,prediction=0,tp=0,fp=0,fn=0),precision=None,recall=None,f1=None),
             by_label=[dict(label='a',metrics=dict(counts=dict(reference=0,prediction=0,tp=0,fp=0,fn=0),precision=None,recall=None,f1=None))],
             by_recording=[],matches=[],false_positives=[],false_negatives=[],
             work=dict(candidate_checks=0,eligible_edges=0,matching_steps=0))
REF = dict(projected=EMPTY['summary'])


class ComparatorTests(unittest.TestCase):
    def test_hand_checked_empty_report(self):
        self.assertEqual(compare_document(DOC, EMPTY, REF), [])

    def test_wrong_count_is_detected(self):
        bad=copy.deepcopy(EMPTY); bad['summary']['counts']['tp']=1
        self.assertTrue(compare_document(DOC,bad,REF))

    def test_undefined_metric_cannot_be_zero(self):
        bad=copy.deepcopy(EMPTY); bad['summary']['f1']=0
        self.assertTrue(compare_document(DOC,bad,REF))

    def test_missing_rows_or_partial_report_is_detected(self):
        bad=copy.deepcopy(EMPTY); bad['by_label']=[]
        self.assertTrue(compare_document(DOC,bad,REF))
        self.assertTrue(compare_document(DOC,dict(status='completed'),REF))

    def test_reference_projection_mismatch_is_detected(self):
        bad=copy.deepcopy(REF); bad['projected']['counts']['fp']=1
        self.assertTrue(compare_document(DOC,EMPTY,bad))

    def test_counts_must_remain_integer_not_boolean_or_float(self):
        for invalid in [False, 0.0]:
            bad=copy.deepcopy(EMPTY);bad['summary']['counts']['tp']=invalid
            self.assertTrue(compare_document(DOC,bad,REF))

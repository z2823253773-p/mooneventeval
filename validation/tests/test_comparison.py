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

    def test_machine_metadata_and_work_types_are_not_coerced(self):
        for key,value in [('schema_version',True),('schema_version',1.0)]:
            bad=copy.deepcopy(EMPTY);bad[key]=value
            self.assertTrue(compare_document(DOC,bad,REF))
        for key in ['candidate_checks','eligible_edges']:
            for value in [False,0.0]:
                bad=copy.deepcopy(EMPTY);bad['work'][key]=value
                self.assertTrue(compare_document(DOC,bad,REF))

    def test_nested_extra_fields_are_rejected(self):
        for path in [('summary',),('work',),('by_label',0),('by_label',0,'metrics')]:
            bad=copy.deepcopy(EMPTY);obj=bad
            for component in path:obj=obj[component]
            obj['unexpected']=0
            self.assertTrue(compare_document(DOC,bad,REF))

    def test_selected_event_times_and_basis_keep_machine_types(self):
        document,report,reference=single_match_fixture()
        self.assertEqual(compare_document(document,report,reference),[])
        for value in [1,1.0,True,'1.000000']:
            bad=copy.deepcopy(report);bad['matches'][0]['reference']['onset_s']=value
            self.assertTrue(compare_document(document,bad,reference))
        bad=copy.deepcopy(report);bad['matches'][0]['basis']['onset_pass']=1
        self.assertTrue(compare_document(document,bad,reference))

    def test_match_row_extra_fields_are_rejected(self):
        document,report,reference=single_match_fixture()
        bad=copy.deepcopy(report);bad['matches'][0]['unexpected']=0
        self.assertTrue(compare_document(document,bad,reference))


def single_match_fixture():
    # Hand-checked single exact event pair; no product/oracle builder creates expectations.
    r=dict(id='r',label='a',onset_s='1',offset_s='2')
    p=dict(id='p',label='a',onset_s='1',offset_s='2')
    document=dict(schema_version=1,labels=['a'],recordings=[dict(id='x',reference=[r],prediction=[p])])
    metric=dict(counts=dict(reference=1,prediction=1,tp=1,fp=0,fn=0),precision=1,recall=1,f1=1)
    report=copy.deepcopy(EMPTY)
    report['summary']=copy.deepcopy(metric)
    report['by_label']=[dict(label='a',metrics=copy.deepcopy(metric))]
    report['by_recording']=[dict(recording_id='x',metrics=copy.deepcopy(metric))]
    report['matches']=[dict(recording_id='x',label='a',reference=r,prediction=p,
        basis=dict(label_match=True,onset_pass=True,offset_pass=True,eligible=True,
                   onset_delta_s='0',offset_delta_s='0',onset_limit_s='0.2',offset_limit_s='0.5'))]
    report['work']=dict(candidate_checks=1,eligible_edges=1,matching_steps=3)
    return document,report,dict(projected=metric)

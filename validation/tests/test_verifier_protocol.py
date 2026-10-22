import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from validation import compare, benchmark
from validation.qualify import run_qualification
from validation.rational_oracle import eligible

ROOT=Path(__file__).resolve().parents[2]


def fixture():
    return json.loads((ROOT/'validation/fixtures/comparison-baseline.json').read_bytes())


def fake_executable(folder,raw):
    path=folder/'fake'
    path.write_text(f'#!{sys.executable}\nimport sys\nsys.stdout.buffer.write({raw!r})\n');path.chmod(0o755)
    return path


def small_report(name):
    doc=dict(benchmark.performance_cases(2))[name]
    report=fixture()['product'];metric=dict(counts=dict(reference=2,prediction=2,tp=2,fp=0,fn=0),precision=1,recall=1,f1=1)
    report['config']=doc['config'];report['summary']=metric
    report['by_label']=[dict(label='a',metrics=copy.deepcopy(metric))]
    report['by_recording']=[dict(recording_id='x',metrics=copy.deepcopy(metric))]
    rec=doc['recordings'][0];report['matches']=[]
    for i,r in enumerate(rec['reference']):
        p=rec['prediction'][1-i if name=='chain' else i]
        report['matches'].append(dict(recording_id='x',label='a',reference=r,prediction=p,basis=eligible(r,p,doc['config'])))
    report['false_positives']=[];report['false_negatives']=[]
    report['work']=dict(candidate_checks=4,eligible_edges=2 if name=='sparse' else 4 if name=='dense' else 3,matching_steps=6 if name=='sparse' else 7 if name=='dense' else 11)
    return doc,report


class VerifierProtocolTests(unittest.TestCase):
    def test_raw_protocol_violations_are_failed_without_rewriting_bytes(self):
        good=json.dumps(fixture()['product'],separators=(',',':')).encode()+b'\n'
        corruptions=[good[:-1],good[:-1]+b'\r\n',good+b'\n',
                     good.replace(b'"status":"completed"',b'"status":"completed","status":"completed"'),
                     good.replace(b'"candidate_checks":0',b'"candidate_checks":0,"candidate_checks":0',1),
                     good.replace(b'"status":"completed"',b'"status":"completed","sta\\u0074us":"completed"'),
                     good.replace(b'"status":"completed"',b'"status":"\\ud800"'),
                     good.replace(b'"precision":0',b'"precision":NaN',1),
                     good.replace(b'"precision":0',b'"precision":1e999',1)]
        for raw in corruptions:
            self.assertNotEqual(raw,good)
            with self.subTest(raw=raw[:40]),tempfile.TemporaryDirectory() as tmp:
                folder=Path(tmp);exe=fake_executable(folder,raw)
                result=compare.run_file_product(exe,fixture()['input'],folder/'run')
                self.assertTrue(result['differences'])
                self.assertEqual((folder/'run/stdout').read_bytes(),raw)

    def test_nonfinite_output_still_gets_failed_case_and_final_ledger(self):
        f=fixture();f['product']['summary']['precision']=float('nan')
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);raw=(json.dumps(f['product'])+'\n').encode();exe=fake_executable(folder,raw)
            case=dict(name='nonfinite',category='decimal_nonboundary',document=f['input'])
            self.assertEqual(run_qualification(exe,folder/'proof',cases=[case]),1)
            report=json.loads((folder/'proof/report.json').read_bytes())
            self.assertEqual(report['unexplained'],['nonfinite'])
            self.assertTrue(json.loads((folder/'proof/nonfinite/comparison.json').read_bytes())['differences'])
            self.assertEqual((folder/'proof/nonfinite/base/stdout').read_bytes(),raw)

    def test_performance_rejects_truthful_illegal_or_foreign_pairs(self):
        for name in ['sparse','dense','chain']:
            doc,good=small_report(name)
            self.assertEqual(benchmark.validate_performance_report(doc,good,name),[])
            bad=copy.deepcopy(good);bad['matches'][0]['prediction'],bad['matches'][1]['prediction']=bad['matches'][1]['prediction'],bad['matches'][0]['prediction']
            for pair in bad['matches']:pair['basis']=eligible(pair['reference'],pair['prediction'],doc['config'])
            if name!='dense':self.assertTrue(benchmark.validate_performance_report(doc,bad,name))
            for component in ['foreign-id','changed-time','wrong-recording','wrong-label','missing-pair','reused-prediction']:
                bad=copy.deepcopy(good)
                if component=='foreign-id':bad['matches'][0]['reference']['id']='foreign'
                elif component=='changed-time':bad['matches'][0]['reference']['onset_s']='0.999999'
                elif component=='wrong-recording':bad['matches'][0]['recording_id']='foreign'
                elif component=='wrong-label':bad['matches'][0]['label']='foreign'
                elif component=='missing-pair':bad['matches'].pop()
                else:bad['matches'][1]['prediction']=copy.deepcopy(bad['matches'][0]['prediction'])
                for pair in bad['matches']:pair['basis']=eligible(pair['reference'],pair['prediction'],doc['config'])
                self.assertTrue(benchmark.validate_performance_report(doc,bad,name),component)

    def test_performance_accepts_equivalent_legal_dense_pairing(self):
        doc,report=small_report('dense')
        report['matches'][0]['prediction'],report['matches'][1]['prediction']=report['matches'][1]['prediction'],report['matches'][0]['prediction']
        self.assertEqual(benchmark.validate_performance_report(doc,report,'dense'),[])


if __name__=='__main__':unittest.main()

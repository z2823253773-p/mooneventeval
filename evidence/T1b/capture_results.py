"""Retain actual reference outputs on synthetic fixtures, not product outputs."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'validation'))
sys.path.insert(0,str(ROOT/'validation/tests'))
from sed_reference import evaluate_document
from test_reference import event,task

if __name__ == '__main__':
    documents = {
        'duplicate': task([event('r','a','10','12')],[event('p1','a','10','12'),event('p2','a','10.05','12.05')]),
        'A2': task([event('r1','a','10','11'),event('r2','a','10.3','11.3')],
                   [event('p1','a','10.15','11.15'),event('p2','a','9.85','10.85')]),
        'cross_label': task([event('r','A','1','2')],[event('p','B','1','2')],['A','B']),
        'empty': task([],[]),
    }
    record = {
        'python':platform.python_version(),
        'packages':{d.metadata['Name'].lower().replace('_','-'):d.version
                    for d in importlib.metadata.distributions()},
        'lock_sha256':hashlib.sha256((ROOT/'validation/reference.lock').read_bytes()).hexdigest(),
        'sed_eval_direct_url':json.loads(importlib.metadata.distribution('sed-eval').read_text('direct_url.json')),
        'verified_source_lock':json.loads((ROOT/'validation/reference-sources.json').read_text()),
        'cases': {name:dict(input=document, output=evaluate_document(document)) for name,document in documents.items()},
    }
    Path(sys.argv[1]).write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'cases':len(documents),'python':record['python'],'packages':len(record['packages']),
                      'output':sys.argv[1]}))

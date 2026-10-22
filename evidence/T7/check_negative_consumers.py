"""Keep real negative public-consumer runs; never change production sources."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import check_consumer
import package_candidate
from release_support import save

output=Path(sys.argv[1]).resolve()
output.mkdir(parents=True,exist_ok=False)
main=(ROOT/'tests/consumer/main/main.mbt').read_text()
wrong=check_consumer.check(ROOT,output/'wrong-count',main_text=main.replace('counts.tp == 1','counts.tp == 2'))
assert not wrong['passed'] and wrong['build']['exit_code']==0 and wrong['run']['exit_code']!=0
with tempfile.TemporaryDirectory(prefix='mee-no-public-event-') as directory:
    source=Path(directory)
    for name in package_candidate.expected_files(ROOT):
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
    model=source/'eventeval/model.mbt';original=model.read_bytes()
    changed=original.replace(b'pub fn event(',b'fn event(',1);assert changed!=original
    model.write_bytes(changed)
    missing=check_consumer.check(source,output/'private-factory')
    assert not missing['passed'] and missing['build']['exit_code']!=0 and missing['run'] is None
    error=(output/'private-factory/build/stderr').read_text()
    assert 'event' in error
    save(output/'private-factory/control.json',dict(original_sha256=hashlib.sha256(original).hexdigest(),private_factory_sha256=hashlib.sha256(changed).hexdigest(),mutation='only pub fn event -> fn event in temporary unpack-like source',source=str(source),production_source_unchanged=hashlib.sha256((ROOT/'eventeval/model.mbt').read_bytes()).hexdigest()==hashlib.sha256(original).hexdigest()))
save(output/'report.json',dict(passed=True,controls={'wrong_count':wrong['run']['exit_code'],'private_factory':missing['build']['exit_code']},scope='expected negative controls; compiler/runtime failures retained, not product mutation score'))
print(json.dumps(dict(passed=True,negative_controls=2)))

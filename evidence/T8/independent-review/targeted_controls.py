from pathlib import Path
import hashlib, json, os, subprocess, sys, tarfile
sys.dont_write_bytecode=True
AUDIT=Path(__file__).resolve().parent; ROOT=AUDIT/'checkout'
sys.path.insert(0,str(ROOT/'scripts'))
import verify
from release_support import save, sha
OUT=AUDIT/'targeted-controls';OUT.mkdir()
rows=[]
def process(name,argv,cwd):
    p=subprocess.run([str(x) for x in argv],cwd=cwd,capture_output=True)
    folder=OUT/name;folder.mkdir();(folder/'stdout').write_bytes(p.stdout);(folder/'stderr').write_bytes(p.stderr)
    receipt=dict(argv=[str(x) for x in argv],cwd=str(cwd),exit_code=p.returncode,stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))
    save(folder/'receipt.json',receipt);return p,receipt
# CLI entry must use actual cwd and fail before running any product step.
empty=OUT/'empty-cwd';empty.mkdir()
p,r=process('wrong-cwd',[sys.executable,ROOT/'scripts/verify.py','--mode','local','--evidence',OUT/'wrong-cwd-proof'],empty)
report=json.loads((OUT/'wrong-cwd-proof/report.json').read_bytes());assert p.returncode==1 and not report['passed'] and len(report['steps'])==0
rows.append(dict(case='wrong-cwd',expected_failure=True,receipt=r,error=report['error']))
# Real source modifications, only in review copy, must block before any checks.
readme=ROOT/'README.md';original=readme.read_bytes()
try:
    readme.write_bytes(original+b'\nreview negative control\n')
    p,r=process('dirty-source',[sys.executable,ROOT/'scripts/verify.py','--mode','local','--evidence',OUT/'dirty-source-proof'],ROOT)
    report=json.loads((OUT/'dirty-source-proof/report.json').read_bytes());assert p.returncode==1 and not report['passed'] and 'commit source' in report['error']['message']
    rows.append(dict(case='dirty-source',expected_failure=True,receipt=r,error=report['error']))
finally:readme.write_bytes(original)
# Inject a source write after a real successful interface command.
original_step=verify.run_step
def mutation(name,command,root,evidence,env):
    result=original_step(name,command,root,evidence,env)
    if name=='interfaces':readme.write_bytes(original+b'\nreview mid-run mutation\n')
    return result
try:
    verify.run_step=mutation
    report=verify.verify(ROOT,OUT/'mid-run-mutation-proof')
    assert not report['passed'] and 'generated interfaces changed' in report['error']['message'] and len(report['steps'])==3
    rows.append(dict(case='mid-run-source-mutation',expected_failure=True,completed_real_steps=3,error=report['error']))
finally:
    verify.run_step=original_step;readme.write_bytes(original)
# Installed-file integrity: use real pinned archives, own mirror links to installed files,
# and one corrupt regular file in the mirror. No shared file is overwritten.
fixture=OUT/'installed-integrity-fixture';(fixture/'docs').mkdir(parents=True)
(fixture/'docs/toolchain.lock.json').write_bytes((ROOT/'docs/toolchain.lock.json').read_bytes())
(fixture/'.tools').mkdir();(fixture/'.tools/downloads').symlink_to((ROOT/'.tools/downloads').resolve(),target_is_directory=True)
lock=json.loads((ROOT/'docs/toolchain.lock.json').read_bytes());realhome=ROOT/'.tools/moonbit'/lock['version'];home=fixture/'.tools/moonbit'/lock['version'];home.mkdir(parents=True)
for path in realhome.rglob('*'):
    dest=home/path.relative_to(realhome)
    if path.is_dir():dest.mkdir(exist_ok=True)
    else:dest.symlink_to(path.resolve())
victim=home/'bin/moonc';victim.unlink();victim.write_bytes(b'corrupt isolated installed compiler')
try:verify.verify_toolchain(fixture)
except ValueError as e:
    assert 'installed toolchain SHA-256 mismatch' in str(e)
    rows.append(dict(case='installed-file-corruption',expected_failure=True,error=str(e),real_compiler_sha256=sha(realhome/'bin/moonc')))
else:raise AssertionError('corrupt installed compiler was accepted')
# Nonempty, skipped, failed and missing artifacts must all reject.
protocol=OUT/'protocol';protocol.mkdir();(protocol/'stdout').write_bytes(b'')
for name,text,kind,minimum in [('empty-python','Ran 0 tests in 0.01s\n\nOK\n','python',20),('skipped-python','Ran 22 tests in 0.01s\n\nOK (skipped=1)\n','python',20),('failed-moon','Total tests: 58, passed: 57, failed: 1\n','moon',58)]:
    (protocol/'stderr').write_text(text)
    try:verify.check_test_protocol(protocol,kind,minimum)
    except ValueError as e:rows.append(dict(case=name,expected_failure=True,error=str(e)))
    else:raise AssertionError(name)
assert not subprocess.check_output(['git','diff','HEAD','--','README.md'],cwd=ROOT)
save(OUT/'report.json',dict(passed=True,cases=rows,scope='fresh bounded actual verifier negatives; runtime source untouched; shared tools read only'))
print(json.dumps(dict(passed=True,controls=len(rows))))

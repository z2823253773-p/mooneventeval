import hashlib, importlib.util, json, pathlib, sys, unittest
sys.dont_write_bytecode=True
path=pathlib.Path('/Users/henryz/Desktop/比赛/mooneventeval-t0/tests/test_ci_history.py')
spec=importlib.util.spec_from_file_location('transport_tests',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
def run(name,fn):
 t=m.OriginalHistory('test_exact_restore_preserves_checkout_and_is_repeatable');t.setUp()
 try: rows.append(dict(name=name,**fn(t)))
 finally:t.doCleanups()
def false_existing(t):
 target=t.root/t.relative;target.parent.mkdir(parents=True);bad=b'x'*len(t.payload);target.write_bytes(bad)
 t.meta['omitted_files'][t.relative]['sha256']=hashlib.sha256(bad).hexdigest();t.save()
 result=t.restore();actual=t.git(t.root,'show',t.meta['original_tip']+':'+t.relative)
 return dict(reported_passed=result['passed'],existing_matches_original=target.read_bytes()==actual,expected_original_sha256=hashlib.sha256(actual).hexdigest(),accepted_existing_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
def parent_symlink(t):
 outside=t.root.parent/'outside';outside.mkdir();(t.root/'evidence').symlink_to(outside,target_is_directory=True)
 try:t.restore();outcome='ACCEPTED'
 except Exception as e:outcome=type(e).__name__+': '+str(e)
 return dict(outcome=outcome,external_written=(outside/'review/stdout').exists())
def leaf_symlink(t):
 target=t.root/t.relative;target.parent.mkdir(parents=True);other=t.root/'other';other.write_bytes(t.payload);target.symlink_to(other)
 try:t.restore();outcome='ACCEPTED'
 except Exception as e:outcome=type(e).__name__+': '+str(e)
 return dict(outcome=outcome,other_unchanged=other.read_bytes()==t.payload)
def wrong_tip(t):
 t.meta['original_tip']='0'*40;t.save()
 try:t.restore();outcome='ACCEPTED'
 except Exception as e:outcome=type(e).__name__+': '+str(e)
 return dict(outcome=outcome,proof_written=(t.root/t.relative).exists())
for name,fn in [('self_consistent_wrong_existing',false_existing),('external_parent_symlink',parent_symlink),('leaf_symlink',leaf_symlink),('wrong_tip',wrong_tip)]:run(name,fn)
print(json.dumps(rows,indent=2))

"""The transport must restore the exact original proof or fail closed."""
import hashlib,importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/restore_ci_history.py'
class OriginalHistory(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  base=Path(self.temp.name);self.source=base/'source';self.root=base/'checkout'
  for p in [self.source,self.root]:
   p.mkdir();self.git(p,'init','-b','main');(p/'README').write_text('fixture\n');self.git(p,'add','.');self.commit(p,'fixture')
  self.relative='evidence/review/stdout';self.payload=b'original review\x00\xff\n'
  path=self.source/self.relative;path.parent.mkdir(parents=True);path.write_bytes(self.payload)
  self.git(self.source,'add','.');self.commit(self.source,'original proof')
  tip=self.git(self.source,'rev-parse','HEAD').decode().strip()
  (self.root/'.ci').mkdir();self.bundle=self.root/'.ci/original-history.bundle'
  self.git(self.source,'bundle','create',str(self.bundle),'main')
  self.meta=dict(original_tip=tip,original_ref='refs/heads/main',bundle_sha256=hashlib.sha256(self.bundle.read_bytes()).hexdigest(),omitted_files={self.relative:dict(bytes=len(self.payload),sha256=hashlib.sha256(self.payload).hexdigest())})
  self.save()
  self.module=None
  if SCRIPT.exists():
   spec=importlib.util.spec_from_file_location('restore_ci_history_test',SCRIPT);self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
 def git(self,root,*args):return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.PIPE)
 def commit(self,root,message):self.git(root,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m',message)
 def save(self):(self.root/'.ci/history.json').write_text(json.dumps(self.meta))
 def restore(self):
  self.assertIsNotNone(self.module,'history transport restore missing')
  return self.module.restore(self.root)
 def test_exact_restore_preserves_checkout_and_is_repeatable(self):
  before=self.git(self.root,'rev-parse','HEAD');r=self.restore()
  self.assertTrue(r['passed']);self.assertEqual((self.root/self.relative).read_bytes(),self.payload)
  self.assertEqual(self.git(self.root,'show',self.meta['original_tip']+':'+self.relative),self.payload)
  self.assertTrue(self.restore()['passed']);self.assertEqual(self.git(self.root,'rev-parse','HEAD'),before)
 def test_corrupt_bundle_never_imports_or_restores(self):
  self.bundle.write_bytes(self.bundle.read_bytes()+b'changed')
  with self.assertRaisesRegex(ValueError,'bundle'):
   self.restore()
  self.assertFalse((self.root/self.relative).exists())
 def test_existing_different_proof_is_preserved(self):
  target=self.root/self.relative;target.parent.mkdir(parents=True);target.write_bytes(b'keep this')
  with self.assertRaisesRegex(ValueError,'existing'):
   self.restore()
  self.assertEqual(target.read_bytes(),b'keep this')
 def test_wrong_expected_proof_never_becomes_valid_evidence(self):
  self.meta['omitted_files'][self.relative]['sha256']='0'*64;self.save()
  with self.assertRaisesRegex(ValueError,'proof'):
   self.restore()
  self.assertFalse((self.root/self.relative).exists())
 def test_path_escape_is_rejected(self):
  row=self.meta['omitted_files'].pop(self.relative);self.meta['omitted_files']['../escape']=row;self.save()
  with self.assertRaisesRegex(ValueError,'path'):
   self.restore()
 def test_existing_metadata_matched_bytes_must_equal_original_blob(self):
  wrong=b'X'*len(self.payload);target=self.root/self.relative
  target.parent.mkdir(parents=True);target.write_bytes(wrong)
  self.meta['omitted_files'][self.relative]['sha256']=hashlib.sha256(wrong).hexdigest();self.save()
  with self.assertRaisesRegex(ValueError,'original'):
   self.restore()
  self.assertEqual(target.read_bytes(),wrong)
if __name__=='__main__':unittest.main()

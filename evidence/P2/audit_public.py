"""Bounded read-only disclosure scan of the export and bundled original Git history.

This detects selected credential formats and known participant contact fields;
it is not a universal secret detector or a guarantee about arbitrary content.
Only counts, object hashes and paths are reported, never matched values.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import zipfile


PATTERNS = {
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----',
    'github_token': rb'\bgh[pousr]_[A-Za-z0-9]{30,255}\b|\bgithub_pat_[A-Za-z0-9_]{50,255}\b',
    'aws_access_id': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'openai_or_anthropic_token': rb'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,255}\b',
    'credential_url': rb'https?://[^\s/"<>:@]{1,100}:[^\s/"<>@]{8,100}@',
}


def audit(root):
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root)

    head = git('rev-parse', 'HEAD').decode().strip()
    roots = [head]
    bundles = []
    for lock_path, bundle_path, tip_key in [
        ('.ci/history.json', '.ci/original-history.bundle', 'original_tip'),
        ('evidence/R1-provenance/lock.json', 'evidence/R1-provenance/author-code.bundle', 'tip'),
    ]:
        lock = json.loads((root/lock_path).read_bytes())
        want = lock.get('bundle_sha256', lock.get('sha256'))
        actual = hashlib.sha256((root/bundle_path).read_bytes()).hexdigest()
        assert actual == want, bundle_path
        roots.append(lock[tip_key])
        bundles.append(dict(path=bundle_path, sha256=actual, original_tip=lock[tip_key]))
    paths = {}
    for line in git('rev-list', '--objects', *roots).splitlines():
        oid, _, path = line.partition(b' ')
        paths.setdefault(oid.decode(), path.decode(errors='replace'))
    rows = subprocess.check_output(['git', 'cat-file', '--batch-check'], cwd=root,
        input=('\n'.join(paths)+'\n').encode()).splitlines()
    blobs = [(row.split()[0].decode(), int(row.split()[2])) for row in rows if row.split()[1] == b'blob']
    patterns = {key: re.compile(value) for key, value in PATTERNS.items()}
    # Contact inputs are supplied at runtime and never written into this script.
    contacts = json.loads(Path(args.contacts).read_bytes())
    info = Counter(); findings = []; zip_members = 0; tar_members = 0; archive_types = Counter(); clinical_contexts = set()

    def inspect(data, oid, path):
        for kind, pattern in patterns.items():
            matches = list(pattern.finditer(data))
            if matches:
                findings.append(dict(kind=kind, object=oid, path=path, count=len(matches)))
        for key, value in contacts.items():
            if value.encode() in data:
                findings.append(dict(kind='participant_contact_'+key, object=oid, path=path))
        if b'/Users/henryz' in data or b'/home/runner' in data:
            info['objects_with_local_or_runner_build_paths'] += 1
        if b'clinical' in data.lower() or '临床'.encode() in data:
            info['objects_with_clinical_word'] += 1
            for needle in [b'clinical', '临床'.encode()]:
                at=data.lower().find(needle)
                if at >= 0:
                    clinical_contexts.add(data[max(0,at-90):at+180].decode(errors='replace'))

    process = subprocess.Popen(['git','cat-file','--batch'], cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for oid, size in blobs:
            process.stdin.write((oid+'\n').encode()); process.stdin.flush()
            header = process.stdout.readline().split()
            assert header[0].decode() == oid and int(header[2]) == size
            data = process.stdout.read(size); assert len(data) == size
            assert process.stdout.read(1) == b'\n'
            path = paths[oid]
            inspect(data, oid, path)
            if data.startswith(b'PK\x03\x04'):
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for member in archive.infolist():
                        if member.is_dir(): continue
                        assert member.file_size <= 128*1024**2
                        inspect(archive.read(member), oid, path+'!'+member.filename)
                        zip_members += 1
            if data.startswith(b'\x1f\x8b') or path.endswith('.tar'):
                try:
                    with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as archive:
                        total=0
                        for member in archive:
                            if not member.isfile():continue
                            total+=member.size
                            assert member.size <= 128*1024**2 and total <= 256*1024**2
                            inspect(archive.extractfile(member).read(),oid,path+'!'+member.name)
                            tar_members+=1
                except tarfile.ReadError:
                    info['invalid_tar_or_gzip_fixture'] += 1
            for suffix in ['.bundle','.zip','.gz','.tar','.7z','.pdf','.docx']:
                if path.endswith(suffix):archive_types[suffix] += 1
    finally:
        process.stdin.close();process.stdout.close();process.wait()
    assert process.returncode == 0
    return dict(scope='selected credential formats and participant contacts in all reachable main/bundled-author Git blobs plus ZIP members',
        head=head, original_roots=roots[1:], bundles=bundles, blobs=len(blobs), bytes=sum(size for _,size in blobs),
        zip_members=zip_members, tar_members=tar_members, archive_types=dict(archive_types), informational_counts=dict(info), findings=findings,
        clinical_word_contexts=sorted(clinical_contexts),
        limitations=['No universal secret detection claim','Build paths and Git author identity are retained in real development evidence','Private hosted artifacts are checked separately from Git objects'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--contacts',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=audit(args.root.resolve())
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['head','blobs','bytes','zip_members','archive_types','informational_counts']}))
    print(json.dumps(dict(findings=len(report['findings']),report=str(args.output))))

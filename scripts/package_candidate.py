"""Audit a real moon package, unpack it and verify local consumption and CLI."""
import argparse
import json
from pathlib import Path,PurePosixPath
import re
import shutil
import stat
import tempfile
import zipfile

from release_support import ROOT,WRAPPER,fresh,record,save,sha
import check_consumer

FIXED={'moon.mod','README.md','EXAMPLES.md','VALIDATION.md','LICENSE','THIRD_PARTY_NOTICES.md',
       'LICENSES/moonbit-core-LICENSE','LICENSES/moonbit-core-NOTICE',
       'docs/API.md','docs/toolchain.lock.json','scripts/install_toolchain.py','scripts/with-toolchain.sh',
       'examples/duplicate.json','examples/greedy-trap.json','examples/boundary.json'}


def expected_files(source):
    source=Path(source);names=set(FIXED)
    for folder in ['eventeval','cli','cmd/mooneventeval']:
        for path in (source/folder).iterdir():
            if path.is_file() and (path.name=='moon.pkg' or path.suffix in {'.mbt','.mbti','.c'}) and not path.name.endswith(('_test.mbt','_wbtest.mbt')):
                names.add(str(path.relative_to(source)))
    return names


def validate_members(actual,expected):
    if set(actual)!=set(expected):raise ValueError(f'archive policy mismatch: missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}')


def archive_members(path):
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)):raise ValueError('duplicate archive members')
        for info in archive.infolist():
            name=info.filename;p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or '\\' in name or not p.parts or name!=str(p):raise ValueError('unsafe archive path: '+name)
            mode=info.external_attr >> 16
            if stat.S_ISLNK(mode) or info.is_dir():raise ValueError('unexpected archive file type: '+name)
        if archive.testzip() is not None:raise ValueError('archive CRC failed')
    return names


def check_links(source,names):
    # Distributed markdown links must resolve within the actual archive.
    for name in names:
        if not name.endswith('.md'):continue
        text=(source/name).read_text()
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if target.startswith(('https://','http://','#')):continue
            target=target.split('#')[0]
            resolved=(source/name).parent.joinpath(target).resolve()
            try:relative=str(resolved.relative_to(source.resolve()))
            except ValueError:raise ValueError('link escapes package: '+name+' -> '+target)
            if relative not in names:raise ValueError('link absent from package: '+name+' -> '+target)


def package(source,output):
    source=Path(source).resolve();output=fresh(output);expected=expected_files(source)
    for name in expected:
        if not (source/name).is_file():raise ValueError('missing package file: '+name)
    check_links(source,expected)
    listing=record([WRAPPER,'moon','package','--list','--frozen'],source,output/'list')
    if listing['exit_code']!=0:raise RuntimeError('package list failed')
    build=record([WRAPPER,'moon','package','--frozen'],source,output/'package')
    if build['exit_code']!=0:raise RuntimeError('package failed')
    # Module name/version are fixed local development identity, never registry claims.
    archive=source/'_build/publish/local-mooneventeval-0.1.0.zip'
    saved=output/archive.name;shutil.copyfile(archive,saved)
    names=archive_members(saved);validate_members(names,expected)
    lines=(output/'list/stderr').read_text().splitlines()
    if lines.count('Check passed')!=1 or not lines[-1].startswith('Package to '):raise ValueError('unknown moon package listing framing')
    listing_names=set(lines[lines.index('Check passed')+1:-1])
    if (output/'list/stdout').read_bytes():raise ValueError('unexpected moon package stdout')
    if listing_names!=expected:raise ValueError('moon list and expected file set differ: '+str(sorted(listing_names^expected)))
    member_hashes={}
    with tempfile.TemporaryDirectory(prefix='mee-unpacked-') as directory:
        unpacked=Path(directory)
        with zipfile.ZipFile(saved) as z:
            for name in names:
                data=z.read(name)
                if data!=(source/name).read_bytes():raise ValueError('archive/source byte mismatch: '+name)
                member_hashes[name]=sha(source/name)
                path=unpacked/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
                mode=z.getinfo(name).external_attr >> 16
                if mode:path.chmod(mode & 0o777)
        # Reuse only the installed compiler/core; source imports stay in the unpack.
        if not (unpacked/'scripts/with-toolchain.sh').stat().st_mode & 0o111:raise ValueError('archive wrapper lost executable permission')
        (unpacked/'.tools').symlink_to(ROOT/'.tools',target_is_directory=True)
        check_links(unpacked,set(names))
        consumer=check_consumer.check(unpacked,output/'unpacked-consumer')
        cli_build=record([unpacked/'scripts/with-toolchain.sh','moon','build','cmd/mooneventeval','--target','native','--release','--deny-warn'],unpacked,output/'unpacked-cli-build')
        if cli_build['exit_code']!=0:raise RuntimeError('unpacked CLI build failed')
        import check_examples
        examples=check_examples.check(unpacked,unpacked/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe',output/'unpacked-examples')
        report=dict(passed=consumer['passed'] and examples['passed'],local_candidate_only=True,published=False,
                    archive=saved.name,archive_sha256=sha(saved),members=sorted(names),member_sha256=member_hashes,
                    list=listing,package=build,consumer=consumer,cli_build=cli_build,examples=examples,
                    source=str(source),toolchain_reused_from=str(ROOT/'.tools'),installer_download_performed=False,scope='real local moon archive; fresh unpack, external API consumer and native CLI examples; no registry or remote')
        save(output/'report.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=ROOT);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=package(args.source,args.output);print(json.dumps(dict(passed=report['passed'],members=len(report['members']),published=False)))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())

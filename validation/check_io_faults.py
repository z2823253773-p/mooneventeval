"""Compile-time syscall injection into temporary native source copies, no runtime switches."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def prefix(mode, stats):
    return r'''
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <signal.h>
#include <sys/stat.h>
#define FAULT_MODE MODE_VALUE
static int oc,sc,rc,cc,wc,live;
static void record_stats(void) {
  FILE *f=fopen(STATS_PATH,"wb");
  if(f){fprintf(f,"{\"open_calls\":%d,\"stat_calls\":%d,\"read_calls\":%d,\"close_calls\":%d,\"stdout_write_calls\":%d,\"live_input_fds\":%d}\n",oc,sc,rc,cc,wc,live);fclose(f);}
}
__attribute__((constructor)) static void init_stats(void){atexit(record_stats);}
static int fault_open(const char *p,int flags){oc++;if(FAULT_MODE==1&&oc==1){errno=EINTR;return -1;}int fd=open(p,flags);if(fd>=0)live++;return fd;}
static int fault_stat(int fd,struct stat *s){sc++;if(FAULT_MODE==1&&sc==1){errno=EINTR;return -1;}return fstat(fd,s);}
static ssize_t fault_read(int fd,void *b,size_t n){rc++;if(FAULT_MODE==1&&rc==1){errno=EINTR;return -1;}if((FAULT_MODE==2&&rc==1)||(FAULT_MODE==3&&rc==2)){errno=EIO;return -1;}if((FAULT_MODE==1||FAULT_MODE==3)&&n>17)n=17;return read(fd,b,n);}
static int fault_close(int fd){cc++;int r=close(fd);if(r==0)live--;if(FAULT_MODE==6||FAULT_MODE==7){errno=FAULT_MODE==7?EINTR:EIO;return -1;}return r;}
static ssize_t fault_write(int fd,const void *b,size_t n){if(fd==1){wc++;if(FAULT_MODE==1&&wc==1){errno=EINTR;return -1;}if(FAULT_MODE==4)return 0;if(FAULT_MODE==5&&wc==2){errno=EIO;return -1;}if((FAULT_MODE==1||FAULT_MODE==5)&&n>7)n=7;}return write(fd,b,n);}
typedef void (*handler)(int);
static handler fault_signal(int s,handler h){if(FAULT_MODE==8)return SIG_ERR;return signal(s,h);}
#define open fault_open
#define fstat fault_stat
#define read fault_read
#define close fault_close
#define write fault_write
#define signal fault_signal
'''.replace('MODE_VALUE',str(mode)).replace('STATS_PATH',json.dumps(str(stats)))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--product',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True);exe=args.product.resolve()
    original=ROOT/'cmd/mooneventeval/io_stub.c';data=original.read_bytes();source_hash=hashlib.sha256(data).hexdigest()
    fixture=output/'input.json';fixture.write_bytes((ROOT/'evidence/T3/parity-final/unicode-order-and-escaping/input.json').read_bytes())
    baseline=subprocess.run([str(exe),'evaluate',str(fixture),'--format','json'],capture_output=True,timeout=10)
    assert baseline.returncode==0 and not baseline.stderr
    (output/'production.stdout').write_bytes(baseline.stdout)
    rows=[]
    modes=['control','eintr-and-short-read-write','read-error','partial-read-error','zero-write','partial-write-error','close-error','close-eintr-no-retry','signal-init-error']
    with tempfile.TemporaryDirectory(prefix='mee-io-faults-') as tmp:
        work=Path(tmp)
        for name in ['moon.mod','scripts/with-toolchain.sh','docs/toolchain.lock.json']:
            target=work/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
        for name in ['eventeval','cli','cmd/mooneventeval']:shutil.copytree(ROOT/name,work/name)
        (work/'.tools').symlink_to(ROOT/'.tools',target_is_directory=True)
        for mode,name in enumerate(modes):
            folder=output/name;folder.mkdir();stats=folder/'syscalls.json'
            injected=prefix(mode,stats).encode()+data
            (work/'cmd/mooneventeval/io_stub.c').write_bytes(injected);(folder/'instrumented-io_stub.c').write_bytes(injected)
            build_command=[str(work/'scripts/with-toolchain.sh'),'moon','build','cmd/mooneventeval','--target','native','--release','--deny-warn']
            build=subprocess.run(build_command,cwd=work,capture_output=True,timeout=120)
            (folder/'build.stdout').write_bytes(build.stdout);(folder/'build.stderr').write_bytes(build.stderr)
            assert build.returncode==0,(name,build.stderr)
            binary=work/'_build/native/release/build/cmd/mooneventeval/mooneventeval.exe'
            command=[str(binary),'evaluate',str(fixture),'--format','json']
            result=subprocess.run(command,cwd=work,capture_output=True,timeout=10)
            (folder/'stdout').write_bytes(result.stdout);(folder/'stderr').write_bytes(result.stderr)
            observed=json.loads(stats.read_bytes());assert observed['live_input_fds']==0,(name,observed)
            expected=0 if mode in [0,1] else 4 if mode==8 else 2
            assert result.returncode==expected,(name,result.returncode,result.stderr)
            if mode in [0,1]:assert result.stdout==baseline.stdout and not result.stderr
            elif mode in [4,5,8]:
                assert (b'INTERNAL_ERROR' if mode==8 else b'FILE_ERROR') in result.stderr
                if mode==5:assert result.stdout==baseline.stdout[:7]
                else:assert result.stdout==b''
            else:
                parsed=json.loads(result.stdout);assert not result.stderr
                assert list(parsed)==['schema_version','status','error'] and parsed['status']=='failed' and parsed['error']['code']=='FILE_ERROR'
            if mode==1:assert observed['open_calls']==2 and observed['stat_calls']==2 and observed['read_calls']>2 and observed['stdout_write_calls']>2
            if mode!=8:assert observed['close_calls']==1
            row=dict(name=name,exit_code=result.returncode,expected_exit=expected,syscalls=observed,
                     instrumented_binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                     instrumented_source_sha256=hashlib.sha256(injected).hexdigest(),
                     stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),passed=True)
            (folder/'receipt.json').write_text(json.dumps(dict(command=command,build_command=build_command,build_exit_code=build.returncode,**row),indent=2)+'\n');rows.append(row)
    assert hashlib.sha256(original.read_bytes()).hexdigest()==source_hash
    report=dict(passed=True,production_source_sha256=source_hash,production_binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),cases=rows,
                scope='temporary compile-time syscall wrappers around actual native C and unchanged Moon code; instrumented binaries are not the production binary; no runtime feature flags')
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))


if __name__=='__main__':main()

"""Local release verification helpers; no installation or registry operations."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT/'scripts/with-toolchain.sh'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def fresh(path):
    path=Path(path).resolve()
    path.mkdir(parents=True,exist_ok=True)
    if any(path.iterdir()):raise ValueError('use a fresh output directory: '+str(path))
    return path


def record(command,cwd,folder,timeout=120):
    folder=Path(folder);folder.mkdir(parents=True)
    timed_out=False
    try:
        result=subprocess.run([str(x) for x in command],cwd=cwd,capture_output=True,timeout=timeout)
        stdout,stderr,code=result.stdout,result.stderr,result.returncode
    except subprocess.TimeoutExpired as error:
        stdout,stderr,code=error.stdout or b'',error.stderr or b'',None
        timed_out=True
    (folder/'stdout').write_bytes(stdout);(folder/'stderr').write_bytes(stderr)
    receipt=dict(command=[str(x) for x in command],cwd=str(cwd),exit_code=code,timed_out=timed_out,
                 stdout_sha256=sha(folder/'stdout'),stderr_sha256=sha(folder/'stderr'))
    save(folder/'receipt.json',receipt)
    return receipt


def machine_report(raw):
    if not raw.endswith(b'\n') or raw.endswith(b'\n\n') or b'\r' in raw:
        raise ValueError('machine report requires one terminal LF and no raw CR')
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate JSON key')
            out[key]=value
        return out
    def invalid(value):raise ValueError('nonfinite JSON number: '+value)
    import math
    def finite(value):
        number=float(value)
        if not math.isfinite(number):invalid(value)
        return number
    parsed=json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_constant=invalid,parse_float=finite)
    pending=[parsed]
    while pending:
        value=pending.pop()
        if isinstance(value,str):value.encode('utf-8')
        elif isinstance(value,dict):pending.extend(value);pending.extend(value.values())
        elif isinstance(value,list):pending.extend(value)
    return parsed

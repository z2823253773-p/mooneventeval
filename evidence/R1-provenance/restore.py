"""Import the locked original author objects for offline frozen R1 verification."""
import hashlib
import json
from pathlib import Path
import subprocess


def restore(root):
    root = root.resolve()
    folder = root / 'evidence/R1-provenance'
    lock = json.loads((folder / 'lock.json').read_bytes())
    bundle = folder / 'author-code.bundle'
    assert not bundle.is_symlink() and bundle.is_file(), 'expected regular bundle'
    assert bundle.stat().st_size == lock['bytes'], 'bundle size mismatch'
    with bundle.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == lock['sha256'], 'bundle hash mismatch'

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.STDOUT).decode().strip()

    head = git('rev-parse', 'HEAD')
    git('bundle', 'verify', str(bundle))
    target = 'refs/ci-evidence/r1-author'
    git('fetch', '--no-tags', '--no-write-fetch-head', str(bundle), lock['ref'] + ':' + target)
    assert git('rev-parse', target) == lock['tip'], 'original author tip mismatch'
    assert git('cat-file', '-t', lock['tip']) == 'commit'
    assert git('rev-parse', 'HEAD') == head, 'checkout changed'
    return dict(passed=True, original_author_code_sha=lock['tip'], bundle_sha256=lock['sha256'], checkout_unchanged=True)


if __name__ == '__main__':
    print(json.dumps(restore(Path(__file__).resolve().parents[2])))

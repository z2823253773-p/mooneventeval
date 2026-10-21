"""Compare real trial and hash-lock rebuild outputs without rewriting metadata."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    first = json.loads((ROOT/'trial-results.json').read_text())
    second = json.loads((ROOT/'rebuilt-results.json').read_text())
    assert first['packages'] == second['packages']
    assert first['cases'] == second['cases']
    assert first['verified_source_lock'] == second['verified_source_lock']
    assert second['sed_eval_direct_url']['url'] == second['verified_source_lock']['archive_url']
    # uv may omit archive_info hashes. Provenance is established by require-hashes
    # at sync plus runtime verification of every source file, not this metadata.
    print(json.dumps({'packages_equal':len(second['packages']),'cases_equal':len(second['cases']),
                      'sources_verified':len(second['verified_source_lock']['source_sha256']),
                      'direct_url_archive_info':second['sed_eval_direct_url']['archive_info']}))

# Historical structural checker, not a feasibility/product acceptance gate.
"""Check documentation only; does not execute MoonBit or sed_eval."""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import json
import re

root = Path(__file__).resolve().parents[2]
prd = root / 'docs/superpowers/specs/2026-10-20-mooneventeval-prd-design.md'
files = sorted(root.glob('docs/**/*.md'))
broken = []
json_blocks = 0
for path in files:
    content = path.read_text()
    assert len(re.findall(r'^```', content, re.M)) % 2 == 0, path
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            if not (path.parent / target.split('#')[0]).exists():
                broken.append((str(path.relative_to(root)), target))
    if path == prd:
        for block in re.findall(r'```json\n(.*?)\n```', content, re.S):
            data = json.loads(block)
            assert data['schema_version'] == 1
            assert data['config'] == {'collar_s': '0.2', 'offset_ratio': '0.5'}
            json_blocks += 1
assert not broken, broken
text = prd.read_text()
assert [int(n) for n in re.findall(r'^## (\d+)\.', text, re.M)] == list(range(1, 14))
assert not re.search(r'\b(?:TODO|TBD|FIXME)\b', text)
assert all(f'| A{i} ' in text for i in range(1, 13))
manifest = json.loads((root / 'docs/research/2026-10-20-source-check.json').read_text())
assert len(manifest['sources']) == 6
assert all(x['read_success'] for x in manifest['files'])
external_index_available = (root / 'docs/research' / manifest['inherited_index']['source']).exists()

# Exact rational arithmetic review of the specified examples; no product code.
def edge(r, p):
    r, p = tuple(map(Fraction, r)), tuple(map(Fraction, p))
    return abs(r[0]-p[0]) <= Fraction('0.2') and abs(r[1]-p[1]) <= max(Fraction('0.2'), (r[1]-r[0])/2)

def all_matchings(refs, preds):
    out = []
    def visit(i, used, pairs):
        if i == len(refs):
            out.append(tuple(pairs))
            return
        visit(i+1, used, pairs)
        for j, p in enumerate(preds):
            if j not in used and edge(refs[i], p):
                visit(i+1, used | {j}, pairs+[(i,j)])
    visit(0, set(), [])
    return out

dup = all_matchings([('10','12')], [('10','12'),('10.05','12.05')])
assert max(map(len, dup)) == 1
trap = all_matchings([('10','11'),('10.3','11.3')], [('10.15','11.15'),('9.85','10.85')])
assert [m for m in trap if len(m) == 2] == [((0,1),(1,0))]
assert edge(('10','12'), ('10.2','12.2'))
assert not edge(('10','12'), ('10.200001','12.2'))
assert edge(('10','12'), ('10','13'))
assert not edge(('10','12'), ('10','13.000001'))
assert 2_592_000_000_000 * 1_000_000 < 2**63
assert max(r*(2000-r) for r in range(2001)) == 1_000_000
print(json.dumps({
    'scope': 'documentation consistency and rational arithmetic only; not product acceptance',
    'markdown_files_checked': len(files),
    'broken_local_links': broken,
    'new_prd_complete_json_examples': json_blocks,
    'new_prd_sections': 13,
    'acceptance_rows_present': 12,
    'source_records': len(manifest['sources']),
    'external_index_snapshot_available': external_index_available,
    'source_files_with_blob_metadata': len(manifest['files']),
    'rational_examples': 'A1/A2/A3/A4 expectations verified',
    'numeric_bounds': 'Int64 product and 2000-event candidate bound verified',
    'product_tests_run': False,
    'sed_eval_run': False
}, ensure_ascii=False, indent=2))

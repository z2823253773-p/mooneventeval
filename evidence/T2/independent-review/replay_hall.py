"""Author replay of the reviewer's Hall formula, not a second independent review."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[3]
fixtures = json.loads((root / 'evidence/T2/graph-oracle-cases.json').read_text())['cases']
actual = json.loads((root / 'evidence/T2/native-committed/graph-oracle-actual.json').read_text())
by_id = {row['case']: row for row in actual}
assert len(by_id) == len(actual) == len(fixtures) == 753
for case in fixtures:
    graph = case['adjacency']
    n = len(graph)
    hall = min(n - mask.bit_count() + len({p for r, row in enumerate(graph)
                if mask & (1 << r) for p in row}) for mask in range(1 << n))
    pairs = by_id[case['id']]['pairs']
    assert hall == case['expected'] == len(pairs), case['id']
    assert len({r for r, _ in pairs}) == len({p for _, p in pairs}) == len(pairs)
    assert pairs == sorted(pairs)
    assert all(0 <= r < n and 0 <= p < case['prediction_count'] and p in graph[r]
               for r, p in pairs)
print(json.dumps({'scope': __doc__, 'graphs_checked': len(fixtures), 'all_passed': True}))

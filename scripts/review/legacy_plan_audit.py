# Historical structural checker, not a feasibility/product acceptance gate.
"""Document checks only. Does not import or execute planned product code."""
from pathlib import Path
import ast
import json
import re

root = Path(__file__).resolve().parents[2]
plan_path = root / 'docs/superpowers/plans/2026-10-20-mooneventeval-implementation.md'
spec_path = root / 'docs/superpowers/specs/2026-10-20-mooneventeval-prd-design.md'
plan = plan_path.read_text()
spec = spec_path.read_text()
review = (root / 'docs/reviews/2026-10-20-plan-review.md').read_text()
files = sorted(root.glob('docs/**/*.md'))
broken = []
python_blocks = 0
for path in files:
    content = path.read_text()
    assert len(re.findall(r'^```', content, re.M)) % 2 == 0, path
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            if not (path.parent / target.split('#')[0]).exists():
                broken.append((str(path.relative_to(root)), target))
    for block in re.findall(r'```python\n(.*?)\n```', content, re.S):
        ast.parse(block)
        python_blocks += 1
assert not broken, broken
assert re.findall(r'^## Task (\d+):', plan, re.M) == [str(i) for i in range(1, 9)]
tasks = re.split(r'^## Task \d+:', plan, flags=re.M)[1:]
step_counts = []
for task in tasks:
    assert '**Files:**' in task and '**Interfaces:**' in task
    assert 'Consumes' in task and 'Produces' in task
    count = len(re.findall(r'^- \[ \] \*\*\d+\.', task, re.M))
    assert count >= 5, count
    assert '```' in task, 'task has no concrete test assertion block'
    step_counts.append(count)
assert not re.search(r'^- \[[xX]\]', plan, re.M)
assert not re.search(r'\b(?:TODO|TBD|FIXME)\b', plan)
for number in range(1, 6):
    assert f'R{number}' in plan
for number in range(1, 13):
    assert re.search(rf'^\| A{number} ', review, re.M)
for value in ['2592000', '2000', '20000000', '1000000', '1000', '256', '8 MiB', '16 MiB', 'collar-max-cardinality/v1']:
    assert value in plan and value in spec, value
for field in ['schema_version', 'implementation_version', 'summary', 'by_label', 'by_recording', 'matches', 'false_positives', 'false_negatives', 'candidate_checks', 'eligible_edges', 'matching_steps']:
    assert field in plan, field
assert '用户已批准' in spec
assert '确认进行实施计划' in (root / 'docs/PROJECT_STATE.md').read_text()
assert not list(root.glob('**/*.mbt'))
assert not (root / 'moon.mod').exists()
print(json.dumps({
    'scope': 'plan documentation audit, no product or reference execution',
    'markdown_files_checked': len(files),
    'broken_local_links': broken,
    'tasks': len(tasks),
    'unchecked_steps_by_task': step_counts,
    'checked_implementation_steps': 0,
    'python_test_blocks_syntax_checked': python_blocks,
    'review_focus_classes': 5,
    'acceptance_rows_mapped': 12,
    'plan_lines': len(plan.splitlines()),
    'spec_lines': len(spec.splitlines()),
    'product_files_created': False,
    'product_tests_run': False,
    'sed_eval_run': False
}, ensure_ascii=False, indent=2))

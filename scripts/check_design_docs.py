"""Reproducible structure checks. Does NOT prove compilation or product correctness."""
import ast
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
markdown = sorted(root.glob('docs/**/*.md')) + [root/'AGENTS.md', root/'CLAUDE.md', root/'BACKLOG.md']
errors = []
python_blocks = 0
for path in markdown:
    content = path.read_text()
    if len(re.findall(r'^```', content, re.M)) % 2:
        errors.append(f'unpaired fence: {path.relative_to(root)}')
    for target in re.findall(r'\]\(([^)]+)\)', content):
        if '://' not in target and not target.startswith('#'):
            if not (path.parent/target.split('#')[0]).exists():
                errors.append(f'broken link: {path.relative_to(root)} -> {target}')
    for block in re.findall(r'```python\n(.*?)\n```', content, re.S):
        try:
            ast.parse(block)
            python_blocks += 1
        except SyntaxError as exc:
            errors.append(f'Python snippet syntax: {path.relative_to(root)}: {exc}')

task_names = ['T0-feasibility', 'T1-time', 'T1b-reference', 'T2-matching', 'T3-evaluation',
              'T4-reports', 'T5-cli-demo', 'T6-qualification', 'T7-package', 'T8-ci-handoff']
tasks = [root/'docs/superpowers/plans/tasks'/f'{name}.md' for name in task_names]
active = (root/'docs/contracts.md').read_text()
step_count = 0
completed_steps = 0
for path in tasks:
    if not path.exists():
        errors.append(f'missing task: {path.name}')
        continue
    text = path.read_text()
    active += '\n'+text
    steps = re.findall(r'^- \[([ xX])\] ', text, re.M)
    step_count += steps.count(' ')
    completed_steps += sum(step.lower() == 'x' for step in steps)
    if not steps:
        errors.append(f'no task steps: {path.name}')
if re.search(r'\bcounts\.fn\b', active) or 'reference/prediction/tp/fp/fn: Int' in active:
    errors.append('active MoonBit contract still uses keyword fn as field')
if 'fn_count' not in active or 'JSON仍写 `"fn"`' not in active:
    errors.append('internal/JSON fn mapping missing')
for value in ['2592000', '2000', '20000000', '1000000', '8 MiB', '16 MiB', 'collar-max-cardinality/v1']:
    if value not in active:
        errors.append(f'missing contract value: {value}')
for path in [root/'docs/PROJECT_STATE.md', root/'docs/reviews/2026-10-20-claude-feedback-disposition.md']:
    if not path.exists():
        errors.append(f'missing current status/review: {path.name}')
count = 500*501*502//6
assert count == 20_958_500 and count > 20_000_000
report = {
    'scope': 'documentation_structure_only', 'errors': errors,
    'markdown_files': len(markdown), 'task_cards': len(tasks), 'pending_steps': step_count,
    'checked_steps': completed_steps, 'checkbox_evidence': 'NOT_ASSESSED',
    'python_snippets_parsed': python_blocks,
    'old_dense_dfs_adjacency_lower_bound_n500': count,
    'compiler_feasibility': 'NOT_ASSESSED', 'product_behavior': 'NOT_ASSESSED',
    'independent_reference': 'NOT_ASSESSED', 'human_manual_review': 'NOT_ASSESSED'
}
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))

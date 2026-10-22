"""Deterministic, preselected qualification inputs; no product/reference outputs."""
import copy
from fractions import Fraction
import random

from validation.rational_oracle import number, decimal_text

SEED = 20261020


def safe_margins(document):
    cfg = document.get('config', {}); collar = number(cfg.get('collar_s', '0.2')); ratio = number(cfg.get('offset_ratio', '0.5'))
    unsafe = []; minimum = None; comparisons = 0
    for rec in document['recordings']:
        for r in rec['reference']:
            for p in rec['prediction']:
                if r['label'] != p['label']: continue
                onset = abs(number(p['onset_s']) - number(r['onset_s']))
                offset = abs(number(p['offset_s']) - number(r['offset_s']))
                limit = max(collar, (number(r['offset_s']) - number(r['onset_s'])) * ratio)
                for kind, margin in [('onset', abs(onset - collar)), ('offset', abs(offset - limit))]:
                    comparisons += 1
                    minimum = margin if minimum is None else min(minimum, margin)
                    if margin <= Fraction(1, 1_000_000):
                        unsafe.append(dict(recording_id=rec['id'], reference=r['id'], prediction=p['id'],
                                           condition=kind, margin_s=decimal_text(margin)))
    return dict(comparisons=comparisons, minimum_margin_s=None if minimum is None else decimal_text(minimum), unsafe=unsafe)


def event(id, onset, duration, label, unit):
    return dict(id=id, label=label, onset_s=decimal_text(Fraction(onset, unit)), offset_s=decimal_text(Fraction(onset + duration, unit)))


def random_document(rng, grid):
    unit = 8 if grid else 1_000_000
    document = dict(schema_version=1, labels=['A', 'B', 'unused'], recordings=[])
    if grid: document['config'] = dict(collar_s='0.25', offset_ratio='0.5')
    for i in range(rng.randint(1, 3)):
        refs = []; preds = []
        for j in range(rng.randint(0, 4)):
            onset = rng.randint(unit, 10 * unit); duration = rng.randint(1 if grid else 100_000, 3 * unit)
            refs.append(event('r' + str(j), onset, duration, rng.choice(['A', 'B']), unit))
        for j in range(rng.randint(0, 4)):
            if refs and rng.random() < .75:
                r = rng.choice(refs); onset = int(number(r['onset_s']) * unit) + rng.randint(-unit // 2, unit // 2)
                duration = int((number(r['offset_s']) - number(r['onset_s'])) * unit)
                label = r['label'] if rng.random() < .8 else rng.choice(['A', 'B'])
            else:
                onset = rng.randint(unit, 10 * unit); duration = rng.randint(1 if grid else 100_000, 3 * unit); label = rng.choice(['A', 'B'])
            preds.append(event('p' + str(j), onset, duration, label, unit))
        document['recordings'].append(dict(id='rec-' + str(i), reference=refs, prediction=preds))
    return document


def qualification_cases():
    from validation.compare import prototype_cases
    rng = random.Random(SEED); accepted = []; excluded = []
    for i in range(128):
        accepted.append(dict(name=f'grid-{i:03d}', category='binary_grid', document=random_document(rng, True)))
    for i in range(160):
        doc = random_document(rng, False)
        if i % 16 == 0:
            # Deliberately include known preselection rejects, before any evaluation.
            doc['recordings'].append(dict(id='boundary-reject', reference=[event('r', 10_000_000, 2_000_000, 'A', 1_000_000)],
                                         prediction=[event('p', 10_200_000, 2_000_000, 'A', 1_000_000)]))
        margins = safe_margins(doc)
        row = dict(name=f'decimal-{i:03d}', category='decimal_nonboundary', document=doc, margins=margins)
        (excluded if margins['unsafe'] else accepted).append(row)
    for name, doc, category in prototype_cases():
        if category in ['decimal_boundary', 'zero_collar']: group = 'exact_boundary'
        elif doc.get('config', {}).get('collar_s') == '0.25': group = 'binary_grid'
        else: group = 'decimal_nonboundary'
        row = dict(name='fixed-' + name, category=group, document=copy.deepcopy(doc))
        if group == 'decimal_nonboundary':
            row['margins'] = safe_margins(doc)
            if row['margins']['unsafe']: row['category'] = 'exact_boundary'
        accepted.append(row)
    return accepted, excluded

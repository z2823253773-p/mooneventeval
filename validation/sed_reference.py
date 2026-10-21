"""Development-only adapter around the unmodified, hash-verified sed_eval."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

SOURCE_LOCK = Path(__file__).with_name('reference-sources.json')

def verify_sources(package):
    package = Path(package)
    expected = json.loads(SOURCE_LOCK.read_text())['source_sha256']
    actual = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in package.rglob('*.py')}
    if actual != expected:
        raise RuntimeError('reference source mismatch; refusing patched or incomplete sed_eval')

def _reference_module():
    # Inspect the package without importing it; validate before executing source.
    spec = importlib.util.find_spec('sed_eval')
    if spec is None or not spec.submodule_search_locations:
        raise RuntimeError('locked reference environment missing sed_eval')
    verify_sources(next(iter(spec.submodule_search_locations)))
    import sed_eval
    return sed_eval

def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [_json_safe(v) for v in value]
    # numpy scalar conversion retains the numeric value; never patch numpy aliases.
    if hasattr(value, 'item'):
        return _json_safe(value.item())
    if isinstance(value,float) and not math.isfinite(value):
        return {'nonfinite': 'NaN' if math.isnan(value) else ('+Infinity' if value>0 else '-Infinity')}
    return value

def evaluate_document(document):
    """Evaluate a validated synthetic PRD document; times become reference floats.

    This is not the product input validator or rational oracle. Class-wise TP is
    projected into the product counting definition; raw substitution stays raw.
    """
    sed_eval = _reference_module()
    config = document.get('config', {})
    metrics = sed_eval.sound_event.EventBasedMetrics(
        event_label_list=list(document['labels']),
        t_collar=float(config.get('collar_s','0.2')),
        percentage_of_length=float(config.get('offset_ratio','0.5')),
        evaluate_onset=True, evaluate_offset=True, event_matching_type='optimal')
    def convert(events):
        return [dict(event_label=e['label'], event_onset=float(e['onset_s']),
                     event_offset=float(e['offset_s'])) for e in events]
    for recording in document['recordings']:
        metrics.evaluate(reference_event_list=convert(recording['reference']),
                         estimated_event_list=convert(recording['prediction']))
    raw_metrics = metrics.results_overall_metrics()
    by_class = metrics.results_class_wise_metrics()
    class_wise = {label: dict(counts=dict(counts), metrics=by_class[label])
                  for label,counts in metrics.class_wise.items()}
    reference = sum(len(r['reference']) for r in document['recordings'])
    prediction = sum(len(r['prediction']) for r in document['recordings'])
    tp = int(sum(c['Ntp'] for c in metrics.class_wise.values()))
    fp, fn = prediction-tp, reference-tp
    denominator = 2*tp+fp+fn
    projected = dict(counts=dict(reference=reference,prediction=prediction,tp=tp,fp=fp,fn=fn),
                     precision=tp/prediction if prediction else None,
                     recall=tp/reference if reference else None,
                     f1=2*tp/denominator if denominator else None)
    flags = {f'projected_{key}_defined': projected[key] is not None
             for key in ['precision','recall','f1']}
    for key, raw_key in [('precision','precision'),('recall','recall'),('f1','f_measure')]:
        flags[f'raw_{key}_defined'] = math.isfinite(raw_metrics['f_measure'][raw_key])
    flags['reference_time_representation'] = 'binary64_from_decimal_strings'
    flags['matching'] = 'original_sed_eval_optimal'
    flags['zero_collar_supported'] = False
    return _json_safe(dict(raw=dict(counts=dict(metrics.overall),metrics=raw_metrics),
                           class_wise=class_wise,projected=projected,
                           metric_definition_flags=flags))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = evaluate_document(json.loads(args.input.read_text()))
    text = json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text,end='')

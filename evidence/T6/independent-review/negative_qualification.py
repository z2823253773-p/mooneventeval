import json,sys,traceback
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'source'))
from validation.qualify import run_qualification
fixture=json.loads((root/'source/validation/fixtures/comparison-baseline.json').read_bytes())
mode=sys.argv[1]
case=dict(name='baseline',category='decimal_nonboundary',document=fixture['input'])
code=run_qualification(root/'negative-controls'/mode,root/'evidence'/('negative-'+mode),cases=[case])
print('QUALIFICATION_RETURN',code)
raise SystemExit(code)

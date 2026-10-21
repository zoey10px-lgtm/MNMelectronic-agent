import sys, json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.chdir(ROOT); sys.path.insert(0,str(ROOT))
from evaluate_model import evaluate
w, out = sys.argv[1], sys.argv[2]
r = evaluate(w, out)
s = r['summary']
print(json.dumps({k: s[k] for k in ('train','val')}, ensure_ascii=False))
print('val per class:', {c: v for c, v in s['val_per_class'].items()})
for c in r['cases']:
    if c['variant'] != 'full': continue
    gt = [(t['class_name']) for t in c['ground_truth']]
    pr = [(p['label'], round(p['confidence'], 2)) for p in c['predictions']]
    wk = [(p['label'], round(p['confidence'], 2)) for p in c['candidates']]
    print(c['split'], c['source_id'], 'GT', gt, 'PRED', pr, 'weak', wk, 'typedTP', c['typed']['tp'], 'locTP', c['localization']['tp'])
print('blank FP:', [len(x['predictions']) for x in r['challenges'] if x['name'].startswith('blank')])

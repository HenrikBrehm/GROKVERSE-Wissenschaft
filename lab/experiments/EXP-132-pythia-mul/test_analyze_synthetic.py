import json, sys, tempfile, pathlib, numpy as np, subprocess
sys.path.insert(0, 'lab/experiments/EXP-043-generalize-steering')
from make_split import group
N, ELEM = group('mul', 113)
root = pathlib.Path(tempfile.mkdtemp())
rng = np.random.default_rng(0)
i = np.arange(N)
for s in (1000, 1001):
    tj = json.load(open(f'lab/experiments/EXP-132-pythia-mul/splits/seed{s}.json'))['targets']
    E0 = rng.normal(size=(113, 16))
    for arm in 'FG':
        ET = 0.96 * E0 + 0.01 * rng.normal(size=E0.shape)
        for k in tj[arm]:
            ET[ELEM, k % 16] += 0.5 * np.cos(2 * np.pi * k * i / N)
        d = root / f'pt_seed{s}_seed{s}_{arm}_steps4000_x'; d.mkdir()
        np.save(d / 'in_snapshots.npy', np.stack([E0, ET]).astype(np.float32))
        (d / 'result.json').write_text(json.dumps({'status': 'completed', 'curve': [[4000, 1, 0.9, 0]], 'ablation': {'C_in': 0.5, 'C_both': 0.5}}))
out = subprocess.run([sys.executable, 'lab/experiments/EXP-132-pythia-mul/analyze.py', '--root', str(root), '--steps', '4000'], capture_output=True, text=True, encoding='utf-8')
print(out.stderr[-800:]); r = json.loads(out.stdout); print(r['reading'], [(x['seed'], round(x['dpow_update_in'], 2), x['top5_log_F']) for x in r['rows']]); print(out.stderr[-300:])

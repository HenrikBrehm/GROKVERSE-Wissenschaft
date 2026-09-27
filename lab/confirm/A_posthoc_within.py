"""Programme A post hoc, EXPLORATION (session 28): does the fine order of the five targets (N39/C1) generalize to 4x width
(EXP-049, d512 and d128 control) and to non-modular integer addition (EXP-048)? Pilot seeds, already seen for K2, never for the
order. Fixed before looking: predictor = mask spectrum (EXP-049: M0c and M0 as in P1; EXP-048: its own M0 `mask_power`),
competitor = step-0 power; mean within-arm Spearman at step 2000, within-arm permutation p (20 000). EXP-048: primary target
measure = detrended DFT of the final W_E (its registered primary), raw spectrum reported too."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "confirm")); sys.path.insert(0, str(LAB / "tools"))
from P1_posthoc_within import m0c_add, mean_rho

def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(Path(path).parent)); spec.loader.exec_module(m); return m

rng = np.random.default_rng(2809)
def perm(X, Y):
    obs = mean_rho(X, Y); null = np.array([mean_rho(rng.permuted(X, axis=1), Y) for _ in range(20000)])
    return {"mean_rho": round(obs, 3), "p_two": float((np.abs(null) >= abs(obs)).mean())}

out = {}
E49 = next((LAB / "experiments").glob("EXP-049*")); ms49 = mod(E49 / "make_split.py", "ms49")
for dm in ("d512", "d128"):
    Y, MC, M0, I0 = [], [], [], []
    for d in sorted((E49 / "raw").glob(f"EXP-049_{dm}_*_devcuda")):
        stem = d.name.split(f"{dm}_seed")[1].split("_", 1)[1].rsplit("_devcuda", 1)[0]
        T = json.loads((E49 / f"splits/{stem}.json").read_text())["targets"]; sel = [k - 1 for k in T]
        idx = np.load(E49 / f"splits/{stem}.npy"); sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        Y.append(sp[st.index(2000)][sel]); I0.append(sp[st.index(0)][sel]); MC.append(m0c_add(idx, 113)[sel]); M0.append(ms49.m0(idx)[sel])
    Y, MC, M0, I0 = map(np.array, (Y, MC, M0, I0))
    out[f"EXP-049_{dm}"] = {"arms": len(Y), "M0c": perm(MC, Y), "M0": perm(M0, Y), "init": perm(I0, Y)}
    print(dm, json.dumps(out[f"EXP-049_{dm}"]), flush=True)

E48 = next((LAB / "experiments").glob("EXP-048*")); ms48 = mod(E48 / "make_split.py", "ms48"); an48 = mod(E48 / "analyze.py", "an48")
from intadd_train import dft_power
Yd, Yr, M0, I0 = [], [], [], []
for d in sorted((E48 / "raw").glob("EXP-048_*_eps2.0_*_devcuda")):
    stem = d.name.split("_", 2)[2].rsplit("_devcuda", 1)[0]
    T = json.loads((E48 / f"splits/{stem}.json").read_text())["targets"]; sel = [k - 1 for k in T]
    idx = np.load(E48 / f"splits/{stem}.npy"); sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
    Yd.append(dft_power(an48.detrend(np.load(d / "we_final.npy").astype(float)))[sel]); Yr.append(sp[st.index(2000)][sel])
    I0.append(sp[st.index(0)][sel]); M0.append(ms48.mask_power(idx)[sel])
Yd, Yr, M0, I0 = map(np.array, (Yd, Yr, M0, I0))
out["EXP-048"] = {"arms": len(Yd), "detrended": {"M0": perm(M0, Yd), "init": perm(I0, Yd)}, "raw": {"M0": perm(M0, Yr), "init": perm(I0, Yr)}}
print("intadd", json.dumps(out["EXP-048"]))
(LAB / "confirm/A_posthoc_within.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

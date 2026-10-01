"""L0b post hoc (Sitzung 66, 2026-10-01): Welche konstruierten Splits verschiebt die Reihenfolge?

Anlass: H2 nicht bestätigt (O-Anteil auf F/G +0.022), die Verschiebung sitzt sichtbar in einer Minderheit der Läufe
(Abb. J1 b). Nur Beschreibung, nicht Teil der Holm-Familie, keine Kernaussage.

Vorab (geschrieben nach dem Blick auf Abb. J1, vor dieser Rechnung):
  je Seed s = x_H2 = Mittel über F/G von o(stride) - o(iid) am Ende (n = 70; je Split getrennt
  speichert die eingefrorene Zusammenfassung o nicht).
  Frage 1: Sind langsam generalisierende Splits anfälliger? rho1 = Spearman(s, Mittel F/G von log2 t_gen(iid)).
           Lesart: rho1 >= 0.3 "langsame anfaelliger", rho1 <= -0.3 "schnelle anfaelliger", sonst "kein klarer Zusammenhang".
  Frage 2 (beschreibend): rho2 = Spearman(s, x_H4) – geht die Verschiebung mit
           der Verzögerung einher?
  Zählung: Seeds mit s > 0.05 ("deutlich verschoben").
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rho with average ranks for ties (numpy only; scipy is not installed globally)."""
    def rank(v: np.ndarray) -> np.ndarray:
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v))
        r[order] = np.arange(len(v), dtype=float)
        for u in np.unique(v):
            m = v == u
            r[m] = r[m].mean()
        return r
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def main() -> None:
    # The frozen summary stores the end-of-budget O share of the engineered splits only as the F/G mean per seed
    # (o_FG_*; x_H2 = its stride - iid difference), so the analysis is per seed (n = 70), F/G averaged.
    rows = json.loads((HERE / "L0b_summary.json").read_text(encoding="utf-8"))["rows"]
    s = np.array([r["x_H2"] for r in rows])
    lg = np.array([np.mean([np.log2(r["tgen_iid16w"][f] or 30000) for f in "FG"]) for r in rows])
    dl = np.array([r["x_H4"] for r in rows])
    rho1 = spearman(s, lg)
    rho2 = spearman(s, dl)
    read = "langsame anfaelliger" if rho1 >= 0.3 else "schnelle anfaelliger" if rho1 <= -0.3 else "kein klarer Zusammenhang"
    out = {"n_seeds": int(len(s)), "rho1_shift_vs_log2tgen_iid": float(rho1), "reading1": read,
           "rho2_shift_vs_delay_xH4": float(rho2), "n_seeds_shift_gt_0.05": int((s > 0.05).sum()),
           "mean_shift": float(s.mean())}
    (HERE / "L0b_posthoc_h2_who_s66.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

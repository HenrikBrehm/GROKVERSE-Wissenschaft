"""EXP-134 post hoc (Sitzung 66, 2026-10-01): Wie wachsen die Zahlzeilen in Phase 1 (nur Text)?

Anlass: In Phase 1 sieht das Modell die Zahl-Tokens 0..112 nie als Eingabe; mit gebundener Einbettung
bekommen ihre Zeilen nur Ausgabe-Gradienten. Für ein Token i, das nie Ziel ist, ist der Gradient der
Kreuzentropie nach seiner Ausgabezeile p_i * h (h = letzter versteckter Zustand). Alle nie gezielten
Zeilen werden also in dieselbe Richtung (gegen das mittlere h) geschoben, und AdamW normiert die
winzigen Gradienten auf Schritte der Größe ~lr. Gegenerklärung für die Norm ×5 (README, Zyklus 9 S65).

Vorab (geschrieben zwischen 03:10 und 03:12 Berlin gemessen, vor dem Rechnen; zuerst stand hier
  irrtümlich die geschätzte Zeit 03:32; nur gespeicherte Schnappschüsse, kein Training):
  D = W(Phase-1-Ende) - W(0) je Zahlzeile (113 × 384).
  c = ||mean_i D_i||^2 / mean_i ||D_i||^2  (Anteil der gemeinsamen Richtung = DC-Anteil im Zahl-Index).
  Lesart je Seed: "gemeinsame Richtung" c >= 0.5, "zeilenspezifisch" c < 0.2, sonst "gemischt".
  Gesamt: gleiche Lesart in beiden Seeds, sonst "uneinheitlich".
  Beschreibend: Anteil der ersten Singulärrichtung von D; Top-5 der Nicht-DC-Frequenzen
  von D (nur beschreibend); Normverlauf |W_i| über die
  Schnappschüsse (linear ≈ konstante Adam-Schritte).
Was die Lesart bedeutet: "gemeinsame Richtung" stützt die Gegenerklärung (Wachstum ist eine DC-Verschiebung,
die Δ_pow nicht direkt misst, aber die Ausgangslage der Zeilen ändert); sie beweist nicht, dass die
Verzögerung in Phase 2 davon kommt (keine Intervention).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
P = 113


def power_by_freq(D: np.ndarray) -> np.ndarray:
    F = np.fft.rfft(D, axis=0)  # über den Zahl-Index
    return (np.abs(F) ** 2).sum(axis=1)  # Länge 57, Index 0 = DC


def reading(c: float) -> str:
    return "gemeinsame Richtung" if c >= 0.5 else "zeilenspezifisch" if c < 0.2 else "gemischt"


def main() -> None:
    out = {}
    for d in sorted((HERE / "raw_pre").iterdir()):
        W = np.load(d / "we_snapshots.npy").astype(np.float64)
        steps = np.load(d / "we_snapshot_steps.npy")
        D = W[-1] - W[0]
        c = float(np.linalg.norm(D.mean(0)) ** 2 / (np.linalg.norm(D, axis=1) ** 2).mean())
        sv = np.linalg.svd(D, compute_uv=False)
        pw = power_by_freq(D)
        norms = np.linalg.norm(W, axis=2).mean(1)
        out[d.name] = {"common_share_c": c, "reading": reading(c),
                       "top1_sv_share": float(sv[0] ** 2 / (sv ** 2).sum()),
                       "dc_share_check": float(pw[0] / pw.sum()),
                       "nonDC_top5_freqs": [int(k) for k in np.argsort(pw[1:])[::-1][:5] + 1],
                       "mean_row_norm_by_step": {int(s): round(float(n), 4) for s, n in zip(steps, norms)},
                       "cos_common_dir_with_mean_init_row": float(
                           D.mean(0) @ W[0].mean(0) / (np.linalg.norm(D.mean(0)) * np.linalg.norm(W[0].mean(0)) + 1e-12))}
    rs = {v["reading"] for v in out.values()}
    res = {"overall": rs.pop() if len(rs) == 1 else "uneinheitlich", "runs": out}
    (HERE / "posthoc_rowdrift_s66.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()

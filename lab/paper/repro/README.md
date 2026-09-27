---
id: paper-repro
status: entwurf
datum: 2026-09-27
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[paper/draft]]"]
---
# Reproduktionspaket (Regel 19c): Stand und Plan

Zurück zu [[paper/STATUS]]. Entwurf Sitzung 24. **Noch nicht vollständig gelaufen.**

## Umgebung (gemessen 2026-09-27)

- Windows 11, Ryzen 5 5600X, 32 GB RAM, AMD Radeon RX 7900 XT (20 GB).
- CPU-Python 3.12.10, torch 2.13.0+cpu, numpy 2.5.1. GPU-Umgebung `.venv-gpu`: torch 2.9.1+rocm7.2.1 (Gleichwertigkeit CPU/GPU: GPU-001).
- Alle Trainings- und Testläufe nur über `python lab/tools/guarded_run.py -- …` (Zeitfenster).

## Heute: Abbildung/Tabelle → eingefrorener Block → Befehle (bestehende Werkzeuge)

| Abbildung / Tabelle | Block (Manifest) | Läufe erzeugen | Auswertung | Abbildung |
|---|---|---|---|---|
| Tab. 3.1, Abb. 2 (K2) | P1 (733e829) | `python lab/tools/parallel_queue.py lab/confirm/P1_jobs.txt --workers 8` | `confirm_p1.py --analyze lab/confirm/P1_manifest.json` | `python lab/paper/figures/fig2_p1_delta_pow.py` |
| 3.2 (K2-Funktion) | P2d (c0cd65f), P2e (3c484ef) | `parallel_queue.py lab/confirm/P2d_jobs.txt`, `…/P2e_jobs.txt` | `confirm_p2d.py` / `confirm_p2e.py --analyze …` | — |
| 3.3, Abb. 4 (K4, K4b) | P3 (f8adf45), N28 (fa154bd) | `…/P3_jobs.txt`, `…/N28_jobs.txt` | `confirm_p3.py` / `confirm_n28.py --analyze …` | `fig4_pi_curve.py` (Pilotkurve aus EXP-059) |
| 3.4, 3.5, Abb. 3 (K4c–e) | N29 (087e042), N29b (db31564), N29c (3c9cb63) | `…/N29_jobs.txt`, `…/N29b_jobs.txt`, `…/N29c_jobs.txt` | `confirm_n29*.py --analyze …` | `fig3_ablation_contrast.py` |
| Abb. 1 (Beispiel) | EXP-016 (Pilot) | `lab/experiments/EXP-016-engineered-split` (CPU) | — | `fig1_mask_vs_learned.py` |

Wichtig: Die Auswertungen prüfen Code-Hashes gegen ihr Manifest. Nach späteren Trainer-Änderungen am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`).

## Plan für das eigentliche Paket (schlank, ohne Nachtrag-Ketten)

1. `repro/train.py`: minimaler Trainer (arch25k, AdamW, Vollbatch, Split-Datei, optionaler Wechsel und Teil-Reset), der bitgleich zu `freq_ban.py` im Standardpfad rechnet (Test gegen gespeicherte Läufe).
2. Je Kernaussage ein Skript `repro/k2.py`, `repro/k2_function.py`, `repro/k4.py`, `repro/k4_resets.py`: Splits bauen (aus `confirm_splits`-Logik kopiert), Läufe, Auswertung, Tabelle; `--smoke` = 2 Seeds, wenige Schritte.
3. Einmal vollständig im Fenster laufen lassen, Zahlen gegen FINDINGS vergleichen, Laufzeiten eintragen.
4. Lizenz- und Rechtefrage zum Studiencode vorher klären (Nutzer, [[paper/STATUS]] „Offen“).

## Stand Sitzung 25 (2026-09-27, vor jedem Lauf): schlanker Trainer `repro/train.py` (Plan Punkt 1), **ungetestet**

`lab/paper/repro/train.py` (≈ 190 Zeilen): Standardpfad von `freq_ban.py` ohne die Labor-Eingriffe (Verbote, Warmup, Lernraten-Skalen, Rewind, Wechsel-Varianten),
ohne Sperren und Fingerabdrücke; gleiche Reihenfolge (Threads, Seed, Datensatz, Init auf der CPU, `.to(device)`, AdamW), gleicher Verlust, gleicher Wechsel und Teil-Reset
(`attn`, `mlp`, `vo`, `qk`, `unembed`, `we`). Abhängig nur von `training/grokverse` (Rechtefrage siehe [[paper/STATUS]]). `--compare-to <Laufordner>` vergleicht die Spektren
mit einem gespeicherten Lauf an allen gemeinsamen Schritten.

**Gleichwertigkeitsprüfung (ab 00:00, GPU, gleiche Umgebung wie die Blöcke; Abnahme: relative Abweichung ≤ 1e-4 an allen gemeinsamen Schritten, Bitgleichheit wird nur berichtet):**

```
G="C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"   # s27 audit: absolute path (relative venv paths fail in CreateProcess); bash syntax, run from Git Bash
# K2 (P1, Seed 1000, Arm F, 2000 Schritte)
python lab/tools/guarded_run.py -- $G lab/paper/repro/train.py --seed 1000 --steps 2000 --device cuda   --split-file lab/confirm/splits/confirm_exp1_eps2.0_add113_seed1000_F.npy --out lab/paper/repro/out/eq_p1_1000F   --compare-to lab/confirm/raw/EXP-016_baseline_seed1000_thr1_confirm_exp1_eps2.0_add113_seed1000_F_devcuda --tol 1e-4
# K4d (N29b, Seed 2300, Wechsel bei 50 mit Attention-Reset, 4050 Schritte)
python lab/tools/guarded_run.py -- $G lab/paper/repro/train.py --seed 2300 --steps 4050 --device cuda   --split-file lab/confirm/n29b_splits/n29b_seed2300_w0_A.npy --test-file lab/confirm/n29b_splits/n29b_seed2300_test.npy   --switch-split-file lab/confirm/n29b_splits/n29b_seed2300_w0_B.npy --switch-step 50 --reset-at-switch attn   --out lab/paper/repro/out/eq_n29b_2300_attn   --compare-to lab/confirm/n29b_raw/EXP-020_baseline_seed2300_thr1_n29b_seed2300_w0_A_to_n29b_seed2300_w0_B_at50_rsattn_devcuda --tol 1e-4
```

Einschränkung: Der Referenzlauf N29b wurde mit `--stop-after-gen 4050` gerechnet (kein vorzeitiger Stopp bei 4050 Schritten), der schlanke Trainer rechnet immer die volle
Schrittzahl; beide sind damit gleich lang. Besteht die Prüfung, folgen die Skripte je Kernaussage (Plan Punkt 2) auf diesem Trainer. `lab/paper/repro/out/` gehört nicht in Git.

**K2-Skript `repro/k2.py` (Sitzung 25, ungetestet):** baut die P1-Splits (Versuchs-ID 1, ε = 2), trainiert F/G je Seed mit `repro/train.py`, berichtet Δ_pow bei 2000 (Mittel, Bootstrap-KI,
Vorzeichentest) und mit `--compare-p1` die größte Abweichung je Seed zur eingefrorenen P1-Zusammenfassung. Smoke: `python lab/tools/guarded_run.py -- python lab/paper/repro/k2.py --smoke`
(2 Seeds, 200 Schritte, CPU). Voll (GPU, ≈ 100 Läufe à 2000 Schritte): `... .venv-gpu/Scripts/python.exe lab/paper/repro/k2.py --device cuda --workers 8 --compare-p1`. Erst nach bestandener
Gleichwertigkeit (oben) laufen lassen. D₅₉ fehlt (anderer Trainer).

**K4c-Skript `repro/k4c.py` (Sitzung 26, ungetestet):** baut die N29-Splits (`overlap_split`, ω = 0, kalibriertes ε), trainiert je Seed A→B und B→A bei t ∈ {25, 50} für t + 4000 Schritte mit
`repro/train.py --save-model`, entfernt am Endmodell die alten bzw. neuen Zielfrequenzen aus W_E[:113] und misst die Genauigkeit auf der zurückgehaltenen Testmenge; H1/H2 wie N29 (t-Test, Holm,
Bootstrap-KI über die Hilfsfunktionen von `confirm_p1`). `--compare-n29` vergleicht je Seed acc_alt/acc_neu mit `lab/confirm/N29_summary.json` (Abnahme ≤ 0.02). Smoke:
`python lab/tools/guarded_run.py -- python lab/paper/repro/k4c.py --smoke` (1 Seed, 300 Schritte nach dem Wechsel, CPU). Voll (GPU, 80 Läufe, nach N29 ≈ 17 min mit 7–8 Arbeitern):
`... .venv-gpu/Scripts/python.exe lab/paper/repro/k4c.py --device cuda --workers 8 --compare-n29`. Erst nach bestandener Gleichwertigkeit (oben).

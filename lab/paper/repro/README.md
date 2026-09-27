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

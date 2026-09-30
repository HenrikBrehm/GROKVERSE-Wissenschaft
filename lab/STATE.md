---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-10-01, 01:59 Berlin (Sitzung 65) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ausführliche ältere Fassung mit allen Sitzungsnotizen 46–63: `git show 546b8874:lab/STATE.md`; davor `b6430af4`, `7f9d56d4`.*

## Lage (Kurzform)

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion, K4–K4e, R2–R12, K5, L0 (Minibatch), N54b (Festlegung ≈ √(N/B)), LM1/LM1-F (≈ 79 % Rechen-Tokens), LM3/LM3-F (≈ 8.7 %). Alle im Paper. Pilot EXP-125 (≈ 29.5 M LM, S65): „K2 hält im LM“ (Δ_pow 3.79/5.42), im Anhang K; Abstract 1919/1920 Zeichen.
- **Pythia-Linie geschlossen** (EXP-127/130/131/132/133): beim Nachtrainieren von Pythia-160M keine Datensteuerung; im Paper Anhang K + Grenze (ii).
- **Paper:** laborseitig fertig bis auf L0b (Sätze vorab in [[paper/L0b_DEUTUNGEN]], Zeichenbudget im Nachtrag S65); EXP-125 eingearbeitet und geprüft (S65). Offen nur Nutzerentscheidungen ([[paper/STATUS]]).

## Beim GPU-Dienst (Regel 21, `lab/queue/status.json`), Reihenfolge

1. `44zzzzz_l0b` – **L0b** (Bestätigung Menge gegen Reihenfolge bei B = 16, eingefroren bce36b1a, 420 Läufe, 8 Worker, ≈ 370 s je Lauf unter Last ≈ 1.3 Läufe/min; 225/420 um 01:58; neben EXP-134 nur ≈ 1.2 Läufe/min → fertig ≈ 04:30–05:00).
2. `45z_exp134_textpre` – **EXP-134** (neu S64, N62): eigenes LM erst 6000 Schritte nur Text, dann LM1-Fakten F/G; steuert die Auswahl noch? 2 Jobs, laufen seit ≈ 01:40, 4250/18 000 um 01:58 (≈ 0.25 s/Schritt) → fertig ≈ 03:00.
3. `45zz_exp135_switch` – **EXP-135** (neu S64): K4 im LM, Faktenwechsel F → G nach 250/1000/3000 Schritten; Festlegung am Anfang oder mit dem Lernen? 6 Jobs.
4. `45zzz_exp136_modulus` – **EXP-136** (neu S65, N63): K2 bei add 211/307, 30 % und 3831 Paaren (LeDoux-Einwand), 24 Läufe à 6–15 min. Auswertung: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-136-large-modulus/analyze.py` (Lesarten + Zweitlesart im README).
5. `46_exp128_sgdclip` (EXP-128, SGD + Clipping), `47_exp129_k1` (EXP-129, ≈ 4.5 % Rechen-Tokens).

Nichts davon selbst neu einreihen; vor dem Ablegen status.json prüfen; Jobdateien außerhalb von inbox schreiben, dann `mv`.

## Nächste Schritte

1. **L0b auswerten**, wenn `lab/queue/done/44zzzzz_l0b.summary.json` da ist: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_l0b.py --analyze lab/confirm/L0b_manifest.json`; dann unabhängige Nachrechnung `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/L0b_independent_recompute.py --analyze`; Abbildung `python lab/paper/figures/fig17_l0b_set_vs_order.py` (vorab geschrieben S65); post hoc (beschreibend, Lesart vorab) `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/L0b_posthoc_r5_s65.py` (R5 unter Minibatch); Paper nach [[paper/L0b_DEUTUNGEN]] + unabhängige Textprüfung; FINDINGS, LAB, Tageserklärung.
2. **EXP-134** / **EXP-135** auswerten: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-134-text-pretrain-steering/analyze.py` bzw. `.../EXP-135-lm-switch-lockin/analyze.py`; Lesarten vorab in den READMEs. Paper erst nach Entscheidung (Explorationen → höchstens Anhang).
3. **EXP-136** auswerten (Befehl oben), Paper nach [[paper/EXP136_DEUTUNGEN]].
4. EXP-128 (`lab/experiments/EXP-128-sgd-clip/analyze.py`), EXP-129 (`lab/experiments/EXP-129-lm-k1-share/analyze.py`).
5. Tägliche Erklärung [[paper/erklaerung/ERKLAERUNG_2026-10-01]] fortschreiben (Punkte 7–9 = L0b, EXP-134, EXP-136 angelegt; EXP-125 eingetragen).

## Nicht ändern (Hashes gebunden)

- `lab/experiments/EXP-001-freq-ban/freq_ban.py`, `lab/tools/confirm_l0b.py`, `lab/confirm/l0b_splits/` (L0b-Manifest).
- `lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py` (LM1/LM3-Manifeste; EXP-134/135 nutzen ihn nur über Wrapper), `confirm_lm3*.py`, `confirm_r12.py` + R12-Splits.
- `ft_pythia.py`, `ft_reset.py`; `lab/confirm/rank_tools.py` (Code-Tore C1–C4).
- Eingefrorene Blöcke: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`); Smoke durch den eingefrorenen Lader vor jedem Block.

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit S33): Prüfungen durch unabhängige Claude-Agenten (nur lesend).
- **P-021:** Pythia-Läufe hängen beim Beenden; Jobdateien mit HF-Modellen immer `stall_minutes=15`. Nicht selbst beenden (Regel 22: Hinweis in LIVE + Nachricht an den Assistenten).
- GPU: ≤ 10 Prozesse (HIP-Fehler bei 12–14), `gpu_gb` immer angeben (lm_stage2 3.5, d 512 6.0, freq_ban 0.75). LM-Läufe höchstens 2–3 gleichzeitig.
- GPU-Läufe sind nicht bitgleich wiederholbar (nichtdeterministische Kernel); Wiederaufnahme-Tests auf der CPU.
- `--analyze`/`analyze.py` brauchen `PYTHONIOENCODING=utf-8`; Auswertungen mit globalem Python über den Wächter, Trainer mit `.venv-gpu` (absoluter Pfad).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`, `lab/paper/outreach/`, Dienstdateien) **nicht committen**; immer einzelne Pfade.
- Notizen: CRLF/LF je Datei erkennen, kein `sed -i` auf Notizen. **Uhrzeiten nur gemessen** (Python zoneinfo) – in S61–S64 mehrfach geschätzt und korrigiert.
- Eine Runner-Sitzung endet mit der Antwort: Jobs im Vordergrund beobachten, nie „Wecker stellen und aufhören“.

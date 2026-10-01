---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-10-01, 04:38 Berlin (Sitzung 66) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ausführliche ältere Fassung mit allen Sitzungsnotizen 46–63: `git show 546b8874:lab/STATE.md`; davor `b6430af4`, `7f9d56d4`.*

## Lage (Kurzform)

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion, K4–K4e, R2–R12, K5, L0 (Minibatch), N54b (Festlegung ≈ √(N/B)), LM1/LM1-F, LM3/LM3-F. **Neu S66: L0b teilweise bestätigt** (B = 16: Reihenfolge verschiebt O-Anteil auf Zufallssplits +0.063, H1; auf konstruierten +0.022, H2 *nicht* bestätigt → keine Aussage „Menge gewinnt“; Steuerung bleibt H3; Verzögerung ×1.5 H4; unabhängig nachgerechnet). Paper §6, Anhang J (Abb. J1), Grenzen, Abstract (1916 Zeichen) – unabhängige Textprüfung lief in S66 (Ergebnis im JOURNAL).
- **Piloten LM (Anhang K):** EXP-125 (29.5 M), EXP-134 (Text-Vortraining; Zahlzeilen-Wachstum = 96 % gemeinsame Verschiebung, S66), **EXP-135 „Festlegung mit dem Lernen“** (S66: Wechsel bei 250/1000 überschrieben, bei 3000 hält F).
- **Pythia-Linie geschlossen.** Paper laborseitig fertig; offen nur Nutzerentscheidungen ([[paper/STATUS]]).

## Beim GPU-Dienst (Regel 21, `lab/queue/status.json`), Reihenfolge

1. `45zzz_exp136_modulus` – **EXP-136** (K2 bei add 211/307, 30 % gegen 3831 Paare; LeDoux-Einwand), 24 Läufe à 6–15 min, 6/24 fertig, 4 laufen (04:38). Auswertung: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-136-large-modulus/analyze.py` (Lesarten + Zweitlesart im README; Vorhersage `mask_prediction_s65.json`; Paper-Sätze [[paper/EXP136_DEUTUNGEN]]).
2. `46_exp128_sgdclip` (EXP-128, SGD + Clipping; 4/16 laufen) und `47_exp129_k1` (EXP-129, ≈ 4.5 % Rechen-Tokens; 1/4 läuft), beide schon gestartet (04:38).

Nichts davon selbst neu einreihen; vor dem Ablegen status.json prüfen; Jobdateien außerhalb von inbox schreiben, dann `mv`.

## Nächste Schritte

1. Falls der L0b-Prüfbericht in S66 nicht mehr eingearbeitet wurde: JOURNAL S66 lesen, Punkte übernehmen.
2. **EXP-136** auswerten (Befehl oben), Paper nach [[paper/EXP136_DEUTUNGEN]] + Textprüfung.
3. EXP-128 (`lab/experiments/EXP-128-sgd-clip/analyze.py`, [[paper/EXP128_DEUTUNGEN]]), EXP-129 (`lab/experiments/EXP-129-lm-k1-share/analyze.py`).
4. Nach L0b: Folgefrage für Regel 20b ist nur noch der Regimeabstand zu LeDoux (EXP-136); GPU-Leerlauf vermeiden – BACKLOG Option 6 (EXP-134 Mittelvektor-Intervention) nur als Füllarbeit.
5. Tageserklärung [[paper/erklaerung/ERKLAERUNG_2026-10-01]] (L0b, EXP-135 eingetragen); ab 02.10. neue Datei.

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

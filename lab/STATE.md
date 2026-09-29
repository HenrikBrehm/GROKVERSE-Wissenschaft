---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 05:32 Berlin (Sitzung 47 läuft, Deadline 06:29) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (Nanda 20/20, nachgerechnet), K4–K4e, R2–R10, K5, **R11** (Festlegung auch add 97 / mul 113), **L0** (K2 unter i.i.d.-Minibatch B 256/64, 10 frische Seeds, eingefroren 26419818, nachgerechnet).
- **Explorationen Sitzung 46:** EXP-100-Pilot (Reihenfolge wirkt bei B 256/64 nicht; SGD nicht kalibrierbar; B 16 lernt bei wd 1 nicht), Wechselläufe (unter B 256 keine Festlegung bis 50 Schritte), **EXP-106** (B 16, wd 0.1: Menge steuert; Reihenfolge verschiebt nur auf Zufallssplits, kostet auf konstruierten ×1.6 Zeit; nachgerechnet), **EXP-107** (unter B 256 Fenster bei 100–200 Schritten, t½ ≈ 133 = 8.9 Epochen; nachgerechnet), **EXP-108** (Batch-Reihe: Festlegung skaliert ≈ √(N/B), α = 0.54 [0.52, 0.56]; nachgerechnet; ohne Full-Batch-Punkt α = 0.556 [0.513, 0.595]), EXP-103 (lr·wd-Uhr ab ≈ 250 Schritten, früh zählt lr), EXP-101 (RFM ohne K2-Lesart).
- **Paper:** Langfassung §3.16 (R10), §3.17 (R11); Kurzfassung §5 (R11), §6 mit L0-Pilot, Bestätigung, EXP-106/107, Grenzen angepasst. Abb. 4 aus echten Daten (Titel noch deutsch). §6 und Abstract nach unabhängiger Textprüfung korrigiert (19 Punkte, Sitzung 46); Abstract 1875 Zeichen.

## Aktive Queue / laufende Jobs

- **EXP-110** (lr-4e-3-Pilot zu N54c, 84 Läufe, 6 Worker, Start ≈ 05:35, Log `lab/runner/logs/exp110.out`) und **EXP-102 „all 30k“** (4 Läufe à 30 000 Schritte, 4 Worker, `lab/runner/logs/exp102_30k.out`). Werden bei der Sitzungsdeadline 06:29 ggf. vom Wächter beendet. **Wiederaufnahme:** dieselben Queues erneut starten (`python lab/tools/parallel_queue.py lab/experiments/EXP-110-lockin-lr4-pilot/jobs.txt --workers 6 --min-minutes 3`; `… EXP-102-lm-ladder-stage1/jobs_long30k.txt --workers 4 …`; fertige Läufe werden übersprungen, unfertige lm_ladder-Läufe mit `run.lock` vorher beiseitelegen), dann `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-110-lockin-lr4-pilot/analyze.py`.
- Fertig in Sitzung 47: **N54b bestätigt** (H1 α 0.583 [0.560, 0.606]; H2 Δα +0.139 [0.098, 0.178]; nachgerechnet); EXP-109; **EXP-102** Pilot (nachgerechnet) + Folgetest 10k („grokkt nicht“: Verlust auf allen Positionen verzögert Grokking > ×10).

## Nächste Schritte (Regel 20)

1. **EXP-102 weiter:** Stufe „all“ grokkt bis 10 000 kaum; 30k-Test (2 Seeds) auswerten, dann Vergleich nach dem Grokking vorab festlegen (längeres Budget oder angepasstes wd); danach Minibatch-Stufe. Leiter-Ergebnis in FINDINGS/Paper erst nach diesem Schritt.
2. **N54c** (nächster Test der Festlegungsuhr): lr 4e-3, Vorhersagen im JOURNAL (05:00) — M_add 20/56/177, M_pow 23/57/141, M_i 18/36/72 für B 1024/256/64. Erst Stabilitätspilot (2 gesehene Seeds), dann Registrierung mit Seeds 3910–3919.
3. **Paper:** N54b-Text in §6 nach der unabhängigen Prüfung korrigieren; Langfassung §3.19 (N54b); Abstract ggf. (1875/1920 Zeichen); Zenodo (k2.py-Pfad = Nutzerentscheidung); Repro-Pfad-Smoke `k4c.py --smoke` nur ohne laufende GPU-Queue (CPU-Überlast).
4. L0b (Reihenfolge bei langen Epochen) bleibt offen, niedrigere Priorität.
5. Sprachmodell-Leiter Stufe 2 (EXP-105) nach Stufe 1.

## Prioritäten

1. **Paper** (Regel 20d, Ziel Do 01.10.): L0 ist bestätigt → §6/Abstract fertigstellen, Textprüfung.
2. **N54b / L0b** (Minibatch-Uhr der Festlegung; Reihenfolge bei langen Epochen) — beide als saubere Registrierungen.
3. Mechanismus-Versuche (EXP-096–099) ruhen (Regel 20a).

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit Sitzung 33). Ersatz: unabhängige Claude-Agenten, nur lesend. Nicht umgehen (Regel 12).
- **HIP-Startfehler** „No HIP GPUs are available“ bei 12–14 gleichzeitigen GPU-Prozessen: ≤ 10 halten, betroffene Läufe mit weniger Workern neu.
- **`lab/confirm/rank_tools.py` NICHT ändern** (Code-Tore C1–C4). C1/C2-Selbsttests nur über `lab/confirm/C12_selftest_wrapper.py`.
- Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`). Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- `--analyze`/`analyze.py` brauchen `PYTHONIOENCODING=utf-8` (Bash-Syntax; in PowerShell `$env:PYTHONIOENCODING='utf-8'`). Auswertungen und Selbsttests laufen mit dem globalen Python über den Wächter; `.venv-gpu` nur für die Trainer-Jobzeilen. Jobdateien per `--jobs` ohne Wächter erzeugen (sonst landen `[guard]`-Zeilen darin).
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung (`--stop-after-gen`); `group_train.py` läuft voll.
- Gelegentlich WinError 5 bei `os.replace` von result.json: Queue neu starten genügt.
- Globales Python ohne scipy. Uhrzeiten nur gemessen (Python zoneinfo).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`, `lab/paper/outreach/`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen.
- Eine Runner-Sitzung endet mit der Antwort: laufende Jobs im Vordergrund beobachten, nie „Wecker stellen und aufhören“.
- **Trainer eingefroren bis Ende L0** (Pilot, Switch, Bestätigung): `freq_ban.py` nicht ändern (R11 ist fertig; L0-Läufe vergleichen gegen denselben Trainer). Ressourcen: GPU-Prozesse zusammen ≤ 10, CPU-Threads zusammen ≤ 12 (jeder GPU-Prozess zählt 1).

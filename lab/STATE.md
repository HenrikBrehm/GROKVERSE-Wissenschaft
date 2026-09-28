---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 01:23 Berlin (Sitzung 46 läuft, Deadline 03:49) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (inkl. D₅₉; Nanda restricted/excluded 20/20 in allen vier Aufgaben, unabhängig nachgerechnet), K4–K4e, R2–R10, K5, **R11 neu (Sitzung 46): Festlegung 25–50 Schritte auch bei add 97 und mul 113, alle 6 bestätigt, nachgerechnet.**
- **Abgeschlossen Sitzung 46:** EXP-101 (RFM) Tor nicht bestanden auch mit 60 Iterationen (0.63–0.88) → keine K2-Lesart in RFM. L0-Machbarkeit: B 256 keine Reihenfolge-Wirkung, B 64 knapp (Regel → `CONFLICT_B64 = True`), B 16 Netz lernt nicht (kein B16-Konfliktarm). SGD-Kalibrierung ohne Treffer → `SGD_DROPPED = True`. Vorab-Maskenvorhersage „unclear“.
- **Paper:** [[paper/draft]] neu §3.16 (R10) und §3.17 (R11), §6-Grenze eingeschränkt. [[paper/draft_short]] noch ohne R11-Satz (nächster Schritt). Tägliche [[paper/erklaerung/ERKLAERUNG_2026-09-29]] fortgeschrieben.

## Aktive Queue / laufende Jobs (Stand 01:23)

- **L0-Pilot** ([[experiments/EXP-100-set-vs-order/README|EXP-100]], 128 Läufe, GPU): `jobs_part1.txt` (64) läuft mit 5 Workern seit 01:21 (Log /tmp/l0p1_pq.log → `lab/runner/logs/pq_*`); `jobs_part2.txt` (64) startet automatisch nach der B16-Sonde (Kette in einer Hintergrund-Bash). **Wiederaufnahme nach Sitzungsende:** gleiche Befehle `python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/jobs_partN.txt --workers 5` erneut (fertige Läufe werden übersprungen; `run.lock` ohne result prüfen). Ausgabe `raw/`, `raw_fb30k/`.
- **B16-Sonde** (`b16probe.txt`, 18 Läufe, `raw_b16probe_v1..v3`): v1 (Wurzelregel) lernt nicht (Training 0.28–0.44); v2/v3 laufen. Lesart in der README (Zusatz B = 16-Sonde).
- Keine CPU-Jobs.

## Nächste Schritte (Regel 20)

1. L0-Pilot fertig → `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/analyze.py` → Ergebnis in README/JOURNAL/FINDINGS; Deutung nur nach [[paper/L0_DEUTUNGEN]]. Unabhängige Nachrechnung (Agent).
2. Danach `switch.txt` (64 Läufe, Wechsel bei 25/50 unter Minibatch) → `switch_analyze.py`.
3. L0-Registrierung ([[confirm/L0_REGISTRATION_DRAFT|L0]], Seeds 3720–3799): n aus der Pilotstreuung (Power ≥ 80 %), Prüfung, Einfrieren, Block.
4. B16-Sonde auswerten (README-Lesart); lernt eine Variante: eigener B16-Konfliktversuch neu festlegen (BACKLOG Sitzung 46).
5. Paper: R11-Satz in [[paper/draft_short]] (Kernaussage 3), L0-Ergebnis, Zenodo-Pfade (7 Repro-Dateien mit absolutem Benutzerpfad).
6. EXP-103 (Füllarbeit, niedrige Priorität): Teil B Job 24 erneut, Teil A (`jobs.txt`), Auswertung.
7. Ab ≈ Fr 02.10.: Sprachmodell-Leiter (EXP-102 Stufe 1, Trainer ungetestet).

## Prioritäten

1. **L0** (Pilot läuft) → Registrierung → Bestätigung.
2. **Paper** ≤ 8 Seiten (R11 in Kernaussage 3, L0), Zenodo-Paket; tägliche ERKLAERUNG.
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

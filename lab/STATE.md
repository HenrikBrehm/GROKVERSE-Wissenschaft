---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-28, 18:35 Berlin (Sitzung 43, Fenster zu; Läufe ab 29.09. 00:00–13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Sitzung 43 hat STATE gekürzt (Astra-Punkt 17). Die alten Abschnitte „Lage“ und „Nächste Schritte“ der Sitzungen 26–42 stehen unverändert in den Abschlussberichten im [[JOURNAL]] und in `git show 7f9d56d4:lab/STATE.md`. Alle dort genannten Nachtschritte vom 28.09. (P2f, R1–R9, EXP-018 … EXP-095, Repro-Paket) sind erledigt.*

## Lage

- **Bestätigt (Kernaussagen, [[FINDINGS]]):** K2 (Split steuert Frequenzen, 4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (inkl. D₅₉), K4–K4e (Festlegung in 25–50 Schritten, Reset-Rollen), R2–R9 (Robustheit, Wechselkosten, Zufallssplit, Uhr), **K5** (Festlegung tickt in Λ bei in Λ gemessenen β-Fenstern, R9).
- **Neueste Exploration:** [[experiments/EXP-095-gradient-feedback/README|EXP-095]] „Auswertungen zählen“: Bei 24 Adam-Schritten legen 3 Gradientenauswertungen so schwach fest wie 3 große Schritte (e8 +0.141 [0.060, 0.211]). Nur der Anfangsgradient bewegt W_E weiter, aber unselektiver (Nicht-Ziele ×1.48, post hoc).
- **Paper:** [[paper/draft]] §1–§5 mit allen Bestätigungen; Repro-Paket vollständig (9/9 Skripte reproduzieren); One-Pager fertig. Offene Nutzerentscheidungen in [[paper/STATUS]].

## Aktive Queue / laufende Jobs

- **Keine Prozesse** (Sitzung 43, 18:21 geprüft).
- **R10 halb gerechnet:** eingefroren 7b583bdb (n = 48, Seeds 3500–3547, 480 GPU-Läufe). 268/480 gebunden (r10_raw/r10_bindings), 0 Fehler, Wächterstopp 17:52 regulär. **Ergebnisse ungesehen, nicht ansehen vor 480/480.**
- **EXP-096 vorbereitet** (add 97 / mul 113, 160 GPU-Läufe, Seeds 3560–3575): Splits/Jobs/Smoke erzeugt und committet (a3bd9415, Sitzung 43). Selbsttest steht noch aus.

## Nächste Schritte (Nacht 29.09., ab 00:00; alles über guarded_run.py bzw. parallel_queue.py)

1. `python lab/tools/guarded_run.py --check`; kein STOP; Prozesse prüfen (`tasklist | grep -i python`). In `lab/confirm/r10_raw/` nach `run.lock` ohne `result.json` suchen (Wächterstopp): beiseitelegen (umbenennen `.stale_s42`), nicht löschen.
2. **R10 fertig:** `python lab/tools/parallel_queue.py lab/confirm/R10_jobs.txt --workers 8` (im Hintergrund; gebundene Läufe werden übersprungen; ≈ 212 Läufe, grob 30–40 min). GPU-Prozesse insgesamt ≤ 10 (HIP-Startfehler bei 12–14).
3. **Parallel dazu (≤ 2 weitere GPU-Worker):** EXP-096-Selbsttest `python lab/tools/guarded_run.py -- python lab/experiments/EXP-096-gradient-feedback-tasks/analyze.py --selftest`, Smoke `parallel_queue.py .../smoke.txt --workers 2`, dann `analyze.py --smoke-check` über den Wächter. Der Block (`jobs.txt --workers 8`) läuft erst nach R10.
4. Nach 480/480: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r10.py --analyze lab/confirm/R10_manifest.json`. Ergebnis in [[confirm/R10_REGISTRATION_DRAFT|R10]], FINDINGS (K6-Kandidat), Paper §3.16 (falls bestätigt; sonst §4), unabhängig nachrechnen lassen.
5. EXP-096-Block, dann `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-096-gradient-feedback-tasks/analyze.py`.
6. Danach: vorbereiteten Folgeversuch aus Sitzung 43 prüfen (Anzahl gegen Abstand der Auswertungen, siehe JOURNAL Sitzung 43 / [[NOVEL_DIRECTIONS]]).

## Prioritäten (Regel 18c + 19)

1. **B/K5-Linie:** R10 (Bestätigung EXP-095) und EXP-096 (Verallgemeinerung, Regel 15c).
2. **Paper:** R10 → §3.16/§4; Literatur zu „frische Gradienten“ (Sitzung 43) in [[paper/related_work]].
3. **C** ruht (EXP-076: einfachste AGF-Brücke negativ).

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit Sitzung 33). Ersatz: unabhängige Claude-Agenten, nur lesend. Nicht umgehen (Regel 12).
- **HIP-Startfehler** „No HIP GPUs are available“ bei 12–14 gleichzeitigen GPU-Prozessen: ≤ 10 halten, betroffene Läufe mit weniger Workern neu.
- **`lab/confirm/rank_tools.py` NICHT ändern** (Code-Tore C1–C4). C1/C2-Selbsttests nur über `lab/confirm/C12_selftest_wrapper.py`.
- Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`). Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- `--analyze`/`analyze.py` brauchen `PYTHONIOENCODING=utf-8`. Jobdateien per `--jobs` ohne Wächter erzeugen (sonst landen `[guard]`-Zeilen darin).
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung (`--stop-after-gen`); `group_train.py` läuft voll.
- Gelegentlich WinError 5 bei `os.replace` von result.json: Queue neu starten genügt.
- Globales Python ohne scipy. Uhrzeiten nur gemessen (Python zoneinfo).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`, `lab/paper/outreach/`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen.
- Eine Runner-Sitzung endet mit der Antwort: laufende Jobs im Vordergrund beobachten, nie „Wecker stellen und aufhören“.

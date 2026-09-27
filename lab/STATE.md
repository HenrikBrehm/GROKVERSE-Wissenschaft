---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 11:55 Berlin (Sitzung 23, Start 09:39, Deadline 12:39; nächster Runner-Start 13:14 Berlin = außerhalb des Fensters)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · Bestätigungen [[confirm/N29_REGISTRATION|N29]] · [[confirm/P2e_REGISTRATION|P2e]] · [[confirm/N29b_REGISTRATION|N29b]]

## Lage (Sitzung 23)

- **N29 bestätigt** (087e042, 20 frische Seeds): Ablationskontrast kehrt sich zwischen Wechsel bei t = 25 (neue gebraucht, 0.60 [0.50, 0.70]) und t = 50 (alte gebraucht, 0.90 [0.85, 0.95]) um. FINDINGS „K4c“.
- **P2e bestätigt** (3c484ef): P2d-Maß bei mul 113 (0.291) und add 97 (0.294), je 20/20. FINDINGS, eng: keine Nutzung über die Energie hinaus belegt.
- **Grenze aller Funktionsbefunde** (EXP-064 post hoc, [[experiments/EXP-068-matched-sensitivity/README|EXP-068]]): Ablation folgt der W_E-Energie; bei gleicher entfernter Energie kein Vorteil der dominanten Menge.
- **N29b bestätigt** (db31564, Seeds 2300–2319): Attention-Reset (Gewichte + AdamW-Zustand) beim Wechsel bei t = 50 senkt den Ablationskontrast um 1.49, stärker als MLP-Reset (1.42); FINDINGS „K4d“ (Reset-Empfindlichkeit).
- Piloten: EXP-067 (Attention, nicht MLP/W_U), **EXP-069** (Wertepfad W_V/W_O trägt den Ausschluss, Muster unklar), **EXP-070** (OV-Ausrichtung steigt gleichmäßig, kein Sprung bei 25–50) → [[NOVEL_DIRECTIONS]] N32.
- EXP-039 *unklar* (Λ-Uhr passt besser als Schrittuhr). EXP-040: Auswertungsfehler vor jedem Lauf behoben (Nachtrag d), noch nicht gelaufen.
- Codex war 11:04–11:45 ohne Guthaben; seit 11:45 wieder verfügbar, alle offenen Prüfungen der Sitzung nachgeholt.

## Aktive Queue / laufende Jobs

- **GPU: N29c-Block** (eingefroren 3c9cb63, Seeds 2320–2339, 120 Läufe) ab 12:00: `python lab/tools/parallel_queue.py lab/confirm/N29c_jobs.txt --workers 7` (Log `lab/runner/logs/n29c_block.log`).
  Nicht fertig bis 12:39 → **im nächsten Fenster** derselbe Befehl (gebundene Läufe werden übersprungen, abgebrochene beiseitegelegt), dann
  `python lab/tools/guarded_run.py -- python lab/tools/confirm_n29c.py --analyze lab/confirm/N29c_manifest.json`, danach Codex zur Schlussfolgerung.
- **CPU:** `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-036,EXP-039,EXP-040,EXP-042,EXP-014` (EXP-036/039 fertig, EXP-040 am Selbsttest gescheitert und inzwischen repariert,
  EXP-042 lief ab 10:59). Wiederaufnahme im Fenster: derselbe Befehl, EXP-040 zusätzlich einzeln (`--experiments EXP-040`).

## Nächste Schritte (in dieser Reihenfolge)

1. `guarded_run.py --check`; kein STOP; Prozesse prüfen. **Außerhalb des Fensters (13:00–00:00) keine Läufe.**
2. **Programm B, N32:** Bestätigung „Wertepfad“ = [[confirm/N29c_REGISTRATION|N29c]] (eingefroren, läuft/fortsetzen, s. oben). Offene Mechanismusfrage: Warum entsteht der Ausschluss zwischen 25 und 50, wenn die OV-Ausrichtung gleichmäßig steigt (EXP-070)? Kandidaten vorab benennen
   (z. B. Schwelle der OV-Verstärkung gegen die Init-Amplitude neuer Richtungen; Adam-Zustand des Wertepfads).
3. **Programm A, D₅₉:** Registrierung „P2f“ (Irrep-Maß, `group_train.py --save-model` vorhanden seit Sitzung 23, noch ohne Codex-Prüfung), frische Seeds (2290–2299 frei oder neuer Block).
4. FINDINGS straffen (Regel 15a: höchstens eine Seite; derzeit weit darüber): Kernaussagen K2, K2-Funktion (P2d/P2e), K4/K4b/K4c, Grenze „Funktion folgt Energie“, offene Frage N32.

## Drei Prioritäten (Regel 18c)

1. **B** Persistenz: Ort des Festhaltens (N29b → N32: Attention).
2. **A** Verallgemeinerung: D₅₉ (nicht-abelsch) für das Funktionsmaß.
3. **C** ruht.

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit 11:04). Kernaussagen in FINDINGS brauchen eine Codex-Prüfung (Regel 18c).
- `freq_ban.py` hat seit 5d84666 `--reset-at-switch attn|mlp|unembed`. Eingefrorene Blöcke (P1, P2d, N28, N29, P2e) prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`).
- Speicher: höchstens ≈ 8–10 GPU-Prozesse gleichzeitig neben dem CPU-Programm.
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung: bei langen Läufen `--stop-after-gen` ≥ Schritte.
- Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht (P2b, P2e: zweimal hat er einen Fehler gefunden).
- Zwei Warteschlangen über dieselbe Liste: Exit 4 am Treffpunkt (`run.lock`) ist erwartet.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**; immer einzelne Pfade.
- Python `write_text` schreibt unter Windows CRLF: Code-Dateien nach Skript-Änderungen auf LF prüfen (Sitzung 23 einmal passiert, behoben).
- Uhrzeiten nur gemessen (Sitzung 23 mehrfach geschätzt und korrigiert). venv-Python mit absolutem Pfad. JOURNAL/STATE/FINDINGS CRLF.

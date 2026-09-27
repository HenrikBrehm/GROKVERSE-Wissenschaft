---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-27, 08:10 Berlin (Sitzung 22 läuft seit 06:59, Deadline 09:59)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · Bestätigungen [[confirm/P1_REGISTRATION_DRAFT|P1]] · [[confirm/P2_REGISTRATION_DRAFT|P2]] · [[confirm/P3_REGISTRATION_DRAFT|P3]]

## Lage (Sitzung 21)

- **Bestätigungsfamilie gerechnet** (alle vorab eingefroren, Läufe an den Code gebunden, Schlussfolgerungen von Codex geprüft):
  **P1 bestätigt** in 4/4 Aufgaben (je 50/50; add 113 Δ_pow 8.24 [7.92, 8.54]). **P2 nicht auswertbar** (3/50 Modelle bei Schritt 2000 nicht generalisiert).
  **P3 bestätigt** (D̄ 0.293 [0.263, 0.322], 30/30): starke Wirkung einer 25-Schritt-Vorgeschichte gegen paar-disjunktes Weitertraining. „Festlegung im Netz“ ist damit **nicht** identifiziert.
- Piloten dieser Sitzung: EXP-035 (Warmup verzögert, n = 3), EXP-038 (Festlegung doppelt vorhanden, 5/5), EXP-056 (Persistenz ohne geteilte Paare), **EXP-057 (volle Optimierer-Neuinit beim Wechsel
  senkt die A-Persistenz: π 0.30 → 0.11)** und **EXP-058 (nur das Momentum m löschen senkt π genauso, 0.12, bei kleineren frühen Schritten → das Überschreiben erklärt es nicht;
  das Momentum der ersten 25 Schritte trägt den größten Teil)** → Kandidat N28 (Pilot, bekannte Seeds 400–409).
- **Achtung Reproduktion:** `freq_ban.py` wurde nach dem Einfrieren geändert (5aa8c34, Option `--reset-optim-at-switch`). Eine erneute Auswertung von P1/P2/P3 besteht die Code-Prüfung
  nur aus einem Checkout von 733e829 bzw. f8adf45. Die Ergebnisse sind committet (4f3fc36, e5f55a5).

## Aktive Queue / laufende Jobs

- **CPU (Sitzung 22, seit 07:00, 3 × 4 Threads):** `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1`
  (EXP-035/038/041 fertig). Die Sitzungsdeadline bricht ab (kein Fehler). **Wiederaufnahme: derselbe Befehl.**
- **GPU, Bestätigungsfamilie Sitzung 22 (alle EINGEFROREN):**
  [[confirm/N28_REGISTRATION|N28]] (fa154bd, seit 07:34): `python lab/tools/parallel_queue.py lab/confirm/N28_jobs.txt --workers 5 > lab/runner/logs/n28_block.log` (300 Läufe).
  [[confirm/P2c_REGISTRATION|P2c]] (e8e0cfa, seit 08:10): `python lab/tools/parallel_queue.py lab/confirm/P2c_jobs.txt --workers 3 > lab/runner/logs/p2c_block.log` (200 Läufe à 4000 Schritte; wird erst in der nächsten Sitzung fertig).
  **P2b ABGEBROCHEN** (Designfehler: Trainer-Standard `--stop-after-gen 2000` beendete die Läufe vor 4000; nicht auswertbar, nicht wieder starten).
  **Wiederaufnahme: dieselben Befehle** (gebundene Läufe werden übersprungen; unvollständige Ordner werden beiseitegelegt; bei `run.lock` von Hand prüfen).
  **Speicher:** höchstens ≈ 8–10 GPU-Prozesse gleichzeitig (07:53 zwei Startfehler bei 12: `bad allocation` / WinError 1455, Auslagerungsdatei).
- **GPU, Pilot [[experiments/EXP-063-exclusion-locus/README|EXP-063]]** (4ea5d56): `parallel_queue.py lab/experiments/EXP-063-exclusion-locus/jobs.txt --workers 2`; Job 2 scheiterte am Speicher → danach mit demselben Befehl nachholen (freq_ban überspringt fertige).
- **Vorab festgelegte Vorhersage** an den N28-Seeds (2bdfdaf): `guarded_run.py -- python lab/confirm/n28_regimes.py` nach dem N28-Block.
- **Auswertung danach:** `python lab/tools/guarded_run.py -- python lab/tools/confirm_n28.py --analyze lab/confirm/N28_manifest.json`, ebenso `confirm_p2b.py … P2b_manifest.json`.

## Nächste Schritte (in dieser Reihenfolge)

1. `guarded_run.py --check`; kein STOP; Prozesse prüfen; laufende Blöcke (oben) nicht doppelt starten, sondern mit demselben Befehl fortsetzen.
2. N28, n28_regimes und (wenn fertig) P2c auswerten (Befehle oben), Ergebnis in die Registrierungen, FINDINGS, LAB; vor einer Kernaussage in FINDINGS Codex die Schlussfolgerung prüfen lassen.
3. Programm B weiter: **was** macht die Wahl in ≈ 50 Schritten so fest (EXP-059: π 0 → 1 zwischen t = 10 und 50)? Kandidaten vorab festlegen.
4. CPU-Auswertungen nach den Läufen: EXP-036, EXP-039 (`eval_pi.py`), EXP-040, EXP-042 (`pi_window.py`), EXP-014.

## Drei Prioritäten (Regel 18c)

1. **B** Persistenz: N28 (eng: m-Reset senkt π, 10 A-Schritte gleichen aus; EXP-059) läuft als Bestätigung; danach Ursache der steilen Festlegung.
2. **A** Funktion: P2c (ersetzt das abgebrochene P2b; 100 frische Seeds 2100–2199, genau 4000 Schritte) läuft.
3. **C** ruht (höchstens zwei Programme aktiv).

## Blocker / Hinweise

- Codex: direkt `node …/codex-companion.mjs task "<prompt>"` (Vordergrund, als Bash-Hintergrundbefehl). Die Weiterleitung `codex:codex-rescue` hat einmal nur im Hintergrund gestartet.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**.
- venv-Python nur mit absolutem Pfad (`C:/Users/…/.venv-gpu/Scripts/python.exe`). CPU-Läufe mit dem globalen Python.
- Zeitstempel nur aus `guarded_run.py --check`. JOURNAL/STATE/LIVE/FINDINGS CRLF (bytegenau bearbeiten).
- Eigene Prüfungen am echten Codepfad testen (Sitzung 21: dreimal eine Prüfung, die nicht das Laufende prüfte).

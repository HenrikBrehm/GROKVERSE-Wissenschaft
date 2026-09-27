---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-27, 06:51 Berlin (Sitzung 21 beendet; nächster Start 07:54 Berlin)._

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

- **CPU (seit 04:20, 3 Arbeiter × 4 Threads):** `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-035,EXP-038,EXP-041,EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1`.
  EXP-035 und EXP-038 fertig, danach EXP-041 … (≈ 250 Läufe à ≈ 5 min, mehrere Sitzungen). Die Sitzungsdeadline bricht ab (kein Fehler). **Wiederaufnahme: derselbe Befehl.**
- **GPU:** frei.

## Nächste Schritte (in dieser Reihenfolge)

1. `python lab/tools/guarded_run.py --check`; kein STOP; Prozesse prüfen; CPU-Programm (oben) wieder starten.
2. (erledigt 06:31: Codex hat 5aa8c34 als korrekt bestätigt, die EXP-057-Deutung ist korrigiert.)
3. **N28 bestätigen (Programm B):** EXP-058-Design (normal / nur m / voller Reset, `--log-update-norms`) als Bestätigung an **frischen** Seeds einfrieren (neuen Seed-Bereich reservieren,
   z. B. 2200–2299, eigene Splits über EXP-053 `overlap_split`), dazu Richtungsanalyse (Kosinus der Updates) und t = 50/150 als Folgefragen. Vorher Codex (Regel 18c).
4. **P2-Nachfolger** ([[BACKLOG]] „P2-Nachfolger“): frische Seeds, sicheres Grokking, feste Ablations-Testmenge, N aus der gesehenen Streuung (≈ 60–80).
5. Auswertungen nach den CPU-Läufen (über den Wächter): EXP-041, EXP-036, EXP-039 (`eval_pi.py`), EXP-040, EXP-042 (`pi_window.py`), EXP-014.

## Drei Prioritäten (Regel 18c)

1. **B** Persistenz: N28 (Momentum trägt die frühe Persistenz) an frischen Seeds bestätigen.
2. **A** Funktion: P2-Nachfolger.
3. **C** ruht (höchstens zwei Programme aktiv).

## Blocker / Hinweise

- Codex: direkt `node …/codex-companion.mjs task "<prompt>"` (Vordergrund, als Bash-Hintergrundbefehl). Die Weiterleitung `codex:codex-rescue` hat einmal nur im Hintergrund gestartet.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**.
- venv-Python nur mit absolutem Pfad (`C:/Users/…/.venv-gpu/Scripts/python.exe`). CPU-Läufe mit dem globalen Python.
- Zeitstempel nur aus `guarded_run.py --check`. JOURNAL/STATE/LIVE/FINDINGS CRLF (bytegenau bearbeiten).
- Eigene Prüfungen am echten Codepfad testen (Sitzung 21: dreimal eine Prüfung, die nicht das Laufende prüfte).

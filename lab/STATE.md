---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 09:35 Berlin (Sitzung 22, Deadline 09:59; nächster Runner-Start laut runner-state.json 10:34 Berlin)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · Bestätigungen [[confirm/N28_REGISTRATION|N28]] · [[confirm/P2c_REGISTRATION|P2c]] · [[confirm/P3_REGISTRATION_DRAFT|P3]]

## Lage (Sitzung 22)

- **N28 bestätigt** (fa154bd, 30/30 frische Seeds): Das Nullsetzen von Adams erstem Moment beim Wechsel senkt den Persistenzindex π um 0.15. Zehn zusätzliche Vorschritte gleichen das aus
  (Nichtunterlegenheit). Enger Wortlaut nach Codex in [[FINDINGS]] („K4b“). Die „Adam-Gedächtnis“-Deutung aus Sitzung 21 ist herabgestuft (EXP-059: verlängerte Exposition genügt).
- **Zwei Spektralsignaturen** (EXP-062): Die Vorhersage an den N28-Seeds ist erfüllt (29/30, 30/30). Bei t = 25 überschüssige alte Energie, bei t = 50 fehlende neue Energie.
  **Funktional (EXP-064, beschreibend, nicht auswertbar 7/10):** Bei t = 25 rechnet das Netz mit den **neuen** Frequenzen (Umstieg), bei t = 50 nur mit den alten (Festhalten, 10/10).
- EXP-063 (Pilot): Ein Reset des Rests oder von W_E bei t = 50 verkleinert das Defizit der neuen stark. EXP-060, EXP-061: zwei Mechanismusideen verworfen.
- **P2b abgebrochen** (mein Designfehler: Trainer-Standard `--stop-after-gen 2000`). **P2c nicht bestätigt** (R̄ −0.108 [−0.149, −0.070], 99/100): Funktionale Nutzung ist mit dem P2-Maß nicht belegt.

## Aktive Queue / laufende Jobs

- **CPU:** `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1`
  (EXP-035/036/038/041 fertig, EXP-039 läuft). Die Sitzungsdeadline bricht ab (kein Fehler). **Wiederaufnahme: derselbe Befehl.**
- **GPU:** frei. N28, P2c, P2d, EXP-059…065 fertig und ausgewertet.

## Nächste Schritte (in dieser Reihenfolge)

1. `guarded_run.py --check`; kein STOP; Prozesse prüfen; CPU-Programm (oben) neu starten.
2. **Programm B, Bestätigung des funktionalen Übergangs** (EXP-064 → frisch): Wechsel bei 25 und 50, **sicheres Nachtraining** (z. B. 4000 Schritte nach dem Wechsel, `--stop-after-gen` ≥ Schritte),
   `--save-model`, Ablation alt/neu am Endmodell, vorab festgelegte Regel für nicht generalisierte Modelle, frischer Seed-Block (2250–2299 frei). Vorher: **ein echter Job bis zum Ende durch den
   eingefrorenen Lader** (Lehre aus P2b) und Codex-Prüfung. Infrastruktur: `lab/tools/bound_block.py` (+ Muster `confirm_n28.py`).
3. **Programm A:** P2d **bestätigt** (D̄ 0.250 [0.229, 0.270], 20/20; Wortlaut nach Codex in [[FINDINGS]]). Nächste Frage: gilt das in anderen Aufgaben (P1-Aufgaben mul 113, add 97, D₅₉)?
4. N29-Ursache ([[BACKLOG]]): welcher Teil des Rests (Attention/MLP/Unembedding), Weight Decay (K1, braucht Trainer-Option + Codex).
5. CPU-Auswertungen nach den Läufen (EXP-036 erledigt: init-getrieben): EXP-039 (`eval_pi.py`), EXP-040, EXP-042 (`pi_window.py`), EXP-014.

## Drei Prioritäten (Regel 18c)

1. **B** Persistenz: funktionaler Übergang Umstieg → Festhalten zwischen t = 25 und 50 bestätigen.
2. **A** Funktion: P2d bestätigt → Verallgemeinerung auf die anderen P1-Aufgaben.
3. **C** ruht (höchstens zwei Programme aktiv).

## Blocker / Hinweise

- **Speicher:** höchstens ≈ 8–10 GPU-Prozesse gleichzeitig neben dem CPU-Programm (07:53 zwei Startfehler bei 12: `bad allocation`, WinError 1455; freier virtueller Speicher ≈ 3 GB).
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung: bei `--steps` > gen + 2000 immer `--stop-after-gen` ≥ Schritte setzen.
- Zwei Warteschlangen über dieselbe Jobliste (vorwärts/rückwärts) funktionieren mit `bound_block` (Exit 4 am Treffpunkt ist erwartet).
- Codex: direkt `node …/codex-companion.mjs task "<prompt>"` (als Bash-Hintergrundbefehl, wartet auf das Ergebnis).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**;
  nie `git add -u lab` (Sitzung 22 einmal passiert, sofort mit `reset --soft` zurückgenommen), immer einzelne Pfade.
- venv-Python nur mit absolutem Pfad. Zeitstempel nur aus `guarded_run.py --check` (Sitzung 22 mehrfach geschätzt, korrigiert). JOURNAL/STATE/LIVE/FINDINGS CRLF.
- Rohdaten der neuen Blöcke per `lab/confirm/.gitignore` ausgeschlossen; Bindungen werden committet.

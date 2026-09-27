---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-27, 03:46 Berlin (Sitzung 20, Deadline 04:29)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · [[LESART-nacht-2026-09-27]] · [[confirm/P1_REGISTRATION_DRAFT|P1-Entwurf]]

## Lage

- Nacht 26./27.09. (Regel 18b) **erledigt**: Wächter-Abnahme A/B/C bestanden, alle Tests grün, **GPU-001 bestanden** (gleichwertig, ≈ 17× schneller, J = 8).
  GPU-Programm komplett: EXP-043, 044, 045, 046, 047, 048, 049, 050, 051 und die Auswertungen 052, 055. Ergebnisse: [[FINDINGS]] „Pilotnacht“ (K2 und K4 verallgemeinern sich im Pilot).
- Run-Fenster wieder normal 00:00–13:00 (die 03:00-Sperre gab es nur in der Nacht 26./27.09.; der Nutzer hat sie 02:25 aufgehoben).
- Schritte 1–3 (Abnahme, Tests) **nicht wiederholen**. Das Archiv des Ablaufs steht im [[JOURNAL]] (STATE-Archiv Sitzung 20).

## Aktive Queue / laufende Jobs

- **CPU (seit 02:56, 1 Arbeiter × 4 Threads):** `python lab/tools/night_program.py --cpu --experiments EXP-035,EXP-038,EXP-041,EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1`.
  ≈ 5 min je Lauf, noch mehrere Fenster. Die Sitzungsdeadline bricht ab (Exit 124/3 = Ablehnung, kein Fehler). **Wiederaufnahme: derselbe Befehl** (Fertiges wird übersprungen).
  Mit freier GPU kann der Arbeiter mehr Threads bekommen: `--cpu-workers 3` (Threadsumme ≤ 12). Nicht mischen (Regel 16d): Die CPU-Versuche bleiben auf der CPU.
- **GPU:** frei. Kein offenes GPU-Programm.

## Nächste Schritte (in dieser Reihenfolge)

1. `python lab/tools/guarded_run.py --check`; kein STOP; laufende Prozesse prüfen (`ps -ef | grep -E "night_program|guarded_run"`); dann das CPU-Programm (oben) wieder starten.
2. **P1 einfrieren** ([[confirm/P1_REGISTRATION_DRAFT|Entwurf]]): Codex-Befunde B1–M9 umgesetzt (Commits 48e7afb … b750fb1). Die Nachprüfung durch Codex läuft bzw. steht im [[JOURNAL]] (Sitzung 20).
   Dann: `python lab/tools/confirm_splits.py --hash-code` → Feld `code_sha256` in `lab/confirm/P1_manifest.json` (aus dem Entwurf, `primary_task` add113, Seeds 1000–1049),
   committen, `commit` eintragen, wieder committen; `confirm_splits.py --manifest …`; `confirm_p1.py --jobs … > lab/confirm/P1_jobs.txt`; `parallel_queue.py lab/confirm/P1_jobs.txt --workers 8`
   (GPU, ≈ 400 Läufe, Minuten); `confirm_p1.py --analyze …`. Vorher lesen: „bereits gesehen“ im Entwurf.
3. **P2** nach EXP-051/055: Registrierung mit ΔL bei Teildosis f = 0.5 an frischen Modellen ([[BACKLOG]] „P2-Maß“), Seeds 1050–1099 oder neue Pilot-Seeds.
4. Auswertungen nach den CPU-Läufen (eingefroren, über den Wächter): EXP-039 `eval_pi.py`; EXP-054 `n30_window.py` (nach EXP-036); EXP-042 `pi_window.py` (je erst `--selftest`).
5. P3 schärfen (t = 25 primär, π, Überlappung EXP-053). EXP-044 stützt Lesart (i): Festlegung im Netz.
6. Offene Reste: EXP-046 beschreibende Zusätze (Top-3, Δ_pow); Folgeversuch EXP-050 (MLP mit getrennten W_in-Hälften); D₅₉/int-add Häufigkeits-Mischarm.

## Drei Prioritäten (Regel 18c: Programm A/B/C)

1. **A** Bestätigung P1 (Block 1000–1049), funktional P2 (Loss-Maß).
2. **B** Persistenz: CPU-Piloten EXP-035–042 fertig rechnen, P3 festlegen.
3. **C** läuft gut (EXP-052 4/4, EXP-050): erst nach A/B weiter, höchstens zwei Programme aktiv.

## Blocker / Hinweise

- **Windows/venv:** `CreateProcess` findet `.venv-gpu/Scripts/python.exe` (relativ, Schrägstriche) nicht. `night_program.py` nutzt den absoluten Pfad, `confirm_p1.interp()` einen absoluten Pfad mit Schrägstrichen.
- Die CPU-torch der `.venv-gpu` ist für CPU-Läufe ≈ 10× zu langsam. CPU-Läufe nur mit dem globalen Python.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`,
  `runner-state.json`, `parallel_queue.py`) **nicht committen**; nur gezielt `git add <pfad>`, nie `commit -a`.
- `guarded_run.py` (Nutzer, 27.09. ≈ 01:30/02:35): Der Wächter tritt vor dem Kindstart dem Job-Objekt bei, argtypes korrigiert. Seitdem keine Warnung mehr.
- Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`). Shell-Skripte LF, JOURNAL/STATE/LIVE CRLF (bytegenau bearbeiten).
- Neue `freq_ban.py`-Argumente nur bei Abweichung vom Standard in den Fingerprint (Sitzung 16).
- Sitzungsgrenze: Ein abgebrochener Job am Deadline-Ende ist kein Fehler (Exit 124 → Ablehnung). Derselbe Befehl setzt fort.
- Codex über den Subagenten `codex:codex-rescue` (nur lesend) funktioniert (Sitzung 20: zweimal).

## Letzte abgeschlossene Versuche (Details [[LAB]], [[FINDINGS]])

- Sitzung 20 (Piloten, je 10 Seeds, vorab festgelegt): EXP-043 (add 97, mul 113), 046 (D₅₉), 048 (int-add), 049 (d 512), 045 (MLP): *steuerbar*; 047: Paarstruktur trägt;
  044: *festgelegt*; 052: K1 4/4; 050: M0c wählt, M0 trägt mit; 051/055: Funktion unklar (Bodeneffekt / Hauptdosis n. s.).

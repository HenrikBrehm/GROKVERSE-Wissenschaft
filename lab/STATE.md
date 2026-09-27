---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 13:21 Berlin (Sitzung 24, Start 12:29, Deadline 15:29; Run-Fenster wieder ab 00:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

## Lage (Sitzung 24)

- **EXP-072 (Pilot):** D₅₉ generalisiert (9/10, erster Test ≥ 0.9 bei Median 4575 Schritten); eigene Irreps 0.90–0.99 der W_E-Energie; Irrep-Funktionsmaß D = 0.22 (5/5, post hoc).
- **EXP-071 (Exploration):** OV-Ausrichtung sagt π je Seed höchstens schwach voraus (r = 0.45, p = 0.09); erklärt den Zeitverlauf nicht besser als die Schrittzahl. Urteil unklar.
- **FINDINGS** auf eine Seite gekürzt; alte Abschnitte wortgleich in [[FINDINGS_DETAILS]].
- **Vorbereitet (Codex geprüft wo Trainer betroffen):** [[experiments/EXP-073-part-rewind/README|EXP-073]] (neues `--rewind-at-switch`), [[experiments/EXP-074-reset-other-tasks/README|EXP-074]].
- **P2f** (D₅₉-Bestätigung) registriert, Code `lab/tools/confirm_p2f.py`, Codex: keine Blocker, 3 kleinere Punkte übernommen. **Nicht eingefroren**: Der Selbsttest nach den Codex-Änderungen
  muss erst im Fenster laufen. Seeds 2340–2359 reserviert (Versuchs-ID 6).

## Aktive Queue / laufende Jobs

- Keine. CPU-Programm wurde um 12:54 vom Wächter am Fensterende gestoppt (Exit 3, erwartet). EXP-042 teilweise, EXP-040 und EXP-014 nicht gestartet.

## Nächste Schritte (ab 00:00, in dieser Reihenfolge; alles über guarded_run.py)

1. `guarded_run.py --check`; kein STOP; Prozesse prüfen.
2. **Trainer-Tests** (neues `--rewind-at-switch`, ungetestet): `python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py`. Scheitert `test_rewind`: EXP-073 nicht starten.
3. **CPU sofort nach den Tests starten, EXP-040 zuerst** (≈ 3 h; direkter Test des Amplitudenmodells H40 für die offene Frage in FINDINGS):
   `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-040,EXP-042,EXP-014` (im Hintergrund).
4. **P2f einfrieren und rechnen** (≈ 30 min): `guarded_run.py -- python lab/tools/confirm_p2f.py --selftest` → Manifest `lab/confirm/P2f_manifest.json` wie P2e (Felder aus `REGISTERED`,
   `python`, `registration`, `code_sha256` aus `--hash-code`), committen, Commit-ID ins Feld `commit`, erneut committen → `--splits` → `--jobs > P2f_jobs.txt` → Smoke: erste Jobzeile allein über
   `parallel_queue` und `--analyze` (Wert nicht ansehen, nur Lader prüfen) → Block `parallel_queue.py lab/confirm/P2f_jobs.txt --workers 10` (12000 Schritte) → `--analyze`.
5. Parallel auf der GPU (nach P2f-Block oder daneben, Speicher beachten): **EXP-073** (140 Läufe) und **EXP-074** (100 Läufe) über `parallel_queue.py`, dann ihre `analyze.py`.


## Drei Prioritäten (Regel 18c)

1. **A** P2f (D₅₉) einfrieren und rechnen.
2. **B** Mechanismus der glatten Festlegung: Konkurrenzmodelle festlegen.
3. **C** ruht.

## Blocker / Hinweise

- `freq_ban.py` hat `--reset-at-switch attn|mlp|unembed|qk|vo`. Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`).
- Speicher: höchstens ≈ 8–10 GPU-Prozesse gleichzeitig neben dem CPU-Programm. 10 D₅₉-Läufe parallel: ≈ 0.03 s/Schritt je Lauf.
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung: bei langen Läufen `--stop-after-gen` ≥ Schritte. `group_train.py` läuft immer die volle Schrittzahl.
- Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- Globales Python hat kein scipy (Sitzung 24): Rangkorrelation selbst rechnen.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen (Sitzung 24 einmal passiert, sofort repariert); Python `write_text` schreibt CRLF in Code-Dateien. Uhrzeiten nur gemessen (Python zoneinfo).

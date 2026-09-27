---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 13:47 Berlin (Sitzung 24, Start 12:29, Deadline 15:29; Run-Fenster wieder ab 00:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

## Lage (Sitzung 24)

- **EXP-072 (Pilot):** D₅₉ generalisiert (9/10, erster Test ≥ 0.9 bei Median 4575 Schritten); eigene Irreps 0.90–0.99 der W_E-Energie; Irrep-Funktionsmaß D = 0.22 (5/5, post hoc).
- **EXP-071 (Exploration):** OV-Ausrichtung sagt π je Seed höchstens schwach voraus (r = 0.45, p = 0.09); erklärt den Zeitverlauf nicht besser als die Schrittzahl. Urteil unklar.
- **FINDINGS** auf eine Seite gekürzt; alte Abschnitte wortgleich in [[FINDINGS_DETAILS]].
- **EXP-076 (Theorie-Rechnung):** M0 ist nicht der AGF-Nutzen erster Stufe (einfachstes Modell) → Brückenvermutung verworfen; Kandidat N34 notiert.
- **Literatur:** Marchetti, Kunin et al. (ICML 2026) erklären die Irrep-Reihenfolge über die Eingabekodierung bei gleichverteilten Daten; K2 (Paarmaske) dort nicht abgedeckt.
- **P2f** hat eine vorab festgelegte Sekundärhypothese S1 (Anteil eigener Irreps bei Schritt 2000 sagt Grokking-Zeit voraus), Codex zweimal nachgeprüft.
- **Vorbereitet (Codex geprüft wo Trainer betroffen):** [[experiments/EXP-073-part-rewind/README|EXP-073]] (neues `--rewind-at-switch`), [[experiments/EXP-074-reset-other-tasks/README|EXP-074]], [[experiments/EXP-075-mlp-lockin/README|EXP-075]] (Festlegung ohne Attention).
- **P2f** (D₅₉-Bestätigung) registriert, Code `lab/tools/confirm_p2f.py`, Codex: keine Blocker, 3 kleinere Punkte übernommen. **Nicht eingefroren**: Der Selbsttest nach den Codex-Änderungen
  muss erst im Fenster laufen. Seeds 2340–2359 reserviert (Versuchs-ID 6).

## Aktive Queue / laufende Jobs

- Keine. CPU-Programm wurde um 12:54 vom Wächter am Fensterende gestoppt (Exit 3, erwartet). EXP-042 teilweise, EXP-040 und EXP-014 nicht gestartet.

## Nächste Schritte (ab 00:00, in dieser Reihenfolge; alles über guarded_run.py)

1. `guarded_run.py --check`; kein STOP; Prozesse prüfen.
2. **Trainer-Tests** (neu, ungetestet: `--rewind-at-switch`, `--lr/--weight-decay/--train-frac`): `python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py`.
   Scheitert `test_rewind`: EXP-073 nicht starten. Danach Selbsttests `confirm_r1.py --selftest` (R1 erst Nacht 28./29.).
3. **CPU sofort nach den Tests starten, EXP-040 zuerst** (≈ 3 h; direkter Test des Amplitudenmodells H40 für die offene Frage in FINDINGS):
   `python lab/tools/night_program.py --cpu --cpu-workers 3 --experiments EXP-040,EXP-042,EXP-014` (im Hintergrund).
4. **P2f einfrieren und rechnen** (≈ 30 min): `guarded_run.py -- python lab/tools/confirm_p2f.py --selftest` → Manifest `lab/confirm/P2f_manifest.json` wie P2e (Felder aus `REGISTERED`,
   `python`, `registration`, `code_sha256` aus `--hash-code`), committen, Commit-ID ins Feld `commit`, erneut committen → `--splits` → `--jobs > P2f_jobs.txt` → Smoke: erste Jobzeile allein über
   `parallel_queue` und `--analyze` (Wert nicht ansehen, nur Lader prüfen) → Block `parallel_queue.py lab/confirm/P2f_jobs.txt --workers 10` (12000 Schritte) → `--analyze`.
5. Parallel auf der GPU (nach P2f-Block oder daneben, höchstens ≈ 10 GPU-Prozesse): **EXP-073** (140 Läufe), **EXP-074** (100), **EXP-075** (120, MLP, sehr schnell) über `parallel_queue.py`,
   dann ihre `analyze.py`. Zusammen erwartet ≈ 45 min GPU.


## Prioritäten (Regel 18c + Regel 19, Veröffentlichung gleichgewichtig)

1. **A** P2f (D₅₉) einfrieren und rechnen; **B** EXP-040/073/074/075 rechnen und auswerten.
2. **Paper** ([[paper/STATUS]]): außerhalb des Fensters (Tag) Trainer-Optionen `--lr/--weight-decay/--train-frac` für [[paper/robustness_plan]] einbauen + Codex; `confirm_p4.py` nach
   [[confirm/P4_REGISTRATION_DRAFT|P4-Entwurf]]; schlanke Repro-Skripte; Literatur [[paper/related_work]] einarbeiten. Offene Nutzerentscheidungen stehen in STATUS.
3. **C** ruht (EXP-076: einfachste AGF-Brücke negativ).

## Blocker / Hinweise

- `freq_ban.py` hat `--reset-at-switch attn|mlp|unembed|qk|vo`. Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`).
- Speicher: höchstens ≈ 8–10 GPU-Prozesse gleichzeitig neben dem CPU-Programm. 10 D₅₉-Läufe parallel: ≈ 0.03 s/Schritt je Lauf.
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung: bei langen Läufen `--stop-after-gen` ≥ Schritte. `group_train.py` läuft immer die volle Schrittzahl.
- Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- Globales Python hat kein scipy (Sitzung 24): Rangkorrelation selbst rechnen.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen (Sitzung 24 einmal passiert, sofort repariert); Python `write_text` schreibt CRLF in Code-Dateien. Uhrzeiten nur gemessen (Python zoneinfo).

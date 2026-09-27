---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 15:22 Berlin (Sitzung 26 läuft, Start 15:09, Deadline 18:09; Run-Fenster wieder ab 00:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

## Lage (Sitzungen 24–25)

- **Sitzung 25 (neu, ungetestet bis 00:00):** `lab/tools/confirm_p4.py` (P4: MLP, d512, Integer-Addition; Seeds 2360–2419, ID 7; Codex: 1 Blocker behoben); `lab/paper/repro/train.py` (schlanker Trainer, Gleichwertigkeitsbefehle in [[paper/repro/README]]); Theorie-Abschnitt §5 im [[paper/draft]]; Seeds 2420–2509 für R1 reserviert.
- **Sitzung 25, Literatur:** Volltextprüfung [[paper/fulltext_check_2026-09-27]]: K4d eingeschränkt (Dong 2026: in Sprachmodellen hilft ein QK-Reset, Value nicht; bei uns umgekehrt), Khanh 2026 Pflichtzitat; K2 weiter nicht gefunden. **EXP-077** (Programm C, Pilot) vorbereitet; `repro/k2.py` geschrieben.

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
   dann ihre `analyze.py`. Schätzung aus den s/Schritt dieser Sitzung: P2f ≈ 25 min (10 parallel, 0.03 s/Schritt), EXP-073 ≈ 18 min, EXP-074 ≈ 13 min, EXP-075 ≈ 5 min,
   GPU zusammen ≈ 1 h nacheinander; CPU (EXP-040 zuerst) ≈ 3 h. Nicht alle GPU-Queues gleichzeitig starten (≤ 10 Prozesse).


6. Nach den GPU-Queues: **EXP-078** (neu, Sitzung 26, Pilot 2-Schicht-Transformer, 20 Läufe ≈ 20 min; erst nach bestandener Gleichwertigkeit von `repro/train.py`, Schritt 7; Befehle in [[experiments/EXP-078-two-layer-steering/README|EXP-078]]) und **EXP-077** (Pilot, 40 Läufe ≈ 5 min): `parallel_queue.py lab/experiments/EXP-077-marginal-steering/jobs.txt --workers 8`, dann `analyze.py` über guarded_run.
7. Nach den Blöcken, falls Zeit (GPU, je ≈ 1–3 min): Selbsttest `confirm_p4.py --selftest`; Repro-Gleichwertigkeit (2 Befehle in [[paper/repro/README]]); neu: `confirm_r2.py --selftest`, `EXP-078/analyze.py --selftest`, Smoke `repro/k4c.py --smoke`. Dazu **EXP-079** (Sekunden, keine Läufe): `guarded_run.py -- python lab/experiments/EXP-079-head-symmetry/measure.py` (Vorbedingung für N36). EXP-080 ist **zurückgestellt** (Designfehler, siehe README) und wird nicht gerechnet. **Die Gleichwertigkeit vor EXP-078 ziehen.** P4 selbst erst Nacht 28./29. (nach Einfrieren; Entwurf `lab/confirm/P4_manifest_DRAFT.json` mit Seeds liegt bereit: `code_sha256` ergänzen, Feld `note` entfernen, als `P4_manifest.json` committen, `commit` setzen).

8. **Neu (Sitzung 26): Rest der Nacht für die Paper-Bestätigungen nutzen.** Die GPU ist nach 1–7 nur ≈ 1–1.5 h belegt. Wenn 1–7 durch sind, alle Selbsttests grün und bis 13:00 noch ≥ 2.5 h bleiben, in dieser Reihenfolge einfrieren und rechnen, je mit Manifest, Commit und Smoke wie P2f: **R1** (`confirm_r1.py`, 180 Läufe ≈ 30 min), **P4** (`confirm_p4.py`, Entwurf `P4_manifest_DRAFT.json`, ≈ 40 min), **R3** ([[confirm/R3_REGISTRATION_DRAFT|R3]], `confirm_r3.py`, Λ- gegen Schrittuhr, 80 Läufe ≈ 17 min; nur nach eingearbeiteter Codex-Prüfung), **R2** ([[confirm/R2_REGISTRATION_DRAFT|R2]], `confirm_r2.py`, 300 Läufe ≈ 45–60 min; Codex ohne Blocker, Punkte eingearbeitet). Nicht mehr als ≈ 10 GPU-Prozesse gleichzeitig. Reicht die Zeit nicht: **R1 vor R3 vor P4 vor R2**, Rest in die Nacht 28./29. Jeder Block braucht vorher seinen Selbsttest (grün) und nach dem Einfrieren einen Smoke-Job.

Vorab-Lesart der Nacht (Kombination EXP-040/073/074/075, P2f): [[LESART-nacht-2026-09-28]].

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

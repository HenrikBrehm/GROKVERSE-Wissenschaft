---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-27, 19:14 Berlin (Sitzung 30, Start 18:19; Run-Fenster wieder ab 00:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

## Lage (Sitzungen 24–30)

- **Sitzung 30 (Fenster zu, 18:19–):** Gutachter-Durchgang durch [[paper/draft]]: 10 Textkorrekturen (Umfang, fehlende Armmittel, Werte nur generalisierter Seeds, LeDoux-Abgrenzung), keine Zahl geändert. Neu vorbereitet: [[experiments/EXP-083-reset-displacement/README|EXP-083]] (Verschiebung ‖W(50) − W(0)‖ je Reset-Teil; 80 × 50 Schritte GPU, ≈ 5 min; Nachtschritt 7). Registrierungsentwurf [[confirm/R4_REGISTRATION_DRAFT|R4]] (Zufallssplit gegen Init, gekreuzt, 60 Einheiten = 240 GPU-Läufe à 8000 Schritte ≈ 1.6 h; ungetestet; Codex-Prüfung Sitzung 30: 1 Blocker + 4 Major eingearbeitet): heute Nacht nur `guarded_run.py -- python lab/tools/confirm_r4.py --selftest`; Codex-Nachprüfung der geänderten Punkte in einer Sitzung ohne Fenster, Einfrieren und Rechnen in der Nacht 28./29. Nach EXP-014: `python lab/confirm/R4_pilot_n.py` (nur Power-Bericht).

- **Sitzung 29 (Fenster zu, 17:59–):** Nachtplan **unverändert**. Literatur: erste Google-Scholar-Abfrage und Init-Skala-Suche, nichts Einschränkendes zu K2/K4 (neu zur menschlichen Prüfung: Stevinson & Prieto 2026, Kontext K2-Funktion). H40 an EXP-039 vorgeprüft: Festlegung bei ≈ 1/3–2/3 der Init-Amplitude; Invarianzvergleich von EXP-040 nur über die s-Zellen lesen ([[LESART-nacht-2026-09-28]] 11–12). Kandidat N41 (nur Init-Hintergrund skalieren), erst nach EXP-040.

- **Sitzung 28 (Fenster zu, 16:49–):** Aus gespeicherten P1-Läufen: K2 absolut (80 % der W_E-Energie auf den Zielen, add 113); Maskenspektrum ordnet die Ziele innerhalb eines Splits (alle 4 Aufgaben) → **C1** registriert (an R1); nach Wechsel bei t = 50 bleibt die Rangfolge der alten Ziele erhalten (N29) → **C2** registriert (an R2). Beides Exploration an gesehenen Seeds; Auswerteskripte ungetestet. Auch bei 4× Breite, Integer-Addition, MLP → **C3** (an P4). Architekturkontrast der Theorie (MLP folgt M0) für die Feinordnung widerlegt (Pilot). Dazu **C4** (an P2f, D₅₉ bei 12 000 Schritten) und Pilot **EXP-082** (Eingriff: vorgegebene Zielstärken, optional). Momentum trägt nach dem Wechsel die Menge, nicht die Ordnung (Exploration). Alle C-Registrierungen Codex-geprüft; eigener Fund: `repro/k2.py` maß mul in der falschen Basis (behoben).

- **Sitzung 27 (Fenster zu, 15:59–):** Paper §2 (Methoden) als Fließtext, unabhängig gegen den Code geprüft (9 Korrekturen). N38: Adams Momentum-Schwanz (≈ 9 Schritte) passt zur K4b-Größe bei t = 25–35 (EXP-059, post hoc), bei 40/50 unentscheidbar; qualitativ bekannt (Xu 2026, arXiv 2608.20442). Nacht-Befehle statisch geprüft und korrigiert (siehe Blocker/Hinweise, Schritte 3/4/8). Literatur: K4b-Deutung bekannt (Sweeney 2026 u. a.), K2/K4 weiter nicht gefunden. Repro-Paket: neu `repro/k4_resets.py` (K4d/e), `repro/k4b.py` (K4/K4b), `repro/k2_function.py` (P2d), `repro/k2_function_p2e.py` (P2e), `train.py --reset-optim-part m`; geprüft, ungetestet, **nicht für heute Nacht** (erst nach der Gleichwertigkeit von `train.py`). Neu entworfen: [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (β₁/β₂-Uhr, kein Code, erst nach R3; Trainer-Option `--beta1/--beta2` erst nach dem Einfrieren der Nachtblöcke).

- **Sitzung 26 (Fenster zu, alles ungetestet bis 00:00):** R2 und R3 registriert (Entwürfe + Werkzeuge, Codex ohne Blocker; R3 = Λ- gegen Schrittuhr), EXP-078 (2 Schichten), EXP-079 (Positionskanäle, Sekunden), `repro/k4c.py`; EXP-080 vor jedem Lauf zurückgestellt (Designfehler). Literatur: Vorwärtszitate; **Tomàs Bernal et al. 2026 schränkt K2 teilweise ein**. Paper-Einleitung als Fließtext (geprüft).
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
   Scheitert `test_rewind`: EXP-073 nicht starten. Danach Selbsttests `confirm_r1.py`, `confirm_r2.py`, `confirm_r3.py --selftest` (Blöcke laut Schritt 8, wenn Zeit bleibt).
3. **CPU sofort nach den Tests starten, EXP-040 zuerst** (≈ 3 h; direkter Test des Amplitudenmodells H40 für die offene Frage in FINDINGS):
   `python lab/tools/night_program.py --cpu --cpu-workers 2 --experiments EXP-040,EXP-042,EXP-014` (im Hintergrund). **Threads (Prüfung Sitzung 27, Regel 17: Summe ≤ 12):** CPU 2 × 4 = 8 Threads, daneben **höchstens 4 GPU-Prozesse** (je 1 Thread); frühere Nächte liefen mit 12 CPU-Threads plus bis zu 10 GPU-Prozessen. Mehr GPU-Prozesse nur, wenn gemessen (Last, s/Schritt) nichts langsamer wird, und im JOURNAL festhalten.
4. **P2f einfrieren und rechnen** (≈ 30 min): `guarded_run.py -- python lab/tools/confirm_p2f.py --selftest` → Manifest `lab/confirm/P2f_manifest.json` wie P2e (Felder aus `REGISTERED`,
   `python`, `registration`, `code_sha256` aus `--hash-code`), committen, Commit-ID ins Feld `commit`, erneut committen → `--splits` → `python lab/tools/confirm_p2f.py --jobs lab/confirm/P2f_manifest.json > lab/confirm/P2f_jobs.txt` (**ohne** guarded_run: reiner Druckmodus wie bei P2e; über den Wächter landeten dessen `[guard]`-Zeilen in der Jobdatei; erste Zeile muss mit `python lab/tools/confirm_p2f.py --run` beginnen; gleiches Muster für R1/R2/R3/P4) → Smoke: erste Jobzeile allein über
   `parallel_queue` und `--analyze` (Wert nicht ansehen, nur Lader prüfen) → Block `parallel_queue.py lab/confirm/P2f_jobs.txt --workers 10` (12000 Schritte) → `--analyze`.
5. Parallel auf der GPU (nach P2f-Block oder daneben, höchstens ≈ 10 GPU-Prozesse): **EXP-073** (140 Läufe), **EXP-074** (100), **EXP-075** (120, MLP, sehr schnell) über `parallel_queue.py`,
   dann ihre `analyze.py`. Schätzung aus den s/Schritt dieser Sitzung: P2f ≈ 25 min (10 parallel, 0.03 s/Schritt), EXP-073 ≈ 18 min, EXP-074 ≈ 13 min, EXP-075 ≈ 5 min,
   GPU zusammen ≈ 1 h nacheinander; CPU (EXP-040 zuerst) ≈ 3 h. Nicht alle GPU-Queues gleichzeitig starten (≤ 10 Prozesse).


6. Nach den GPU-Queues: **EXP-078** (neu, Sitzung 26, Pilot 2-Schicht-Transformer, 20 Läufe ≈ 20 min; erst nach bestandener Gleichwertigkeit von `repro/train.py`, Schritt 7; Befehle in [[experiments/EXP-078-two-layer-steering/README|EXP-078]]) und **EXP-077** (Pilot, 40 Läufe ≈ 5 min): `parallel_queue.py lab/experiments/EXP-077-marginal-steering/jobs.txt --workers 8`, dann `analyze.py` über guarded_run.
7. Nach den Blöcken, falls Zeit (GPU, je ≈ 1–3 min): Selbsttest `confirm_p4.py --selftest`; Repro-Gleichwertigkeit (2 Befehle in [[paper/repro/README]]); neu: `confirm_r2.py --selftest`, `EXP-078/analyze.py --selftest`, Smoke `repro/k4c.py --smoke`. Dazu **EXP-018** (seit Sitzung 5 vorab registriert, nie gerechnet; Sitzung 30 auf GPU umgestellt, Nachtrag c: Beschleunigt ein spektral konstruierter Split das Grokking? 30 Läufe ≈ 15 min; Smoke, `jobs_cuda.txt`, `analyze.py --device cuda`; Befehle in der README; E/R-Arme sind über EXP-041 schon gesehen, der Kontrollarm D ist prospektiv; nach dem Ergebnis eine Bestätigung an frischen Seeds entwerfen). Dazu **EXP-083** (neu, Sitzung 30; 80 Läufe à 50 Schritte, GPU ≈ 5 min): `parallel_queue.py lab/experiments/EXP-083-reset-displacement/jobs.txt --workers 8`, dann `guarded_run.py -- python lab/experiments/EXP-083-reset-displacement/measure.py` (Tore: Init-Prüfsumme, W_E bei 0/50 = Blockschnappschuss). Dazu **EXP-079** (Sekunden, keine Läufe): `guarded_run.py -- python lab/experiments/EXP-079-head-symmetry/measure.py` (Vorbedingung für N36). EXP-080 ist **zurückgestellt** (Designfehler, siehe README) und wird nicht gerechnet. **Die Gleichwertigkeit vor EXP-078 ziehen.** P4 selbst erst Nacht 28./29. (nach Einfrieren; Entwurf `lab/confirm/P4_manifest_DRAFT.json` mit Seeds liegt bereit: `code_sha256` ergänzen, Feld `note` entfernen, als `P4_manifest.json` committen, `commit` setzen).

8. **Neu (Sitzung 26): Rest der Nacht für die Paper-Bestätigungen nutzen.** Die GPU ist nach 1–7 nur ≈ 1–1.5 h belegt. Wenn 1–7 durch sind, alle Selbsttests grün und bis 13:00 noch ≥ 2.5 h bleiben, in dieser Reihenfolge einfrieren und rechnen, je mit Manifest, Commit und Smoke wie P2f: **R1** (`confirm_r1.py`, 180 Läufe ≈ 30 min), **P4** (`confirm_p4.py`, Entwurf `P4_manifest_DRAFT.json`, ≈ 40 min), **R3** ([[confirm/R3_REGISTRATION_DRAFT|R3]], `confirm_r3.py`, Λ- gegen Schrittuhr, 80 Läufe ≈ 17 min; nur nach eingearbeiteter Codex-Prüfung), **R2** ([[confirm/R2_REGISTRATION_DRAFT|R2]], `confirm_r2.py`, 300 Läufe ≈ 45–60 min; Codex ohne Blocker, Punkte eingearbeitet). GPU-Prozesse wie in Schritt 3 (Thread-Summe ≤ 12). **R1:** Entwurf `lab/confirm/R1_manifest_DRAFT.json` liegt bereit (Seeds 2420–2509 in CELLS-Reihenfolge, 15 je Zelle; ε aus `R1_calibration.json`; `confirm_r1.py` prüft jetzt auch die Obergrenze 2509). Reicht die Zeit nicht: **R1 vor R3 vor P4 vor R2**, Rest in die Nacht 28./29. **Neu (Sitzung 30): R4** ([[confirm/R4_REGISTRATION_DRAFT|R4]], Codex zweimal geprüft; Entwurf `lab/confirm/R4_manifest_DRAFT.json` mit Einfrier-Anleitung im Feld `note`): Selbsttest heute Nacht in jedem Fall; einfrieren und rechnen (240 GPU-Läufe ≈ 1.6 h) nur, wenn nach R1 noch ≥ 2.5 h bis 13:00 bleiben, sonst in der Nacht 28./29. als Erstes. Jeder Block braucht vorher seinen Selbsttest (grün) und nach dem Einfrieren einen Smoke-Job.

9. **Neu (Sitzung 28): C1/C2** (reine Auswertungen, kein Training): Selbsttests `guarded_run.py -- python lab/confirm/C1_analyze.py --selftest` und `... C2_analyze.py --selftest` (Sekunden; reproduzieren 0.438 bzw. 0.580) **vor** dem Start von R1/R2. Nach `confirm_r1.py --analyze`: `python lab/confirm/C1_analyze.py lab/confirm/R1_manifest.json`; nach R2 entsprechend `C2_analyze.py lab/confirm/R2_manifest.json` (beide über guarded_run). Ebenso **C3** (an P4): Selbsttest `C3_analyze.py --selftest`, nach P4 `python lab/confirm/C3_analyze.py lab/confirm/P4_manifest.json`. Ebenso **C4** (an P2f, D₅₉ nach dem Grokking): Selbsttest `C4_analyze.py --selftest` **vor dem Einfrieren von P2f** (Schritt 4), nach P2f `python lab/confirm/C4_analyze.py lab/confirm/P2f_manifest.json`. Registrierungen: [[confirm/C1_REGISTRATION|C1]], [[confirm/C2_REGISTRATION|C2]], [[confirm/C3_REGISTRATION|C3]], [[confirm/C4_REGISTRATION|C4]]. **Wichtig:** C1–C4 verlangen, dass ihr Code-Tor vor dem Manifest-Commit des Blocks committet ist (ist erfüllt, solange R1/R2/P4 erst danach eingefroren werden); die Auswerteskripte **und die Dateien `C1–C4_REGISTRATION.md` sowie `C1–C4_manifest.json` bis nach der jeweiligen Auswertung nicht anfassen** (auch keinen Status/Tag ändern): Jeder spätere Commit daran lässt das Tor verweigern. Ergebnisse gehören ins JOURNAL/FINDINGS; die Registrierung erst nach der Auswertung als abgeschlossen markieren.

10. **Optional, niedrige Priorität (Sitzung 28):** Pilot [[experiments/EXP-082-graded-targets/README|EXP-082]] (vorgegebene Zielstärken, kausaler Test der Feinordnung; 40 GPU-Läufe ≈ 5–10 min): Selbsttest, `parallel_queue.py .../jobs.txt --workers 8`, `analyze.py` (Befehle in der README). Nur wenn 1–9 durch sind und die GPU frei ist.

Vorab-Lesart der Nacht (Kombination EXP-040/073/074/075, P2f): [[LESART-nacht-2026-09-28]].

## Prioritäten (Regel 18c + Regel 19, Veröffentlichung gleichgewichtig)

1. **A** P2f (D₅₉) einfrieren und rechnen; **B** EXP-040/073/074/075 rechnen und auswerten.
2. **Paper** ([[paper/STATUS]]): R1/R3/P4/R2 rechnen (Schritt 8); Trainer-Optionen sind eingebaut; `confirm_p4.py` nach
   [[confirm/P4_REGISTRATION_DRAFT|P4-Entwurf]]; schlanke Repro-Skripte; Literatur [[paper/related_work]] einarbeiten. Offene Nutzerentscheidungen stehen in STATUS.
3. **C** ruht (EXP-076: einfachste AGF-Brücke negativ).

## Blocker / Hinweise

- **Statische Prüfung der Nachtbefehle (Sitzung 27, nur Lesen):** behoben: absoluter GPU-Interpreterpfad in [[paper/repro/README]] (Gleichwertigkeitsbefehle); `--jobs` ohne Wächter (s. o.); R1-Seed-Obergrenze; R2/R3 löschen eine alte Zusammenfassung vor `--analyze`. Offen, nur Hinweis: Die Selbsttests von R2/R3 messen kein Zufallsmodell Ende-zu-Ende; ein Fehler in `one_run` zeigt sich erst im Smoke (Pflicht). Die „Voll“-Befehle von `repro/k2.py`/`k4c.py` nennen den venv-Pfad jetzt absolut (Sitzung 28).

- `freq_ban.py` hat `--reset-at-switch attn|mlp|unembed|qk|vo`. Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`).
- Speicher: höchstens ≈ 8–10 GPU-Prozesse gleichzeitig neben dem CPU-Programm. 10 D₅₉-Läufe parallel: ≈ 0.03 s/Schritt je Lauf.
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung: bei langen Läufen `--stop-after-gen` ≥ Schritte. `group_train.py` läuft immer die volle Schrittzahl.
- Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- Globales Python hat kein scipy (Sitzung 24): Rangkorrelation selbst rechnen.
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen (Sitzung 24 einmal passiert, sofort repariert); Python `write_text` schreibt CRLF in Code-Dateien. Uhrzeiten nur gemessen (Python zoneinfo).

---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-26, 17:41 Berlin (Sitzung 10, Deadline 20:29; nächster Runner-Start 22:29 Berlin)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[JOURNAL]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]]

## Wiederaufnahme (zuerst lesen)

- **SITZUNG 10 (17:41):** EXP-035 Seed 30 fertig (7 Läufe), Seed 31 t = 50, 150 laufen von Hand bis ~17:52 (Log
  `lab/runner/logs/exp035_s10_manual.log`). `queue_s9.sh` ist beendet. EXP-036 hat **Nachtrag d + e** (kalibriertes P36b mit frühen
  Spektren `--spectra-at`, Smoke vorgeschaltet und von Hand geprüft). **Nächstes Fenster (ab 00:00) unverändert:**
  `python lab/tools/guarded_run.py --check`, keine Queue aktiv (`ps -ef | grep -E "queue|guarded_run"`), dann
  `sh lab/experiments/queue_s10.sh` im Hintergrund (EXP-035 Rest überspringt Fertiges → EXP-038 → EXP-036 (+ `analyze_p36b.py`) → EXP-034 → queue_s5).

- **ENDE SITZUNG 9 (17:06) → nächste Sitzung beginnt hier.** Nächster Start 19:49 Berlin = **außerhalb des Fensters** (heute bis
  18:00, ab 27.09. 00:00–13:00): bis 00:00 nur Denk-/Sucharbeit. **Im Fenster ein Befehl:** `python lab/tools/guarded_run.py --check`,
  prüfen, dass keine Queue läuft (`ps -ef | grep -E "queue|guarded_run"`), dann **`sh lab/experiments/queue_s10.sh`** im
  Hintergrund (Log z. B. `lab/runner/logs/queue_s10.log`): EXP-035 (Rest; überspringt Fertiges) → **EXP-038** → **EXP-036** →
  EXP-034 → queue_s5. Nach jeder Auswertung Ergebnis ins README/JOURNAL/LAB (die Queue schreibt nur `summary.json`).
  Abgeschlossen in Sitzung 9: EXP-020 (*nicht bestätigt*; beschreibend (25, 50] in 5/5), EXP-028 (*teilweise*), EXP-037
  (*gestützt* mit Einschränkung: reproduzierbare, funktionale Konfliktfrequenzen). Befunde: JOURNAL „Abschlussbericht Sitzung 9“.
  **Vor dem EXP-036-Start (Denkarbeit, 19:49–00:00):** P36b kalibriert neu festlegen (EXP-036 Nachtrag c; Codex-Einwände
  in `EXP-037-alternation-conflict/codex_conclusion_review_2026-09-26.txt`). EXP-036 steht in queue_s10 erst nach EXP-038.
  Denkarbeit-Ideen: warum 25–50 Schritte (Verbindung zur linearen Modentheorie aus EXP-033), Konfliktfrequenzen theoretisch
  (gemeinsame Unterstützung, P36b), EXP-038-Folgeversuch mit norm-angepasstem Rücksetzen.

- **SITZUNG 9 (16:22):** EXP-020 **abgeschlossen** (*nicht bestätigt* 4/5; beschreibend (25, 50] in 5/5), EXP-028 *teilweise*,
  EXP-020 Nachtrag d an frischen Seeds **nicht bestätigt**. `queue_s9.sh` läuft EXP-037 (Smoke ok; 9 Läufe bis ~17:05), dann
  EXP-035. Wiederaufnahme: `sh lab/experiments/queue_s9.sh` (überspringt Fertiges). Nach EXP-037:
  `python lab/tools/guarded_run.py -- python lab/experiments/EXP-037-alternation-conflict/ablate_foreign.py` (von Hand,
  nicht in der Queue; braucht `summary.json` von EXP-037).

- **SITZUNG 9 (15:13):** `queue_s8.sh` angehalten, **`queue_s9.sh` läuft** (Log `lab/runner/logs/queue_s9.log`; Reihenfolge EXP-020 Rest → Auswertungen → **EXP-037** → EXP-035 → EXP-036 → EXP-034 → queue_s5). Wiederaufnahme = `sh lab/experiments/queue_s9.sh`.
- **SITZUNG 9 (15:04):** `queue_s8.sh` lief seit 14:50 (Log `lab/runner/logs/queue_s8.log`, EXP-020 Seed 32
  t = 1000, dann Seeds 33, 34, dann EXP-035). **Ab jetzt `sh lab/experiments/queue_s9.sh` statt `queue_s8.sh`** (gleiche
  Reihenfolge, zusätzlich Nachtrag-d-Auswertung und **EXP-036** nach EXP-035; überspringt Fertiges). Nie zwei Queues
  gleichzeitig: vorher `ps -ef | grep -E "queue|guarded_run"`.
  Neu vorab festgelegt: EXP-020 **Nachtrag d** (fremde Frequenzen in Mischzuständen, P-d1/P-d2 für Seeds 33/34,
  `conflict_freqs.py`), **EXP-036** (neue Init bei gleichem Split, 7 Paare, Vorzeichentest über Paare; nach Codex umgebaut,
  Nachtrag a). N15 in NOVEL_DIRECTIONS.

- **ENDE SITZUNG 8 (14:27):** `queue_s5.sh` kontrolliert angehalten; letzter Lauf EXP-020 Seed 32 t = 150 lief zu Ende (vor der
  Deadline). EXP-020: Seeds 30, 31 vollständig (beide (25, 50], stützen H20), Seed 32: nur F, nur G, t = 150, 50, 25, 10 fertig (es fehlen 400, 1000).
  **Weiter mit `sh lab/experiments/queue_s8.sh`** (siehe nächster Punkt). Befunde der Sitzung: JOURNAL „Abschlussbericht Sitzung 8“.

- **NÄCHSTE SITZUNG, ein Befehl (Sitzung 8, 13:51):** `python lab/tools/guarded_run.py --check`, dann prüfen, dass keine Queue läuft
  (`ps -ef | grep -E "queue|guarded_run"`), dann **`sh lab/experiments/queue_s8.sh`** im Hintergrund (Log z. B.
  `lab/runner/logs/queue_s8.log`). Reihenfolge darin: Rest von EXP-020 (Seeds 31–34) → Auswertung EXP-020 und EXP-028 →
  EXP-035 (Smoke, Seeds 30–32) → Auswertung → EXP-034 → Auswertung → Rest von `queue_s5.sh`. Alles überspringt Fertiges.
  Nach jeder Auswertung: Ergebnis ins README/JOURNAL/LAB (die Queue schreibt nur `summary.json`).

- **Sitzung 8, 13:47 (neuester Stand):** Reihenfolge für die nächsten Fenster: (1) `queue_s5.sh` weiter (EXP-020 Seeds 31–34; danach
  EXP-020- und EXP-028-Auswertung), (2) `sh lab/experiments/EXP-035-warmup-lockin/queue.sh 30 31 32` (braucht die EXP-020-
  Intervalle der Seeds; beginnt mit Smoke), (3) `sh lab/experiments/EXP-034-phase2-optimizer/queue.sh`. Alternativ EXP-034 vor
  EXP-035, falls EXP-020 noch läuft und ein Jobplatz frei ist: nie zwei Queues gleichzeitig. `queue_s5.sh` enthält nach EXP-020
  noch EXP-018/014/023/022/010 (viele Stunden): nach EXP-020 ggf. anhalten, um EXP-035/034 vorzuziehen.
  `freq_ban.py` hat seit b231fc6 eine Option `--warmup` (Standard 0 = unverändert).

- **Sitzung 8, 13:32:** EXP-033 **abgeschlossen** (*zustandsbestimmt* vorab; nach Codex eingeschränkt: AdamW in Phase 1 nicht nötig).
  `queue_s5.sh` läuft wieder seit 13:17 (EXP-020 Seed 30 fast fertig, dann Seeds 31–34). **EXP-034** vorab festgelegt
  (Nachtrag a, commit a7e9cf2/c36d212), nicht ausgeführt, `--opt2 gd` ungetestet. **Nächste Sitzung (Fenster heute bis 18:00,
  ab 2026-09-27 wieder 00–13):** Prioritätsvorschlag: EXP-020 zu Ende (liefert EXP-020 + EXP-028), dann
  `sh lab/experiments/EXP-034-phase2-optimizer/queue.sh` (A ≈ 75 min, Pilot ≈ 27 min, B ≈ 90 min), Auswertung
  `python lab/tools/guarded_run.py -- python lab/experiments/EXP-034-phase2-optimizer/analyze.py`. Vor dem Start prüfen, ob
  noch eine Queue läuft (`ps -ef | grep -E "queue|guarded_run"`); nie zwei Queues gleichzeitig.

- **Sitzung 8, 12:30:** EXP-033-Queue läuft (Nachtrag c, `_bt`-Läufe); Wiederaufnahme = `sh lab/experiments/EXP-033-optimizer-lockin/queue.sh` (überspringt Fertiges). `queue_s5.sh` weiter pausiert.

- **Sitzung 8, 12:18:** `queue_s5.sh` **angehalten** (EXP-020 Seed 30: F, G, t = 150 fertig, t = 50 lief zu Ende). EXP-033-Queue
  läuft im Hintergrund (Log `lab/runner/logs/queue_exp033.log`). Danach: `analyze.py` von EXP-033, dann `sh lab/experiments/queue_s5.sh`.
- **Sitzung 8, 12:15:** `queue_s5.sh` läuft (EXP-020 Seed 30, Log `lab/runner/logs/queue_s5.log`). **EXP-033** vorab festgelegt
  (Nachtrag a nach Codex, commit 840e890), noch kein Lauf. Plan: nach EXP-020 Seed 30 Warteschlange anhalten (nur den
  `sh`-Prozess beenden, laufenden Lauf fertig werden lassen), dann `sh lab/experiments/EXP-033-optimizer-lockin/queue.sh`,
  dann `python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/analyze.py`, dann `queue_s5.sh`
  erneut (überspringt Fertiges). Wurde die Sitzung unterbrochen: erst `tasklist | grep python` prüfen, dann in dieser
  Reihenfolge fortsetzen (beide Skripte überspringen Fertiges).

- **ENDE SITZUNG 7 (11:24) → nächste Sitzung beginnt hier.** Kette `queue_s7.sh` wird vor Sitzungsende kontrolliert
  um 11:51 gestoppt (EXP-025 vollständig, ausgewertet). **Nächste Schritte im Fenster:**
  1. `python lab/tools/guarded_run.py --check`
  2. EXP-025 ist fertig und ausgewertet (*teilweise*, 11:51).
  3. `sh lab/experiments/queue_s5.sh` (EXP-018/020-Smokes, dann **EXP-020 zuerst** (liefert auch EXP-028), EXP-018, EXP-014, …),
     danach `python lab/tools/guarded_run.py -- python lab/experiments/EXP-028-memo-imprint/analyze.py`
  **Neue Befunde Sitzung 7:** EXP-032 *Festlegung in ≤ 20 Schritten* (t½ = 5), EXP-030 *Rest gestützt*, EXP-029 *teilweise*,
  EXP-024 Q *richtungsgleich n. s.* / R *bestätigt* (memorierend), EXP-026 *Anker ok, Trend n. s.*, EXP-027 *nicht auswertbar*,
  EXP-027b *widerspricht*. EXP-031 zurückgestellt (Umbau nötig). Ideen: EXP-033 (AdamW-Rolle), EXP-031 neu (gekreuzte Spender).
- **Sitzung 7, 10:32:** EXP-026 fertig (*Anker ok, Trend n. s.*; beschreibend Festlegung in ≤ 50 Schritten). Kette läuft:
  EXP-027 → EXP-032 → EXP-027b (beide in `EXP-025/queue.sh` vorangestellt) → EXP-025 → queue_s5. Wiederaufnahme:
  `sh lab/experiments/queue_s7.sh` (überspringt Fertiges). Auswertungen: EXP-027 `analyze.py` (erwartet *nicht auswertbar*,
  Güte), EXP-032 `analyze.py`, EXP-027b `analyze_b.py`, EXP-025 `analyze.py`. EXP-031 zurückgestellt.
- **Sitzung 7, 09:59, neue Befunde (ohne Training, vorab festgelegt):** EXP-029 *teilweise* (W_E ist in der Memorisierungsphase
  spezifisch mit der eigenen Maske ausgerichtet, 10/10; Abbau bis gen + 25 nur 8/10), EXP-030 *Rest gestützt* (M0 → K läuft
  über W_E bei Schritt 250). EXP-028 vorbereitet (wartet auf EXP-020-Läufe). N13 nach Codex korrigiert.
- **Sitzung 7, 09:46:** EXP-024 **abgeschlossen** (Q richtungsgleich n. s., R bestätigt aber memorierend). Läuft:
  `sh lab/experiments/queue_s7.sh` (Log `lab/runner/logs/queue_s7.log`): EXP-026-Smoke (ok) → EXP-026 (30 Läufe, seit 09:44,
  **Umschaltdesign nach Codex, Nachtrag a**, commit 53450e1) → EXP-027 (in EXP-026/queue.sh verkettet) → EXP-025 → `queue_s5.sh`. Alles überspringt Fertiges;
  Wiederaufnahme = `sh lab/experiments/queue_s7.sh` erneut starten (die Warteschleife endet sofort, weil das EXP-024-Log
  schon eine `[exp024]`-Zeile hat; fehlt sie, zuerst `sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh`).
  Auswertungen danach: EXP-026, EXP-027, EXP-025 je `analyze.py` (über den Wächter).

- **Sitzung 6, 08:53:** Baseline 19 fertig (EXP-003d 10/10). Läuft: **EXP-024** (`sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh`,
  Log `lab/runner/logs/queue_exp024.log`, überspringt fertige Läufe). `queue_s5.sh` ist **angehalten**; danach neu starten
  (setzt bei den Smokes EXP-018/020 fort). Nach EXP-024: `python lab/tools/guarded_run.py -- python lab/experiments/EXP-024-quadratic-agf-mask/analyze.py`.
- EXP-015/012 Phase 2 mit n = 10 nur berichten: `mask_spectrum.py --phase 2 --suffix _n10`, `predict.py --phase 2 --predictor G0 --suffix _n10`.

- **Sitzung 5, 07:31:** Der Nutzer hat um 06:58 die Freigabe erteilt (`.claude/settings.local.json`: `sh lab/experiments/*queue*`,
  `python lab/tools/guarded_run.py *`). `queue_s5.sh` lief 07:30–08:24: EXP-016 Seeds 16–19 und Baseline 18 fertig; Baseline 19
  vom Wächter abgelehnt (Deadline), rc 3, keine Prozesse mehr. **Nächste Sitzung: denselben Befehl erneut starten** (setzt
  bei Baseline 19 fort).
- **Neue Warteschlange:** `sh lab/experiments/queue_s5.sh` (ersetzt `queue_s4b.sh`, dieselben Läufe plus EXP-018/020,
  neue Reihenfolge). Log z. B. nach `lab/runner/logs/queue_s5.log`. Reihenfolge: EXP-016 Seeds 16–19 (je 2 × 4.5 min,
  danach Entscheidung) → EXP-003d-Baselines 18, 19 → Smoke EXP-018 und EXP-020 (+ `check_smoke.py`) → EXP-018 Seeds
  20–24 → EXP-014 Kreuzpaare → EXP-020 → EXP-023 → EXP-022 (über deren eigene `queue.sh`) → EXP-018 Seeds 25–29 →
  EXP-010-Tausch 11–19. Sie stoppt bei **jedem** Exit ≠ 0;
  fertige Läufe werden übersprungen (`freq_ban.py` endet dann seit Sitzung 5 mit 0). Neu starten = fortsetzen.
- **Abgebrochene Läufe** stehen mit `status: running` in `result.json` und werden neu gestartet (kein Resume).
- Vor jedem Start: `python lab/tools/guarded_run.py --check`.
- **Abhängigkeit:** Die Läufe mit `--min-minutes 33` (Baselines, EXP-014, EXP-010) brauchen den **uncommitteten**
  `guarded_run.py` des Nutzers ohne feste Jobgrenze (Regel 14). Mit der committeten Fassung (Jobgrenze 20 min) würde der
  Wächter sie mit Exit 3 ablehnen und die Warteschlange hielte an (Codex-Prüfung der Warteschlange, Sitzung 5).
- **Zeilenenden:** Python schreibt unter Windows im Textmodus CRLF. Shell-Skripte müssen LF haben (sonst bricht `sh`).
  Nach Änderungen an `*.sh` mit `file` prüfen; beim Schreiben aus Python `newline='
'` benutzen.
- Nach EXP-016 Seed 17 (8 Seeds): `python lab/experiments/EXP-016-engineered-split/analyze.py`.

## Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  Uncommittete Änderungen an `lab/runner/*`, `lab/runner-state.json` und `lab/tools/guarded_run.py` stammen vom
  Nutzer (Regeln 13/14, keine feste Jobgrenze). Sie sind bewusst nicht committet; der Nutzer entscheidet.
- **Umgebung:** Windows 11, Python 3.12, torch 2.13.0, numpy 2.5.1 (Studie: torch 2.12.1). Die rekonstruierten Inits
  stimmen trotzdem bitgenau mit den gespeicherten Schritt-0-Checkpoints überein. 0.13 s/Schritt (Transformer, 4 Threads).
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Interpretation bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`), Sitzungsstart und -ende-Klassifikation belegt.

## Stand der Versuche (nach Sitzung 5)

**Bestätigt an frischen Seeds 10–17 (vorab festgelegt):**
- [[experiments/EXP-015-mask-spectrum/README|EXP-015]]: Das Masken-Spektrum M0 des Trainingssplits (ohne Gewichte) sagt die
  Rangfolge der gelernten Frequenzen voraus (r̄ 0.277, fremde Masken 0.499, p 2.5e-5). **Nur Assoziation.**
- [[experiments/EXP-012-init-gradient/README|EXP-012]]: Erster Gradient an W_E > Init-Spektrum (p 0.031).

**Abgeschlossen (Sitzung 5, 08:06):** [[experiments/EXP-016-engineered-split/README|EXP-016]] *steuerbar*: 10/10 Seeds, Δ̄ = +7.7 von 10,
p ≈ 0.001. Konstruierte Splits geben die gelernten Frequenzen vor; alle Abweichungen sind 2k-Harmonische der Ziele.

**Neu vorbereitet in Sitzung 5 (alle nicht ausgeführt, Codex-Reviews eingearbeitet):**
- [[experiments/EXP-018-split-speed/README|EXP-018]]: Beschleunigt ein spektral konzentrierter Split das Grokking?
  Feste Testmenge, Kontrolle D = Gewichte von E innerhalb der Antidiagonalen permutiert, Seeds 20–29. Drei
  konkurrierende Vorhersagen (H18 / Frequency Principle nach Zhou et al. 2024 / Komplement-Artefakt).
- [[experiments/EXP-019-coherent-mask/README|EXP-019]]: kohärentes Masken-Spektrum M0c gegen M0 (post hoc
  richtungsgleich, n. s.); Bestätigung ohne eigene Läufe aus EXP-018 Arm R + Baselines 18/19.
- [[experiments/EXP-020-data-switch/README|EXP-020]]: Datenwechsel F → G nach t Schritten, gleiches G-Budget:
  kausale Festlegungszeit der Frequenzwahl. Seeds 30–34.
- [[experiments/EXP-021-harmonic-misses/README|EXP-021]]: Bestätigung „Fehlgriffe = 2k der Ziele“ an 18 frischen Läufen
  (EXP-016 16–19, EXP-020 nur-F/nur-G), ohne eigenes Training.
- [[experiments/EXP-023-split-value/README|EXP-023]]: Eigene Wertematrix für Position 1 (Seeds 50–59, rand/copy/Baseline,
  3000 Schritte): folgt die finale Wahl dann M0 statt M0c? Kausaltest des Mechanismus.
- [[experiments/EXP-022-single-frequency/README|EXP-022]]: Erzwingt ein Ein-Frequenz-Split eine Ein-Frequenz-Lösung?
  Seeds 40–44, Arme S1/D1/S5, 6000 Schritte, funktionale Messung (`nanda`) am gespeicherten Modell.
**Post hoc (Sitzung 5):** Die natürliche M0-Konzentration eines Zufallssplits sagt die Grokking-Zeit nicht voraus.
**Mechanismus (Sitzung 5, post hoc, nach Codex-Angriff präzisiert):** Im ersten W_E-Gradienten interferieren linke und
rechte Eingabeposition frequenzweise so, wie es der Kreuzterm der Maske (M0c − M0) vorhersagt (18/18 Seeds, fremde
Maske −0.09); deshalb beschreibt M0c die Gradientenleistung besser als M0 (0.77 vs. 0.57). Ob M0c auch K besser
vorhersagt: EXP-019.
**Oberwellen (Sitzung 5, explorativ):** Alle 14 Nicht-Ziel-Frequenzen in EXP-016 (Seeds 10–15) sind fold(2k) eines Ziels.
Auch unter Zufallssplits enthält die W_E-Top-5 gehäuft (k, 2k)-Paare. In den Studienmodellen sind die schwächeren
2k-Glieder die unwichtigsten der Top-5 (Ablation 8/8), aber nicht null; Phasenkopplung nur in 3/10 Paaren deutlich;
sie erreichen die Top-5 meist erst nach dem Grokking. Vorhersage für EXP-016 Seeds 16–19 vorab festgelegt (Nachtrag b).
**Literatur (Sitzung 5):** N3 in anderer Form bekannt (Zhou et al. 2024, Frequency Principle, andere Aufgaben); bei
festem Split variiert K trotzdem über Inits (GitHub-Nachbau) → Split ist nicht die einzige Ursache.

**Weiter vorbereitet:** EXP-014 (Kreuzdesign), EXP-017 (RFM), EXP-013 (Lock-in-Kurve), EXP-011, EXP-001/002.
**Teilweise:** EXP-010 (1/10 Paare), EXP-003d (9/10 Baselines; Seed 18 gen 8775).

## Nächste konkrete Aktionen (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`, dann `sh lab/experiments/queue_s5.sh` im Hintergrund, beobachten.
2. EXP-016 ist fertig. Nach den Baselines 18/19: EXP-015/012 Phase 2 mit n = 10 nur berichten.
3. Nach den Smokes: `check_smoke.py` (EXP-020) und `result.json` des EXP-018-Smokes prüfen (`test_hash`, 2554 Testpaare).
4. Auswertungen: `EXP-021-harmonic-misses/analyze.py`, `EXP-022-single-frequency/analyze.py`, `EXP-018-split-speed/analyze.py`, `EXP-019-coherent-mask/analyze.py`, `EXP-014-split-vs-init/analyze.py`,
   `EXP-020-data-switch/analyze.py`, `EXP-010-init-swap/analyze.py` (je über den Wächter, wo `make_dataset` benutzt wird).
5. Außerhalb des Fensters: Theorie (AGF-Nutzen mit maskiertem Verlust ↔ M0c herleiten), Reverse-Kontrolle G → F für
   EXP-020 als eigenen Nachtrag erwägen, Google Scholar gezielt zu N6.

## Blocker

- **Aufgehoben 07:31:** Der Nutzer hat um 06:58 die Bash-Freigabe erteilt; die Warteschlange läuft. Der Eintrag darunter ist historisch.

- **Sitzung 5 (2026-09-26 05:52 Berlin):** Der Start von `sh lab/experiments/queue_s4b.sh` im Hintergrund wurde vom
  Auto-Mode-Klassifikator von Claude Code abgelehnt („Safety Bypass Flag“), obwohl jeder Lauf über `guarded_run.py`
  geht. Nach den Regeln der Ablehnung **nicht umgangen** (auch nicht über Einzelaufrufe). Die Warteschlange muss der
  Nutzer freigeben: entweder eine Bash-Berechtigungsregel für `sh lab/experiments/queue_s5.sh` (Nachfolger von `queue_s4b.sh`) bzw.
  `python lab/tools/guarded_run.py` hinzufügen oder die Warteschlange selbst starten. Bis dahin nur Denk- und Sucharbeit.

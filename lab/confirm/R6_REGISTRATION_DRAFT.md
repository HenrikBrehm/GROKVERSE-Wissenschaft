---
id: R6
status: entwurf
datum: 2026-09-27
tags: [lab/confirm, programm/B, paper, exp/vorbereitet, neu/kandidat]
---
# R6: Verzögert ein Datenwechsel mitten in der Festlegung das Grokking? Bestätigung an frischen Seeds (Registrierungsentwurf)

Zurück: [[LAB]] · [[FINDINGS]] (Programm B, größte offene Frage: funktionale Signatur der Festlegung) · [[NOVEL_DIRECTIONS]] N43 · [[JOURNAL]] Sitzung 32, Zyklen 5–6 · Konstruktion wie [[confirm/N28_REGISTRATION|N28]].

**Status:** Entwurf, Sitzung 32 (2026-09-27, Berlin, Fenster zu), **vor jedem R6-Lauf**. Code `lab/tools/confirm_r6.py` geschrieben, **ungetestet** (nur Syntaxprüfung; Selbsttest im Fenster). Einfrieren erst nach Codex-Prüfung und grünem Selbsttest.

## Warum

Post hoc (Sitzung 32) habe ich zum ersten Mal die Generalisierungszeiten gespeicherter Wechsel-Blöcke gelesen. **N28** (30 Seeds, GPU): Ein Wechsel A→B bzw. B→A bei 25 Schritten generalisiert pro Seed in 28/30 später als der Lauf nur auf dem Ziel-Split (Mittel C(25) = 0.54 log2, SD 0.42). Bei 50 Schritten ist er in 24/30 früher. C(25) − C(50) = 0.90 (SD 0.62), 27/30. **P3** (Seeds 1050–1079, Hypothese vorher festgelegt): 28/30. **EXP-020** (CPU, 5 Seeds): @10/@25/@50 langsam, @150/@400 schnell. Die Kosten eines Datenwechsels scheinen dort am größten, wo die Frequenzwahl umschlägt (K4c: 25 → neu, 50 → alt). Das wäre eine funktionale, billige Messung der Festlegung. Alle Zahlen sind post hoc an Seeds, deren Frequenzen gesehen waren.

## Aufbau

- **Konstruktion:** EXP-053 `overlap_split`, ω = 0, gleiche Steuerstärke (ε aus `calibration.json`), gemeinsame Testmenge je Seed; identisch zu N28. **Seeds 2800–2829** (30, frisch, vor jeder Nutzung reserviert in [[FINDINGS_DETAILS]]).
- **Läufe je Seed (16):** A allein und B allein (je 2000 Schritte); Wechsel A→B und B→A bei **t ∈ {10, 20, 25, 30, 40, 50, 75}** (t + 2000 Schritte, AdamW-Zustand bleibt). freq_ban, GPU, `--threads 1`, **`--stop-after-gen` = Schrittbudget** (kein vorzeitiger Stopp; der End-Schnappschuss für π ist immer da). 480 Läufe.
- **Zeit:** b = min(Ereignis, 2000). Das Ereignis ist der Trainerschritt mit der ersten Testgenauigkeit ≥ 0.95, gezählt ab Schritt 0. Der **gemeinsame Horizont 2000 gilt für alle Arme**, zwei beidseitig zensierte Läufe ergeben also genau 0. Gezeigt wird damit „frühere Generalisierung bis 2000“, nicht die Endgenauigkeit.
- **Kosten je Seed:** C(t) = Mittel über beide Richtungen von log2 b(Wechsel@t) − log2 b(nur Ziel-Split). Das Ziel von A→B ist B.

## Hypothesen (Primärfamilie, Holm über 2 bei α = 0.05)

- **H1:** C(25) > 0. Ein Wechsel bei 25 Schritten verzögert das Grokking gegenüber dem Training nur auf dem Ziel-Split.
- **H2:** C(25) − C(50) > 0. Die Verzögerung ist bei 25 größer als bei 50.
- **Test je Hypothese:** p = max(p_flip, p_Vorzeichen). p_flip ist der einseitige Vorzeichen-Permutationstest der Summe, **exakt über alle 2^n Vorzeichen** (Meet-in-the-Middle, exakt bis n = 40; bei n = 30 also exakt). p_Vorzeichen ist der exakte einseitige Binomialtest über die Seeds mit |Wert| > 1e-9. „Bestätigt“ heißt Holm-p < 0.05. Die Effektgröße ist das Mittel mit 95-%-Bootstrap-KI und Faktor 2^Mittel (geometrisches Mittel des beschränkten Zeitverhältnisses), nur als Schätzer. Es gibt keine Mindesteffekt-Schwelle als Urteil.
- **Nullhypothese (präzisiert nach Codex):** p_flip setzt Vorzeichensymmetrie der Verteilung des seedweisen Werts voraus (scharfe Austauschbarkeit der Arme innerhalb eines Seeds). p_Vorzeichen prüft P(Wert > 0) > 1/2. Das Maximum ist eine konservative Ko-Bedingung: „Bestätigt“ heißt, dass beide die Nullhypothese in der vorhergesagten Richtung ablehnen, nicht nur, dass ein Mittel positiv ist.
- **Deutung (eng, nach Codex):** Bis zum Horizont hat jeder Arm genau 2000 Updates. H1 vergleicht A^t→B^(2000−t) mit B^2000, also einen **Regimevergleich**: Die ersten t Ziel-Updates werden durch Ursprungs-Updates ersetzt. Weniger Ziel-Exposition kann C erhöhen, mehr verschiedene Paare können es senken. H1 allein belegt daher keine „Unterbrechung der Festlegung“. H2 trennt teilweise: Die Deutung „nur weniger Ziel-Exposition“ sagt C(50) ≥ C(25) vorher (bei 50 werden mehr Ziel-Updates ersetzt, bei gleicher Paarvereinigung), H2 behauptet das Gegenteil. Ein von Beginn an gemischter A∪B-Arm wäre eine weitere Kontrolle. Er fehlt bewusst (die größere Datenmenge beschleunigt für sich, der Arm wäre nicht sauber vergleichbar) und ist als Grenze genannt.

## Sekundär (außerhalb der Familie, „gestützt“ / „nicht gestützt“)

- **S1 (Lage der Spitze):** Alle t aus dem Raster mit dem größten mittleren C (Gleichstand ≤ 1e-9) liegen höchstens 10 Schritte neben t_π. *Nicht auswertbar*, wenn weniger als 10 Seeds ein π haben, wenn der Median von π schon am ersten Rasterpunkt ≥ 0.5 ist (linkszensiert) oder 0.5 nie erreicht. t_π ist der erste Wechselzeitpunkt, an dem der Median der Persistenz π(t) (N28-Definition, End-W_E, nur Seeds mit L(A) − L(B) ≥ 2) den Wert 0.5 erreicht, linear interpoliert. Das verknüpft die Zeitkosten mit der gemessenen Festlegung.
- **S2 (Schwelle der Persistenz; ergänzt in Sitzung 32 vor dem Einfrieren, Anlass: Blockebene post hoc, JOURNAL Zyklus 10):** „Gestützt“, wenn mittleres C(t) ≤ 0 für jedes t mit Median-π(t) ≥ 0.9 **und** mittleres C(t) > 0 für jedes t mit 0.2 ≤ Median-π(t) ≤ 0.8. π < 0.2 ist vorab ausgenommen, weil C für t → 0 gegen 0 gehen muss. Es braucht mindestens einen Rasterpunkt je Klasse und mindestens 10 Seeds mit π, sonst *nicht auswertbar*.
- **Beschreibend:** Mittel und Median von C(t) für alle t, Ereignisanteile je Arm, π(t).

## Stichprobe

**n = 30** (nach Codex-Prüfung, vor jedem Lauf; Entwurf zuerst 20). Nachprüfbar in `lab/confirm/R6_pilot_power.py` → `R6_pilot_power.json`. Dort stehen die N28-Werte je Seed, genau wie in R6 gerechnet (gemeinsamer Horizont 2000): C(25) Mittel 0.54, SD 0.41, 28/30 positiv; C(25) − C(50) 0.90, SD 0.62, 27/30. P3 C(25): 0.60, SD 0.38, 28/30. Die Power beider Ablehnungen (Holm; Seeds gemeinsam neu gezogen, Flip-Test als Monte Carlo) liegt bei n = 20 bei 0.99, bei n = 30 bei 1.00. **Sensitivität bei halbem Effekt** (beide Werte um das halbe Mittel verschoben, wegen des Winner's Curse): n = 20 → 0.41, n = 25 → 0.55, n = 30 → 0.78 (archiviert in `R6_pilot_power.json`, `power_half_effect_shift`). Daher n = 30.

## Gültigkeit

Alle 16 Läufe eines Seeds sind gebunden und über den gemeinsamen Lader geladen (Seed, Gerät, Schrittbudget, Split-, Test- und Wechsel-Hash, W_E-Schnappschuss am Ende endlich), dazu mindestens 2000 abgeschlossene Schritte. Die Splits sind bitgleich mit dem deterministischen Neubau. Fehlt ein Seed, ist R6 *nicht auswertbar*; es wird nicht mit weniger Seeds geurteilt.

## Was dagegen spräche

- H1 nicht bestätigt: Die Verzögerung bei 25 war eine Eigenheit von N28/P3 (gesehene Seeds) oder hängt am Block.
- H1 bestätigt, H2 nicht: Jeder frühe Wechsel verzögert; eine Spitze im Festlegungsfenster ist nicht belegt.
- S1 nicht gestützt: Die Zeitkosten messen etwas anderes als die Persistenz π.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

Die Generalisierungszeiten von N28 (Seeds 2200–2229), P3 (1050–1079), EXP-020 (30–34) und EXP-041 (20–29) wurden in Sitzung 32 gelesen (`lab/confirm/speed_switch_cost_*_s32.py`, `speed_prefix_s32.py`). Beeinflusst sind die Hypothesen, die Wahl von 25/50, das Raster, der gemeinsame Horizont 2000 und n. *Ergänzt 21:12 (vor dem Einfrieren):* Zusätzlich gelesen wurden die Zeiten von EXP-059 und EXP-056 (Seeds 400–409, gleiche Splits und Init) als Trockenlauf der R6-Auswertung (`lab/confirm/speed_switch_curve_s32.py`). C(t) = 0.27 / 0.38 / 0.53 / 0.57 / 0.55 / 0.33 / −0.67 bei t = 10 / 15 / 20 / 25 / 30 / 35 / 50; H1, H2, S1 und S2 würden dort zutreffen. Dieser Trockenlauf hat an R6 nichts geändert (Hypothesen, Raster, n und Regeln standen vorher fest). Kein Lauf mit Seeds 2800–2829.

## Grenzen (vorab)

Eine Aufgabe (add 113), eine Architektur, eine Optimierer-Einstellung, eine Split-Konstruktion (ω = 0). Die Wechselkosten mischen mindestens drei Einflüsse: die Unterbrechung der Festlegung, die geringere Ziel-Exposition und die zusätzlichen verschiedenen Paare (siehe Deutung). Das Vorzeichen ihrer Summe ist nicht allgemein festgelegt. EXP-020 (andere Konstruktion, CPU) zeigte @50 noch langsam: Die Lage des Fensters kann von der Konstruktion abhängen.

## Reproduktion (im Fenster; Muster wie P2f/N28)

```
python lab/tools/guarded_run.py -- python lab/tools/confirm_r6.py --selftest
# Manifest lab/confirm/R6_manifest.json = REGISTERED + python (absoluter .venv-gpu-Pfad) + registration + code_sha256 (--hash-code); committen, commit setzen, committen
python lab/tools/confirm_r6.py --splits lab/confirm/R6_manifest.json
python lab/tools/confirm_r6.py --jobs lab/confirm/R6_manifest.json > lab/confirm/R6_jobs.txt      # ohne Wächter
# Smoke: erste Jobzeile allein über parallel_queue, dann --analyze (nur Lader prüfen; nicht auswertbar erwartet)
python lab/tools/parallel_queue.py lab/confirm/R6_jobs.txt --workers 10                           # ≈ 50 min GPU
python lab/tools/guarded_run.py -- python lab/tools/confirm_r6.py --analyze lab/confirm/R6_manifest.json
```

## Codex-Prüfung (Sitzung 32, `lab/confirm/R6_codex_review_s32.txt`, vor jedem Lauf): kein Blocker, 3 Major, 2 Minor, alle selbst geprüft

1. **MAJOR Estimand:** übernommen als engere Deutung (Regimevergleich) plus Hinweis, was H2 trennt. Die pauschale Aussage „H1 konservativ“ ist gestrichen. Einen gemischten Arm gibt es nicht, mit Begründung.
2. **MAJOR früher Stopp:** übernommen. `--stop-after-gen` entspricht jetzt dem Schrittbudget, und der Lader verlangt genau den End-Schritt. Praktisch war das Risiko klein, weil das Ereignis nie vor t ≤ 75 kommt (Memorisation ≈ 120).
3. **MAJOR Power nicht nachprüfbar:** übernommen: `R6_pilot_power.py`/`.json` mit genau dem R6-Horizont, dazu die Sensitivität bei halbem Effekt, danach n = 30.
4. **MINOR Nullhypothese / Monte Carlo:** übernommen: exakter Vorzeichentest über alle 2^n Vorzeichen (nach der Nachprüfung als Meet-in-the-Middle, weil n = 30 für die zuerst eingebaute Aufzählung bis n = 22 zu groß war); Nullhypothese präzisiert.
5. **MINOR S1-Randfälle:** übernommen: Gleichstände, Linkszensur, mindestens 10 Seeds mit π. Die Selbsttest-Zusicherungen sind ergänzt.
Codex bestätigte als korrekt: Jobzahl und -reihenfolge, Run-IDs, Lader-Hashes, Richtung von `cost()`, Binomialtest, max-Regel, Holm, Selbsttest-Arithmetik. **Offen vor dem Einfrieren:** eine kurze Codex-Nachprüfung der geänderten Stellen und der Selbsttest im Fenster.

**Codex-Nachprüfung (Sitzung 32, `R6_codex_recheck_s32.txt`):** Punkte 1, 2 und 5 geschlossen. Neu gemeldet: (MAJOR) Die Sensitivität bei halbem Effekt stand nicht im Skript. Jetzt `power_half_effect_shift` in `R6_pilot_power.py`/`.json`. (MINOR) n = 30 lag über der exakten Aufzählung bis n = 22. Jetzt ist der Test exakt per Meet-in-the-Middle (bis n = 40), die Selbsttests vergleichen gegen rohe Aufzählung (n = 1, 7, 10) und prüfen den Fall n = 30. Stopp-Semantik, Lader-Gleichheit, Blockarithmetik und die S1-Regeln bestätigte Codex als korrekt.

**Codex-Nachprüfung 2 (Sitzung 32, 21:09, `R6_codex_recheck2_s32.txt`, nur S2):** keine Befunde. `s2_rule` entspricht dem Text, die Selbsttest-Arithmetik stimmt; eine als post hoc gekennzeichnete Sekundärhypothese vor dem Einfrieren ist zulässig.

---
id: EXP-119
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, lm-leiter, befund/positiv]
---
# EXP-119: Lernt ein kleines Sprachmodell Rechenfakten aus konstruierten Splits früher als aus zufälligen? (R5 im LM, Pilot, 2 Seeds)

Zurück: [[LAB]] · [[FINDINGS]] (R5: konstruierte Splits groken ≈ ×6.5 früher als Zufall; Verallgemeinerung, Programm A, Regel 15c/20e) · [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] · [[confirm/LM1_REGISTRATION|LM1]] · [[JOURNAL]] Sitzung 52

**Bezug zu FINDINGS:** R5 ist eine der drei Hauptaussagen des Paper-Haupttexts, bisher nur im Spielzeugmodell. Die LM-Leiter prüft bisher nur K2 (Δ_pow). Frage: Überträgt sich der Zeitvorteil konstruierter Trainingsmengen auf ein von Grund auf trainiertes LM? Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 52, 17:00 Berlin gemessen, vor jedem Lauf)

- **Aufbau:** unveränderter Trainer `lm_stage2.py` (wie LM1; Hash in LM1 gebunden), K = 19 Rechensätze je Sequenz, `--loss answer`, 6000 Schritte. Modell-Seeds **3866/3867** (per Dateisuche unbenutzt) mit den EXP-102-Splits der Seeds 3806/3807: **F, G** (P1-Konstruktion, Zielanteil der Maske ≈ 0.18, etwa R5-Stufe E2) und **R** (gleichverteilt, gleiche Größe 3831, gleicher Pool). Gemeinsame zurückgehaltene Testmenge `design.build(seed)["test"]` (2554 Fakten, disjunkt zu F, G und R, geprüft). Alle Arme eines Modell-Seeds teilen Init, Text, Schablonen und Einfügepositionen.
- **Messgrößen** (`analyze.py`, Docstring): t_test = erster (interpolierter) Schritt mit Genauigkeit auf zurückgehaltenen Fakten ≥ 0.5; t_train ebenso für Trainingsfakten; q = t_test(R) / Mittel(t_test(F), t_test(G)); R ohne Kreuzung bis 6000 → q als untere Schranke 6000/Mittel.
- **Lesarten:** „constructed faster“: q ≥ 1.5 in beiden Seeds. „no advantage“: q ≤ 1.15 in beiden Seeds (R nicht zensiert). Sonst „unclear“. F oder G ohne Kreuzung → „not learned (budget)“ für diesen Seed, keine Lesart.
- **Erwartung, ehrlich unsicher:** Im Spielzeugmodell liegt der Vorteil fast ganz in der Lücke nach der Memorisation; im LM lernen Trainings- und zurückgehaltene Fakten fast gleichzeitig (EXP-114: 0.80 / 0.33 bei Schritt 2000). Es gibt also keine direkte Entsprechung der Grokking-Lücke; beide Ausgänge sind plausibel.
- **Was dagegen spräche:** „no advantage“ → Der Zeitvorteil (R5) ist dann eine Eigenschaft des Grokking-Regimes des Spielzeugmodells, nicht der Datenauswahl allgemein; im Paper als Grenze.
- **Grenzen, vorab:** Keine je Antwort abgeglichene Kontrolle D wie in R5 (Regel 20e); die P1-Splits tragen die Ziele auch in den Zählungen von a und b. Ein Vorteil wäre deshalb nicht von einem Häufigkeitseffekt getrennt (Folgefrage: flache Splits wie EXP-115 gegen deren Zufallsgegenstück).
- **Budget:** 6 Läufe à 6000 Schritte (≈ 30–40 min je Lauf bei 2–3 LM-Läufen gleichzeitig), GPU-Dienst `36_exp119_lm_r5.jobs`, workers 2, gpu_gb 3.5, job_minutes 240. Läuft nach LM1 und R4-Repro.
- **Bereits gesehene Daten:** EXP-114 (Seed 3862/Split 3802, K 19: Lernbeginn ≈ 1750–2000) und LM1-Zwischenstände (Lernbeginn ≈ 2000–3250); EXP-102/112 (Stufe 1, anderes Modell) liefen mit den Splits 3806/3807, deren Zeiten habe ich für diesen Entwurf nicht gelesen. Beeinflusst: Budget 6000 (wie LM1), Schwelle 0.5.

## Befehle

```
python lab/experiments/EXP-119-lm-speed-r5/make_jobs.py > lab/queue/inbox/36_exp119_lm_r5.jobs     # erledigt (Tests geschrieben)
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-119-lm-speed-r5/analyze.py --selftest   # grün
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-119-lm-speed-r5/analyze.py
```

**Literatur (Sitzung 52, 17:01 gemessen; WebSearch, 2 Abfragen: „language model trained from scratch arithmetic facts selection training data Fourier frequencies speeds up learning modular addition 2026“, „grokking data selection structured training subset accelerates generalization language model arithmetic "training set composition" speed“):** Nächstverwandt: Zhou et al. 2024 (arXiv 2406.03445; LMs von Grund auf nutzen bei Addition nur niederfrequente Merkmale, vortrainierte Embeddings retten), Datenaugmentation/Transfer beschleunigen Grokking in Spielzeugaufgaben (arXiv 2405.16658; GrokTransfer 2504.13292), Howe 2026b (Prior-Struktur). Keine Arbeit gefunden, die in einem von Grund auf trainierten LM die Auswahl der Rechenfakten (konstruiert gegen zufällig, gleiche Größe) auf den Lernzeitpunkt prüft (vorläufig, „nach unserer Suche nicht gefunden“).

**Nach dem Einfrieren gesehen (Sitzung 52, 17:02; ändert keine Lesart):** In EXP-102 Stufe 1 (Textformat, 2000 Schritte, Splits 3800–3809) generalisieren unter „allnb“ F/G in 20/20 Läufen, R in 0/10; unter „tieallnb“ F/G 20/20, R 2/10 ([[JOURNAL]] Sitzung 52, Zyklus 5).

**Ergänzung vor jedem EXP-119-Lauf (Sitzung 52, 18:23 gemessen; beschreibend, keine Lesart):** je Lauf Spearman ρ zwischen dem Maskenspektrum des eigenen Splits (M0) und der Leistung der Zahl-Zeilen am Ende (R4-Analogon: prägt auch ein Zufallssplit die Frequenzen des LM?). Smoke an EXP-114 (Seed 3862, Splits 3802, K 19, 4000 Schritte; damit gesehen): ρ = 0.37 (F), 0.13 (G). Selbsttest weiter grün.

## Ergebnis (Sitzung 54, 23:24 Berlin gemessen; 6/6 Läufe, Dienst-Job 36_exp119_lm_r5; `summary.json`; Exploration, 2 Seeds)

**Vorab-Lesart: „constructed faster“** (q ≥ 1.5 in beiden Seeds). R erreicht 0.5 auf zurückgehaltenen Fakten in keinem Seed bis 6000 → q ist eine untere Schranke: **q ≥ 3.15** (Seed 3866) und **q ≥ 2.61** (Seed 3867).

| Seed | Arm | t_train (≥ 0.5) | t_test (≥ 0.5) | zurückgehalten bei 6000 | ρ(Maske, Zahl-Zeilen) |
|---|---|---|---|---|---|
| 3866 | F | 1872 | 1915 | 0.989 | 0.33 |
| 3866 | G | 1873 | 1890 | 0.983 | 0.42 |
| 3866 | R | 1870 | — (zensiert) | 0.333 | 0.57 |
| 3867 | F | 2115 | 2177 | 0.977 | 0.28 |
| 3867 | G | 2343 | 2421 | 0.988 | 0.21 |
| 3867 | R | 2112 | — (zensiert) | 0.322 | 0.29 |

**Der vorab formulierte Erklärungssatz ist widerlegt** ([[paper/LM1_DEUTUNGEN]], Satz „constructed faster“, zweiter Teil: „weil das LM Trainings- und zurückgehaltene Fakten fast gleichzeitig lernt, ist das eine Verschiebung des Lernbeginns, keine kürzere Grokking-Lücke“). Beschreibend (nicht vorab festgelegt): Die **Trainingsfakten** lernt R genauso früh wie F/G (1870 gegen 1872/1873; 2112 gegen 2115/2343). Nur die **zurückgehaltenen** Fakten folgen bei R nicht: bis 6000 Schritte ≈ 0.33, also mindestens ≈ 3900 Schritte Lücke nach der Memorisation. Im LM erzeugt der Zufallssplit demnach eine grokking-artige Lücke, die konstruierten Splits nicht (dort 17–78 Schritte). Der Vorteil liegt also in der Lücke, nicht im Lernbeginn (ob das im Spielzeugmodell für R5 genauso ist, ist im Paper nicht belegt; die dortige Lücken-Zerlegung betrifft die Wechselkosten, Anhang F). Die frühere Beobachtung „im LM keine Grokking-Lücke“ (Sitzung 52, post hoc, 9 Läufe) galt nur für konstruierte Splits.
**Grenzen (vorab und neu):** 2 Seeds, Exploration; keine je Antwort abgeglichene Kontrolle D, die P1-Splits tragen die Ziele auch in den Zahl-Häufigkeiten, ein Häufigkeitseffekt ist deshalb nicht ausgeschlossen (Folgefrage wie vorab: flache Splits gegen ihr Zufallsgegenstück, vgl. BACKLOG LM2). 6000 Schritte: Ob R später generalisiert, ist offen (ein abgebrochener Lauf beweist nichts). ρ bei R 0.57 / 0.29 (beschreibend; R4-Analogon, kein Befund).

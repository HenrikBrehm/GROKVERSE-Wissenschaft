---
id: EXP-119
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
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

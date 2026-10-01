---
id: EXP-139
status: laufend
datum: 2026-10-01
tags: [exp/laufend, neu/kandidat]
verwandt: ["[[experiments/EXP-137-modulus-density/README|EXP-137]]", "[[confirm/R14_REGISTRATION|R14]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-139: Paarzahl statt Anteil? Generalisierung und Steuerung bei p = 401/503/613 mit fester Paarzahl (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds × F/G je Zelle), keine Bestätigung.** Folge von [[experiments/EXP-137-modulus-density/README|EXP-137]] und [[confirm/R14_REGISTRATION|R14]]; Kandidat [[NOVEL_DIRECTIONS]] N63.

**Bezug zu FINDINGS:** K2 (Programm A, Regel 20b, LeDoux-Einwand). R14 bestätigte K2 bei add 307 mit 10 % Daten (9425 Paare) nach der Generalisierung. In EXP-137 generalisierte add 211 mit 4452 Paaren (10 %) nie, add 307 mit 9425 Paaren (10 %) immer – das spricht für eine Mindest-*Paarzahl* statt eines Mindest-*Anteils*, war aber nicht getrennt. Ist es die Paarzahl, dann erreicht man mit größerem p kleinere Anteile (Richtung LeDoux: p = 9973, 0.3 %), und die Frage „steuert die Menge auch bei kleinem Anteil?“ wird prüfbar. Begründung gegen Regel 15b: stärkster offener Gutachter-Einwand, GPU sonst leer (Regel 20i).

## Vorab (Sitzung 68, 2026-10-01, geschrieben 08:33–08:38 Berlin, vor jedem Blocklauf)

- **Frage 1 (Generalisierung):** Generalisiert das Netz mit fester Paarzahl N = 9425 auch bei p = 401/503/613 (Anteil 5.9 / 3.7 / 2.5 %)? Und bei gleichem Anteil (3.73 %): unterscheiden sich p 503 mit N = 9425 und p 613 mit N = 14 000?
- **Frage 2 (Steuerung, K2):** Wo generalisiert wird – steuern die konstruierten Splits die Frequenzen nach der Generalisierung (placebo-kalibriert wie EXP-137/R14)?
- **Hypothesen:** (H1) die Paarzahl trägt: alle N = 9425-Zellen generalisieren im Budget; (H2) wo generalisiert wird, steuert die Menge.
- **Konkurrenzmodelle:** (A) Mindestanteil: Generalisierung bricht mit sinkendem Anteil, unabhängig von N; (L) LeDoux-Lesart: bei kleinem Anteil legt etwas anderes als die Menge die Frequenzen fest → Δ_pow nach gen im Placebo-Band.
- **Aufbau:** unveränderter Trainer `freq_ban.py` (1 Schicht, AdamW lr 1e-3, wd 1, Full-Batch, GPU), Test = Komplement. EXP-043-Konstruktion (ε = 2), nur `TRAIN_FRAC` = N/p² überschrieben (innerhalb `build`, danach wiederhergestellt). Zellen p ∈ {401, 503, 613} × N ∈ {9425, 14 000}; Anteile 5.86/8.71 %, 3.73/5.53 %, 2.51/3.73 %. Seeds 13900–13902 (neu), F und G mit disjunkten Zielen. Höchstens 30 000 Schritte, Stopp 2000 nach gen, Schnappschüsse 50, 250, 500 und alle 1000 Schritte. 36 Läufe.
- **Vorab-Rechnung (`make_jobs.py --mask` → `mask_prediction_s68.json`, kein Lauf):** Top-5 der Maske = Ziele in allen 36 Splits; Masken-Δ 0.84–0.90 (613/9425) bis 1.63–1.68 (401/14 000), fällt mit dem Anteil.
- **Messung je Arm/Seed (wie EXP-137):** gen = `transitions.primary.generalization.first_crossing_step` (Test ≥ 0.95); Δ_pow an den ersten eigenen Schnappschüssen ≥ gen + 1000; Placebo-q90/q99 aus 2000 zufälligen disjunkten 5+5-Mengen außerhalb F ∪ G an denselben Spektren.
- **Zellenlesart (kalibriert, wie EXP-137):** < 2 Seeds mit beiden Armen generalisiert → „kein Lernen im Budget“; ≥ 2, aber < 2 auswertbar → „nicht auswertbar“; alle auswertbaren Δ_pow > q99 → „steuert“; mindestens die Hälfte ≤ q90 → „nicht unterscheidbar“; sonst „unklar“. Generalisiert heißt eine Zelle bei ≥ 2 Seeds mit beiden Armen generalisiert.
- **Lesart Frage 1:** alle drei N = 9425-Zellen generalisiert → „Paarzahl trägt (bis 2.5 %)“; 401/9425 generalisiert, aber 613/9425 nicht → „Grenze zwischen 5.9 % und 2.5 % bei N = 9425“ und zusätzlich der Gleich-Anteil-Kontrast: 613/14 000 generalisiert, 503/9425 nicht → „bei gleichem Anteil hilft mehr Paare“; beide gleich → „Gleich-Anteil-Kontrast unentschieden“; keine N = 9425-Zelle generalisiert → „Paarzahl 9425 reicht oberhalb p 307 nicht“.
- **Lesart Frage 2:** alle auswertbaren Zellen „steuert“ → „K2 hält bis zum kleinsten generalisierenden Anteil“ (Anteil nennen); eine auswertbare Zelle „nicht unterscheidbar“ → „Steuerung schwindet bei kleinem Anteil“ (Zellen nennen); keine auswertbare Zelle → „kein Lernen im Budget“; sonst „beschreibend“.
- **Beschreibend:** gen-Schritte gegen Anteil und N, Δ_pow bei 2000 und am letzten Schnappschuss vor gen, Top-5-Überlappung, Spearman(Masken-Δ, Δ_pow nach gen).
- **Was gegen H1/H2 spräche:** N = 9425-Zellen generalisieren bei 503/613 nicht (gegen H1); Δ_pow nach gen ≤ q90 in der Hälfte der Seeds einer Zelle (gegen H2).
- **Budget/Abbruch:** Smoke (Seed 13999, außerhalb des Blocks, p 613/9425, 1000 Schritte): 0.039 s/Schritt allein, **7.6 GB Grafikspeicher** (Testauswertung in einem Stück) → Jobdateien je p: 401 `gpu_gb=3.0` (4 Worker), 503 `5.0` (2), 613 `8.0` (1); `job_minutes=150`. Schlimmster Fall 613: 12 × ≈ 20–40 min nacheinander. Ein abgebrochener oder nicht generalisierter Lauf beweist nicht, dass Generalisierung unmöglich ist (30 000 Schritte sind ein Budget).
- **Grenzen:** eine Architektur, ein Optimierer; p ≤ 613, Anteil ≥ 2.5 % (LeDoux 0.3 % bei p = 9973 bleibt weit weg); 3 Seeds; additive Salze wie EXP-043 (Pilot); Einbettungsenergie, keine Ablation.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-136/137 und R14 (alle Ergebnisse) – beeinflusst: Wahl N = 9425 (307/10 % generalisierte) und 14 000, die drei p, Budget 30 000, Messpunkt und Placebo-Lesart. Smoke (s. o.): Top-5 nach 1000 Schritten = eigene Ziele (Auswendiglernphase), Test 0.004; nur Speicher und Tempo verwendet.

## Befehle

```
python lab/experiments/EXP-139-pair-count/make_jobs.py > lab/queue/staging/52_exp139_pairs.jobs   # dann je p aufgeteilt (52a/b/c)
python lab/experiments/EXP-139-pair-count/make_jobs.py --check
python lab/experiments/EXP-139-pair-count/make_jobs.py --mask
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-139-pair-count/analyze.py [--selftest]
```

## Ergebnis

Offen (läuft beim GPU-Dienst als `52a_exp139_p401`, `52b_exp139_p503`, `52c_exp139_p613`).

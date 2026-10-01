---
id: EXP-137
status: laufend
datum: 2026-10-01
tags: [exp/laufend, neu/kandidat]
verwandt: ["[[experiments/EXP-136-large-modulus/README|EXP-136]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-137: Steuert die Trainingsmenge bei größerem Modulus auch mit weniger Daten, wenn das Netz noch generalisiert? (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds × F/G je Zelle), keine Bestätigung.** Folge von [[experiments/EXP-136-large-modulus/README|EXP-136]]; Kandidat [[NOVEL_DIRECTIONS]] N63.

**Bezug zu FINDINGS:** K2 (Programm A, Regel 15c/20b). EXP-136 zeigte K2 bei add 211/307 mit 30 % Daten; mit 3831 Paaren (8.6 % / 4.1 %) generalisierte kein Lauf in 20 000 Schritten, die Frage „Steuerung bei geringer Datendichte“ blieb daher unbeantwortbar. LeDoux 2026 (arXiv 2603.25047) berichtet bei p = 9973 und 0.3 % Daten, die Frequenz entstehe unabhängig von der Zusammensetzung der Trainingsmenge. Dieser Pilot sucht zwischen 4–9 % und 30 % die Dichte, bei der das Netz noch generalisiert, und misst dort die Steuerung **nach** der Generalisierung. Begründung gegen Regel 15b (kein automatischer Mini-Versuch): Das ist der stärkste offene Gutachter-Einwand (Regel 20b), und die GPU würde sonst nach EXP-128/129 leer laufen (Regel 20i).

## Vorab (Sitzung 67, 2026-10-01, 05:45 Berlin gemessen; vor jedem Blocklauf)

- **Frage:** Geben die konstruierten Splits (EXP-043, ε = 2) die gelernten Frequenzen bei add p = 211 und 307 auch mit 10 %, 15 % und 20 % Daten vor, gemessen nach der Generalisierung?
- **Hypothese:** ja, in allen Zellen, in denen generalisiert wird; Δ_pow kleiner bei weniger Daten (Maskensignal kleiner).
- **Konkurrenzmodell (LeDoux-Lesart):** Mit abnehmender Dichte legt etwas anderes als die Menge die Frequenzen fest → |Δ_pow| ≤ 1 nach der Generalisierung bei kleinen Anteilen.
- **Aufbau:** unveränderter Trainer `freq_ban.py` (1 Schicht, AdamW lr 1e-3, wd 1, Vollbatch, GPU), Test = Komplement. Seeds 13700–13702 (neu), je Zelle F und G mit disjunkten Zielen; nur `TRAIN_FRAC` von `make_split.py` wird überschrieben (wie EXP-136). Höchstens 30 000 Schritte, Stopp 2000 Schritte nach der Generalisierung, W_E-Schnappschüsse bei 50, 250, 500 und alle 1000 Schritte. 2 p × 3 Anteile × 3 Seeds × 2 Arme = 36 Läufe.
- **Messgröße (primär):** Δ_pow (wie P1/EXP-136) am ersten gemeinsamen Schnappschuss ≥ max(gen_F, gen_G) + 1000; ein Seed zählt nur, wenn beide Arme generalisieren (`first_crossing_step` des primären Generalisierungsübergangs).
- **Lesart je Zelle (`analyze.py`, vor jedem Blocklauf geschrieben):** < 2 auswertbare Seeds → „kein Lernen im Budget“; sonst unter den auswertbaren: alle Δ_pow > 1 → „steuert“; mindestens die Hälfte |Δ_pow| ≤ 1 → „bricht“; sonst „unklar“.
- **Gesamtlesart je p (Pilot, beschreibend über die Anteile):** alle auswertbaren Zellen „steuert“ und kleinster auswertbarer Anteil ≤ 15 % → „K2 hält bei p mit weniger Daten“; kleinste auswertbare Zelle „bricht“, f20 „steuert“ → „Steuerung schwindet mit der Dichte“; keine auswertbare Zelle → „kein Lernen im Budget“; sonst „beschreibend“.
- **Beschreibend:** Δ_pow bei 2000 (wie EXP-136), Generalisierungsschritte, End-Genauigkeit, Top-5-Überlappung, Mittel je Zelle (steigt Δ_pow mit dem Anteil?).
- **Vorhersage erster Ordnung (vorab, `make_jobs.py --mask` → `mask_prediction_s67.json`, kein Lauf):** Masken-Δ je Seed: p 211 f10 1.09–1.24, f15 1.61–1.63, f20 1.95–2.07; p 307 f10 1.45–1.50, f15 1.98–2.02, f20 2.41–2.45. Vorhersage (beschreibend): Δ_pow nach Generalisierung steigt je p mit dem Anteil; Spearman(Masken-Δ, Δ_pow) > 0. Vorsicht aus der EXP-136-Prüfung: Dort kam die Korrelation fast nur aus dem Gegensatz generalisiert/auswendig (innerhalb der 30-%-Zellen −0.26); hier zählen nur generalisierte Seeds, die Prüfung ist also strenger.
- **Was dagegen spräche:** |Δ_pow| ≤ 1 nach der Generalisierung in mindestens der Hälfte der Seeds einer Zelle.
- **Budget/Abbruch:** gemessen p = 211, 10 %: 0.069 s/Schritt unter Last (Lader-Test); p = 307, 30 % in EXP-136: 0.13–0.16 s/Schritt. Schlimmster Fall (kein Lauf generalisiert) ≈ 35–75 min je Lauf; 5 Worker, `gpu_gb=1.5`, harte Grenze 120 min je Lauf. Ein abgebrochener oder nicht generalisierter Lauf beweist nicht, dass Generalisierung unmöglich ist.
- **Grenzen:** eine Architektur, ein Optimierer; p ≤ 307, Anteile ≥ 10 % (weit weg von LeDoux' 0.3 %); Paarzahl und Anteil gekoppelt; Seeds über additive Salze wie EXP-043/136 (Pilot; eine Bestätigung bräuchte getrennte Ströme, Astra 5); Einbettungsenergie, keine Ablation.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** (1) EXP-136 (alle Ergebnisse): Wahl der Anteile 10/15/20 % zwischen „nie generalisiert“ (4–9 %) und „schnell generalisiert“ (30 %, gen 150–575), Budget 30 000 statt 20 000, Primärmessung nach der Generalisierung statt bei 2000. (2) Lader-Test nach dem Schreiben der Lesarten (`raw_loadtest/`, 1000 Schritte): Seed 13700, p = 211, 10 %, nur Arm F: bis 1000 nicht generalisiert, Top-5 am Ende = eigene Ziele, 0.069 s/Schritt. Δ_pow wurde nicht berechnet (nur ein Arm). Der Block wiederholt diesen Lauf.

## Befehle

```
python lab/experiments/EXP-137-modulus-density/make_jobs.py > lab/queue/staging/48_exp137_density.jobs && mv lab/queue/staging/48_exp137_density.jobs lab/queue/inbox/
python lab/experiments/EXP-137-modulus-density/make_jobs.py --check
python lab/experiments/EXP-137-modulus-density/make_jobs.py --mask
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-137-modulus-density/analyze.py [--selftest]
```

## Ergebnis

Noch nicht ausgeführt (beim GPU-Dienst als `48_exp137_density`).

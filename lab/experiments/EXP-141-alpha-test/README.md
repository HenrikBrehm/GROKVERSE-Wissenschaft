---
id: EXP-141
status: laufend
datum: 2026-10-01
tags: [exp/laufend, neu/kandidat]
verwandt: ["[[experiments/EXP-139-pair-count/README|EXP-139]]", "[[experiments/EXP-140-random-at-edge/README|EXP-140]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-141: Daten je Zahl (N/p) oder Margin-Skalierung (N/p^{5/3})? Ein trennender Test bei p = 503 (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds × F/G je Zelle), keine Bestätigung.** Folge von [[experiments/EXP-139-pair-count/README|EXP-139]] (Nachträge b/c); [[NOVEL_DIRECTIONS]] N64.

**Bezug zu FINDINGS:** K2 bei geringer Dichte (LeDoux-Einwand, Regel 20b). In den vergleichbaren 30 000-Schritt-Zellen trennt nur eine Schwelle N/p^α mit α ∈ [0.54, 1.78] Lernen von Nicht-Lernen. Zwei naheliegende Werte: α = 1 (jede Zahl-Einbettungszeile sieht ≈ 2N/p Paare je Schritt; Schwelle zwischen 27.8 [503/14 000 nein] und 30.7 [307/9425 ja]) und α = 5/3 (Margin-Theorie, Õ(p^{5/3}) Daten; Schwelle zwischen 0.595 [211/4452 nein] und 0.642 [401/14 000 ja]). EXP-139 trennt sie nicht. Begründung Regel 15b: ein einziger, scharf trennender Test statt weiterer Zellen; ersetzt in der Warteschlange den Vorrang der wenig informativen p-613-Zellen.

## Vorab (Sitzung 68, 2026-10-01, geschrieben ≈ 10:15–10:22 Berlin, vor jedem EXP-141-Lauf)

- **Frage:** Generalisiert add 503 mit N = 16 100 (N/p 32.0; N/p^{5/3} 0.51; 6.36 %) bzw. 18 100 Paaren (36.0; 0.57; 7.15 %) im Budget von 30 000 Schritten?
- **Vorhersagen:** α = 1 → beide ja; α = 5/3 → beide nein.
- **Aufbau:** identisch zu EXP-139 (`make_jobs.py` geklont, nur Seeds 13910–13912, p = 503, N, Pfade, Kopfzeile geändert): EXP-043-Konstruktion ε = 2, F/G disjunkt, `freq_ban.py` unverändert, GPU, höchstens 30 000 Schritte, Stopp 2000 nach gen. 12 Läufe. Vorab-Rechnung (`--mask`): Masken-Top-5 = Ziele in allen 12 Splits, Masken-Δ 1.45–1.65.
- **Lesart Frage 1 (`analyze.py`, geklont, nur q1/Selbsttest/Pfade/Placebo-Salz geändert):** Zelle generalisiert = ≥ 2 Seeds mit beiden Armen. Beide → „passt zu α ≈ 1 (Daten je Zahlzeile), nicht zu p^{5/3}“; keine → „passt zu p^{5/3}, nicht zu α = 1 mit Schwelle ≤ 30.7“; nur 18 100 → „Schwelle in N/p bei p 503 zwischen 32 und 36: unentschieden“; nur 16 100 → „nicht monoton: unklar“.
- **Frage 2 (Steuerung):** wie EXP-139 (placebo-kalibriert, Messung ≥ gen + 1000).
- **Was dagegen spräche (je Lesart):** siehe Vorhersagen; ein Ergebnis gilt nur innerhalb von 30 000 Schritten (ein mit p wachsendes Budget ist nicht ausgeschlossen).
- **Budget:** ≈ 7 GB je Lauf (gemessen bei EXP-139 p 503), daher einer gleichzeitig; 0.03–0.05 s/Schritt → ≤ 25 min je Lauf, ≤ 5 h gesamt, kürzer bei Generalisierung.
- **Grenzen:** ein p, 3 Seeds, ein Budget, eine Architektur; additive Salze (Pilot).
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** alle EXP-136/137-Ergebnisse, EXP-139 p 401 (beide Zellen ausgewertet), 503/9425 Seed 13900 F/G und 503/14 000 Seeds 13900 F/G, 13901 F (alle nicht generalisiert, Test ≤ 0.002) – sie legten die Wahl N/p 32/36 fest (knapp über der α = 1-Schwelle). Unabhängige Prüfung von Nachtrag b (Budgets).

## Befehle

```
python lab/experiments/EXP-141-alpha-test/make_jobs.py > lab/queue/staging/52bzz_exp141_alpha.jobs
python lab/experiments/EXP-141-alpha-test/make_jobs.py --check
python lab/experiments/EXP-141-alpha-test/make_jobs.py --mask
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-141-alpha-test/analyze.py [--selftest]
```

## Ergebnis

Offen (beim GPU-Dienst als `52bzz_exp141_alpha`, nach EXP-140, vor EXP-139 p 613).

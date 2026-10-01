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

## Vorab (Sitzung 68, 2026-10-01, geschrieben 10:13–10:16 Berlin (gemessen), vor jedem EXP-141-Lauf)

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

## Nachtrag a (Sitzung 69, 2026-10-01, 11:22 Berlin (gemessen), vor 10 der 12 Läufe): Iso-Zeit-Exponent (beschreibend)

Die Schwellenfrage (lernt die Zelle in 30 000 Schritten?) ist grob; der Median-gen-Schritt g ist stetig. Zusätzliche, **beschreibende** Frage: Wie wächst die Paarzahl N_T(p), bei der der Median g = T ist, mit p (N_T ~ p^α_T)? α_T ist nicht das Schwellen-α aus EXP-139 Nachtrag b. Verfahren fest in `iso_time_s69.py` (Docstring): Zellmedian über 6 Arme (nicht generalisiert = > 30 000; nur bei ≥ 4/6), lokale Steigung s = d log g / d log N aus p 211/307 (−7.18, −6.87; s = −7.02), N_T per log-Interpolation zwischen Zellen (sonst eine Zelle + s), Fit über p 211/307/401.
- **Vorhersage (nur bereits gesehene Daten, EXP-141 ausgeschlossen; `--seen-only`):** T = 5000: N_T = 6547 / 10 184 / 14 214 (p 211/307/401), α_T = 1.21; N_T(503) ≈ 18 600; Median g bei 503/16 100 ≈ 13 800, bei 503/18 100 ≈ 6 100 (T = 3000/8000 praktisch gleich).
- **Lesart nach EXP-141:** α_T(401 → 503) aus den EXP-141-Zellen: 1.0–1.4 → „Iso-Zeit-Exponent konstant (≈ 1.2)“; > 1.4 → „steigt mit p“; < 1.0 → „fällt“. Zur Einordnung: α_T 1.0 bzw. 1.4 entsprechen bei 18 100 einem Median g ≈ 4 500 bzw. ≈ 8 500.
- **Schon gesehen:** Seed 13910 bei 16 100 (gen 23 100 / 25 600, beide über der Vorhersage 13 800 – ein Hinweis Richtung „steigt“, aber ein Seed; bei s ≈ −7 bedeutet ±10 % in N einen Faktor 2 in g). Grenzen: 4 p-Werte, je 3 Seeds, Steigung aus zwei p geborgt, T willkürlich (Empfindlichkeit berichtet).

## Ergebnis

Offen (beim GPU-Dienst als `52a6_exp141_alpha`; zuerst als `52bzz_…` abgelegt und vor dem ersten Start umbenannt).

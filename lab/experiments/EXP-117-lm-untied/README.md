---
id: EXP-117
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, lm-leiter]
---
# EXP-117: Sprachmodell mit ungekoppelten Ein-/Ausgabe-Embeddings – steuert die Faktenauswahl die Eingabe-Zeilen?

Zurück: [[LAB]] · [[FINDINGS]] · Bezug [[confirm/LM1_REGISTRATION|LM1]] (gekoppelte Embeddings, 10 frische Seeds), [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] (K = 19, 1 Seed, Δ_pow 5.6), [[experiments/EXP-115-lm-flat-marginals/README|EXP-115]] (flache Zahl-Häufigkeiten) · [[JOURNAL]] Sitzung 51

**Bezug zu FINDINGS:** Verallgemeinerung von K2 auf ein kleines LM (Programm A, Regel 20e); Kontrolle der Messgröße für LM1 (Vorbehalt Sitzung 50, 12:42: mit gebundenen Embeddings sind die Zahl-Zeilen zugleich Ausgabevektoren, ein positives Δ_pow kann über die Ausgabeseite entstehen). Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 51, vor jedem Lauf)

- **Frage:** Liegt die Steuerung im LM in der Eingabe-Repräsentation der Zahlen oder nur in den Ausgabevektoren? Mit getrennten Matrizen lässt sich das messen: Δ_pow auf den 113 Zahl-Zeilen der Eingabe-Einbettung (Δ_in) und der Ausgabeschicht (Δ_out).
- **Hypothese:** Δ_in > 1 (die Eingabe-Repräsentation wird gesteuert wie im Spielzeugmodell, das gar keine gebundenen Embeddings hat); Δ_out beschreibend.
- **Aufbau:** `lm_untied.py` = Kopie von `lm_stage2.py` (der eingefrorene Trainer bleibt unverändert, sein Hash steckt in EXP-113/LM1) mit eigener Ausgabeschicht `head` (ohne Bias, Init N(0, 0.02), Weight Decay wie alle Matrizen) und Snapshots beider Zeilensätze; Diff: 10 Zeilen (Journal). Selbsttest (inkl. bitgleichem Wiederanlauf) grün, Sitzung 51. `--arith-facts 19 --loss answer --steps 6000` (wie LM1; EXP-114 lernte gebunden bei ≈ 2000). Modell-Seeds 3862/3863 ↔ EXP-102-Splits 3802/3803, Testmengen von EXP-113 (`tests/`). Nicht gepaart mit den gebundenen Läufen (die zusätzliche Schicht verändert die Init-Zufallsfolge); Vergleich mit EXP-114 nur beschreibend. 4 Läufe als `33_exp117_untied.jobs` (1 Worker, gpu_gb 3.5).
- **Budget/Abbruch:** ≈ 0.3–0.5 s/Schritt → ≈ 30–50 min je Lauf, 4 Läufe nacheinander ≈ 2–3 h; harte Grenze 240 min je Lauf. Abbruch bei NaN (Trainer) oder Absturz.
- **Lesarten (`analyze.py`, vor dem Lauf geschrieben):** Vorrang „nicht gelernt (Budget)“, wenn die Trainingsfakten-Genauigkeit in ≥ 3/4 Läufen < 0.1 ist; „Eingabe gesteuert“: Δ_in > 1 in beiden Seeds und zurückgehaltene Fakten > 0.5 in ≥ 3/4; „nur Ausgabe gesteuert“: Δ_in ≤ 1 in beiden, Δ_out > 1 in beiden (Fakten gelernt); „keine Steuerung“: |Δ_in|, |Δ_out| ≤ 1 in beiden (Fakten gelernt); sonst „unklar“.
- **Was gegen die Hypothese spräche:** „nur Ausgabe gesteuert“ oder „keine Steuerung“ → LM1-Werte wären als Eigenschaft der gebundenen Ausgabevektoren zu lesen, nicht der Zahl-Repräsentation (so in Anhang K berichten).
- **Bereits gesehene Daten:** EXP-113/114 (gebunden, Seeds 3862/3802), EXP-102/112 (Stufe 1 auf 3802/3803), LM1-Zwischenstände (Logzeilen der Läufe 0/1: Genauigkeiten, keine Δ_pow). Davon beeinflusst: K, Budget, Seeds.

**Zwischenblick (Sitzung 52, 17:35; 1 von 2 Seeds, keine Lesart):** Seed 3862: Δ_in 6.44 (Eingabe), Δ_out 4.04 (Ausgabeschicht), zurückgehaltene Fakten 0.97 / 0.92 (`peek_seed3862_s52.json`). Die Vorab-Lesart folgt erst mit Seed 3863 über `analyze.py`.

## Ergebnis (Sitzung 52, 19:04 Berlin gemessen; 4/4 Läufe, Exploration, 2 Seeds; `summary.json`)

Vorab-Lesart **„Eingabe gesteuert“**: Δ_in (Eingabe-Embedding, Zahl-Zeilen) **6.44** (Seed 3862) und **5.54** (Seed 3863), beide > 1; zurückgehaltene Fakten 0.97 / 0.92 und 0.95 / 0.95 (4/4 > 0.5); Trainingsfakten 0.99–1.00; Generalisierung (≥ 0.95, F / G): Seed 3862 3000 / nicht erreicht (Ende 0.92), Seed 3863 3750 / 3000. Hinweis: Der Schlüssel `reading` oben in `summary.json` stammt aus `analyze_pilot.py` (EXP-105-Lesart); maßgeblich ist `reading_exp117`. Unabhängig geprüft (Claude-Agent, nur lesend): Zahlen richtig; „output rows were steered too“ im Paper auf „Δ_out also positive (descriptive)“ abgeschwächt. Beschreibend: Ausgabeschicht Δ_out 4.04 und 4.74. Deutung nach [[paper/LM1_DEUTUNGEN]]: Mit ungekoppelten Ein-/Ausgabe-Embeddings wird die Eingabe-Repräsentation der Zahlen gesteuert; die LM-Steuerung ist also nicht nur eine Eigenschaft gemeinsamer Ausgabevektoren. Grenzen: 2 Seeds, P1-Splits (Häufigkeiten tragen die Ziele mit), nicht nachgerechnet.

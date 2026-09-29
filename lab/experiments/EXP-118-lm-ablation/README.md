---
id: EXP-118
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/positiv, lm-leiter]
---
# EXP-118: Tragen die gesteuerten Frequenzen im kleinen LM die Fakten? (Ablation an fertigen Modellen, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (K2-Funktion, Programm A) · Modelle aus [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] und [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] · [[JOURNAL]] Sitzung 51

**Bezug zu FINDINGS:** K2-Funktion (im Spielzeugmodell: Nanda-Ablation „Ziele funktional“ 20/20 je Aufgabe) im LM. Greift die Annahme an, Δ_pow im LM messe etwas Funktionales (Rückblick Sitzung 51, 15:15). Exploration an bekannten Modellen, kein Training.

## Vorab (Sitzung 51, vor jeder Ablation; Lesarten im Docstring von `ablate.py`)

- **Frage:** Fällt die Genauigkeit auf zurückgehaltenen Fakten stärker, wenn man aus den Zahl-Zeilen die eigenen Zielfrequenzen entfernt, als wenn man die des anderen Splits oder Kontrollfrequenzen entfernt?
- **Modelle:** Seed 3862, F/G, K = 19 (EXP-114, 4000 Schritte) und K = 8 (EXP-113 `answer`, 16 000 Schritte); gemeinsame Testmenge (2554 Fakten). Gebundene Embeddings → die Ablation wirkt auf Ein- und Ausgabe.
- **Eingriff:** X ← X − P_S X (Fourier-Unterraum über den Zahlindex, Konstante unberührt) für S = eigene Ziele, fremde Ziele, 4 Kontrollmengen (5 Frequenzen aus 1..56 ohne beide Zielmengen, rng 118).
- **Lesarten:** „Ziele funktional“: C = acc(fremd) − acc(eigen) > 0.3 **und** Kontrollmittel − acc(eigen) > 0.3 in allen 4 Läufen; „nicht funktional“: |C| < 0.1 in allen 4; sonst „unklar“.
- **Was dagegen spräche:** „nicht funktional“ → Δ_pow im LM wäre Energie ohne Nutzen für die Fakten (gegen eine funktionale Lesart von LM1).
- **Grenze:** Ablation an gebundenen Embeddings trifft auch die Ausgabeseite; Ergebnis also „die Zielfrequenzen der Zahl-Vektoren tragen die Vorhersage“, ohne Trennung von Ein- und Ausgabe (dafür EXP-117).
- **Befehl:** `python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/experiments/EXP-118-lm-ablation/ablate.py` (CPU, 2 Threads, wenige Minuten).

## Ergebnis (Sitzung 51, 15:45 Berlin gemessen; Exploration an bekannten Modellen, 1 Seed, 2 Konfigurationen)

Lauf über den Wächter, 1132 s (CPU), `summary.json`. Held-out-Genauigkeit (2554 Fakten) je Modell: Basis / eigene Ziele entfernt / fremde Ziele entfernt / Kontrollen (Min–Max):

| Modell | Basis | eigen | fremd | Kontrollen | C |
|---|---|---|---|---|---|
| K 19 F | 0.983 | 0.298 | 0.986 | 0.927–0.985 | 0.69 |
| K 19 G | 0.991 | 0.036 | 0.994 | 0.992–0.994 | 0.96 |
| K 8 F | 0.983 | 0.042 | 0.984 | 0.980–0.986 | 0.94 |
| K 8 G | 0.950 | 0.026 | 0.950 | 0.952–0.960 | 0.92 |

**Lesart: „Ziele funktional“** (C > 0.3 und Kontrollmittel − eigen > 0.3 in allen 4 Läufen). Die fünf über die Faktenauswahl gesteuerten Frequenzen der Zahl-Vektoren tragen im kleinen LM die Vorhersage der zurückgehaltenen Fakten; fünf andere Frequenzen (auch die Ziele des anderen Splits) sind entbehrlich. **Grenzen:** gebundene Embeddings (Ein- und Ausgabe zugleich getroffen), bekannte Modelle eines Seeds, Exploration. **Nächster Schritt:** dieselbe Ablation vorab registriert an den 20 LM1-Modellen (frische Seeds, bisher ohne Ablation angesehen).

## Nachtrag 1: Modelle mit flachen Zahl-Häufigkeiten (EXP-115; Sitzung 51, 16:42 gemessen)

`ablate_flat.py` (Lesarten je Seed vor dem Lauf committet), 2389 s CPU, `summary_flat.json`. Held-out-Genauigkeit: Basis / eigen / fremd / Kontrollen:

| Modell | Basis | eigen | fremd | Kontrollen | C |
|---|---|---|---|---|---|
| 3850 F | 0.896 | 0.218 | 0.879 | 0.753–0.908 | 0.66 |
| 3850 G | 0.982 | 0.243 | 0.984 | 0.579–0.986 | 0.74 |
| 3851 F | 0.633 | 0.133 | 0.275 | 0.514–0.674 | 0.14 |
| 3851 G | 0.976 | 0.446 | 0.866 | 0.630–0.981 | 0.42 |

**Lesarten: Seed 3850 „funktional“, Seed 3851 „unklar“.** Beschreibend: Anders als bei den P1-Splits (EXP-118 oben) senken hier auch einzelne Kontrollmengen die Genauigkeit deutlich (bis 0.58 / 0.51 / 0.63), und im nicht generalisierten Lauf 3851 F schadet das Entfernen der *fremden* Ziele fast so viel wie das der eigenen. Die Modelle mit flachen Häufigkeiten verteilen die Rechnung also breiter über mehrere Frequenzen; das passt zum schwächeren, nach dem Gipfel fallenden Δ_pow in EXP-115 (2 Seeds, Exploration, keine Ursachenaussage).

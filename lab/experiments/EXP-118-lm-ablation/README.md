---
id: EXP-118
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
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

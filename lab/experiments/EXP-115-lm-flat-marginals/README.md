---
id: EXP-115
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
---
# EXP-115: Steuert im LM die Paarstruktur allein, ohne Häufigkeitsunterschiede der Zahlen? (Pilot, 2 Seeds)

Zurück: [[LAB]] · [[FINDINGS]] · [[confirm/LM1_REGISTRATION|LM1]] · Pilot [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] · flache Splits [[experiments/EXP-104-flat-marginal-splits/README|EXP-104]] · [[JOURNAL]] Sitzung 50

**Bezug zu FINDINGS:** Verallgemeinerung von K2 auf ein kleines LM (Programm A, Regel 20e); Kontrolle für die Deutung von LM1. Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 50, 12:54 Berlin gemessen, vor jedem Lauf)

- **Anlass (JOURNAL 12:42):** In den P1-Splits tragen auch die Zählungen je Zahl die Ziele (count(b) Zielanteil 0.225, count(a) 0.165 gegen 0.089 Zufall). Mit gebundenen Embeddings kann ein LM solche Häufigkeiten direkt in die Zahl-Zeilen schreiben (z. B. über die Ausgabeseite). Ein positives Δ_pow in EXP-114/LM1 sagt deshalb noch nicht, ob die Paarstruktur selbst steuert.
- **Aufbau:** unveränderter Trainer `lm_stage2.py` (wie LM1), K = 19, `--loss answer`, 4000 Schritte, GPU-Dienst. Splits aus EXP-104 mit **exakt flachen Zählungen** von a, b und c (m = 500; SD der Zählungen 0 in F und G, nachgeprüft), Seeds 3850/3851, gemeinsame Testmenge `s{seed}_test.npy` (disjunkt zu allen Splits des Seeds), Modell-Seeds 3950/3951 (unbenutzt). 3842 Fakten je Split; F und G überlappen (1103/1135 Paare), wie in EXP-104.
- **Lesarten (vorab, `analyze_pilot.py` von EXP-105 auf `raw`, Paare 3950:F,G und 3951:F,G):** Tor: zurückgehaltene Fakten ≥ 0.5 in ≥ 3/4 Läufen, sonst **„nicht gelernt (Budget)“**. **„Paarstruktur reicht“**: Δ_pow > 1 in beiden Seeds; **„braucht Häufigkeiten“**: |Δ_pow| ≤ 1 in beiden Seeds; sonst „unklar“. Beschreibend: Δ_pow neben EXP-114 (P1-Splits, 5.60 bei 4000; andere Seeds, daher nur grob vergleichbar) und neben EXP-104 im Spielzeugmodell (m = 500: 6.02 / 6.06).
- **Was dagegen spräche:** „braucht Häufigkeiten“ – dann wäre die LM-Steuerung in LM1 vermutlich ein Häufigkeitseffekt über die gebundenen Embeddings.
- **Budget:** 4 Läufe à 4000 Schritte, ≈ 40–55 min je Lauf unter Last; harte Grenze 180 min.
- **Bereits gesehene Daten:** EXP-104 (dieselben Splits im Spielzeugmodell: steuern und generalisieren bei m = 500), EXP-114, EXP-113-Zwischenblick. Davon beeinflusst: Wahl m = 500 (m = 0/10 generalisierten im Spielzeugmodell nicht in beiden Seeds).
- **Befehl Auswertung:** `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py --root lab/experiments/EXP-115-lm-flat-marginals/raw --pairs 3950:lab/experiments/EXP-104-flat-marginal-splits/splits/s3850_F_m500.npy,lab/experiments/EXP-104-flat-marginal-splits/splits/s3850_G_m500.npy 3951:lab/experiments/EXP-104-flat-marginal-splits/splits/s3851_F_m500.npy,lab/experiments/EXP-104-flat-marginal-splits/splits/s3851_G_m500.npy`. Hinweis: dessen eingebaute Lesarten gelten für EXP-105; hier zählen die Lesarten oben (Tor 0.5 in ≥ 3/4, „Paarstruktur reicht“ = Δ_pow > 1 in beiden Seeds).

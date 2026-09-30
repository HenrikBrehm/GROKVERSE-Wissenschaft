---
id: EXP-125
status: abgeschlossen
datum: 2026-09-30
tags: [exp/abgeschlossen, befund/positiv, lm-leiter]
---
# EXP-125: Sprachmodell-Leiter – hält die Steuerung in einem ≈ 2× größeren Modell?

Zurück: [[LAB]] · [[FINDINGS]] · Vorlage [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] / Bestätigung [[confirm/LM1_REGISTRATION|LM1]] (gleiche Einstellung, Standardgröße) · [[experiments/EXP-116-lm-low-share/README|EXP-116]] (Lesarten) · [[JOURNAL]] Sitzung 57

**Bezug zu FINDINGS:** Verallgemeinerung von K2 (Programm A, Regel 15c) im Sprachmodell (Regel 20e, Stufe 2: „≈ 10–30 M Parameter“). Bisher wurde nur eine Modellgröße (≈ 13.8 M) geprüft; Gutachter fragen als Erstes nach der Größe. Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 57, 2026-09-30, vor jedem Lauf)

- **Frage:** Steuert die Faktenauswahl die Zahl-Embeddings auch in einem LM mit ≈ 29.5 M Parametern (d 512, 8 Schichten, 8 Köpfe; gerechnet: Einbettung 8192·512 ≈ 4.2 M + 8·12·512² ≈ 25.2 M) statt ≈ 13.8 M?
- **Hypothese:** ja: Δ_pow > 1 in beiden Seeds, wenn die Fakten gelernt werden (LM1 bei Standardgröße: Δ_pow 5.32 [4.86, 5.73], 10/10).
- **Aufbau:** unveränderter Trainer `lm_stage2.py` (Hash in LM1/LM3 gebunden, nicht ändern), LM1-Einstellung: K = 19 Rechensätze je Sequenz (≈ 79 % Rechen-Tokens), `--loss answer`, 6000 Schritte, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, Kontext 256, gebundene Embeddings; nur `--d 512 --layers 8 --heads 8`. Modell-Seeds 3868/3869 (unbenutzt; 3860–3867 vergeben) ↔ P1-Splits der EXP-102-Seeds 3808/3809 (F/G), gemeinsame Testmenge je Seed = `design.build(seed)["test"]` (wie EXP-113/116). Lernrate bewusst **nicht** an die Größe angepasst (eine Variable ändern).
- **Messgrößen:** Δ_pow der 113 Zahl-Token-Zeilen am Ende (analyze_pilot.py), Genauigkeit auf Trainings- und zurückgehaltenen Fakten; beschreibend: erster Schritt mit zurückgehaltener Genauigkeit ≥ 0.5, n_params, Δ_pow-Verlauf.
- **Lesarten (`analyze.py`, vor dem Lauf geschrieben; Regeln wie EXP-116):** „K2 haelt im LM“: Δ_pow > 1 in beiden Seeds und zurückgehaltene Fakten > 0.5 in ≥ 3/4 Läufen; „nur Repraesentation“: Δ_pow > 1 in beiden Seeds und zurückgehaltene Fakten < 0.1 in ≥ 3/4; „bricht“: |Δ_pow| ≤ 1 in beiden Seeds; sonst „unklar“; Vorrang „nicht gelernt (Budget)“, wenn Trainingsfakten < 0.1 in ≥ 3/4 Läufen. Die Auswertung bricht ab, wenn ein Lauf nicht d 512 / 8 / 8 / K 19 / answer / 6000 hat.
- **Was gegen die Hypothese spräche:** Fakten gelernt, aber |Δ_pow| ≤ 1 → die Steuerung hängt an der kleinen Modellgröße (wäre ein Befund für §7 ii und Anhang K). „Nicht gelernt (Budget)“ sagt nichts über K2.
- **Budget/Abbruch:** geschätzt ≈ 0.6–0.8 s/Schritt neben anderen Läufen → ≈ 60–80 min je Lauf; 4 Läufe, 2 Worker, harte Grenze 600 min je Lauf (Dienst). Grafikspeicher je Lauf unbekannt, zunächst mit `gpu_gb=7` angemeldet, vor jedem Start auf `gpu_gb=6` gesenkt (Überschlag Aktivierungen + Logits + AdamW ≈ 5.3 GB, hochgerechnet mit dem Verhältnis gemessen/geschätzt des Standardmodells ≈ 3.4 GB; so passen später zwei Läufe unter 16 GB); startet deshalb erst, wenn LM3 den Speicher freigibt. Abbruch bei NaN (Trainer) oder Absturz.
- **Bereits gesehene Daten:** LM1 (Seeds 4000–4009/4100–4109, Standardgröße), EXP-114 (K = 19, Seed 3862), Stufe-1-Läufe auf den Split-Seeds 3808/3809 (`20_s48c_r0long_10k`, anderes Format). Beeinflusst: Wahl der LM1-Einstellung (lernt nach ≈ 2000–2750 Schritten, also innerhalb des Budgets).

## Befehle

```
python lab/experiments/EXP-125-lm-size/make_jobs.py > lab/queue/staging/45_exp125_lm_size.jobs && mv lab/queue/staging/45_exp125_lm_size.jobs lab/queue/inbox/
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-125-lm-size/analyze.py
```

## Ergebnis (Sitzung 65, 01.10.2026, 01:40 Berlin gemessen; `analyze.py`, Lesart vorab)

**Lesart: „K2 haelt im LM“** (Exploration, 2 Seeds; keine Bestätigung). Alle 4 Läufe vollständig (Dienst `45_exp125_lm_size`, 4/4, keine Fehler), je 29 545 472 Parameter (d 512, 8 Schichten, 8 Köpfe), Rechen-Token-Anteil 0.79, keine Textwiederholung.
- Δ_pow am Ende (Schritt 6000): Seed 3868 **3.79**, Seed 3869 **5.42** (beide > 1; LM1 bei ≈ 13.8 M: 5.32 [4.86, 5.73], andere Seeds – kein Größenvergleich).
- Zurückgehaltene Fakten am Ende: 0.961 / 0.928 (3868 F/G), 0.995 / 0.901 (3869 F/G); Trainingsfakten 0.995–0.999. Erster Schritt mit zurückgehaltener Genauigkeit ≥ 0.5: 2500 / 2750 / 2250 / 2500.
- Verlauf (beschreibend): Δ_pow bleibt bis Schritt 1750 bei |Δ_pow| ≤ 0.14 und springt mit dem Faktenlernen (Seed 3868: 0.25 bei 2000 → 3.81 bei 2750, danach flach 3.77–3.82; Seed 3869: 1.18 bei 2000 → 4.32 bei 2500, danach langsam steigend bis 5.42). Wie bei LM1 entsteht die Steuerung mit dem Lernen, nicht davor.
- Nicht gesagt: keine Skalierungsaussage (zwei Größen, zwei Seeds); der Betrag ist nicht mit LM1 vergleichbar (andere Seeds). Paper nach [[paper/EXP125_DEUTUNGEN]] (Anhang K, Grenze ii).

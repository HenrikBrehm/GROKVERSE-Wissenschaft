---
id: EXP-116
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
---
# EXP-116: Sprachmodell-Leiter Stufe 2c – wenige Prozent Rechensätze, Verlust nur auf der Antwort

Zurück: [[LAB]] · [[FINDINGS]] · Vorgänger [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] (K = 8, ≈ 34 %), [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] (K = 19, ≈ 79 %), [[experiments/EXP-105-lm-ladder-stage2/README|EXP-105]] (K = 2, Verlust überall, Pilot „unklar“) · Bestätigung bei K = 19: [[confirm/LM1_REGISTRATION|LM1]] · [[JOURNAL]] Sitzung 51

**Bezug zu FINDINGS:** Verallgemeinerung von K2 (Programm A, Regel 15c) auf ein kleines Sprachmodell (Regel 20e, Stufe 2: „natürlicher Text mit wenigen Prozent Rechensätzen“). Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 51, vor jedem Lauf)

- **Frage:** Steuert die Faktenauswahl die Zahl-Embeddings auch dann, wenn Rechensätze nur ≈ 8.7 % der Tokens ausmachen (K = 2, wie der EXP-105-Pilot), sofern das LM die Fakten lernt? EXP-114/LM1 prüfen ≈ 79 %, EXP-113 ≈ 34 %; die Regel-20e-Stufe mit „wenigen Prozent“ fehlt.
- **Hypothese:** Mit Verlust nur auf der Antwort und 16 000 Schritten lernen die Läufe die Fakten (EXP-105: Seed 3860 begann mit Verlust überall schon bei ≈ 9 250 Schritten; der Lernbeginn hing bisher eher an der Schrittzahl als an den gezeigten Fakten: K = 2 ≈ 9 250, K = 8 ≈ 8 500–10 000, nur K = 19 ≈ 2 000), und dann ist Δ_pow > 1.
- **Aufbau:** unveränderter Trainer `lm_stage2.py` (≈ 14 M Parameter, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, Kontext 256), `--arith-facts 2 --loss answer --steps 16000`. Modell-Seeds 3864/3865 (unbenutzt, per grep über Jobdateien geprüft) ↔ P1-Splits der EXP-102-Seeds 3804/3805 (F/G mit gleicher Init, gleichem Text, gleichen Positionen), gemeinsame Testmenge je Seed = EXP-102 `design.build(seed)["test"]` (`tests/`). 4 Läufe, `make_jobs.py` → GPU-Dienst `41_exp116_lowshare.jobs` (hinter EXP-113; workers 2, gpu_gb 3.5).
- **Textumlauf:** Bei 91 % Text-Tokens verbrauchen 16 000 Schritte ≈ 120 Mio. Text-Tokens von 113.7 Mio. → **ein Umlauf** gegen Ende (≈ 5 % des Textes zum zweiten Mal). Bewusst in Kauf genommen (Pilot); `text_wraps` wird berichtet. LM1 verlangt dagegen 0 Umläufe.
- **Budget/Abbruch:** ≈ 0.3 s/Schritt bei 2–3 LM-Läufen → ≈ 80 min je Lauf, 4 Läufe bei 2 Workern ≈ 3 h; harte Grenze 900 min je Lauf (Dienst). Abbruch bei NaN (Trainer) oder Absturz; Checkpoints alle 1000 Schritte.
- **Lesarten (`analyze.py`, vor dem Lauf geschrieben; Regeln wie EXP-113 für einen Arm):** „K2 haelt im LM“: Δ_pow > 1 in beiden Seeds und zurückgehaltene Fakten > 0.5 in ≥ 3/4 Läufen; „nur Repraesentation“: Δ_pow > 1 in beiden Seeds und zurückgehaltene Fakten < 0.1 in ≥ 3/4; „bricht“: |Δ_pow| ≤ 1 in beiden Seeds; sonst „unklar“; Vorrang **„nicht gelernt (Budget)“**, wenn die Trainingsfakten-Genauigkeit in ≥ 3/4 Läufen < 0.1 ist. Beschreibend: erster Schritt mit zurückgehaltenen Fakten ≥ 0.5 je Lauf, Textumläufe.
- **Was gegen die Hypothese spräche:** Die Fakten werden gelernt (> 0.5 zurückgehalten), aber |Δ_pow| ≤ 1 → bei wenigen Prozent Rechensätzen bricht K2 (erste Stufe, auf der K2 bricht; Regel 20e). „Nicht gelernt (Budget)“ wäre dagegen kein Befund über K2.
- **Bereits gesehene Daten:** EXP-105-Pilot (K = 2, Verlust überall, Seeds 3860/3861), EXP-113-Zwischenblicke (K = 8, `answer`, Seed 3862), EXP-114 (K = 19), Stufe 1 auf den Split-Seeds 3804/3805 (EXP-102/112). Davon beeinflusst: Wahl von K, Verlust-Arm, Budget.

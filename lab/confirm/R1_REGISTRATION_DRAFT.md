---
id: R1-registrierung-entwurf
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, lab/paper]
verwandt: ["[[paper/robustness_plan]]", "[[paper/STATUS]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[FINDINGS]]"]
---
# R1-Bestätigung (Regel 19a): Gilt K2 bei anderer Lernrate, anderem Weight Decay und anderem Trainingsanteil? **ENTWURF, nicht eingefroren, kein Code**

Zurück zu [[paper/robustness_plan]] · [[paper/STATUS]]. Entwurf Sitzung 24 (2026-09-27), vor jedem R1-Lauf.

- **Aussage R1 (je Zelle):** Bei add 113 verschiebt eine konstruierte Auswahl der Trainingspaare bei Schritt 2000 die relative W_E-Energie zu den fünf vorgegebenen Frequenzen (Δ_pow wie P1,
  `confirm_p1.delta_pow`), auch wenn genau ein Hyperparameter vom Standard abweicht.
- **Zellen (6, je eine Abweichung, sonst Standard lr 1e-3, wd 1.0, train_frac 0.3):** lr 5e-4 · lr 2e-3 · wd 0.3 · wd 3.0 · train_frac 0.2 · train_frac 0.5.
- **Einheit, Test, Urteil:** Einheit = Seed mit F/G-Paar (eigene Init je Seed, F und G mit derselben Init, wie P1). Einseitiger Test Mittel > 0 (Vorzeichen-Permutation, exakt bei n ≤ 20),
  95-%-Bootstrap-KI; **bestätigt** = alle geplanten Paare gültig, Holm-p (über die 6 Zellen) < 0.05 und KI-Untergrenze ≥ 1 (Mindesteffekt wie P1). Technischer Ausfall → nicht auswertbar (p = 1).
  Ein „nicht bestätigt“ in einer Zelle ist ein Befund („gilt nur in einem Bereich“) und kommt so ins Paper.
- **Stichprobe:** P1 add 113: Δ_pow 8.24, KI [7.92, 8.54] bei n = 50 → SD ≈ 1.1. Bei Abschwächung auf die Hälfte (≈ 4) und doppelter Streuung ist der standardisierte Abstand zum Mindesteffekt ≈ 1.4;
  n = 15 gibt dann einseitig bei α = 0.05/6 grob > 90 % Power (Normalnäherung). **n = 15 je Zelle**, 6 × 15 × 2 = 180 Läufe à 2000 Schritte (GPU ≈ 40 s je Lauf) ≈ 20–30 min bei 8 parallel.
- **Zusätzlich beschreibend:** Test-Genauigkeit und Generalisierungsschritt je Zelle (lr/wd verändern das Grokking; Δ_pow bei 2000 kann vor oder nach dem Grokking liegen, das wird berichtet).
- **Splits:** `confirm_splits`-Konstruktion mit eigener Versuchs-ID (8) und frischen Seeds; für die train_frac-Zellen muss die Split-Größe round(f · 113²) sein, und ε muss so gewählt werden, dass der
  M0-Zielanteil dem Standard entspricht (Kalibrierung an Kalibrier-Seeds vor jedem Lauf, wie EXP-053) — sonst wäre eine Abschwächung bei 0.5 nur eine schwächere Steuerung.
- **Code (fehlt):** `lab/tools/confirm_r1.py` (Muster confirm_p2e: Manifest, Bindung, Selbsttest mit End-zu-End-Maß), Split-Erzeugung mit Anteil als Parameter (ohne `confirm_splits.py` zu ändern,
  dessen Hash in eingefrorenen Manifesten steht), Jobzeilen mit `--lr/--weight-decay/--train-frac` (seit Sitzung 24 im Trainer). **Codex-Prüfung vor dem Einfrieren.**
- **Seeds:** frischer Block, vor der Nutzung in [[FINDINGS_DETAILS]] reservieren.
- **Bereits gesehene Daten:** P1 (Maß, Mindesteffekt, Streuung). Zu anderen Hyperparametern wurde bisher nichts gemessen.

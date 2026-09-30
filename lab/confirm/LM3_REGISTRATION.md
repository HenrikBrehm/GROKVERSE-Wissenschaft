---
id: LM3
status: entwurf
datum: 2026-09-30
tags: [confirm, lm-leiter]
---
# LM3: Steuert die Faktenauswahl die Zahl-Embeddings auch bei nur ≈ 9 % Rechen-Tokens? (Bestätigungsblock, Entwurf Sitzung 56)

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, Verallgemeinerung von K2; Regel 20e Stufe 2 „wenige Prozent“) · Vorgänger [[confirm/LM1_REGISTRATION|LM1]] (≈ 79 %, bestätigt) · Pilot [[experiments/EXP-116-lm-low-share/README|EXP-116]] · Code `lab/confirm/confirm_lm3.py`

## Fassung 1 (Sitzung 56, Entwurf; wird vor jedem Lauf dieses Blocks eingefroren)

**Frage.** LM1 hat K2 im kleinen Sprachmodell bei ≈ 79 % Rechen-Tokens bestätigt und ausdrücklich offen gelassen, ob das bei „wenigen Prozent“ Rechendaten gilt (Regel 20e). Hält K2, wenn nur 2 Rechensätze je Sequenz eingestreut sind (≈ 8.7 % der Tokens), sofern das Modell die Fakten lernt?

**Aufbau (einzufrieren).** Wie LM1 bis auf: K = 2 Rechensätze je Sequenz (`--arith-facts 2`), 15 000 Schritte (unter dem ersten Text-Umlauf bei ≈ 15 130 Schritten; `text_wraps` = 0 ist Bindung), frische Split-Seeds 4010–4019 (Modell-Seed + 100 = 4110–4119; per grep über lab/ unbenutzt, 30.09.), Bootstrap-rng 4021. Trainer `lm_stage2.py` (Hash im Manifest), Verlust auf Text und Antwort-Tokens, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, Kontext 256, GPU. F/G eines Seeds teilen Init, Text, Schablonen und Einfügepositionen. Code: `confirm_lm3.py` = `confirm_lm1.py` mit genau diesen Konstanten geändert (Erzeugung durch exakte Ersetzungen, Sitzung 56).

**Messgröße, H1, Bindung, Ausfälle, Sekundär:** wie LM1 (Δ_pow auf den 113 Zahl-Token-Zeilen am letzten Schritt; H1 Mittel > 1 mit Perzentil-Bootstrap-KI und exaktem Vorzeichen-Permutationstest; „unter Mindesteffekt“ gespiegelt; Familie = {H1}).

**Funktional (LM3-F, `confirm_lm3f.py`, Kopie von `confirm_lm1f.py` mit den LM3-Konstanten, rng 4031):** H1F wie LM1-F (C̄ = acc(fremde Ziele entfernt) − acc(eigene Ziele entfernt), Mittel über 10 Seeds > 0.1, Bootstrap-KI und exakter Vorzeichentest), wird mit LM3 eingefroren und nur ausgewertet, wenn LM3 auswertbar ist. Eigene Familie {H1F} wie bei LM1-F (keine Holm-Korrektur über H1 und H1F; H1F wird nur geprüft, wenn LM3 auswertbar ist). Neu gegenüber LM1: H1F wird schon vor den Läufen eingefroren, nicht nachträglich.

**Tor (offen bis zum EXP-116-Ergebnis):** zurückgehaltene Faktengenauigkeit ≥ 0.5 am Ende in ≥ GATE_N von 20 Läufen, sonst „nicht auswertbar (Budget)“.

**Offen vor dem Einfrieren:** GATE_N und die Schrittzahl gegen die vollständigen EXP-116-Verläufe prüfen (bisher gesehen: Seed 3864 F/G lernen ab ≈ 5000–6000, zurückgehalten 0.78/0.95 bei 16 000; Seed 3865 bei 7750 erst beginnend); Smoke `lm3_smoke` (Seed 4010 F, 250 Schritte); unabhängige Prüfung; Manifest mit Commit-ID.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen.** EXP-116 (K = 2, Seeds 3864/3865, 16 000 Schritte; Lernbeginn, Endgenauigkeiten) → Wahl von K = 2, Budget 15 000, Tor. EXP-105-Pilot (K = 2, Verlust überall), EXP-113 (K = 8), LM1/LM1-F, EXP-114. Keiner der Seeds 4010–4019 wurde je trainiert.

**Smoke (Sitzung 56, 03:47 Berlin gemessen, in der Sitzung über den Wächter, 159 s):** Seed 4010 F, 250 Schritte, `lm3_smoke/lm2_seed4110_seed4010_F_steps250_728dae53c7605c25`, completed; Rechen-Token-Anteil 0.0868, text_wraps 0. Lader liest Snapshots [0, 250], Ziele F = {16, 30, 39, 40, 43}; die Bindungsprüfung (Manifest im Speicher) meldet nur „config steps“ (erwartet). Permutationstest-Probe: zehnmal 5.0 → p = 1/1024; Werte 0.8/1.2 → p = 0.62. `confirm_lm3f.py --selftest` grün. Die Seeds 4010–4019/4110–4119 kommen in lab/ nur als Zahlenwerte in fremden result.json/Tokenizer-Dateien vor, nie als Seed (grep 30.09.). Der Smoke-Lauf zählt nicht.

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

**Aufbau (einzufrieren).** Wie LM1 bis auf: K = 2 Rechensätze je Sequenz (`--arith-facts 2`), 15 000 Schritte (unter dem ersten Text-Umlauf bei ≈ 15 135 ± 1 Schritten, nachgerechnet aus den Schablonenlängen; Reserve ≈ 135 Schritte, das Budget lässt sich deshalb nicht erhöhen; `text_wraps` = 0 ist Bindung), frische Split-Seeds 4010–4019 (Modell-Seed + 100 = 4110–4119; per grep über lab/ unbenutzt, 30.09.), Bootstrap-rng 4021. Trainer `lm_stage2.py` (Hash im Manifest), Verlust auf Text und Antwort-Tokens, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, Kontext 256, GPU. F/G eines Seeds teilen Init, Text, Schablonen und Einfügepositionen. Code: `confirm_lm3.py` = `confirm_lm1.py` mit genau diesen Konstanten geändert (Erzeugung durch exakte Ersetzungen, Sitzung 56), dazu Kopfzeile der Jobdatei (3 Worker, job_minutes 600, gpu_gb 3.5), Docstring und `confirm_lm3f.py` in der CODE-Liste (sein Hash steht im Manifest und wird von `confirm_lm3f.py` geprüft).

**Messgröße, H1, Bindung, Ausfälle, Sekundär:** wie LM1 (Δ_pow auf den 113 Zahl-Token-Zeilen am letzten Schritt; H1 Mittel > 1 mit Perzentil-Bootstrap-KI und exaktem Vorzeichen-Permutationstest; „unter Mindesteffekt“ gespiegelt; Familie = {H1}).

**Funktional (LM3-F, `confirm_lm3f.py`, Kopie von `confirm_lm1f.py` mit den LM3-Konstanten, rng 4031):** H1F wie LM1-F (C̄ = acc(fremde Ziele entfernt) − acc(eigene Ziele entfernt), Mittel über 10 Seeds > 0.1, Bootstrap-KI und exakter Vorzeichentest), wird mit LM3 eingefroren und nur ausgewertet, wenn LM3 auswertbar ist. Eigene Familie {H1F} wie bei LM1-F (keine Holm-Korrektur über H1 und H1F; H1F wird nur geprüft, wenn LM3 auswertbar ist). Neu gegenüber LM1: H1F wird schon vor den Läufen eingefroren, nicht nachträglich.

**Tor (festgelegt nach dem EXP-116-Ergebnis, vor jedem LM3-Lauf):** zurückgehaltene Faktengenauigkeit ≥ 0.5 am Ende in ≥ 16 von 20 Läufen (wie LM1), sonst „nicht auswertbar (Budget)“. `confirm_lm3f.py` importiert GATE_N aus `confirm_lm3.py`. Begründung: Im Piloten lagen bei Schritt 15 000 alle 4 Läufe über 0.5 (0.738 / 0.960 / 0.920 / 0.771); der Lernbeginn schwankte aber stark (Δ_pow > 1 ab 5000 bzw. 7500), und ein spät lernender Seed fällt mit beiden Läufen durch; 16/20 erlaubt zwei solche Seeds. Nicht lernende Seeds zählen in H1 mit (konservativ).

**Pilot EXP-116 vollständig (gesehen vor dem Einfrieren):** Lesart „K2 haelt im LM“; Δ_pow 2.06 / 4.72 bei 15 000 (2.06 / 4.97 bei 16 000; die Pilotläufe liefen ≈ 865 Schritte über den Text-Umlauf hinaus), zurückgehalten bei 15 000 0.738 / 0.960 (Seed 3864) und 0.920 / 0.771 (Seed 3865); Test ≥ 0.5 ab 6250–12 250. Δ_pow stieg mit dem Lernbeginn und fiel bei Seed 3864 danach von 4.3 auf 2.1 (beschreibend). **Power:** mit 2 Pilotwerten (≈ 2.1 und ≈ 4.7) nicht schätzbar; bei wahrem Mittel 3 und SD 1.5 wäre „bestätigt“ wahrscheinlich, bei Mittel ≈ 1.5 kaum (Mindesteffekt 1). Ein „unklar“ wird so berichtet.

**Unabhängige Prüfung vor dem Einfrieren (Claude-Agent, nur lesend; Codex ohne Guthaben):** kein Blocker. Übernommen: Docstring von `confirm_lm3f.py` auf LM3 umgeschrieben (Befehlszeile hätte sonst LM1-F neu gerechnet), Hash von `confirm_lm3f.py` gebunden, GATE_N nur an einer Stelle, Wrap-Schritt genauer (15 135), Pilotwerte bei 15 000 statt 16 000. Diff gegen LM1: nur die beabsichtigten Konstanten; nichts hängt sonst an K oder STEPS (Snapshots alle 250, Checkpoint am Ende).

**Bereits gesehene Daten und davon beeinflusste Entscheidungen.** EXP-116 (K = 2, Seeds 3864/3865, 16 000 Schritte; Lernbeginn, Endgenauigkeiten) → Wahl von K = 2, Budget 15 000, Tor. EXP-105-Pilot (K = 2, Verlust überall), EXP-113 (K = 8), LM1/LM1-F, EXP-114. Keiner der Seeds 4010–4019 wurde je trainiert.

**Smoke (Sitzung 56, 03:47 Berlin gemessen, in der Sitzung über den Wächter, 159 s):** Seed 4010 F, 250 Schritte, `lm3_smoke/lm2_seed4110_seed4010_F_steps250_728dae53c7605c25`, completed; Rechen-Token-Anteil 0.0868, text_wraps 0. Lader liest Snapshots [0, 250], Ziele F = {16, 30, 39, 40, 43}; die Bindungsprüfung (Manifest im Speicher) meldet nur „config steps“ (erwartet). Permutationstest-Probe: zehnmal 5.0 → p = 1/1024; Werte 0.8/1.2 → p = 0.62. `confirm_lm3f.py --selftest` grün. Die Seeds 4010–4019/4110–4119 kommen in lab/ nur als Zahlenwerte in fremden result.json/Tokenizer-Dateien vor, nie als Seed (grep 30.09.). Der Smoke-Lauf zählt nicht.

---
id: R9
status: entwurf
datum: 2026-09-28
tags: [confirm/entwurf, neu/kandidat]
---
# R9-Bestätigung (Entwurf): Tickt die frühe Festlegung in Λ, wenn Adams β-Fenster in Λ gemessen werden?

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage) · Piloten [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]], [[experiments/EXP-090-beta-window-lambda/README|EXP-090]], [[experiments/EXP-081-optimizer-clock/README|EXP-081]] · [[confirm/R3_REGISTRATION_DRAFT|R3]] · [[NOVEL_DIRECTIONS]] N48.

**Status:** Entwurf, Sitzung 40 (2026-09-28, ≈ 12:12 Berlin). **Kein Code, nicht eingefroren.** Vor dem Einfrieren: Code `confirm_r9.py` nach dem Muster von `confirm_r3.py` (Manifest, Code-Hashes, Lader, Smoke), unabhängige Prüfung von Design und Auswertung, Seeds reservieren.

## Hypothesen (Familie, Holm über 3, α = 0.05)

Protokoll wie EXP-090 (add 113, ω = 0-Splits nach EXP-053-Bau mit eigenem Seed-Strom, Wechsel A → B und B → A bei t, danach 2000 Schritte Standard; π gegen reine Läufe; `--lr-scale c` in den Schritten 1 … t; `--pre-switch-betas` mit β′ = 1 − c(1 − β)).
- **H1 (Richtung, c = 0.25, Λ = 25):** e₁ = π(lr × 0.25, t = 100) − π(dieselbe Zelle mit β′ = 0.975/0.995) > 0. Einseitiger gepaarter t-Test, Mindesteffekt 0.05 (bestätigt = Holm-p < 0.05 und KI-Untergrenze > 0.05). Pilot: +0.16, SD 0.14.
- **H2 (Äquivalenz, c = 0.25):** d₁ = π(lr × 0.25, t = 100, β′) − π(Standard, t = 25) liegt in ±0.1 (TOST, 90-%-KI ganz in [−0.1, 0.1]; Holm auf das größere der beiden einseitigen p). Pilot: +0.002, SD 0.05.
- **H3 (zweite Stufe, c = 2, Λ = 30):** e₂ = π(lr × 2, t = 15, β′ = 0.8/0.96) − π(lr × 2, t = 15, Standard-β) > 0 (H-β: bei c = 2 sind die Standardfenster in Λ doppelt so lang → weniger Festlegung; β′ gleicht aus). Pilot [[experiments/EXP-091-beta-window-c2/README|EXP-091]] (bekannte Seeds 3260–3269): +0.049 [0.023, 0.078], SD 0.048, 10/10. **Test gegen 0** (kein Mindesteffekt; 0.03 wäre bei halbem Piloteffekt zu streng); Power bei n = 24 und halbem Effekt ≈ 0.8.
- **Beschreibend:** d₂ = π(c = 2, β′) − π(Standard, t = 30); Trennung beim Wechsel (zählerfreie Lesart); t_eq.

## Umfang, n

Zellen je Seed: rein A/B, Standard t = 25 und t = 30, (0.25, 100), (0.25, 100, β′), (2, 15), (2, 15, β′) → 14 Läufe. **n = 24** (Normalnäherung bei halbem Piloteffekt für H1: Power ≈ 0.88; H2 bei 1.5-facher Pilot-SD ≈ 1.0; H3 offen) → 336 GPU-Läufe, ≈ 35–40 min bei 8 Workern.

## Offene Punkte vor dem Einfrieren

1. c = 2: t = 15 ergibt Λ = 30; `--lr-scale` wirkt bis Schritt 250 nur auf dem ersten Split (passt). Prüfen, dass β′ = 0.8/0.96 bei lr 2e-3 stabil ist (Smoke).
2. Zählerunterschied nach dem Wechsel (EXP-090 Nachtrag a): betrifft H2 und d₂, nicht H1/H3 (Paarung innerhalb derselben c-Stufe). In der Registrierung so nennen; zählerfreie Lesart beschreibend.
3. Seeds: neuer reservierter Block (z. B. 3300–3323), Splits über eigenen SeedSequence-Strom.
4. **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-091 (c = 2: Richtung, SD, Wahl von t = 15 und β′ 0.8/0.96, Test gegen 0), EXP-089/090 (Effektgrößen, SD, Wahl von Λ = 25, t = 100, β′-Regel, Äquivalenzgrenze ±0.1), EXP-081 (Richtung bei β₁), R3 (c = 2 und 0.5 als Stufen). Keine Seeds aus diesen Blöcken.

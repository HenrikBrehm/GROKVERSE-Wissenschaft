---
id: R8-registrierung-entwurf
status: entwurf
datum: 2026-09-28
tags: [lab/bestaetigung, exp/vorbereitet, programm/B, neu/kandidat]
verwandt: ["[[experiments/EXP-086-same-spectrum-switch/README|EXP-086]]", "[[confirm/R6_REGISTRATION_DRAFT|R6]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]"]
---
# R8: Kostet nur ein Wechsel zu *anderen* Zielfrequenzen Grokking-Zeit? Bestätigung des Frequenzkonflikts an frischen Seeds (**ENTWURF, kein Code**)

Zurück: [[FINDINGS]] (Programm B, Zeitsignatur) · Pilot [[experiments/EXP-086-same-spectrum-switch/README|EXP-086]] · [[confirm/R6_REGISTRATION_DRAFT|R6]] · [[NOVEL_DIRECTIONS]] N43.
Entwurf Sitzung 37 (2026-09-28, Berlin), vor jedem R8-Lauf. Code `lab/tools/confirm_r8.py` fehlt noch (Muster `confirm_r6.py` + `EXP-086/make_splits.py`).

## Aussage R8 (eng)

Bei add 113 (1-Schicht-Transformer, Standard-Preset) verzögert ein Datenwechsel nach 25 Schritten das Grokking stärker, wenn der neue Split **andere** Zielfrequenzen trägt (A→B), als wenn er dieselben Zielfrequenzen mit neuen, disjunkten Paaren trägt (A→A2). Beide Wechsel gehen zwischen disjunkten Splits gleicher Größe und gleicher Steuerstärke aus demselben Pool. Das ist eine Aussage über Zeit, nicht über einen Mechanismus.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- EXP-086 (Seeds 400–409, Sitzung 37): D = C_AB(25) − C_AA2(25) = +0.82 log2 (SD 0.55), 9/10, p = 0.011; C_AA2(25) −0.26 (SD 0.41). Dazu EXP-056 (A, B, A↔B bei 25 an denselben Seeds) und die Zeitkurven aus Sitzung 32 (N28, P3, EXP-056/059).
- **Davon beeinflusst:** t = 25, der gemeinsame Horizont 2000, die Konstruktion von A2 (EXP-086 `make_splits.py`: gleiche Zielmenge F, neue Phasen und Schlüssel, ε je Seed so kalibriert, dass der M0-Anteil auf F dem von A gleicht, |Δ| ≤ 0.005), n.
- Nicht gesehen: keine Läufe mit den Seeds unten.

## Aufbau (fest, sobald eingefroren)

| Punkt | Festlegung |
|---|---|
| Einheiten | **Seeds 3100–3119** (n = 20; Block 3100–3129 reserviert, Sitzung 37, vorher ungenutzt) |
| Splits | A, B, Testmenge: EXP-053 `overlap_split`, ω = 0, ε aus `calibration.json` (wie N28/R6). A2: Konstruktion aus EXP-086 `make_splits.py`, eigener Strom `SeedSequence([88_001, seed, Zweck])`. Splits bitgleich aus dem deterministischen Neubau geprüft |
| Läufe je Seed (7) | A, B, A2 allein (2000 Schritte); A→B, B→A, A→A2, A2→A bei 25 (2025 Schritte, AdamW-Zustand behalten). 140 GPU-Läufe, `--threads 1` |
| Zeit | b = min(erste Testgenauigkeit ≥ 0.95 [Trainer-Ereignis], 2000) ab Schritt 0; C_XY(25) = Mittel beider Richtungen von log2 b(Wechsel) − log2 b(nur Ziel-Split) |
| **Primär (eine Hypothese)** | **H1:** D = C_AB(25) − C_AA2(25) > 0. p = max(p_flip, p_Vorzeichen) wie R6 (exakter einseitiger Vorzeichen-Permutationstest über alle 2^20 Vorzeichen; exakter Binomialtest über |D| > 1e-9). *Bestätigt* bei p < 0.05. Effektgröße: Mittel mit 95-%-Bootstrap-KI |
| Sekundär (nicht im Urteil) | **S1:** C_AA2(25) < 0.5 · C_AB(25) im Mittel (gestützt / nicht gestützt, beschreibend mit KI der Differenz C_AA2 − 0.5·C_AB). Beschreibend: C_AB(25), C_AA2(25) mit Vorzeichenzählung; Anteil generalisierter Arme |
| Gültigkeit | Alle 7 Läufe je Seed gebunden, gleiche Init- und Test-Prüfsumme, W_E am Ende endlich. Fehlt ein Seed, ist R8 *nicht auswertbar* (kein Urteil mit weniger Seeds). Abgestürzte, ungebundene Läufe dürfen **vor** der ersten Auswertung neu gestartet werden |
| Stichprobe | Pilot SD(D) = 0.55; bei halbem Pilotmittel (0.41, Winner's Curse) ist der standardisierte Effekt 0.75, n = 20 gibt für den t-Test einseitig ≈ 0.9 Power (Normalnäherung); das Maximum mit dem Vorzeichentest senkt das. **Vor dem Einfrieren:** Power per Simulation aus den 10 Pilotwerten (Muster `R6_pilot_power.py`), n = kleinstes aus {20, 25, 30} mit Power ≥ 0.8 bei halbem Effekt |
| Budget | 140 Läufe × ≈ 2000 Schritte, GPU 7 parallel ≈ 15–20 min |

## Was dagegen spräche

- H1 nicht bestätigt: Die Trennung aus EXP-086 war eine Eigenheit der bekannten Seeds; dann bleibt „jede frühe Datenänderung kostet“ offen.
- H1 bestätigt, S1 nicht gestützt: Auch ein Wechsel bei gleicher Zielmenge kostet, aber weniger (gemischte Lesart).

## Offene Schritte vor dem Einfrieren

1. Code `confirm_r8.py` (Block/Bindung/Lader wie R6, Selbsttest mit synthetischen Zeiten).
2. Power-Simulation, n festlegen.
3. Prüfung (Codex, falls Guthaben; sonst unabhängige Claude-Prüfung, nur lesend).
4. Manifest, Commit, Splits, Jobs, Smoke, Block, Analyse.

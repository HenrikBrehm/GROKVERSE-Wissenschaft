---
id: R8-registrierung-entwurf
status: entwurf
datum: 2026-09-28
tags: [lab/bestaetigung, exp/vorbereitet, programm/B, neu/kandidat]
verwandt: ["[[experiments/EXP-086-same-spectrum-switch/README|EXP-086]]", "[[confirm/R6_REGISTRATION_DRAFT|R6]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]"]
---
# R8: Kostet nur ein Wechsel zu *anderen* Zielfrequenzen Grokking-Zeit? Bestätigung des Frequenzkonflikts an frischen Seeds (**ENTWURF, Code vorhanden**)

Zurück: [[FINDINGS]] (Programm B, Zeitsignatur) · Pilot [[experiments/EXP-086-same-spectrum-switch/README|EXP-086]] · [[confirm/R6_REGISTRATION_DRAFT|R6]] · [[NOVEL_DIRECTIONS]] N43.
Entwurf Sitzung 37 (2026-09-28, Berlin), vor jedem R8-Lauf. Code `lab/tools/confirm_r8.py` (Muster `confirm_r6.py` + `EXP-086/make_splits.py`), Stand unten.

## Aussage R8 (eng)

Bei add 113 (1-Schicht-Transformer, Standard-Preset) verzögert ein Datenwechsel nach 25 Schritten das Grokking stärker, wenn der neue Split **andere** Zielfrequenzen trägt (A→B), als wenn er dieselben Zielfrequenzen mit neuen, disjunkten Paaren trägt (A→A2). Beide Wechsel gehen zwischen disjunkten Splits gleicher Größe und gleicher Steuerstärke aus demselben Pool. Das ist eine Aussage über Zeit, nicht über einen Mechanismus.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- EXP-086 (Seeds 400–409, Sitzung 37): D = C_AB(25) − C_AA2(25) = +0.82 log2 (SD 0.55), 9/10, p = 0.011; C_AA2(25) −0.26 (SD 0.41). Dazu EXP-056 (A, B, A↔B bei 25 an denselben Seeds) und die Zeitkurven aus Sitzung 32 (N28, P3, EXP-056/059).
- **Davon beeinflusst:** t = 25, der gemeinsame Horizont 2000, die Konstruktion von A2 (EXP-086 `make_splits.py`: gleiche Zielmenge F, neue Phasen und Schlüssel, ε je Seed so kalibriert, dass der M0-Anteil auf F dem von A gleicht, |Δ| ≤ 0.005), n.
- Nicht gesehen: keine Läufe mit den Seeds unten.

## Aufbau (fest, sobald eingefroren)

| Punkt | Festlegung |
|---|---|
| Einheiten | **Seeds 3100–3124** (n = 25 nach der Power-Regel unten; Block 3100–3129 reserviert, Sitzung 37, vorher ungenutzt) |
| Splits | A, B, Testmenge: EXP-053 `overlap_split`, ω = 0, ε aus `calibration.json` (wie N28/R6). A2: Konstruktion aus EXP-086 `make_splits.py`, eigener Strom `SeedSequence([88_001, seed, Zweck])`. Splits bitgleich aus dem deterministischen Neubau geprüft |
| Läufe je Seed (7) | A, B, A2 allein (2000 Schritte); A→B, B→A, A→A2, A2→A bei 25 (2025 Schritte, AdamW-Zustand behalten). 175 GPU-Läufe (n = 25), `--threads 1` |
| Zeit | b = min(erste Testgenauigkeit ≥ 0.95 [Trainer-Ereignis], 2000) ab Schritt 0; C_XY(25) = Mittel beider Richtungen von log2 b(Wechsel) − log2 b(nur Ziel-Split) |
| **Primär (eine Hypothese)** | **H1:** D = C_AB(25) − C_AA2(25) > 0. p = max(p_flip, p_Vorzeichen) wie R6 (exakter einseitiger Vorzeichen-Permutationstest über alle 2^n Vorzeichen, n = 25; exakter Binomialtest über |D| > 1e-9). *Bestätigt* bei p < 0.05. Effektgröße: Mittel mit 95-%-Bootstrap-KI |
| Sekundär (nicht im Urteil) | **S1:** C_AA2(25) < 0.5 · C_AB(25): *gestützt*, wenn die Obergrenze des 95-%-Bootstrap-KI des Seed-Mittels von C_AA2 − 0.5·C_AB unter 0 liegt. Beschreibend: C_AB(25), C_AA2(25) mit Vorzeichenzählung; Anteil generalisierter Arme |
| Gültigkeit | Alle 7 Läufe je Seed gebunden, gleiche Init- und Test-Prüfsumme, W_E am Ende endlich. Fehlt ein Seed, ist R8 *nicht auswertbar* (kein Urteil mit weniger Seeds). Abgestürzte, ungebundene Läufe dürfen **vor** der ersten Auswertung neu gestartet werden |
| Stichprobe | Pilot SD(D) = 0.55; halber Pilotmittelwert 0.41 (Winner's Curse). Power per Simulation (`R8_pilot_power.py`): Bootstrap aus den 10 Pilotwerten **und** Normalmodell, je bei halbem Effekt; n = kleinstes aus {20, 25, 30} mit Power ≥ 0.8 in beiden → **n = 25** |
| Budget | 175 Läufe × ≈ 2000 Schritte, GPU 7 parallel ≈ 25 min |

## Was dagegen spräche

- H1 nicht bestätigt: Die Trennung aus EXP-086 war eine Eigenheit der bekannten Seeds; dann bleibt „jede frühe Datenänderung kostet“ offen.
- H1 bestätigt, S1 nicht gestützt: Auch ein Wechsel bei gleicher Zielmenge kostet, aber weniger (gemischte Lesart).

## Offene Schritte vor dem Einfrieren

1. Code `confirm_r8.py` (Block/Bindung/Lader wie R6, Selbsttest mit synthetischen Zeiten).
2. Power-Simulation, n festlegen.
3. Prüfung (Codex, falls Guthaben; sonst unabhängige Claude-Prüfung, nur lesend).
4. Manifest, Commit, Splits, Jobs, Smoke, Block, Analyse.

## Stand Sitzung 37 (gemessen, vor jedem R8-Lauf)

- **Code** `lab/tools/confirm_r8.py` geschrieben; Selbsttest über den Wächter **grün** (Bindung, Run-IDs, Jobformat, Split-Neubau deterministisch und disjunkt an zwei Seeds außerhalb des Blocks, Anteil A2 auf F innerhalb 0.005, Kosten- und Urteilsarithmetik).
- **Power** (`R8_pilot_power.py` → `R8_pilot_power.json`, 2000 Ziehungen aus den 10 Pilotwerten): voller Effekt n = 20: 0.99; halber Effekt n = 20: 0.96, n = 25: 0.99, n = 30: 1.00 → zunächst n = 20; nach der Prüfung (unten) gilt **n = 25**.
- S1 ist im Code präzisiert: *gestützt*, wenn die Obergrenze des 95-%-Bootstrap-KI von C_AA2 − 0.5·C_AB (je Seed) unter 0 liegt.
- **Unabhängige Prüfung (Sitzung 37, Claude, nur lesend; Codex ohne Guthaben): kein Blocker.** Übernommen: (1) **MAJOR Power:** Das Bootstrap aus nur 10 Pilotwerten schmeichelt dem Vorzeichentest. Ergänzt ist ein Normalmodell (Pilot-SD 0.55, halber Effekt 0.41). Dort hat n = 20 die Power 0.70, n = 25 0.81, n = 30 0.93. Die Regel verlangt jetzt Power ≥ 0.8 in **beiden** Modellen → **n = 25** (Seeds 3100–3124). (2) A2 überlappt B zu ≈ 60 % (≈ 2300 von 3831 Paaren; wie im Piloten, weil der Kandidatenpool B enthält). Das ist kein Störfaktor für D: Kein Lauf paart A2 mit B, beide Wechsel gehen von A zu einem zu A disjunkten Split, und der G-Anteil von A2 liegt auf Zufallsniveau. Überlappung und G-Anteil stehen jetzt in der Split-Metadatei. (3) S1-Zeile und Kopf aktualisiert. Nicht geändert: `split_mismatch` prüft nur die NPY-Dateien, nicht die Metadatei (harmlos, der Neubau ist deterministisch).

- **Eingefroren (Sitzung 37, 2026-09-28, Berlin):** Manifest `lab/confirm/R8_manifest.json` (`REGISTERED` mit Seeds 3100–3124 + `python` + `registration` + `code_sha256`), Commit-ID im Feld `commit`. Selbsttest nach den Änderungen erneut grün. Bereits gesehene Daten: wie oben (EXP-086, EXP-056); kein Lauf mit Seeds 3100–3129.

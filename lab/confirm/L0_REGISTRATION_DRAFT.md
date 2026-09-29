---
id: L0
status: entwurf
datum: 2026-09-28
tags: [confirm/entwurf]
---
# L0-Bestätigung (Entwurf): Steuert die Menge auch unter Minibatch, und was gewinnt gegen eine strukturierte Reihenfolge?

Zurück: [[LAB]] · [[FINDINGS]] · Regel 20b (Priorität 1) · Pilot [[experiments/EXP-100-set-vs-order/README|EXP-100]] · Paper [[paper/draft_short]] §6

**Status:** Gerüst, Sitzung 43 (2026-09-28, vor dem Piloten). Die Hypothesen H1/H2 sind **vor jedem Pilotergebnis** festgelegt. n, Mindesteffekte und die Form von H3 werden erst nach dem Piloten gesetzt. Dieser Pilot ist dann als „gesehene Daten“ aufgeführt. **Nicht eingefroren.**

## Reservierte Seeds

**3720–3799** (80 Seeds; Dateisuche 28.09., Sitzung 43, ohne Treffer). Die Splits kommen aus einem eigenen Strom (SeedSequence [100200, seed, purpose]), nicht aus dem Init-Seed. Genutzt werden die ersten n; der Rest bleibt reserviert.

## Hypothesen (Familie, Holm, α = 0.05)

- **H1 (Steuerung unter i.i.d.-Minibatch, B = 256):** Δ_pow (P1-Definition, W_E-Gruppenleistung, eigene gegen fremde Ziele) am Budgetende > 0. Einseitig, bestätigt = Holm-p < 0.05 und KI-Untergrenze > 0.
- **H2 (kleinere Batches, B = 64):** wie H1.
- **H3 (Konflikt mit der Stride-Reihenfolge):** Form nach dem Piloten. Vorab festgelegt ist nur Folgendes: Zeigt der Pilot keine Wirkung der Reihenfolge (EXP-100-Lesart „Konflikt nicht prüfbar“), gibt es kein H3. Dann wird „Reihenfolge wirkt bei 30 % Daten nicht“ als Pilotbefund berichtet und nicht als Bestätigung.
- **Sekundär (beschreibend):** SGD mit Momentum (wenn die Kalibrierung ein lr liefert), budget-gleiche Full-Batch-Referenz, R5-Zeitverhältnis E gegen R unter Minibatch.

## Offene Punkte vor dem Einfrieren

n aus der Pilotstreuung (Power ≥ 0.8 bei halbem Piloteffekt, Holm und KI-Regel eingerechnet; kleine Piloten schönen die Power, also eher größer). Mindesteffekt, Budget (30 000 oder 15 000 Schritte, nach gemessener Laufzeit), Code-Gerüst `lab/tools/confirm_l0.py` steht (20:01; nach `confirm_r11.py`: Bindung, Lader, Split-Neubau, Holm über H1/H2; `N_SEEDS`/`BUDGET` noch None, der Selbsttest verweigert bis dahin; H3 wird nach dem Piloten ergänzt; ungetestet), unabhängige Prüfung, Smoke durch den eingefrorenen Lader.

## Bereits gesehene Daten

Zum Zeitpunkt dieses Gerüsts: keine L0-Daten. P1/R5 (Full-Batch-Effektgrößen), LeDoux 2026 (Methode). Nach dem Piloten hier EXP-100 mit allen davon beeinflussten Entscheidungen eintragen.

## Nachtrag Sitzung 46 (2026-09-29, 02:10 Berlin): Pilot gesehen, Entscheidungen (noch nicht eingefroren)

**Gesehene Daten:** EXP-100-Pilot (Seeds 3700–3707, 128 Läufe): K2 unter Minibatch groß (Δ_pow iid256 9.60, SD 0.95; iid64 9.85, SD 1.34); feste stride-Reihenfolge bei B 256/64 ohne Wirkung; SGD nicht kalibrierbar; Machbarkeit (B 16 lernt bei wd 1 nicht); B16-Sonde (wd 0.1 lernt; Reihenfolge verschiebt Energie, Spitze 0/3 in O). EXP-106 (B 16, wd 0.1, 8 Seeds) läuft.
**Davon beeinflusst:** (1) n = 10 für H1/H2 (`lab/confirm/L0_power_s46.py`: Power ≈ 1 schon bei n = 6 unter halbem Effekt und 1.5-facher SD; 10 ist die Mindestzahl nach Regel 15b). (2) Kein H3 bei B 256/64 (vorab festgelegte Regel: Konflikt nicht prüfbar → kein H3; Pilotbefund „Reihenfolge wirkt bei 30 % Daten und B ≥ 64 nicht“ wird als Pilot berichtet). (3) **Kandidat H3 aus EXP-106** (B = 16, wd 0.1): Form erst nach dessen Auswertung; falls EXP-106 „nicht prüfbar“ ergibt, entfällt H3 ganz. (4) SGD-Arm entfällt. (5) Budget 30 000 Schritte beibehalten (Laufzeit ≈ 4–5 min je Lauf).
**Nächster Schritt:** EXP-106 auswerten → H3 festlegen → `confirm_l0.py` (N_SEEDS = 10, BUDGET = 30 000) vervollständigen → unabhängige Prüfung → Einfrieren → Smoke → Block (Seeds 3720–3729).

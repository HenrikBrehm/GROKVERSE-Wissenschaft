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

n aus der Pilotstreuung (Power ≥ 0.8 bei halbem Piloteffekt, Holm und KI-Regel eingerechnet; kleine Piloten schönen die Power, also eher größer). Mindesteffekt, Budget (30 000 oder 15 000 Schritte, nach gemessener Laufzeit), Code `confirm_l0.py` nach dem Muster von `confirm_r11.py` (Bindung, Lader, Split-Neubau), unabhängige Prüfung, Smoke durch den eingefrorenen Lader.

## Bereits gesehene Daten

Zum Zeitpunkt dieses Gerüsts: keine L0-Daten. P1/R5 (Full-Batch-Effektgrößen), LeDoux 2026 (Methode). Nach dem Piloten hier EXP-100 mit allen davon beeinflussten Entscheidungen eintragen.

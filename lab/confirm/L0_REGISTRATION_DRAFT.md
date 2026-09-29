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

## Fassung 2 (Sitzung 46, 02:11 Berlin, vor dem Einfrieren; verbindlich, ersetzt Abweichendes oben)

- **Familie = H1 und H2** (Holm über 2, α = 0.05), n = 10 (Seeds 3720–3729), Budget 30 000 Schritte, GPU, AdamW lr 1e-3 / wd 1, i.i.d.-Minibatch B = 256 (H1) und B = 64 (H2), Splits F/G nach der EXP-100-Konstruktion (eigener Zielstrom, O ausgeschlossen).
- **Kein H3 in dieser Familie.** Ein Konflikt-Test im Regime langer Epochen (B = 16, wd 0.1) wird nach [[experiments/EXP-106-l0-b16-long-epochs/README|EXP-106]] als **eigene Registrierung** (L0b, eigene Seeds aus 3730–3799) festgelegt, falls EXP-106 ihn prüfbar macht.
- Keine SGD- und keine B = 16-Arme hier.
- Bekannt aus dem Piloten und vorab festgehalten: Bei B = 64 sind viele Netze am Ende nicht eingeschwungen; H2 misst trotzdem wie vorab festgelegt Δ_pow am Budgetende (keine neue Gültigkeitsregel).

## Fassung 3 (Sitzung 46, 02:22 Berlin, nach der Prüfung vor dem Einfrieren; verbindlich, ersetzt alles Abweichende oben einschließlich der Abschnitte „Hypothesen“, „Offene Punkte“ und Fassung 2)

Unabhängige Prüfung (Claude-Agent, nur lesend; Codex ohne Guthaben): **kein Blocker.** Geprüft: Split-Konstruktion (mit dem Pilot-Salz bytegleich zu allen 8 Pilot-Seeds; für 3720–3729 Ziele disjunkt, ohne O, Zielanteil 0.176–0.196), Seeds 3720–3729 nirgends benutzt, Run-IDs gleich der Trainer-Regel, Lader-Erwartungen an allen 32 Pilotläufen iid256/iid64 ohne Fehler, CODE_FILES vollständig, Holm über 2. Übernommen:

- **Familie = {H1, H2}, Holm über k = 2, α = 0.05.** H1: Δ_pow am Budgetende > 0 bei i.i.d.-Minibatch B = 256; H2: dasselbe bei B = 64 (Aussage: „Steuerung am Budgetende unter B = 64“, nicht „in konvergierten Netzen“). Einseitiger t-Test; **bestätigt = Holm-p < 0.05 und untere Grenze des zweiseitigen 95-%-Perzentil-Bootstraps (confirm_p1) > 0**. Kein Mindesteffekt (bestätigt heißt > 0). **Kein H3** in dieser Familie; ein Konflikt-Test aus EXP-106 wäre eine eigene Registrierung mit eigenen Seeds und eigener Familie.
- **Aufbau:** add 113, 30 % Daten, je Seed F und G (EXP-100-Konstruktion: Zielziehung aus eigenem Strom SeedSequence([100200, s, 0]) ohne O; Testmenge, Phasen und Schlüssel aus den EXP-053-Strömen wie P1), AdamW lr 1e-3, wd 1, β 0.9/0.98, festes Budget 30 000 Schritte (`--stop-after-gen 30000`), W_E-Schnappschuss bei 30 000, GPU, 1 Thread. n = 10 (Seeds 3720–3729), 40 Läufe.
- **Gültigkeit:** Jeder technische Fehler (fehlt, nicht gebunden, Ladefehler, nicht-endliche Werte bzw. divergierter Lauf, Δ_pow nicht endlich) macht **den ganzen Block „nicht auswertbar“** (auch H1, wenn nur ein B-64-Lauf betroffen ist; Konvention wie R11). **Wiederholungsregel:** Reine Infrastrukturfehler vor `--analyze` (z. B. „No HIP GPUs are available“, WinError 5 beim Umbenennen) dürfen mit derselben Jobzeile erneut gestartet werden; gezählt wird nur, was danach noch fehlt oder defekt ist. Keine Ausschlussregel nach Trainingsgenauigkeit.
- **Nebenziele:** SGD, budget-gleiche Full-Batch-Referenz und R5-Zeit sind **gestrichen** (nicht Teil dieses Blocks). **Beschreibend, nicht bestätigend, nach der Auswertung aus den gebundenen result.json/Schnappschüssen (eigenes Skript, als post hoc gekennzeichnet):** Endgenauigkeit (Training/Test) je Lauf und Zahl der Läufe < 0.99 je Arm; H2-Statistik nur über Seeds, deren beide iid64-Läufe ≥ 0.99 Trainingsgenauigkeit haben; Δ_pow gemittelt über die Schnappschüsse 25 000 / 27 500 / 30 000.
- **Gesehene Daten (vollständig):** EXP-100-Machbarkeit (18 Läufe; nach der Regel wirkte die Reihenfolge bei B 64 durch Seed 3702 mit +0.05 → `CONFLICT_B64 = True`; B 16 lernt bei wd 1 nicht), SGD-Kalibrierung (ohne Treffer), B16-Sonde (18 Läufe), Pilotblock (128 Läufe: Δ_pow fb 8.36, fb30k 10.28, iid256 9.60, iid64 9.85, stride256 9.90, stride64 9.88; bei 2000 Schritten fb 8.36, iid256 8.05, iid64 7.29), Vorab-Maskenvorhersage (`mask_prediction_s45`, „unclear“), unabhängige Nachrechnung `recheck_s46` (B 64 am Ende oft nicht eingeschwungen: iid64 7/16 < 0.99), Power-Hilfe `L0_power_s46.py` (Normalmodell, halber Effekt, 1.5-fache SD, Holm k = 3 — konservativ gegenüber k = 2). Die Wechselläufe (`raw_switch`) laufen während des Einfrierens, **ungelesen**. EXP-106 läuft, ungelesen.
- **Davon beeinflusst:** n = 10, Budget 30 000, Streichung von H3/SGD, Wiederholungsregel, die beschreibenden Zusatzanalysen.

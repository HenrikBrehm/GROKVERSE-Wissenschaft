---
id: EXP-100
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-100 (L0-Pilot): Menge gegen Reihenfolge. Steuert die Zusammensetzung auch unter Minibatch, und was gewinnt gegen eine strukturierte Reihenfolge? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2, R5; alle Kernaussagen Full-Batch) · Regel 20b (Priorität 1) · Anlass: LeDoux 2026 (arXiv 2603.25047), Notiz in [[paper/related_work]] (Nachtrag Sitzung 43, 19:20) · Begründung [[paper/outreach/DECISION_2026-09-28]]

**Stand:** Entwurf (Sitzung 43, 2026-09-28, ≈ 19:35 Berlin, Fenster zu). Noch **kein Code**. Der Trainer braucht drei neue Optionen (unten). Sie werden als Patch gebaut und erst nach `confirm_r10.py --analyze` committet (R10 bindet den Trainer-Hash). Pilot = Exploration; die Bestätigung folgt als eigene Registrierung (L0-R) mit Power aus diesem Pilot.

## Frage

LeDoux zeigt bei p = 9973, 0.3 % Daten, Batch 256 und einer festen „Stride“-Reihenfolge (sortiert nach (a mod ⌊√p⌋, a)): Die gelernte Grundfrequenz ist die zur Reihenfolge duale Frequenz, über Seeds mit verschiedenen *zufälligen* Teilmengen gleich. Unsere Kernaussagen (K2: konstruierte Menge steuert die Frequenzen; R5: konstruierte Menge beschleunigt) sind alle Full-Batch ohne Reihenfolge. **L0:** (1) Hält K2/R5 unter i.i.d.-Minibatch (zwei Batchgrößen, AdamW) und mit SGD + Momentum? (2) Bevorzugt eine strukturierte Reihenfolge eine *andere* Frequenz als die Menge: Gewinnt die Menge, die Reihenfolge, oder hängt es vom Regime ab? Jeder Ausgang ist ein Befund und kommt so ins Paper.

## Aufbau (vorläufig; wird mit dem Code verbindlich)

- add 113, 1-Schicht-Transformer der Studie (arch25k), AdamW lr 1e-3, wd 1, β 0.9/0.98 wie immer; Trainingsanteil 30 % (3831 Paare); GPU.
- **Reihenfolge-Frequenzen:** Stride für p = 113: s = ⌊√113⌋ = 10. Das Leistungsspektrum von (a mod 10) über Z₁₁₃ hat seine Spitze bei **k = 11** (49 % der Leistung), dann 23 (10 %), 34 (9 %), 12 (8 %), 45, 22 (gerechnet in Sitzung 43). O = {11, 12, 22, 23, 34, 45}.
- **Splits:** je Seed zwei konstruierte Splits F und G (EXP-053/P1-Bau, 5 Ziele je Split, disjunkt) mit Zielmengen **ohne O**. Dazu ein Zufallssplit R gleicher Größe. Eigene Zufallsströme (SeedSequence über Experiment/Split/Arm/Reihenfolge, Astra 5).
- **Arme je Seed** (je F und G, außer R):
  | Arm | Batch | Reihenfolge | Optimierer |
  |---|---|---|---|
  | FB | voll | – | AdamW (Referenz, wie P1) |
  | iid256 | 256 | i.i.d. je Epoche neu gemischt | AdamW |
  | iid64 | 64 | i.i.d. | AdamW |
  | sgdm256 | 256 | i.i.d. | SGD, Momentum 0.9 (lr kalibrieren, s. u.) |
  | stride256 | 256 | fest: sortiert nach (a mod 10, a), jede Epoche gleich | AdamW (Konflikt-Arm) |
  | R-iid256, R-stride256 | 256 | i.i.d. / Stride | AdamW, Zufallssplit (Reihenfolge allein) |
  → 12 Läufe je Seed; Pilot **8 frische Seeds** (Vorschlag 3700–3707, vor dem Festlegen per Dateisuche prüfen) = 96 Läufe.
- **Budget:** FB 2000 Schritte (wie P1). Minibatch-Arme 30 000 Schritte (= 2000 Epochen bei B = 256, 500 Epochen bei B = 64); Schritte und Epochen werden beide berichtet. Schnappschüsse von W_E bei 0, 50, 250, 2000 und am Ende.
- **SGD-Kalibrierung (vor dem Pilot, als solche gekennzeichnet):** lr ∈ {0.1, 0.3, 1.0} an 2 Seeds (nur F); die kleinste lr, die in 30 000 Schritten generalisiert. Generalisiert keine: SGD-Arm „nicht auswertbar“ (so berichten; die Slingshot-Studie fand ohne Adam kein Grokking).

## Messgrößen und Lesarten (Entwurf, wird vor dem ersten Lauf eingefroren)

- **K2 unter Minibatch:** Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] der W_E-Gruppenleistung am Ende (P1-Definition, `confirm_p1.delta_pow`), je Arm; Mittel, Bootstrap-KI. „Menge steuert unter Minibatch“, wenn die KI-Untergrenze in iid256 und iid64 > 0 liegt.
- **Konflikt (stride256):** (i) Δ_pow unter Stride; (ii) Reihenfolge-Anteil o = P(O)/P(alle) am Ende, stride gegen iid (E- und R-Splits); (iii) Spitzenfrequenz je Lauf. Lesarten: **„Menge gewinnt“**: Δ_pow-KI > 0 unter Stride und in ≥ 6/8 Seeds liegt die Spitze nicht in O. **„Reihenfolge gewinnt“**: Spitze in O in ≥ 6/8 Seeds und Δ_pow-KI enthält 0. Sonst **„beide wirken“** (mit Größe beider Effekte).
- **Reihenfolge allein (R-stride256 gegen R-iid256):** Repliziert LeDoux' Effekt bei p = 113 und 30 % Daten? (o-Anteil, Spitze in O.) Wenn nicht, ist das eine Grenze des Konflikt-Arms und wird so berichtet.
- **R5 unter Minibatch (beschreibend im Pilot):** Epochen bis Test ≥ 0.95, E gegen R in iid256.
- **Sekundär (später, eigener Schritt):** Wechsel F → G nach 25/50 Schritten unter iid256.

## Nötige Trainer-Optionen (Patch nach R10)

`--batch-size B` (0 = voll, Standard), `--order {iid, fixed, stride}` (eigener Zufallsstrom, Epoche = ⌈n/B⌉ Schritte, nach einem Datenwechsel neu aufgebaut), `--optimizer {adamw, sgdm}` mit `--sgd-momentum`. Alles andere unverändert; Standardwerte ändern keinen alten Lauf (Fingerprint nur bei Abweichung). Tests zuerst: (1) B = n und `iid` gibt bitgleich den Full-Batch-Lauf? (nur, wenn die Reihenfolge die Summe nicht ändert; sonst Toleranz), (2) `stride` erzeugt genau die sortierte Reihenfolge, jede Epoche gleich, (3) `iid` mischt je Epoche neu und ist über den Seed reproduzierbar, (4) SGD-Schritt = −lr·(Momentum-Puffer) ohne Adam-Zustand. Dann unabhängige Prüfung.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

P1/P4/R5 (Full-Batch-Größen von Δ_pow und der Beschleunigung), LeDoux (Methode, Batch 256), Slingshot (SGD-Risiko). Keine L0-Seeds benutzt.

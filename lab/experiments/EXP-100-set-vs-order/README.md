---
id: EXP-100
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-100 (L0-Pilot): Menge gegen Reihenfolge. Steuert die Zusammensetzung auch unter Minibatch, und was gewinnt gegen eine strukturierte Reihenfolge? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2, R5; alle Kernaussagen Full-Batch) · Regel 20b (Priorität 1) · Anlass: LeDoux 2026 (arXiv 2603.25047), Notiz in [[paper/related_work]] (Nachtrag Sitzung 43, 19:20) · Begründung [[paper/outreach/DECISION_2026-09-28]]

**Stand:** Entwurf (Sitzung 43, 2026-09-28, ≈ 19:35 Berlin, Fenster zu). Trainer-Optionen liegen seit 19:20 als `trainer_l0.patch` vor (Test `test_minibatch_order` zuerst geschrieben; ungetestet, statische Prüfung läuft). Anwenden und committen erst nach `confirm_r10.py --analyze` (R10 bindet den Trainer-Hash). Achtung: Der Patch und der zurückgestellte EXP-097-Patch berühren dieselben Stellen, also nicht beide zugleich anwenden. `design.py` steht (19:22): Splits für die Seeds 3700–3707 erzeugt (numpy; Zielanteil F/G 0.177–0.194 wie P1; Zufallssplit R bei Zufallsniveau 0.09; O-Anteil in allen Splits ≈ Zufallsniveau 0.09–0.11), `calib.txt` (SGD-lr 0.1/0.3/1.0 an 2 Seeds) und `smoke.txt` (300 Schritte je neuer Option). `--jobs` verweigert, solange `SGD_LR` nicht aus der Kalibrierung gesetzt ist. `analyze.py` mit den Lesarten im Docstring steht (19:24, ungetestet; Selbsttest ab 23:59 über den Wächter). Vor dem Pilot-Block: statische Prüfung, dann `analyze.py` + `jobs.txt` committen (Festlegung). Pilot = Exploration; die Bestätigung folgt als eigene Registrierung (L0-R) mit Power aus diesem Pilot.

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

## Fassung 2 nach der statischen Prüfung (Sitzung 43, 19:31, vor jedem Lauf; verbindlich, ersetzt Abweichendes oben)

Prüfer (Claude-Agent, nur lesend, Splits im Speicher byte-genau nachgebaut, O dreifach nachgerechnet): Monkeypatch, Budget-Erzwingung, Run-ID-Muster und Lader stimmen. Übernommen:
- **Blocker behoben:** Smoke, Kalibrierung und Machbarkeit schreiben nach `raw_smoke`, `raw_calib`, `raw_feas`. Sonst hätten gleiche Run-IDs Pilotläufe verweigert oder die Kalibrierläufe zu Pilotdaten gemacht.
- **Konflikt-Lesart:** „Menge gewinnt“ nur, wenn die Reihenfolge überhaupt wirkt (R allein „wirkt“ oder gepaartes KI von o(stride256) − o(iid256) > 0). Sonst gilt **„Konflikt nicht prüfbar (Reihenfolge wirkt nicht)“**. Ohne diese Bedingung wäre „Menge gewinnt“ schon bei einer wirkungslosen Reihenfolge herausgekommen, denn die Spitze liegt zufällig in ≈ 90 % der Läufe außerhalb von O. Zusätzlich berichtet: Δ_pow(stride) − Δ_pow(iid256) gepaart, Anteil der Läufe mit einer O-Frequenz unter den Top 5.
- **Machbarkeit vor dem Block** (`feas.txt`: R-stride256 gegen R-iid256, 3 Seeds): LeDoux arbeitete bei 0.3 % Daten, wo i.i.d. scheitert. Hier gibt es 30 % Daten und 15 Schritte je Epoche, und Adams β₂ mittelt über mehr als 3 Epochen. **Vorab festgelegte Regel:** Ist o(R-stride) − o(R-iid) in allen 3 Seeds ≤ 0.02 und liegt keine Spitze in O, dann läuft der Konflikt-Arm zusätzlich mit Batch 64 und Stride-Reihenfolge. Das wird vor dem Block hier eingetragen. Ein „Reihenfolge wirkt nicht bei 30 % Daten“ ist selbst ein Befund (Abgrenzung zu LeDoux).
- **Budget-gleiche Referenz:** Arm `fb30k` (Full-Batch, 30 000 Schritte), damit sich „Minibatch“ von „langem Training“ trennen lässt. Schnappschüsse alle 2500 Schritte.
- **SGD-Kalibrierung:** Raster 0.03/0.1/0.3/1.0/3.0. Gewählt wird das kleinste lr, das in beiden Seeds innerhalb von 50 % des Budgets generalisiert.
- `delta_pow_checked` (nicht-endlich → ungültig), Zahl der generalisierten Läufe je Arm, R5-Zeiten (Median in Epochen, E gegen R) jetzt im Ergebnis. Die Gültigkeit umfasst fb, fb30k, iid256, iid64 und stride256.
- Hinweis: `analyze.py` braucht torch (EXP-043-Import), also das globale Python über den Wächter.

Umfang jetzt: 8 Seeds × (6 Arme × F/G + 2 R) = 112 Läufe, dazu Machbarkeit (6), Kalibrierung (10), Smoke (3).

## Ablauf in der Nacht (nach R10 `--analyze` und dem Patch-Commit)

```
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/smoke.txt --workers 3     # s/Schritt messen, events.minibatch lesen
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/feas.txt --workers 6      # Machbarkeit: wirkt Stride bei 30 % Daten? Regel oben
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/calib.txt --workers 8     # SGD-lr wählen (Regel oben), SGD_LR in design.py setzen, README
python lab/experiments/EXP-100-set-vs-order/design.py --jobs > lab/experiments/EXP-100-set-vs-order/jobs.txt   # nach analyze.py + Commit
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/jobs.txt --workers 8
```
Laufzeit schätzen, bevor der Block startet: 30 000 Minibatch-Schritte je Lauf, 84 solche Läufe. Ist das länger als ≈ 3 h, das Budget auf 15 000 Schritte senken (vor dem Block festlegen).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

P1/P4/R5 (Full-Batch-Größen von Δ_pow und der Beschleunigung), LeDoux (Methode, Batch 256), Slingshot (SGD-Risiko). Keine L0-Seeds benutzt.

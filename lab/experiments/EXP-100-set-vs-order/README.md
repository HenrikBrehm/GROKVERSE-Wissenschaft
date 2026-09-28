---
id: EXP-100
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-100 (L0-Pilot): Menge gegen Reihenfolge. Steuert die Zusammensetzung auch unter Minibatch, und was gewinnt gegen eine strukturierte Reihenfolge? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2, R5; alle Kernaussagen Full-Batch) · Regel 20b (Priorität 1) · Anlass: LeDoux 2026 (arXiv 2603.25047), Notiz in [[paper/related_work]] (Nachtrag Sitzung 43, 19:20) · Begründung [[paper/outreach/DECISION_2026-09-28]]

**Stand:** Entwurf (Sitzung 43, 2026-09-28, ≈ 19:35 Berlin, Fenster zu). Trainer-Optionen liegen seit 19:20 als `trainer_l0.patch` vor (Test `test_minibatch_order` zuerst geschrieben; ungetestet, statisch geprüft, Befunde eingearbeitet). Anwenden und committen erst nach `confirm_r10.py --analyze` (R10 bindet den Trainer-Hash). Achtung: Der Patch und der zurückgestellte EXP-097-Patch berühren dieselben Stellen, also nicht beide zugleich anwenden. `design.py` steht (19:22): Splits für die Seeds 3700–3707 erzeugt (numpy; Zielanteil F/G 0.177–0.194 wie P1; Zufallssplit R bei Zufallsniveau 0.09; O-Anteil in allen Splits ≈ Zufallsniveau 0.09–0.11), `calib.txt` (SGD-lr 0.03/0.1/0.3/1.0/3.0 an 2 Seeds) und `smoke.txt` (300 Schritte je neuer Option). `--jobs` verweigert, solange `SGD_LR` nicht aus der Kalibrierung gesetzt ist. `analyze.py` mit den Lesarten im Docstring steht (19:24, ungetestet; Selbsttest ab 23:59 über den Wächter). Vor dem Pilot-Block: statische Prüfung, dann `analyze.py` + `jobs.txt` committen (Festlegung). Pilot = Exploration; die Bestätigung folgt als eigene Registrierung (L0-R) mit Power aus diesem Pilot.

> [!summary] Aktuell gültig (Stand Sitzung 44, 2026-09-28 abends; Einzelheiten in den Nachträgen unten)
> - **Reihenfolge der Nacht:** Patch anwenden + Tests + Commit → `analyze.py --selftest`, `switch_analyze.py --selftest` → `smoke.txt` (3) → **`feas.txt` (12 Läufe: B 256 und 64)** → `feas_read.py` → falls Reihenfolge nur bei B 64 wirkt: `CONFLICT_B64 = True` in `design.py` + Vermerk → `calib.txt` → `SGD_LR` → `design.py --jobs > jobs.txt` → Commit → Pilot → `analyze.py` → `switch.txt` (64) → `switch_analyze.py`.
> - **Vorhersage erster Ordnung (vor den Läufen):** B 256 ausgewaschen, B 64 an der Kante (nachgerechnet; Messerschneide).
> - **Erwartung E2:** bei gleicher Schrittzahl fb ≥ iid256 ≥ iid64 (beschreibend).
> - **Deutungssätze je Ausgang:** [[paper/L0_DEUTUNGEN]].
> - Befehlsliste der Nacht: [[NACHT_2026-09-29]].

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

**Planprüfung Sitzung 43 (Blocker behoben):** `fb` und `fb30k` hatten dieselbe Run-ID (Schritte gehören nicht zur ID) → `fb30k` schreibt nach `raw_fb30k`, `analyze.py` lädt von dort. **GPU-Prozesse:** zusammen mit R11 höchstens 10 (z. B. R11 5 Worker, L0 höchstens 5; Smoke 3).

## Ablauf in der Nacht (nach R10 `--analyze` und dem Patch-Commit)

```
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/smoke.txt --workers 3     # s/Schritt messen, events.minibatch lesen
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/feas.txt --workers 5      # Machbarkeit: wirkt Stride bei 30 % Daten? Regel oben
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/calib.txt --workers 5     # SGD-lr wählen (Regel oben), SGD_LR in design.py setzen, README
python lab/experiments/EXP-100-set-vs-order/design.py --jobs > lab/experiments/EXP-100-set-vs-order/jobs.txt   # nach analyze.py + Commit
python lab/tools/parallel_queue.py lab/experiments/EXP-100-set-vs-order/jobs.txt --workers 5   # neben R11 (5); allein bis 8
```
Laufzeit schätzen, bevor der Block startet: 30 000 Minibatch-Schritte je Lauf, 84 solche Läufe. Ist das länger als ≈ 3 h, das Budget auf 15 000 Schritte senken (vor dem Block festlegen).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

P1/P4/R5 (Full-Batch-Größen von Δ_pow und der Beschleunigung), LeDoux (Methode, Batch 256), Slingshot (SGD-Risiko). Keine L0-Seeds benutzt.

## Erwartung vor dem Piloten (Sitzung 44, 20:49; beschreibend, entscheidet nichts, ändert keine Lesart)

Aus der R1-Nachauswertung (Sitzung 44, draft §3.7, post hoc): Die Größe von Δ_pow folgt bis Schritt 2000 weitgehend der Zeit t·lr·wd. Alle AdamW-Arme von L0 haben dasselbe lr und wd, also bei gleicher Schrittzahl dieselbe lr·wd-Zeit. **Erwartung E1:** Wäre die Steuerung reine Mengeneigenschaft und der Minibatch-Rauschterm unwichtig, läge Δ_pow(iid256, t = 2000) nahe Δ_pow(fb, 2000). **Erwartung E2 (wahrscheinlicher):** Rauschen vergrößert Adams zweites Moment und verkleinert die normierten Schritte; bei Batch 64 kommt jede Zahl nur ≈ 1–2-mal je Batch vor (dünne Gradienten auf W_E-Zeilen). Daher die Rangfolge fb ≥ iid256 ≥ iid64 bei gleicher Schrittzahl, mit iid256 innerhalb von ≈ 30 % von fb. Berichtet wird das gepaarte Verhältnis bei 2000 und am Ende. Weicht es stark ab (iid256 < 0.5 × fb), ist das kein Befund gegen K2, sondern ein Hinweis, dass die Zeit unter Minibatch anders läuft; die registrierte Lesart („KI > 0“) bleibt maßgeblich.

## Vorhersage erster Ordnung vor dem Piloten (Sitzung 44, 21:01; ändert keine Lesart)

`firstorder_window_s44.py` (Regel vorab, committet 11d6196c; nur Split-Dateien): Summe der Maskenterme der ersten L Batches, M0-Spektrum, O-Anteil Stride minus iid auf dem Zufallssplit R, verglichen mit dem Zielüberschuss des konstruierten Splits (0.094). **B = 256:** +0.005 bei L = 50 (3.3 Epochen) → in erster Ordnung ausgewaschen. **B = 64:** +0.147 bei L = 25, +0.047 bei L = 50 (0.84 Epochen) → „kann wirken“, genau an der Schwelle. Erwartung damit: Die Machbarkeitsprüfung (R-stride256 gegen R-iid256) zeigt kaum Reihenfolgewirkung; dann greift die vorab festgelegte Ausweichregel (Konflikt-Arm zusätzlich mit B = 64). Regime-Hypothese für die Deutung: Reihenfolge kann nur wirken, wenn eine Epoche (n/B Schritte) länger ist als das Festlegungsfenster (≈ 25–50 Schritte). LeDoux' Regime (Epoche ≈ 1165 Schritte) liegt weit auf der Reihenfolge-Seite.

**Machbarkeit erweitert (Sitzung 44, vor jedem Lauf):** Wegen der Vorhersage oben enthält `feas.txt` jetzt 12 statt 6 Läufe: R-iid/R-stride bei B = 256 **und** B = 64 (je 3 Seeds, 30 000 Schritte, `raw_feas`). Auswertung mit `feas_read.py` nach der Regel aus Sitzung 43, je Batchgröße getrennt; daneben die Vorhersage erster Ordnung. Folge wie vorab festgelegt: Wirkt die Reihenfolge nur bei B = 64, läuft der Konflikt-Arm im Piloten zusätzlich mit B = 64 (dann `stride64` in `ARMS` aufnehmen und hier eintragen, bevor der Block startet); wirkt sie bei keiner Batchgröße, lautet das L0-Konfliktergebnis „bei 30 % Daten nicht prüfbar“ (Abgrenzung zu LeDoux, ein Befund). Die Seeds 3700–3702 der Machbarkeit bleiben dieselben wie zuvor geplant.

**Korrektur nach unabhängiger Nachrechnung (Sitzung 44, 21:03; Claude-Agent, eigener Code):** Alle Zahlen stimmen (Mengenüberschuss 0.09398; B = 256: 0.0200/0.0049; B = 64: 0.1468/0.0476 bei 20 bzw. 0.0472 bei 100 iid-Ziehungen). **Das Urteil „kann wirken“ bei B = 64, L = 50 ist aber nicht belastbar:** Rand 0.0002–0.0006 über der Schwelle 0.04699; 2 von 8 Seeds einzeln darunter (0.040, 0.043), Bootstrap über Seeds P(Lücke < 0) ≈ 0.40. Der Wert fällt steil mit L (B = 64: L = 25 0.147, 40 0.082, 45 0.067, 50 0.047, 55 0.021, 60 **exakt 0**, weil nach einer Epoche jedes Paar genau einmal gesehen ist). Das Urteil sagt also vor allem, wo L relativ zur Epoche liegt. **Gültige Lesart:** „B = 256: in erster Ordnung ausgewaschen (klar); B = 64: großer Reihenfolgeüberschuss in der ersten Epoche, der am Epochenende verschwindet; ob das im Festlegungsfenster reicht, ist an der Kante“. Weitere Einwände übernommen: Adams Normierung (fast Vorzeichenschritte) und β₁-Glättung über ≈ 10 Batches fehlen; Gewichte, Weight Decay und Nichtlinearität fehlen; der Vergleich stellt einen Rest innerhalb einer Epoche einer statischen Maske gegenüber. Die Rechnung ist höchstens eine notwendige Bedingung. (Der Prüfer nahm β₂ = 0.999 an; bei uns 0.98, Gedächtnis ≈ 50 Schritte, ändert die Richtung des Einwands nicht.) Die Erweiterung der Machbarkeit auf B = 64 bleibt richtig: Dort wird die Frage empirisch entschieden.

**Auswertung für den B = 64-Konflikt vorbereitet (Sitzung 44, 21:07, vor jedem Lauf):** `analyze.py` rechnet die Konflikt-Lesarten (Fassung 2, unverändert) jetzt über eine Funktion `conflict_reading(stride, iid)`. Die registrierte Lesart bleibt `Konflikt` = stride256 gegen iid256. Steht `stride64` in `ARMS` (Ausweichregel), kommt `Konflikt_B64` = stride64 gegen iid64 mit denselben Regeln dazu. **Dann auch `R_ARMS` um `iid64` und `stride64` erweitern** (für „Reihenfolge allein“ bei B = 64). Der Selbsttest deckt beide Wege ab (ungetestet bis zum Fenster).

**Ein Schalter für den B = 64-Konflikt (Sitzung 44, nach Prüfung):** `design.py`: `CONFLICT_B64 = True` fügt `stride64` in `ARMS` (F/G) **und** `iid64`/`stride64` in `R_ARMS` ein. Nur setzen, wenn `feas_read.py` eine Reihenfolgewirkung allein bei B = 64 zeigt, und das hier vor dem Block vermerken. Standard bleibt `False`; `feas.txt` und die Pilot-Jobliste sind unverändert.

## Sekundärer Teil: Wechsel bei 25/50 Schritten unter Minibatch (Sitzung 44, 21:14, vor jedem Lauf; Exploration)

Regel 20b nennt ihn als sekundär; bisher nicht ausgearbeitet. `design.py --switch` → `switch.txt` (64 Läufe: Seeds 3700–3707, Arme fb und iid256, Wechsel F→G und G→F bei t = 25 und 50, danach das Budget des Arms; Ordner `raw_switch`; die reinen F/G-Läufe kommen aus dem Pilotblock). Auswertung `switch_analyze.py` (π wie N28/EXP-056; Lesarten im Docstring: Referenz d_fb = π_fb(50) − π_fb(25) muss KI > 0 haben, sonst nur beschreibend; unter Minibatch „Fenster wie Full-Batch“ / „verschoben oder fehlt“ (mit Richtung) / „umgekehrt“). Erst nach dem Pilotblock rechnen (braucht dessen reine Läufe). Anlass zusätzlich: Die N52-Schwelle setzt voraus, dass das Festlegungsfenster unter Minibatch ähnlich bleibt; bei B = 256 liegen beide Wechselzeiten nach mindestens einer vollen Epoche.
**Stütze für E2 aus derselben Rechnung erster Ordnung (Sitzung 44, 21:23, beschreibend):** Zielanteil der aufsummierten Batch-Masken des konstruierten Splits F unter i.i.d.-Batches: B = 256 nach 25 Schritten 0.174, nach 50 0.181 (voller Split 0.183); B = 64 nach 25 Schritten 0.121, nach 50 0.163. Bei B = 64 ist das Mengensignal im Festlegungsfenster also verdünnt (nach 25 Schritten ist nur ein Teil der Paare gesehen). Passt zur erwarteten Rangfolge fb ≥ iid256 ≥ iid64, falls das Fenster unter Minibatch ähnlich bleibt.

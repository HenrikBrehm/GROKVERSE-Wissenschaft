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
> - **Reihenfolge der Nacht:** Patch anwenden + Tests + Commit → `analyze.py --selftest`, `switch_analyze.py --selftest` → `smoke.txt` (3) → **`feas.txt` (18 Läufe: B 256, 64 und 16; B 16 seit Sitzung 45)** → `feas_read.py` → falls Reihenfolge nur bei B 64 wirkt: `CONFLICT_B64 = True` in `design.py` + Vermerk → `calib.txt` → `SGD_LR` → `design.py --jobs > jobs.txt` → Commit → Pilot → `analyze.py` → `switch.txt` (64) → `switch_analyze.py`.
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

**Nach der Konsistenzprüfung (Sitzung 44, vor jedem Lauf):** (1) Zahlen: Machbarkeit jetzt 12 Läufe; der Pilotblock hat 112 Läufe, mit `CONFLICT_B64 = True` 144 (+16 stride64 auf F/G, +16 iid64/stride64 auf R); die Laufzeitregel („84 solche Läufe“) dann mit 116 Minibatch-Läufen rechnen. (2) Vor dem Block `jobs.txt` statisch prüfen (Agent, nur lesend), wie oben verlangt. (3) **SGD-Kalibrierung ohne Treffer:** `SGD_DROPPED = True` in `design.py` nimmt `sgdm256` aus den Armen; `analyze.py` läuft dann ohne `SGD_LR`; im Ergebnis „SGD-Arm nicht auswertbar“. (4) Budget 15 000 statt 30 000: `switch.txt` neu erzeugen.

**Machbarkeit um B = 16 erweitert (Sitzung 45, 22:15 Berlin gemessen, vor jedem Lauf; Anlass: simulierte Gutachter-Prüfung der Kurzfassung):** Bei B = 256/64 dauert eine Epoche 15/60 Schritte, bei LeDoux ≈ 1170; der Konflikt-Arm wäre dann fast sicher „nicht prüfbar“, und der Einwand „Full-Batch-Artefakt / falsches Regime“ bliebe offen. Erste Ordnung (`firstorder_window_s44.py` mit B = 256, 64, 16; Ausgabe `firstorder_window_s45_b16.json`, die s44-Datei unverändert): Reihenfolge-Überschuss auf O bei L = 50: B 256 0.005, B 64 0.0473, **B 16 0.194** (Schwelle = halber Mengenüberschuss 0.047) → bei B = 16 „kann wirken“, doppelt so groß wie der Zielüberschuss der Menge. **Zweite Vorhersage (neu):** Bei B = 16 sieht das Netz im Fenster nur 0.21 Epochen; dann ist schon unter i.i.d. der frühe Zielanteil des konstruierten Splits klein (0.103 gegen 0.181 bei B = 256). Kleine Batches könnten K2 also selbst schwächen oder das Festlegungsfenster in Schritten verlängern. **Änderung:** `FEAS_B16` (iid16/stride16) nur in der Machbarkeit (`feas.txt` 12 → 18, gleiche Regel, `feas_read.py` liest B = 16 mit). Die Pilotarme bleiben unverändert; ein B = 16-Konfliktarm bräuchte einen eigenen Schalter plus Auswertungscode und wird erst nach `feas_read.py` entschieden. `calib.txt`, `smoke.txt`, `switch.txt` byte-gleich neu erzeugt.

**Vorhersage an unberührten Fällen (Sitzung 45, 22:38 Berlin gemessen, vor jedem EXP-100-Lauf; Exploration, keine GPU-Kosten):** `mask_prediction_s45.py` prüft an den 18 Machbarkeitsläufen (Zufallssplit R, Seeds 3700–3702), ob der Befund aus R4 (post hoc: Top-5 der gelernten Frequenzen beim 78. Perzentil des eigenen M0c) unter Minibatch wiederkehrt. Vorab: „überträgt sich“, wenn jede Batchgröße bei i.i.d. im Mittel ≥ 0.65 liegt; „nicht“, wenn das Mittel über alle 9 i.i.d.-Läufe ≤ 0.55; sonst „unklar“. Beschreibend: Wirkt die Reihenfolge bei einer Batchgröße, sollten die Stride-Läufe dort tiefer liegen. Aufruf nach `feas_read.py`: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/mask_prediction_s45.py`.

**Schalter für einen B = 16-Konflikt vorbereitet (Sitzung 45, 22:39 Berlin gemessen, vor jedem Lauf; ungetestet bis zum Selbsttest im Fenster):** `design.py`: `CONFLICT_B16 = True` fügt iid16/stride16 auf F/G und R hinzu (+48 Läufe: 112 → 160, mit B 64 zusammen 192; per Ausführung aller vier Schalterkombinationen gezählt). `analyze.py` liest `Konflikt_B16` mit denselben Regeln wie B 64 (Schleife über 64 und 16 statt eines festen B 64-Blocks) und gibt Δ_pow bei iid16 beschreibend aus (erste Ordnung: nur 0.21 Epochen im Fenster). Selbsttest um den B 16-Fall ergänzt. Nur setzen, wenn `feas_read.py` eine Reihenfolgewirkung bei B = 16 zeigt, und das hier vor dem Block vermerken. Standard `False`; alle Joblisten byte-gleich.

## Machbarkeit: Ergebnis und Entscheidungen (Sitzung 46, 2026-09-29, 01:05 Berlin; vor jedem Pilotlauf)

18/18 Läufe fertig (Zufallssplit R, Seeds 3700–3702, 30 000 Schritte, GPU, Log `lab/runner/logs/pq_20260928T225157_241451Z`). `feas_read.py` (Regel aus Sitzung 43/45: „keine Wirkung“, wenn o(stride) − o(iid) ≤ 0.02 in allen 3 Seeds und kein stride-Lauf mit Spitze in O):

| B | o(stride) − o(iid) je Seed | Spitze stride in O | Regel | Test-Gen. iid / stride (Endgenauigkeit) |
|---|---|---|---|---|
| 256 | +0.019, 0.000, 0.000 | 0/3 | keine Wirkung | 1.00 / 1.00 in allen Seeds |
| 64 | −0.351, −0.005, **+0.050** | 0/3 | Wirkung (nur durch Seed 3702) | 0.98, 0.90, 0.98 / 0.73, 0.95, 0.62 |
| 16 | +0.028, **+0.860, +0.860** | 2/3 | Wirkung | **0.73, 0.14, 0.12 / 0.09, 0.07, 0.05** |

Vorhersage erster Ordnung (vorab): B 256 ausgewaschen ✓, B 64 „an der Kante“ ✓ (Wirkung nur knapp nach der Regel), B 16 „kann wirken“ ✓.

**Wichtige Einschränkung bei B = 16:** Mit der Standard-Lernrate (AdamW 1e-3, wd 1) lernt das Netz bei B = 16 die Aufgabe in 30 000 Schritten nicht: Trainingsgenauigkeit iid 0.78 / 0.18 / 0.14, stride 0.11 / 0.08 / 0.06. Die starke Konzentration auf O (86 % der Gruppenleistung in 2/3 Seeds) entsteht also in einem Netz, das die Menge gar nicht lernt. Das ist kein Konflikt „Menge gegen Reihenfolge“ im Sinn der Frage (die Menge hat keine Chance, weil das i.i.d.-Netz selbst nicht lernt).

**Entscheidungen (vor jedem Pilotlauf):**
1. `CONFLICT_B64 = True` nach der vorab festgelegten Regel (Wirkung bei B = 64). Vermerk: Die Wirkung hängt an einem Seed (+0.05), keine stride-Spitze in O; dafür generalisieren 2/3 stride64-Läufe nicht (≥ 0.95). Pilot jetzt 144 Läufe.
2. **Kein B = 16-Konfliktarm** (`CONFLICT_B16` bleibt aus): Der i.i.d.-Arm lernt bei B = 16 nicht, also sind weder K2 noch der Konflikt dort messbar. Berichtet wird der Befund selbst: „bei B = 16 mit den Standard-Hyperparametern lernt das Netz nicht; in diesem Zustand bestimmt eine feste Reihenfolge das W_E-Spektrum (2/3 Seeds)“. Eine B = 16-Variante mit angepasster Lernrate (z. B. Wurzelregel lr/4) wäre ein eigener, neu festzulegender Versuch, nicht Teil dieses Piloten.

**Vorab-Vorhersage an unberührten Läufen (`mask_prediction_s45.py`, Sitzung 45 festgelegt):** P-iid **„unclear“** (Mittel 0.63; Regel verlangt ≥ 0.65 in jeder Batchgröße: B 256 0.638, B 64 0.709, B 16 0.543), P-pred **„unclear“** (Überlappung 0.18; B 256 0.27, B 64 0.20, B 16 0.07; Zufall 0.09). Beschreibend: In den Batchgrößen, in denen das Netz lernt (256, 64), liegen die gelernten Top-5 beim 64.–71. Perzentil des Maskenspektrums (voll Batch R4: 78.), bei B = 16 (lernt nicht) nahe Zufall. P-order (beschreibend): bei B = 64 zieht die feste Reihenfolge die Wahl vom Maskenspektrum weg (Perzentil 0.50 gegen 0.71 iid), wie vorhergesagt. n = 3 je Zelle, Exploration.

### Zusatz B = 16-Sonde (Sitzung 46, 01:10 Berlin, festgelegt vor jedem Lauf; Exploration, kein Teil des Piloten)

*Frage:* Gibt es eine einfache Einstellung, in der das Netz bei B = 16 (240 Schritte je Epoche, das LeDoux-nähere Regime langer Epochen) lernt? Nur dann ist dort ein Konflikt „Menge gegen Reihenfolge“ prüfbar. *Aufbau:* `b16probe.txt`, 18 Läufe = 3 Varianten × (iid16, stride16) × R-Split der Seeds 3700–3702, 30 000 Schritte, eigene Ausgabeordner `raw_b16probe_v1/v2/v3`. v1: lr 2.5·10⁻⁴ mit β₁/β₂ = 0.99375/0.99875 (Wurzelregel nach Malladi et al. 2022 für Batch × 1/16); v2: lr 2.5·10⁻⁴, Standard-β; v3: lr 1e-3, weight decay 0.1. *Lesart:* Eine Variante „lernt“, wenn iid16 in ≥ 2/3 Seeds Testgenauigkeit ≥ 0.95 am Ende erreicht. Für lernende Varianten die Reihenfolge-Regel von `feas_read.py` (Differenz o(stride) − o(iid) > 0.02 in einem Seed oder stride-Spitze in O). *Erwartung:* v1/v2 laufen nach der Wurzelregel etwa 16-mal „langsamer“ in Schritten und lernen in 30 000 Schritten womöglich nicht; v3 unklar. Lernt keine: „bei B = 16 in 30 000 Schritten mit diesen Einstellungen kein Lernen“ berichten; kein weiteres Suchen in dieser Sitzung. Ein B = 16-Konfliktarm bräuchte danach eine eigene Festlegung.

### SGD-Kalibrierung: Ergebnis (Sitzung 46, 01:18 Berlin)

10 Läufe (Seeds 3700/3701, Split F, B = 256, SGD mit Momentum 0.9, lr 0.03/0.1/0.3/1.0/3.0, 30 000 Schritte; Log `lab/runner/logs/pq_20260928T230444_497079Z`). lr 0.03: beide Seeds lernen nicht (Trainingsgenauigkeit 0.01). lr 0.1: Seed 3701 generalisiert (Schritt 1400), Seed 3700 divergiert (nicht-endliche Werte, Artefaktprüfung des Trainers schlägt fehl). lr 0.3/1.0/3.0: beide divergieren. **Kein lr generalisiert in beiden Seeds** → nach der vorab festgelegten Regel `SGD_DROPPED = True`, **SGD-Arm „nicht auswertbar“** (so berichten). Einordnung: Die SGD-Frage (Regel 20b „ein Arm SGD mit Momentum“) bleibt offen; ein engeres Raster (z. B. 0.05–0.1) oder Gradienten-Clipping wäre ein neuer Versuch. `jobs.txt` (128 Läufe = 8 Seeds × 6 Arme × F/G + 8 × 4 R-Läufe) aus `design.py --jobs`.

### Pilotblock: Start (Sitzung 46, ≈ 01:24 Berlin)

Statische Prüfung von `jobs.txt` (Agent, nur lesend): **kein Blocker**, nichts Größeres; `jobs.txt` byte-gleich mit `design.py --jobs`, Abdeckung exakt (8 Seeds × 6 Arme × F/G + 8 × 4 R), Run-IDs je Ausgabeordner eindeutig, Schrittzahlen passen zum Lader, SGD-Teil liefert wie gewollt „nicht auswertbar“. Kleinigkeiten: Die Zahl „144 Läufe“ oben gilt mit SGD-Arm; nach `SGD_DROPPED` sind es **128**. **Laufzeitregel (vor dem Block):** 96 Minibatch-Läufe + 16 fb30k à 30 000 Schritte, 16 fb à 2000; gemessen ≈ 0.008 s/Schritt bei 10 GPU-Prozessen → ≈ 4–5 min je 30 000-Schritt-Lauf, bei 5–10 Workern ≈ 1–1.5 h < 3 h → Budget bleibt 30 000. Ausführung: `jobs.txt` in zwei Hälften (`jobs_part1.txt` Zeilen 1–64 sofort mit 5 Workern, `jobs_part2.txt` Zeilen 65–128 mit 5 Workern nach der B = 16-Sonde); gleiche Zeilen, nur aufgeteilt.

## Ergebnis Pilotblock (Sitzung 46, 2026-09-29, 02:07 Berlin; Exploration, 8 Seeds 3700–3707)

128/128 Läufe ohne Fehler (Logs `lab/runner/logs/pq_*` der Teile 1/2), `analyze.py` (Lesarten aus dem Docstring, vorab): 8/8 Seeds gültig.
- **K2-MB: „Menge steuert unter Minibatch“.** Δ_pow am Ende (30 000 Schritte): iid256 **9.60 [8.98, 10.21]**, iid64 **9.85 [9.00, 10.73]**; Full-Batch-Referenzen fb (2000 Schritte) 8.36 [7.67, 9.01], fb30k (30 000) 10.28 [9.24, 11.21]; stride256 9.90 [9.26, 10.50]. Bei 2000 Schritten fb 8.36 ≥ iid256 8.05 ≥ iid64 7.29 → vorab festgelegter Zusatz „schwächer bei B = 64 (Verdünnung im Festlegungsfenster)“ gilt, am Ende aber nicht mehr.
- **Konflikt: „nicht prüfbar (Reihenfolge wirkt nicht)“** bei B = 256 und bei B = 64 (`Konflikt_B64`): stride-Spitze in O 0/16 bzw. 0/16; KI von o(stride) − o(iid) auf F/G [−0.003, 0.015] bzw. [−0.000, 0.011]; Δ_pow(stride) − Δ_pow(iid) +0.30 [−0.39, 0.90] bzw. +0.04 [−0.77, 0.86].
- **Reihenfolge allein (R): „unklar“** bei beiden B: keine Spitze in O (0/8; B 64: 1/8), das KI von o(R-stride) − o(R-iid) liegt aber ganz **unter** 0 ([−0.23, −0.03]; B 64 [−0.36, −0.06]) — getrieben von einzelnen i.i.d.-Läufen mit viel Energie auf O (z. B. Seed 3700 bei B 64 in der Machbarkeit 0.36); keine Deutung.
- **SGD:** „nicht auswertbar“ (Kalibrierung ohne Treffer).
- **Beschreibend:** generalisiert fb/fb30k/iid256/stride256 16/16, iid64 13/16. R5 unter Minibatch: Median t_gen in Epochen E (iid256) 77 gegen R 333 (≈ ×4.3 schneller, wie R5 Full-Batch-Richtung).
- **Abgleich mit der ersten Ordnung (vorab):** B 256 ausgewaschen ✓; B 64 „an der Kante“ → im Piloten keine Wirkung.
- **Power für L0 (`lab/confirm/L0_power_s46.py`, Normalmodell, halber Effekt, 1.5-fache SD, Holm k = 3):** H1/H2 schon bei n = 6 Power ≈ 1 → Regel n = 10 (Mindestzahl nach Regel 15b). H3 aus diesem Piloten entfällt (Konflikt nicht prüfbar); ein H3 kann nur aus [[experiments/EXP-106-l0-b16-long-epochs/README|EXP-106]] (B = 16, wd 0.1) kommen.
Unabhängige Nachrechnung läuft. Offen: Wechselläufe `switch.txt` (laufen), `switch_analyze.py`.

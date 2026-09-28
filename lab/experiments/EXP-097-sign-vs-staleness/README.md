---
id: EXP-097
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-097: Veralteter Gradient oder Vorzeichenschritt? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage nach EXP-095: Warum braucht die frühe Festlegung frische Gradienten?) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-095-gradient-feedback/README|EXP-095]] (Nachtrag b) · Bestätigung [[confirm/R10_REGISTRATION_DRAFT|R10]]

**Festgelegt vor jedem EXP-097-Lauf** (Sitzung 43, 2026-09-28, Fenster zu; `design.py`, `analyze.py`, Trainer-Patch `trainer_psu.patch`; alles ungetestet bis 29.09. 00:00).

## Bezug und Frage

EXP-095: Mit nur dem Anfangsgradienten (g24) legt das Modell bis Λ = 24 schwach fest (e24 = +0.187). Daraus hatten wir geschlossen, die erste Ordnung trage nur einen kleinen Teil der Festlegung. **Nachtrag b (Sitzung 43, post hoc):** Mit eingefrorenem Gradienten sind Adams Momente exakt m̂ = g₀, v̂ = g₀², jeder Schritt ist also lr · sign(g₀) je Element (gemessen: 99.9 % der W_E-Einträge). Binarisiert man die normale n24-Bewegung, entstehen schon 56 % [53, 59] der Selektivitätslücke. Das Ergebnis von g24 ist deshalb zwischen zwei Erklärungen verwechselt: **(V) Veraltung:** Der Anfangsgradient zeigt in die falsche Richtung, frische Gradienten sind nötig. **(Q) Vorzeichen-Quantisierung:** Adam macht aus einem festen Gradienten elementweise gleich große Schritte und streut so Energie auf Nicht-Ziele. Dieselbe Richtung, linear gegangen, könnte ausreichen.

**Eingriff (2 × 2 vor dem Wechsel):** {Adam, linear normierte Schritte} × {frischer Gradient in jedem Schritt, nur Anfangsgradient}. Linear heißt: W ← W(1 − lr·wd) − lr · g / rms(g) je Tensor; bei W_E werden die p Token-Zeilen als ein Block normiert, getrennt von der „=“-Zeile (sonst würde deren Gradient, der in jedem Beispiel steckt, die Normierung beherrschen und die Token-Zeilen kaum bewegen; Prüfung Sitzung 43). Die Schrittgröße (RMS lr über die Token-Zeilen) ist gleich der eines Vorzeichenschritts, die Richtung aber exakt g (linear entlang der Token-Achse, also ohne Frequenz-Streuung durch die Normierung). Adams Momente und Schrittzähler laufen dabei im Schatten mit denselben Gradienten weiter. Nach dem Wechsel setzt AdamW deshalb mit einem Zustand fort, der wie im Adam-Arm aufgebaut ist. So bleibt der EXP-057-Boden aus: ein leerer Adam-Zustand beim Wechsel senkt π von 0.30 auf 0.11. L24 und g24 haben beim Wechsel exakt denselben Adam-Zustand (m = g₀, v = g₀², Zähler 24) und unterscheiden sich nur im Weg der Gewichte.

## Aufbau

Wie EXP-095 (add 113, ω = 0-Splitpaare nach EXP-053, Wechsel A → B und B → A bei t = 24, danach 2000 Standardschritte, π gegen reine Läufe; GPU). **Seeds 3600–3615** (frisch; Dateisuche 28.09. ohne Treffer). Zellen: **n24** (Adam, frisch; Referenz), **g24** (Adam, nur Anfangsgradient; Replikation von EXP-095), **L1** (linear, frisch), **L24** (linear, nur Anfangsgradient). 10 Läufe je Seed, **160 GPU-Läufe** (≈ 15 min mit 8 Workern wie EXP-095).

## Vorhersagen und Lesarten (verbindlich, im Code; Fassung 2 nach der statischen Prüfung, Sitzung 43, vor jedem Lauf)

eA = π(n24) − π(g24), **sA = π(L24) − π(g24)**, eL = π(L1) − π(L24); gepaarte Bootstrap-KIs über Seeds (10 000, rng 97). Zwei Fragen, beide Exploration (keine Holm-Korrektur, keine Kernaussage):

**Q1 (primär): Wie viel von eA ist Vorzeichen-Quantisierung des Gewichtswegs?** L24 und g24 haben denselben Anfangsgradienten und beim Wechsel exakt denselben Adam-Zustand; sie unterscheiden sich nur darin, ob W vor dem Wechsel linear oder in Vorzeichenschritten gegangen ist. Reihenfolge:
- **„nicht trennbar“:** KI-Untergrenze von eA ≤ 0.03 (EXP-095 repliziert nicht).
- **„Quantisierung erklärt“:** KI-Untergrenze von sA > 0.03 und mittleres sA ≥ 0.5 · mittleres eA.
- **„Quantisierung teilweise“:** KI-Untergrenze von sA > 0.03, mittleres sA < 0.5 · eA.
- **„Quantisierung nicht“:** KI von sA innerhalb ±0.05.
- sonst **„unklar“**.

**Q2: Braucht die Festlegung frische Gradienten auch bei linearem Gewichtsweg?** Reihenfolge nach „nicht trennbar“:
- **„Boden“:** mittleres π(L1) < 0.5 · mittleres π(n24) (der frische lineare Arm legt deutlich schwächer fest; eL nicht vergleichbar).
- **„Veraltung zählt“:** KI-Untergrenze von eL > 0.03 und relativer Rückstand eL/π(L1) ≥ 0.5 · eA/π(n24).
- **„Veraltung teilweise“:** KI-Untergrenze von eL > 0.03, relativer Rückstand kleiner.
- **„erste Ordnung genügt“:** KI von eL innerhalb ±0.05.
- **„erste Ordnung besser“:** KI-Obergrenze von eL < −0.03.
- sonst **„unklar“**. < 10 gültige Seeds → beide *nicht auswertbar*.

**Vorbehalt Q2 (Prüfung Sitzung 43):** Nach dem Wechsel trägt L24 dieselbe Adam-Vorgeschichte wie g24 (m = 0.92 · g₀, v = 0.38 · g₀²). Die ersten Schritte danach sind deshalb noch zum Teil Vorzeichenschritte entlang g₀, bei L1 dagegen Schritte aus der eigenen frischen Vorgeschichte. eL enthält also noch einen Rest Quantisierung und ist eine **Obergrenze** für reine Veraltung (Verzerrung Richtung „Veraltung zählt“).
- **Beschreibend:** π(L1) − π(n24); Zellmittel von π, Zielanteil f und Norm N beim Wechsel; Anteil q der Vorzeichenschritte unter den W_E-Einträgen (Erwartung: g24 ≈ 1, L24 und L1 klein).
- **Erwartung (vorab):** Q1 „Quantisierung teilweise“ bis „erklärt“ (Nachtrag b: 56 % der f-Lücke; π ist aber nicht linear in f, und sign(D_n24) ist nur ein Ersatz). Q2 „Veraltung teilweise“. Gegen die Veraltungs-Deutung von EXP-095 spräche Q1 „erklärt“ zusammen mit Q2 „erste Ordnung genügt“. Dann wäre die schwache Festlegung mit nur dem Anfangsgradienten ein Adam-Artefakt.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-095 (Zellmittel, Nachtrag a und b, alle gesehen), EXP-057 (Boden bei leerem Adam-Zustand → Schattenzustand), EXP-092/093/094. Keine Seeds aus diesen Blöcken. Die Schwelle 0.5 · eA und die Werte HI = 0.03 / EQ = 0.05 sind aus EXP-095 übernommen. Der Schattenzustand folgt aus EXP-057 (leerer Adam-Zustand beim Wechsel: π 0.30 → 0.11). Fassung 2 (vor jedem Lauf, nach der statischen Prüfung durch einen Claude-Agenten): W_E-Blocknormierung, Q1 mit sA als primärem Kontrast, relativer statt absoluter Boden, Vorbehalt zum Momentum-Schwanz, schärferer Trainer-Test (RMS des ersten Schritts, Adam-Moment protokolliert).

## Reihenfolge und Befehle (ab 00:00; erst NACH den Auswertungen von R10 und R11 und nach dem EXP-096-Block, weil R10/R11 den Trainer-Hash binden)

```
git apply lab/experiments/EXP-097-sign-vs-staleness/trainer_psu.patch      # erst nach confirm_r10.py --analyze
python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py   # alle 9 Tests grün (neu: pre_switch_update)
git add lab/experiments/EXP-001-freq-ban/freq_ban.py lab/tests/test_freq_ban_fingerprint.py; git commit
python lab/tools/guarded_run.py -- python lab/experiments/EXP-097-sign-vs-staleness/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-097-sign-vs-staleness/smoke.txt --workers 3
python lab/tools/guarded_run.py -- python lab/experiments/EXP-097-sign-vs-staleness/analyze.py --smoke-check
python lab/tools/parallel_queue.py lab/experiments/EXP-097-sign-vs-staleness/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-097-sign-vs-staleness/analyze.py
```
Splits, `jobs.txt` und `smoke.txt` sind schon erzeugt (`design.py`, reines numpy, Sitzung 43). Scheitert der Trainer-Test: EXP-097 nicht starten, Fehler im JOURNAL. Laufen R10-Reste noch, den Patch NICHT anwenden (R10 würde jeden weiteren Lauf und `--analyze` verweigern).

## Ergebnis

*(noch nicht ausgeführt)*

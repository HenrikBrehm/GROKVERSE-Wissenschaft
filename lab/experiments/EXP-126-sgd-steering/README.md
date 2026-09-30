---
id: EXP-126
status: abgeschlossen
datum: 2026-09-30
tags: [exp/abgeschlossen, befund/unklar]
---
# EXP-126: Ist die Split-Steuerung (K2) ein Adam-Artefakt? Full-Batch-SGD mit Momentum

Zurück: [[LAB]] · [[FINDINGS]] · Vorlage/Splits [[experiments/EXP-100-set-vs-order/README|EXP-100]] (L0-Pilot) · [[JOURNAL]] Sitzung 57

**Bezug zu FINDINGS:** Geltungsbereich von K2 (Programm A, Regel 15c/19a); Paper §7 (i): alle Aussagen mit AdamW, der SGD-Arm von L0 war „nicht auswertbar“ (unter Minibatch B 256 lernte lr 0.03 nicht, ≥ 0.1 divergierte meist). Exploration (4 Seeds), keine Bestätigung.

## Vorab (Sitzung 57, 2026-09-30, vor jedem Lauf)

- **Frage:** Steuert die Auswahl der Trainingspaare die gelernten Frequenzen auch ohne Adam, mit Full-Batch-SGD und Momentum?
- **Gesehene Daten, die die Frage angeregt haben (beschreibend, kein Beleg):** In den L0-Kalibrierungsläufen (B 256, nur Split F) lernte Seed 3701 bei lr 0.1 und generalisierte; am Ende lagen **0.968** der W_E-Energie auf den 5 Zielfrequenzen von F (Gleichverteilung 0.09). Seed 3700 bei lr 0.1 erreichte 0.686, bevor der Lauf divergierte. Ohne G-Gegenarm ist das kein Δ_pow.
- **Hypothese:** K2 ist kein Adam-Artefakt (die Theorie erster Ordnung, Anhang G, hängt am Gradienten, nicht am Optimierer): Δ_pow > 1, wenn SGD lernt.
- **Aufbau:** unveränderter Trainer `freq_ban.py` (`--optimizer sgdm`, Momentum 0.9, Weight Decay entkoppelt und auf AdamWs lr·wd = 10⁻³ je Schritt abgeglichen, wie L0), Full-Batch, lr **0.05** und **0.1**, EXP-100-Splits F/G mit gemeinsamer Init und Testmenge je Seed, **Seeds 3704–3707** (im L0-Pilot mit AdamW/Minibatch benutzt, nie mit SGD), 20 000 Schritte ohne vorzeitigen Stopp, Spektren bei 50, 250, 2000 und alle 2500 Schritte. 16 Läufe, GPU.
- **Messgrößen und Lesarten (`analyze.py`, vor dem Lauf geschrieben):** je lr: Lauf „divergiert“ (Spektrum bei 20 000 nicht endlich), „nicht gelernt“ (Train < 0.99), sonst ok; Seed auswertbar, wenn F und G ok. Δ_pow bei 20 000 (P1-Definition). **„K2 ohne Adam“**: ≥ 3 auswertbare Seeds und Δ_pow > 1 in allen; **„bricht“**: ≥ 3 auswertbar und |Δ_pow| ≤ 1 in allen; **„nicht auswertbar“**: < 3 auswertbar; sonst „unklar“. Beschreibend: Δ_pow bei 2000, Divergenzen, Generalisierung, Testgenauigkeit.
- **Was gegen die Hypothese spräche:** SGD lernt (Train ≥ 0.99), aber |Δ_pow| ≤ 1 → die Steuerung braucht Adams koordinatenweise Normierung (Befund für §7 i und für N49 „Koordinatenbasis von Adam“).
- **Budget/Abbruch:** ≈ 0.04–0.065 s/Schritt unter Last → 13–22 min je Lauf; 16 Läufe bei 4 Workern ≈ 1–1.5 h; harte Grenze 120 min je Lauf. Divergenz beendet nichts (Lauf zählt als „divergiert“).
- **Priorität:** als `43z_exp126_sgd` vor R12 eingereiht (kurz; R12 verzögert sich dadurch um ≈ 1 h, ist ohnehin ≈ 10 h lang).

## Deutung je Ausgang (vor dem Ergebnis festgelegt, 06:37 gemessen)

Ort im Paper: nur als Exploration, ein Satz in §7 (i) *Regime* und im Anhang J (L0, SGD-Arm). Kein Kernsatz.
- **„K2 ohne Adam“ (bei mindestens einer lr):** *In a pilot with full-batch SGD with momentum (4 seeds, exploration), engineered splits steered the learned frequencies as with AdamW (Δ_pow … to …), so the steering is not specific to Adam's per-coordinate normalization.* Die Festlegung (Result 3) bleibt ausdrücklich AdamW-gebunden (R9/K5 hängen an Adams Fenstern).
- **„bricht“:** *With full-batch SGD with momentum the runs learned the training set but the engineered splits did not steer the frequencies (|Δ_pow| ≤ 1 in all evaluable seeds; pilot); the steering may depend on Adam.* Dann als Grenze in §7 (i) und Kandidat für eine Bestätigung.
- **„unklar“:** nur Zahlen, keine Richtung behaupten.
- **„nicht auswertbar“ (lernt nicht / divergiert):** *SGD with momentum did not train reliably in this setting (…/8 runs learned), so we could not test the steering without Adam.* Wie beim L0-Arm.
- Verschiedene Ausgänge bei 0.05 und 0.1: beide berichten, keine Auswahl der günstigeren lr.

## Befehle

```
python lab/experiments/EXP-126-sgd-steering/make_jobs.py > lab/queue/staging/43z_exp126_sgd.jobs && mv lab/queue/staging/43z_exp126_sgd.jobs lab/queue/inbox/
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-126-sgd-steering/analyze.py
```

## Ergebnis (Sitzung 57, 07:58 gemessen; 12/16 Läufe fertig, 3706/3707 bei lr 0.1 laufen noch – sie können die Lesart nicht mehr ändern)

Befehl: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-126-sgd-steering/analyze.py` → `summary.json`.

- **Vorab-Lesart: „nicht auswertbar“ bei beiden Lernraten.** lr 0.05: 8/8 Läufe lernen nichts (Train ≈ 0.012 nach 20 000 Schritten). lr 0.1: 4/4 fertige Läufe divergieren (erste nicht endliche Spektren bei 1250, 1250, 1500 und 14 750 Schritten); selbst wenn 3706 und 3707 beide lernen, bleiben höchstens 2 < 3 auswertbare Seeds.
- **Korrektur an der Auswertung vor der endgültigen Lesart (dokumentiert):** Der Trainer setzt bei nicht endlichen Spektren nicht „completed“, sondern bleibt auf „finalizing“ (Artefaktprüfung, Exit 1). `analyze.py` zählte solche Läufe zuerst als „fehlt“ und ordnet sie jetzt, wie vorab definiert, als „divergiert“ ein (volle Schrittzahl, Spektrum bei 20 000 nicht endlich). Die Lesart ändert sich dadurch nicht.
- **Beschreibend (ein Lauf, kein Δ_pow, gesehen):** 3704 G bei lr 0.1 lernte (Train ≥ 0.99 ab 1150), generalisierte (Test ≥ 0.95 ab 1175) und hatte 0.84 (Schritt 2000) bzw. 0.92 (5000–12 500) der W_E-Energie auf den eigenen Zielen, 0.004–0.011 auf den Zielen von F; bei 14 750 divergierte er. Zusammen mit dem L0-Kalibrierungslauf 3701 F (B 256, lr 0.1: 0.968 auf den eigenen Zielen) heißt das: **Wenn SGD mit Momentum hier überhaupt trainiert, folgen die gelernten Frequenzen der Datenauswahl** – als Beobachtung an 2 Einzelläufen, nicht als Test.
- **Deutung:** Die Frage „Adam-Artefakt?“ ist mit diesem Aufbau nicht beantwortbar, weil SGD mit Momentum ohne Stabilisierung zwischen „lernt nicht“ (0.05) und „divergiert“ (0.1) kein brauchbares Fenster hat. Paper: Satz nach der Vorab-Deutung „nicht auswertbar“ (§7 i / Anhang J), die beiden Einzelläufe höchstens als Beobachtung.
- **Nächster Schritt (vorgemerkt, nicht gestartet):** SGD stabilisieren (Gradienten-Clipping oder Warmup im SGD-Pfad, oder lr 0.07). Das braucht eine Trainer-Änderung; `freq_ban.py` ist bis zur R12-Auswertung per Hash gebunden → Patch erst danach, dann eigener Versuch mit Vorab-Lesart.

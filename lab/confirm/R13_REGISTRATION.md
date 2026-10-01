---
id: R13
status: entwurf
datum: 2026-10-01
tags: [lab/confirm, programm/A, paper, exp/vorbereitet]
---
# R13: Steuert die Trainingsmenge das W_E-Spektrum auch ohne Adam – unter Full-Batch-SGD mit Momentum und Gradient-Clipping? (Registrierung, Sitzung 67)

Zurück: [[LAB]] · [[FINDINGS]] · Vorlagen: [[confirm/P1_REGISTRATION_DRAFT|P1]] (K2), [[confirm/P4_REGISTRATION_DRAFT|P4]] (Steuerung ohne Generalisierung bei Integer-Addition) · Piloten: [[experiments/EXP-126-sgd-steering/README|EXP-126]], [[experiments/EXP-128-sgd-clip/README|EXP-128]] · [[JOURNAL]] Sitzung 67.

Geschrieben 2026-10-01 ab 06:10 Berlin (gemessen), **vor jedem R13-Blocklauf**. Code: `lab/tools/confirm_r13.py` (Selbsttest grün 06:09, über den Wächter; Smoke außerhalb des Blocks siehe unten).

## Warum (Bezug zu FINDINGS / Paper)

Grenze (i) des Papers: „all results are AdamW results“. Der naheliegende Gutachter-Einwand: Ist die Datensteuerung (K2) eine Eigenheit von Adams koordinatenweiser Normierung? EXP-126 (SGDm ohne Clipping) und EXP-128 (SGDm mit Clipping) waren nach ihrer Vorab-Regel „nicht auswertbar“, weil die Regel eine Anpassung an die Trainingsmenge verlangte. **Post hoc** (nach der EXP-128-Textprüfung, gesehene Seeds 3704–3707) war Δ_pow bei Schritt 2000 aber in jedem Seed groß: 7.19–7.62 (Clip 0.1) und 3.95–4.52 (Clip 0.017), meist ohne Anpassung. R13 prüft diese **Repräsentationsaussage** an frischen Seeds und Splits – wie P4 bei Integer-Addition („Steuerung des W_E-Spektrums ohne Generalisierung“), nicht als Aussage über einen gelernten Algorithmus.

## Aufbau (gilt; Einzelheiten im Docstring von `confirm_r13.py`)

- **Trainer:** `lab/experiments/EXP-128-sgd-clip/freq_ban_sgdclip.py` (Kopie von `freq_ban.py` @267fde1e + Clipping-Patch, wie EXP-128; Hash im Manifest gebunden). 1-Schicht-Transformer, add 113, Full-Batch, `--optimizer sgdm --sgd-lr 0.1 --sgd-momentum 0.9`, Weight Decay entkoppelt wie EXP-126/128, GPU, `--threads 1`, **genau 2000 Schritte** (`--stop-after-gen 100000`), Spektren bei 250 und 2000. Test = Komplement.
- **Bedingungen (Holm über 2):** **c01** `--sgd-clip 0.1`, **c0017** `--sgd-clip 0.017` (Werte aus EXP-128 übernommen, dort vor jedem Pilotlauf festgelegt).
- **Einheit:** Seed mit F/G-Paar (gleiche Init für F und G, wie P1/P4). Splits: P1-Konstruktion (`confirm_splits.build`, ε = 2, 30 %, Ziele F/G disjunkt je 5 aus k = 1..56) mit **Versuchs-ID 13** (eigene Zufallsströme `SeedSequence([1000001, 13, add, 113, Seed, Arm, Zweck])`, nie aus dem Init-Seed abgeleitet).
- **Seeds (frisch, reserviert, disjunkt):** c01 4400–4414, c0017 4415–4429 (n = 15 je Bedingung). Nirgends im Labor verwendet (geprüft: keine Laufverzeichnisse, keine Manifeste mit 44xx).
- **Primär je Bedingung:** Δ_pow (Formel wie P1: log-Verhältnis der W_E-Leistung auf eigenen gegen fremde Ziele, über F- und G-Lauf summiert; additive DFT aus `spectra.npy`, k = 1..56) bei Schritt 2000; exakter einseitiger Vorzeichen-Flip-Test (n = 15, 2¹⁵ Muster), Holm über 2 bei 0.05, 95-%-Bootstrap-KI. **„bestätigt“:** alle 15 Paare gültig, Holm-p < 0.05 **und** KI-Untergrenze ≥ 1 (Mindesteffekt wie P1/P4).
- **Gültigkeit:** ein fehlender oder defekter Lauf, Bindungs-/Hashverletzung (Split-Bytes, Code), abweichende Optimierereinstellungen (Optimierer, lr, Momentum, Clip-Wert in `events.sgd_clip`), nicht endliches Spektrum → Bedingung „nicht auswertbar“ (p = 1 in der Familie). Läufe nur über `confirm_r13.py --run` (Bindung an Manifest und Code).
- **Beschreibend (kein Urteil):** Δ_pow bei 250; Train-/Testgenauigkeit am Ende; Zahl der Arme mit Train ≥ 0.99; Generalisierungsschritt; Anteil gekappter Schritte; nicht endliche protokollierte Gradientennormen.

## Stichprobengröße

n = 15 je Bedingung wie P4. Pilotstreuung (EXP-128, gesehen, 4 Seeds): c01 Mittel 7.40, SD ≈ 0.18; c0017 Mittel 4.20, SD ≈ 0.28. Selbst bei halbem Effekt und fünffacher SD liegt die erwartete KI-Untergrenze weit über 1; das Vorzeichen-Kriterium erreicht bei 15/15 positiven p = 2⁻¹⁵. Die Power ist damit praktisch 1 für den Pilot-Effekt; ein Pilot aus 4 Seeds kann den Effekt aber überschätzen (Gedächtnisnotiz „power from small pilots“) – deshalb kein Schluss aus der Power, nur das Urteil.

## Was dagegen spräche

- „nicht bestätigt“ in c01: Die Steuerung des Spektrums unter geclipptem SGDm ist nicht robust über frische Seeds/Splits; Grenze (i) bleibt unverändert.
- c01 bestätigt, c0017 nicht: hängt vom Clipping-Regime ab (stark gekapptes = fast normiertes SGDm verhält sich anders) – so berichten.
- Beide bestätigt: Die Repräsentationsseite von K2 ist nicht an Adam gebunden (in diesem Aufbau, bei Schritt 2000, ohne Aussage über gelernte Lösungen, da die meisten SGD-Läufe die Trainingsmenge in 2000 Schritten nicht anpassen).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- EXP-126 (Seeds 3704–3707, SGDm ohne Clipping; lr 0.05 lernt nichts, lr 0.1 divergiert) und EXP-128 (gleiche Seeds, Clip 0.017/0.1, 20 000 Schritte, alle Ergebnisse gelesen, inkl. post hoc Δ_pow bei 50/250/2000/5000/20 000 und W_E-Energieanteile auf eigenen Zielen 0.73–0.998). **Beeinflusst:** die ganze Frage, Wahl des Messschritts 2000 (dort im Pilot schon groß, vor der Divergenzzone von EXP-126 bei 1000–1500 – die mit Clipping in EXP-128 nicht auftrat), beide Clip-Werte, n.
- Smoke (06:06–06:09, außerhalb des Blocks, Seed 4399 nicht reserviert, R13-Konstruktion, c01, 2000 Schritte, `lab/confirm/r13_smoke/`): fand einen Fehler in der Run-ID-Regel (Präfix EXP-016 statt EXP-018 ohne Testdatei; korrigiert vor dem Einfrieren); Lader liest, Optimiererfelder stimmen, Train 0.45 / Test 0.22 bei 2000. Δ_pow wurde nicht berechnet (nur ein Arm).
- P1/P4/R7 (K2 unter AdamW) – das Design ist von dort übernommen.

## Grenzen (vorab)

Eine Architektur, eine Aufgabe (add 113), eine Lernrate (0.1) mit Momentum 0.9, zwei Clip-Werte, ε = 2, 30 % Daten; Messung nur bei Schritt 2000 und nur Einbettungsenergie (keine Ablation, keine Aussage über eine gelernte Lösung); Full-Batch. Keine Aussage über SGD ohne Clipping oder über Minibatch-SGD.

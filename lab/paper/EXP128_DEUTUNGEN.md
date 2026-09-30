---
id: paper-EXP128-deutungen
status: vorbereitet
datum: 2026-09-30
tags: [lab/paper]
verwandt: ["[[paper/draft_short]]", "[[experiments/EXP-128-sgd-clip/README|EXP-128]]", "[[experiments/EXP-126-sgd-steering/README|EXP-126]]"]
---
# EXP-128: Paper-Sätze je Ausgang, vor jedem Pilotlauf festgelegt (Sitzung 59, 2026-09-30)

Zurück: [[paper/STATUS]] · Versuch [[experiments/EXP-128-sgd-clip/README|EXP-128]] · Lesart maschinell in `lab/experiments/EXP-128-sgd-clip/analyze.py`.
Zweck wie [[paper/R12_DEUTUNGEN]]: Die Deutung jedes Ausgangs steht fest, bevor ein Pilotlauf gerechnet ist. **Stand beim Schreiben:** gesehen sind nur der Kalibrierlauf (C = 10⁶) und zwei Smokes (C_A 3000, C_B 2500 Schritte, Seed 3704 F, beide „nicht gelernt“, keine Divergenz). Der Pilot nutzt gesehene Seeds (3704–3707) → **jeder Ausgang ist Exploration**; kein Ausgang wird Kernaussage, alle Sätze gehen nur in §7 (i) (Limitations) und ggf. Anhang J.

**Ort:** §7 (i), Satz „An exploratory attempt to test the steering without Adam … all results are AdamW results.“ Der EXP-126-Satz bleibt; der passende Satz unten wird direkt danach angefügt. Zahlen einsetzen: auswertbare Seeds, Δ_pow bei 20 000 (Spanne), Anteil gekappter Schritte.

## Arm C_B (0.1, kappt nur Spitzen; fast gewöhnliches SGD mit Momentum) – maßgeblich

- **„K2 ohne Adam“:** *With gradient-norm clipping at 0.1 (a value three times the largest sampled pre-divergence norm, so most steps are ordinary momentum SGD; … % of steps clipped), SGD with momentum trained on … of 4 seeds and the engineered splits steered the learned frequencies (Δ_pow … to … at 20 000 steps, all > 1; exploration on seen seeds, EXP-128). The steering is therefore not specific to Adam's per-coordinate normalization in this setting; a confirmation on fresh seeds has not been run.* → danach Bestätigungsblock registrieren (frische Seeds, ≥ 10, Leistung aus der Pilotstreuung).
- **„bricht“:** *With gradient-norm clipping at 0.1, SGD with momentum fitted the training set on … of 4 seeds but the engineered splits did not steer the learned frequencies (|Δ_pow| ≤ 1 in all; exploration, EXP-128). In this setting the steering may depend on Adam's per-coordinate normalization; we therefore restrict all claims to AdamW.* → Befund für N49 („Koordinatenbasis von Adam“); Paper sagt das so, ohne Mechanismus.
- **„unklar“:** *With clipping at 0.1, SGD with momentum gave mixed results (Δ_pow … to …, … evaluable seeds; exploration, EXP-128); we draw no conclusion about optimizers other than AdamW.*
- **„nicht auswertbar“:** *Stabilising SGD with gradient-norm clipping (0.1 and 0.017) did not make it evaluable either (… of 4 seeds fitted the training set within 20 000 steps; EXP-128).* – zusammen mit dem Satz zu C_A, wenn auch dieser „nicht auswertbar“ ist.

## Arm C_A (0.017, kappt fast jeden Schritt; praktisch normiertes SGD mit Momentum) – nachrangig

- **„K2 ohne Adam“:** nur als Halbsatz: *…; with clipping at 0.017, where almost every step is clipped (normalised momentum SGD), the splits steered as well (Δ_pow … to …).* Nicht als „ohne Adam“ verallgemeinern, falls C_B nicht ebenfalls so ausgeht (normiertes SGD ist nicht Standard-SGD).
- **„bricht“:** *With clipping at 0.017 (normalised momentum SGD) the splits did not steer (|Δ_pow| ≤ 1).* Steht C_B auf „K2 ohne Adam“, heißt der Kontrast: die Steuerung hängt an der Schrittlänge bzw. am Regime, nicht an Adam – so beschreibend berichten, keine Ursache behaupten.
- **„unklar“ / „nicht auswertbar“:** kein eigener Satz (höchstens „… and at 0.017 it did not fit the training set within 20 000 steps“ im Satz zu C_B).

## Was in keinem Fall geschrieben wird

- Keine Aussage über SGD ohne Clipping, über andere Lernraten oder über Minibatch-SGD.
- Keine Aussage, dass K2 „optimiererunabhängig“ ist; höchstens „not specific to Adam in this setting“.
- Das Paper bleibt bei „all confirmed results are AdamW results“, solange kein Bestätigungsblock gerechnet ist.

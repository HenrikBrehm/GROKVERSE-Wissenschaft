---
id: EXP139_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# EXP-139 (Paarzahl statt Anteil, p 401/503/613): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[experiments/EXP-139-pair-count/README|EXP-139]] · [[paper/R14_DEUTUNGEN]]

**Geschrieben in Sitzung 68 (01.10.2026, ≈ 08:41 Berlin), bevor ein EXP-139-Lauf fertig war** (4 von 36 laufen, Schritt ≈ 6000, gelesen nur Schritt/Tempo). Ort: Anhang A.2 ein Absatz nach R14; Grenze (ii) nur ein Halbsatz („nothing was tested near LeDoux's 0.3 %“ wird präzisiert). **Pilot (3 Seeds je Zelle), keine Bestätigung, kein Abstract.** Zahlen nach `analyze.py`, unabhängige Nachrechnung und Textprüfung.

## Anhang A.2, je Ausgang (Frage 2 zuerst, Frage 1 als Nebensatz)

- **„K2 hält bis zum kleinsten generalisierenden Anteil“:** *A further pilot with a fixed number of training pairs (EXP-139; 9425 or 14 000 pairs at moduli 401, 503 and 613, i.e. 2.5–8.7 % data; three seeds per cell) found steering after generalization in every cell that generalized, down to … % data (Δ_pow …–…, every seed above its 99 % placebo quantile …–…); [Frage-1-Satz].*
- **„Steuerung schwindet bei kleinem Anteil“:** *… in the cells with … % data the steering after generalization was not distinguishable from placebo frequency sets (Δ_pow …, placebo 90 % quantile …), whereas at … % it held; so the steering found at 10 % may weaken at lower data fractions.*
- **„kein Lernen im Budget“:** *… no cell generalized within 30 000 steps, so the pilot says nothing about steering below 10 % data.*
- **„beschreibend“:** *… gave mixed results (…).* + Zahlen.

Frage-1-Satz: „Paarzahl trägt“ → *with 9425 pairs every modulus up to 613 generalized (2.5 % data), so the data limit seen at mod 211 (EXP-137) reflects the number of pairs rather than the fraction;* „Grenze …“ → *with 9425 pairs the networks generalized at … but not at … (within 30 000 steps); at equal fraction (3.73 %) …;* „reicht nicht“ → *with 9425 pairs no modulus above 307 generalized within 30 000 steps.*

## Grenze (ii), nur falls Frage 2 „hält“ oder „schwindet“

*…; a pilot reached … % data (EXP-139); nothing was tested near LeDoux's 0.3 %;*

## Was ausdrücklich nicht gesagt wird

- nichts über p = 9973 oder 0.3 %; „Paarzahl statt Anteil“ höchstens für den getesteten Bereich und das Budget von 30 000 Schritten;
- keine Bestätigung (3 Seeds, additive Salze); Einbettungsenergie, keine Ablation; Messpunkt je Arm verschieden.

---
id: EXP125_DEUTUNGEN
datum: 2026-09-30
tags: [lab/paper]
---
# EXP-125 (≈ 2× größeres Sprachmodell): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[LAB]] · [[experiments/EXP-125-lm-size/README|EXP-125]] · Vorlage [[paper/LM1_DEUTUNGEN]] · [[paper/PYTHIA_DEUTUNGEN]]

**Geschrieben in Sitzung 63 (30.09., 21:16 Berlin gemessen), bevor ein EXP-125-Lauf gestartet war** (Dienst: `45_exp125_lm_size` wartet hinter EXP-132/EXP-133). Bekannt waren LM1/LM1-F und LM3/LM3-F (≈ 14 M Parameter, bestätigt) und die Pythia-Reihe (vortrainiert, nicht gesteuert). EXP-125 ist eine **Exploration mit 2 Seeds**: höchstens ein Satz in Anhang K (Manuskript: Appendix J, „Towards language models“) und ein Halbsatz in Grenze (ii). **Kein Abstract, keine neue Kernaussage.** Zahlen werden nach `analyze.py` eingesetzt und unabhängig geprüft. Die Lesarten und ihre Regeln stehen unverändert im EXP-125-README (vorab, Sitzung 57).

## Satz in Anhang K (nach dem LM1/LM3-Absatz), je Lesart

- **„K2 haelt im LM“:** *In a pilot with a model about twice as large (≈ 29.5 M parameters: width 512, 8 layers, 8 heads; LM1 setting otherwise unchanged, including the learning rate; two seeds, exploration), the fact selection again steered the tied number embeddings (Δ_pow … and …) and the models generalized to held-out facts (…–…).*
- **„nur Repraesentation“:** *… the fact selection steered the tied number embeddings (Δ_pow … and …), but the models did not generalize to held-out facts within 6000 steps (…–…); steering of the representation therefore did not require generalization in this pilot.*
- **„bricht“:** *… the models learned the facts (held-out accuracy …–…) but the fact selection did not steer the number embeddings (Δ_pow … and …; pre-set threshold 1). In this pilot the steering did not carry over to a model twice as large at an unchanged learning rate.*
- **„unklar“:** *… gave mixed results (Δ_pow … and …; held-out accuracy …–…).*
- **„nicht gelernt (Budget)“:** *… did not learn the training facts within 6000 steps at the unchanged learning rate, so this pilot says nothing about steering at that size.*

## Grenze (ii), Halbsatz (Ende des Satzes „Steering also held in one small language-model architecture …“)

- bei „K2 haelt“ / „nur Repraesentation“: *…; a pilot with a twice larger model (two seeds) pointed the same way (Appendix K).*
- bei „bricht“: *…; in a pilot with a twice larger model (two seeds) it did not hold (Appendix K), so model size is an open limit.*
- bei „unklar“ / „nicht gelernt (Budget)“: *…; a pilot with a twice larger model was inconclusive (Appendix K).*

## Was ausdrücklich nicht gesagt wird

- keine Skalierungsaussage („steering grows/shrinks with size“): zwei Größen, zwei Seeds;
- kein Vergleich der Δ_pow-Beträge zwischen 14 M und 29.5 M als Effekt der Größe (andere Seeds, keine Bestätigung);
- bei „bricht“ keine Ursache (Lernrate nicht angepasst, das ist die naheliegende Gegenerklärung und wird genannt, wenn es dazu kommt).

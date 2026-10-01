---
id: R15_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# R15 (konstruierte gegen gleich große Zufallsmenge an der Datengrenze): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[confirm/R15_REGISTRATION]] · [[experiments/EXP-140-random-at-edge/README|EXP-140]] · [[experiments/EXP-142-shuffled-weights/README|EXP-142]]

**Geschrieben in Sitzung 69 (01.10.2026, 12:12 Berlin gemessen), nach dem Einfrieren (a8033017), vor jedem gelesenen R15-Ergebnis** (bis dahin nur Status von 2 Läufen bei 307 gesehen: Seed 4500 F/G generalisiert). Ort: Anhang A, ein Absatz nach dem R14-Absatz („Confirmation at mod 307 with 10 % data“); in §2 ein Halbsatz beim LeDoux-Vergleich (Mengen-Seite von LeDoux §6.4). **Kein Abstract, keine neue Kernaussage** (Regel 20a). Zahlen nach `confirm_r15.py --analyze`, unabhängige Nachrechnung und Textprüfung. Wortwahl in allen Fällen: „engineered (ε = 2, frequency-targeted) vs. uniform random subset of the same size“, nie „spectral content replaces density“, außer EXP-142 zeigt „Frequenzstruktur nötig“ (dann als *Pilot*-Satz dazu, nicht als Teil der Bestätigung).

## Anhang A, je Ausgang

- **H1 und H2 bestätigt, beide „ermöglicht“:** *Confirmation at the data edge (R15; 10 fresh seeds per cell, frozen analysis, Holm over two cells): at addition mod 401 with 14 000 training pairs and at mod 307 with 9425 pairs, the engineered splits generalized (median … and … steps) while a uniform random subset of the same size generalized in only … and … of 10 seeds within 30 000 steps (mean log ratio of censored generalization steps … [CI] and … [CI], Holm-p …). Near this data edge, which pairs are trained on decides whether the network generalizes within the budget at all, not only when.*
- **bestätigt, „beschleunigt“ (R generalisiert in > 2 Seeds):** *… the random subsets generalized later (… of 10 seeds within the budget; mean log ratio … [CI]) …; the engineered splits shift the data edge rather than removing it for random data.*
- **nur H1 bestätigt:** *… at mod 401 / 14 000 pairs …; at mod 307 / 9425 pairs the difference was not confirmed (…), so the effect depends on the cell.*
- **H1 nicht bestätigt:** *The pilot result that a random subset of the same size fails to generalize at mod 401 / 14 000 pairs (EXP-140, 3 seeds) was not confirmed on 10 fresh seeds (R15: …).* (und kein Satz in §2)
- **nicht auswertbar:** *(a confirmation, R15, was not evaluable: …)*; Pilot EXP-140 nur als Exploration.

## §2, Halbsatz (nur bei H1 bestätigt)

*…; conversely, at our data edge the composition of the set alone (full batch, no order) decided whether a uniform-random-sized set generalized within the budget (R15), the set-side counterpart of LeDoux's §6.4 remark that order matters more when the content signal is weak.*

## Was ausdrücklich nicht gesagt wird

- „R generalisiert nie“ – nur „nicht in 30 000 Schritten“ (zensiert);
- nichts über p = 9973 / 0.3 %, Minibatch oder LeDoux' Architektur; keine Aussage „LeDoux widerlegt“;
- keine Aussage über Frequenzstruktur als Ursache ohne EXP-142 (und auch dann nur Pilot);
- keine Ablation, keine Messung der Nutzung; zwei Zellen, ein Budget, eine Architektur, AdamW.

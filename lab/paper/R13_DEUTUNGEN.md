---
id: R13_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# R13 (K2 unter geclipptem SGD mit Momentum): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[confirm/R13_REGISTRATION]] · [[experiments/EXP-128-sgd-clip/README|EXP-128]] · [[paper/EXP128_DEUTUNGEN]]

**Geschrieben in Sitzung 67 (01.10.2026, 06:11 Berlin gemessen), vor dem Einfrieren und vor jedem R13-Blocklauf.** R13 ist eine Bestätigung (frische Seeds, eingefrorenes Manifest), aber eine **Repräsentationsaussage bei Schritt 2000**. Ort: Grenze (i) der Kurzfassung (ersetzt den Schluss „all results are AdamW results“ nur im Fall „beide bestätigt“ bzw. „c01 bestätigt“), Volltext in Anhang J (neben L0/EXP-126/EXP-128). **Kein Abstract, keine neue Kernaussage** (der Satz der Kernaussagen ist eingefroren, Regel 20a). Zahlen nach `confirm_r13.py --analyze`, unabhängige Nachrechnung und Textprüfung wie immer.

## Grenze (i), je Ausgang

- **c01 und c0017 bestätigt:** *… was not evaluable; however, the steering of the embedding spectrum itself did not require Adam: under full-batch SGD with momentum and global gradient-norm clipping (learning rate 0.1, clip 0.1 or 0.017; R13, 15 fresh seeds each), Δ_pow at step 2000 was … [CI …] and … [CI …], although most runs had not fitted the training set by then. All results on learned solutions, persistence and timing are AdamW results.*
- **nur c01 bestätigt:** wie oben, nur mit Clip 0.1; *with clip 0.017 (almost every step clipped) it was not confirmed (…).*
- **nur c0017 bestätigt:** analog; Hinweis, dass der Standardfall (0.1) nicht bestätigt wurde.
- **keiner bestätigt / nicht auswertbar:** Grenze (i) bleibt unverändert; Anhang J: *A confirmation of the embedding steering under clipped SGD with momentum (R13, …) was not confirmed (…) / not evaluable (…).*

## Was ausdrücklich nicht gesagt wird

- nicht „optimizer-independent“ oder „holds for SGD“: nur geclipptes Full-Batch-SGDm, eine Lernrate, add 113, ein Messschritt;
- keine Aussage über gelernte Lösungen, Funktion (keine Ablation), Festlegung (K4) oder Geschwindigkeit (R5) unter SGD;
- keine Deutung als Mechanismus („Adam-Normierung spielt keine Rolle“); höchstens: die Repräsentationsseite der Steuerung braucht Adams koordinatenweise Normierung nicht;
- die Theorie erster Ordnung (Maskenspektrum im Gradienten) sagt diese Richtung für jedes Gradientenverfahren voraus – das wird als Einordnung genannt, nicht als neuer Befund.

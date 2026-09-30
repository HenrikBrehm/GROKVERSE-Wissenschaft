---
id: EXP-131
status: abgeschlossen
datum: 2026-09-30
tags: [exp/abgeschlossen, befund/negativ, lab/lm, neu/kandidat]
verwandt: ["[[experiments/EXP-127-pretrained-lm/README|EXP-127]]", "[[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-131: Steuert die Faktenauswahl die Zahldarstellung in den Zwischenschichten eines nachtrainierten Pythia-160M? (Pilot, ohne neues Training)

Zurück zu [[LAB]]. **Exploration (2 Seeds × F/G), keine Bestätigung. Kein eigenes Training:** nutzt die von [[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]] gespeicherten Modelle.

**Bezug:** Vorab festgelegte Folge von [[experiments/EXP-127-pretrained-lm/README|EXP-127]] (Lesart „bricht“): „Zwischenschichten messen, bevor etwas behauptet wird“. K2-Geltungsgrenze beim Nachtrainieren (N58, [[FINDINGS]] Exploration S61).

## Vorab (Sitzung 61, 30.09., 17:29 Berlin gemessen, bevor irgendein EXP-130-Modell existiert)

**Bereits gesehen:** EXP-127 (Einbettung nicht gesteuert; Ablationen treffen vortrainierte Frequenzen), das vortrainierte Schichtspektrum aus dem Selbsttest (alle 13 Stufen Top 5 aus {1, 2, 3, 4, 5, 11, 23, 56}). Keine Zwischenschicht eines nachtrainierten Modells.

- **Frage:** Trägt die Änderung der Zahldarstellung in den Schichten 1–12 (Zustand an der Position der Zahl im Prompt [eot, a], hängt kausal nur von a ab) die Zielfrequenzen des jeweiligen Splits?
- **Messgröße:** je Schicht l die Rest-Änderung U_l = H_l(T) − c·H_l(0) gegen das vortrainierte Modell (c skalar, wie EXP-127), P1-Δ_pow zwischen F und G desselben Seeds.
- **Lesarten:** Tor: EXP-130-Basisgenauigkeit ≥ 0.5 in allen vier Modellen. **„gesteuert (Zwischenschichten)“**: Δ_pow_l > 1 in ≥ 3 aufeinanderfolgenden Schichten in beiden Seeds. **„nicht gesteuert“**: |Δ_pow_l| ≤ 1 in allen Schichten 1–12 in beiden Seeds. Sonst **„unklar“**.
- **Beschreibend:** Δ_pow der rohen Zustände, Top 5 von U_l je Arm, Anteil der vortrainierten Top 8 an U_l.
- **Was dagegen spräche (für „gesteuert“):** Die Einbettung (Stufe 0) war in EXP-127 nicht gesteuert; eine Steuerung erst in späteren Schichten würde heißen, dass die Faktenauswahl dort ansetzt, wo das Modell die Zahl weiterverarbeitet. „Nicht gesteuert“ stützt die Wiederverwendungs-Lesart.
- **Nachtrag vor jedem Modell (18:07):** zusätzlich beschreibend die zurückgehaltene Genauigkeit getrennt nach a + b < 113 und a + b ≥ 113 (Übertrag/Abzug). Anlass: die Spekulation aus dem EXP-127-Verlauf, Pythia rechne mod 113 als Addition mit Abzug; ein deutlicher Unterschied wäre ein Hinweis, gleiche Werte widerlegen nichts. Keine Lesart daran gebunden. Selbsttest mit dieser Funktion grün (42 s).
- **Grenzen vorab:** nur die Operandenposition, nicht die Position von „ =“; 12 Schichten × 2 Seeds ohne Korrektur für Mehrfachtests (deshalb 3 aufeinanderfolgende Schichten verlangt); 2 Seeds.
- **Budget:** CPU, 4 Modelle à 113 kurze Prompts: Sekunden bis wenige Minuten. Selbsttest am vortrainierten Modell grün (17:28, 17 s).

## Befehl

```
python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-131-pythia-layer-spectrum/layer_spectrum.py --device cpu
```

## Ergebnis (Sitzung 62, 30.09., 19:55–20:06 Berlin gemessen, CPU 687 s): „nicht gesteuert“

`layer_spectrum.py` (unverändert, vor jedem EXP-130-Modell geschrieben) → `summary.json`. Tor erfüllt (EXP-130-Basis 0.981–0.994). **Δ_pow der Rest-Änderung U_l in den Stufen 0–12: Seed 4002 −0.21 bis −0.01, Seed 4003 +0.01 bis +0.46** → |Δ_pow_l| ≤ 1 in allen Schichten beider Seeds → Vorab-Lesart **„nicht gesteuert“**.

**Beschreibend:** Die Top 5 von U_l sind in allen Schichten 1–12 und in beiden Armen fast dieselben, aus {1, 2, 3, 11, 23} (bei Schicht 1–3 teils 56 statt 3); in der Einbettungsstufe 0 {23, 11, 2, 56, 3}. Anteil der vortrainierten Top 8 an der Leistung von U_l 0.76–0.83 in den Schichten 1–12 (0.53–0.56 in Stufe 0). Rohe Zustände: Δ_pow −0.17 bis +0.45. **Übertrag-Test (Nachtrag vorab, beschreibend):** zurückgehaltene Genauigkeit bei a + b < 113 gegen a + b ≥ 113: 0.993 / 0.994 (4002 F), 0.981 / 0.988 (4002 G), 0.984 / 0.988 (4003 F), 0.982 / 0.979 (4003 G) → kein Unterschied; die Spekulation „Addition mit Abzug“ bekommt daraus keinen Hinweis (widerlegt ist sie damit nicht).

**Deutung (vorläufig, Pilot):** Auch in den Zwischenschichten setzt die Faktenauswahl beim nachtrainierten Pythia keine eigenen Frequenzen durch; die Änderung liegt in allen Schichten auf denselben, überwiegend vortrainierten Frequenzen wie in der Einbettung ([[experiments/EXP-127-pretrained-lm/README|EXP-127]]) und in der Nutzung ([[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]]). Grenze: nur die Operandenposition, 2 Seeds. Ob der vortrainierte Rumpf oder die vortrainierten Zahlzeilen das festlegen, klärt [[experiments/EXP-133-pythia-reset-numbers/README|EXP-133]].

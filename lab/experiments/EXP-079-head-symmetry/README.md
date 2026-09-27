---
id: EXP-079
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]", "[[confirm/N29_REGISTRATION|N29]]", "[[confirm/N29c_REGISTRATION|N29c]]", "[[JOURNAL]]"]
---
# EXP-079: Sind die Attention-Köpfe nach a + b austauschsymmetrisch? (Vorbedingung für N36, Exploration)

Zurück zu [[LAB]] · [[NOVEL_DIRECTIONS]] N36 („Routing oder Inhalt“, Schärfung Sitzung 26) · offene Frage in [[FINDINGS]] (Dong-Gegensatz zu K4e).
Festgelegt 2026-09-27, Sitzung 26, 15:46 Berlin (gemessen), **vor jeder Messung**. Keine Läufe: nur Vorwärtsrechnung der 80 gespeicherten N29-Endmodelle (add 113).

- **Frage:** Ist das Attention-Muster von „=“ auf die Operanden austauschsymmetrisch, α_a(a, b) = α_b(b, a) je Kopf? Nur dann kann das Netz (geteiltes W_E) ausschließlich symmetrische Funktionen
  berechnen, und der geplante Wechsel a + b → a − b verlangt wirklich eine neue Leitung (QK), während a + b → a² + b² nur neuen Inhalt verlangt.
- **Maße je Modell und Kopf:** share_a (mittlerer Anteil auf a unter a und b), swap_diff (mittleres |α_a(a, b) − α_b(b, a)| über alle p² Eingaben).
- **Lesart vorab (beschreibend):** swap_diff < 0.05 in allen Köpfen und |share_a − 0.5| < 0.2 → *symmetrisch* → N36-Versuch mit a − b / a² + b² festlegen. Einzelne Köpfe mit swap_diff ≥ 0.2 oder
  |share_a − 0.5| > 0.2 → *nicht symmetrisch* → a − b ist kein reiner Leitungswechsel; eine andere Leitungsaufgabe suchen. Dazwischen *unklar*.
- **Grenzen:** Endmodelle nach einem Datenwechsel (nicht reine a + b-Läufe); Symmetrie der Attention ist notwendig, aber nicht hinreichend für einen sauberen Gegensatz (MLP, W_pos-Anteile).
- **Befehl (ab 00:00, Sekunden):** `python lab/tools/guarded_run.py -- python lab/experiments/EXP-079-head-symmetry/measure.py`

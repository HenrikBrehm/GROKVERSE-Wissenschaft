---
id: EXP-079
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar]
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

## Nachtrag a (15:53 Berlin, gemessen; vor jeder Messung): Maße erweitert, Lesart nur noch beschreibend

Ein Prüfagent (nur lesend) zeigte: Austauschsymmetrische Attention erzwingt **keine** symmetrischen Ausgaben. Bei symmetrischer Attention ist die Differenz der Ausgaben unter Vertauschung genau Σ_h (α_a − α_b)(a, b) · W_O^h W_V^h (W_pos[0] − W_pos[1]); Inhaltsanteile und der Anteil von „=“ heben sich weg. Antisymmetrie (a − b) kann also auch über eine **Positionsmarke im Wertepfad** (OV(W_pos[0] − W_pos[1])) oder über W_pos entstehen, nicht nur über QK. Das deckt sich mit meiner eigenen Nachrechnung vor der Prüfung. **Neu gemessen:** je Kopf der positionsabhängige QK-Versatz q·K(W_pos[0] − W_pos[1]) und die relative Stärke der OV-Positionsmarke; je Modell die funktionale Antisymmetrie der Logits (mittleres |logits(a, b) − logits(b, a)| relativ). **Lesart ersetzt:** Die Werte beschreiben, über welche Kanäle Positionsinformation am „=“ ankommt; sie sind Material für ein neues N36-Design, kein Startsignal für EXP-080. Grenze bleibt: Endmodelle nach einem Datenwechsel, nicht der Zustand am Wechselzeitpunkt eines geplanten Versuchs.

## Ergebnis (Sitzung 36, 2026-09-28 01:49 Berlin, gemessen; beschreibend nach Nachtrag a)

80 Endmodelle, 320 Köpfe. swap_diff Mittel 0.0066; 3 von 320 Köpfen > 0.05, 2 > 0.2 (Maximum 0.87); größtes |share_a − 0.5| 0.44 (ein Kopf).
QK-Positionsversatz Median 0.0048, OV-Positionsmarke relativ Median 0.0096; funktionale Logit-Antisymmetrie Median 0.25 % (Maximum 5.4 %).
**Beschreibung:** Fast alle Köpfe sind austauschsymmetrisch, und am „=“ kommt kaum Positionsinformation an (weder über QK noch über die OV-Marke); die Ausgaben sind praktisch
symmetrisch. Wenige einzelne Köpfe sind klar asymmetrisch (nach der ursprünglichen, ersetzten Lesart wäre das „nicht symmetrisch“). Für ein N36-Design heißt das: Ein Wechsel
a + b → a − b müsste einen Positionskanal erst aufbauen, den die a + b-Modelle praktisch nicht haben. Welche Köpfe/Modelle die Ausreißer sind, steht nicht in der Zusammenfassung
(nicht nachgesehen). [[JOURNAL]] Sitzung 36.

---
id: EXP-053
status: entwurf
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[BACKLOG]]", "[[experiments/EXP-044-generalize-lockin/README|EXP-044]]", "[[experiments/EXP-041-imprint/README|EXP-041]]", "[[experiments/EXP-020-data-switch/README|EXP-020]]"]
---
# EXP-053 (Entwurf): Split-Paare mit kontrollierter Überlappung für P3 (Paket B)

**Status:** Entwurf der Konstruktion, **keine Läufe, kein Urteil, nicht eingefroren**. Das P3-Design wird erst nach der Pilotnacht
festgelegt ([[BACKLOG]] „Entwurf P3-Bestätigung“). Hier steht nur, *wie* man die Überlappungsstufen baut, ohne die Konkurrenzmodelle zu
vermengen. Zurück zu [[LAB]] · [[FINDINGS]] (Paket B, P3).

## Problem (offline gefunden, Sitzung 14, 21:32 Berlin)

Die Konkurrenzmodelle (i) „Festlegung im Netz“ und (ii) „nur geteilte Paare halten die Wahl“ werden über Stufen der Überlappung
zwischen erstem (A, Ziele F) und zweitem Split (B, Ziele G) getrennt. Zwei naheliegende Konstruktionen sind dafür unbrauchbar:

1. **B aus dem Rest nach A ziehen** (sequenziell, damit die Überlappung genau stimmt): Der Rest trägt das Negativbild von A. Die
   F-Leistung im M0 von B steigt dann auf 0.12–0.21 (Zufall 0.09, B:G 0.15–0.21). B würde F selbst hervorheben, und „Persistenz“ wäre
   teilweise Datenwirkung.
2. **Geteilte Paare gleichverteilt, ε fest:** Die Steuerstärke sinkt mit der Überlappung (A:F bei ω = 0.375: 0.14 statt 0.18 bei ε = 2;
   bei ω = 0.75 höchstens 0.12 selbst mit ε → ∞). Dann wäre Überlappung mit schwächerer Steuerung vermengt.

## Konstruktion (`overlap_split.py`)

Gemeinsame Testmenge (20 %), geteilte Paare S (ω · 3831) **gleichverteilt** aus dem Pool (ohne Zielinhalt), die übrigen Paare von A und B
**abwechselnd** aus ihren eigenen Schlüsselreihenfolgen (symmetrische Konkurrenzziehung, Überlappung exakt |S|), ε je Stufe so
kalibriert, dass der M0-Zielanteil von A und B bei 0.185 liegt (EXP-016-Niveau). Kalibrierseeds 900–909 (nicht der reservierte Block).

| ω (Anteil geteilter Paare) | ε | A: Anteil F | A: Anteil G | B: Anteil G | B: Anteil F | M0c-Anteil A:F | Häufigkeitsrang F (Zufall 27.5) | Spiegelpaare A/B |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 2.23 | 0.184 | 0.093 | 0.186 | 0.092 | 0.185 | 14.4 | 564/568 |
| 0.2 | 3.01 | 0.187 | 0.088 | 0.183 | 0.089 | 0.190 | 13.9 | 570/561 |
| 0.4 | 5.94 | 0.185 | 0.083 | 0.185 | 0.082 | 0.188 | 11.6 | 570/563 |

Mittel über 10 Kalibrierseeds, reine Rechnung (`calibration.json`). Die Kreuzanteile liegen auf Zufallsniveau (0.09), die Steuerstärke
ist über die Stufen gleich, M0c und Spiegelpaare ebenso. **Rest-Confounds:** ε unterscheidet sich (die Gewichte werden mit größerem ε
binärer) und der Häufigkeitsrang der Ziele ist bei ω = 0.4 etwas besser (11.6 statt 14.4). ω > 0.4 ist mit gleicher Stärke kaum
erreichbar; höhere Überlappung nur mit schwächerer Steuerung (dann als eigener, konfundierter Arm kennzeichnen).
*Lehre:* Bei jedem Paar-Design aus einem gemeinsamen Pool das M0 des *zweiten* Splits auf die Ziele des *ersten* prüfen.

**Nicht betroffen (geprüft per Suche nach Paar-Ausschlüssen in den `make_split`-Dateien):** Die vorhandenen Split-Paare ziehen
unabhängig (EXP-044) oder schließen nur Ziel*mengen* aus, keine Paare. Die Testmenge ist das Komplement des Trainings und trägt dessen
Negativbild; für W_E-Messungen unerheblich, für funktionale Tests auf der Komplement-Testmenge zu bedenken (EXP-051 nutzt eine gemeinsame Testmenge).

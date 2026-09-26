---
id: EXP-028
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/unklar]
---
# EXP-028: Prägt die Memorisierungsphase das Masken-Spektrum ein, und bringt die Generalisierung die Oberwellen?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N13) · Grundlage
[[experiments/EXP-016-engineered-split/README|EXP-016]] (post hoc) · Bestätigungsdaten aus
[[experiments/EXP-020-data-switch/README|EXP-020]] · verwandt [[experiments/EXP-021-harmonic-misses/README|EXP-021]],
[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] (ReLU-Netze memorieren und zeigen F sofort).

## Anlass (post hoc, Sitzung 7, 09:45 Berlin, `EXP-016/posthoc_memo_imprint.py`)

In allen 20 EXP-016-Transformerläufen liegt Schritt 250 in der Memorisierungsphase (Train ≥ 0.99 ab Schritt 120–130,
Test ≥ 0.95 erst bei 450–1100). **Bei Schritt 250 sind die W_E-Top-5 in 20/20 Läufen genau die 5 Ziele F** (Anteil der
W_E-Leistung auf F 0.27–0.40, Zufall 0.089). Bis zum Ende fällt die Überlappung auf 3.9; die ersetzten Ziele werden nach
EXP-016 (post hoc) durch 2k-Oberwellen verdrängt. Der Abfall liegt grob um die Generalisierung (Spektren nur alle 250
Schritte). Das ist explorativ und an denselben Daten gefunden, die es beschreibt; deshalb hier die Bestätigung an frischen
Läufen.

## Versuch (vorab festgelegt 2026-09-26 09:47 Berlin; kein EXP-020-Lauf existiert zu diesem Zeitpunkt)

| Punkt | Festlegung |
|---|---|
| **Frage** | Ist die Zielmenge des Splits in der Memorisierungsphase vollständig in W_E eingeprägt, bevor das Netz generalisiert, und verliert sie danach Plätze? |
| **Daten** | Die EXP-020-Läufe **ohne Wechsel**: „nur F“ (Seeds 30–34, bis Generalisierung + 2000) und „nur G“ (Seeds 30–34, 2000 Schritte); zusammen bis zu 10 Läufe. Keine eigenen Läufe |
| **Memorisierungsfenster** | Gespeicherte Spektren (alle 250 Schritte) mit Schritt ≥ Memorisierungsschritt (Train ≥ 0.99) und < Generalisierungsschritt (Test ≥ 0.95; nie erreicht → Laufende). Maßgeblich ist das **letzte** Spektrum im Fenster. Lauf ohne Spektrum im Fenster: nicht auswertbar |
| **P28a (Einprägung, primär)** | Top-5 von W_E im Memorisierungsfenster = Zielmenge des Splits. *bestätigt*: ≥ 8 der auswertbaren Läufe mit Überlappung 5/5 **und** mittlere Überlappung ≥ 4.5; *widerspricht*: mittlere Überlappung < 3; dazwischen *teilweise*. < 6 auswertbare Läufe: *nicht auswertbar* |
| **P28b (Verlust um die Generalisierung, sekundär)** | In den Läufen mit 5/5 im Fenster ist die Überlappung am Laufende kleiner (≥ 1 verlorenes Ziel) in mindestens der Hälfte; verlorene Ziele werden durch fold(2f) eines Ziels ersetzt (Zählung wie EXP-021). Nur berichtet |
| **Was dagegen spräche** | Überlappung im Fenster wie am Ende (≈ 3.9) oder darunter: Dann ist die volle Einprägung von EXP-016 ein Zufall der Gitterpunkte |
| **Grenzen** | Spektren nur alle 250 Schritte; bei früher Generalisierung (< 250) gibt es kein Fenster. Die „nur F“-Läufe laufen länger als die „nur G“-Läufe; Endvergleich (P28b) deshalb getrennt nach Arm berichten. Die Einprägung ist nur eine Assoziation mit dem Masken-Spektrum; der Kausaltest der Steuerung ist EXP-016 selbst |

**Neuheit:** vorläufig, siehe [[NOVEL_DIRECTIONS]] N13.

## Befehle

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-028-memo-imprint/analyze.py

## Ergebnis (2026-09-26 16:22 Berlin, `analyze.py` über die EXP-020-Läufe „nur F“/„nur G“, Seeds 30–34)

**P28a: *teilweise*** (vorab festgelegte Regel): 10 auswertbare Läufe, 6 mit Überlappung 5/5 im Memorisierungsfenster
(gefordert ≥ 8), mittlere Überlappung 4.5 (gefordert ≥ 4.5 für *bestätigt*, < 3 *widerspricht*). Am Laufende mittlere
Überlappung 3.5.
**P28b (nur berichtet):** In 5 der 6 Läufe mit 5/5 geht bis zum Laufende mindestens ein Ziel verloren (Arm F 2/3, Arm G 3/3);
alle 8 Ersetzungen sind fold(2f) eines Ziels. Stützt das Bild „Memorisierung prägt das Masken-Spektrum ein, um die
Generalisierung verdrängen 2k-Oberwellen Teile davon“ (N13) beschreibend.

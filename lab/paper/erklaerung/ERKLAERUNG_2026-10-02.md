---
id: ERKLAERUNG_2026-10-02
datum: 2026-10-02
tags: [lab/erklaerung]
---
# Erklärung für den 02.10.2026 (angelegt in Sitzung 68 am 01.10. um 08:46, vor den Ergebnissen)

Zurück zu [[LAB]] · [[FINDINGS]] · [[paper/STATUS]] · Vortag [[paper/erklaerung/ERKLAERUNG_2026-10-01]]

## Was gerade läuft und was wir vorher erwarten

1. **EXP-139 (Vorversuch, 3 Seeds je Zelle): Zählt die Zahl der Trainingspaare oder ihr Anteil?** Bei Zahlen bis 210 reichten 10 % der Aufgaben (4452 Paare) nicht zum Verallgemeinern, bei Zahlen bis 306 reichten 10 % (9425 Paare). Jetzt trainieren wir mit immer gleich vielen Paaren (9425 oder 14 000) bei Zahlen bis 400, 502 und 612 – das sind nur noch 2,5 bis 8,7 % aller Aufgaben. Drei mögliche Erklärungen, vorher aufgeschrieben: (a) die Zahl der Paare entscheidet, (b) der Anteil entscheidet, (c) entscheidend ist, wie oft jede einzelne Zahl im Training vorkommt (Paare geteilt durch p). Danach prüfen wir wie immer, ob die Datenauswahl die Frequenzen auch dort bestimmt.
2. **EXP-140 (vorbereitet): Hilft die gezielte Auswahl dem Netz an der Datengrenze überhaupt erst zu lernen?** Dieselben Zellen mit gleich vielen, aber *zufällig* gewählten Paaren. Wenn die Zufallsauswahl nicht verallgemeinert, die gezielte aber schon, ersetzt der „Inhalt“ der Daten fehlende Menge. Das wäre die Mengen-Seite eines Satzes aus der LeDoux-Arbeit („die Reihenfolge ist umso wichtiger, je schwächer das Signal im Inhalt“).

3. **EXP-143 (neu, Sitzung 70, Vorversuch mit 1 Seed je Lauf): der LeDoux-Test selbst.** Zahlen bis 9972, nur 300 000 Trainingsaufgaben (0,3 %), Stapel von 256 – genau LeDoux' Einstellung, aber mit unserem Netz. Vier Läufe: zufällige oder gezielte Auswahl × gemischte oder sortierte Reihenfolge (LeDoux' „Stride“). Vorher aufgeschrieben: (a) Lernt nur die gezielte Auswahl bei gemischter Reihenfolge, ersetzt der Inhalt die Reihenfolge. (b) Lernt die zufällige Auswahl mit sortierter Reihenfolge und zeigt Frequenz 101, haben wir LeDoux' Effekt mit unserem Netz nachgestellt. (c) Im Konfliktlauf (gezielt + sortiert) sehen wir, ob unsere Ziel-Frequenzen oder die der Reihenfolge gewinnen. Ehrliche Erwartung: Es kann gut sein, dass in 250 000 Schritten gar kein Lauf lernt – unsere Hochrechnung sagt, dass 300 000 Paare für unser Netz eher zu wenig sind. Das wäre dann „keine Aussage“, kein Gegenbeweis.

## Was heute herauskam

(wird nach den Auswertungen ergänzt)

## Drei Fragen, die eine Jury stellen könnte

1. **„Warum nicht gleich mit Zahlen bis 9972 wie LeDoux?“** – Unser Trainingsprogramm rechnet die Prüfung über alle Aufgaben auf einmal; bei 9973 wären das Hunderte Gigabyte. Dafür müsste man es umbauen und den Umbau erst prüfen. Wir gehen deshalb schrittweise nach oben und lernen unterwegs, welche Größe die Grenze setzt.
2. **„Was heißt ‚bestätigt‘ bei R14?“** – Vorher festgelegte Regel, 12 neue Seeds, Auswertungscode eingefroren, bevor ein Lauf fertig war; dann hat ein zweites Programm (unabhängig geschrieben) alle Zahlen nachgerechnet.
3. **„Warum reicht ein Vorversuch mit 3 Seeds nicht?“** – Drei Seeds zeigen eine Richtung, aber zufällige Ausreißer können sie vortäuschen. Darum steht EXP-139 im Paper höchstens als Vorversuch, bis ein Bestätigungsblock mit frischen Seeds folgt.

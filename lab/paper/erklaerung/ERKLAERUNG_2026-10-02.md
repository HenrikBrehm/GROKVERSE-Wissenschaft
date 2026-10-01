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

4. **EXP-144 (neu, Sitzung 71, Vorversuch mit 1 Seed je Lauf): dasselbe wie EXP-143, aber mit einem 4-mal breiteren Netz.** In EXP-143 hat unser kleines Netz in LeDoux' Einstellung nicht einmal die Trainingsaufgaben gelernt, also konnten wir die Frage „Menge oder Reihenfolge“ dort gar nicht stellen. Jetzt prüfen wir zuerst, ob ein breiteres Netz die Trainingsaufgaben lernt (Frage 0), und dann dieselben Fragen wie vorher. Ehrliche Erwartung: Die zufällige Auswahl mit gemischter Reihenfolge lernt wahrscheinlich nicht – das war auch bei LeDoux so. Spannend ist, ob unsere gezielte Auswahl ohne Sortierung lernt.

## Was heute herauskam

(wird nach den Auswertungen ergänzt)

## Drei Fragen, die eine Jury stellen könnte

1. **„Warum nicht gleich mit Zahlen bis 9972 wie LeDoux?“** – Unser Trainingsprogramm rechnet die Prüfung über alle Aufgaben auf einmal; bei 9973 wären das Hunderte Gigabyte. Dafür müsste man es umbauen und den Umbau erst prüfen. Wir gehen deshalb schrittweise nach oben und lernen unterwegs, welche Größe die Grenze setzt.
2. **„Was heißt ‚bestätigt‘ bei R14?“** – Vorher festgelegte Regel, 12 neue Seeds, Auswertungscode eingefroren, bevor ein Lauf fertig war; dann hat ein zweites Programm (unabhängig geschrieben) alle Zahlen nachgerechnet.
3. **„Warum reicht ein Vorversuch mit 3 Seeds nicht?“** – Drei Seeds zeigen eine Richtung, aber zufällige Ausreißer können sie vortäuschen. Darum steht EXP-139 im Paper höchstens als Vorversuch, bis ein Bestätigungsblock mit frischen Seeds folgt.

**Zusatzfragen zu EXP-143 (Sitzung 70):**

4. **„Warum nehmt ihr nicht einfach LeDoux' Netz?“** – Uns geht es nicht darum, LeDoux nachzubauen, sondern darum, ob *unser* Befund (die Auswahl steuert die Frequenzen) in seinem Datenregime hält. Deshalb übernehmen wir seine Daten (Zahlen bis 9972, 300 000 Aufgaben, Stapel von 256, schwacher Weight Decay 0,1), behalten aber unser Netz. Ob LeDoux' Reihenfolge-Effekt mit unserem Netz überhaupt auftritt, prüft ein eigener Kontrolllauf (zufällige Auswahl + sortierte Reihenfolge). Klappt der nicht, können wir den Konfliktlauf nur eingeschränkt deuten – auch das steht vorher fest.
5. **„Ihr habt den Versuch vor dem Start dreimal geändert. Ist das nicht Schummeln?“** – Nein, solange es *vor* jedem Ergebnis passiert und begründet ist. Alle drei Änderungen (Weight Decay 0,1, weil unser Netz mit 1,0 bei kleinen Stapeln in früheren Versuchen nicht lernte; längere Läufe, weil LeDoux so lange brauchte; eine sauber berechnete Liste der „Reihenfolge-Frequenzen“) stehen mit Uhrzeit in der Versuchsbeschreibung, und ein unabhängiger Prüfer hat zwei davon angestoßen. Schummeln wäre, die Regeln *nach* dem Blick auf die Ergebnisse zu ändern.


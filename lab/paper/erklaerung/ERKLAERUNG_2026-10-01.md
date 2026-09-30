---
id: ERKLAERUNG_2026-10-01
datum: 2026-10-01
tags: [lab/erklaerung]
---
# Erklärung für den 01.10.2026 (angelegt in Sitzung 57 am 30.09. um 06:26, vor den Ergebnissen)

Zurück zu [[LAB]] · [[FINDINGS]] · [[paper/STATUS]] · Vortag [[paper/erklaerung/ERKLAERUNG_2026-09-30]]

## Was gerade läuft und was wir vorher erwarten

1. **LM3 (Sprachmodell mit nur ≈ 9 % Rechentext, 10 neue Seeds):** Bestätigungsblock für EXP-116. Erwartung: Die Faktenauswahl steuert die Zahlen im Modell auch hier (Δ_pow über 1). Risiko: Im Pilot sank die Steuerung nach dem Lernbeginn in einem Seed wieder ab; gemessen wird erst am Ende (Schritt 15 000). Ein Ergebnis knapp über oder unter der Grenze wäre deshalb kein Widerspruch zum Pilot.
2. **R12 (neu, Sitzung 57):** Unser zweites Hauptergebnis („mit ausgewählten Trainingsdaten groket das Netz etwa 6- bis 7-mal früher“) war bisher nur für eine Aufgabe (Addition mod 113) bestätigt. R12 prüft dasselbe, vorher festgelegt und mit 20 neuen Einheiten je Aufgabe, bei Addition mod 97 und Multiplikation mod 113. Erwartung: schneller als Zufallsdaten (ein alter Pilot zeigte das schon); ob auch schneller als die Kontrolle mit gleich vielen Aufgaben je Ergebnis, wissen wir nicht, dafür gibt es keinen Pilot.
3. **EXP-125 (neu, Pilot mit 2 Seeds):** dasselbe Sprachmodell-Experiment wie LM1, aber mit einem etwa doppelt so großen Modell (≈ 30 statt 14 Millionen Parameter). Erwartung: Die Steuerung hält. Bricht sie, wäre das eine wichtige Grenze.
4. **EXP-127 (vorbereitet in Sitzung 58, läuft nach R12): ein fertiges, öffentlich trainiertes Modell (Pythia-160M) auf ausgewählte Rechenfakten nachtrainieren.** Erwartung (vorab, 30.09. mittags): Am Anfang zeigt die Lernrichtung unsere Auswahl nicht (gemessen, [[paper/erklaerung/ERKLAERUNG_2026-09-30]] Nachtrag 11:36); wenn die Steuerung trotzdem kommt, entsteht sie erst im Verlauf. Beides wäre ein Befund.
5. **EXP-128 (neu, Sitzung 59, läuft nach EXP-125): Steuerung ohne Adam, zweiter Versuch.** Einfaches SGD war gestern nicht prüfbar (lernt nicht oder läuft aus dem Ruder). Jetzt wird die Schrittlänge nach oben begrenzt („Clipping“), zwei Stärken, die aus einer Messung abgeleitet sind. Erwartung: offen; die Paper-Sätze für jeden Ausgang stehen schon vorher fest ([[paper/EXP128_DEUTUNGEN]]).

6. **EXP-133 (neu, Sitzung 62, 30.09. abends, Pilot mit 2 Seeds): Warum steuert unsere Datenauswahl das fertige Modell Pythia nicht?** Zwei mögliche Gründe: (a) Pythia hat in seinen Zahl-Vektoren schon passende Muster und benutzt einfach die; (b) der Rest von Pythia (die Schichten dahinter) zwingt jeder Zahl seine eigenen Muster auf. Test: Wir löschen nur das Zahlspezifische in den Zahl-Vektoren (ersetzen es durch Zufall) und trainieren wie vorher. Kommt die Steuerung zurück, spricht das für (a), sonst für (b). Kniff, der beim Vorbereiten auffiel: Alle Zahl-Vektoren teilen einen gemeinsamen Anteil („das ist eine Zahl“). Löscht man den mit, rät das Modell am Anfang völlig daneben (Verlust 840 statt 6). Deshalb bleibt dieser gemeinsame Anteil stehen. Erwartung: offen; beide Ausgänge sind ein Befund.

## Was heute herauskam

- **EXP-126 (30.09., 07:59, Sitzung 57): Klappt die Steuerung auch ohne Adam, mit einfachem SGD?** Nicht prüfbar: Bei Lernrate 0.05 lernt SGD gar nichts, bei 0.1 läuft es aus dem Ruder (die Zahlen werden unendlich). Das Urteil lautet deshalb, wie vorher festgelegt, „nicht auswertbar“. *Was es nicht bedeutet:* nicht, dass die Steuerung Adam braucht. Im einzigen Lauf, der vor dem Absturz lernte, lagen 92 % der Energie auf den Frequenzen, die unsere Datenauswahl vorgab. Das ist aber nur ein einzelner Lauf, also eine Beobachtung und kein Test. Für einen echten Test muss SGD zuerst stabil laufen (später, mit einer Trainer-Änderung).
- (LM3, R12 und EXP-125 werden eingetragen, sobald sie fertig und ausgewertet sind.)

## Drei Fragen, die eine Jury stellen könnte

1. **„Warum prüft ihr ein bestätigtes Ergebnis noch einmal an anderen Aufgaben?“** – Weil ein Ergebnis, das nur bei einer Zahl (113) gilt, wenig heißt. Wenn es bei 97 und bei der Multiplikation auch gilt, ist es eine Eigenschaft der Datenauswahl; wenn nicht, schreiben wir die Grenze genau so ins Paper.
2. **„Was ist die Kontrolle D?“** – Ein Datensatz, der für jedes Ergebnis (zum Beispiel „Summe = 17“) genau so viele Trainingsaufgaben hat wie unser ausgewählter Datensatz, nur anders verteilt. Ist unser Datensatz auch schneller als D, liegt es an der *Anordnung* der Aufgaben, nicht daran, wie oft jedes Ergebnis vorkommt.
3. **„Heute Nacht habt ihr etwas ausgeschlossen. Was?“** – Unsere Datensätze lernen die Vertauschungsregel (a + b = b + a) viel früher. Eine einfache Erklärung wäre: Sie enthalten mehr Paare, bei denen beide Reihenfolgen im Training sind. Das stimmt nicht: Alle Datensätze haben davon gleich viele (etwa 30 %). Die Erklärung muss also woanders liegen (vermutlich bei den früh gelernten Frequenzen, das ist aber nicht geprüft).

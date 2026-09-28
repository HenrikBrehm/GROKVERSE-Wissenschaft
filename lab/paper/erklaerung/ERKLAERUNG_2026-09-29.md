---
id: ERKLAERUNG_2026-09-29
datum: 2026-09-29
tags: [lab/erklaerung]
---
# Erklärung für den 29.09.2026 (angelegt in Sitzung 44 am 28.09. abends, vor den Nachtläufen)

Zurück zu [[LAB]] · [[FINDINGS]] · [[paper/STATUS]] · [[NACHT_2026-09-29]]

## Was wir vor den Läufen vorhergesagt haben (festgehalten, damit man später vergleichen kann)

1. **Reihenfolge gegen Menge (L0).** Das Netz legt sich in den ersten 25–50 Trainingsschritten auf seine Frequenzen fest. Wenn man die Beispiele in einer festen Reihenfolge zeigt, kann diese Reihenfolge nur dann etwas „einflüstern“, wenn das Netz in dieser Zeit noch nicht alle Beispiele gesehen hat. Bei 30 % Daten und Päckchen zu 256 Beispielen ist nach 15 Schritten schon alles einmal gezeigt, bis Schritt 50 also mehr als dreimal. Unsere Rechnung (vereinfachte erste Näherung) sagt: Dort wäscht sich die Reihenfolge aus. Bei Päckchen zu 64 Beispielen dauert ein Durchgang 60 Schritte; dort könnte die Reihenfolge wirken, die Rechnung liegt aber genau an der Grenze. Deshalb prüfen wir heute Nacht beide Päckchengrößen.
2. **Recursive Feature Machine (EXP-101).** Ein Lernverfahren ohne „Sparzwang“ könnte alle Frequenzen gleichzeitig nutzen. Dann würde die Datenauswahl dort wenig steuern. Das wäre ein Hinweis, dass unsere Steuerung einen Lerner braucht, der sich für wenige Frequenzen entscheiden muss.
3. **Frühe Kurve (EXP-103).** Die Abweichung der ersten Punkte in Abb. 12 ist vermutlich nur ein Rechenartefakt (wir kannten die Standardkurve nur bei Schritt 0 und 250).

4. **Zufallssplits unter Päckchen-Training (neu, 28.09. abends).** Bei gewöhnlichen Zufallssplits nutzt das Netz vor allem Frequenzen, die im Muster seiner eigenen Trainingspaare stark sind. Wir sagen voraus, dass das auch beim Training in Päckchen gilt (die fünf stärksten Frequenzen im Mittel mindestens beim 65. Perzentil der eigenen Maske), und dass eine feste Reihenfolge das dort abschwächt, wo sie überhaupt wirkt. Getestet an 18 Läufen, die heute Nacht zum ersten Mal gerechnet werden.

## Was heute herauskam

**Schon am späten Abend des 28.09. (ohne neue Läufe, an gespeicherten Daten, unabhängig nachgerechnet):**
- **Auch ein ganz normaler Zufallssplit lenkt.** Jede Auswahl von Trainingspaaren hat ein „Maskenspektrum“: wie stark jede Frequenz im Muster der gezeigten Paare steckt. Bei 60 Einheiten mit gewöhnlichen Zufallssplits lagen die fünf Frequenzen, die ein Netz am stärksten nutzt, im Mittel beim 78. Perzentil der eigenen Maske. Beim anderen, gleich großen Split derselben Einheit lagen sie nur beim 50. Perzentil, also beim Zufall (60 von 60 Einheiten). Unsere konstruierten Splits drehen also nur stärker an einem Regler, der immer schon da ist. *Grenze:* nachträglich gerechnet, eine Aufgabe; dass es genau über das Maskenspektrum läuft, ist nicht bewiesen.
- **Kleinere Päckchen für den Reihenfolge-Test.** Die Rechnung sagt: Nur wenn ein Durchgang durch die Daten viel länger dauert als die 25–50 Schritte, in denen das Netz sich festlegt, kann eine feste Reihenfolge gegen die Menge ankommen. Deshalb testen wir heute Nacht zusätzlich Päckchen zu 16 Beispielen (240 Schritte je Durchgang).
- **Ein neuer Split-Typ (Idee N53):** Paare so auswählen, dass jede Zahl in jeder Rolle genau gleich oft vorkommt und trotzdem fünf Frequenzen stark betont sind. Damit kann man später in einem Sprachmodell ausschließen, dass nur die Häufigkeit der Zahlen wirkt. Noch nicht trainiert.

**In der Nacht (ab 23:59):**
- **Die gelenkten Frequenzen tragen wirklich die Rechnung.** Man kann aus den Ausgaben eines fertigen Netzes alles herausfiltern außer den fünf Frequenzen, die wir über die Trainingspaare vorgegeben haben. Dann rechnet das Netz auf ungesehenen Aufgaben immer noch praktisch fehlerfrei. Lässt man stattdessen nur die fünf Frequenzen des anderen Splits übrig, liegt es völlig daneben. Das gilt für alle vier Aufgaben und alle 20 Netze je Aufgabe. *Grenze:* noch nicht unabhängig nachgerechnet; gemessen an schon bekannten Netzen.

*Nachtrag 01:22:* Die Nanda-Messung ist inzwischen von einem zweiten, unabhängigen Programm nachgerechnet: gleiche Zahlen, in jeder Aufgabe 20 von 20 Netzen.
- **Die frühe Festlegung gilt auch bei anderen Aufgaben (R11).** Bisher war nur für Addition mod 113 bestätigt, dass die ersten 25–50 Schritte die spätere Frequenzwahl festlegen. Jetzt auch für Addition mod 97 und Multiplikation mod 113, mit je 30 neuen Netzen, vorher eingefroren: Wechselt man die Trainingsdaten nach 25 Schritten, setzt sich meist der zweite Datensatz durch (vom ersten bleiben im Mittel 27–38 % übrig); nach 50 Schritten bleibt überwiegend der erste (74–90 %). Alle sechs vorab formulierten Tests bestanden. *Grenze:* ein Energiemaß der Einbettung, keine Ablation; eine Architektur; unabhängige Nachrechnung läuft.
- **Reihenfolge gegen Menge, erster Schritt (Machbarkeit).** Vorhersage 1 hat gestimmt: Bei Päckchen zu 256 wirkt eine feste Reihenfolge überhaupt nicht, bei 64 nur ganz knapp. Bei 16 wirkt sie stark, **aber dort lernt das Netz mit den normalen Einstellungen gar nichts** (auch nicht mit zufälliger Reihenfolge). Ein Netz, das nicht lernt, kann aber keinen fairen Wettstreit zwischen Menge und Reihenfolge zeigen. Deshalb testen wir jetzt, ob es bei 16 mit kleinerer Lernrate lernt.
- **Vorhersage 2 (RFM) nicht prüfbar.** Die Recursive Feature Machine hat die Aufgabe bei 30 % Daten nicht gelernt (Testgenauigkeit 0.63–0.88 statt ≥ 0.95), auch nicht mit doppelt so vielen Schritten. Also können wir dort nichts über die Steuerung sagen, weder dafür noch dagegen.
- **Vorhersage 4 knapp verfehlt („unklar“).** Unter Päckchen-Training lagen die genutzten Frequenzen beim 64.–71. Perzentil der eigenen Maske (bei 256 knapp unter der Schwelle 65). Wo die feste Reihenfolge wirkt (64), zieht sie die Wahl von der Maske weg, wie vorhergesagt. Nur 3 Netze je Zelle.
- **Klassisches SGD ließ sich nicht einstellen:** Bei kleiner Lernrate lernt es nicht, bei größerer läuft es aus dem Ruder. Der SGD-Vergleich fällt deshalb aus („nicht auswertbar“).

*(Weitere Ergebnisse folgen.)*

## Drei Fragen, die eine Jury stellen könnte

0. **„Wenn schon Zufallssplits lenken, ist euer Ergebnis dann nicht trivial?“** – Nein: Beim Zufall ist der Effekt klein und nicht steuerbar (die gemeinsamen Top-Frequenzen zweier Netze mit gleichem Split: etwa eine von fünf). Mit konstruierten Splits wählt man die Frequenzen vorher aus, und das Netz folgt in 50 von 50 Fällen. Dass beides in dieselbe Richtung zeigt, macht die Erklärung einheitlicher.

1. **„Warum schreibt ihr Vorhersagen auf, bevor ihr rechnet?“** – Damit wir uns hinterher nicht selbst etwas zurechtlegen. Jede Vorhersage steht mit Uhrzeit in git, bevor der passende Lauf startet.
2. **„Was ist eine Epoche?“** – Ein kompletter Durchgang durch alle Trainingsbeispiele. Bei 3831 Beispielen und Päckchen zu 256 sind das 15 Schritte.
3. **„Und wenn die Vorhersage falsch ist?“** – Dann ist das ein Ergebnis. Die Vorhersage ist eine vereinfachte Rechnung ohne den Optimierer. Liegt sie daneben, zeigt das, dass Adam oder die Nichtlinearität des Netzes die Reihenfolge anders verarbeitet.

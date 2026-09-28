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

*(Nachtergebnisse folgen.)*

## Drei Fragen, die eine Jury stellen könnte

0. **„Wenn schon Zufallssplits lenken, ist euer Ergebnis dann nicht trivial?“** – Nein: Beim Zufall ist der Effekt klein und nicht steuerbar (die gemeinsamen Top-Frequenzen zweier Netze mit gleichem Split: etwa eine von fünf). Mit konstruierten Splits wählt man die Frequenzen vorher aus, und das Netz folgt in 50 von 50 Fällen. Dass beides in dieselbe Richtung zeigt, macht die Erklärung einheitlicher.

1. **„Warum schreibt ihr Vorhersagen auf, bevor ihr rechnet?“** – Damit wir uns hinterher nicht selbst etwas zurechtlegen. Jede Vorhersage steht mit Uhrzeit in git, bevor der passende Lauf startet.
2. **„Was ist eine Epoche?“** – Ein kompletter Durchgang durch alle Trainingsbeispiele. Bei 3831 Beispielen und Päckchen zu 256 sind das 15 Schritte.
3. **„Und wenn die Vorhersage falsch ist?“** – Dann ist das ein Ergebnis. Die Vorhersage ist eine vereinfachte Rechnung ohne den Optimierer. Liegt sie daneben, zeigt das, dass Adam oder die Nichtlinearität des Netzes die Reihenfolge anders verarbeitet.

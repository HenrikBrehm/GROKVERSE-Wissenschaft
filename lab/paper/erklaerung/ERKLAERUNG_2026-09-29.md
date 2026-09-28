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

## Was heute herauskam

*(wird von der Nachtsitzung ergänzt)*

## Drei Fragen, die eine Jury stellen könnte

1. **„Warum schreibt ihr Vorhersagen auf, bevor ihr rechnet?“** – Damit wir uns hinterher nicht selbst etwas zurechtlegen. Jede Vorhersage steht mit Uhrzeit in git, bevor der passende Lauf startet.
2. **„Was ist eine Epoche?“** – Ein kompletter Durchgang durch alle Trainingsbeispiele. Bei 3831 Beispielen und Päckchen zu 256 sind das 15 Schritte.
3. **„Und wenn die Vorhersage falsch ist?“** – Dann ist das ein Ergebnis. Die Vorhersage ist eine vereinfachte Rechnung ohne den Optimierer. Liegt sie daneben, zeigt das, dass Adam oder die Nichtlinearität des Netzes die Reihenfolge anders verarbeitet.

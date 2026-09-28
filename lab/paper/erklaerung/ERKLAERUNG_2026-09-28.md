---
id: ERKLAERUNG_2026-09-28
datum: 2026-09-28
tags: [lab/erklaerung]
---
# Erklärung für den 28.09.2026 (Abend, Sitzung 43)

Zurück zu [[LAB]] · [[FINDINGS]] · [[paper/STATUS]]

## Was heute herauskam

1. **Eine Einschränkung an einem eigenen Befund.** Gestern hatten wir gesehen: Wenn das Netz in den ersten 24 Schritten nur den *allerersten* Gradienten benutzen darf, legt es sich viel schwächer auf seine Frequenzen fest (EXP-095). Heute hat sich gezeigt: Mit so einem eingefrorenen Gradienten macht der Optimierer Adam nur noch „Vorzeichenschritte“. Jede Zahl im Embedding bewegt sich gleich weit, nur die Richtung (+ oder −) unterscheidet sich. Allein dieses Runden erklärt etwa die Hälfte der schwächeren Zielgenauigkeit. Der Hauptbefund („wie oft der Gradient neu berechnet wird, zählt“) bleibt davon unberührt, weil die anderen Versuchsarme kaum gerundet sind. Das wurde bei drei verschiedenen Toleranzen geprüft.
2. **Der Plan für die Woche wurde umgestellt** (dein Auftrag, Regel 20). Wichtigster offener Einwand: Alle unsere Ergebnisse stammen aus Training mit dem *ganzen* Datensatz auf einmal (Full-Batch). LeDoux (2026) zeigt, dass beim Training mit kleinen Portionen (Minibatches) schon die *Reihenfolge* der Beispiele bestimmen kann, welche Frequenz das Netz lernt. Deshalb ist der nächste Hauptversuch **L0 „Menge gegen Reihenfolge“** (EXP-100): Steuert unsere konstruierte Datenauswahl die Frequenzen auch mit Minibatches? Und was gewinnt, wenn eine sortierte Reihenfolge eine *andere* Frequenz bevorzugt (bei p = 113 vor allem Frequenz 11)? Plan und Trainer-Code sind fertig, gerechnet wird ab heute Nacht.
3. **Für das Paper:** Es gibt jetzt eine Kurzfassung (≤ 8 Seiten, drei Kernaussagen, [[paper/draft_short]]). Jeder Abschnitt wurde von einem unabhängigen Prüfprogramm gegen die gespeicherten Ergebnisse gelesen. Alle Zahlen stimmten, aber mehrfach war der Geltungsbereich zu groß formuliert (z. B. gelten Beschleunigung und Festlegung bisher nur für Addition mod 113). Das ist korrigiert. Dazu zwei neue Abbildungen (Abb. 9 zu K5, Abb. 10 zur Beschleunigung) und ein vorbereitetes Zenodo-Paket (nicht hochgeladen, Autorschaft und Lizenz entscheidest du).

## Was das bedeutet und was nicht

- Es heißt: Eine unserer Deutungen („die erste Näherung erklärt wenig“) war zu stark. Bei Adam steckt ein Teil davon im Optimierer, nicht in der Veraltung des Gradienten. Wir haben das gefunden, bevor es als Ergebnis ins Paper ging.
- Es heißt nicht, dass K2 (Datenauswahl steuert Frequenzen) falsch ist. Ob K2 auch mit Minibatches gilt, ist offen. Das prüft L0. Jeder Ausgang ist ein Ergebnis.

## Drei Fragen, die eine Jury stellen könnte

1. **„Ihr trainiert immer mit allen Daten auf einmal. Gilt euer Ergebnis auch so, wie man normalerweise trainiert?“**
   Bisher wissen wir es nicht. Genau deshalb rechnen wir jetzt L0 mit Minibatches (zwei Batchgrößen und ein anderer Optimierer). Hält die Steuerung dort, ist sie robuster. Gewinnt die Reihenfolge, zeigt das, wann Datenauswahl nicht reicht.
2. **„Was ist ein Vorzeichenschritt, und warum ist er wichtig?“**
   Adam teilt jede Änderung durch ihre eigene Größe. Bleibt der Gradient gleich, geht jede Zahl immer um genau denselben Betrag nach oben oder unten. Das verwischt die Frequenzmuster ein wenig („Energie streut auf andere Frequenzen“). Das ist ein Effekt des Optimierers, nicht der Daten, und muss man beim Deuten auseinanderhalten.
3. **„Woher wisst ihr, dass ihr euch das nicht nachträglich zurechtgelegt habt?“**
   Bei jeder Nachauswertung wurde die Lesart vorher im Skript festgelegt und mit Zeitstempel in git gespeichert. Die Zahlen hat ein zweites, unabhängiges Programm nachgerechnet. Heute hat diese Nachprüfung auch eine zu schwache Stelle gefunden (Toleranzabhängigkeit), und wir haben die Aussage deshalb zurückgenommen.

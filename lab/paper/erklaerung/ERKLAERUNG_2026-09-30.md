---
id: ERKLAERUNG_2026-09-30
datum: 2026-09-30
tags: [lab/erklaerung]
---
# Erklärung für den 30.09.2026 (angelegt in Sitzung 54 am 29.09. um 23:36, vor den Nachtergebnissen)

Zurück zu [[LAB]] · [[FINDINGS]] · [[paper/STATUS]] · Vortag [[paper/erklaerung/ERKLAERUNG_2026-09-29]]

## Was wir vorher erwarten (festgehalten, damit man später vergleichen kann)

1. **Nachrechnung LM1-F:** Ein zweites, unabhängig geschriebenes Programm rechnet die Lösch-Tests an den 20 Sprachmodellen nach. Wir erwarten dieselben Zahlen (das erste Modell stimmt schon überein). Weicht etwas ab, klären wir das zuerst, bevor der Satz ins Paper kommt.
2. **EXP-121 (flacher Zufallsdatensatz im Sprachmodell):** Jede Zahl kommt gleich oft vor, aber die Paare betonen keine Frequenzen. Unsere Vermutung (unsicher): Das Modell lernt die Trainingsfakten, bleibt bei ungesehenen Fakten aber hängen wie der gewöhnliche Zufallsdatensatz in EXP-119. Dann wäre es die *Auswahl der Paare*, nicht die Häufigkeit der Zahlen, die das schnelle Verallgemeinern ermöglicht. Genauso möglich: Schon die gleichmäßige Bauart hilft. Beides ist ein Ergebnis.
3. **EXP-116 (nur ≈ 9 % Rechentext):** Offen, ob das Modell die Fakten bei so wenig Rechentext in 16 000 Schritten überhaupt lernt. Lernt es sie nicht, sagt das nichts gegen die Steuerung, nur etwas über das Budget.

## Was heute herauskam

*(wird ergänzt, sobald Ergebnisse vorliegen)*

## Drei Fragen, die eine Jury stellen könnte

1. **„Warum ist ein Datensatz mit gleich häufigen Zahlen wichtig?“** – Unsere konstruierten Datensätze betonen die Zielfrequenzen auch darüber, wie oft jede Zahl vorkommt. Ein Sprachmodell könnte einfach diese Häufigkeiten lernen. Mit gleich häufigen Zahlen bleibt nur die Auswahl der Paare als Unterschied.
2. **„Was heißt Plateau?“** – Das Modell kann alle Trainingsfakten, bei ungesehenen liegt es aber lange bei etwa 30 % und wird kaum besser. Beim Grokking kommt nach so einem Plateau irgendwann der Sprung. Ob er beim Zufallsdatensatz noch käme, wissen wir nicht, weil wir nach 6000 Schritten aufgehört haben.
3. **„Warum rechnet ein zweites Programm alles nach?“** – Damit ein Programmierfehler nicht unbemerkt das Ergebnis macht. Das zweite Programm ist unabhängig geschrieben und nutzt keinen Code des ersten.

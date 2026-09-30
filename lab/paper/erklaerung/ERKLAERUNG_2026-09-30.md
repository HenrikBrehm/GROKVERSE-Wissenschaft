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

- **LM1-F (Nachrechnung):** Das zweite Programm kommt auf dieselben Zahlen (bis auf 0,00000002). Erwartung 1 hat gestimmt.
- **EXP-121 (Sitzung 55, 01:07):** Erwartung 2 hat *nicht* gestimmt. Der Zufallsdatensatz mit gleich häufigen Zahlen bleibt nicht hängen. Nach dem Auswendiglernen dauert es 223 bzw. 570 Schritte, bis er auch ungesehene Fakten kann; der gewöhnliche Zufallsdatensatz aus EXP-119 schaffte das in über 3900 Schritten nicht. Er kann auch Aufgaben ohne gesehenes Tauschpaar (68 % bzw. 98 %). Bedeutung: Die besondere Paarauswahl ist nicht nötig, um das Plateau zu verlassen. Was den gewöhnlichen Zufallsdatensatz festhält (ungleich häufige Zahlen oder ungleichmäßige Paare), ist offen. Das sind nur 2 Läufe mit anderen Seeds, also ein Hinweis, kein Beweis. Vorab-Urteil: „unklar“.
- **Korrektur (01:11):** Der „flache Zufallsdatensatz“ war weniger zufällig als gedacht. Seine Bauart erzeugt im Spektrum trotzdem ein paar starke Spitzen, nur an zufälligen Stellen, fast so stark wie bei unseren konstruierten Datensätzen. Der gewöhnliche Zufallsdatensatz hat keine solche Spitze. Neue, vorsichtige Lesart: Um das Plateau zu verlassen, braucht es *irgendeine* Spitze, egal wo; die ungleich häufigen Zahlen sind es nicht. Das ist nachträglich abgelesen und nicht direkt getestet.
- **Literatur (01:00):** Das Muster „nur Tauschpaare richtig“ ist bekannt, aber aus einem Netz, das die beiden Zahlen einfach addiert und deshalb die Vertauschung schon eingebaut hat (He et al. 2026). Unser Transformer muss sie erst lernen. Die Jury-Antwort unten ist damit schärfer: *bekannt* ist das Muster, *nicht gefunden* haben wir es als gelernte erste Stufe und als Stelle, an der die Datenauswahl wirkt.
- **EXP-123 (02:47):** Mit Zufallsdaten lernt der Transformer vor dem Grokking zuerst die Vertauschungsregel, in allen 18 auswertbaren Einheiten (vorher festgelegt). Erst spät und steil kommen die übrigen Aufgaben. *Nicht* bestätigt hat sich meine Vermutung, dass unsere konstruierten Daten vor allem diesen zweiten Schritt beschleunigen: Sie beschleunigen beide, den ersten (Vertauschung) sogar stärker (etwa 11-fach gegen 5-fach). Der Pilot hatte das verdeckt, weil er in Anteilen der Gesamtzeit gemessen hat.

## Drei Fragen, die eine Jury stellen könnte

0. **„Ihr habt euch heute zweimal korrigiert. Ist das nicht schlecht?“** – Nein. Beide Korrekturen kamen, weil wir die Daten genauer angesehen haben (Aufteilung nach Tauschpaar, Spektrum der Datensätze). Wir schreiben den alten und den neuen Stand auf, damit man sieht, was vorher erwartet war.

1. **„Warum ist ein Datensatz mit gleich häufigen Zahlen wichtig?“** – Unsere konstruierten Datensätze betonen die Zielfrequenzen auch darüber, wie oft jede Zahl vorkommt. Ein Sprachmodell könnte einfach diese Häufigkeiten lernen. Mit gleich häufigen Zahlen bleibt nur die Auswahl der Paare als Unterschied.
2. **„Was heißt Plateau?“** – Das Modell kann alle Trainingsfakten, bei ungesehenen liegt es aber lange bei etwa 30 % und wird kaum besser. Beim Grokking kommt nach so einem Plateau irgendwann der Sprung. Ob er beim Zufallsdatensatz noch käme, wissen wir nicht, weil wir nach 6000 Schritten aufgehört haben.
3. **„Warum rechnet ein zweites Programm alles nach?“** – Damit ein Programmierfehler nicht unbemerkt das Ergebnis macht. Das zweite Programm ist unabhängig geschrieben und nutzt keinen Code des ersten.

**Nachtrag (30.09., 00:10, Sitzung 54): Kommutativität vor dem Grokking.** Mit zufälligen Trainingsdaten lernt das Netz zuerst nur die Vertauschungsregel: Wenn es „b + a“ gesehen hat, beantwortet es auch „a + b“. Alle anderen ungesehenen Aufgaben kann es erst später. Das gilt im Sprachmodell (dort bleibt es sogar dabei stehen) und, wie sich um Mitternacht zeigte, auch im kleinen Spielzeugmodell kurz vor dem Grokking (4 von 4 Läufen, vorher festgelegt). Mit unseren konstruierten Daten kommt die zweite Stufe viel früher. *Ehrlich:* Um 23:43 hatte ich aus der Gesamtkurve geschlossen, das Spielzeugmodell habe keine solche Phase. Das war falsch; erst die Aufteilung nach „Tauschpaar gesehen ja/nein“ zeigte es. *Jury-Frage:* „Ist das nicht bekannt?“ – Dass Kommutativität beim Grokking hilft, ist bekannt (z. B. beschleunigt es, beide Reihenfolgen zu zeigen). Eine Messung, dass die Genauigkeit vor dem Grokking fast nur aus dieser Regel besteht, haben wir bei unserer Suche nicht gefunden (vorläufig, Volltexte noch prüfen).

4. **„Warum ist die Vertauschungsregel leichter als die Addition?“** – Um „a + b“ richtig zu beantworten, wenn man „b + a“ schon kennt, muss das Netz nur lernen, dass die Reihenfolge der beiden Zahlen egal ist; es kann dann die gelernte Antwort wiederverwenden. Für wirklich neue Paare muss es die Rechenregel selbst finden (bei uns über Fourier-Frequenzen). Bei Netzen, die die beiden Zahlen einfach addieren, ist die Vertauschung schon eingebaut (He et al. 2026); unser Transformer kennt die Reihenfolge der Eingaben und muss sie erst ignorieren lernen.

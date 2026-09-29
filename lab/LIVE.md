---
tags: [lab/live]
---
# LIVE: Laborsitzung 54

- **Sitzungsstart:** 2026-09-29 22:09 Berlin (20:09Z, vom Runner)
- **Deadline:** 2026-09-30 01:09 Berlin (23:09Z)
- **Zuletzt aktualisiert:** 00:44 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet (00:44).** Nächster geplanter Start laut Runner: 30.09. 01:44 Berlin. Der GPU-Dienst rechnet weiter: EXP-113-Rest, EXP-116, EXP-121 (wartet auf Speicher).

## Als Nächstes

Anhang-J-Absätze prüfen lassen; EXP-121 auswerten → LM2 entscheiden; EXP-116/113 auswerten; N57-Nachfolger festlegen.

## Dienst (00:09)

LM1-F-Nachrechnung 12/20; EXP-113 3/8 fertig (2 laufen); EXP-116 1 läuft; EXP-121 wartet auf Grafikspeicher.

## Verlauf dieser Sitzung

- 00:43 **LM1-F unabhängig nachgerechnet: identisch.** Satz im Paper-Anhang J eingesetzt.
- 00:18 Code-Prüfung EXP-122: kein Fehler; nur das Tauschpaar hilft, andere Nachbarn nicht.
- 00:08 **EXP-122:** Auch das Spielzeugmodell lernt vor dem Grokking zuerst die Vertauschungsregel (4/4 Läufe); konstruierte Splits ziehen die übrigen Aufgaben früher mit. Mein „erster Blick“ von 23:43 war falsch.
- 23:41 **Plateau = Kommutativität:** Das Sprachmodell mit Zufallsdaten beantwortet nur ungesehene Fakten richtig, deren gespiegeltes Paar (b, a) es gelernt hat (99 % gegen 3 %). Es hat „a + b = b + a“ gelernt, nicht die Addition.
- 23:33 EXP-121 festgelegt und eingereiht (flacher Zufallsarm: trennt Paarstruktur von Zahl-Häufigkeit). Anhang-J-Sätze zu EXP-119/120 nach unabhängiger Prüfung korrigiert.
- 23:26 **EXP-119:** Im Sprachmodell lernt ein Zufallssplit die Trainingsfakten gleich schnell, generalisiert aber nicht (Lücke ≥ 3900 Schritte); konstruierte Splits generalisieren sofort. Meine vorab formulierte Erklärung war falsch.
- 23:20 EXP-120 (Ein- vs. Ausgabeseite im LM): vorab „unklar“; Eingabe allein trägt die volle Wirkung, Ausgabe teilweise.
- 22:51 **LM1-F bestätigt**: Das Sprachmodell nutzt die gesteuerten Frequenzen (10/10 Seeds). Nachrechnung eingereiht.
- 22:35 Anhänge F und H logisch geprüft (10 kleine Punkte, u. a. veraltetes „R4 is pending“); alle Anhänge jetzt einmal geprüft.
- 22:25 Anhänge B, E, G logisch geprüft: 1 Richtungsfehler in der Theorie (MLP: M0 gegen M0c vertauscht) und 13 kleinere Punkte korrigiert; committed.
- 22:20 Anhang A: 3 Logikpunkte eingearbeitet (Zahlen nachgerechnet), 1 Fehlalarm verworfen; committed.
- 22:10 Stand gelesen, Dienst läuft ohne Fehler.

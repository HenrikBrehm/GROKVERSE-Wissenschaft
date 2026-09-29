---
tags: [lab/live]
---
# LIVE: Laborsitzung 54

- **Sitzungsstart:** 2026-09-29 22:09 Berlin (20:09Z, vom Runner)
- **Deadline:** 2026-09-30 01:09 Berlin (23:09Z)
- **Zuletzt aktualisiert:** 23:31 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Ein Prüfagent kontrolliert die neuen Paper-Sätze zu EXP-119/120. LM1-F-Nachrechnung läuft (≈ 15 min je Modell).

## Als Nächstes

Prüfergebnis einarbeiten; danach LM2 (flache Splits gegen Zufallsgegenstück im LM) als Versuch festlegen.

## Dienst (22:10)

LM1-F 12/20 Modelle; EXP-119 3/6 fertig, 2 laufen; EXP-113 2/8, 1 läuft; EXP-116 0/4.

## Verlauf dieser Sitzung

- 23:26 **EXP-119:** Im Sprachmodell lernt ein Zufallssplit die Trainingsfakten gleich schnell, generalisiert aber nicht (Lücke ≥ 3900 Schritte); konstruierte Splits generalisieren sofort. Meine vorab formulierte Erklärung war falsch.
- 23:20 EXP-120 (Ein- vs. Ausgabeseite im LM): vorab „unklar“; Eingabe allein trägt die volle Wirkung, Ausgabe teilweise.
- 22:51 **LM1-F bestätigt**: Das Sprachmodell nutzt die gesteuerten Frequenzen (10/10 Seeds). Nachrechnung eingereiht.
- 22:35 Anhänge F und H logisch geprüft (10 kleine Punkte, u. a. veraltetes „R4 is pending“); alle Anhänge jetzt einmal geprüft.
- 22:25 Anhänge B, E, G logisch geprüft: 1 Richtungsfehler in der Theorie (MLP: M0 gegen M0c vertauscht) und 13 kleinere Punkte korrigiert; committed.
- 22:20 Anhang A: 3 Logikpunkte eingearbeitet (Zahlen nachgerechnet), 1 Fehlalarm verworfen; committed.
- 22:10 Stand gelesen, Dienst läuft ohne Fehler.

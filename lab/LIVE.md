---
tags: [lab/live]
---
# LIVE: Laborsitzung 54

- **Sitzungsstart:** 2026-09-29 22:09 Berlin (20:09Z, vom Runner)
- **Deadline:** 2026-09-30 01:09 Berlin (23:09Z)
- **Zuletzt aktualisiert:** 23:33 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Zenodo-Paket: LM1-F-Skripte ergänzt, Trockenlauf läuft. Dienst: EXP-113-Rest, EXP-116, LM1-F-Nachrechnung (5/20); EXP-121 wartet auf Grafikspeicher.

## Als Nächstes

Nächste Sitzung: LM1-F-Nachrechnung vergleichen → Paper-Satz; EXP-121 auswerten → über LM2 entscheiden; EXP-116/113 auswerten.

## Dienst (23:33)

LM1-F-Nachrechnung 5/20; EXP-113 5/8 fertig, 2 laufen; EXP-116 1 läuft; EXP-119 fertig; EXP-121 (2 Läufe) wartet.

## Verlauf dieser Sitzung

- 23:33 EXP-121 festgelegt und eingereiht (flacher Zufallsarm: trennt Paarstruktur von Zahl-Häufigkeit). Anhang-J-Sätze zu EXP-119/120 nach unabhängiger Prüfung korrigiert.
- 23:26 **EXP-119:** Im Sprachmodell lernt ein Zufallssplit die Trainingsfakten gleich schnell, generalisiert aber nicht (Lücke ≥ 3900 Schritte); konstruierte Splits generalisieren sofort. Meine vorab formulierte Erklärung war falsch.
- 23:20 EXP-120 (Ein- vs. Ausgabeseite im LM): vorab „unklar“; Eingabe allein trägt die volle Wirkung, Ausgabe teilweise.
- 22:51 **LM1-F bestätigt**: Das Sprachmodell nutzt die gesteuerten Frequenzen (10/10 Seeds). Nachrechnung eingereiht.
- 22:35 Anhänge F und H logisch geprüft (10 kleine Punkte, u. a. veraltetes „R4 is pending“); alle Anhänge jetzt einmal geprüft.
- 22:25 Anhänge B, E, G logisch geprüft: 1 Richtungsfehler in der Theorie (MLP: M0 gegen M0c vertauscht) und 13 kleinere Punkte korrigiert; committed.
- 22:20 Anhang A: 3 Logikpunkte eingearbeitet (Zahlen nachgerechnet), 1 Fehlalarm verworfen; committed.
- 22:10 Stand gelesen, Dienst läuft ohne Fehler.

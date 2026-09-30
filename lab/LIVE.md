---
tags: [lab/live]
---
# LIVE: Laborsitzung 61

- **Sitzungsstart:** 2026-09-30 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-30 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 16:29 Berlin (gemessen)

## Gerade

- **Hinweis für den Nutzer (16:29):** Die zwei fertigen Pythia-Läufe (EXP-127, Seed 4000; Ergebnisse vollständig gespeichert) hängen beim Beenden seit 15:44/15:49 gestarteten Prozessen (PIDs 24416→19156 und 28528→31860) und halten ≈ 10 GB Grafikspeicher; der Dienst startet deshalb die nächsten Läufe nicht. Mein Beenden per `taskkill` wurde von der Sicherheitsprüfung abgelehnt – ich umgehe das nicht. Falls sie nicht von selbst enden: bitte diese zwei Prozessbäume beenden.

- Beobachte den Pythia-Piloten EXP-127: Lauf 1 von 4 fertig (Testgenauigkeit 0.99). Erste Beobachtung, noch keine Auswertung: Das Wegnehmen der eigenen Zielfrequenzen schadet hier nicht, das Wegnehmen einiger vortrainierter Frequenzen (z. B. 2, 23) schon. Die Auswertung folgt, wenn alle 4 Läufe fertig sind (≈ 17:10).
- LM3-F-Funktionstest läuft weiter (CPU).

## Als Nächstes

1. EXP-127 auswerten (nach der Vorab-Lesart im README). 2. LM3-F auswerten, sobald fertig.

## Verlauf dieser Sitzung

- 16:29 Pythia Seed 4000 F/G fertig (Test 0.987/0.974); Prozesse hängen beim Beenden, Beenden abgelehnt.
- 16:25 EXP-130 (Ablation jeder einzelnen Frequenz im nachtrainierten Pythia) vorbereitet, CPU-Smoke läuft.
- 16:21 Pythia-Lauf 1/4 fertig (Seed 4000, Split F).
- 16:06 R12 im Paper fertig (Abstract geprüft: alle Zahlen richtig), committet.
- 16:04 Abstract neu: R12 („auch Addition mod 97 und Multiplikation mod 113: 4.5–7.4× schneller“), an anderer Stelle gekürzt.
- 16:03 Tabelle 1 um R12, LM1, LM1-F, LM3 ergänzt (aus den eingefrorenen Manifesten erzeugt).
- 16:01 Abbildung zu R12 erzeugt (`fig16`), Beschriftung auf Englisch.
- 16:01 Start: STATE, JOURNAL, Dienst geprüft.

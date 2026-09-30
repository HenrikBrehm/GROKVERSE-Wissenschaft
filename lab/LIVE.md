---
tags: [lab/live]
---
# LIVE: Laborsitzung 57

- **Sitzungsstart:** 2026-09-30 05:50 Berlin (03:50Z, vom Runner)
- **Deadline:** 2026-09-30 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 08:25 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet (08:25).** Nächster geplanter Start laut Runner: 30.09. 09:24 Berlin (2026-09-30T07:24Z). Der GPU-Dienst rechnet LM3, R12 und danach EXP-125 weiter.

## Als Nächstes

1. Paper: LM1/LM1-F ins Abstract und in den Haupttext (Nutzerentscheidung 30.09.), unabhängig prüfen. 2. LM3 (≈ 16 Uhr) und R12 (≈ abends) auswerten, Deutungssätze liegen bereit. 3. EXP-126-Satz ins Paper.

## Dienst (07:17)

LM3 2/20 fertig; EXP-126 4/16; R12 13/200 (pausiert hinter EXP-126); EXP-125 wartet.

## Verlauf dieser Sitzung

- 08:25 EXP-126 endgültig: SGD lernt bei 0.05 in 0 von 8 Läufen, divergiert bei 0.1 in 8 von 8 → „nicht auswertbar“.

- 07:59 **EXP-126 fertig entschieden: „nicht auswertbar“** – SGD lernt bei 0.05 nichts und divergiert bei 0.1. Beschreibend: der einzige lernende Lauf folgte der Datenauswahl (92 % der Energie auf den Zielen).

- 07:17 EXP-126 Zwischenstand: Mit SGD bei Lernrate 0.05 lernt das Netz in 20 000 Schritten gar nichts (4 von 4 fertigen Läufen). Lernrate 0.1 läuft jetzt.

- 06:35 EXP-126 vorab festgelegt und eingereiht (SGD statt Adam, 4 Seeds, lr 0.05/0.1).

- 06:32 Paper Anhang K: ein geprüfter Satz dazu (Vertauschungsstufe bei ähnlicher Frequenz-Konzentration in allen Datensätzen; eher Fortschrittsmarker als Ursache).
- 06:31 Nachträglich (Lesart vorab): Die Frequenz-Konzentration hängt innerhalb eines Datensatztyps eng an der Generalisierung, weniger an der Vertauschungsstufe.
- 06:27 Erklärung für morgen mit Erwartungen vorab angelegt (LM3, R12, EXP-125).
- 06:26 **Ausgeschlossen:** Konstruierte Daten lernen die Vertauschungsregel nicht deshalb früher, weil sie mehr gespiegelte Paare enthalten (alle ≈ 30 %).
- 06:22 R12-Abbildung und unabhängige Nachrechnung vorbereitet (vor jedem Ergebnis); Literatur nachgesucht (nichts Einschränkendes).

- 06:12 **EXP-125 eingereiht:** Hält die Steuerung auch in einem ≈ 2× größeren Sprachmodell (≈ 29.5 M Parameter)? 2 Seeds, startet nach LM3.
- 06:06 **R12 eingefroren und gestartet** (200 Läufe): Beschleunigen konstruierte Daten das Grokking auch bei Addition mod 97 und Multiplikation mod 113? Deutungssätze vorab festgelegt.
- 06:05 Smoke (je ein echter Lauf je Aufgabe) durch die Auswertung: grün. Codeprüfung durch unabhängigen Agenten: keine Blocker.
- 05:54 R12-Code (`confirm_r12.py`) geschrieben, Selbsttest grün; Splits offline geprüft (Zielanteil konstruiert 0.18–0.20, Kontrolle 0.09–0.11).
- 05:50 Stand gelesen; LM3 läuft, GPU hat Platz für kleine Läufe.

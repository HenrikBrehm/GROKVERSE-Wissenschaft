---
tags: [lab/live]
---
# LIVE: Laborsitzung 57

- **Sitzungsstart:** 2026-09-30 05:50 Berlin (03:50Z, vom Runner)
- **Deadline:** 2026-09-30 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 06:27 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Läufe beobachten; Denkarbeit an gespeicherten Daten, während R12/LM3 rechnen.

## Als Nächstes

R12 auswerten, sobald 200/200 fertig (bei jetzigem Tempo ≈ 0.27 Läufe/min eher am Abend; schneller, wenn LM3 fertig ist ≈ 16 Uhr). LM3 auswerten, sobald 20/20 fertig.

## Dienst (06:27)

LM3 2/20 fertig (3 laufen, ≈ 95 min je Lauf); R12 6/200 (4 laufen); EXP-125 wartet auf Speicher (Anmeldung auf 6 GB gesenkt).

## Verlauf dieser Sitzung

- 06:27 Erklärung für morgen mit Erwartungen vorab angelegt (LM3, R12, EXP-125).
- 06:26 **Ausgeschlossen:** Konstruierte Daten lernen die Vertauschungsregel nicht deshalb früher, weil sie mehr gespiegelte Paare enthalten (alle ≈ 30 %).
- 06:22 R12-Abbildung und unabhängige Nachrechnung vorbereitet (vor jedem Ergebnis); Literatur nachgesucht (nichts Einschränkendes).

- 06:12 **EXP-125 eingereiht:** Hält die Steuerung auch in einem ≈ 2× größeren Sprachmodell (≈ 29.5 M Parameter)? 2 Seeds, startet nach LM3.
- 06:06 **R12 eingefroren und gestartet** (200 Läufe): Beschleunigen konstruierte Daten das Grokking auch bei Addition mod 97 und Multiplikation mod 113? Deutungssätze vorab festgelegt.
- 06:05 Smoke (je ein echter Lauf je Aufgabe) durch die Auswertung: grün. Codeprüfung durch unabhängigen Agenten: keine Blocker.
- 05:54 R12-Code (`confirm_r12.py`) geschrieben, Selbsttest grün; Splits offline geprüft (Zielanteil konstruiert 0.18–0.20, Kontrolle 0.09–0.11).
- 05:50 Stand gelesen; LM3 läuft, GPU hat Platz für kleine Läufe.

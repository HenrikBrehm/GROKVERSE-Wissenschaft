---
tags: [lab/live]
---
# LIVE: Laborsitzung 57

- **Sitzungsstart:** 2026-09-30 05:50 Berlin (03:50Z, vom Runner)
- **Deadline:** 2026-09-30 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 06:12 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- R12 und LM3 rechnen beim GPU-Dienst; ein Agent schreibt die unabhängige R12-Nachrechnung. Ich prüfe die Literatur zu „Datenauswahl beschleunigt Grokking“ auf neue Arbeiten seit dem 27.09.

## Als Nächstes

Nachrechnung prüfen; Dienst beobachten; R12 auswerten, sobald 200/200 fertig (grob am Nachmittag).

## Dienst (06:12)

LM3 2/20 fertig (3 laufen); R12 1/200 (4 laufen, ≈ 6–9 min je Lauf); EXP-125 (größeres Sprachmodell, 4 Läufe) wartet auf Speicher.

## Verlauf dieser Sitzung

- 06:12 **EXP-125 eingereiht:** Hält die Steuerung auch in einem ≈ 2× größeren Sprachmodell (≈ 29.5 M Parameter)? 2 Seeds, startet nach LM3.
- 06:07 **R12 eingefroren und gestartet** (200 Läufe): Beschleunigen konstruierte Daten das Grokking auch bei Addition mod 97 und Multiplikation mod 113? Deutungssätze vorab festgelegt.
- 06:05 Smoke (je ein echter Lauf je Aufgabe) durch die Auswertung: grün. Codeprüfung durch unabhängigen Agenten: keine Blocker.

- 05:54 R12-Code (`confirm_r12.py`) geschrieben, Selbsttest grün; Splits offline geprüft (Zielanteil konstruiert 0.18–0.20, Kontrolle 0.09–0.11).
- 05:50 Stand gelesen; LM3 läuft, GPU hat Platz für kleine Läufe.

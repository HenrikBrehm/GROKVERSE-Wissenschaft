---
tags: [lab/live]
---
# LIVE: Laborsitzung 53

- **Sitzungsstart:** 2026-09-29 19:29 Berlin (17:29Z, vom Runner)
- **Deadline:** 2026-09-29 22:29 Berlin (20:29Z)
- **Zuletzt aktualisiert:** 20:00 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **Eigenen Fehler gefunden:** Die Erklärung „Rückgang von Δ_pow bei flachen Splits = Verdünnung“ (Sitzung 52) kann nicht stimmen: Δ_pow ist ein Verhältnis eigene/fremde Zielenergie, andere Frequenzen ändern es nicht. Der Rückgang kommt daher, dass die Ziele des *anderen* Arms schneller wachsen. Unabhängige Nachrechnung läuft, danach Korrektur in Paper und Notizen.

## Als Nächstes

LM1 20/20 → `confirm_lm1.py --analyze` → unabhängige Nachrechnung → LM1-F als Dienst-Job.

## Dienst (19:30)

LM1 15/20, R4-Repro 134/240, EXP-119 0/6, EXP-113 2/8, EXP-116 0/4; Speicher 15.5/16 GB gebucht.

## Verlauf dieser Sitzung

- 19:58 Fehler in der Deutung von EXP-115 gefunden (s. o.).
- 19:40 Manuskript: veraltete Abbildungsverweise korrigiert (Generator), committet.
- 19:32 Start, Lage geprüft.

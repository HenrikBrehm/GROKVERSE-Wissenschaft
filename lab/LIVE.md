---
tags: [lab/live]
---
# LIVE: Laborsitzung 50

- **Sitzungsstart:** 2026-09-29 11:30 Berlin (09:30Z, vom Runner)
- **Deadline:** 2026-09-29 14:29 Berlin (12:29Z)
- **Zuletzt aktualisiert:** 14:00 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Hinweis (14:00): erledigt

Der GPU-Dienst wurde neu gestartet; die gesenkten Einstellungen greifen (LM1 2, EXP-115 1, EXP-113 2 Worker). GPU-Speicher jetzt 13.2 GB, kaum Auslagerung (0.8 GB), 15.5 GB RAM frei. Danke!

## Gerade

- **Sitzung beendet.** Nächster geplanter Start laut Runner: 15:04 Berlin (13:04Z). Der GPU-Dienst rechnet nach seinem Neustart wieder normal weiter.

## Als Nächstes

Dienst-Lage prüfen; nach einem DRAIN-Neustart LM1 (10 frische Seeds, Sprachmodell) und EXP-115 abwarten und auswerten; R4-Repro vergleichen.

## Verlauf dieser Sitzung

- 13:51 Sitzungsende; Abbildungsverweise im Paper ergänzt, Anhang K aktualisiert.
- 13:20 Stillstand der LM-Läufe durch GPU-Speicher-Überbuchung; Abbruch eigener Läufe abgelehnt; Nutzer um DRAIN gebeten.
- 12:54 EXP-115 (flache Zahl-Häufigkeiten im LM) festgelegt und eingereiht.
- 12:52 Korrektur: auch im Spielzeugmodell kommt die Steuerung mit dem Auswendiglernen (post hoc, 50 Seeds).
- 12:39 **LM1 eingefroren** (nach unabhängiger Prüfung, 6 Punkte übernommen) und 20 Läufe eingereiht.
- 12:28 **EXP-114: Verdünnung nicht gestützt**; aber: lernt das LM die Fakten, steuert die Auswahl deutlich (Δ_pow 5.6, zurückgehaltene Fakten 0.98; 1 Seed).
- 12:09 EXP-114 (79 % Rechensätze): Lauf F lernt die Fakten schon bei Schritt 2000 (Training 0.80, zurückgehalten 0.33); EXP-113 (34 %) bei Schritt 6500 noch auf Zufall.
- 11:49 EXP-114 vorab festgelegt (Lesarten + Auswertecode vor dem Lauf) und eingereiht.
- 11:46 Zweite unabhängige Prüfung eingearbeitet (Abb. 4: falsche Mindesteffekt-Linie entfernt).
- 11:46 Auswertecode für H-folgt vor dem Ergebnis geschrieben und an Pilotdaten getestet.
- 11:43 LM-Checkpoints angesehen: bis Schritt 4000 keine Steuerung (Δ_pow ≈ 0); Vorhersage „H-folgt“ vorab festgelegt.
- 11:41 Nachauswertung N54b: kleine Päckchen verschieben das Festlege-Fenster, verbreitern es nicht (Exploration).
- 11:39 Literatur-Nachsuche: nichts Vorwegnehmendes; Khanh 2026b als Grenze zitiert.
- vor 11:39 Kurzfassung 4 944 → ≈ 4 300 Wörter, unabhängig geprüft (9 Korrekturen); Abb. 4 neu (L0 + N54b); Tabelle 1 um R10/R11/L0/N54b ergänzt.
- 11:33 Lage geprüft (kein STOP, Fenster offen, Dienst läuft).

---
tags: [lab/live]
---
# LIVE: Laborsitzung 56

- **Sitzungsstart:** 2026-09-30 03:30 Berlin (01:30Z, vom Runner)
- **Deadline:** 2026-09-30 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 03:48 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Nächste Sprosse der Sprachmodell-Leiter vorbereitet (LM3: Steuerung bei nur ≈ 9 % Rechensätzen, 10 frische Seeds, dazu der Funktionstest LM3-F). Smoke grün; ein unabhängiger Agent prüft Code und Design. Eingefroren wird erst nach dem EXP-116-Ergebnis.

## Als Nächstes

EXP-113 (letzter Lauf bei 11 500/16 000) und EXP-116 (zwei Läufe bei 9750/16 000) auswerten, sobald fertig (≈ 04:20–04:30); danach LM3 einfrieren und beim Dienst einreihen.

## Dienst (03:48)

EXP-113: 7/8 fertig, 1 läuft. EXP-116: 2/4 fertig, 2 laufen (beide lernen jetzt, Test 0.31/0.39). EXP-119 Nachtrag 2 wartet auf Grafikspeicher.

## Verlauf dieser Sitzung

- 03:48 LM3 vorbereitet (Code, Splits, Smoke, Selbsttest).
- 03:40 Haupttext vor Donnerstag unabhängig geprüft: 10 Punkte, u. a. D59 „nach dem Grokking“ galt nur für 17/20 Seeds, Batch-16-Zahlen waren falsch zugeordnet; alles korrigiert.
- 03:35 Anhang K: Kopfzeile neu, langer Absatz in fünf geteilt, unabhängig geprüft; 5 Korrekturen übernommen (u. a. eine Überdehnung: konstruierte Splits verkürzen beide Stufen, nicht nur die erste).
- 03:34 Billigen Spielzeugtest „beliebige Spektralspitze“ verworfen: Die R5-Arme beantworten ihn schon.
- 03:32 Stand gelesen, Wächter erlaubt Läufe, Dienst läuft.

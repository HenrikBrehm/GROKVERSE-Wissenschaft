---
tags: [lab/live]
---
# LIVE: Laborsitzung 56

- **Sitzungsstart:** 2026-09-30 03:30 Berlin (01:30Z, vom Runner)
- **Deadline:** 2026-09-30 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 05:47 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet (05:47).** Nächster geplanter Start laut Runner: 30.09. 07:04 Berlin (05:04Z). Der GPU-Dienst rechnet LM3 weiter.

## Als Nächstes

LM3 auswerten, sobald 20/20 fertig (≈ 14–15 Uhr): eingefrorene Auswertung, LM3-F, unabhängige Nachrechnung, dann Paper-Satz.

## Dienst (05:47)

LM3: 3 Läufe gleichzeitig, 0/20 fertig (die ersten beiden bei 13 750/15 000). Sonst nichts in der Warteschlange.

## Verlauf dieser Sitzung

- 05:46 LM1 zeigt den Rückgang nach dem Gipfel nicht (9/10 Seeds am Ende am höchsten).
- 05:45 **EXP-119-Langlauf „unklar“:** Zufallsdaten im Sprachmodell nach 16 000 Schritten bei 47 % (Grenze 50 %), das Plateau bröckelt langsam.
- 04:45 Literatur: eine Arbeit mit gegenteiligem Befund zum Verlustmodus gefunden (Lin et al. 2025) und im Paper abgegrenzt.
- 04:31 Nachträglich: Im Sprachmodell hat die Steuerung ihren Gipfel beim Lernbeginn und sinkt danach oft wieder (bleibt aber über 1).
- 04:29 Zwei zu starke Sätze im Paper entschärft (Verlustmodus; Abstract nur bei Lernrate 10⁻³).
- 04:24 **EXP-116: Steuerung auch bei nur ≈ 9 % Rechentext** (2 Seeds) → Bestätigungsblock LM3 eingefroren und gestartet (10 frische Seeds).
- 04:14 **EXP-113:** mit Antwort-Verlust gesteuert und verallgemeinert; mit Verlust auf allen Wörtern nur auswendig gelernt.
- 03:48 LM3 vorbereitet (Code, Splits, Smoke, Selbsttest).
- 03:40 Haupttext vor Donnerstag unabhängig geprüft: 10 Punkte, u. a. D59 „nach dem Grokking“ galt nur für 17/20 Seeds, Batch-16-Zahlen waren falsch zugeordnet; alles korrigiert.
- 03:35 Anhang K: Kopfzeile neu, langer Absatz in fünf geteilt, unabhängig geprüft; 5 Korrekturen übernommen (u. a. eine Überdehnung: konstruierte Splits verkürzen beide Stufen, nicht nur die erste).
- 03:34 Billigen Spielzeugtest „beliebige Spektralspitze“ verworfen: Die R5-Arme beantworten ihn schon.
- 03:32 Stand gelesen, Wächter erlaubt Läufe, Dienst läuft.

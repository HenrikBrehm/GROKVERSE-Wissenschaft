---
tags: [lab/live]
---
# LIVE: Laborsitzung 56

- **Sitzungsstart:** 2026-09-30 03:30 Berlin (01:30Z, vom Runner)
- **Deadline:** 2026-09-30 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 04:32 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Warte auf den Langlauf EXP-119 (Zufallsdaten im Sprachmodell, 16 000 Schritte: kommt das Grokking doch noch?), Ende ≈ 06:10. Auswertung und Paper-Satz sind vorbereitet.

## Als Nächstes

EXP-119 Nachtrag 2 auswerten; LM3 läuft bis etwa 17 Uhr (nächste Sitzungen werten aus).

## Dienst (04:32)

EXP-113 und EXP-116 fertig. Laufend: EXP-119 Nachtrag 2 (Schritt ≈ 3500/16 000) und LM3 (2 von 20 Läufen gleichzeitig, dann 3).

## Verlauf dieser Sitzung

- 04:31 Nachträglich: Im Sprachmodell hat die Steuerung ihren Gipfel beim Lernbeginn und sinkt danach oft wieder (bleibt aber über 1).
- 04:29 Zwei zu starke Sätze im Paper entschärft (Verlustmodus; Abstract nur bei Lernrate 10⁻³).
- 04:24 **EXP-116: Steuerung auch bei nur ≈ 9 % Rechentext** (2 Seeds) → Bestätigungsblock LM3 eingefroren und gestartet (10 frische Seeds).
- 04:14 **EXP-113:** mit Antwort-Verlust gesteuert und verallgemeinert; mit Verlust auf allen Wörtern nur auswendig gelernt.
- 03:48 LM3 vorbereitet (Code, Splits, Smoke, Selbsttest).
- 03:40 Haupttext vor Donnerstag unabhängig geprüft: 10 Punkte, u. a. D59 „nach dem Grokking“ galt nur für 17/20 Seeds, Batch-16-Zahlen waren falsch zugeordnet; alles korrigiert.
- 03:35 Anhang K: Kopfzeile neu, langer Absatz in fünf geteilt, unabhängig geprüft; 5 Korrekturen übernommen (u. a. eine Überdehnung: konstruierte Splits verkürzen beide Stufen, nicht nur die erste).
- 03:34 Billigen Spielzeugtest „beliebige Spektralspitze“ verworfen: Die R5-Arme beantworten ihn schon.
- 03:32 Stand gelesen, Wächter erlaubt Läufe, Dienst läuft.

---
tags: [lab/live]
---
# LIVE: Laborsitzung 52

- **Sitzungsstart:** 2026-09-29 16:50 Berlin (14:50Z, vom Runner)
- **Deadline:** 2026-09-29 19:49 Berlin (17:49Z)
- **Zuletzt aktualisiert:** 17:02 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Nachschauen, ob es in den gespeicherten Läufen schon einen Hinweis gibt, wie schnell Zufallssplits im Vergleich lernen (Erwartung für EXP-119).

## Als Nächstes

LM1 auswerten, sobald 20/20 fertig (Stand 16:50: 7/20) → unabhängige Nachrechnung → LM1-F. EXP-117 auswerten, sobald beide Läufe eines Seeds fertig sind.

## Dienst (16:50)

LM1 7/20 fertig, 2 laufen; EXP-117 1/4; R4-Repro 88/240; EXP-113-Rest und EXP-116 warten. Speicher 14.7 GB + 1.0 GB geteilt, Aufnahme wartet (Speicherschutz greift).

## Verlauf dieser Sitzung

- 17:02 EXP-119 festgelegt und beim Dienst eingereiht: Lernt das Sprachmodell Rechenfakten aus konstruierten Splits früher als aus zufälligen? (Übertragung der Hauptaussage R5; läuft nach LM1.)
- 16:56 EXP-115 zerlegt: Die Steuerung wird nach dem Lernen durch neue Frequenzen verdünnt, nicht verloren (Anhang K ergänzt).
- 16:53 Literaturliste: fehlende Autoren/Titel/URLs aus arXiv ergänzt (Janati et al., GrokTransfer).
- 16:52 Spielzeugmodell mit flachen Splits: Δ_pow fällt dort nach dem Gipfel NICHT ab → der Rückgang im Sprachmodell (EXP-115) ist vorläufig LM-spezifisch.
- 16:50 Start, Lage geprüft (kein STOP, Fenster offen, Dienst normal).

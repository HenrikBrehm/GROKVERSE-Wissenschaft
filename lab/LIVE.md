---
tags: [lab/live]
---
# LIVE: Laborsitzung 52

- **Sitzungsstart:** 2026-09-29 16:50 Berlin (14:50Z, vom Runner)
- **Deadline:** 2026-09-29 19:49 Berlin (17:49Z)
- **Zuletzt aktualisiert:** 17:39 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Warte auf EXP-117 Seed 3863 (läuft beim Dienst, ≈ 45 min je Lauf), dann Auswertung nach Vorab-Lesart. Zwischendurch Paper-Feinschliff nach dem Probe-Gutachten.

## Als Nächstes

LM1 auswerten, sobald 20/20 fertig (Stand 16:50: 7/20) → unabhängige Nachrechnung → LM1-F. EXP-117 auswerten, sobald beide Läufe eines Seeds fertig sind.

## Dienst (16:50)

LM1 7/20 fertig, 2 laufen; EXP-117 1/4; R4-Repro 88/240; EXP-113-Rest und EXP-116 warten. Speicher 14.7 GB + 1.0 GB geteilt, Aufnahme wartet (Speicherschutz greift).

## Verlauf dieser Sitzung

- 17:39 Paper: Fachkürzel und Versuchsnummern aus dem Haupttext entfernt, p-Werte an der Auflösungsgrenze als Schranke, Holm-Geltungsbereich genannt; Zahlen für die Wortlaut-Entscheidung „Festlegung nach 25–50 Schritten“ in paper/STATUS (Halbwert ≈ 31 Schritte).
- 17:35 EXP-117 (ungekoppelte Embeddings), erster Seed: Steuerung sitzt in der Eingabe-Repräsentation (Δ_in 6.44).
- 17:22 Simulierte Gutachter-Prüfung: 6/10, alle nachgeprüften Zahlen richtig; 7 Textpunkte übernommen, 6 Punkte für dich in paper/STATUS („Offen“), u. a. der genaue Wortlaut der Festlegungsaussage und die Nennung der GROKVERSE-Studie.
- 17:10 Unabhängige Prüfung eingearbeitet: mein Anhang-K-Satz war an zwei Stellen zu stark (korrigiert); Literaturliste um 9 Einträge ergänzt (Anhang wird jetzt mitgeprüft).
- 17:06 Im kleinen Sprachmodell gibt es keine Grokking-Lücke: zurückgehaltene Fakten werden fast gleichzeitig mit den Trainingsfakten gelernt (9 Läufe).
- 17:05 LaTeX-Fassung des Manuskripts für Overleaf erzeugt (ungetestet, kein TeX hier); FINDINGS ergänzt.
- 17:02 In gespeicherten Stufe-1-Läufen generalisieren konstruierte Splits 40/40, Zufallssplits 2/20 (Hinweis für EXP-119).
- 17:02 EXP-119 festgelegt und beim Dienst eingereiht: Lernt das Sprachmodell Rechenfakten aus konstruierten Splits früher als aus zufälligen? (Übertragung der Hauptaussage R5; läuft nach LM1.)
- ≈ 16:55 EXP-115 zerlegt: Die Steuerung wird nach dem Lernen durch neue Frequenzen verdünnt, nicht verloren (Anhang K ergänzt).
- 16:53 Literaturliste: fehlende Autoren/Titel/URLs aus arXiv ergänzt (Janati et al., GrokTransfer).
- 16:52 Spielzeugmodell mit flachen Splits: Δ_pow fällt dort nach dem Gipfel NICHT ab → der Rückgang im Sprachmodell (EXP-115) ist vorläufig LM-spezifisch.
- 16:50 Start, Lage geprüft (kein STOP, Fenster offen, Dienst normal).

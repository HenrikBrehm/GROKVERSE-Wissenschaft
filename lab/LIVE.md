---
tags: [lab/live]
---
# LIVE: Laborsitzung 52

- **Sitzungsstart:** 2026-09-29 16:50 Berlin (14:50Z, vom Runner)
- **Deadline:** 2026-09-29 19:49 Berlin (17:49Z)
- **Zuletzt aktualisiert:** 19:08 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Anhang-Buchstaben im generierten Manuskript lückenlos machen (A–K statt A–H, J, K, M), mit Verweisprüfung. Sitzungsende gegen 19:39.

## Als Nächstes

LM1 auswerten (eingefroren) → unabhängige Nachrechnung → LM1-F (Funktion). EXP-119 auswerten, sobald 6/6 fertig. Paper: deine Entscheidungen in paper/STATUS („Offen“), v. a. Wortlaut „Festlegung nach 25–50 Schritten“.

## Dienst (19:08)

LM1 13/20, R4-Repro 122/240, EXP-119 0/6, EXP-113 2/8, EXP-116 0/4. Speicherschutz arbeitet (Aufnahme wartet am 16-GB-Budget).

## Verlauf dieser Sitzung

- 19:08 KI-Offenlegung im Manuskript als eigener Abschnitt.
- 19:05 EXP-117 ausgewertet: „Eingabe gesteuert“ – auch mit getrennten Ein-/Ausgabe-Vektoren wird die Zahl-Darstellung selbst gesteuert (2 Seeds).
- 18:23 EXP-119 vor dem Start um eine beschreibende Zusatzgröße ergänzt (prägt auch ein Zufallssplit die Frequenzen des LM?).
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

---
tags: [lab/live]
---
# LIVE: Laborsitzung 61

- **Sitzungsstart:** 2026-09-30 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-30 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 17:29 Berlin (gemessen)

## Gerade

- **Hinweis für den Nutzer (17:29):** Auch die zwei Seed-4001-Läufe von EXP-127 (fertig ≈ 17:23, Ergebnisse gespeichert und ausgewertet) hängen beim Beenden (P-021); dahinter wartet EXP-130. Beenden bitte durch dich/deinen Assistenten, ich darf es nicht.
- **EXP-127 ausgewertet: „bricht“.** Beim Nachtrainieren des vortrainierten Pythia steuert die Faktenauswahl die Zahl-Einbettung nicht. Das Modell scheint stattdessen die Zahlfrequenzen zu nutzen, die es schon aus dem Vortraining hat (2, 3, 11, 23).
- EXP-130 (welche Frequenz braucht das Modell wirklich?) und EXP-131 (Zwischenschichten) sind vorbereitet.

## Als Nächstes

1. EXP-130 läuft, sobald die Grafikkarte frei ist (≈ 40 min), danach EXP-131 (Sekunden). 2. LM3-F auswerten, sobald fertig.

## Verlauf dieser Sitzung

- 17:29 EXP-131 (Zwischenschichten) vorbereitet, Selbsttest grün.
- 17:26 **EXP-127: „bricht“** (Δ_pow +0.13 / −0.17; nur vortrainierte Frequenzen werden gebraucht, beschreibend).
- 17:27 EXP-130 speichert jetzt auch die Modelle.
- 17:11 EXP-130: Smoke grün, Codeprüfung eingearbeitet, beim Dienst eingereiht.
- 16:29 Pythia Seed 4000 F/G fertig (Test 0.987/0.974); Prozesse hängen beim Beenden, Beenden abgelehnt.
- 16:25 EXP-130 (Ablation jeder einzelnen Frequenz im nachtrainierten Pythia) vorbereitet, CPU-Smoke läuft.
- 16:21 Pythia-Lauf 1/4 fertig (Seed 4000, Split F).
- 16:06 R12 im Paper fertig (Abstract geprüft: alle Zahlen richtig), committet.
- 16:04 Abstract neu: R12 („auch Addition mod 97 und Multiplikation mod 113: 4.5–7.4× schneller“), an anderer Stelle gekürzt.
- 16:03 Tabelle 1 um R12, LM1, LM1-F, LM3 ergänzt (aus den eingefrorenen Manifesten erzeugt).
- 16:01 Abbildung zu R12 erzeugt (`fig16`), Beschriftung auf Englisch.
- 16:01 Start: STATE, JOURNAL, Dienst geprüft.

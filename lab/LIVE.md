---
tags: [lab/live]
---
# LIVE: Laborsitzung 61

- **Sitzungsstart:** 2026-09-30 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-30 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 17:53 Berlin (gemessen)

## Gerade

- **Hinweis für den Nutzer:** Die zwei Seed-4001-Läufe von EXP-127 hängen seit ≈ 17:23 beim Beenden (P-021, Ergebnisse gesichert und ausgewertet). EXP-130 wartet dahinter. Beenden bitte durch dich/deinen Assistenten.
- **LM3-F bestätigt:** Auch bei ≈ 8.7 % Rechentext *braucht* das Sprachmodell die gesteuerten Frequenzen: Werden sie entfernt, fällt die Genauigkeit auf ≈ 1 %; das Entfernen der fremden Frequenzen schadet kaum (C̄ 0.84 [0.75, 0.91], 10/10). Die unabhängige Nachrechnung läuft (≈ 2 h), danach kommt der Satz ins Paper.
- Neue Frage N60 → **EXP-132** vorbereitet: Pythia auf *Multiplikation* mod 113 nachtrainieren (dort passen die Dezimalmerkmale nicht). Selbsttests grün; eine unabhängige Codeprüfung läuft.
- Die Grafikkarte steht seit ≈ 17:23 still (P-021-Hänger), EXP-130 wartet.

## Als Nächstes

1. Nächste Sitzung: LM3-F-Nachrechnung prüfen → Paper-Satz (Anhang K, §7) + Prüfung. 2. EXP-130 auswerten, dann EXP-131.

## Verlauf dieser Sitzung

- 17:53 EXP-132 vorbereitet (Selbsttest, Splits, Auswertung getestet).
- 17:46 N60 notiert; Rückschau im JOURNAL.
- 17:44 **LM3-F bestätigt** (C̄ 0.839 [0.747, 0.913], 10/10, p = 1/1024).
- 17:31 EXP-127-Verlauf: Die Änderung sammelt sich in allen Läufen auf denselben Frequenzen {2, 3, 11, 23, 56} (ab Schritt 2250; korrigiert nach Prüfung).
- 17:29 EXP-131 (Zwischenschichten) vorbereitet, Selbsttest grün.
- 17:26 **EXP-127: „bricht“** (Δ_pow +0.13 / −0.17; beschreibend schaden vor allem Sätze mit vortrainierten Frequenzen).
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

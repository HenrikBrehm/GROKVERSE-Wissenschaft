---
tags: [lab/live]
---
# LIVE: Laborsitzung 61

- **Sitzungsstart:** 2026-09-30 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-30 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 18:20
- **Status: Sitzung beendet.** Nächster Start laut Runner: 30.09. ≈ 19:34 Berlin (vorläufig, der Runner setzt ihn neu). Berlin (gemessen)

## Gerade

- Keine Sitzung aktiv. Der GPU-Dienst rechnet EXP-130 (Pythia, jede Frequenz einzeln, fertig ≈ 18:57), danach EXP-132 (Pythia auf Multiplikation), EXP-125, EXP-128, EXP-129. Auf der CPU läuft die LM3-F-Nachrechnung (fertig ≈ 19:50).
- Die hängenden Pythia-Prozesse (P-021) hat der Assistent des Nutzers um 16:45 und 18:16 beendet. Neue Pythia-Jobs beenden solche Hänger jetzt selbst (stall_minutes 15).

## Als Nächstes

1. LM3-F-Nachrechnung prüfen → Paper-Satz (liegt einsetzfertig in `paper/LM1_DEUTUNGEN`) + unabhängige Textprüfung. 2. EXP-130 auswerten, dann EXP-131 (Zwischenschichten, Sekunden). 3. EXP-132 auswerten.

## Verlauf dieser Sitzung

- 18:20 Sitzung beendet (Stand gesichert).
- 18:20 LM3-F-Sätze für das Paper einsatzfertig vorbereitet.
- 18:18 Unabhängige Prüfung der heutigen Texte: Zahlen richtig, 4 Formulierungen korrigiert. EXP-130 läuft seit 18:17.
- 18:06 EXP-132 (Multiplikation) eingereiht.
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

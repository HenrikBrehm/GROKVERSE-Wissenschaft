---
tags: [lab/live]
---
# LIVE: Laborsitzung 53

- **Sitzungsstart:** 2026-09-29 19:29 Berlin (17:29Z, vom Runner)
- **Deadline:** 2026-09-29 22:29 Berlin (20:29Z)
- **Zuletzt aktualisiert:** 21:45 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **LM1 bestätigt** (20:50): Im kleinen Sprachmodell steuert die Faktenauswahl die Zahl-Embeddings, Δ_pow 5.32 [4.86, 5.73], 10/10 Seeds, unabhängig nachgerechnet; im Paper eingetragen und geprüft.
- **R4-Reproduktion** fertig: 239/240 Läufe bitgleich; der eine abweichende war der *eingefrorene* Lauf selbst (einmaliger GPU-Ausreißer, durch 3 Wiederholungen geklärt).
- Letzte Logikprüfung (Anhänge C/D) läuft; danach Sitzungsende.

## Als Nächstes

Nächste Sitzung: LM1-F auswerten (läuft, 8/20 Modelle), unabhängig nachrechnen (Jobzeile in STATE), dann EXP-119/116/113 nach Vorab-Lesarten.

## Dienst (21:45)

{'40_exp113_stage2b': (2, 8), '41_exp116_lowshare': (0, 4), '36_exp119_lm_r5': (1, 6), '32_lm1f': (0, 1)}; LM1-F 8/20 Modelle.

## Verlauf dieser Sitzung

- 21:45 R4-Abweichung geklärt: eingefrorener Lauf war ein einmaliger Ausreißer (alter und neuer Trainer stimmen untereinander bitgleich überein).
- 21:23 R4-Reproduktion: 239/240 Läufe bitgleich, 1 Lauf weicht ab Schritt 2250 ab (Urteile gleich); Wiederholungen laufen.
- 21:19 Unabhängiges Nachrechen-Skript für LM1-F geschrieben, Seed 4000 stimmt exakt.
- 20:50 LM1 ausgewertet: bestätigt (s. o.); LM1-F eingereiht.
- ≈ 20:20 Meine Neuformulierungen gegengeprüft: 3 weitere Präzisierungen (L0-Satz im Abstract, EXP-116, R8-Schranke).
- 20:08 Logikprüfung des Haupttexts: 9 Punkte, 8 übernommen (Abstract zu L0/R8/N54b, R9 nur eine Äquivalenzzelle); der Wortlaut „25–50 Schritte“ bleibt deine Entscheidung (Argument in paper/STATUS).
- 19:48 Logikprüfung Anhang J: 4 Punkte, alle nachgeprüft und korrigiert (u. a. „lernt erst bei genug Häufigkeit“ war mit dem Verlustmodus vermischt).
- 19:38 Nachsatz: Das Wachstum der fremden Ziele ist nicht maskengetrieben (Maskenanteil unter Gleichverteilung).
- 19:36 Fehler in der Deutung von EXP-115 gefunden (s. o.).
- 19:32 Manuskript: veraltete Abbildungsverweise korrigiert (Generator), committet.
- 19:32 Start, Lage geprüft.

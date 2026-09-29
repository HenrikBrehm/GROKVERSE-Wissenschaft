---
tags: [lab/live]
---
# LIVE: Laborsitzung 53

- **Sitzungsstart:** 2026-09-29 19:29 Berlin (17:29Z, vom Runner)
- **Deadline:** 2026-09-29 22:29 Berlin (20:29Z)
- **Zuletzt aktualisiert:** 22:03 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet (22:03).** Nächster geplanter Start laut Runner: 29.09. 23:04 Berlin. Der GPU-Dienst rechnet weiter: LM1-F (11/20 Modelle, Ende nach Schätzung ≈ 23:05), EXP-119, EXP-113-Rest, EXP-116.
- Heute Abend: **LM1 bestätigt** (Sprachmodell, 10/10 Seeds); eigene Deutungsfehler durch Logikprüfungen gefunden und korrigiert; R4-Reproduktion abgeschlossen.

## Als Nächstes

Nächste Sitzung: LM1-F auswerten (läuft, 8/20 Modelle), unabhängig nachrechnen (Jobzeile in STATE), dann EXP-119/116/113 nach Vorab-Lesarten.

## Dienst (21:45)

{'40_exp113_stage2b': (2, 8), '41_exp116_lowshare': (0, 4), '36_exp119_lm_r5': (1, 6), '32_lm1f': (0, 1)}; LM1-F 8/20 Modelle.

## Verlauf dieser Sitzung

- 22:03 Anhänge C/D: 8 Logik-Punkte geprüft und eingearbeitet, Diff unabhängig geprüft (keine Probleme).
- 21:54 Sitzungsende; Logikprüfung Anhänge C/D (8 Punkte) als Liste für die nächste Sitzung.
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

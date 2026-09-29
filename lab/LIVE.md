---
tags: [lab/live]
---
# LIVE: Laborsitzung 53

- **Sitzungsstart:** 2026-09-29 19:29 Berlin (17:29Z, vom Runner)
- **Deadline:** 2026-09-29 22:29 Berlin (20:29Z)
- **Zuletzt aktualisiert:** 20:55 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- **LM1 bestätigt** (20:50): Im kleinen Sprachmodell steuert die Faktenauswahl die Zahl-Embeddings, Δ_pow 5.32 [4.86, 5.73], 10/10 Seeds, unabhängig nachgerechnet. Im Paper (Anhang J + ein Satz in §7) eingetragen; unabhängige Prüfung des Absatzes läuft.
- LM1-F (funktional: Ablation an den 20 Modellen) läuft seit 20:51 im Dienst.

## Als Nächstes

Prüfbefund einarbeiten; LM1-F beobachten und auswerten (CPU ≈ 1–1.5 h, Schätzung); Sitzungsende 22:29.

## Dienst (20:51)

LM1 20/20 fertig; LM1-F läuft; R4-Repro ≈ 180/240; EXP-119 0/6, EXP-113 2/8, EXP-116 0/4.

## Verlauf dieser Sitzung

- 20:50 LM1 ausgewertet: bestätigt (s. o.); LM1-F eingereiht.
- ≈ 20:20 Meine Neuformulierungen gegengeprüft: 3 weitere Präzisierungen (L0-Satz im Abstract, EXP-116, R8-Schranke).
- 20:08 Logikprüfung des Haupttexts: 9 Punkte, 8 übernommen (Abstract zu L0/R8/N54b, R9 nur eine Äquivalenzzelle); der Wortlaut „25–50 Schritte“ bleibt deine Entscheidung (Argument in paper/STATUS).
- 19:48 Logikprüfung Anhang J: 4 Punkte, alle nachgeprüft und korrigiert (u. a. „lernt erst bei genug Häufigkeit“ war mit dem Verlustmodus vermischt).
- 19:38 Nachsatz: Das Wachstum der fremden Ziele ist nicht maskengetrieben (Maskenanteil unter Gleichverteilung).
- 19:36 Fehler in der Deutung von EXP-115 gefunden (s. o.).
- 19:32 Manuskript: veraltete Abbildungsverweise korrigiert (Generator), committet.
- 19:32 Start, Lage geprüft.

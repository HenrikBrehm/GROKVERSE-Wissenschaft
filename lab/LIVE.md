---
tags: [lab/live]
---
# LIVE: Laborsitzung 51

- **Sitzungsstart:** 2026-09-29 14:10 Berlin (12:10Z, vom Runner)
- **Deadline:** 2026-09-29 17:09 Berlin (15:09Z)
- **Zuletzt aktualisiert:** 16:43 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Hinweis (14:37): wird behoben

Die Start-Blockade durch die Speicherzusage (P-013) hat der Nutzer-Assistent erkannt; ein sanfter Neustart (DRAIN) mit korrigiertem Speicherschutz läuft seit 14:29, danach starten die wartenden Läufe wieder. Danke!

## Gerade

- **Sitzung beendet (16:43).** Nächster geplanter Start laut Runner: 29.09. 17:44 Berlin (15:44Z). Der GPU-Dienst rechnet weiter: LM1 (5/20 fertig), EXP-117, R4-Repro, danach EXP-113-Rest und EXP-116.

## Als Nächstes

LM1 auswerten, sobald 20/20 fertig → unabhängige Nachrechnung → LM1-F (Funktion, eingefroren) → EXP-117/EXP-116/EXP-113.

## Verlauf dieser Sitzung

- 16:43 Sitzungsende; Ablation an Modellen mit flachen Häufigkeiten: Seed 3850 „funktional“, 3851 „unklar“.
- 16:01 EXP-115 ausgewertet („unklar“); LM1-F eingefroren (bfdab8d8).
- 15:45 EXP-118: „Ziele funktional“ (4/4).
- 15:26 EXP-118 festgelegt und gestartet (Ablation im Sprachmodell, kein Training).
- 15:05 EXP-114-Vergleich bei gleicher Faktenzahl: „Verdünnung nicht gestützt“ (vorab festgelegt); mit mehr Text braucht das Modell ≈ 1.9× mehr Wiederholungen bis zum Lernen.
- 15:00 Neue Paper-Sätze unabhängig geprüft, 4 Korrekturen übernommen.
- 14:50 Manuskript mit Anhang A–M, Tabelle 1 und umgeschriebenen Querverweisen; Zenodo-Paket erweitert (Import-Test ok).
- 14:45 Abb. K1 (Sprachmodell: Steuerung setzt mit dem Faktenlernen ein) aus EXP-114.
- 14:37 LM1 Lauf 0 fertig (723 s); Deutungssätze für LM1/EXP-115/EXP-117 vorab festgelegt.
- 14:26 EXP-117 festgelegt (ungekoppelte Kopie des Trainers, Selbsttest grün) und eingereiht.
- 14:22 Kürzung unabhängig geprüft; 2 verlorene Einschränkungen und 4 kleinere Punkte wiederhergestellt (Haupttext 4 147 Wörter).
- 14:21 EXP-116 (wenige Prozent Rechensätze) festgelegt und eingereiht.
- 14:19 Kürzung der Kurzfassung (Haupttext 4 440 → 4 085 Wörter), Prüfung läuft.
- 14:16 Manuskript-Generator mit Zitatprüfung: 3 fehlende Literatureinträge gefunden und ergänzt (Fu, Karkada, Howe 2026b); LM1-Nachrechnung vorbereitet.
- 14:13 Zyklus 1: Steuerung folgt dem Lernbeginn auch bei ×4 Lernrate („coupled“, post hoc) – trennt aber „braucht Anpassen“ nicht von „gleiche Uhr“.
- 14:10 Sitzungsstart, kein STOP, Fenster offen.

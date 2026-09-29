---
tags: [lab/live]
---
# LIVE: Laborsitzung 51

- **Sitzungsstart:** 2026-09-29 14:10 Berlin (12:10Z, vom Runner)
- **Deadline:** 2026-09-29 17:09 Berlin (15:09Z)
- **Zuletzt aktualisiert:** 14:37 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Hinweis (14:37): wird behoben

Die Start-Blockade durch die Speicherzusage (P-013) hat der Nutzer-Assistent erkannt; ein sanfter Neustart (DRAIN) mit korrigiertem Speicherschutz läuft seit 14:29, danach starten die wartenden Läufe wieder. Danke!

## Gerade

- GPU-Dienst wurde um 14:25 mit neuem Code neu gestartet (Speicherwächter; nicht von mir). Läuft: LM1 2 (bei Schritt 4250/6000, am Checkpoint fortgesetzt), EXP-115 1. Neue Starts warten gerade auf freien Arbeitsspeicher-Commit (1.4 GB frei).
- Zwei neue LM-Piloten eingereiht: EXP-116 (nur ≈ 9 % Rechensätze) und EXP-117 (Ein-/Ausgabe-Embeddings getrennt: steckt die Steuerung wirklich in der Zahl-Repräsentation?).

## Als Nächstes

EXP-115 (flache Zahl-Häufigkeiten) auswerten, sobald das erste Lauf-Paar fertig ist; LM1 beobachten.

## Verlauf dieser Sitzung

- 14:37 LM1 Lauf 0 fertig (723 s); Deutungssätze für LM1/EXP-115/EXP-117 vorab festgelegt.
- 14:26 EXP-117 festgelegt (ungekoppelte Kopie des Trainers, Selbsttest grün) und eingereiht.
- 14:22 Kürzung unabhängig geprüft; 2 verlorene Einschränkungen und 4 kleinere Punkte wiederhergestellt (Haupttext 4 147 Wörter).
- 14:21 EXP-116 (wenige Prozent Rechensätze) festgelegt und eingereiht.
- 14:19 Kürzung der Kurzfassung (Haupttext 4 440 → 4 085 Wörter), Prüfung läuft.
- 14:16 Manuskript-Generator mit Zitatprüfung: 3 fehlende Literatureinträge gefunden und ergänzt (Fu, Karkada, Howe 2026b); LM1-Nachrechnung vorbereitet.
- 14:13 Zyklus 1: Steuerung folgt dem Lernbeginn auch bei ×4 Lernrate („coupled“, post hoc) – trennt aber „braucht Anpassen“ nicht von „gleiche Uhr“.
- 14:10 Sitzungsstart, kein STOP, Fenster offen.

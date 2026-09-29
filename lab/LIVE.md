---
tags: [lab/live]
---
# LIVE: Laborsitzung 51

- **Sitzungsstart:** 2026-09-29 14:10 Berlin (12:10Z, vom Runner)
- **Deadline:** 2026-09-29 17:09 Berlin (15:09Z)
- **Zuletzt aktualisiert:** 15:05 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Hinweis (14:37): wird behoben

Die Start-Blockade durch die Speicherzusage (P-013) hat der Nutzer-Assistent erkannt; ein sanfter Neustart (DRAIN) mit korrigiertem Speicherschutz läuft seit 14:29, danach starten die wartenden Läufe wieder. Danke!

## Gerade

- Warte auf EXP-115 (flache Zahl-Häufigkeiten; 2 von 4 Läufen fertig) und beobachte LM1 (Sprachmodell-Bestätigung, 2/20 fertig, 2 laufen).
- Neu: Auch bei ≈ 34 % Rechensätzen steuert die Faktenauswahl die Zahl-Darstellung deutlich, sobald das Modell die Fakten gelernt hat (EXP-113, 1 Seed-Paar: Δ_pow 7.0, zurückgehaltene Fakten 0.98/0.95).

## Als Nächstes

EXP-113 (2 Läufe fast fertig) und EXP-115 beobachten; EXP-115 auswerten, sobald alle 4 Läufe fertig sind.

## Verlauf dieser Sitzung

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

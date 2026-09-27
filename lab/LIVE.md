---
tags: [lab/live]
---
# LIVE: Laborsitzung 30

- **Sitzungsstart:** 2026-09-27 18:19 Berlin (16:19Z, vom Runner)
- **Deadline:** 2026-09-27 21:19 Berlin (19:19Z)
- **Zuletzt aktualisiert:** 19:12 Berlin (gemessen)
- **Run-Fenster:** zu bis 00:00: kein Training, keine Tests.

## Gerade

Auffällige Beobachtung in gespeicherten Läufen: Konstruierte Splits groken etwa 9× früher als zufällige. Der vorab registrierte Test dafür ([[experiments/EXP-018-split-speed/README|EXP-018]]) war nie gelaufen; jetzt ist er für heute Nacht auf der GPU eingeplant (≈ 15 min).

## Als Nächstes

Stand sichern; weitere Gutachterfragen an gespeicherten Daten.

## Verlauf dieser Sitzung

- 19:12 EXP-018 (Grokking-Beschleunigung durch konstruierte Splits) auf GPU umgestellt und in den Nachtplan aufgenommen.
- 19:09 Exploration: Die Steuerung (Δ_pow) wächst nach dem Grokking weiter (20/20 Seeds, drei Aufgaben), getragen von den eigenen Zielen.
- vor 19:09 Venue-Abgleich der Literaturliste (arXiv-Seiten).
- 19:04 Abbildung 0 (Masken, M0c, Wechselprotokoll) aus P1-Splitdateien.
- vor 19:04 Quellenprüfung der Entwurfsänderungen: 4 eigene Fehler gefunden und korrigiert.
- 19:00 Literaturliste [[paper/references]] erstellt (35 Zitate, Lücken markiert); N42 (Phaseneingriff) nach Überschlag verworfen.
- 18:56 R4 nach zwei Codex-Runden überarbeitet (1 Blocker, 5 Major eingearbeitet; 60 Einheiten, zwei Zeitpunkte, Null-SD nachgerechnet).
- 18:36 R4 entworfen (160 GPU-Läufe, fest 40 Einheiten), Code ungetestet; im Entwurf §4 die Zufallssplit-Assoziation aus EXP-015 mit Seed-Vorbehalt.
- vor 18:35 EXP-083 vorbereitet (Verschiebung je Reset-Teil); Code-Prüfung fand einen Fehler (Thread-Zahl), behoben.
- vor 18:30 Gutachter-Durchgang: 10 Textkorrekturen im Paper-Entwurf, keine Zahl geändert.
- 18:20 Start: kein STOP, keine Python-Prozesse, Fenster zu.

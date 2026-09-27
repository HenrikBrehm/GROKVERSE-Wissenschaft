---
tags: [lab/live]
---
# LIVE: Laborsitzung 33

- **Sitzungsstart:** 2026-09-27 22:19 Berlin (20:19Z, vom Runner)
- **Deadline:** 2026-09-28 01:19 Berlin (23:19Z)
- **Zuletzt aktualisiert:** 22:41 Berlin
- **Run-Fenster:** gesperrt bis Mo 28.09. 01:30 (Nutzer), dann bis 18:00. In dieser Sitzung also **keine Läufe**.

## Gerade

Unabhängige Quellenprüfung der zwei neuen Paper-Absätze (Gegenterm in N28/P3, Persistenz unabhängig davon). Codex ist nicht mehr verfügbar (Guthaben leer).

## Als Nächstes

Prüfbefunde einarbeiten, committen. Dann weitere Vorbereitung für die Nacht.

## Verlauf dieser Sitzung

- 22:41 **Neu (post hoc, P3):** Wo der Gegendruck der neuen Daten fast verschwindet (ω 0.4), bleibt die Persistenz gleich (π 0.351/0.355). Die frühe Wahl wird also nicht direkt von den Daten abgebaut. Paper §3.3, FINDINGS.
- 22:36 Codex zu R7: 1 Blocker + 4 Major, alle geprüft und übernommen (Fassung 2). Paper §2: In N28/P3 drückt der neue Split in erster Ordnung gegen die alten Frequenzrichtungen (30/30).
- 22:28 Vorab zu EXP-086: A2 zeigt bei F zum Teil gegen A (cos −0.52, wie B). Ein positives D wäre damit sauberer als gedacht.
- 22:28 Statische Prüfung der Nachtbefehle: keine Laufzeitfehler; Threads-Grenze und P2f-Schritt in STATE korrigiert.
- 22:25 R7 entworfen (Registrierung + `confirm_r7.py`, ungetestet); `repro/train.py` markiert fertige Läufe als completed.
- 22:20 Start: kein STOP, keine Python-Prozesse, Wächter Exit 3 (Fenster zu bis 01:30).

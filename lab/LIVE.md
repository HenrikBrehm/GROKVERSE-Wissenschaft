---
tags: [lab/live]
---
# LIVE: Laborsitzung 33 (beendet)

- **Sitzungsstart:** 2026-09-27 22:19 Berlin (20:19Z, vom Runner)
- **Deadline:** 2026-09-28 01:19 Berlin (23:19Z)
- **Zuletzt aktualisiert:** 22:46 Berlin
- **Run-Fenster:** gesperrt bis Mo 28.09. 01:30 (Nutzer), dann bis 18:00. In dieser Sitzung also **keine Läufe**.

## Gerade

**Sitzung beendet (22:46).** Nächster geplanter Start laut runner-state.json: **Mo 28.09. 01:54 Berlin** (23:54Z). Läufe ab 01:30.

## Als Nächstes

Checkliste [[NACHT_2026-09-28]]: CPU EXP-040/014; GPU P2f → EXP-073/074/075 → EXP-086/085 → EXP-078 → R1 → R6 → R5 → R7 → R3 → P4 → R2 → R4.

## Verlauf dieser Sitzung

- 22:46 Sitzung beendet; Abschlussbericht im [[JOURNAL]]. Nacht-Checkliste angelegt, zweite Literatursuche zu N43 (nichts Einschränkendes).
- 22:41 **Neu (post hoc, P3):** Wo der Gegendruck der neuen Daten fast verschwindet (ω 0.4), bleibt die Persistenz gleich (π 0.351/0.355). Keine erkennbare Abhängigkeit vom Gegenterm erster Ordnung (Quellenprüfung: vorsichtiger formuliert). Paper §3.3, FINDINGS.
- 22:36 Codex zu R7: 1 Blocker + 4 Major, alle geprüft und übernommen (Fassung 2). Paper §2: In N28/P3 drückt der neue Split in erster Ordnung gegen die alten Frequenzrichtungen (30/30).
- 22:28 Vorab zu EXP-086: A2 zeigt bei F zum Teil gegen A (cos −0.52, wie B). Ein positives D wäre damit sauberer als gedacht.
- 22:28 Statische Prüfung der Nachtbefehle: keine Laufzeitfehler; Threads-Grenze und P2f-Schritt in STATE korrigiert.
- 22:25 R7 entworfen (Registrierung + `confirm_r7.py`, ungetestet); `repro/train.py` markiert fertige Läufe als completed.
- 22:20 Start: kein STOP, keine Python-Prozesse, Wächter Exit 3 (Fenster zu bis 01:30).

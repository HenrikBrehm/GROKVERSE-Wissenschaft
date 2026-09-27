---
tags: [lab/live]
---
# LIVE: Laborsitzung 23

- **Sitzungsstart:** 2026-09-27 09:39 Berlin (07:39Z, vom Runner)
- **Deadline:** 2026-09-27 12:39 Berlin (10:39Z)
- **Zuletzt aktualisiert:** 09:52 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

Codex prueft zwei vorab festgelegte Bestaetigungen: N29 (funktionaler Uebergang nach einem Datenwechsel) und P2e (gilt der P2d-Befund auch bei Multiplikation und mod 97?).

## Als Naechstes

Registrierung + Code, Codex-Pruefung, einfrieren, ein Smoke durch den Lader, dann den Block auf der GPU.

## Verlauf dieser Sitzung

- 09:50 P2e festgelegt (Entwurf, Code getestet): P2d-Mass an frischen Seeds fuer mul 113 und add 97.
- 09:48 **EXP-066 (Exploration):** Der P2d-Effekt zeigt sich auch bei Multiplikation mod 113 (0.16) und Addition mod 97 (0.22), in allen 100 Seed-Werten positiv.
- 09:45 N29 festgelegt (Entwurf, Code getestet): Wechsel bei 25 gegen 50 Schritte, 20 frische Seeds, 4000 Schritte Nachtraining.
- 09:41 CPU-Programm neu gestartet (EXP-039 laeuft weiter).

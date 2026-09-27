---
tags: [lab/live]
---
# LIVE: Laborsitzung 22

- **Sitzungsstart:** 2026-09-27 06:59 Berlin (04:59Z, vom Runner)
- **Deadline:** 2026-09-27 09:59 Berlin (07:59Z)
- **Zuletzt aktualisiert:** 07:12 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

EXP-059 auf der GPU: etwa die Haelfte der 200 Laeufe fertig, keine Fehler. Codex prueft parallel den Plan fuer P2b (Nachfolger der gescheiterten Funktionspruefung P2).

## Als Naechstes

EXP-059 auswerten -> N28-Bestaetigung festlegen. Danach N28 und P2b einfrieren und beide auf der GPU rechnen (zusammen etwa 75 min).

## Verlauf dieser Sitzung

- 07:12 P2b-Entwurf fertig: frische Seeds 2000-2099, 4000 Schritte, n = 100 aus der beobachteten Streuung (Power ca. 0.9). Seeds reserviert.
- 07:08-07:12 Gemeinsames Bindungsmodul (bound_block.py) fuer neue Bestaetigungen; N28- und P2b-Code bestehen den Selbsttest.
- 07:03 EXP-059 gestartet (GPU, 8 parallel).
- 07:02 EXP-059 vor jedem Lauf festgelegt (7d6374e): Momentum gegen verlaengerte Exposition.
- 07:00 CPU-Programm wieder gestartet (EXP-036 ...).

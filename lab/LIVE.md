---
tags: [lab/live]
---
# LIVE: Laborsitzung 22

- **Sitzungsstart:** 2026-09-27 06:59 Berlin (04:59Z, vom Runner)
- **Deadline:** 2026-09-27 09:59 Berlin (07:59Z)
- **Zuletzt aktualisiert:** 07:51 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

Zwei eingefrorene Bestaetigungen laufen auf der GPU (zusammen 500 Laeufe, ca. 80 min): **N28** (Momentum-Reset) und **P2b** (nutzt das Netz die gesteuerten Frequenzen wirklich?).
Das CPU-Programm laeuft daneben weiter.

## Als Naechstes

Laeufe beobachten (P2b 67/200, N28 87/300 um 07:51); Literatur zum Zwei-Regime-Bild suchen; danach N28, die N28-Vorhersage und P2b auswerten.

## Verlauf dieser Sitzung

- 07:51 **EXP-062: Zwei Regime.** Wechselt man frueh (bis ca. 30 Schritte), behaelt das Netz die alten Frequenzen UND lernt die neuen dazu. Wechselt man nach 50 Schritten, entstehen die neuen kaum noch. Vorhersage fuer die frischen N28-Seeds vorab festgelegt.
- 07:48 EXP-061 verworfen: Der Gradient der neuen Daten baut die alte Wahl eher ab, statt sie zu verstaerken.
- 07:37 EXP-060: Die alte Wahl ist nicht einfach am Spektrum von W_E ablesbar.
- 07:34 N28 und P2b eingefroren (fa154bd) und gestartet. Codex hatte vorher 2 Blocker bei P2b und 1 bei N28 gefunden, alle behoben.
- 07:22 **EXP-059: Das "Adam-Gedaechtnis" ist nur verlaengerte Uebung.** Loescht man das Momentum, fehlen dem Netz etwa 6-10 Lernschritte, mehr nicht. Die Deutung von gestern war zu stark und ist korrigiert.
  Eigentlicher Befund: Die Festlegung ist sehr steil. Nach 10 Schritten ist fast nichts fest, nach 50 alles.
- 07:12 P2b-Entwurf fertig: frische Seeds 2000-2099, 4000 Schritte, n = 100 aus der beobachteten Streuung (Power ca. 0.9). Seeds reserviert.
- 07:08-07:12 Gemeinsames Bindungsmodul (bound_block.py) fuer neue Bestaetigungen; N28- und P2b-Code bestehen den Selbsttest.
- 07:03 EXP-059 gestartet (GPU, 8 parallel).
- 07:02 EXP-059 vor jedem Lauf festgelegt (7d6374e): Momentum gegen verlaengerte Exposition.
- 07:00 CPU-Programm wieder gestartet (EXP-036 ...).

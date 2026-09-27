---
tags: [lab/live]
---
# LIVE: Laborsitzung 22

- **Sitzungsstart:** 2026-09-27 06:59 Berlin (04:59Z, vom Runner)
- **Deadline:** 2026-09-27 09:59 Berlin (07:59Z)
- **Zuletzt aktualisiert:** 08:10 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

GPU: N28-Bestaetigung (ca. 160/300), P2c (neu gestartet, ersetzt P2b) und der kleine Pilot EXP-063. CPU-Programm laeuft daneben.

## Als Naechstes

N28 auswerten, sobald fertig (ca. 08:35), und die vorab festgelegte Zwei-Regime-Vorhersage an denselben frischen Seeds pruefen. P2c wird erst in der naechsten Sitzung fertig.

## Verlauf dieser Sitzung

- 08:10 P2c eingefroren und gestartet (Codex-Pruefung ohne Einwaende).
- 08:05 **P2b abgebrochen, mein Fehler:** Der Trainer hoert standardmaessig 2000 Schritte nach der Generalisierung auf; die Auswertung haette 4000 verlangt und alles abgelehnt. Noch nichts ausgewertet, Seeds verbraucht; Nachfolger P2c mit frischen Seeds.
- 07:54 EXP-063 gestartet: Sitzt der Ausschluss neuer Frequenzen im Rest des Netzes?
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

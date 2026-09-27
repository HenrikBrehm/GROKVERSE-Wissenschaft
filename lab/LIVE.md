---
tags: [lab/live]
---
# LIVE: Laborsitzung 22

- **Sitzungsstart:** 2026-09-27 06:59 Berlin (04:59Z, vom Runner)
- **Deadline:** 2026-09-27 09:59 Berlin (07:59Z)
- **Zuletzt aktualisiert:** 09:31 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

Codex prueft die P2d-Schlussfolgerung; danach FINDINGS und Abschluss (Sitzungsende gegen 09:50).

## Als Naechstes

Den funktionalen Uebergang (frueh umsteigen, ab 50 Schritten festhalten) an frischen Seeds sauber bestaetigen; danach ein besseres Mass fuer die Funktionsfrage (P2d).

## Verlauf dieser Sitzung

- 09:30 **P2d BESTAETIGT (20/20 frische Seeds):** Mit gleich grossen Schritten reagiert das Netz entlang der gesteuerten Frequenzen viel staerker als bei Kontrollfrequenzen. Die Funktionsfrage ist damit (lokal) beantwortet.
- 09:15 **EXP-065 (Exploration):** Mit gleich grossen Schritten reagiert das Netz entlang der gesteuerten Frequenzen viel staerker als bei Kontrollen (80/80 Modelle). Die P2c-Umkehrung lag wohl am Mass.
- 09:13 Abschlussbericht im JOURNAL, STATE fuer die naechste Sitzung.
- 09:06 **EXP-064 (beschreibend):** Nach einem fruehen Wechsel rechnet das Netz mit den NEUEN Frequenzen, nach 50 Schritten nur noch mit den alten. Formal nicht auswertbar (3 Modelle nicht fertig), das Muster ist aber in allen 10 Seeds gleich.
- 09:03 **P2c nicht bestaetigt:** Das Entfernen der gesteuerten Frequenzen schadet mit diesem Mass nicht mehr als bei Kontrollfrequenzen, eher weniger. Die Funktionsfrage bleibt offen.
- 08:34 Codex prueft die Schlussfolgerungen: Aussagen enger gefasst (Spektrum, nicht Funktion). FINDINGS aktualisiert.
- 08:29 **N28 BESTAETIGT (30/30 frische Seeds):** Momentum loeschen senkt die Persistenz um 0.15, zehn Extra-Schritte gleichen es aus. **Zwei-Regime-Vorhersage bestaetigt** (29/30 und 30/30): frueh Koexistenz, ab 50 Schritten Ausschluss.
- 08:17 **EXP-063:** Der Ausschluss braucht W_E und den Rest des Netzes zusammen; das Behalten der alten Wahl nicht.
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

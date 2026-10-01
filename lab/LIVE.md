---
tags: [lab/live]
---
# LIVE: Laborsitzung 72

- **Sitzungsstart:** 2026-10-01 17:49 Berlin (15:49Z, vom Runner)
- **Deadline:** 2026-10-01 20:49 Berlin (18:49Z)
- **Zuletzt aktualisiert:** 19:27

## Gerade

- **Pause aktiv (Regel 23).** Die LeDoux-Linie ist vollständig ausgewertet und nachgerechnet. Der GPU-Dienst ist leer; es laufen keine Trainings.
- **Sitzung 72 beendet.** Nächster geplanter Start: 01.10. 21:24 Berlin (runner-state.json). Er macht nur eine kurze Lagekontrolle und endet wieder mit „Pause aktiv“, bis du die Pause aufhebst.

## Als Nächstes

- Nichts rechnen. Für dich: neue Fragen zu EXP-144 in [[paper/erklaerung/LEITFRAGEN_LEDOUX]] (unten).

## Verlauf dieser Sitzung
- 19:25 Nebenarm EXP-143 (starker Weight Decay) fertig: lernt gar nichts; in den Läufen mit sortierter Reihenfolge besteht die Einbettung danach aber fast nur aus dem Muster der Reihenfolge. Damit ist EXP-143 abgeschlossen.
- 19:19 **EXP-144 fertig und nachgerechnet:** Kein Lauf lernt die Regel. Bei zufälliger Reihenfolge lernt das breite Netz 86–91 % der Trainingsaufgaben auswendig, bei sortierter nur ≈ 26 %. „Menge gegen Reihenfolge“ bleibt bei 0,3 % Daten offen. Korrektur: Stärkste Frequenz bei sortierter Reihenfolge ist 303, nicht 101.
- 18:57 F-stride 111 500/250 000: Train 0.36, Test ≈ 0.001.
- 18:38 **EXP-144, 3 von 4 Läufen:** Das breite Netz lernt die Trainingsaufgaben fast (Spitze 91 %, Ende 86 %), aber keiner der Läufe lernt die Regel. Damit wieder keine Aussage zu „Menge gegen Reihenfolge“. Das passt zu LeDoux: Auch dort lernt die zufällige Reihenfolge nur auswendig.
- 18:10 R-iid 108 500/250 000 Schritte: Train 0.88, Test ≈ 0; R-stride 107 500: Train 0.31, Test ≈ 0.001. Fertig ≈ 18:40.
- 17:52 Start; STATE gelesen, kein STOP, Fenster offen; Dienst rechnet EXP-144 (1/4 fertig, 2 laufen, 1 wartet auf Speicher).

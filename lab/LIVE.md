---
tags: [lab/live]
---
# LIVE: Laborsitzung 23

- **Sitzungsstart:** 2026-09-27 09:39 Berlin (07:39Z, vom Runner)
- **Deadline:** 2026-09-27 12:39 Berlin (10:39Z)
- **Zuletzt aktualisiert:** 10:25 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

P2e laeuft auf der GPU (etwa 30/80 fertig, 7 Arbeiter). Danach Auswertung und die Trainer-Option fuer EXP-067 (Patch vorbereitet, darf erst nach P2e eingespielt werden, weil der Trainer im Code-Hash von P2e steht).

## Als Naechstes

P2e auswerten → Codex zur Schlussfolgerung → FINDINGS. Dann Trainer-Option + Tests + Codex → EXP-067 (60 Laeufe).

## Verlauf dieser Sitzung

- 10:24 **EXP-068 (Exploration):** Bei gleich viel entfernter Energie reagiert das Netz auf die dominante Frequenzmenge NICHT staerker. Die gemessene Funktion folgt der Energie; das ist jetzt als Grenze in FINDINGS vermerkt.
- 10:21 FINDINGS: N29 als K4c im engen Wortlaut nach Codex eingetragen.
- 10:17 **N29 bestaetigt:** zwischen 25 und 50 Schritten kippt, auf welche Frequenzen das Netz am Ende angewiesen ist. Nachtraeglich: Die Energie in W_E zeigt dieselbe Richtung.
- 10:16 N29-Block fertig (80/80); P2e zweite Warteschlange gestartet.
- 10:09 EXP-067 vorab festgelegt (Pilot).
- 10:07 P2e eingefroren (zweiter Anlauf) und gestartet.
- 10:04 P2e-Probelauf deckt einen Klammerfehler in der Auswertung auf; behoben, Selbsttest erweitert.
- 09:59 N29 eingefroren, Probelauf durch den Lader ok, Block gestartet.
- 09:54 Codex: zwei Blocker in N29 (Auswahlregel, fehlende Datei im Code-Hash), behoben und nachgeprueft.
- 09:50 P2e festgelegt (Entwurf, Code getestet): P2d-Mass an frischen Seeds fuer mul 113 und add 97.
- 09:48 **EXP-066 (Exploration):** Der P2d-Effekt zeigt sich auch bei Multiplikation mod 113 (0.16) und Addition mod 97 (0.22), in allen 100 Seed-Werten positiv.
- 09:45 N29 festgelegt (Entwurf, Code getestet): Wechsel bei 25 gegen 50 Schritte, 20 frische Seeds, 4000 Schritte Nachtraining.
- 09:41 CPU-Programm neu gestartet (EXP-039 laeuft weiter).

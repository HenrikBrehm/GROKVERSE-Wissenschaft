---
tags: [lab/live]
---
# LIVE: Laborsitzung 23

- **Sitzungsstart:** 2026-09-27 09:39 Berlin (07:39Z, vom Runner)
- **Deadline:** 2026-09-27 12:39 Berlin (10:39Z)
- **Zuletzt aktualisiert:** 10:19 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

**N29 BESTAETIGT (20 frische Seeds):** Wechselt man die Trainingsdaten nach 50 Schritten, rechnet das fertige Netz weiter mit den ALTEN Frequenzen (0.90); nach 25 Schritten mit den NEUEN (0.60).
Codex greift gerade die Formulierung an. P2e laeuft auf der GPU (7 Arbeiter).

## Als Naechstes

Codex-Ergebnis einarbeiten, dann FINDINGS. Nach P2e: Auswertung, danach Trainer-Option fuer EXP-067 (welcher Netzteil haelt die alten Frequenzen fest).

## Verlauf dieser Sitzung

- 10:17 **N29 bestaetigt:** zwischen 25 und 50 Schritten kippt, auf welche Frequenzen das Netz am Ende angewiesen ist. Nachtraeglich: Die Energie in W_E zeigt dieselbe Richtung.
- 10:16 N29-Block fertig (80/80); P2e zweite Warteschlange gestartet.
- 10:10 EXP-067 vorab festgelegt (Pilot).
- 10:07 P2e eingefroren (zweiter Anlauf) und gestartet.
- 10:04 P2e-Probelauf deckt einen Klammerfehler in der Auswertung auf; behoben, Selbsttest erweitert.
- 09:59 N29 eingefroren, Probelauf durch den Lader ok, Block gestartet.
- 09:54 Codex: zwei Blocker in N29 (Auswahlregel, fehlende Datei im Code-Hash), behoben und nachgeprueft.
- 09:50 P2e festgelegt (Entwurf, Code getestet): P2d-Mass an frischen Seeds fuer mul 113 und add 97.
- 09:48 **EXP-066 (Exploration):** Der P2d-Effekt zeigt sich auch bei Multiplikation mod 113 (0.16) und Addition mod 97 (0.22), in allen 100 Seed-Werten positiv.
- 09:45 N29 festgelegt (Entwurf, Code getestet): Wechsel bei 25 gegen 50 Schritte, 20 frische Seeds, 4000 Schritte Nachtraining.
- 09:41 CPU-Programm neu gestartet (EXP-039 laeuft weiter).

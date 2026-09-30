---
tags: [lab/live]
---
# LIVE: Laborsitzung 58

- **Sitzungsstart:** 2026-09-30 08:29 Berlin (06:29Z, vom Runner)
- **Deadline:** 2026-09-30 11:29 Berlin (09:29Z)
- **Zuletzt aktualisiert:** 10:47 Berlin (gemessen)
- **Status: Sitzung beendet.** Nächster Start laut Runner: 30.09. 12:04 Berlin (vorläufig, der Runner setzt ihn neu).

## Gerade

- Keine Sitzung aktiv. Der GPU-Dienst rechnet weiter: LM3 (11/20 fertig), R12 (62/200), danach der Pythia-Pilot EXP-127 (≈ 20:30), dann EXP-125.

## Als Nächstes

1. LM3 und R12 auswerten, sobald fertig (Deutungssätze liegen bereit). 2. EXP-127 auswerten (`analyze.py`). 3. Nach R12: SGD-Clipping-Patch (EXP-128) anwenden und testen.

## Verlauf dieser Sitzung (Uhrzeiten = Commit-/Wächterzeiten)

- 10:45 Warteschlange umgestellt (Assistent des Nutzers): Pythia-Pilot vor EXP-125.
- 10:32 Test: Am vortrainierten Modell zeigt der erste Lernschritt die gewünschten Frequenzen nicht („nicht gestützt“, vorher so festgelegt).
- 09:29 SGD-Clipping als getesteter Patch vorbereitet (EXP-128).
- 09:25 Pythia-160M kann ohne Nachtraining nicht addieren (0.7 %).
- 09:11 Unabhängige Codeprüfung von EXP-127: keine Blocker.
- 09:06 EXP-127-Messgröße vor dem Start gegen Weight-Decay-Verfälschung gehärtet.
- 09:02 Vortrainierte Zahl-Einbettungen tragen schon Frequenzen 1–3 und 11/23/45 (Zehnerrhythmus).
- 09:00 EXP-127 (Pythia-160M nachtrainieren) vorbereitet und eingereiht.
- 08:36 Paper: LM1/LM1-F im Abstract und in §7, unabhängig geprüft.
- 08:30 Start.

---
tags: [lab/live]
---
# LIVE: Laborsitzung 58

- **Sitzungsstart:** 2026-09-30 08:29 Berlin (06:29Z, vom Runner)
- **Deadline:** 2026-09-30 11:29 Berlin (09:29Z)
- **Zuletzt aktualisiert:** 10:34 Berlin (gemessen)
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Stand sichern. Um ≈ 10:38–11:00 stellt der Assistent des Nutzers die Warteschlange um (EXP-127 vor EXP-125); danach passe ich STATE an und schreibe den Abschlussbericht.

## Als Nächstes

1. EXP-127-Pilot startet, sobald der Dienst Platz hat (nach LM3/R12/EXP-125). 2. LM3 und R12 auswerten, wenn fertig (Deutungssätze liegen bereit). 3. Nach R12: SGD-Clipping-Patch anwenden (EXP-128).

## Dienst (09:24)

Neustart (P-017-Fix) erledigt, läuft wieder. LM3 8/20 fertig, 3 laufen; R12 26/200, 4 laufen; EXP-125 und EXP-127 warten auf Speicher.

## Verlauf dieser Sitzung (Uhrzeiten = Commit-/Wächterzeiten)

- 10:32 **Gradiententest fertig: „nicht gestützt“** – am vortrainierten Modell trägt der erste Lernschritt die gewünschten Frequenzen nicht; wenn Pythia gesteuert wird, dann erst im Lauf des Trainings. Der CPU-Prozess ist beendet (dauerte 62 statt wenige Minuten).
- 10:12 Nutzerentscheidung: der Pythia-Pilot läuft vor EXP-125 (heute Abend fertig statt nachts).

- 10:02 Erster Seed des Gradiententests: Am vortrainierten Modell zeigt der erste Lernschritt die vorgegebenen Frequenzen *nicht* (Δ ≈ 0); die Zahlen-Vorprägung dominiert. Zweiter Seed läuft.

- 09:29 EXP-128-Patch protokolliert jetzt auch die Gradientennorm (Clipping-Wert später gemessen statt geraten).
- 09:25 Pythia-160M kann ohne Nachtraining nicht addieren (0.7 %).

- 09:23 Eigene Uhrzeiten korrigiert: einige Notizen hatten geschätzte statt gemessene Zeiten.
- 09:21 **EXP-128 vorbereitet:** SGD mit Gradient-Clipping als Patch (Trainer ist wegen R12 gesperrt), alle Tests grün.
- 09:11 Unabhängige Codeprüfung von EXP-127: keine Blocker; Auswertung robuster gemacht.
- 09:06 EXP-127: Messgröße vor dem Start verbessert – Weight Decay schrumpft die vortrainierten Einbettungen und hätte das Ergebnis verfälschen können.
- 09:03 Literatur: vortrainierte Fourier-Zahlmerkmale sind bekannt (Zhou et al. 2024); Steuerung durch die Faktenauswahl beim Nachtrainieren nach unserer Suche nicht gefunden.
- 09:02 Vortrainierte Zahl-Einbettungen (Pythia, GPT-2) tragen schon Frequenzen 1–3 und 11/23/45 (Zehnerrhythmus).
- 09:00 **EXP-127 vorbereitet und eingereiht:** Pythia-160M lernt Rechenfakten mod 113 nach. Selbsttest und Smoke grün.
- 08:36 **Paper: LM1/LM1-F im Abstract und als Absatz in §7**, unabhängig geprüft (alle Zahlen richtig, 8 Formulierungen verbessert).
- 08:30 Start: Stand gelesen, Fenster offen, kein STOP.

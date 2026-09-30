---
tags: [lab/live]
---
# LIVE: Laborsitzung 62

- **Sitzungsstart:** 2026-09-30 18:29 Berlin (16:29Z, vom Runner)
- **Deadline:** 2026-09-30 21:29 Berlin (19:29Z)
- **Zuletzt aktualisiert:** 19:57

## Hinweis für den Assistenten (19:24) – **erledigt 19:34: Prozess endete von selbst, nichts zu tun**

- **Symptom:** Mein eigener CPU-Zeittest (erster Gradient für EXP-133) belegt ≈ 5 Kerne und bremst die LM3-F-Nachrechnung des Dienstes (PID 29844). Mein Abbruch wurde von der Sicherheitsprüfung abgelehnt (Interfere With Workloads).
- **Prozess:** PID 18524, gestartet 30.09. 19:13:09, `python lab/experiments/EXP-133-pythia-reset-numbers/first_gradient_reset.py --device cpu --threads 4 --limit 256` (Wächter PID 23656).
- **Gewünschte Maßnahme:** PID 18524 beenden (der Wächter endet dann selbst). Wenn nicht: nichts tun, der Test endet von selbst (nur 256 Fakten je Arm).
- **Warum nichts verloren geht:** reiner Zeittest ohne Ergebnisbedeutung, schreibt nur `first_gradient_reset_limit256.json`; den echten Lauf rechne ich später auf der GPU.

## Gerade

- EXP-131 läuft (CPU, Minuten): Tragen die Zwischenschichten der nachtrainierten Pythia-Modelle die Ziele der Faktenauswahl?
- Beim Dienst jetzt: erster Gradient für EXP-133, dann EXP-132 (Multiplikation), dann EXP-133.

## Als Nächstes

1. EXP-131 auswerten. 2. Paper: LM3 ins Abstract? (nur mit Kürzung, 3 Zeichen frei). 3. Stand sichern vor 21:29.

## Verlauf dieser Sitzung

- 19:55 **EXP-130: „Wiederverwendung“.** Alle vier nachtrainierten Pythia-Modelle brauchen dieselben Frequenzen {1, 2, 11, 23, 56}, egal welche Fakten sie sahen (meist schon vortrainiert stark; 56 ≈ gerade/ungerade).
- 19:52 Textprüfung LM3-F: Zahlen richtig, 4 Formulierungen übernommen (Nullwert 0.1 beim p, „C̄ > 0“, Grenzen ii/iii).
- 19:46 **LM3-F unabhängig nachgerechnet: identisch** -> Sätze in Anhang K und §7 des Papers eingesetzt; unabhängige Textprüfung läuft.
- 19:25 Erster-Gradient-Job für EXP-133 beim Dienst; CPU-Zeittest zu langsam, Abbruch abgelehnt -> Hinweis oben.
- 19:12 Paper-Sätze für jeden Ausgang der Pythia-Reihe vorab geschrieben (paper/PYTHIA_DEUTUNGEN).
- 19:00 EXP-133 beim Dienst eingereiht. Vorher selbst gefunden und behoben: Ganz zufällige Zahlzeilen hätten den gemeinsamen „ist eine Zahl“-Anteil gelöscht (Anfangsverlust 840). Jetzt bleibt die Mittelzeile, nur das Zahlspezifische wird neu gestartet. Codeprüfung ohne Blocker.
- 18:45 EXP-133 vorbereitet (Selbsttest grün, Auswertung synthetisch getestet, Lesarten vorab).
- 18:35 Literatursuche N61: nicht gefunden (nächstverwandt Zhou et al. 2024, Gegenstück).
- 18:33 Sitzung 62 gestartet, Stand und Dienst geprüft.

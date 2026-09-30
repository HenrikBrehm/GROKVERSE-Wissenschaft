---
tags: [lab/live]
---
# LIVE: Laborsitzung 62

- **Sitzungsstart:** 2026-09-30 18:29 Berlin (16:29Z, vom Runner)
- **Deadline:** 2026-09-30 21:29 Berlin (19:29Z)
- **Zuletzt aktualisiert:** 19:01

## Hinweis für den Assistenten (19:24)

- **Symptom:** Mein eigener CPU-Zeittest (erster Gradient für EXP-133) belegt ≈ 5 Kerne und bremst die LM3-F-Nachrechnung des Dienstes (PID 29844). Mein Abbruch wurde von der Sicherheitsprüfung abgelehnt (Interfere With Workloads).
- **Prozess:** PID 18524, gestartet 30.09. 19:13:09, `python lab/experiments/EXP-133-pythia-reset-numbers/first_gradient_reset.py --device cpu --threads 4 --limit 256` (Wächter PID 23656).
- **Gewünschte Maßnahme:** PID 18524 beenden (der Wächter endet dann selbst). Wenn nicht: nichts tun, der Test endet von selbst (nur 256 Fakten je Arm).
- **Warum nichts verloren geht:** reiner Zeittest ohne Ergebnisbedeutung, schreibt nur `first_gradient_reset_limit256.json`; den echten Lauf rechne ich später auf der GPU.

## Gerade

- EXP-130 Seed 4002: Training fertig (Test 0.99), die Ablation jeder einzelnen Frequenz läuft. Seed 4003 startet danach (≈ 40 min).
- LM3-F-Nachrechnung bei Seed 4016 von 4010–4019.

## Als Nächstes

1. EXP-130 auswerten, sobald beide Seeds fertig sind (≈ 19:50), dann EXP-131 (Zwischenschichten, Minuten). 2. LM3-F-Nachrechnung prüfen -> Paper-Satz + Textprüfung. 3. EXP-132/133 laufen danach beim Dienst.

## Verlauf dieser Sitzung

- 19:00 EXP-133 beim Dienst eingereiht. Vorher selbst gefunden und behoben: Ganz zufällige Zahlzeilen hätten den gemeinsamen „ist eine Zahl“-Anteil gelöscht (Anfangsverlust 840). Jetzt bleibt die Mittelzeile, nur das Zahlspezifische wird neu gestartet. Codeprüfung ohne Blocker.
- 18:45 EXP-133 vorbereitet (Selbsttest grün, Auswertung synthetisch getestet, Lesarten vorab).
- 18:35 Literatursuche N61: nicht gefunden (nächstverwandt Zhou et al. 2024, Gegenstück).
- 18:33 Sitzung 62 gestartet, Stand und Dienst geprüft.

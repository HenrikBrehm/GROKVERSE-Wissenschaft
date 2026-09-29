---
tags: [lab/live]
---
# LIVE: Laborsitzung 47

- **Sitzungsstart:** 2026-09-29 03:29 Berlin (01:29Z, vom Runner)
- **Deadline:** 2026-09-29 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 03:40 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

EXP-109 läuft (112 Läufe, 10 GPU-Worker): Pilot bei Lernrate 2e-3, um das Schrittraster der Bestätigung von N54b (Festlegung ∝ √(N/B)) festzulegen. Parallel: Bestätigungsskript `confirm_n54b.py` (frische Seeds 3900+), Literatursuche.

## Als Nächstes

Pilot auswerten → Registrierung N54b einfrieren → Block (≈ 1100 Läufe, ≈ 90 min GPU) starten; währenddessen Paper (Regel 20d).

## Verlauf dieser Sitzung

- 03:40 Prüfung des Bestätigungsskripts: kein Blocker; 4 Punkte übernommen. Full-Batch-Arm gestrichen (teuer; Modell sagt Sättigung dort) → 840 Läufe.
- 03:40 Literatur: keine Arbeit mit dieser Wurzel-Skalierung gefunden; Adam/Sign-Modell sagt α = 0.5 und Halbierung bei doppelter Lernrate voraus.
- 03:40 Paper: Abb. 4 englisch; Langfassung §3.18 (L0-Bestätigung).

- 03:36 Bestätigungsskript confirm_n54b.py: Selbsttest ok.
- 03:33 EXP-109 festgelegt (Commit 9804ce01) und gestartet.
- 03:30 Stand gelesen; keine laufenden Prozesse; Fenster offen.

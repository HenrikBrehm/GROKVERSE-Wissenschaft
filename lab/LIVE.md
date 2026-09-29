---
tags: [lab/live]
---
# LIVE: Laborsitzung 47

- **Sitzungsstart:** 2026-09-29 03:29 Berlin (01:29Z, vom Runner)
- **Deadline:** 2026-09-29 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 03:46 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

Letzte Prüfung der geänderten Registrierung N54b (H1: Wurzel-Uhr bei lr 1e-3; H2: die doppelte Lernrate beschleunigt bei kleinen Batches weniger). Danach einfrieren und 840 Läufe starten (≈ 65 min GPU).

## Als Nächstes

Einfrieren, Smoke, Block starten; währenddessen Paper und Tageserklärung.

## Verlauf dieser Sitzung

- 03:46 **EXP-109:** doppelte Lernrate halbiert die Festlegungszeit bei großen Batches (1024: 31 statt 62 Schritte), bei B 64 nur ×0.75 → Registrierung umgestellt (H2: gepaarte Exponent-Differenz > 0).

- 03:40 Prüfung des Bestätigungsskripts: kein Blocker; 4 Punkte übernommen. Full-Batch-Arm gestrichen (teuer; Modell sagt Sättigung dort) → 840 Läufe.
- 03:40 Literatur: keine Arbeit mit dieser Wurzel-Skalierung gefunden; Adam/Sign-Modell sagt α = 0.5 und Halbierung bei doppelter Lernrate voraus.
- 03:40 Paper: Abb. 4 englisch; Langfassung §3.18 (L0-Bestätigung).

- 03:36 Bestätigungsskript confirm_n54b.py: Selbsttest ok.
- 03:33 EXP-109 festgelegt (Commit 9804ce01) und gestartet.
- 03:30 Stand gelesen; keine laufenden Prozesse; Fenster offen.

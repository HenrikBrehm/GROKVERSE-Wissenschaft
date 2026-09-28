---
tags: [lab/live]
---
# LIVE: Laborsitzung 36

- **Sitzungsstart:** 2026-09-27 23:39 Berlin (21:39Z, vom Runner)
- **Deadline:** 2026-09-28 02:39 Berlin (00:39Z)
- **Zuletzt aktualisiert:** 01:52 Berlin
- **Run-Fenster:** offen seit 01:30, heute bis 18:00.

## Gerade

P2f-Block (D₅₉, 40 Läufe à 12 000 Schritte, 8 GPU-Prozesse) seit 01:48; CPU rechnet EXP-040 (1 × 4 Threads). Ich beobachte beide Läufe.

## Als Nächstes

Nach P2f: `confirm_p2f.py --analyze`, dann `C4_analyze.py`. Was um 02:39 abbricht, startet Sitzung 37 (03:14) mit denselben Befehlen neu; danach EXP-074/075, EXP-086/085, Repro, EXP-078/077, Bestätigungen ([[NACHT_2026-09-28]]).

## Verlauf dieser Sitzung

- 01:49 **EXP-079** (Kopf-Symmetrie, beschreibend): praktisch symmetrisch, kaum Positionsinformation am „=“; 2/320 Köpfe asymmetrisch.
- 01:49 **EXP-073** (Pilot Zurückspulen, 140 Läufe): *gemischt*, Teil-Redundanz. W_E und der Rest nehmen einzeln je ≈ 1/3 der Festigkeit weg, zusammen alles.
- 01:48 P2f-Block gestartet (Smoke und Lader ok um 01:35).
- 01:31 **EXP-021 bestätigt** (22/23 gerade Oberwellen, p = 7e-22); **EXP-019: M0c besser** (p = 0.0012); **N45** nicht auswertbar (MLP-Top-5 = Ziele).
- 01:30 Selbsttests C1/C2, R4, R7, EXP-078/073/075 grün; CPU (EXP-040/014), P2f-Smoke und EXP-073 gestartet.
- 23:40–01:30 Gewartet (Fenster gesperrt); Sitzung 35 hatte sich mit einem Hintergrund-Wecker selbst beendet.

---
tags: [lab/live]
---
# LIVE: Laborsitzung 46

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 01:12 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

GPU: R11 (138/240) und L0-SGD-Kalibrierung (10 Läufe) laufen. Danach startet automatisch die B = 16-Sonde (18 Läufe). CPU: RFM mit 60 Iterationen (Arm R). Ein unabhängiger Agent rechnet Nanda nach.

## Als Nächstes

Kalibrierung lesen → `SGD_LR` setzen → L0-Pilot (144 Läufe) starten. R11 auswerten, sobald fertig.

## Verlauf dieser Sitzung

- 01:10 B = 16-Sonde festgelegt (lernt das Netz bei B = 16 mit kleinerer Lernrate oder weniger Weight Decay?).
- 01:06 **L0-Machbarkeit:** B = 256 keine Reihenfolge-Wirkung (wie vorhergesagt); B = 64 knapp nach der Regel → Konfliktarm B = 64 kommt in den Piloten; B = 16: Reihenfolge dominiert, **aber das Netz lernt dort gar nicht** → kein Konfliktarm bei B = 16.
- 01:05 Vorab-Vorhersage (Maskenspektrum) an unberührten Läufen: „unklar“ (knapp unter der Schwelle).
- 01:00 R10 als §3.16 ins Paper (Langfassung).
- 00:53 L0-Machbarkeit gestartet; RFM-Wiederholung mit 60 Iterationen gestartet.
- 00:52 R11 eingefroren und gestartet (5 GPU-Worker).
- 00:50 RFM (EXP-101): Tor nicht bestanden (generalisiert nach 30 Iterationen nicht, steigt aber noch) → Ausweichregel 60 Iterationen.

---
tags: [lab/live]
---
# LIVE: Laborsitzung 35

- **Sitzungsstart:** 2026-09-27 23:19 Berlin (21:19Z, vom Runner)
- **Deadline:** 2026-09-28 02:19 Berlin (00:19Z)
- **Zuletzt aktualisiert:** 23:35 Berlin
- **Run-Fenster:** gesperrt bis Mo 28.09. 01:30 (Nutzer), dann bis 18:00.

## Gerade

Vorbereitung abgeschlossen. Ich warte ohne Modellanfragen bis 01:29 (Hintergrund-Wecker) und starte dann die Läufe. Der Prüfagent fand in den übrigen ungetesteten Nachtskripten keinen relevanten Fehler.

## Als Nächstes (Plan für 01:30–02:09)

1. `--check`, dann die offenen Selbsttests: C1/C2-Wrapper, `confirm_r4.py`, `confirm_r7.py`, `EXP-078/analyze.py`, `EXP-073/075 analyze.py` (Sekunden); dazu die Auswertungen EXP-021, EXP-019 (`--device cuda`) und N45.
2. CPU: `night_program.py --cpu --cpu-workers 1 --experiments EXP-040,EXP-014` (4 Threads), daneben 8 GPU-Prozesse (Summe 12).
3. GPU: P2f-Smoke (Jobzeile 1) → `--analyze` nur als Ladertest → `P2f_jobs.txt --workers 8` (≈ 30 min).
Was um 02:19 abgebrochen wird, nimmt die nächste Sitzung mit denselben Befehlen wieder auf.

## Verlauf dieser Sitzung

- 23:33 **Zyklen 7–9:** Literatur zu Oberwellen (He et al.: im MLP nur ungerade Oberwellen in den Eingangsgewichten); N45 vorab festgelegt (gerade Oberwellen in W_E: Transformer gegen MLP); Prüfagent: keine relevanten Fehler in EXP-073/075/077/079/083.
- 23:30 **Zyklen 5–6:** EXP-021 (seit Sitzung 5 registriert, nie gerechnet) und EXP-019 (jetzt über die GPU-Läufe von EXP-018 auswertbar, Nachtrag c vor jeder Statistik) für 01:30 vorbereitet.
- 23:27 **Zyklus 4:** EXP-078-Trainerpfad und weitere ungetestete Pfade gelesen: kein Befund.

- 23:26 `confirm_r4.py` statisch gelesen (Import-Hülle, Jobformat, Selbsttest): kein Befund.
- 23:25 **Zyklus 3:** C1/C2-Selbsttest-Wrapper korrigiert (591c8e8). C1/C2 enthalten selbst `permutation(5.0)`, und `permutation(5)` erzeugt Rang-Gleichstände (57 % je Block) → `TieError`. Die gegateten Dateien bleiben unverändert.
- 23:25 **Zyklus 2:** R7-Änderungen aus Sitzung 34 statisch nachgelesen: kein Fehler.
- 23:22 **Zyklus 1:** Abnahmeregel der Repro-Vergleiche vor der Gleichwertigkeitsprüfung festgelegt (6011803).
- 23:20 Start: kein STOP, keine Python-Prozesse, Wächter Exit 3 (Fenster zu bis 01:30). EXP-040: 6/8 Referenzläufe fertig, Seed 31 hat verwaiste Sperren (werden übernommen).

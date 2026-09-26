---
tags: [lab/live]
---
# LIVE: Laborsitzung 18

- **Sitzungsstart:** 2026-09-27 00:39 Berlin (22:39Z, vom Runner)
- **Deadline:** 2026-09-27 03:39 Berlin (01:39Z)
- **Zuletzt aktualisiert:** 00:46 Berlin (gemessen)
- **Run-Fenster:** zu bis 03:00 (Regel 18). Diese Sitzung hat 03:00–03:39 im Fenster.

## Gerade

Ein zweiter Prüfer liest den neuen GPU-Komponententest (Forward, Backward, AdamW, Wiederholung, Astra-Punkt 9) gegen, nur lesend.
Danach committe ich den Test.

## Als Nächstes

03:00: Wächter-Abnahme (60-s-Job + STOP, dazu eine venv-Probe), Tests über den Wächter, danach ≈ 03:12 das Nachtprogramm (GPU-001 zuerst)
im Hintergrund. Es wird um 03:39 an der Deadline angehalten; die nächste Sitzung setzt mit demselben Befehl fort.

## Verlauf dieser Sitzung

- ≤ 00:45 Lücke gefunden: Die GPU-Abnahme prüfte nur ganze Läufe, nicht Forward/Backward/AdamW/Wiederholung einzeln (Astra 9). Stufe „components“ mit vorab festen Kriterien gebaut (ungetestet).
- ≤ 00:45 Venv-Frage per Quelltext geklärt: Der Python-Starter hängt sein Kind an ein eigenes Job-Objekt, es stirbt also mit. Abnahmeskript mit drei Proben gebaut (`accept_guard.ps1`).
- 00:40 Sitzung gestartet: Fenster zu (Exit 3), kein STOP, keine Python-Prozesse. Sitzung 17 endete schon 00:38.

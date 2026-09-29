---
tags: [lab/live]
---
# LIVE: Laborsitzung 49

- **Sitzungsstart:** 2026-09-29 08:49 Berlin (06:49Z, vom Runner, nach Absturz von Sitzung 48 um 08:24)
- **Deadline:** 2026-09-29 11:49 Berlin (09:49Z)
- **Zuletzt aktualisiert:** 08:55 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe laufen jetzt über den GPU-Dienst (Regel 21).

## Gerade

- GPU-Dienst: `20_s48c_r0long_10k` (60 Läufe, 8 Worker: EXP-102 „r0 lang“ + EXP-112 „10k“).
- EXP-105-Pilot, Fortsetzung der 2 offenen Läufe **gescheitert**: Fehler beim Laden des Checkpoints (RNG-Zustand landet auf der GPU). Die zwei abgestürzten Trainerprozesse hängen und blockieren 2 Worker bis ≈ 10:20 (Wächter-Grenze 90 min). **Beenden wurde mir nicht freigegeben – Entscheidung beim Nutzer.** Reparatur liegt bereit (`resume_wrapper.py`, Run-ID bleibt gleich).

## Als Nächstes

Sobald die hängenden Jobs weg sind: Pilot-Fortsetzung mit dem Wrapper einreihen. Bis dahin: Paper (Regel 20d) und Tagesbericht.

## Verlauf dieser Sitzung

- 08:53 queue_s48c über die Inbox eingereiht (läuft, 8 Worker).
- 08:51 Pilot-Fortsetzung über die Inbox: RNG-Fehler beim Laden entdeckt, Wrapper geschrieben.

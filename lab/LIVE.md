---
tags: [lab/live]
---
# LIVE: Laborsitzung 6

- **Sitzungsstart:** 2026-09-26 08:29 Berlin (06:29Z, vom Runner)
- **Deadline:** 2026-09-26 11:29 Berlin (09:29Z)
- **Zuletzt aktualisiert:** 08:54 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin), Wächter ok.

## Gerade

**[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] läuft** (seit 08:52, 38 Läufe à ~80 s, fertig ~09:45).
Frage: Lernt ein Netz mit quadratischer Aktivation auf den EXP-016-Splits die *halben* Zielfrequenzen statt der Ziele?
Das sagt die Theorie (AGF) voraus; der Transformer lernt die Ziele selbst.

## Als Nächstes

EXP-024 auswerten (vorab festgelegt), danach `queue_s5.sh` fortsetzen (Smokes EXP-018/020 → EXP-018).

## Verlauf dieser Sitzung

- 08:52 EXP-024-Hauptserie gestartet. Smoke ok (80 s/Lauf, generalisiert).
- 08:50 Codex-Review von EXP-024: 11 Punkte, 6 übernommen (u. a. Herleitung war unvollständig, Biases raus, invariante Messgröße).
- 08:49 Baseline 19 fertig → alle 10 frischen Baselines da.
- 08:45 **Nebenbefund:** In EXP-016 sind zwei Splits identisch (Seed 12/G = 19/F). Ohne Duplikat bleibt das Ergebnis *steuerbar* (9/9, p ≈ 0.002).
- 08:40 **Neue Idee N11:** Rechnung + Numerik: Ein quadratisches Netz sollte auf denselben Splits die halben Zielfrequenzen bevorzugen (3.3 von 5 statt 0.2). Literatur: nicht gefunden (vorläufig).
- 08:31 Warteschlange gestartet, Baseline 19 lief.
- 08:29 Stand gelesen: kein STOP, keine Python-Prozesse, Branch lab/research.

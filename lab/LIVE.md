---
tags: [lab/live]
---
# LIVE: Laborsitzung 7

- **Sitzungsstart:** 2026-09-26 08:59 Berlin (06:59Z, vom Runner)
- **Deadline:** 2026-09-26 11:59 Berlin (09:59Z)
- **Zuletzt aktualisiert:** 09:09 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

**[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] läuft weiter** (aus Sitzung 6 übernommen, 7/38 Läufe fertig,
~83 s/Lauf, Ende ~09:45). Frage: Lernt ein quadratisches Netz die *halben* Zielfrequenzen, ein ReLU-Netz die Ziele?
Nebenher: Codex prüft das Design des neuen Versuchs [[experiments/EXP-026-parity-crossover/README|EXP-026]].

## Als Nächstes

EXP-024 auswerten → EXP-026 (25 Läufe, ~35 min) → EXP-025 (20 Läufe) → `queue_s5.sh`.

## Verlauf dieser Sitzung

- 09:08 **Neu: EXP-026 vorab festgelegt.** Rechnung: Der ungerade Teil einer Aktivierung lenkt auf die Ziele, der gerade auf die halben Ziele. Der Umschlagpunkt soll zeigen, *wann* im Training die Frequenzwahl fällt.
- 09:01 Literatur geprüft: He et al. 2026 bestätigt, dass ReLU-Endlösungen auf dem geraden Anteil beruhen.
- 09:02 Stand gelesen: kein STOP, EXP-024-Warteschlange läuft (1 Job), Sitzung 6 endete 08:57 nach 27 min.

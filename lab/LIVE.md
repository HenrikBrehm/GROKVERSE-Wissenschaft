---
tags: [lab/live]
---
# LIVE: Laborsitzung 7

- **Sitzungsstart:** 2026-09-26 08:59 Berlin (06:59Z, vom Runner)
- **Deadline:** 2026-09-26 11:59 Berlin (09:59Z)
- **Zuletzt aktualisiert:** 09:23 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

**[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] läuft weiter** (aus Sitzung 6 übernommen, 7/38 Läufe fertig,
~83 s/Lauf, Ende ~09:45). Frage: Lernt ein quadratisches Netz die *halben* Zielfrequenzen, ein ReLU-Netz die Ziele?
EXP-024: quadratischer Arm ausgewertet, ReLU-Arm läuft (Ende ~09:43). Danach startet die Kette EXP-026 → EXP-025 → queue_s5 von selbst.

## Als Nächstes

Kette (startet von selbst nach EXP-024): EXP-026 (30 Läufe) → EXP-027 (15) → EXP-025 (20) → `queue_s5.sh`. Codex prüft EXP-027.

## Verlauf dieser Sitzung

- 09:22 **Neu: EXP-027 vorab festgelegt.** Ab 448 Neuronen muss das Netz nicht wählen (Morwani, Thm 7). Muss ein schmales Netz (32–128) wählen, und folgt es dann dem Split?
- 09:18 **EXP-024 Arm Q: richtungsgleich, n. s.** Das x²-Netz neigt sich wie vorhergesagt zu den halben Zielen (p = 0.002), aber nur schwach (1.1 statt ≥ 2 von 5). Überraschung: Das Netz nutzt fast *alle* Frequenzen gleich stark; der Split kippt nur die Gewichtung.
- 09:15 Codex hat EXP-026 zerlegt (6 Einwände, alle berechtigt). Umgebaut zu einem Umschaltversuch: bis Schritt t mit Aktivierung 3x + x², danach x². Ab welchem t bleibt die Wahl?
- 09:08 **Neu: EXP-026 vorab festgelegt.** Rechnung: Der ungerade Teil einer Aktivierung lenkt auf die Ziele, der gerade auf die halben Ziele. Der Umschlagpunkt soll zeigen, *wann* im Training die Frequenzwahl fällt.
- 09:01 Literatur geprüft: He et al. 2026 bestätigt, dass ReLU-Endlösungen auf dem geraden Anteil beruhen.
- 09:02 Stand gelesen: kein STOP, EXP-024-Warteschlange läuft (1 Job), Sitzung 6 endete 08:57 nach 27 min.

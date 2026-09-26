---
tags: [lab/live]
---
# LIVE: Laborsitzung 7

- **Sitzungsstart:** 2026-09-26 08:59 Berlin (06:59Z, vom Runner)
- **Deadline:** 2026-09-26 11:59 Berlin (09:59Z)
- **Zuletzt aktualisiert:** 09:48 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

**[[experiments/EXP-026-parity-crossover/README|EXP-026]] läuft** (seit 09:44, 30 Läufe à ~88 s, Ende ~10:30).
Frage: Wenn ein Netz erst mit Aktivierung 3x + x² (zieht zu den Zielen) und ab Schritt t mit x² (zieht zu den halben
Zielen) trainiert: Ab welchem t bleibt die erste Neigung? Das misst, *wann* sich das Netz festlegt.

## Als Nächstes

Kette läuft von selbst weiter: EXP-027 (Breite, 20 Läufe) → EXP-025 (20) → `queue_s5.sh`. Auswertungen je danach.

## Verlauf dieser Sitzung

- 09:47 **Neu: EXP-028 vorab festgelegt.** In allen 20 alten Transformer-Läufen stehen während des Auswendiglernens genau die Split-Frequenzen oben; erst beim Generalisieren kommen Oberwellen dazu. Bestätigung an frischen Läufen folgt.
- 09:44 EXP-026 gestartet. Smoke ok; das Netz mit starkem linearem Anteil memoriert allerdings nur.
- 09:43 **EXP-024 fertig.** ReLU: Ziele F sofort und fast vollständig (4.8/5, p = 2e-6), wie vorhergesagt, aber ohne Generalisierung. x²: nur schwache Neigung zu den halben Zielen. Richtung beider Arme wie vorhergesagt.
- 09:31 Beobachtung: Die ReLU-Netze aus EXP-024 memorieren nur (Test 3–9 %). Bei EXP-025 vorab vermerkt.
- 09:29 Codex zu EXP-027: 4 Einwände übernommen (u. a. faire Statistik für schmale Netze, Güte-Schwelle, Breite 256 dazu).
- 09:22 **Neu: EXP-027 vorab festgelegt.** Ab 448 Neuronen muss das Netz nicht wählen (Morwani, Thm 7). Muss ein schmales Netz (32–128) wählen, und folgt es dann dem Split?
- 09:18 **EXP-024 Arm Q: richtungsgleich, n. s.** Das x²-Netz neigt sich wie vorhergesagt zu den halben Zielen (p = 0.002), aber nur schwach (1.1 statt ≥ 2 von 5). Überraschung: Das Netz nutzt fast *alle* Frequenzen gleich stark; der Split kippt nur die Gewichtung.
- 09:15 Codex hat EXP-026 zerlegt (6 Einwände, alle berechtigt). Umgebaut zu einem Umschaltversuch: bis Schritt t mit Aktivierung 3x + x², danach x². Ab welchem t bleibt die Wahl?
- 09:08 **Neu: EXP-026 vorab festgelegt.** Rechnung: Der ungerade Teil einer Aktivierung lenkt auf die Ziele, der gerade auf die halben Ziele. Der Umschlagpunkt soll zeigen, *wann* im Training die Frequenzwahl fällt.
- 09:01 Literatur geprüft: He et al. 2026 bestätigt, dass ReLU-Endlösungen auf dem geraden Anteil beruhen.
- 09:02 Stand gelesen: kein STOP, EXP-024-Warteschlange läuft (1 Job), Sitzung 6 endete 08:57 nach 27 min.

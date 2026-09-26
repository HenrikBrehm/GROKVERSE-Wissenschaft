---
tags: [lab/live]
---
# LIVE: Laborsitzung 7

- **Sitzungsstart:** 2026-09-26 08:59 Berlin (06:59Z, vom Runner)
- **Deadline:** 2026-09-26 11:59 Berlin (09:59Z)
- **Zuletzt aktualisiert:** 10:57 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

**[[experiments/EXP-032-early-lockin/README|EXP-032]] läuft** (12/20, Ende ~11:09): Wie viele Schritte mit linearem Anteil
reichen, um die Frequenzwahl festzulegen: 1, 5, 10 oder 20? Danach von selbst EXP-027b (~15 min) → EXP-025.

## Als Nächstes

Auswertungen in dieser Reihenfolge, sobald die Läufe fertig sind. Sitzungsende 11:59; Abschluss ab ~11:45.

## Verlauf dieser Sitzung

- 10:38 EXP-027 *nicht auswertbar* (32er-Netze generalisieren nicht); beschreibend kein Breiten-Trend. Wiederholung EXP-027b mit frischen Splits vorab festgelegt.
- 10:32 **EXP-026 fertig:** Schon 50 Schritte mit Aktivierung 3x + x² legen die Frequenzwahl eines x²-Netzes fest (5/5, danach ändert sich nichts mehr). Der vorab gewählte Test passte nicht zur Stufenform → formal n. s.; Folgeversuch EXP-032 mit feinem Raster festgelegt.
- 10:10 EXP-031 zurückgestellt: Codex zeigte, dass der Versuch so nicht trennen kann, ob die Init oder der Split wirkt. Umbau später.
- 10:02 **Neu: EXP-031 vorab festgelegt:** Eingriff statt Korrelation. Einbettung von Lauf A bei Schritt 500 in Lauf B verpflanzen; folgt die Frequenzwahl A oder B? Codex prüft.
- 09:59 **EXP-030: Die Wirkung des Splits auf die Endfrequenzen läuft fast vollständig über den Zustand der Einbettung bei Schritt 250** (10/10 Seeds). Codex hatte diese Prüfung verlangt.
- 09:53 Kontrolle: Der Abdruck ist spezifisch für die eigene Trainingsmaske (fremde Masken: ≈ 0).
- 09:50 **EXP-029 teilweise bestätigt:** Auch bei normalen Zufallssplits prägt das Auswendiglernen das Muster der Trainingsdaten in die Einbettung ein (10/10 frische Seeds). Codex greift die Deutung gerade an.
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

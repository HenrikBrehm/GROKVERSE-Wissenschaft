---
id: EXP-084
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, programm/A, paper, neu/kandidat]
---
# EXP-084: Dosis-Kurve der Grokking-Beschleunigung: sättigt sie oder kehrt sie bei extremer Konzentration um? (Exploration, frische Seeds)

Zurück: [[LAB]] · [[FINDINGS]] (Beobachtung „konstruierte Splits groken früher“, Ergänzung Sitzung 31: Dosis-Wirkung) · Bestätigung: [[confirm/R5_REGISTRATION_DRAFT|R5]] · Anlass: `EXP-042-bias-strength/posthoc_speed_dose.py` ([[JOURNAL]] Sitzung 31, Zyklus 2) · [[NOVEL_DIRECTIONS]] N6.

**Status:** vorbereitet, Sitzung 31 (2026-09-27, 20:14 Berlin, gemessen), vor jedem Lauf. Splits erzeugt (reine Rechnung). Jobliste, Smoke und `analyze.py` fertig, **ungetestet**. **Exploration, kein Urteil für FINDINGS**; frische Seeds, damit die Form der Kurve nicht an gesehenen Seeds bestimmt wird.

## Frage und Bezug

Post hoc (Seeds 30, 31, 32, 34) generalisieren Splits umso früher, je konzentrierter ihr Paarspektrum ist (ε 1 / 2 / 8). Offen ist die **Form** der Kurve: Wird es mit weiter steigender Konzentration immer schneller, sättigt es, oder kehrt es sich bei extremer Konzentration um (zu wenige „Nicht-Ziel“-Paare, extreme Ziehgewichte)? Das betrifft die Paper-Beobachtung (§4) und die Frage, wie man Trainingsdaten für schnelles Grokking wählt. R5 prüft nur ε 1 gegen 8 (sekundär).

## Aufbau (vorab festgelegt)

| Punkt | Festlegung |
|---|---|
| Einheiten | 10, Init-Seeds **2780–2789** (reserviert), eigene Split-Ströme `SeedSequence([20261002, u, …])`, keiner aus dem Init-Seed |
| Arme je Einheit | R (gleichverteilt) und ε ∈ {0.5, 1, 2, 4, 8, 16, 32} (Konstruktion EXP-016/018, Untergrenze 0.05), **gleiche** Testmenge (20 %), Schlüssel, Wellenphasen und Ziele A; Arme unterscheiden sich nur in ε |
| Realisierter M0-Zielanteil (Rechnung vor dem Lauf) | R 0.08–0.10, ε 0.5 0.09–0.10, 1 0.11–0.12, 2 0.17–0.18, 4 0.27–0.28, 8 0.35–0.36, 16 0.39–0.41, **32 0.42–0.44**. Die Konstruktion sättigt: ε 16/32 prüfen vor allem extremere Ziehgewichte, kaum mehr Konzentration |
| Training | freq_ban, GPU, `--threads 1`, 4000 Schritte, `--stop-after-gen 100`, Spektrum bei 250; Reihenfolge der 80 Läufe fest gemischt |
| Ereignis | erste Kreuzung des Trainers (Test ≥ 0.95); zensiert bei 4000. Exploration: die erste Kreuzung reicht (R5 verlangt 3 Auswertungen) |
| Lesarten (beschreibend, je Einheit; mehrere können zugleich gelten) | **monoton:** Spearman(Konzentrationsrang, log2 b) ≤ −0.8 in ≥ 8/10 Einheiten. **Umkehr:** b(ε 32) > b(ε 8) in ≥ 7/10 Einheiten und Median log2(b32/b8) ≥ 0.25. **Sättigung:** \|Median log2(b32/b8)\| ≤ 0.25 |
| Beschreibend | Median b je Arm, beobachtete Ereignisse, W_E-Zielanteil bei 250, M0-Zielanteil, Endgenauigkeit |
| Was gegen die Beobachtung spräche | ε 2 < ε 8 nicht in der Mehrheit der Einheiten (dann trägt schon der Befund aus Sitzung 31 nicht) |
| Budget | 80 Läufe; konstruierte Arme ≈ 500–1000 Schritte, R und kleine ε bis 4000; GPU bei 8–10 parallel ≈ 15 min |
| Bereits gesehen | EXP-020/042 (Seeds 30, 31, 32, 34) für ε 1/2/8; daraus die Wahl des Bereichs. Keine Läufe mit 2780–2789 |

**Neuheit:** Die Suche vom 2026-09-27 ([[paper/lit_grokking_speed_2026-09-27]]) fand keine Beschleunigung über die Konzentration des Paarspektrums; eine Dosis-Kurve wurde dort ebenfalls nicht gefunden (vorläufig, keine neue Suche).

## Reproduktion (im Fenster, alles über den Wächter)

```
python lab/experiments/EXP-084-dose-curve/make_splits.py                     # reine Rechnung, prüft vorhandene Dateien bitgleich
python lab/tools/guarded_run.py -- python lab/experiments/EXP-084-dose-curve/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-084-dose-curve/smoke.txt --workers 1
python lab/tools/parallel_queue.py lab/experiments/EXP-084-dose-curve/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-084-dose-curve/analyze.py
```

---
id: EXP-010
status: vorbereitet
datum: 2026-09-25
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]", "[[experiments/EXP-003-early-prediction/CONFIRM_d|EXP-003d]]", "[[experiments/EXP-002-destined-ban/README|EXP-002]]"]
---
# EXP-010: Frequenzwahl per Init-Tausch steuern

**Status:** vorbereitet, **noch nicht ausgeführt**. Definition fixiert am 2026-09-25 um ~22:10 Berlin
(Sitzung 3), außerhalb des Run-Fensters. Code: Bedingung `init_swap` in
`lab/experiments/EXP-001-freq-ban/freq_ban.py`, Unit-Check in `test_freq_ban.py`, Auswertung
`analyze.py`. **Alles ungetestet.** Kriterienänderungen gehören in EXP-010b.

Backlog: [[BACKLOG]] (EXP-010) · Kandidat [[NOVEL_DIRECTIONS]] (N2)

## Warum

[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]] zeigt: Die späteren Top-5-Frequenzen
liegen im Init-Spektrum von `W_E` überdurchschnittlich weit oben, und zwar seed-spezifisch. Die
W_E-Init ist randomisiert, das spricht im Populationssinn schon für einen Einfluss. Offen bleibt
die **Steuerbarkeit im Einzelfall**: Wandert die Frequenzwahl mit, wenn man bei **sonst identischem
Lauf** (gleicher Split, gleiche übrige Gewichte) nur die Init-Koeffizienten zwischen den stärksten
und schwachen Frequenzen tauscht? Der Tausch erhält die iid-Normalverteilung der Init exakt.
Er ist also kein Eingriff „außerhalb der Verteilung“, er vertauscht nur die Etiketten.

| | |
|---|---|
| **Fragestellung** | Folgt die finale Frequenzmenge beim Transformer den Init-starken Koeffizienten, wenn diese auf andere Frequenzen verschoben werden? |
| **Hypothese H10** | Nach dem Tausch enthält K_end mehr S- und weniger T-Frequenzen als die Baseline desselben Seeds |
| **Null** | Der Tausch ändert K_end nicht systematisch, d̄ ≤ 0 oder nicht signifikant |
| **Bedingungen** | `baseline` = die EXP-003d-Läufe (Seeds 10–19, `--stop-after-gen 25`), werden wiederverwendet · `init_swap`: T = die 5 stärksten Init-Frequenzen von `W_E[:p]`, S = 5 Frequenzen aus den Init-Rängen ≥ 11 (gezogen mit seed + 20011). Paarweise werden die (cos, sin)-Koeffizienten getauscht, T absteigend nach Power, S aufsteigend nach k. Die '='-Zeile bleibt, sonst ändert sich nichts |
| **Seeds** | 10–19 (frisch, dieselben wie EXP-003d) |
| **K_end** | `final_top_m_freqs` (Top-5 bei Laufende, also Crossing + 25 bzw. Cap 15 000) |
| **Primärgröße** | pro Seed d = [\|K_swap∩S\| − \|K_swap∩T\|] − [\|K_base∩S\| − \|K_base∩T\|] |
| **Test** | exakter Vorzeichen-Permutationstest über 10 Seeds (2¹⁰), einseitig (d̄ > 0) |
| **Entscheidung** | *steuerbar*: d̄ > 0 und p < 0.05 · *richtungsgleich, nicht signifikant*: d̄ > 0, p ≥ 0.05 · *widerspricht*: d̄ ≤ 0. Mit weniger als 8 gültigen Paaren ist das Ergebnis *nicht auswertbar* |
| **Gültigkeit eines Paars** | Beide Läufe sind `completed`, der `split_hash` ist gleich, und das Spektrum der Baseline bei Schritt 0 stimmt mit `events.init_swap.power_before` überein (rtol 1e-5). So ist belegt, dass die Init bis auf den Tausch identisch war |
| **Sekundär (nur berichtet)** | Δgen = gen(swap) − gen(base). Aus Symmetriegründen erwartet: ≈ 0. **Unabhängige Replikation von EXP-009** an den frischen Baselines: r̄(0) von K_end im Init-Spektrum, Monte-Carlo-Null wie EXP-009 (n = 10), einseitig, p < 0.05 = *repliziert*. K_end liegt hier bei Crossing + 25, nicht bei 25k |
| **Erwartung** | Nach EXP-009 stammt etwa 1 von 5 Frequenzen aus den Init-Top-5 → d̄ ≈ +1 bis +1.5 |
| **Was gegen H10 spräche** | d̄ ≤ 0, oder d̄ ≈ 0 bei unverändertem K_end |
| **Budget** | 10 neue Läufe, je ≤ 20 min (Wächter), einer nach dem anderen. Voraussetzung sind die 10 EXP-003d-Baselines. s/Schritt kommt aus dem EXP-001-Funktionstest |
| **Grenzen** | nur Transformer, eine Plattform (4 Threads, torch 2.13). Der Tausch verschiebt Amplitude *und* Phase gemeinsam, einzeln ist das nicht getrennt |

## Befehle (im Fenster, nach den EXP-003d-Baselines desselben Seeds)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition init_swap --stop-after-gen 25 --out-root lab/experiments/EXP-010-init-swap/raw
python lab/experiments/EXP-010-init-swap/analyze.py
```

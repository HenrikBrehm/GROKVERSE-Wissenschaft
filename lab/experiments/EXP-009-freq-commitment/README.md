---
id: EXP-009
status: vorbereitet
datum: 2026-09-25
tags: [exp/vorbereitet]
verwandt: ["[[experiments/EXP-002-destined-ban/README|EXP-002]]", "[[experiments/EXP-003-early-prediction/SUMMARY|EXP-003]]"]
---
# EXP-009: Wann legt sich das Netz auf seine Frequenzen fest?

**Status:** Definition fixiert am 2026-09-25 um ~22:05 Berlin (Sitzung 3), **bevor** eine
Frequenzidentität der gespeicherten Läufe über die Zeit angesehen wurde. Diese Läufe hat EXP-003
nur über die *Konzentration* (F6) genutzt, nicht über die Frage, *welche* Frequenzen es sind. Es
wird nur ausgewertet, es läuft kein Training. Kriterienänderungen gehören in EXP-009b.

Backlog: [[BACKLOG]] (EXP-009) · Kandidat in [[NOVEL_DIRECTIONS]] (N2)

## Warum

[[experiments/EXP-002-destined-ban/README|EXP-002]] fragt kausal, ob die „Zielfrequenzen“ eines
Seeds privilegiert sind. Vorher lässt sich billig beobachten, ob diese Frequenzen schon **bei der
Initialisierung** oder früh im Training im Embedding-Spektrum hervorstechen, und ab welchem
Schritt die endgültige Auswahl feststeht (Commitment). Zeigt das Init-Spektrum keine
Information, spricht das für eine Symmetriebrechung durch die Dynamik und gegen eine
„Lotterie“, die schon bei der Initialisierung entschieden ist.

| | |
|---|---|
| **Daten** | 40 Läufe, je 10 Seeds (0–9): `txf_add_p113_wd1.0_frac0.3`, `mlp_add_p113_wd1.0_frac0.3`, `mlp_…_dm572` (alle `training/runs/*_arch25k`) und `m2h_…` (`training/external/twohot10/runs/*_arch25k`) |
| **Objekt** | das Embedding-Objekt der Studie: `W_E[:p]`, bei m2h `W_in[:p]` (wie EXP-003/003b). Spektrum = rfft über die Token-Achse, Leistung summiert über die Modell-Dimensionen, Frequenzen 1..56 |
| **K_final** | Top-5-Frequenzen nach Leistung im Checkpoint 25 000 (m = 5 wie EXP-001/002) |
| **Primärgröße** | r̄(t) = Mittel über die Läufe des mittleren normierten Rangs der K_final-Frequenzen im Spektrum bei Schritt t. Rang 1 = stärkste Frequenz, normiert (Rang−1)/55. Null: 0.5 |
| **Hypothese H9 (Nullhypothese als Arbeitsannahme)** | Bei t = 0 enthält das Spektrum keine Information über K_final: r̄(0) ≈ 0.5 |
| **Test** | einseitig (r̄ < Null). Nullverteilung per Monte Carlo: pro Lauf 5 zufällige verschiedene Ränge aus 1..56, 100 000 Replikate, RNG-Seed 0. Bei iid-Gauß-Init ist das exakt, weil die DFT-Leistungen verschiedener Frequenzen iid sind |
| **Entscheidung (t = 0, alle 40)** | p < 0.05: *Init trägt Information* · p ≥ 0.05: *kein Nachweis von Init-Information*. Die vier Gruppen werden einzeln mitberichtet, zählen aber nicht für die Entscheidung |
| **Sekundär (nicht entscheidend)** | r̄(t) für jeden gemeinsamen Grid-Schritt (0, 500, 1000, 2000, …). **Lock-in-Schritt L** = der früheste Grid-Schritt, ab dem bei allen späteren Grid-Schritten ≥ 4 der 5 K_final-Frequenzen in den Top-5 liegen. Berichtet werden L im Verhältnis zum Generalisierungsschritt g (`first_crossing_step`) und der Anteil der Läufe mit L < g |
| **Was gegen H9 spräche** | r̄(0) deutlich < 0.5 mit p < 0.05 |
| **Grenzen** | Zeigt nur Korrelation. Die kausale Frage beantwortet EXP-002. K_final bei 25k ist eine Definition, keine Wahrheit, weil sich die Top-5 auch spät noch umsortieren können. Die Läufe wurden schon für andere Fragen benutzt |

Reproduktion: `python lab/experiments/EXP-009-freq-commitment/commitment.py`

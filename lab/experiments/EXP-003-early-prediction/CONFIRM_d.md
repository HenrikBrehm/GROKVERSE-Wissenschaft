---
id: EXP-003d
status: vorbereitet
datum: 2026-09-25
tags: [exp/vorbereitet]
verwandt: ["[[experiments/EXP-003-early-prediction/SUMMARY|EXP-003]]", "[[experiments/EXP-010-init-swap/README|EXP-010]]"]
---
# EXP-003d: unabhängige Bestätigung an frischen Seeds (Training nötig)

**Status:** vorbereitet, **noch nicht ausgeführt**. Die Definition wurde am 2026-09-25 um
~17:15 Berlin fixiert, außerhalb des Run-Fensters. Das Auswerteskript ist ungetestet.
Ausführung nur im Fenster 00:00–13:00 Berlin und nur über `guarded_run.py`. Die Läufe von EXP-001
haben Vorrang.

## Warum

EXP-003 (vorab festgelegt) fand F6 bei 2000 im Transformer bei ρ = −0.71. Die Bestätigung war
*teilweise* (MLP-512 ja, MLP-572 nein). EXP-003b (Two-hot-MLP) ergab nur *richtungsgleich, nicht
signifikant*. In der Zeitauflösung EXP-003c (explorativ) wirkt F6 wie ein **Fortschrittsmaß**: Es
sagt etwas voraus, sobald es sich vom Init-Niveau löst. Beim Transformer ist das früh der Fall,
bei der Two-hot-MLP erst um Schritt 10 000. Alle 40 gespeicherten Läufe sind damit **angesehen**.
Eine unabhängige Bestätigung braucht also neue Seeds. Getestet wird nur der Transformer, weil
dort die Exploration am stärksten war.

| | |
|---|---|
| **Hypothese H-E3d** | Beim Transformer (Preset `arch25k`) korreliert F6 bei Schritt 2000 über frische Seeds negativ mit dem Generalisierungsschritt |
| **Daten** | 10 neue Läufe, Seeds **10–19** (neue Splits, nie angesehen). `freq_ban.py --condition baseline` mit 4 Threads und torch 2.13. Das ist innerhalb der Gruppe einheitlich, weicht aber von der Studie ab (1 Thread, torch 2.12.1) |
| **Befehl je Seed** | `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition baseline --stop-after-gen 25 --out-root lab/experiments/EXP-003-early-prediction/raw_d` |
| **Merkmal (primär)** | F6 bei 2000 = Top-8-Anteil von `spectra.npy` im Schritt 2000. Das ist dieselbe Größe wie in EXP-003, weil die orthonormale DFT-Leistung je Frequenz proportional zur rfft-Leistung ist |
| **Sekundär (nur berichtet)** | F6 bei 1000 und bei 4000 |
| **Zielgröße** | `events.generalization_step` (test ≥ 0.95, Raster 25) |
| **Zensur** | Kein Crossing bis 15 000 → Wert 15 001 (geteilter letzter Rang). Bei ≥ 3 zensierten Läufen ist das Ergebnis *technisch nicht auswertbar* |
| **Test** | Spearman ρ, einseitig (ρ < 0), 20 000 Permutationen, RNG-Seed 0 |
| **Entscheidung** | *bestätigt*: ρ < 0 und p < 0.05 · *richtungsgleich, nicht signifikant*: ρ < 0 und p ≥ 0.05 · *widerspricht*: ρ ≥ 0 |
| **Budget** | Die Studie brauchte etwa 21 min für 25k Schritte der m2h mit 1 Thread. Für den Transformer mit 4 Threads bis zum Crossing (≈ 6–10k Schritte) gibt es keinen Messwert. Den liefert der EXP-001-Funktionstest (s/Schritt). Ein Lauf ≤ 20 min (Wächter), einer nach dem anderen, über ≥ 2 Sitzungen verteilbar. Jeder abgeschlossene Seed ist für sich gültig |
| **Grenzen** | n = 10. Korrelation ist keine Ursache. Die Bestätigung gilt nur für diese Konfiguration und Plattform |

Auswertung (nach allen 10 Läufen): `python lab/experiments/EXP-003-early-prediction/confirm_d.py`.
Dabei handelt es sich um eine Auswertung, nicht um ein Training.

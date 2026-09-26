---
id: EXP-015
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-014-split-vs-init/README|EXP-014]]", "[[experiments/EXP-012-init-gradient/README|EXP-012]]", "[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]"]
---
# EXP-015: Sagt allein der Trainingssplit die Frequenzen voraus? (Masken-Spektrum)

**Status:** vorbereitet. Definition fixiert 2026-09-26 ~03:15 Berlin (Sitzung 4), **bevor** M0 für irgendeinen
Seed berechnet wurde. Kriterienänderungen gehören in EXP-015b.

## Auslöser

EXP-014-Vorschau (`EXP-014-split-vs-init/grad_preview.py`, explorativ, Seeds 0–9, alle 100 Init×Split-Kombinationen):
Das Leistungsspektrum des ersten Gradienten an W_E hängt am **Split**, nicht an der Init. Die Spearman-Korrelation
mit dem Gradienten bei gleichem Split beträgt 0.34, bei gleicher Init −0.01. In 98 % der Kombinationen liegt der
gleiche Split näher.

Überlegung: Bei Init ist dL/dlogits ≈ 1/p − onehot(c). Der Gradient an Token t ist ungefähr
Σ_c N(t, c) · v(c), mit N(t, c) = 1, falls das Paar (t, c−t) (Token links) bzw. (c−t, t) (Token rechts) im
Training liegt, und zufälligen Vektoren v(c) (Unembedding durch das Netz zurückgespielt). Mittelt man über
zufällige v, hängt die erwartete Leistung bei Frequenz k **nur von der Maske** ab:

M0(k) = Σ_c ( |Σ_t N_links(t, c) e^{−2πikt/p}|² + |Σ_t N_rechts(t, c) e^{−2πikt/p}|² ), für k = 1..56 (k und p−k zusammengefasst).

| | |
|---|---|
| **Fragestellung** | Sagt M0, berechnet nur aus dem Trainingssplit, die finale Frequenzmenge K voraus? |
| **H15** | r̄(M0) < 0.5 (MC-Null wie EXP-009) an frischen Seeds |
| **Maß** | r̄ wie EXP-009/012 (mittlerer normierter Rang von K in der M0-Ordnung, 0 = stärkste) |
| **Exploration** | Seeds 0–9 (K = `k_final`, 25k). Nur berichtet, keine Auswahl mehr nötig (M0 ist parameterfrei) |
| **Bestätigung** | Seeds 10–19 (K = `final_top_m_freqs` der EXP-003d-Baselines). **Primär:** r̄(M0) gegen Null, einseitig, p < 0.05 → *bestätigt*. **Sekundär:** r̄(M0) gegen r̄(E0) und r̄(G0), Vorzeichentest einseitig (M0 besser) |
| **Was dagegen spräche** | r̄(M0) ≈ 0.5 an 10–19; dann trägt die Maske nur über die Wechselwirkung mit den Gewichten |
| **Budget** | reine Rechnung (Split rekonstruieren, FFT), Sekunden; über den Wächter, weil `make_dataset` aufgerufen wird |
| **Grenzen** | M0 ist eine Erwartung über zufällige Rückkopplungsvektoren; Positionsgewichte, Attention und Weight Decay sind ignoriert |

## Befehl

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-015-mask-spectrum/mask_spectrum.py --phase 1
python lab/tools/guarded_run.py -- python lab/experiments/EXP-015-mask-spectrum/mask_spectrum.py --phase 2
```

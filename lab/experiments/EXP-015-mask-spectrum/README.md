---
id: EXP-015
status: laufend
datum: 2026-09-26
tags: [exp/laufend, neu/kandidat]
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

## Phase 1 (Exploration, Seeds 0–9), ausgeführt 2026-09-26 ~03:17 Berlin

`summary_phase1.json`: **r̄(M0) = 0.307** (Null 0.5, MC p < 1e-5), im Mittel 1.3 von 5 Frequenzen in den M0-Top-5
(Zufall 0.45). Zum Vergleich [[experiments/EXP-012-init-gradient/README|EXP-012]]: E0 0.375, G0 0.302. Die Maske allein
ist also so informativ wie der tatsächliche erste Gradient. Explorativ; Bestätigung an Seeds 10–19 (Phase 2) offen.

**Mechanismus-Prüfung** (`m0_vs_g0.py`, 12 s): Spearman zwischen M0 eines Splits und dem tatsächlichen Spektrum des
ersten Gradienten (Mittel über 3 Inits) = **0.57** (Spanne 0.41–0.78, Seeds 0–9); Kontrolle mit fremdem Split −0.07.
Die Formel erfasst also den Hauptteil der Gradienten-Frequenzvorliebe.

**Post hoc (nicht vorab festgelegt):** Das Spektrum der Token-Häufigkeiten erklärt M0 nicht (Spearman ≈ 0) und sagt K
nicht voraus (r̄ 0.497). M0 spiegelt die Paarstruktur des Splits (`count_spectrum_posthoc.py`).

**Post hoc über Architekturen** (`arch_posthoc.py`, nicht vorab festgelegt; gleiche Seeds = gleiche Splits):
r̄(M0) Transformer 0.307 · MLP-512 0.323 · MLP-572 0.329 · **Two-hot-MLP 0.327** (alle MC p < 1e-5). Zum Vergleich
EXP-009, Init-Spektrum: 0.37 / 0.25 / 0.33 / **0.58** (bei der Two-hot-MLP kein Init-Effekt). Das Masken-Spektrum
wirkt also auch dort, wo die Init nichts vorhersagt.
**Kreuz-Architektur-Überlappung** (`cross_arch_overlap_posthoc.py`): Bei gleichem Seed überlappen die finalen Top-5
verschiedener Architekturen in allen 6 Paaren stärker als bei fremdem Seed (0.6–1.0 vs. 0.37–0.56 von 5), einzeln
schwach (Permutations-p 0.015–0.33). Vorsicht: MLP-512/572 teilen wahrscheinlich die W_E-Init (gleiche RNG-Reihenfolge);
nur die Paare mit Transformer bzw. Two-hot-MLP haben verschiedene Init und gleichen Split.

## Nachtrag a (2026-09-26 03:20 Berlin, vor Phase 2; Baselines 11–19 existierten noch nicht)

Exploration Seeds 0–9 (`combined_explore.py`): r̄ E0 0.375 · M0 0.307 · G0 0.302 · Rangmittel(E0, M0) 0.290 ·
**log E0 + log M0: 0.284**. Für Phase 2 kommt als **Sekundärgröße** (nur berichtet, keine Entscheidung) hinzu:
r̄(log E0 + log M0) gegen r̄(M0), einseitiger Vorzeichentest. Die Primärentscheidung (M0 gegen Null) bleibt unverändert.

## Nachtrag b (2026-09-26 ~03:30 Berlin, nach Codex-Review, vor Phase 2)

Codex: Der Vergleich gegen gleichverteilte Ränge schließt eine **allgemeine** Frequenzvorliebe nicht aus, die zufällig
auch jedes Masken-Spektrum hätte; die angekündigten Vergleiche mit E0/G0 fehlten im Code. **Übernommen:**
- **Ko-primär** in Phase 2: passende gegen fremde Masken (Permutation der Zuordnung Lauf → Maske, 20 000 Züge).
  *bestätigt* verlangt jetzt p < 0.05 gegen die Null **und** p_perm < 0.05.
- E0- und G0-Vergleiche implementiert (sekundär).
- **Vorabprüfung an den Explorationsdaten** (`foreign_mask_check.py`, Seeds 0–9, alle 4 Architekturen): passend
  0.307–0.329, fremd 0.49–0.52, p_perm ≤ 5.5e-4 überall. Die Vorhersage ist also **split-spezifisch**, keine
  allgemeine Vorliebe. Das ist Exploration; die Bestätigung bleibt Phase 2.
Nicht übernommen: unabhängig gekreuzte Init/Split-Läufe für EXP-015 selbst. Das leistet
[[experiments/EXP-014-split-vs-init/README|EXP-014]].

---
id: EXP-019
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[experiments/EXP-018-split-speed/README|EXP-018]]", "[[experiments/EXP-012-init-gradient/README|EXP-012]]"]
---
# EXP-019: Kohärentes Masken-Spektrum M0c gegen M0

**Status:** vorbereitet, **nicht ausgeführt** (braucht keine eigenen Läufe, nutzt EXP-018 Arm R und die
EXP-003d-Baselines 18/19). Definition fixiert 2026-09-26 06:11 Berlin (Sitzung 5), bevor einer dieser Läufe existierte.

## Idee

[[experiments/EXP-015-mask-spectrum/README|EXP-015]] leitet M0 als erwartete Leistung des ersten Gradienten an W_E her,
addiert aber die Beiträge von linker Position (t, c−t) und rechter Position (c−t, t) **inkohärent**
(|N̂_links|² + |N̂_rechts|²). W_E ist für beide Positionen dasselbe, und bei Init mischt die Attention beide Positionen
ähnlich; die Beiträge sollten sich also **kohärent** addieren:

M0c(k) = Σ_c |Σ_t (N_links(t, c) + N_rechts(t, c)) e^{−2πikt/p}|², k und p−k zusammengefasst.

Post hoc (Sitzung 5, `EXP-015-mask-spectrum/posthoc/coherent_m0.py`): Exploration Seeds 0–9 r̄ 0.280 (M0c) gegen 0.307
(M0), p 0.14; Seeds 10–17 (schon für die M0-Bestätigung benutzt, daher nur Replikation) 0.222 gegen 0.277, p 0.098.
Rangkorrelation M0/M0c ≈ 0.70. Richtung gleich, einzeln nicht signifikant.

| | |
|---|---|
| **Fragestellung** | Sagt das kohärente Masken-Spektrum die finalen Frequenzen besser voraus als M0? |
| **H19** | r̄(M0c) < r̄(M0) an frischen Seeds |
| **Seeds / Läufe** | EXP-018 Arm R, Seeds 20–29 (gleichverteilte Zufallsmenge aus dem Pool, 3831 Paare) und EXP-003d-Baselines 18, 19. Masken aus den Split-Dateien bzw. `make_dataset` |
| **K** | `final_top_m_freqs` des Laufs (Top-5 von W_E am Laufende; bei EXP-018 gen + 25 oder 8000, falls zensiert) |
| **Maß** | r̄ wie EXP-009/012/015 |
| **Test** | d_i = r̄_i(M0) − r̄_i(M0c); Vorzeichen-Permutationstest einseitig (d̄ > 0), n = 12 |
| **Entscheidung** | *M0c besser*: d̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: d̄ > 0, p ≥ 0.05 · *widerspricht*: d̄ ≤ 0 · < 10 gültige: *nicht auswertbar* |
| **Sekundär** | r̄(M0c) gegen die MC-Null; dasselbe an Arm D (auch dort ist die Anordnung zufällig); M0c gegen G0 (erster Gradient), falls berechnet |
| **Was dagegen spräche** | d̄ ≤ 0: Dann ist die Trennung der Positionen im Transformer real (z. B. durch Positions-Embeddings und Attention), und M0 bleibt die bessere Näherung |
| **Grenzen** | Nur Transformer; die EXP-018-Läufe haben eine andere Testmenge (T*, 20 %) als die Baselines, das betrifft K nur über den Stoppzeitpunkt |

Auswertung: `python lab/experiments/EXP-019-coherent-mask/analyze.py` (nach EXP-018 und den Baselines 18/19).

## Nachtrag (2026-09-26 06:22, Mechanismus, keine Kriterienänderung)

Der tatsächliche erste Gradient an W_E folgt M0c deutlich besser als M0: gemittelt über 3 Inits (Seeds 0–9)
ρ 0.773 gegen 0.571, 10/10; eine Init pro Seed (Seeds 0–17) 0.572 gegen 0.422, 17/18, p 1.1e-5. Fremde Maske ≈ 0.
Skripte `EXP-015-mask-spectrum/posthoc/coherent_vs_*.py`. Das stützt die Herleitung, sagt aber noch nichts darüber,
ob M0c die **finalen** Frequenzen besser vorhersagt (das bleibt H19).
Präzisierung (06:37, nach Codex und direkter Messung `posthoc/positional_gradient.py`): Nicht „kohärent addiert“ im Sinn
gleicher Phase. Über alle Frequenzen heben sich die Kreuzterme zwischen linker und rechter Position auf; frequenzweise
folgt der gemessene Kreuzterm dem Masken-Kreuzterm M0c − M0 (ρ 0.50, 18/18 Seeds positiv, fremde Maske −0.09).

## Herleitung (2026-09-26 06:44, numerisch geprüft)

Mit N_rechts(t, c) = N_links(c − t, c) (Spiegelung entlang der Antidiagonale) gilt N̂_rechts(k, c) = e^{−ikc}·conj(N̂_links(k, c))
(ω = 2π/p in den Exponenten mitgedacht). Daraus:

M0c(k) = 4 Σ_c |N̂_links(k, c)|² · cos²(arg N̂_links(k, c) + πkc/p),  M0(k) = 2 Σ_c |N̂_links(k, c)|².

M0c gewichtet also jede Antidiagonale danach, wie **spiegelsymmetrisch** ihr Paarmuster um a = c/2 ist, d. h. nach der
**Kommutationssymmetrie** des Splits ((a, b) und (b, a) beide im Training). Für eine kommutationssymmetrische Maske ist
M0c = 2·M0 exakt (gleiche Rangfolge). Der ganze Unterschied zwischen M0c und M0 stammt aus der Asymmetrie des Splits.
Numerisch geprüft: Formel gegen `m0c` relative Abweichung ≤ 5e-15; symmetrische Masken M0c/(2·M0) = 1.000.

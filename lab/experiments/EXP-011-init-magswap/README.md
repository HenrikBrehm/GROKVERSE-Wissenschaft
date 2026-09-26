---
id: EXP-011
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-010-init-swap/README|EXP-010]]", "[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]"]
---
# EXP-011: Betrag oder Richtung? Init-Tausch nur der Normen

**Status:** vorbereitet, **noch nicht ausgeführt**. Definition fixiert am 2026-09-26 um ~03:00 Berlin
(Sitzung 4), **bevor** ein EXP-010-Paar ausgewertet war. Code: Bedingung `init_magswap` in
`lab/experiments/EXP-001-freq-ban/freq_ban.py`. Unit-Test `test_init_magswap_moves_power_but_keeps_directions`
lief im Fenster (9/9 ok). Auswertung `analyze.py` (ungetestet). Kriterienänderungen gehören in EXP-011b.

Backlog: [[BACKLOG]] (EXP-011) · [[NOVEL_DIRECTIONS]] (N2)

## Warum

[[experiments/EXP-010-init-swap/README|EXP-010]] tauscht pro Paar (t, s) den ganzen (cos, sin)-Koeffizientenblock
(2 × d_model) von `W_E[:p]`, also Betrag **und** Richtung. Wandert die Frequenzwahl mit, bleibt offen,
was sie trägt: nur die Energie der Frequenz im Embedding, oder die Richtung des Blocks, d. h. wie er zu den
übrigen zufälligen Gewichten (W_pos, Attention, MLP, Unembedding) passt. He et al. 2026 finden pro
Neuron bei zweischichtigen Netzen, dass Betrag und Phase zusammen zählen. Bei gemeinsamem Embedding
in einem Transformer ist das nach unserer Suche nicht getrennt worden (vorläufig, siehe [[NOVEL_DIRECTIONS]]).

`init_magswap` tauscht **nur die Normen** der Blöcke: Block t wird auf die Norm von Block s skaliert
und umgekehrt, jede Frequenz behält ihre eigene Richtung. Das Leistungsspektrum nach dem Eingriff ist
**identisch** mit dem von `init_swap`. Unterschiede zwischen beiden Bedingungen gehen also allein auf
die Richtung zurück. Verteilung: Bei iid-normaler Init sind Norm und Richtung eines Blocks unabhängig,
der Normtausch zwischen zwei Blöcken erhält die gemeinsame Verteilung.

| | |
|---|---|
| **Fragestellung** | Reicht der Betrag allein, um die Frequenzwahl zu verschieben? |
| **Hypothese H11** | Nach dem Normtausch enthält K_end mehr S- und weniger T-Frequenzen als die Baseline desselben Seeds |
| **Null** | d̄_mag ≤ 0 oder nicht signifikant |
| **Bedingungen** | `baseline` = EXP-003d-Läufe (Seeds 10–19) · `init_magswap`: dieselben Paare (t, s) wie EXP-010 (T = Init-Top-5, S gezogen mit seed + 20011) |
| **Seeds** | 10–19 |
| **Primärgröße** | d_mag = [\|K_mag∩S\| − \|K_mag∩T\|] − [\|K_base∩S\| − \|K_base∩T\|] |
| **Test** | exakter Vorzeichen-Permutationstest, einseitig (d̄ > 0), wie EXP-010 |
| **Entscheidung** | *steuerbar*: d̄_mag > 0, p < 0.05 · *richtungsgleich, n. s.*: d̄_mag > 0, p ≥ 0.05 · *widerspricht*: d̄_mag ≤ 0 · < 8 gültige Paare: *nicht auswertbar*. Gültigkeit wie EXP-010 |
| **Sekundär (nur berichtet)** | Richtungsanteil d_swap − d_mag pro Seed, zweiseitiger Vorzeichentest. Δgen |
| **Deutung (vorab)** | EXP-010 steuerbar & EXP-011 steuerbar & Richtungsanteil ≈ 0 → **Betrag trägt**. EXP-010 steuerbar & EXP-011 nicht & Richtungsanteil > 0 → **Richtung (Passung zu den anderen Gewichten) trägt mit**. EXP-010 nicht steuerbar → EXP-011 kaum deutbar |
| **Erwartung** | Betrag trägt den Großteil: d̄_mag ≈ d̄_swap |
| **Budget** | 10 Läufe à ≈ 12–22 min (0.127 s/Schritt, Cap 15 000). Erst nach den EXP-010-Paaren |
| **Grenzen** | nur Transformer, eine Plattform. Die Richtung des 2 × d-Blocks umfasst Phase und Einbettungsrichtung zugleich; beides wird hier nicht getrennt |

## Befehle (im Fenster, nach den EXP-003d-Baselines desselben Seeds)

```
python lab/tools/guarded_run.py --min-minutes 33 -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition init_magswap --stop-after-gen 25 --out-root lab/experiments/EXP-011-init-magswap/raw
python lab/experiments/EXP-011-init-magswap/analyze.py
```

## Nachtrag a (2026-09-26, ~03:10 Berlin, Sitzung 4): nach Codex-Review, vor jedem Lauf

Es gelten die Punkte 1–5 aus dem Nachtrag a zu [[experiments/EXP-010-init-swap/README|EXP-010]] sinngemäß
(ko-primärer Gewinn von S, fail-closed-Gültigkeit, beide Arme müssen kreuzen, kein Exaktheitsanspruch,
rangbedingter Eingriff). Zusätzlich:
- Der Kontrast d_swap − d_mag heißt jetzt **inkrementeller Richtungskontrast**, nicht „Anteil“. Er ist ein
  bedingter Kontrast beim getauschten Normspektrum und kann Wechselwirkungen enthalten. Eine Aussage
  „Betrag trägt allein“ ist ohne vorab festgelegte Äquivalenzgrenze nicht zulässig; berichtet werden Mittel,
  Streuung pro Seed und der zweiseitige Test. Ein reiner Richtungsarm (2×2-Design) bleibt eine Option (EXP-011b).
- Für den Kontrast müssen die Paare (T, S) in beiden Armen identisch sein.
- Die Aussage „der Normtausch erhält die gemeinsame Verteilung“ oben ist zu stark: Er erhält die Multimenge der
  Normen und die Richtungen, ist aber rangbedingt.

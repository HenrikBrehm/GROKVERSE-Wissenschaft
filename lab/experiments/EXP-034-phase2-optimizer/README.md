---
id: EXP-034
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-034: Hält die frühe Festlegung ohne AdamW in Phase 2, und gilt sie schon bei der 5-Schritte-Amplitude?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Vorgänger
[[experiments/EXP-033-optimizer-lockin/README|EXP-033]] · [[experiments/EXP-032-early-lockin/README|EXP-032]].

## Anlass

EXP-033 zeigte: Eine σ_3-Phase mit reinem GD bis zur Amplitude von 10 AdamW-Schritten erzeugt eine bleibende F-Neigung
(10/10). Codex' Angriff auf die Schlussfolgerung (übernommen): (1) Phase 2 war immer AdamW, der **Erhalt** der Neigung
könnte an AdamW hängen; (2) geprüft war nur die Stufe t_s = 10, nicht die 5-Schritte-Stufe; (3) Nachtrag c war eine
ergebnisblinde Protokolländerung, das endgültige Protokoll gehört an frischen Splits bestätigt.

## Versuch (vorab festgelegt 2026-09-26 13:24 Berlin, commit a5c543c, vor jedem EXP-034-Lauf)

| Punkt | Festlegung |
|---|---|
| **Einheiten** | frische EXP-016-Splits (`make_split.py`, ε = 2, Arm F) **Seeds 60–69**; Pilot Split 70. In allen 11 ist M0-Top-5 = Ziele |
| **Code** | `EXP-033/train_opt.py` (Protokoll von EXP-033 Nachtrag c: GD/SIGN mit `--backtrack`, interpolierter Median) mit `--split-dir` und `--opt2` |
| **Teil A (Stufe 5, Phase 2 AdamW)** | Arme: Anker (AdamW, `--switch-step 0`), **AR5** (AdamW 5 Schritte), **GD5** (GD lr 3 aus EXP-033, bis r ≥ r_AR5 des Splits, backtrack). Phase 2: frischer AdamW, 5000 Schritte |
| **Teil B (Phase 2 GD)** | Arme: Anker-GD2 (kein Phase 1), **AR10-GD2**, **GD10-GD2** (r wie AR10). Phase 2: GD ohne Momentum, Weight Decay 1e-3/lr₂ (gleiche Schrumpfung pro Schritt wie AdamW), N₂ Schritte |
| **Pilot B** | Split 70, nur Anker-GD2, lr₂ ∈ {1, 3, 10}, N₂ = 10 000; gewählt: größte lr₂, die endlich bleibt und Test ≥ 0.9 erreicht (`select_lr2.py` → `lr2.json`). Keine gültige lr₂ → Teil B *nicht durchführbar* (dokumentieren, nicht umbauen ohne neuen Nachtrag) |
| **Messgröße** | Δ = ds_Ende − ds_Anker (gleicher Split, gleiche Phase 2), ds wie EXP-032/033 |
| **Tor A** | Δ_AR5 > 0 in ≥ 9/10 (Bestätigung von EXP-032 t_s = 5 an frischen Splits) |
| **Primär A** | k_A = #Splits mit Δ_GD5 > 0; Vorzeichentest, ≥ 9/10 (p = 0.011) |
| **Entscheidung A** | Tor verfehlt → *nicht auswertbar*; k_A ≥ 9 → ***Festlegung bei 1.25 × Init ohne AdamW in Phase 1***; sonst → ***bei der 5-Schritte-Stufe nicht ohne AdamW gezeigt*** |
| **Primär B** | k_AR = #Δ_AR10\|GD2 > 0, k_GD = #Δ_GD10\|GD2 > 0 |
| **Entscheidung B** | beide ≥ 9 → ***Erhalt ohne AdamW*** (die ganze Kette GD → GD legt fest); beide < 9 → ***Erhalt braucht AdamW in Phase 2***; sonst → ***teilweise*** (berichten, welcher Arm) |
| **Gültig** | alle Läufe vollständig, Matching ≤ 2 %, jedes Endnetz Test ≥ 0.9 (Teil B: gilt für die Anker-GD2-Läufe mit; generalisiert ein Anker nicht, zählt der Split in B als ungültig; < 8 gültige Splits → B *nicht auswertbar*, Schwelle dann nicht angepasst) |
| **Sekundär** | ds am Umschaltschritt (GD > AR wie in EXP-033 / linearer Modentheorie?); R = Δ_GD/Δ_AR je Teil; Generalisierungsschritt; lineares Modenmaß ds(J) der neuen Splits gegen ds am Umschaltschritt (Bestätigung des Post-hoc-Befunds aus EXP-033, Spearman > 0 erwartet) |
| **Was dagegen spräche** | A: Δ_GD5 ≈ 0 (bei kleiner Amplitude braucht die Festlegung Adams Vorzeichen-Schritte). B: Δ ≈ 0 unter GD2 (AdamW erhält/verstärkt die Neigung, GD vergisst sie) |
| **Grenzen** | GD2 ist eine andere Dynamik (u. U. langsamere Generalisierung, andere Endlösung); N₂ aus dem Pilot; eine Architektur |
| **Budget** | A: 30 × 1.5 min ≈ 45 min; Pilot B 3 × ~3 min; B: 30 × ~3 min ≈ 1.5 h |

## Befehle

    sh lab/experiments/EXP-034-phase2-optimizer/make_splits.sh        # erledigt 13:23 (über den Wächter)
    sh lab/experiments/EXP-034-phase2-optimizer/queue.sh               # A, dann Pilot B, dann B; überspringt Fertiges
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-034-phase2-optimizer/analyze.py

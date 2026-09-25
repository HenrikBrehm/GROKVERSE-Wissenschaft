# EXP-001 — Frequenzverbot während des Trainings

**Status:** vorbereitet, **noch nicht ausgeführt** (Definition geschrieben 2026-09-25, 13:3x Berlin,
außerhalb des Run-Fensters). Code ungetestet. Diese Definition ist vor jedem Ergebnis fixiert;
spätere Änderungen an Kriterien gehören in einen neuen Versuch (EXP-001b …), nicht hierher.

## Warum

RESULTS.md §8 (H4) zeigt: Strukturmetriken steigen in 10/10 Seeds *vor* dem Generalisierungssprung —
ausdrücklich nur korrelativ. §6 zeigt kausal nur am *fertigen* Modell, dass Key-Frequenzen tragend
sind. Offen ist, ob die **während des Plateaus entstehenden** Frequenzen für den *Übergang* nötig sind
oder ob das Netz bei einem Verbot billig auf andere Frequenzen ausweicht. Das ist ein Eingriff in die
Trainingsdynamik, den die Studie nicht enthält (neu für das Projekt; Neuheit für die Literatur
**nicht geprüft**).

## Definition

| | |
|---|---|
| **Fragestellung** | Verzögert ein Verbot der bei t0 stärksten Embedding-Frequenzen die Generalisierung stärker als ein Verbot gleich vieler zufälliger schwacher Frequenzen? |
| **Hypothese H-E1** | Ja: `ban_emerging` verzögert den Generalisierungs-Crossing deutlich stärker als `ban_random`. |
| **Baseline / Kontrolle** | `baseline` (gleicher Code, kein Eingriff, lokal neu gerechnet) und `ban_random` (m Frequenzen aus Power-Rängen > 2m bei t0, Seed + 10007) |
| **Intervention** | ab t0 = 2000 nach jedem Optimizer-Schritt `W_E[:p] ← (I − P_K) W_E[:p]`, K = Top-m (m = 5) Frequenzen der W_E-Power bei t0. Adam-Momente bleiben unberührt. |
| **Aufgabe/Modell** | Preset `arch25k`: Transformer, p = 113, train_frac 0.3, wd 1.0, AdamW lr 1e-3, full batch, kein Grokfast |
| **Seeds (Exploration)** | 0, 1, 2 — gleiche Splits wie die Primärstudie. Seeds 3–9 bleiben für eine spätere Bestätigung **unberührt**. |
| **Threads** | 4 in allen Bedingungen (weicht von der Studie ab, die 1 Thread nutzt; daher lokaler Baseline-Lauf statt der gespeicherten Läufe als Kontrolle) |
| **Messgrößen** | primär: Generalisierungs-Crossing (test ≥ 0.95, Raster 25 Schritte) · Verzögerung Δ = gen(Bedingung) − gen(baseline, gleicher Seed). Sekundär: Train-/Test-Acc direkt vor/nach dem Eingriff; finale Top-5-Frequenzen und Jaccard mit den finalen Top-5 der lokalen Baseline; W_E-Spektren alle 250 Schritte |
| **Erwartetes Ergebnis** | Δ(ban_emerging) − Δ(ban_random) ≥ 1000 Schritte; das Netz findet danach andere Frequenzen (Jaccard mit Baseline-Final klein) |
| **Gegen H-E1 spricht** | Δ(ban_emerging) ≤ Δ(ban_random) + 500 in ≥ 2 von 3 Seeds |
| **Entscheidungsregel** | *unterstützt*: Δ(ban_emerging) − Δ(ban_random) ≥ 1000 in ≥ 2/3 Seeds (ein bei Cap zensierter `ban_emerging`-Lauf bei nicht zensiertem `ban_random` zählt als ≥ 1000) · *widerspricht*: s. o. · sonst *unklar* |
| **Budget** | Cap 15.000 Schritte, Stopp 2000 Schritte nach dem Crossing; ≤ 20 min pro Lauf (guarded_run), 9 Läufe. |
| **Abbruchkriterium** | Funktionstest zeigt > 0,07 s/Schritt (15.000 Schritte passen nicht in 18 min) → Cap = ⌊18 min / (s/Schritt)⌋; liegt dieser unter 11.000, wird das Design in einem neuen Versuch umgeplant (z. B. train_frac 0.4), nicht still angepasst. |
| **Zensur** | Nicht generalisiert bis Cap ⇒ „> Cap", **nicht** „grokkt nicht". |

Zusatzbedingung `ban_destined` (Top-5 des gespeicherten 25k-Modells ab Schritt 1 verboten) ist
implementiert, gehört aber **nicht** zu diesem Versuch; sie ist als EXP-002 im Backlog.

## Reihenfolge (im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/test_freq_ban.py`
2. Funktionstest (misst s/Schritt, prüft, dass der Eingriff greift):
   `python lab/tools/guarded_run.py --job-minutes 5 --min-minutes 3 -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 0 --condition ban_emerging --t0 100 --steps 300 --out-root lab/experiments/EXP-001-freq-ban/raw_smoke`
3. Plattform-Check: Baseline seed 0 — W_E bei Schritt 2000 gegen `training/runs/txf_add_…seed0_arch25k/ckpt_step002000.pt` (Achtung: 4 vs. 1 Thread, torch 2.13 vs. 2.12 → Abweichung erwartet; nur dokumentieren).
4. Pro Seed 0, 1, 2: `baseline`, `ban_emerging`, `ban_random`, jeweils
   `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition C`
5. `python lab/experiments/EXP-001-freq-ban/analyze.py` → `summary.json`, `SUMMARY.md`

Rohdaten: `raw/` (gitignored). Kompakte Ergebnisse: `summary.json`, `SUMMARY.md` (committet).

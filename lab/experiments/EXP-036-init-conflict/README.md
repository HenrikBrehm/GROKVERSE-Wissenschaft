---
id: EXP-036
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
---
# EXP-036: Kommen die „fremden“ Frequenzen der Mischzustände aus der Initialisierung?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Grundlage [[experiments/EXP-020-data-switch/README|EXP-020]] (Nachtrag d) ·
verwandt [[experiments/EXP-012-init-gradient/README|EXP-012]], [[experiments/EXP-035-warmup-lockin/README|EXP-035]].

## Anlass

EXP-020 (Seeds 30–32, Exploration, `conflict_freqs.py`): Wird nach t ≤ 50 Schritten von Split F auf Split G gewechselt,
enthält das Endnetz Frequenzen, die weder zu F, G, deren 2k-Oberwellen noch zu den Endfrequenzen der reinen Läufe gehören
(z. B. Seed 30: 34, 39). Bei t ≥ 150 nie. Ihre Ränge im Init-Spektrum von W_E sind auffällig klein (Median 8 von 56).
Deutung (Spekulation): Im noch nicht festgelegten Netz heben sich die Datensignale von F und G teilweise auf, und das
Init-Spektrum setzt sich durch. Rangvergleich allein ist nur eine Assoziation; die Init ist hier der Eingriff.

## Versuch (vorab festgelegt 2026-09-26 14:53 Berlin (commit 5730b38), vor jedem EXP-036-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Folgen die fremden Frequenzen der Init (Eingriff: neue Init, gleicher Split) oder dem Split? |
| **H36** | Sie sind init-getrieben: Unter der neuen Init stehen die neuen fremden Frequenzen im **neuen** Init-Spektrum höher als im alten |
| **Alternative** | Split-getrieben: Die fremden Frequenzen hängen nicht von der Init ab; dann ist rank_new < rank_old ein Münzwurf, und die fremden Mengen alt/neu überlappen |
| **Kontrolle** | EXP-020-Läufe derselben Splits mit der alten Init (Seed s); die Init ist der einzige Unterschied |
| **Eingriff** | `--seed s + 100` (130, 131, 132) bei den Splits von Seed s ∈ {30, 31, 32}. Mit `--split-file` bestimmt `--seed` nur Init (und Reihenfolge, full batch) |
| **Läufe je Paar** | nur F (2000 Schritte), nur G (2000), Wechsel F → G bei t = 25, 50, 10 (+ 2000 G-Schritte). 15 Läufe, ≈ 4.3 min je Lauf, ≈ 65 min |
| **Messung** | A = F ∪ G ∪ fold(2k) ∪ K_nurF ∪ K_nurG (reine Läufe **dieser** Init, Top-5 von W_E bei Schritt 2000); fremd = ⋃_{t∈{10,25,50}} Top-5(t + 2000) \ A. Je verschiedene fremde Frequenz k: Erfolg, wenn Rang im neuen Init-Spektrum < Rang im alten (Schritt 0, Rang 1 = stärkste) |
| **Test** | gepoolt über die drei Paare, einseitiger Vorzeichentest (Bin(n, ½)) |
| **Urteil** | n < 5 → *nicht auswertbar*; Anteil ≥ 0.75 und p < 0.05 → *init-getrieben*; Anteil ≤ 0.5 → *nicht init-getrieben*; sonst *unklar*. Fehlt ein Lauf oder ist das Init-Spektrum identisch → *nicht auswertbar* |
| **Sekundär (beschreibend)** | Überlappung der fremden Mengen alt/neu je Split; Median des neuen Init-Rangs; ob die neue Init überhaupt Mischzustände zeigt (Festlegung könnte bei anderer Init früher/später fallen) |
| **Budget / Abbruch** | ≈ 65 min, ein Job; Abbruch bei NaN oder Stillstand. Queue stoppt bei jedem Fehler |

**Was gegen H36 spräche:** Anteil ≤ 0.5, oder die gleichen fremden Frequenzen wie unter der alten Init.
**Grenzen:** n ist klein (erwartet ≈ 5–10 fremde Frequenzen); ein positives Urteil zeigt nur, dass die Init die Wahl im
Mischzustand mitbestimmt, nicht den Mechanismus. Die neue Init kann ein anderes Festlegungsintervall haben; zeigt sie bei
t ∈ {10, 25, 50} keine Mischzustände, ist n klein und der Versuch eher *nicht auswertbar*.

## Reproduktion

```
sh lab/experiments/EXP-036-init-conflict/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-036-init-conflict/analyze.py
python lab/experiments/EXP-036-init-conflict/analyze.py --selftest   # Urteilslogik
```

## Status

Vorbereitet, nicht ausgeführt. Warteschlange erst nach `queue_s8.sh` (EXP-020 → EXP-035 → EXP-034) bzw. im nächsten Fenster.

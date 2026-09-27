---
id: EXP-038
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-038: Wo sitzt die Festlegung, im Embedding W_E oder in den nachgelagerten Gewichten?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N16) · Grundlage
[[experiments/EXP-020-data-switch/README|EXP-020]] · verwandt [[experiments/EXP-033-optimizer-lockin/README|EXP-033]].

## Anlass

EXP-020: Nach 150 Schritten auf F behält der Transformer in 5/5 Seeds exakt die F-Frequenzen, auch nach 2000 Schritten nur auf
G. Gemessen wird die Wahl im Spektrum von W_E. Offen ist, **wo** die Festlegung gespeichert ist: Wird W_E zurückgesetzt und
schreiben die nachgelagerten Gewichte (Attention, MLP, Unembedding) die F-Frequenzen wieder hinein? Oder trägt W_E selbst die
Festlegung, und der Rest folgt?

## Versuch (vorab festgelegt 2026-09-26 16:25 Berlin, vor jedem EXP-038-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Welcher Teil des Netzes hält die Frequenzwahl nach der kritischen Periode fest? |
| **Eingriff** | EXP-020-Protokoll mit t = 150 (F 150 Schritte, dann G 2000). Beim Wechsel setzt Arm **RW** nur W_E auf die Init zurück, Arm **RR** alle übrigen Parameter (jeweils mit ihrem AdamW-Zustand). `freq_ban.py --reset-at-switch we|rest` (neu) |
| **Kontrolle** | EXP-020-Lauf t = 150 ohne Rücksetzen (gleiche Init, gleiche Splits; K = K_nurF in 5/5) |
| **Seeds** | 30–34 (EXP-020) |
| **Messung** | d_h = \|K ∩ Fx\| − \|K ∩ Gx\|, Fx = F ∪ fold(2F), Gx = G ∪ fold(2G), Frequenzen auf beiden Seiten ausgenommen (Lehre aus EXP-020 Seed 33); K = Top-5 von W_E bei Schritt 2150. „umgeschlagen“ = d_h ≤ 0 |
| **Muster je Seed** | *W_E* (RW umgeschlagen, RR nicht), *downstream* (RR umgeschlagen, RW nicht), *redundant* (keiner), *beide* (beide). Seed gültig, wenn alle drei Läufe gültig sind und d_h(Kontrolle) > 0 |
| **Urteil** | < 4 gültige Seeds → *nicht auswertbar*; ≥ 4 gültige Seeds mit demselben Muster → dieses Muster; sonst *gemischt* |
| **Erwartung (vorab, ohne Festlegung auf eine Richtung)** | Plausibel ist *downstream* oder *redundant*: Die nachgelagerten Gewichte haben 150 Schritte lang F-Paare gelernt und dürften den Gradienten an W_E auf F lenken. *W_E* wäre überraschend und hieße: Das Embedding allein trägt die Wahl |
| **Prüfungen** | Frischer Smoke (40 Schritte, Wechsel bei 30, beide Arme): Rücksetzen trifft genau numel(W_E) bzw. den Rest (`check_smoke.py`); strenger Lader wie EXP-020 Nachtrag d; Init-Prüfsumme gleich wie EXP-020 |
| **Budget / Abbruch** | 2 Smokes + 10 Läufe à 2150 Schritte ≈ 46 min; Abbruch bei NaN/Stillstand |

**Grenzen:** Rücksetzen auf die Init ist ein grober Eingriff (Größenordnung der Gewichte ändert sich). *downstream* hieße nicht,
welcher Teil (Attention, MLP, W_U); das wäre ein Folgeversuch. Nur ein Wechselzeitpunkt (t = 150).

## Nachtrag a (16:31 Berlin, nach Codex-Review, **vor jedem EXP-038-Lauf**)

Codex (`codex_review_2026-09-26.txt`, needs-attention) bestätigt die Umsetzung (genau W_E bzw. der Rest, AdamW-Zustand sicher
entfernt, Rücksetzen nach dem Optimiererschritt von Schritt 150, alte Lauf-IDs unverändert) und fand drei Schwächen, übernommen:
1. **d_h ≤ 0 als „umgeschlagen“ war zu grob.** Neu: gehalten = d_h > 0, umgeschlagen = d_h < 0; d_h = 0 oder Test-Acc < 0.9 in
   einem Arm → Seed nicht auswertbar.
2. **Ort der Speicherung ist mit der Eingriffsgröße vermengt** (RW setzt 14 592 Parameter zurück, RR 211 584 ≈ 93.5 %).
   Neu: Die Muster heißen jetzt *W_E notwendig+hinreichend* (RW um, RR hält), *Rest trägt* (RW hält, RR um), *redundant*
   (beide halten), *nur zusammen* (beide um), und werden als Aussage über **Notwendigkeit/Hinlänglichkeit des behaltenen
   Teils unter Rücksetzen und Neulernen** gelesen, nicht als Speicherort. Bezug für ein volles Rücksetzen ist der reine
   G-Lauf (t = 0, d_h < 0 in 5/5). Zusätzlich wird die Verschiebung ‖θ − θ₀‖ von W_E und Rest vor dem Rücksetzen protokolliert
   (Größe des Sprungs). Norm-angepasste Rücksetz-Kontrollen und reine Optimiererzustands-Kontrollen: **nicht** umgesetzt
   (Folgeversuch, falls das Ergebnis es verlangt).
3. **Smoke prüfte nur Zählwerte.** Neu prüft `freq_ban.py` bei jedem Rücksetzen selbst: zurückgesetzte Tensoren = Init und ohne
   AdamW-Zustand, alle anderen unverändert und mit Zustand; sonst Abbruch. `check_smoke.py` verlangt `check = true`.
Urteil sonst wie oben (≥ 4 auswertbare Seeds mit gleichem Muster).

## Reproduktion

```
sh lab/experiments/EXP-038-where-lockin/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-038-where-lockin/analyze.py
python lab/experiments/EXP-038-where-lockin/analyze.py --selftest
```

## Status

Vorbereitet, nicht ausgeführt; `--reset-at-switch` im echten Lauf ungetestet (Smoke am Anfang der Queue).
## Ergebnis (Sitzung 21, 2026-09-27, eingeordnet 04:51 Berlin; Läufe und Auswertung im CPU-Programm, Auswertung 04:46)

Formales Urteil nach der Festlegung (≥ 4 auswertbare Seeds mit gleichem Muster): ***redundant*** (5/5 Seeds).

| Seed | d_h Kontrolle (ohne Rücksetzen) | RW (nur W_E auf Init) d_h | RR (alles außer W_E auf Init) d_h | Test-Acc RW / RR | Train-Acc direkt nach dem Rücksetzen RW / RR |
|---|---|---|---|---|---|
| 30 | 5 | 5 | 4 | 1.0 / 1.0 | 0.065 / 0.013 |
| 31 | 5 | 5 | 4 | 1.0 / 1.0 | 0.062 / 0.012 |
| 32 | 4 | 4 | 5 | 1.0 / 1.0 | 0.076 / 0.012 |
| 33 | 4 | 4 | 5 | 1.0 / 1.0 | 0.082 / 0.011 |
| 34 | 5 | 5 | 5 | 1.0 / 1.0 | 0.085 / 0.010 |

**Lesart (nach Nachtrag a: Notwendigkeit/Hinlänglichkeit unter Rücksetzen und Neulernen, kein Speicherort):** Nach 150 Schritten auf F reicht **jeder der beiden
Teile allein**, damit das Netz nach 2000 Schritten nur auf G wieder die F-Frequenzen trägt. Bemerkenswert ist RW: W_E steht nach dem Rücksetzen auf der Init
(Train-Acc 0.06–0.09), und trotzdem schreiben die übrigen Gewichte die F-Wahl während des G-Trainings in das neue W_E zurück. Die Festlegung steckt also nicht nur
im Embedding. Sie ist nach 150 Schritten doppelt vorhanden. Ob schon ein Teil des Rests (Attention, MLP, W_U) genügt, ist offen (Folgeversuch).
**Einordnung (Regel 15b):** n = 5, Seeds aus EXP-020 bekannt → **Pilot**, keine Kernaussage. Grenzen wie oben (grober Eingriff; RR setzt 93.5 % der Parameter zurück,
RW 6.5 %; t = 150 liegt nach EXP-020 bereits an der Decke der Persistenz).

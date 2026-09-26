---
id: EXP-037
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-037: Gibt anhaltender Datenkonflikt in der kritischen Periode die Frequenzwahl an die Init zurück?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N15) · Grundlage
[[experiments/EXP-020-data-switch/README|EXP-020]] (Nachtrag d) · Schwesterversuch [[experiments/EXP-036-init-conflict/README|EXP-036]].

## Anlass

EXP-020: Die Frequenzwahl des Transformers fällt zwischen Schritt 25 und 50 (Seeds 30–32 identisch). Ein **einzelner** früher
Wechsel F → G (t ≤ 50) erzeugt „fremde“ Frequenzen außerhalb F ∪ G ∪ 2k ∪ K_nurF ∪ K_nurG, meist mit kleinem Init-Rang
(Nachtrag d, Exploration). EXP-036 prüft über einen Init-Wechsel, ob sie aus der Init stammen. EXP-037 greift die Deutung
von der anderen Seite an: Wenn **widersprüchliche Datensignale** die Wahl an die Init zurückgeben, dann sollte ein
**anhaltender** Konflikt über die ganze kritische Periode (F und G wechseln sich in kurzen Blöcken ab) die fremden,
init-starken Frequenzen noch zuverlässiger hervorbringen als ein einzelner Wechsel.

## Versuch (vorab festgelegt 2026-09-26 15:06 Berlin (commit 3325b72), vor jedem EXP-037-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Was wählt das Netz, wenn F und G sich während der ersten 200 Schritte in Blöcken von A Schritten abwechseln (dann 2000 Schritte nur G)? |
| **H37 (Konflikt → Init)** | Fremde Frequenzen mit kleinem Init-Rang |
| **Alternative 1 (F-Akkumulation)** | Die F-Schritte summieren sich (100 F-Schritte > Festlegungszeit 50) → K wie „nur F“ (d ≥ +2) |
| **Alternative 2 (Rezenz)** | Die jüngsten Daten gewinnen (Ende und G-Phase sind G) → d ≤ −2 |
| **Kontrolle** | EXP-020-Läufe derselben Seeds (gleiche Init, gleiche Splits): nur F, nur G, Einzelwechsel bei t = 10–1000 |
| **Eingriff** | `freq_ban.py --alternate-every A --switch-step 200` (neu): Block k (Schritte (k−1)A+1 … kA) auf F für ungerades k, auf G für gerades k; ab Schritt 201 nur G. A = 5 (primär: 20 F- und 20 G-Blöcke) und A = 25 (sekundär: 4 + 4 Blöcke). Je 100 F- und 100 G-Schritte |
| **Seeds** | 30, 31, 32 (Init und Splits aus EXP-020) |
| **Messung** | K = Top-5 von W_E bei Schritt 2200; d = \|K ∩ F\| − \|K ∩ G\|; fremd = K \ A (A wie Nachtrag d, reine EXP-020-Läufe desselben Seeds); Init-Rang = Rang im W_E-Spektrum bei Schritt 0 |
| **Urteil (A = 5, primär)** | *gestützt*, wenn ≥ 2 von 3 Seeds ≥ 1 fremde Frequenz haben **und** der gepoolte Median ihrer Init-Ränge ≤ 14 ist; sonst *F-Akkumulation*, wenn d ≥ +2 in ≥ 2 Seeds; *G (Rezenz)*, wenn d ≤ −2 in ≥ 2 Seeds; sonst *unklar*. Ungültiger/fehlender Lauf → *nicht auswertbar*. A = 25 mit derselben Regel, nur berichtet |
| **Prüfungen** | strenger Lader (`load_run`: Status, Seed, Schritte, Hashes, endliche Spektren), `alternate_every` und Zahl der Wechsel (39 bzw. 7) im `result.json`, Init-Prüfsumme gleich wie EXP-020 |
| **Budget / Abbruch** | Smoke (30 Schritte) + 6 Läufe à 2200 Schritte ≈ 28 min; Abbruch bei NaN/Stillstand |

**Was gegen H37 spräche:** keine fremden Frequenzen (F-Akkumulation oder Rezenz), oder fremde Frequenzen mit Init-Rängen
wie der Zufall (Median ≈ 28).
**Grenzen:** 3 Seeds, dieselben Seeds wie die Exploration in Nachtrag d (die Läufe selbst sind neu, die Init-Ränge dieser
Seeds sind bekannt). Ein *gestützt* zeigt eine Assoziation mit dem Init-Spektrum, keine Kausalität; die kausale Seite prüft
EXP-036. Die Bedingung „Median ≤ 14“ ist grob (Zufall ≈ 28).

## Nachtrag a (15:12 Berlin, nach Codex-Review, **vor jedem EXP-037-Lauf**)

Codex (`codex_review_2026-09-26.txt`, needs-attention; Blockplan und alte Lauf-IDs als korrekt bestätigt) fand drei Schwächen,
alle übernommen:
1. **Urteile nicht exklusiv:** Eine fremde Frequenz plus vier G-Frequenzen hätte H37 *und* Rezenz erfüllt, gemeldet als
   *gestützt*. Neu: H37 und eine Alternative zugleich → *mehrdeutig*.
2. **Fehlende Kontrollen:** Neu **C_F100** (F 100 Schritte, dann G 2100; gleiche Exposition, kein Wechselspiel; Seeds 30–32).
   Zeigt auch C_F100 das H37-Muster → *nicht spezifisch*. Außerdem gehört die Top-5 des Masken-Spektrums M0 der gemittelten
   Maske (F + G)/2 jetzt zu A (Mischmasken-Frequenzen zählen nicht als fremd); ihre Ränge werden berichtet.
   Nicht umgesetzt: ein echtes gewichtetes Mischtraining (Codebaustelle); A = 5 kommt ihm unter AdamW (β1 = 0.9) schon nahe.
3. **Smoke prüfte nur Metadaten und konnte veraltet sein:** Neu läuft der Smoke immer frisch (`--force`), `freq_ban.py`
   protokolliert je Blockwechsel den Hash des gewählten Trainingssets (`alternation_trace`), `check_smoke.py` verlangt
   G, F, G nach den Schritten 5, 10, 15 und den Wechsel auf G bei 20.
**Urteil (ersetzt die Zeile oben):** ungültig/fehlend (Arm oder Kontrolle) → *nicht auswertbar*; H37 ∧ (F-Akkumulation ∨
Rezenz) → *mehrdeutig*; H37 ∧ H37(C_F100) → *nicht spezifisch*; nur H37 → *gestützt*; sonst *F-Akkumulation* / *G (Rezenz)* /
*unklar*. Budget jetzt 9 Läufe + Smoke ≈ 42 min.

**Nachtrag b (15:16, vor jedem Lauf):** Alle 9 Läufe mit `--save-model` (Endmodell), damit fremde Frequenzen später
funktional geprüft werden können (Ablation). Ändert weder Messung noch Urteil.

## Reproduktion

```
sh lab/experiments/EXP-037-alternation-conflict/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-037-alternation-conflict/analyze.py
python lab/experiments/EXP-037-alternation-conflict/analyze.py --selftest
```

## Status

Vorbereitet, nicht ausgeführt; `--alternate-every` ist im echten Lauf ungetestet (Smoke am Anfang der Queue).

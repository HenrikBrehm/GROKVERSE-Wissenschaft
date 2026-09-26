---
id: EXP-037
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/unklar]
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

**Nachtrag b (15:14, vor jedem Lauf):** Alle 9 Läufe mit `--save-model` (Endmodell), damit fremde Frequenzen später
funktional geprüft werden können (Ablation). Ändert weder Messung noch Urteil.

## Reproduktion

```
sh lab/experiments/EXP-037-alternation-conflict/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-037-alternation-conflict/analyze.py
python lab/experiments/EXP-037-alternation-conflict/analyze.py --selftest
```

## Ergebnis (2026-09-26 16:50 Berlin; Smoke bestanden, alle Prüfungen des Laders bestanden)

| Arm | Seed | K (Schritt 2200) | d | fremd | Init-Rang | Mischmasken-Rang | Test-Acc |
|---|---|---|---|---|---|---|---|
| C_F100 | 30 | 6, 12, 29, 42, 55 | +3 | – | – | – | 1.00 |
| C_F100 | 31 | 23, 29, 41, 45, 55 | +3 | – | – | – | 1.00 |
| C_F100 | 32 | 5, 11, 20, 22, 48 | +3 | – | – | – | 1.00 |
| A = 5 | 30 | 6, 29, 34, 45, 47 | +1 | 34, 45 | 11, 26 | 19, 40 | 1.00 |
| A = 5 | 31 | 8, 22, 29, 41, 44 | +1 | 22, 44 | 8, 26 | 13, 20 | 1.00 |
| A = 5 | 32 | 8, 11, 13, 35, 50 | 0 | 8, 13, 50 | 4, 18, 9 | 9, 45, 54 | 0.48 |

**Vorab festgelegtes Urteil (A = 5, primär): *gestützt*** (3/3 Seeds mit fremden Frequenzen, gepoolter Init-Rang-Median 11,
keine F-Akkumulation oder Rezenz, Kontrolle C_F100 ohne fremde Frequenzen).
**Einschränkungen (wichtig):** Der Median wird von Frequenzen getragen, die schon aus der Exploration bekannt waren (34, 22, 8,
13 traten beim Einzelwechsel derselben Seeds auf); die neuen haben Init-Ränge 26, 26, 9. 45 = fold(2 · 34) und 44 = fold(2 · 22)
sind Oberwellen der wiederkehrenden. An frischen Seeds (EXP-020 Nachtrag d) hielt die Init-Deutung nicht. Belastbar ist:
**Anhaltender F/G-Konflikt erzeugt je Seed reproduzierbar dieselben „Konfliktfrequenzen“, gleiche Exposition ohne Konflikt
nicht.** Ob sie aus der Init stammen, bleibt offen → [[experiments/EXP-036-init-conflict/README|EXP-036]].
**Ablation (Nachtrag b, beschreibend, `ablate_foreign.json`):** Wiederkehrende fremde Frequenzen sind funktional (Δloss 34: 1.38,
22: 1.57, 8: 3.28, 13: 4.19; Zufallsfrequenzen ≈ 0), die Oberwellen 45, 44 kaum (0.011, 0.005).
**A = 25 (sekundär, 17:04): ebenfalls *gestützt*.** K = [6, 19, 29, 34, 47], [8, 16, 29, 41, 42], [8, 11, 13, 26, 30];
d = +1, +1, +1; fremd 34 | 42 | 8, 13, 26, 30 (Init-Ränge 11 | 2 | 4, 18, 25, 8); alle Test-Acc 1.0. Wieder dieselben
Kernfrequenzen je Seed (in Seed 31 diesmal 42, die fremde Frequenz des Einzelwechsels bei t = 10/50), 26 = fold(2 · 13) ist
Oberwelle. Ablation: 34, 8, 13 funktional (Δloss 1.7–5.3), 42 dazwischen (0.38), 26 und 30 kaum (0.057, 0.002).

## Nachtrag c (17:15 Berlin, nach Codex-Angriff auf die Schlussfolgerung, `codex_conclusion_review_2026-09-26.txt`)

Die vorab festgelegten Urteile bleiben (*gestützt*, A = 5 und A = 25). **Die Deutung wird eingeengt:**
1. C_F100 hat 100 ununterbrochene F-Schritte und legt sich deshalb vor dem Wechsel fest; der Kontrast trennt also **wiederholtes
   Wechseln** von **einem Wechsel nach der Festlegung**, nicht „widersprüchliche Signale“ als Ursache. Richtig ist: *Das
   Auftreten der fremden Frequenzen hängt vom Wechselplan ab*; konfliktspezifisch ist es nicht gezeigt (dafür bräuchte es
   Kontrollen mit gleichem Wechselplan und verträglichen Daten, echtes Mischtraining, zufällige Blockfolgen).
2. „Reproduzierbar“ heißt nur: **über Wechselpläne hinweg innerhalb der drei schon explorierten Seeds** 30–32, keine unabhängige
   Replikation. An frischen Seeds (33, 34) war das Bild schwächer.
3. „Funktional“ gilt nur für generalisierende Modelle: 34 (Seed 30), 22 (Seed 31, A = 5), 8 und 13 (Seed 32, A = 25) mit Δloss
   1.4–5.3; 42 (Seed 31, A = 25) nur 0.38; die Schwelle ist eine beschreibende Konvention, die Zufallskontrollen sind nicht nach
   spektraler Stärke angeglichen. Die A = 5-Werte von Seed 32 (Test-Acc 0.48) zählen dafür nicht.

## Post hoc (Sitzung 14, 2026-09-26 21:53 Berlin, explorativ, bereits gesehene Läufe): kontinuierliche Persistenz π

Maß wie [[experiments/EXP-020-data-switch/README|EXP-020]] „Post hoc (Sitzung 14)“ (0 = wie nur G, 1 = wie nur F; Normierung mit den reinen
EXP-018-Läufen). Alle Arme haben 100 F-Schritte vor der reinen G-Phase:

| Seed | 100 F am Stück, dann G (at100) | 100 F + 100 G in 25er-Blöcken (alt25) | in 5er-Blöcken (alt5) |
|---|---|---|---|
| 30 | 1.03 | 0.66 | 0.60 |
| 31 | 1.01 | 0.75 | 0.52 |
| 32 | 1.04 | 0.63 | 0.52 |

**Lesart (explorativ, 3 Seeds):** Gleiche Menge F-Training hält vollständig fest, wenn es am Stück kommt, aber nur zu ≈ 0.5–0.75, wenn
G-Schritte dazwischen liegen; feinere Verschränkung hält weniger. Die Festlegung ist also kein bloßes Aufsummieren von F-Schritten, sondern
ein Wettlauf, bei dem die konkurrierenden G-Schritte im Fenster zählen (passt zu [[NOVEL_DIRECTIONS]] N22). Nur beschreibend.

*Korrektur nach adversarieller Prüfung (Sitzung 14):* Die Endschritte sind fair (auch at100 endet bei 2200), die Zahl der F- und G-Schritte
ist gleich (100 F, 2100 G). Die Nullhypothese „nur die Summe zählt“ ist damit verworfen, aber schwach, weil EXP-020 schon zeigt, dass frühe
Schritte dominieren. Die aussagekräftigere Null „nur der erste F-Block zählt“ (aus der EXP-020-Kurve: 5 F-Schritte → ≈ 0.1, 25 → ≈ 0.38) liegt
**unter** den Beobachtungen (0.52–0.60 bzw. 0.63–0.75): **Spätere F-Blöcke tragen noch bei, das Fenster ist länger als der erste Block.**
„Wettlauf“ ist eine Deutung, kein Test. alt5 Seed 32 hat nicht generalisiert (Test-Acc 0.48). Zahlen: `EXP-020-data-switch/posthoc_pi_other.json`.

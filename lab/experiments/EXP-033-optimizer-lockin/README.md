---
id: EXP-033
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/positiv]
---
# EXP-033: Ist die 5-Schritte-Festlegung aus EXP-032 ein AdamW-Artefakt?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Vorgänger
[[experiments/EXP-032-early-lockin/README|EXP-032]] · [[experiments/EXP-026-parity-crossover/README|EXP-026]].

## Anlass

EXP-032: 5 Schritte mit σ_3 = 3x + x² legen die halbe F-Neigung des danach rein quadratischen Netzes fest. Einwand
(eigener, gestützt durch Abuduweili & Liu 2024, https://arxiv.org/abs/2412.02153): Der erste Adam-Schritt ist ein reiner
Vorzeichen-Schritt der Größe lr pro Parameter, unabhängig davon, wie klein der Gradient ist. Bei Init-Einträgen von ≈ 0.0067
verschiebt jeder Schritt jeden Eintrag um ≈ 15 %. In EXP-032 ist die Amplitude r am Umschaltschritt über alle 5 Splits
**praktisch gleich** (t_s = 5: 0.01180–0.01185; t_s = 20: 0.02893–0.02897), ebenso ds am Umschaltschritt (0.035 ± 0.004).
Das passt zu gleichförmigen Vorzeichen-Schritten. „5 Schritte“ ist also keine Eigenschaft der Lerndynamik, sondern der
Schrittgröße. Offen ist, ob die **Festlegung selbst** (ein kleiner früher Vorsprung wird bis zum Ende verstärkt und
beibehalten) an der Adam-Geometrie hängt oder ob jeder Weg zum gleichen Zustand dasselbe Ergebnis gibt.

## Versuch (vorab festgelegt 2026-09-26 12:05 Berlin, commit 6bb4557, vor jedem EXP-033-Lauf; **ersetzt durch Nachtrag a**)

| Punkt | Festlegung |
|---|---|
| **Frage** | Entsteht die bleibende F-Neigung auch, wenn die σ_3-Phase mit reinem Gradientenabstieg (GD) statt AdamW läuft, bei gleicher erreichter Merkmalsamplitude r? |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F (wie EXP-032), gleiche Init |
| **Phase 1** | σ_3. Arm **AR** (Kontrolle): AdamW wie EXP-032, t_s ∈ {5, 10, 20} Schritte. Arm **GD**: `torch.optim.SGD` ohne Momentum und ohne Weight Decay, volle Batch, bis Median-r ≥ Ziel-r; Ziel-r je Split und Stufe = r am Umschaltschritt des EXP-032-Laufs (t_s = 5/10/20) |
| **Phase 2** | Beide Arme: reines x², **frischer** AdamW (lr 1e-3, wd 1, β 0.9/0.98), 5000 Schritte. Nur Phase 1 unterscheidet die Arme |
| **Anker** | EXP-032 t_s = 0 (nur x², 5000 Schritte AdamW ab Init): ds₀ je Split |
| **GD-Lernrate** | Vorab per Smoke nur an Phase 1 gewählt (`--phase1-only`, Split 10, Ziel r = 0.0290): größte lr aus {0.3, 1, 3, 10, 30}, die das Ziel ohne NaN erreicht und dabei die Trainings-Acc nicht springen lässt; bei mehreren gültigen die kleinste, die ≤ 3000 Schritte braucht. Das Ergebnis (ds) wird im Smoke nicht berechnet |
| **Messgröße** | ds = Anteil(F) − Anteil(H) am normierten h = 2-Spektrum am Ende von Phase 2 (wie EXP-032) |
| **Primär P33a** | GD-Neigung über dem Anker: ds(GD) > ds₀ in ≥ 13 der 15 Einheiten (Split × Stufe); Vorzeichentest einseitig p ≈ 0.004 |
| **Primär P33b** | Quotient Q = Mittel ds(GD) / Mittel ds(AR) über die 15 Einheiten |
| **Entscheidung** | P33a erfüllt und 0.5 ≤ Q ≤ 2 → ***zustandsbestimmt*** (Festlegung nicht an AdamW gebunden); P33a erfüllt und Q > 2 → ***GD stärker***; P33a erfüllt und Q < 0.5 → ***AdamW verstärkt, Festlegung schwach vorhanden***; P33a nicht erfüllt → ***AdamW-gebunden*** (ohne Adam-Phase-1 keine bleibende Neigung). Gültig nur, wenn ≥ 12 GD-Einheiten das Ziel-r erreichen und alle Endnetze Test ≥ 0.9 haben; sonst *nicht auswertbar* |
| **Sekundär** | ds am Umschaltschritt je Arm (ist GD gleich weit geneigt?); Verstärkungsfaktor ds_Ende / ds_Umschalt; Phase-1-Schritte von GD; AR gegen EXP-032 (Wirkung des frischen Optimierers); Generalisierungsschritt |
| **Erwartung (schwach)** | *zustandsbestimmt* oder *GD stärker*: GD folgt dem Gradienten ohne Vorzeichen-Rauschen; der lineare Anteil liefert die F-Richtung direkt |
| **Was dagegen spräche** | ds(GD) ≈ ds₀: Dann braucht die Festlegung die Adam-Geometrie der ersten Schritte |
| **Grenzen** | Ziel-r ist ein Median über Neuronen, nicht die ganze Verteilung; W_out wächst unter GD anders (berichtet: ‖W_out‖ am Umschaltschritt). Eine Architektur, 5 Splits |
| **Budget** | Smoke 5 × ≤ 1 min; 15 AR-Läufe ≈ 90 s, 15 GD-Läufe ≈ 2–4 min → ≈ 1–1.5 h |

## Nachtrag a (2026-09-26 12:14 Berlin, commit 840e890, nach Codex-Review, vor jedem EXP-033-Lauf): neues Design, gilt allein

Codex (`codex_review_2026-09-26.txt`, „needs-attention“, 6 × high, 1 × medium). Selbst geprüft; übernommen:
(1) 15 Einheiten aus 5 Splits sind Pseudoreplikation → **Split ist die Einheit**, 10 Splits (10–19), eine Stufe;
(2) `torch.median` nimmt bei 512 Neuronen den unteren Mittelwert → interpolierter Median wie NumPy, Ziel-r aus dem
eigenen AdamW-Kontrolllauf, Toleranz ±2 %; (3) Reset des Optimierers → zusätzlich Arm „AdamW behalten“ (EXP-032-Protokoll)
berichtet; (4) Q ohne Unsicherheit → ankerbereinigte Effekte und Bootstrap-KI; (5) lr-Wahl uneindeutig und am
Bestätigungs-Split → deterministische Regel an einer Pilot-Init; (6) Queue fail-closed. Teilweise übernommen: Codex'
Faktorial­design (Optimierer × Aktivierung) und large-ε-Adam nicht; stattdessen ein **Vorzeichen-Arm** (signGD, Schritt 1e-3,
= Adams erster Schritt wiederholt), der den vermuteten Mechanismus direkt isoliert. Die Unterschiede in ‖W_out‖, r-Verteilung
und ds am Umschaltschritt sind Teil der Behandlung (verschiedene Wege zu gleicher Amplitude) und werden berichtet, nicht
als Tor verwendet: Die Frage ist gerade, ob der Weg zählt.

| Punkt | Festlegung (ersetzt die Tabelle oben) |
|---|---|
| **Einheiten** | EXP-016-Splits Seeds 10–19, Arm F, Stufe t_s = 10 (EXP-032: ds 0.13, t_s = 5: 0.09) |
| **Arme (Phase 1, σ_3)** | **AR**: AdamW 10 Schritte (EXP-032), dann frischer AdamW. **GD**: SGD ohne Momentum/Decay bis r ≥ r_AR(Split). **SIGN**: signGD 1e-3 bis r ≥ r_AR (sekundär). **RET**: AdamW durchgehend = EXP-032 (10–14 vorhanden, 15–19 neu; sekundär) |
| **Phase 2** | x², frischer AdamW, 5000 Schritte (AR, GD, SIGN) |
| **Anker ds₀** | nur x² ab Init, 5000 Schritte: EXP-026 t_s = 0 (10–14), EXP-027b Breite 512 (15–19) |
| **Matching** | r = interpolierter Median der Merkmalsamplitude; GD/SIGN gültig nur bei r_switch/r_AR − 1 ∈ [0, 0.02] |
| **GD-lr** | Pilot Split 10 mit Init-Seed 99 (kein Bestätigungs-Init), nur Phase 1, keine Spektren gespeichert; Ziel r = 0.0167; Kandidaten 0.3, 1, 3, 10, 30; gewählt: größte lr mit Ziel erreicht, endlich, Überschuss ≤ 2 % (`select_lr.py` → `lr.json`) |
| **Effekte** | Δ_X(s) = ds_X(s) − ds₀(s) am Ende von Phase 2 |
| **Tor** | Δ_AR > 0 in ≥ 9/10 Splits (die Festlegung repliziert unter Reset), sonst *nicht auswertbar*; alle 10 AR- und GD-Läufe gültig und Test ≥ 0.9, sonst *nicht auswertbar* |
| **Primär** | k = #Splits mit Δ_GD > 0 (Vorzeichentest, 9/10: p = 0.011); R = mean Δ_GD / mean Δ_AR mit 95-%-Bootstrap-KI über Splits (10 000×, Seed 0) |
| **Entscheidung** | k ≥ 9 und KI ⊂ [0.5, 2] → ***zustandsbestimmt***; k ≥ 9 und KI-Untergrenze > 2 → ***GD stärker***; k ≥ 9 und KI-Obergrenze < 0.5 → ***AdamW verstärkt, Festlegung schwach vorhanden***; k ≥ 9 sonst → ***GD-Neigung vorhanden, Größenverhältnis offen***; k < 9 und KI-Obergrenze < 0.5 → ***AdamW-gebunden***; k < 9 sonst → ***unklar***. Die Spanne [0.5, 2] ist eine Konvention (Faktor 2), keine physikalisch begründete Grenze |
| **Sekundär** | Δ_SIGN (liegt SIGN bei AR → Vorzeichen-Mechanismus); ds am Umschaltschritt je Arm; GD-Schritte; ‖W_out‖ und r-Quantile am Umschaltschritt; RET − AR (Wirkung des Optimierer-Resets) |
| **Budget** | Pilot ≤ 5 × 2 min; 10 AR + 10 GD + 10 SIGN + 5 RET ≈ 35 Läufe ≈ 60–80 min |

## Nachtrag b (2026-09-26 12:17 Berlin, vor jedem EXP-033-Lauf): Vorhersage aus der linearen Theorie (sekundär)

`linear_modes.py` → `linear_modes.json` (ohne Training). In der σ_3-Phase ist das Netz nahe der Init praktisch linear;
unter GD wächst es entlang der Singulärvektoren der Residuen-Korrelation J = Xᵀ(Y − 1/P), jede Mode mit einer Rate ∝ ihrem
Singulärwert. Befund: In allen 10 Splits hat **jede** der 10 obersten Moden ihre stärkste Frequenz in der Zielmenge F;
ds der obersten 5 Moden (s²-gewichtet) 0.27–0.44 (Mittel 0.38), ds von J selbst und von sign(J) je 0.105. Das Spektrum
fällt aber **flach** ab (Split 10: s₁ 12.0, s₁₀ 10.2, s₂₀ 9.0, s₅₀ 6.6), die bevorzugte Verstärkung bis zu r = 1.78 × Init
ist deshalb mäßig. **Vorhersage (sekundär, vorab):** ds am Umschaltschritt GD > AR in ≥ 7/10 Splits (GD verstärkt die
F-lastigen Top-Moden, Vorzeichen-Schritte bewegen alle Koordinaten gleich weit). Geringe Zuversicht; beeinflusst die
Primärentscheidung nicht.

## Nachtrag c (2026-09-26 12:26 Berlin, nach den ersten 3 Hauptläufen, **ohne Ansicht eines ds-Werts**): genaues Matching

Beim ersten Split überschießt der Vorzeichen-Arm das Ziel-r um 4.7 % (Schritt 1e-3 ist grob), GD um 1.5 % (Pilot 0.4 %). Mit
der Toleranz 2 % wäre SIGN meist ungültig und GD knapp; ein einziger GD-Ausreißer machte den ganzen Versuch *nicht auswertbar*.
Änderung (`--backtrack`): In GD und SIGN wird ein Schritt, der r über 1.005 · Ziel heben würde, so lange halbiert, bis er das
nicht tut (nur der letzte Anflug ist betroffen; die Halbierungen werden gespeichert). Lauf-IDs enden auf `_bt`; nur diese
werden ausgewertet. Die beiden alten Läufe von Split 10 (`EXP-033_gd_r0.0167032_lr3_seed10`, `EXP-033_sign_r0.0167032_seed10`)
bleiben liegen, werden nicht ausgewertet, ihre ds wurden nicht angesehen. Alle übrigen Festlegungen (Toleranz 2 %, Tor,
Entscheidung) unverändert. AdamW-Läufe sind nicht betroffen.

## Ergebnis (Sitzung 8, 13:18 Berlin)

Pilot: lr = 3 (Regel, `lr.json`). Alle 10 Splits × 3 Arme vollständig, Amplitude mit Rückwärtshalbierung auf ≤ 0.4 %
getroffen, alle Endnetze Test 1.0; zusätzlich 5 RET-Läufe (15–19).

| Größe (Mittel über 10 Splits) | AR (AdamW, Reset) | GD | SIGN | RET (AdamW behalten) |
|---|---|---|---|---|
| Δ = ds_Ende − ds₀ | 0.120 | **0.151** | 0.133 | ≈ AR + 0.015 |
| ds am Umschaltschritt | 0.066 | **0.105** | 0.071 | – |
| Phase-1-Schritte | 10 | 76.7 | 11 | 10 |
| Verstärkung ds_Ende / ds_Umschalt (grob) | ≈ 1.8 | ≈ 1.4 | ≈ 1.9 | – |

**Primär:** Δ_GD > 0 in **10/10** Splits (p = 0.001); Δ_AR > 0 in 10/10 (Tor erfüllt). R = 1.26, 95-%-KI [1.10, 1.46] ⊂ [0.5, 2].
**Urteil (vorab festgelegt): *zustandsbestimmt*.** Die bleibende F-Neigung entsteht auch ohne Adam in Phase 1; reiner
Gradientenabstieg bis zur gleichen Amplitude gibt sogar eine etwas größere Neigung (KI schließt 1 aus, bleibt aber unter
dem Faktor 2). **Nachtrag b bestätigt:** ds am Umschaltschritt GD > AR in 10/10 (vorhergesagt ≥ 7/10). SIGN ≈ AR, der
Vorzeichen-Schritt allein reproduziert also AdamW, GD weicht in die vorhergesagte Richtung ab.
**Post hoc (n = 10, nicht vorab festgelegt):** Das lineare Modenmaß ds(J) des Splits sagt die Neigung am Umschaltschritt
voraus (Spearman GD 0.84, AR 0.62), die End-Neigung nur schwach (0.42 / 0.30). Die schwächsten Splits (16, 14) sind in
allen Armen dieselben.
**Einordnung:** „Festlegung in 5 Schritten“ (EXP-032) ist in Schritten eine AdamW-Zahl; in Zuständen gemessen fällt die
Festlegung, bevor die Merkmalsamplitude das ~1.8-Fache der Init erreicht, und zwar unabhängig davon, ob der Weg dorthin
AdamW, Vorzeichen-GD oder GD ist. Der Optimierer-Reset kostet wenig (RET − AR 0.015).
**Grenzen:** Phase 2 immer AdamW; eine Stufe (r ≈ 1.78 × Init); ‖W_out‖ am Umschaltschritt unter GD größer (3.55 gegen 2.60)
und ist Teil der Behandlung; eine Architektur; Anker 15–19 aus EXP-027b (gleiches Protokoll).

## Befehle

    sh lab/experiments/EXP-033-optimizer-lockin/queue.sh      # Pilot + lr.json + alle Läufe, überspringt Fertiges
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/analyze.py

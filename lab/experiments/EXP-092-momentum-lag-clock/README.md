---
id: EXP-092
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-092: Sagt eine „Momentum-Verzögerungs-Uhr“ die Festlegung in ungesehenen Zellen voraus? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (Kandidat K5 / offene Frage „Warum macht eine kürzere Verzögerung selektiver?“) · [[NOVEL_DIRECTIONS]] N48 · [[confirm/R9_REGISTRATION_DRAFT|R9]] · [[experiments/EXP-090-beta-window-lambda/README|EXP-090]] · [[experiments/EXP-081-optimizer-clock/README|EXP-081]]

**Festgelegt vor jedem EXP-092-Lauf** (Sitzung 41, 2026-09-28, ≈ 13:30 Berlin; Code `design.py`, `analyze.py`, Selbsttest grün 13:30 über den Wächter).

## Bezug und Frage

R9 bestätigte: Die frühe Festlegung tickt in Λ, wenn Adams β-Fenster in Λ gemessen werden. Offen ist das *Wie*. Einfachstes Modell (M-lag): Adams bias-korrigiertes erstes Moment ist beim Wechsel im Mittel lag(β₁, t) = Σ k β₁ᵏ / Σ β₁ᵏ (k = 0 … t − 1) Schritte alt. Die Richtung der Bewegung hinkt also um c·lag Λ-Einheiten hinterher, und die frühe Bewegung wird mit der Zeit selektiver. Die wirksame Uhr wäre **Λ_eff = c·t − c·lag(β₁, t)**.
Post hoc an den R9-Armmitteln (gesehen, deshalb nur Anlass): Gerade durch π über Λ_eff hat RMSE 0.027, über Λ 0.060, über Schritte 0.059 (6 Arme). Dieser Versuch prüft M-lag **an Zellen, die es noch nicht gab**: β₁ nur vor dem Wechsel geändert bei Standard-Lernrate (EXP-081 änderte β₁ im ganzen Lauf), c = 0.5 und c = 4.

## Aufbau

add 113, arch25k, ω = 0-Splitpaare wie EXP-089/090 (EXP-053-Bau), **Seeds 3400–3415** (frisch: Dateisuche 28.09. ohne Treffer), Wechsel A → B und B → A bei t, danach 2000 Schritte Standard (lr 1e-3, β 0.9/0.98), GPU. π wie EXP-056 gegen die reinen Läufe des Seeds.

| Zelle | c | t | β vor dem Wechsel | Λ | lag·c | Λ_eff | rel. Lage Lag-Uhr | Λ-Uhr | Schritt-Uhr |
|---|---|---|---|---|---|---|---|---|---|
| n25 (Eichung) | 1 | 25 | 0.9/0.98 | 25 | 7.07 | 17.93 | 0 | 0 | 0 |
| n30 (Eichung) | 1 | 30 | 0.9/0.98 | 30 | 7.67 | 22.33 | 1 | 1 | 1 |
| n20 | 1 | 20 | 0.9/0.98 | 20 | 6.23 | 13.77 | −0.95 | −1 | −1 |
| b08 | 1 | 25 | **0.8**/0.98 | 25 | 3.91 | 21.09 | **+0.72** | 0 | 0 |
| b095 | 1 | 25 | **0.95**/0.98 | 25 | 9.40 | 15.60 | **−0.53** | 0 | 0 |
| c05 | 0.5 | 50 | 0.9/0.98 | 25 | 4.37 | 20.63 | +0.61 | 0 | +5 |
| c4 | 4 | 6 | 0.9/0.98 | 24 | 8.78 | 15.22 | −0.62 | −0.2 | −3.8 |

„rel. Lage“ = (x − x(n25)) / (x(n30) − x(n25)); vorhergesagtes π = π(n25) + rel. Lage · (π(n30) − π(n25)), jeweils mit den Mittelwerten dieses Versuchs. 7 Zellen × 2 + 2 reine = 16 Läufe je Seed, **256 GPU-Läufe** (≈ 20–40 s je Lauf, 8 Worker, neben dem Repro-Paket: erwartet ≈ 20–30 min).

## Vorhersagen und Lesarten (verbindlich, im Code)

- **P1:** MAE der drei Uhren über die fünf ungesehenen Zellen (n20, b08, b095, c05, c4); δ_Λ = MAE_Λ − MAE_lag, δ_S = MAE_Schritte − MAE_lag, Bootstrap über Seeds (Eichung in jeder Ziehung neu).
- **P2:** b_up = π(b08) − π(n25) > 0 und b_dn = π(n25) − π(b095) > 0 (Λ- und Schritt-Uhr sagen 0 voraus). Größe nach M-lag: ≈ +0.72 bzw. +0.53 mal (π(n30) − π(n25)) ≈ +0.08 / +0.06, wenn der Abstand n25 → n30 wie in R9 ≈ 0.11 ist.
- **Lesarten:** *Lag-Uhr gestützt* = KI-Untergrenzen von δ_Λ, δ_S, b_up, b_dn alle > 0. *Lag-Uhr widerlegt* = b_up oder b_dn mit KI-Obergrenze < 0, oder beide KIs innerhalb ±0.03. *Lag-Uhr teilweise* = b_up und b_dn > 0 (KI), aber nicht beide δ. Sonst *unklar*. Weniger als 10 gültige Seeds → *nicht auswertbar*.
- **Was gegen M-lag spräche:** kein β₁-Effekt vor dem Wechsel (dann wirkt β₁ nur über den Schwanz nach dem Wechsel, EXP-081), oder c05/c4 weit weg von der Λ_eff-Vorhersage (dann ist die Verzögerung nicht die ganze Nichtlinearität; lineare Eichung über n25/n30 extrapoliert bei n20, b095 und c4 außerhalb des Eichbereichs, das ist eine bekannte Schwäche).
- **Beschreibend:** MAE_lag selbst, Spearman über die 7 Zellmittel je Uhr, Selektivität der Verschiebung beim Wechsel (Anteil der Gruppenleistung von W_E(t) − W_E(0) auf den Zielen des ersten Splits) und ihre Norm je Zelle. M-lag in der Lesart „ältere Gradienten sind unselektiver“ erwartet höhere Selektivität bei kürzerer Verzögerung (b08 > n25 > b095); die Lesart „weniger Bewegung“ erwartet dagegen vor allem eine Normänderung.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

R9 (Armmittel: Wahl des Modells und der Uhrgröße lag = mittleres Alter des bias-korrigierten Moments; die post-hoc-RMSE oben), EXP-090 (β₁ allein genügt → nur β₁ variiert, β₂ bleibt 0.98), EXP-081 (β₁-Richtung im ganzen Lauf), EXP-089/091 (Lernratenstufen 0.25/2 → hier neue Stufen 0.5/4). Keine Seeds aus diesen Blöcken.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-092-momentum-lag-clock/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-092-momentum-lag-clock/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-092-momentum-lag-clock/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-092-momentum-lag-clock/analyze.py
```

## Ergebnis (Sitzung 41, 2026-09-28; Block 13:32–14:26 Berlin, 256/256 ok; `analyze.py` über den Wächter; `summary.json`)

16/16 Seeds gültig. **Registrierte Lesart: „Lag-Uhr gestützt“.**
- **P1:** MAE über die fünf ungesehenen Zellen: Lag-Uhr **0.029**, Λ-Uhr 0.067, Schritt-Uhr 0.149; δ_Λ KI [0.022, 0.054], δ_S KI [0.040, 0.199] (beide > 0).
- **P2:** b_up = π(b08) − π(n25) = **+0.083** [0.046, 0.123] (14/16); b_dn = π(n25) − π(b095) = **+0.037** [0.016, 0.061] (13/16). β₁ *nur vor dem Wechsel* verschiebt die Festlegung also bei gleicher Lernrate und gleichem Λ, in der vorhergesagten Richtung (Λ- und Schritt-Uhr sagen 0).
- **Beschreibend:** Zellmittel π: n20 0.265, n25 0.361, n30 0.459, b08 0.444, b095 0.324, c05 0.426, c4 0.195. Beobachtet − Lag-Vorhersage (je Seed geeicht, post hoc): n20 −0.004, b08 +0.013, b095 +0.015, c05 +0.005 (KIs schließen 0 ein), **c4 −0.107 [−0.16, −0.06]** (3/16 > 0). Spearman über 7 Zellen: Lag 0.96, Λ 0.64, Schritte 0.68.
- **Selektivität beim Wechsel (beschreibend):** b08 gegen n25 log f +0.083, log N +0.069; n25 gegen b095 log f +0.045, log N +0.024; mehr Zeit (n30 gegen n25) log f +0.053, log N +0.175. **c4** ist die unselektivste Zelle: gegen n20 log N +0.150, aber log f −0.044 (f 0.166 gegen 0.173).
- **Einordnung:** Die Verzögerungs-Uhr Λ_eff = c·t − c·lag(β₁, t) sagt vier von fünf ungesehenen Zellen innerhalb ±0.015 voraus (β₁ vor dem Wechsel 0.8/0.95, c = 0.5, t = 20), mit derselben Eichung. Sie versagt bei **c = 4, t = 6** (wenige, sehr große Schritte): Die Festlegung ist dort viel schwächer, als Λ_eff sagt, und die frühe Bewegung ist groß, aber unselektiv. Post-hoc-Kandidat (nicht geprüft): Adams erste Schritte sind fast vorzeichenartig (m̂/√v̂ ≈ ±1 aus ein, zwei Gradienten) und damit maximal unselektiv; bei c = 4 fällt ein großer Teil von Λ in diese ersten Schritte. Alternativ: Überschießen bei lr 4e-3. **Grenzen:** Pilot, 16 Seeds, eine Aufgabe, π = W_E-Energiemaß, lineare Eichung über n25/n30 (Extrapolation bei n20, b095, c4); das Lag-Maß ist das mittlere Alter des bias-korrigierten ersten Moments (erste Ordnung).

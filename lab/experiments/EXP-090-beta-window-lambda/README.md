---
id: EXP-090
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-090: Kommt die stärkere Festlegung vieler kleiner Schritte von Adams Fenstern, die in Schritten zählen? (Pilot)

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage: Was macht die frühe Wahl fest?) · Vorläufer [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]] (Nachtrag a: H-β), [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (β₁ als Hebel) · [[confirm/R3_REGISTRATION_DRAFT|R3]] · [[JOURNAL]] Sitzung 40.

**Festgelegt:** Sitzung 40, 2026-09-28, Commit 11:38 Berlin (035ed917; die frühere Angabe „≈ 11:50“ war nicht gemessen), vor jedem EXP-090-Lauf. Pilot/Exploration (16 frische Seeds, kein eingefrorenes Manifest).

## Konkurrenzmodelle

EXP-089: Bei gleicher Lernratensumme Λ = 25 hält die Wahl nach 100 Schritten mit lr × 0.25 stärker fest als nach 25 Standardschritten (Δπ +0.24, 10/10), und der Unterschied steckt schon im Zustand beim Wechsel.
- **H-β (Fenster in Schritten):** Adams Mittelwerte haben feste Fenster in *Schritten* (≈ 10 für m bei β₁ = 0.9, ≈ 50 für v bei β₂ = 0.98). Bei lr × 0.25 sind sie in Λ gemessen 4× kürzer; die Bewegung ist weniger verzögert und selektiver. EXP-081 stützt das post hoc: Ein längeres β₁-Fenster senkt die Festlegung beim Wechsel (π_m25 0.34/0.21/0.13 für β₁ 0.8/0.9/0.95, 9/10).
  *Vorhersage:* Mit Fenstern, die in Λ gleich lang sind wie beim Standardlauf (β₁′ = 1 − 0.25 · 0.1 = 0.975, β₂′ = 1 − 0.25 · 0.02 = 0.995 vor dem Wechsel), verschwindet der Vorsprung: π(l100b) ≈ π(n25), also e = π(l100) − π(l100b) ≈ +0.24 und d_b = π(l100b) − π(n25) ≈ 0.
- **H-disk (Diskretisierung / Schrittweite selbst):** Kleinere Schritte folgen dem Fluss genauer oder oszillieren weniger (Rückwärtsfehler-Terme ∝ Schrittweite; Barrett & Dherin 2020, Cattaneo et al. 2024). Die β-Anpassung ändert daran nichts: e ≈ 0, d_b ≈ +0.24.
- **Mischung:** beides trägt bei: e > 0 und d_b > 0.

## Versuch

| Punkt | Festlegung |
|---|---|
| **Protokoll** | wie EXP-089: add 113, ω = 0-Splits (EXP-053-Bau), Wechsel A → B und B → A bei t, danach 2000 Schritte mit Standard-Lernrate und Standard-β (0.9, 0.98); GPU, 1 Thread |
| **Zellen** | n25, n33, n45 (Standard, Kurve); l100 = lr × 0.25 für 100 Schritte (Replikation EXP-089); **l100b** = wie l100 mit β = (0.975, 0.995) vor dem Wechsel; **l100b1** = wie l100 mit β = (0.975, 0.98) (nur das m-Fenster angeglichen) |
| **Eingriff** | `freq_ban.py --pre-switch-betas b1,b2` (74a1d140, Tests grün): β gelten in den Updates 1 … t; beim Wechsel Standard-β, m und v so umskaliert, dass m̂ und v̂ stetig bleiben (Ereignisprüfung im Lauf). Bei Preset-Werten bitgleich mit dem normalen Lauf (Test) |
| **Seeds** | 3270–3285 (16, frisch; Dateisuche 28.09.) |
| **Umfang** | 16 × (2 + 6 × 2) = 224 GPU-Läufe à 2000–2100 Schritte, ≈ 25 min bei 8 Workern |
| **Primär** | e = π(l100) − π(l100b) und d_b = π(l100b) − π(n25), gepaart; 95-%-Perzentil-Bootstrap (10 000, rng 90) |
| **Lesart vorab** | e-KI > 0 **und** d_b-KI in [−0.1, +0.1] → ***H-β gestützt***; e-KI > 0 **und** d_b-KI > 0 → ***Fenster erklären einen Teil***; e-KI in [−0.1, +0.1] → ***Fenster erklären nichts*** (H-disk); sonst ***unklar***. < 10 gültige Seeds → *nicht auswertbar* |
| **Sekundär (beschreibend)** | d100 (Replikation EXP-089); f1 = π(l100) − π(l100b1) (Anteil des m-Fensters allein; EXP-081 lässt erwarten, dass β₁ den größeren Teil trägt, β₂ in Gegenrichtung klein); t_eq der Zellmittel auf der Kurve 25/33/45; Trennung beim Wechsel aus dem W_E-Schnappschuss bei t |
| **Gültigkeit je Seed** | alle 14 Läufe über den gemeinsamen Lader ok (Split-/Testhash, `lr_scale`, `pre_switch_betas`, β nach dem Wechsel 0.9/0.98, Schnappschüsse bei t und am Ende), Ereignisprüfung des β-Wechsels wahr, L(A) − L(B) ≥ 2 |
| **Was dagegen spräche (H-β)** | e ≈ 0 (β-Anpassung ändert nichts) oder d_b deutlich > 0 |
| **Grenzen** | Pilot; add 113, eine Architektur, ein Λ; die Fensterangleichung ist erster Ordnung (1 − β′ = c(1 − β)); die Bias-Korrektur in den ersten Schritten unterscheidet sich weiter (in Schritten gezählt); beim Wechsel tragen m̂/v̂ Inhalte des längeren Fensters in die Zeit danach (stetig, aber anders zusammengesetzt) |
| **Budget / Abbruch** | ≈ 25 min GPU. NaN oder fehlgeschlagene Ereignisprüfung → betroffene Seeds ungültig; > 6 ungültige → *nicht auswertbar* |
| **Bereits gesehene Daten** | EXP-089 (Seeds 3260–3269: Effektgröße, Ort beim Wechsel), EXP-081 (Seeds 830–839, π_m25 nach β₁ post hoc), R3. Beeinflusst: Wahl von Λ = 25, t = 100, der β′-Werte (Regel 1 − β′ = c(1 − β)), n = 16 (EXP-089-SD 0.15 → SE ≈ 0.04) und der Äquivalenzgrenze ±0.1 (wie EXP-089) |

## Ziel in FINDINGS

Größte offene Frage („Was macht die frühe Wahl fest?“). Entscheidet zwischen H-β und H-disk (Regel 18c). Fällt H-β, ist die Festlegungsuhr eine Eigenschaft von Adams Fenstern und keine Größe des Lernproblems allein.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-090-beta-window-lambda/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-090-beta-window-lambda/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-090-beta-window-lambda/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-090-beta-window-lambda/analyze.py
```
Selbsttest grün (Sitzung 40). Start erst nach der unabhängigen Prüfung von `--pre-switch-betas` (ohne Blocker).

## Nachtrag a (Sitzung 40, Commit 11:39 Berlin (8127533f; „≈ 11:42“ war nicht gemessen), nach der Code-Prüfung, vor dem Block; nur der Smoke lief, kein Ergebnis gelesen)

Unabhängige Prüfung von `--pre-switch-betas` (Claude-Agent, nur lesend): **kein Blocker.** Zeitpunkt richtig (Updates 1 … t mit β′, ab t + 1 Standard; `state["step"]` = t beim Umschalten), torch 2.9.1+rocm liest `group["betas"]` in jedem Schritt für EMA und Bias-Korrektur (foreach und single-tensor), Umskalierung hält m̂/v̂ stetig; ohne sie fiele v̂ um 2.2× und der Schritt stiege um ≈ 1.48×. Smoke (Seed 3270, l100b beide Richtungen): Ereignisprüfung wahr, Faktoren m 1.086, v 2.200, Test 0.995–1.0.
**Übernommen:**
1. **(M1) Zähler nach dem Wechsel:** Der Schrittzähler steht beim Wechsel auf t (100 in l100/l100b/l100b1, 25 in n25). Danach wirken neue Gradienten mit (1 − β)/(1 − β^(t+k)); bei t = 100 behält v̂ das Gedächtnis vor dem Wechsel etwa doppelt so lange (Anteil nach 50 Schritten 0.33 gegen 0.19). **Der Primärkontrast e = π(l100) − π(l100b) ist davon frei** (beide Arme t = 100, gleiche Regeln nach dem Wechsel). **d_b und d100 enthalten den Zählerunterschied** (wie schon EXP-089). Deshalb zusätzlich, vorab festgelegt, als *zählerfreie Lesart von d_b* (beschreibend, ändert das Primärurteil nicht): die Trennung beim Wechsel, Anteil r = (sep(l100b) − sep(n25)) / (sep(l100) − sep(n25)) aus den Zellmitteln. H-β erwartet r ≈ 0, H-disk r ≈ 1. Weicht das Primärurteil zu d_b von dieser Lesart ab, wird das so berichtet.
2. **β′-Werte:** exakte Angleichung wäre 0.9^(1/4) = 0.9740 und 0.98^(1/4) = 0.99496; wir bleiben bei der Regel erster Ordnung 1 − β′ = c(1 − β) (0.975/0.995). Der Unterschied im m-Fenster ist klein (0.975⁴ = 0.9037 statt 0.9).
3. **Auswertung verlangt** die Ereignisprüfung des β-Wechsels (schon im Lader; ein Lauf ohne Ereignis ist ungültig). Frühstopp ist bei t ≤ 100 und `stop_after_gen` 2000 ausgeschlossen.
**Nicht übernommen (Code bleibt):** Zähler beim Wechsel auf lr × t setzen: Das würde nur die l100b-Arme ändern und den Primärkontrast e verzerren. Kleinigkeiten (tautologische Ereignisprüfung, Fingerprint mit Rohstring, fehlender Test mit `--lr-scale` zusammen) dokumentiert; der Smoke deckt die Kombination ab.

## Ergebnis (Sitzung 40, 2026-09-28; 224/224 GPU-Läufe 11:39–11:58 Berlin laut Queue-Log; `analyze.py` über den Wächter; Pilot)

16/16 Seeds gültig, keine technischen Ausfälle, alle β-Wechsel-Ereignisse geprüft.
- **Primär, registriert: *H-β gestützt*.** e = π(l100) − π(l100b) = **+0.161** [0.099, 0.229], 15/16 > 0. d_b = π(l100b) − π(n25) = **+0.002** [−0.024, +0.024] (SD 0.05, 10/16 > 0), ganz in ±0.1.
- **Zählerfreie Lesart (Nachtrag a):** Trennung beim Wechsel n25 0.037, l100 0.056, l100b 0.038 → r = **0.04** (H-β erwartet ≈ 0, H-disk ≈ 1). Stimmt mit dem Primärurteil überein.
- **Sekundär:** Replikation EXP-089 d100 = +0.163 [0.092, 0.236] (EXP-089: +0.24). Nur das m-Fenster angeglichen (l100b1): f1 = π(l100) − π(l100b1) = +0.188 [0.120, 0.259]; l100b1 − n25 = −0.025 (5/16 > 0). Zusätzlich β₂ angeglichen (l100b − l100b1): +0.027 (13/16 > 0), klein. Zellmittel π: n25 0.33, n33 0.52, n45 0.87, l100 0.49, l100b 0.33, l100b1 0.31; t_eq l100 31.8, l100b **25.1**, l100b1 unter 25 (außerhalb der Kurve).

**Lesart (Interpretation, Pilot):** Werden Adams Mittelungsfenster in Lernratensumme gleich lang gemacht, verschwindet der Vorsprung der vielen kleinen Schritte vollständig: Die Festlegung folgt dann genau der Λ-Uhr (l100b liegt auf n25, KI ±0.024). Schon das Fenster des ersten Moments (β₁) allein erklärt den ganzen Effekt; das β₂-Fenster wirkt klein und in Gegenrichtung (wie in EXP-081). **Die „Mischuhr“ aus R3/EXP-089 ist also keine Eigenschaft der Schrittweite (H-disk verworfen für diesen Fall), sondern Adams Momentum-Verzögerung, die in Schritten zählt.** Zusammen mit EXP-081 (längeres β₁-Fenster → weniger Festlegung beim Wechsel; Momentum-Schwanz trägt mit der vorhergesagten Größe bei) ergibt sich ein einfaches Bild: Die frühe Festlegung tickt in Λ, gemessen mit einem Optimierer, dessen β₁-Verzögerung in Λ konstant ist. Eine längere Verzögerung (in Λ) macht die Bewegung vor dem Wechsel weniger selektiv.
**Grenzen:** Pilot, 16 frische Seeds, kein eingefrorenes Manifest; add 113, eine Architektur, ein Λ und ein c; Fensterangleichung erster Ordnung; der Zählerunterschied nach dem Wechsel (t = 100 gegen 25) steckt in d_b, die zählerfreie Lesart stimmt aber überein; Vollbatch (bei Minibatches käme Rauschen als weitere Schrittgröße hinzu).
**Folge:** Kandidat für eine Bestätigung (eingefrorenes Manifest, frische Seeds, zweite Λ-/c-Stufe, z. B. c = 2 mit β′ = 1 − 2(1 − β) = 0.8/0.96 und c = 0.5), dann Kernaussage in FINDINGS und Paper §3.10.

## Literatur (Sitzung 40, 12:03, nach dem Ergebnis; ändert keine Lesart)

Suche 2026-09-28 (WebSearch: „SDEs and scaling rules adaptive gradient algorithms beta rescaling“, „grokking Adam momentum beta1 critical period lock-in“). **Die Umskalierung selbst ist bekannt:** Malladi, Lyu, Panigrahi & Arora (NeurIPS 2022, [arXiv 2205.10287](https://arxiv.org/abs/2205.10287)) leiten für Adam/RMSprop SDE-Näherungen her; damit die Dynamik invariant bleibt, werden β₁, β₂ als 1 − κ(1 − β) mitskaliert (dort beim Skalieren der Batchgröße). Unsere Regel 1 − β′ = c(1 − β) ist dieselbe Zeit-Umparametrisierung für Vollbatch und Lernratenfaktor c. Nicht gefunden (nach dieser Suche): dass die frühe, persistente Frequenzwahl beim Grokking (Festlegung vor einem Datenwechsel) in Λ tickt, sobald die β₁-Verzögerung in Λ gemessen wird, und dass eine längere Momentum-Verzögerung die frühe Bewegung weniger frequenzselektiv macht. Einordnung: Anwendung einer bekannten Invarianz auf eine neue Messgröße; neu höchstens der Befund, nicht die Regel. Nächstverwandt zum Einfluss von Adam-Zeitskalen aufs Grokking: [arXiv 2609.18314](https://arxiv.org/html/2609.18314) (Stabilitäts-Phasendiagramm von Adam, konkurrierende Moment-Zeitskalen; nur Suchtreffer, nicht gelesen).

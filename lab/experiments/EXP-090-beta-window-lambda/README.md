---
id: EXP-090
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-090: Kommt die stärkere Festlegung vieler kleiner Schritte von Adams Fenstern, die in Schritten zählen? (Pilot)

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage: Was macht die frühe Wahl fest?) · Vorläufer [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]] (Nachtrag a: H-β), [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (β₁ als Hebel) · [[confirm/R3_REGISTRATION_DRAFT|R3]] · [[JOURNAL]] Sitzung 40.

**Festgelegt:** Sitzung 40, 2026-09-28, ≈ 11:50 Berlin, vor jedem EXP-090-Lauf. Pilot/Exploration (16 frische Seeds, kein eingefrorenes Manifest).

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

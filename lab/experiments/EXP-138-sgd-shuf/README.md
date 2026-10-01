---
id: EXP-138
status: abgeschlossen
datum: 2026-10-01
tags: [exp/abgeschlossen, befund/positiv]
verwandt: ["[[confirm/R13_REGISTRATION]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[experiments/EXP-128-sgd-clip/README|EXP-128]]", "[[FINDINGS]]"]
---
# EXP-138: Steuert die Trainingsmenge unter SGD über die Paarstruktur oder über die Token-Häufigkeiten? (Pilot)

Zurück zu [[LAB]]. **Exploration (4 Seeds), keine Bestätigung.**

**Bezug zu FINDINGS:** K2 und Paper-Grenze (i) („all results are AdamW results“). [[confirm/R13_REGISTRATION|R13]] (eingefroren, beim Dienst) prüft, ob die Menge das W_E-Spektrum auch unter geclipptem SGDm steuert. Die Prüfung vor dem Einfrieren (HIGH) wies darauf hin, dass die Kontrolle „Paarstruktur statt Token-Häufigkeit“ ([[experiments/EXP-047-marginal-control/README|EXP-047]]: unter AdamW Δ_shuf ≈ 0) unter SGD fehlt; ohne Adams koordinatenweise Normierung könnten die Token-Zählungen (die selbst Zielenergie tragen) durchschlagen. Dieser Pilot trennt das.

## Vorab (Sitzung 67, 2026-10-01, 06:21 Berlin gemessen; vor jedem Lauf)

- **Frage:** Unter R13-Einstellungen (Full-Batch-SGDm, lr 0.1, Momentum 0.9, Clip 0.1 bzw. 0.017, 2000 Schritte): Bleibt Δ_pow > 1, wenn die Paarstruktur zerstört, die Token-Häufigkeiten aber exakt erhalten sind?
- **Hypothese (wie unter AdamW):** Die Paarstruktur trägt (Δ_eng − Δ_shuf > 1), Δ_shuf klein.
- **Konkurrenzmodell:** Unter SGD tragen die Token-Häufigkeiten (Δ_shuf > 1).
- **Aufbau:** Trainer `freq_ban_sgdclip.py` (wie R13/EXP-128), EXP-047-Splits (eng = EXP-016-Konstruktion ε = 2, shuf = gleiche Randverteilungen von a und b, Paare zerstört), Seeds 150–153, Arme F/G, Test = Komplement. 4 Seeds × 2 Arten × 2 Arme × 2 Clip-Werte = 32 Läufe à ≈ 2.7 min, GPU.
- **Messgröße:** Δ_pow (P1-Formel, additive DFT) bei 2000 je Seed, getrennt für eng und shuf.
- **Lesart je Clip-Wert (`analyze.py`, vor jedem Lauf):** „Paarstruktur trägt“: Δ_eng − Δ_shuf > 1 in 4/4; „Häufigkeiten tragen“: Δ_shuf > 1 in ≥ 3/4 (beide Etiketten können zugleich gelten); keines → „unklar“; |Δ_eng| ≤ 1 in ≥ 3/4 → „keine Steuerung“ (geht vor); < 4 vollständige Seeds → „nicht auswertbar“.
- **Was dagegen spräche:** „Häufigkeiten tragen“ ohne „Paarstruktur trägt“ – dann wäre ein R13-„bestätigt“ unter SGD ein Zähleffekt, nicht der K2-Mechanismus.
- **Grenzen:** 4 Seeds, eine Aufgabe, ein Messschritt; Seeds 150–153 sind unter AdamW gesehen (EXP-047), unter SGD neu.
- **Bereits gesehene Daten:** EXP-047 (AdamW, alle Ergebnisse), EXP-126/128 (SGD auf anderen Splits), R13-Smoke (Seed 4399). Keine SGD-Läufe auf EXP-047-Splits.
- **Budget:** 32 × ≈ 2.7 min, 4 Worker, `gpu_gb=0.75`, eingereiht nach R13 (`50_exp138_sgd_shuf`).

## Befehle

```
python lab/experiments/EXP-138-sgd-shuf/make_jobs.py > lab/queue/staging/50_exp138_sgd_shuf.jobs && mv lab/queue/staging/50_exp138_sgd_shuf.jobs lab/queue/inbox/
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-138-sgd-shuf/analyze.py [--selftest]
```


## Ergebnis (Sitzung 67, 01.10., 06:54 Berlin gemessen; Dienst 32/32, keine Fehler)

`analyze.py` (Lesarten vorab): **Clip 0.1: „Paarstruktur trägt“**, **Clip 0.017: „Paarstruktur trägt“**; „Häufigkeiten tragen“ bei keinem.

| Clip | Seed 150 | 151 | 152 | 153 |
|---|---|---|---|---|
| 0.1: Δ_eng / Δ_shuf | 6.68 / 0.37 | 7.56 / 2.19 | 7.19 / 0.17 | 7.38 / 2.48 |
| 0.017: Δ_eng / Δ_shuf | 4.40 / 0.19 | 4.40 / 0.27 | 5.18 / 0.34 | 5.19 / 0.67 |

Beschreibend: bei 250 Δ_eng 0.17–0.36, Δ_shuf −0.02–0.04. Bei Clip 0.1 liegt Δ_shuf in 2/4 Seeds über 1 (2.19, 2.48) – unter der Regel „≥ 3/4“, aber ein kleiner Beitrag der Token-Häufigkeiten unter SGD ist damit nicht ausgeschlossen (unter AdamW in EXP-047: 0.02 ± 0.65). Deutung: Auch unter SGD trägt vor allem die Paarstruktur die Steuerung (Pilot, 4 Seeds). Paper: Halbsatz in Grenze (i) und Satz in Anhang J (mit R13).

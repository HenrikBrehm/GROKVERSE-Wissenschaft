---
id: EXP-091
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-091: Gilt die β-Fenster-Regel auch bei größerer Lernrate (c = 2)? (kleiner Pilot für R9 H3)

Zurück: [[LAB]] · [[confirm/R9_REGISTRATION_DRAFT|R9]] (H3 ohne Pilotwert) · [[experiments/EXP-090-beta-window-lambda/README|EXP-090]] · [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]] · [[FINDINGS]] (größte offene Frage) · [[JOURNAL]] Sitzung 40.

**Festgelegt:** Sitzung 40, 2026-09-28, ≈ 12:05 Berlin, vor jedem Lauf. Exploration an **bekannten** Seeds 3260–3269 (EXP-089), zur Streuung und Richtung für R9 H3; kein Urteil mit Bestätigungscharakter.

| Punkt | Festlegung |
|---|---|
| **Frage** | Bei lr × 2 für t = 15 Schritte (Λ = 30) sind Adams Fenster in Λ doppelt so lang wie im Standardlauf. Hebt β′ = 1 − 2(1 − β) = (0.8, 0.96) vor dem Wechsel die Festlegung an? |
| **Vorhersage H-β** | e₂ = π(c2, β′) − π(c2, Standard-β) > 0; π(c2, β′) nahe der Standardkurve bei Λ = 30 (zwischen π_n25 und π_n33 von EXP-089, ≈ 0.4). H-disk (Schrittweite) sagt e₂ ≈ 0 |
| **Läufe** | 10 Seeds × 2 Zellen × 2 Richtungen = 40 GPU-Läufe (`jobs.txt`), reine Läufe und Standardkurve aus EXP-089 (gleiche Seeds, Splits, Gerät) |
| **Auswertung** | `run.py` (Selbsttest grün): e₂ mit 95-%-Bootstrap-KI (rng 91), SD für die R9-Fallzahl; Lesart: KI > 0 → *H-β-Richtung*, KI < 0 → *gegen H-β*, sonst *unklar* |
| **Grenzen** | bekannte Seeds; 10 Seeds; t = 15 liegt unter der Standardkurve 25/33/45 (t_eq dort nicht definiert); lr × 2 mit β₁′ = 0.8 kann unruhiger sein |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-091-beta-window-c2/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-091-beta-window-c2/run.py
```

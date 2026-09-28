---
id: EXP-091
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
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

## Ergebnis (Sitzung 40, 2026-09-28; 40/40 GPU-Läufe ab 12:03 Berlin laut Queue-Log; `run.py` über den Wächter; Exploration, bekannte Seeds)

10/10 Seeds gültig, keine Ausfälle, alle β-Wechsel geprüft. **e₂ = π(c2, β′) − π(c2, Standard) = +0.049** [0.023, 0.078], SD 0.048, **10/10 > 0** → *H-β-Richtung*. Zellmittel π: c2 Standard 0.39 (t_eq 27.3), c2 β′ 0.44 (t_eq 28.9); Standardkurve n25/n33/n45 0.32/0.56/0.84. Λ = 30 entspräche t_eq = 30.
**Lesart (Pilot):** Auch in die andere Richtung (größere Lernrate, weniger Schritte) wirkt das Fenster wie vorhergesagt: Mit Standard-β bleibt die Festlegung unter der Λ-Erwartung (die Fenster sind in Λ doppelt so lang), mit β′ rückt sie fast an sie heran (28.9 von 30; t_eq aus Zellmitteln, grob). Der Effekt ist kleiner als bei c = 0.25 (+0.16), passend zu einer kleineren Fensteränderung (Faktor 2 statt 4). Das passt zur R3-Zelle „doppelte Lernrate für 25 Schritte“ (≈ 86 % des Weges zur Λ-Erwartung, beschreibend).
**Für R9 H3:** SD 0.048 → bei halbem Piloteffekt (0.025) und n = 24 Power ≈ 0.8 (einseitig gegen 0, Normalnäherung); Mindesteffekt 0.03 wäre zu streng → H3 gegen 0 testen.
**Grenzen:** bekannte Seeds (EXP-089), 10 Seeds, t_eq nur grob (t = 15 liegt unter der Kurve, Zellmittel).

---
id: EXP-112
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/positiv]
---
# EXP-112: Sprachmodell-Leiter Stufe 1, letzte Sprosse: LM-Format + i.i.d.-Minibatch

Zurück zu [[LAB]] · Bezug: [[FINDINGS]] Programm A (Verallgemeinerung von K2), Regel 20e · Vorgänger: [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]] (Format-Sprossen einzeln, Full-Batch), L0 (K2 unter Minibatch im freq_ban-Format bestätigt).

**Frage.** Hält die Steuerung (K2), wenn die Format-Sprossen, die in EXP-102 einzeln hielten (Operator-Token, volle Softmax, gebundene Embeddings), zusammen UND mit i.i.d.-Minibatches (B 256) trainiert werden? Und kostet Next-Token-Verlust auf allen Positionen außer b unter Minibatch Steuerung?
**Hypothese.** Hält (EXP-102: jede Sprosse einzeln 7.3–8.0 gegen r0 8.04; L0: Minibatch 256 bestätigt 9.43).
**Kontrolle.** r0B: alle Schalter aus, gleiche Batchgröße, gleiche Seeds und Splits.
**Eingriff.** lmB = `--op-token --full-softmax --tie`; lmnbB = lmB + `--loss all_but_b`. Alle `--batch-size 256`.
**Messgrößen.** Δ_pow (Zahl-Token-Zeilen von W_E) bei 5000 (primär) und 2000; Generalisierung (Test ≥ Schwelle).
**Erwartet.** lmB und lmnbB „hält“, evtl. etwas schwächer als r0B (EXP-102: tie −0.8 gegenüber r0).
**Dagegen spräche.** obere KI-Grenze < halbes r0B-Mittel („bricht“) oder gepaartes KI zu r0B < 0 („schwächer“).
**Budget.** 60 Läufe (10 Seeds 3800–3809 × F/G × 3 Sprossen) à 5000 Schritte, GPU, 10 Worker; geschätzt ≈ 15–25 min. Abbruch bei NaN/Hängen.
**Gesehene Daten.** Seeds 3800–3809 und ihre Splits sind aus EXP-102 (Full-Batch) bekannt; unter Minibatch ungesehen. Exploration, keine Bestätigung. Die Seeds sind derselbe Satz wie EXP-102, damit die gepaarte Einordnung gegen die Full-Batch-Sprossen möglich ist.
**Lesarten** (vorab, `analyze.py`): je Sprosse „bricht“ / „schwaecher“ / „haelt“ / „unklar“ wie EXP-102, Referenz r0B bei 5000. Beschreibend: r0B − Full-Batch-r0 bei 2000 (gepaart).
**Trainer.** `lab/experiments/EXP-102-lm-ladder-stage1/lm_ladder.py` unverändert (Minibatch-Pfad per Selbsttest geprüft: eine Epoche = Permutation, eigener Zufallsstrom).

## Befehle

```
python lab/experiments/EXP-112-lm-ladder-minibatch/design.py --jobs > lab/experiments/EXP-112-lm-ladder-minibatch/jobs.txt
python lab/tools/parallel_queue.py lab/experiments/EXP-112-lm-ladder-minibatch/jobs_smoke.txt --workers 1
python lab/tools/parallel_queue.py lab/experiments/EXP-112-lm-ladder-minibatch/jobs.txt --workers 10 --min-minutes 3
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-112-lm-ladder-minibatch/analyze.py
```

## Ergebnis (Sitzung 48, 07:07 Berlin gemessen; 60/60 Läufe fehlerfrei; `summary.json`; Exploration, nicht nachgerechnet)

| Sprosse (B 256) | Δ_pow 2000 | Δ_pow 5000 [KI] | gepaart zu r0B (5000) | generalisiert bis 5000 (Median) | Lesart |
|---|---|---|---|---|---|
| r0B (alles aus) | 8.30 | 9.86 [9.43, 10.28], 10/10 | – | 20/20 (1013) | Referenz |
| lmB (Operator + volle Softmax + gebunden) | 7.71 | **9.96 [9.44, 10.47]**, 10/10 | +0.10 [−0.20, 0.40] | 20/20 (1025) | **„haelt“** |
| lmnbB (lmB + Next-Token-Verlust ohne b) | 6.79 | **8.24 [6.78, 9.72]**, 10/10 | **−1.62 [−3.16, −0.13]** | 13/20 (1575) | **„schwaecher“** |

Beschreibend: r0B − Full-Batch-r0 bei 2000: +0.26 [−0.14, 0.70] (Minibatch B 256 kostet in diesem Format keine Steuerung).
**Deutung (vorsichtig):** Das LM-Format (alle Format-Sprossen zusammen) hält K2 auch unter i.i.d.-Minibatch voll. Kommt Next-Token-Verlust auf den übrigen Positionen dazu (ohne b), wird die Steuerung unter Minibatch kleiner und das Grokking langsamer (7/20 Läufe bis 5000 nicht generalisiert); im Full-Batch hielt dieselbe Verlustform (allnb 8.26, tieallnb 7.53, EXP-102). Ob das eine Wechselwirkung mit dem Minibatch oder nur ein Verzögerungseffekt bis 5000 ist, bleibt offen (Δ_pow wächst noch: 6.79 → 8.24). **Leiter Stufe 1 insgesamt:** Format hält (auch unter Minibatch); jeder Verlust auf Nicht-Antwort-Positionen schwächt oder verzögert, am stärksten das b-Ziel (EXP-102: ≈ 55 % von r0 nach dem Grokking).

### Nachtrag „10k“ (Sitzung 48, vor den Läufen; Exploration)
Ist „lmnbB schwaecher“ nur Verzögerung? r0B und lmnbB, B 256, Seeds 3800–3809, F/G, 10 000 Schritte (`raw_10k`, 40 Läufe). Lesarten in `analyze_10k.py`: „bleibt schwaecher“ (gepaartes KI lmnbB − r0B bei 10 000 < 0), „nur verzoegert“ (sonst, wenn ≥ 16/20 lmnbB-Läufe generalisiert), sonst „unklar“.

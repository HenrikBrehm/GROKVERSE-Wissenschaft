---
id: EXP-085
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar, programm/B, neu/kandidat]
---
# EXP-085: Kostet ein Datenwechsel im Festlegungsfenster auch in der MLP-Architektur Grokking-Zeit? (Pilot, bekannte Seeds)

Zurück: [[LAB]] · [[FINDINGS]] (Programm B, funktionale Signatur der Festlegung; Grenze „eine Architektur“) · [[NOVEL_DIRECTIONS]] N43 · Bestätigung im Transformer: [[confirm/R6_REGISTRATION_DRAFT|R6]] · Geschwister: [[experiments/EXP-075-mlp-lockin/README|EXP-075]] (π(t) im MLP, gleiche Seeds, nur 2000 Schritte nach dem Wechsel).

**Status:** vorbereitet, Sitzung 32 (2026-09-27, Berlin, Fenster zu), **vor jedem Lauf**. Jobliste, Smoke und `analyze.py` fertig, **ungetestet** (nur Syntaxprüfung). Pilot mit bekannten Seeds (400–409), Exploration.

## Frage und Bezug

Im Transformer verzögert ein Wechsel der Trainingsmenge das Grokking, solange die Frequenzwahl noch nicht persistiert (post hoc: N28, P3, EXP-059/056, N29, EXP-044; Spitze bei t ≈ 25, Vorzeichenwechsel dort, wo π ≈ 1). Gilt dieser Zusammenhang auch ohne Attention? EXP-075 misst π(t) im MLP, doch das MLP groks erst nach 3500–7600 Schritten (EXP-045), deshalb sind 2000 Schritte nach dem Wechsel für die Zeit zu kurz. EXP-085 wiederholt das EXP-075-Protokoll mit 10 000 Schritten und misst beides: π aus dem W_E bei t + 2000 (wie EXP-075) und die Zeit bis zur Generalisierung.

## Aufbau (vorab festgelegt)

| Punkt | Festlegung |
|---|---|
| Einheiten | Seeds 400–409 (bekannt), EXP-056-Splits ω = 0, gemeinsame Testmenge je Seed |
| Läufe | `--arch mlp`, GPU, `--threads 1`, `--stop-after-gen 100000` (kein vorzeitiger Stopp). A und B allein: 10 000 Schritte, W_E bei 2000 und 10 000. Wechsel A→B, B→A bei t ∈ {10, 25, 50, 100, 200}: t + 10 000 Schritte, W_E bei t, t + 2000, t + 10 000. 120 Läufe |
| Zeit | b = min(erste Testgenauigkeit ≥ 0.95, 10 000) ab Schritt 0, gemeinsamer Horizont; C(t) = Mittel beider Richtungen von log2 b(Wechsel@t) − log2 b(nur Ziel-Split) |
| Persistenz | π(t) wie EXP-056/059/075 aus dem W_E 2000 Schritte nach dem Wechsel (reine Läufe: Schritt 2000); nur Seeds mit L(A) − L(B) ≥ 2 |
| **Lesart (primär für diesen Piloten)** | Regel S2 aus R6: *gestützt*, wenn mittleres C(t) ≤ 0 für jedes t mit Median-π(t) ≥ 0.9 **und** mittleres C(t) > 0 für jedes t mit 0.2 ≤ Median-π(t) ≤ 0.8; *nicht auswertbar* bei < 8 Seeds mit π oder wenn eine der beiden Klassen leer ist (z. B. wenn π im MLP bis 200 nie 0.9 erreicht) |
| Beschreibend | C(t) und Median-π(t) je t, Anzahl positiver C je t, Generalisierung der reinen Läufe bis 10 000 |
| Was gegen die Hypothese spräche | *nicht gestützt*: Im MLP hängen die Zeitkosten nicht an der Persistenz; dann ist der Zusammenhang im Transformer architekturgebunden |
| Budget | 120 Läufe à ≤ 10 200 Schritte, MLP ≈ 0.004 s/Schritt (EXP-045) → ≈ 40 s je Lauf, ≈ 10 min bei 8 parallel |
| Bereits gesehen | Seeds 400–409: Transformer-Zeiten (Sitzung 32, Zyklus 11) und π (EXP-059); MLP-Frequenzen dieser Seeds (EXP-045 nutzte andere Splits). Keine MLP-Läufe auf den EXP-056-Splits vor EXP-075/085 |

**Neuheit:** siehe N43 (Suche vom 2026-09-27, 5 Anfragen; nicht gefunden, vorläufig).

## Reproduktion (im Fenster, alles über den Wächter; nach EXP-075)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-085-mlp-switch-cost/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-085-mlp-switch-cost/smoke.txt --workers 1
python lab/tools/parallel_queue.py lab/experiments/EXP-085-mlp-switch-cost/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-085-mlp-switch-cost/analyze.py
```

## Ergebnis (Sitzung 37, 2026-09-28, Läufe 04:12–04:24, Auswertung 04:25 Berlin, gemessen)

120/120 Läufe ok (GPU, `--workers 7`), 10/10 Seeds gültig. **Lesart nach Regel S2: *nicht auswertbar*.** Nur 5 Seeds erfüllen L(A) − L(B) ≥ 2 (Regel: ≥ 8); dasselbe Trennproblem wie EXP-075.
Beschreibend (kein Urteil): mittleres C(t) = −0.06 / −0.10 / −0.29 / −0.81 / −1.29 log2 bei t = 10 / 25 / 50 / 100 / 200. Positiv sind 1 / 1 / 1 / 0 / 0 von 10 Seeds. Median-π (5 Seeds) = −0.02 / 0.13 / 0.51 / 1.13 / 1.45. Im MLP verzögert ein früher Wechsel das Grokking bei keinem t, auch nicht dort, wo π noch klein ist (t = 10, 25). Im Transformer liegt C(25) bei +0.85 (R6). Das spricht vorläufig dafür, dass die Zeitkosten im Festlegungsfenster an die Attention-Architektur gebunden sind. Ein Urteil ist das nicht: bekannte Seeds, π nur an 5 Seeds, andere Zeitskala (MLP groks nach ≈ 3500–7600 Schritten). Programm B; keine Nachträge. [[JOURNAL]] Sitzung 37.

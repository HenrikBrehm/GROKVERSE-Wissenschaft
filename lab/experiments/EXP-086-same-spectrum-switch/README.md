---
id: EXP-086
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, programm/B, neu/kandidat]
---
# EXP-086: Kostet ein Wechsel zu einem Split mit *denselben* Zielfrequenzen auch Grokking-Zeit? (Kontrolle zu N43, Pilot)

Zurück: [[LAB]] · [[FINDINGS]] (Programm B) · [[NOVEL_DIRECTIONS]] N43 · [[confirm/R6_REGISTRATION_DRAFT|R6]] · Anlass: Skeptiker-Prüfung in [[JOURNAL]] Sitzung 32, Zyklus 21.

**Status:** vorbereitet, Sitzung 32 (2026-09-27, Berlin, Fenster zu), **vor jedem Lauf**. Splits erzeugt (reine Rechnung, bitgleicher Neubau geprüft). Jobliste, Smoke und `analyze.py` fertig, **ungetestet** (Syntaxprüfung). Pilot mit bekannten Seeds 400–409.

## Frage

Ein Wechsel A→B bei t = 25 verzögert das Grokking (post hoc in fünf Blöcken). Liegt das an einem **Konflikt der Frequenzmengen**, also an halb aufgebauten Merkmalen für F, während die neuen Daten G verlangen? Oder kostet **jede** frühe Datenänderung Zeit, etwa weil die schnelle Anfangsphase gestört wird? Der Skeptiker nannte das die ernsteste Alternative. EXP-086 wechselt deshalb bei 25 von A zu **A2**: gleiche Zielfrequenzen F, gleiche Stärke (realisierter M0-Anteil auf F bis auf ≤ 0.002 gleich), keine gemeinsamen Paare, gleiche Testmenge.

**Grenze der Konstruktion (vorab gefunden):** Ein zu A disjunkter Split mit *denselben Wellenphasen* wie A ist bei gleicher Stärke unmöglich. A hält die hoch gewichteten Paare seines Musters, der Rest trägt das Negativbild (Anteil auf F 0.083, also Zufallsniveau, selbst bei ε = 80). A2 hat daher neue Phasen. Kostet A→A2 so viel wie A→B, bleibt offen, ob eine generische frühe Änderung oder ein Phasenkonflikt die Ursache ist. Die R-Kontrolle trennt das teilweise.

## Aufbau (vorab festgelegt)

| Punkt | Festlegung |
|---|---|
| Einheiten | Seeds 400–409 (bekannt), EXP-056-Splits ω = 0 (A, B, Testmenge), neue Splits A2, R1, R2 (`make_splits.py`, Ströme `SeedSequence([86_001, seed, Zweck])`) |
| Läufe je Seed (9) | A2 allein (2000); A→A2 und A2→A bei 25 und bei 50 (t + 2000); R1 und R2 allein (12 000, Stopp 100 nach dem Ereignis); R1→R2 und R2→R1 bei 25 (12 025, dito). A, B allein und A↔B bei 25 liegen aus EXP-056 vor (gleiche Init und Testmenge, geprüft im Skript). 90 Läufe, GPU, `--threads 1` |
| Zeit | b = min(Ereignis, Horizont) ab Schritt 0, Horizont 2000 (A-, A2-, B-Arme) bzw. 12 000 (R-Arme); C_X(t) = Mittel beider Richtungen von log2 b(Wechsel) − log2 b(nur Ziel-Split) |
| **Primär** | D = C_AB(25) − C_AA2(25) > 0, exakter einseitiger Vorzeichentest über 10 Seeds; *gestützt* bei p < 0.05 |
| Beschreibend | C_AA2(25), C_AA2(50), C_RR(25) mit Vorzeichenzählung |
| Lesarten (vorab) | **Frequenzkonflikt:** D > 0 (gestützt) und C_AA2(25) nahe 0. **Generische frühe Störung:** D ≈ 0 und C_AA2(25) > 0 wie C_AB(25); dann ist N43 keine Frequenzaussage. Bleibt C_RR(25) dabei ≈ 0, ist ein Phasenkonflikt als Rest möglich. **Gemischt:** D > 0 und C_AA2(25) > 0, beides trägt bei |
| Budget | A-Arme ≈ 2000 Schritte, R-Arme bis 12 000 (Zufallssplits groken bei ≈ 3500–11 000); GPU bei 10 parallel ≈ 0.03 s/Schritt → A-Teil ≈ 5 min, R-Teil ≈ 20 min |
| Bereits gesehen | Die Zeiten von EXP-056 (A, B, A↔B@25) für diese Seeds (Sitzung 32, Zyklen 8 und 11); daraus die Wahl t = 25. Keine Läufe mit A2, R1, R2 |

## Reproduktion (im Fenster, alles über den Wächter)

```
python lab/experiments/EXP-086-same-spectrum-switch/make_splits.py        # reine Rechnung, prüft vorhandene Dateien bitgleich
python lab/tools/guarded_run.py -- python lab/experiments/EXP-086-same-spectrum-switch/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-086-same-spectrum-switch/smoke.txt --workers 1
python lab/tools/parallel_queue.py lab/experiments/EXP-086-same-spectrum-switch/jobs.txt --workers 10
python lab/tools/guarded_run.py -- python lab/experiments/EXP-086-same-spectrum-switch/analyze.py
```

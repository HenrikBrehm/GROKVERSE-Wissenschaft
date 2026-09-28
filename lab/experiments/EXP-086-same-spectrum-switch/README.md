---
id: EXP-086
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv, programm/B, neu/kandidat]
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

## Nachtrag a (Sitzung 33, 22:28 Berlin gemessen, vor jedem EXP-086-Lauf): A2 zeigt bei F zum Teil *gegen* A

Reine Rechnung auf den gespeicherten Split-Dateien (`gradient_overlap_s33.py`, `overlap_alignment_s33.py`, Ergebnis `gradient_overlap_s33.json`). Maß: Kosinus der Gradientenrichtungen erster Ordnung von W_E bei den Zielfrequenzen F (Frequenzinhalt X[k, c] = Σ_t e^{−2πikt/P} M(t, c − t) je Ausgabeklasse c, beide Operandenplätze; Realteil = Richtungen, wie sie sind; nahezu orthogonale Zufallszeilen von W_U angenommen, [[paper/draft]] §5).

| Paar (Seeds 400–409) | cos bei F (Mittel, Spanne) |
|---|---|
| A gegen A2 | **−0.52** (−0.55 … −0.49) |
| A gegen B (ω 0) | −0.53 (−0.56 … −0.50) |
| R1 gegen R2 | −0.42 (−0.45 … −0.39) |
| A gegen R1 | +0.06 (+0.04 … +0.09) |

**Grund:** Alle Splits kommen aus demselben Pool (alle Paare ohne Testmenge). Ein zu A disjunkter Split trägt deshalb das Negativbild von A (Erwartungswert ≈ −0.60 · X_A bei Zufallsauswahl aus dem Rest: 3831 von 12 769 − 2554 − 3831 = 6384 Paaren). A2 hat zwar dieselbe Stärke auf F (Anteil 0.177 gegen 0.176), aber etwa ein Viertel seiner F-Leistung (0.52² ≈ 0.27) liegt entlang **−A**. Der Rest ist neu und orthogonal. Die README oben nannte „neue Phasen“; genauer ist: teilweise *umgekehrte* Richtungen.

**Folgen für die Lesart (die Kriterien oben bleiben unverändert):**
1. D = C_AB(25) − C_AA2(25) > 0 lässt sich **nicht** durch eine Richtungsumkehr bei F erklären, weil A2 und B dort gleich stark gegen A zeigen. Ein positives D spricht damit sauberer für den Mengenkonflikt als bisher angenommen.
2. D ≈ 0 mit C_AA2(25) > 0 trennt „generische frühe Störung“ **nicht** von „Richtungsumkehr bei F“. Die R-Kontrolle trennt das auch nicht: R1 und R2 sind ebenfalls gegeneinander ausgerichtet (−0.42).
3. **Vorhersage des Richtungsmodells an schon gesehenen Daten (EXP-056):** Mit wachsender Überlappung ω zeigt B bei F weniger gegen A (cos −0.53 / −0.28 / −0.04 bei ω 0 / 0.2 / 0.4). Ein Modell „Kosten = Umkehr halb aufgebauter Richtungen“ sagt also *sinkende* Kosten mit ω voraus. Gesehen wurden *steigende* (Mediane 0.71 / 1.07 / 1.04; 8/10, p = 0.055, Sitzung 32). Das spricht schwach gegen das Richtungsmodell und für ein Konkurrenzmodell (Kosten, solange die neuen Daten die alten Merkmale nicht aktiv abbauen). Post hoc, n. s., nur Hinweis.
4. **Vorhersage vor dem Lauf (Konkurrenzmodell):** C_AA2(25) nahe 0 oder negativ (keine zweite Frequenzmenge), D > 0. Richtungsmodell und generisches Modell: C_AA2(25) ≈ C_AB(25).

## Ergebnis (Sitzung 37, 2026-09-28, Läufe 02:31–02:46, Auswertung 02:46 Berlin, gemessen)

90/90 Läufe ok (GPU, `--workers 7`, daneben das CPU-Programm), 10/10 Seeds gültig, keine defekten Läufe. **Primär gestützt:** D = C_AB(25) − C_AA2(25) = **+0.82** log2, 9/10 positiv, p = 0.011 (exakter einseitiger Vorzeichentest).

| Größe (log2, Mittel über 10 Seeds) | Wert | positiv |
|---|---|---|
| C_AB(25) (Wechsel zu B, andere Ziele) | +0.57 | 8/10 |
| C_AA2(25) (Wechsel zu A2, gleiche Ziele) | −0.26 | 4/10 |
| C_AA2(50) | −0.98 | 0/10 |
| C_RR(25) (Zufallssplit zu Zufallssplit) | −0.80 | 0/10 |

**Lesart nach der vorab festgelegten Regel: *Frequenzkonflikt*** (D > 0 gestützt, C_AA2(25) nahe 0 bzw. negativ). Die Vorhersage vor dem Lauf (Nachtrag a, Punkt 4, Konkurrenzmodell) ist getroffen; Richtungsmodell und generisches Modell (C_AA2(25) ≈ C_AB(25)) nicht. Ein früher Wechsel kostet also nicht an sich Zeit: Ein Wechsel auf neue Paare mit *denselben* Zielfrequenzen beschleunigt eher (bei 50 in 10/10 Seeds, zwischen Zufallssplits bei 25 ebenfalls in 10/10), obwohl A2 bei F in erster Ordnung genauso gegen A zeigt wie B (cos −0.52 gegen −0.53). Die Verzögerung braucht eine *andere Zielmenge*. **Grenzen:** Pilot an bekannten Seeds (400–409; C_AB(25) stammt aus EXP-056), n = 10; die Beschleunigung durch neue Paare ist ein eigener Effekt (mehr verschiedene Trainingspaare insgesamt) und hier nicht getrennt. Programm B, [[FINDINGS]] Zeitsignatur; [[JOURNAL]] Sitzung 37.

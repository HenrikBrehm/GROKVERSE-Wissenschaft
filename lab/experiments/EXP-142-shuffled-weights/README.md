---
id: EXP-142
status: vorbereitet
datum: 2026-10-01
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-140-random-at-edge/README|EXP-140]]", "[[confirm/R15_REGISTRATION|R15]]", "[[experiments/EXP-139-pair-count/README|EXP-139]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-142: Reicht irgendeine gleich starke Ungleichgewichtung der Paare, oder braucht es die Frequenzstruktur? (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds), keine Bestätigung.** [[NOVEL_DIRECTIONS]] N64.

**Bezug zu FINDINGS:** R5 und der LeDoux-Einwand (Regel 20b). [[experiments/EXP-140-random-at-edge/README|EXP-140]] zeigte bei add 401 / 14 000 Paaren: konstruierte Menge (ε = 2) generalisiert bei ≈ 5 500 Schritten, gleich große Zufallsmenge nicht in 30 000. Die Prüfung vor dem Einfrieren von [[confirm/R15_REGISTRATION|R15]] (MEDIUM 2) wies darauf hin, dass damit nur „konstruiert gegen gleichverteilt“ verglichen ist, nicht „frequenzgerichtet gegen beliebig ungleich“. Regel-15b-Begründung: kein Rest-Nachtrag, sondern die fehlende Kontrolle für die Deutung von EXP-140/R15; drei billige Läufe.

## Vorab (Sitzung 69, 2026-10-01, geschrieben 12:02 Berlin (gemessen), vor jedem EXP-142-Lauf)

- **Frage:** Generalisiert ein Arm U im Budget, dessen Paargewichte genau die von F sind, aber zufällig über die p² Paare permutiert (gleiche Gewichtsverteilung, keine Frequenzstruktur)?
- **Aufbau:** Gewichte q von F exakt wie `EXP-043/make_split.engineered_train_idx` (Seed, Ziele, Phasen; Reproduktion des F-Splits von EXP-139 geprüft, bitgleich), dann Permutation und gewichtete Schlüsselziehung mit eigenem Strom (Salz 3000); genau 14 000 Paare. Seeds 13900–13902 (gleiche Init wie EXP-139 F/G und EXP-140 R), `freq_ban.py` unverändert, GPU, 30 000 Schritte, Stopp 2000 nach gen.
- **Vorab-Rechnung (`make_jobs.py --check`):** Masken-Top-5 von U überlappt die F-Ziele in 0/0/1 von 5; Abdeckung wie F und R (Streuung je Ausgabe U 5.48–5.80, F 5.53–5.69, R 5.65–5.82; je Zahl U 5.53–6.04, F 5.23–5.58; Minimum je Ausgabe 19–22 überall).
- **Lesart (`analyze.py`, Selbsttest grün):** U generalisiert in ≤ 1 von 3 Seeds → „Frequenzstruktur nötig (nicht bloßes Ungleichgewicht)“; in ≥ 2 von 3 und Median gen_U / gen_E ≤ 1.5 → „Ungleichgewicht reicht“; sonst „Ungleichgewicht hilft teilweise“. Fehlender/nicht abgeschlossener Lauf → „nicht auswertbar“.
- **Was dagegen spräche:** „Ungleichgewicht reicht“ → EXP-140/R15 zeigen dann einen Effekt der Ungleichmäßigkeit, nicht der Frequenzen; Wortwahl im Paper entsprechend.
- **Budget:** 3 Läufe à ≈ 4 GB (EXP-140 gemessen 2.9 GB), ≤ 20 min je Lauf.
- **Grenzen:** 3 Seeds, eine Zelle, ein Budget; Permutation zerstört jede Struktur (auch Zeilen-/Spaltenmuster), ist also nur eine von vielen „unstrukturierten“ Kontrollen.
- **Bereits gesehen:** EXP-139 (alle Zellen), EXP-140 (alle 3 R-Läufe), R15-Prüfung; kein U-Lauf.

## Befehle

```
python lab/experiments/EXP-142-shuffled-weights/make_jobs.py > lab/queue/staging/52a57_exp142_shuf.jobs
python lab/experiments/EXP-142-shuffled-weights/make_jobs.py --check
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-142-shuffled-weights/analyze.py [--selftest]
```

## Ergebnis

Offen (beim GPU-Dienst als `52a57_exp142_shuf`, nach R15 p 307, vor EXP-141).

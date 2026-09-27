---
id: EXP-056
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[BACKLOG]]", "[[experiments/EXP-053-p3-overlap-design/README|EXP-053]]", "[[experiments/EXP-044-generalize-lockin/README|EXP-044]]", "[[experiments/EXP-020-data-switch/README|EXP-020]]", "[[JOURNAL]]"]
---
# EXP-056: Hängt die Persistenz nach einem Datenwechsel an der Überlappung der Splits? (P3-Pilot, Paket B)

Zurück zu [[LAB]] · [[FINDINGS]] (Paket B, P3; offene Frage „Festlegung im Netz oder nur geteilte Paare?“) · Konstruktion
[[experiments/EXP-053-p3-overlap-design/README|EXP-053]] · [[BACKLOG]] „Entwurf P3-Bestätigung“.
Festgelegt 2026-09-27 04:44 Berlin (Sitzung 21), **bevor ein EXP-056-Lauf oder -Split existiert**. **Pilot** (Regel 15b: 10 Seeds; liefert die Streuung für P3).

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-020 (add 113, ≈ 73 % geteilte Paare; π 0.38/0.72/≈1 bei t = 25/50/150) und EXP-044
(add 97/mul 113, ≈ 38 %; π(25) 0.37/0.22, SD 0.12/0.17). Daraus: t = 25 (empfindlichster Wechselzeitpunkt, π weit weg von 0 und 1) und das Maß π.
EXP-053: Konstruktion und ε-Kalibrierung (Seeds 900–909, reine Rechnung). Die Seeds 400–409 wurden nie benutzt (geprüft 04:41).

| | |
|---|---|
| **Frage** | Hält das Netz nach 25 Schritten auf A die Frequenzen von A gegen B fest, weil es sich festgelegt hat (i), oder nur, soweit A und B Paare teilen (ii)? |
| **Konkurrenzmodelle** | (i) Festlegung im Netz: π unabhängig von ω · (ii) geteilte Paare halten die Wahl: π steigt mit ω · (iii) ELR (Lyle et al. 2025) wird hier **nicht** getrennt (gleiches lr, gleiche Init, gleicher Wechselzeitpunkt in allen Stufen) |
| **Aufgabe/Modell** | add 113, Transformer der Studie (`freq_ban.py`), GPU (nach GPU-001), 1 Thread |
| **Splits** | EXP-053 `overlap_split.build`: A (Ziele F) und B (Ziele G), je 3831 Paare, geteilter Anteil ω ∈ {0, 0.2, 0.4} (gleichverteilt), ε je Stufe auf gleiche Steuerstärke kalibriert (`calibration.json`), eine gemeinsame Testmenge je Seed für alle Stufen. `make_splits.py` |
| **Arme je Seed und ω** | nur A (2000), nur B (2000), A→B und B→A (25 Schritte auf dem ersten, dann genau 2000 auf dem zweiten). Gleiche Init (Seed) in allen 12 Läufen eines Seeds |
| **Seeds** | 400–409 (Init, Split-Ströme über `SeedSequence([53001, seed, level, zweck])`) → 120 Läufe |
| **Maß** | L = log[P(F)/P(G)] der W_E-Leistung am Ende (DFT, EXP-043 `group_power`). π_AB = (L(A→B) − L(B)) / (L(A) − L(B)), π_BA entsprechend, π = Mittel (0 = wie nur der zweite Split, 1 = wie nur der erste) |
| **Gültig** | Stufe: alle vier Läufe ok (gemeinsamer Lader: Seed, Gerät, Schritte, Split-/Test-/Wechsel-Hashes, endlicher Snapshot) und L(A) > L(B). Seed: alle drei Stufen gültig |
| **Primär** | b_s = Steigung (kleinste Quadrate) von π über ω je Seed; einseitiger t-Test b̄ > 0 über gültige Seeds |
| **Urteil** | < 8 gültige Seeds → *nicht auswertbar* · b̄ > 0 und p < 0.05 → ***Überlappung trägt Persistenz (ii)*** · 90-%-KI von b̄ ganz in [−0.25, 0.25] (Δπ ≤ 0.1 über ω 0 → 0.4) → ***Persistenz unabhängig von der Überlappung (i)*** · sonst ***unklar*** |
| **Sekundär (beschreibend)** | π je ω (Mittel, SD) als Grundlage der P3-Stichprobe; π_AB gegen π_BA; π(ω = 0) > 0 heißt: Festlegung auch ganz ohne geteilte Paare |
| **Erwartung** | offen. EXP-020 (73 %) und EXP-044 (38 %) liegen bei t = 25 ähnlich (0.38 gegen 0.22–0.37), das spricht eher für (i). (ii) wäre die sparsamere Erklärung ohne „Gedächtnis“ im Netz |
| **Was dagegen spräche** | Für (i): b̄ deutlich > 0. Für (ii): π(ω = 0) ≈ π(ω = 0.4) |
| **Grenzen** | ε unterscheidet sich zwischen den Stufen (2.23/3.01/5.94; die Gewichte werden binärer), Häufigkeitsrang der Ziele bei ω = 0.4 etwas besser (EXP-053). Nur add 113, ein Wechselzeitpunkt, ω ≤ 0.4 |
| **Budget** | 120 Läufe à 2000–2025 Schritte auf der GPU, 8 parallel ≈ 5–10 min; davor ein Smoke (60 Schritte, Wechsel bei 30) |

**Neuheit:** vorläufig. Die Frage „trägt das Netz oder die Datenüberlappung die Persistenz der Frequenzwahl“ ist nach der Suche vom 2026-09-26 (Sitzung 14, [[NOVEL_DIRECTIONS]])
nicht gefunden; hier nicht neu gesucht.

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-056-overlap-persistence/make_splits.py
python lab/experiments/EXP-056-overlap-persistence/make_splits.py --jobs > lab/experiments/EXP-056-overlap-persistence/jobs.txt
python lab/tools/parallel_queue.py lab/experiments/EXP-056-overlap-persistence/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-056-overlap-persistence/analyze.py
```

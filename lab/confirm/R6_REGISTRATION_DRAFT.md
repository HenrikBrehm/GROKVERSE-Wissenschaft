---
id: R6
status: entwurf
datum: 2026-09-27
tags: [lab/confirm, programm/B, paper, exp/vorbereitet, neu/kandidat]
---
# R6: Verzögert ein Datenwechsel mitten in der Festlegung das Grokking? Bestätigung an frischen Seeds (Registrierungsentwurf)

Zurück: [[LAB]] · [[FINDINGS]] (Programm B, größte offene Frage: funktionale Signatur der Festlegung) · [[NOVEL_DIRECTIONS]] N43 · [[JOURNAL]] Sitzung 32, Zyklen 5–6 · Konstruktion wie [[confirm/N28_REGISTRATION|N28]].

**Status:** Entwurf, Sitzung 32 (2026-09-27, Berlin, Fenster zu), **vor jedem R6-Lauf**. Code `lab/tools/confirm_r6.py` geschrieben, **ungetestet** (nur Syntaxprüfung; Selbsttest im Fenster). Einfrieren erst nach Codex-Prüfung und grünem Selbsttest.

## Warum

Post hoc (Sitzung 32) habe ich zum ersten Mal die Generalisierungszeiten gespeicherter Wechsel-Blöcke gelesen. **N28** (30 Seeds, GPU): Ein Wechsel A→B bzw. B→A bei 25 Schritten generalisiert pro Seed in 28/30 später als der Lauf nur auf dem Ziel-Split (Mittel C(25) = 0.54 log2, SD 0.42). Bei 50 Schritten ist er in 24/30 früher. C(25) − C(50) = 0.90 (SD 0.62), 27/30. **P3** (Seeds 1050–1079, Hypothese vorher festgelegt): 28/30. **EXP-020** (CPU, 5 Seeds): @10/@25/@50 langsam, @150/@400 schnell. Die Kosten eines Datenwechsels scheinen dort am größten, wo die Frequenzwahl umschlägt (K4c: 25 → neu, 50 → alt). Das wäre eine funktionale, billige Messung der Festlegung. Alle Zahlen sind post hoc an Seeds, deren Frequenzen gesehen waren.

## Aufbau

- **Konstruktion:** EXP-053 `overlap_split`, ω = 0, gleiche Steuerstärke (ε aus `calibration.json`), gemeinsame Testmenge je Seed; identisch zu N28. **Seeds 2800–2819** (20, frisch, vor jeder Nutzung reserviert in [[FINDINGS_DETAILS]]).
- **Läufe je Seed (16):** A allein und B allein (je 2000 Schritte); Wechsel A→B und B→A bei **t ∈ {10, 20, 25, 30, 40, 50, 75}** (t + 2000 Schritte, AdamW-Zustand bleibt). freq_ban, GPU, `--threads 1`, Stopp 2000 Schritte nach der Generalisierung (Standard; der Stopp liegt nie vor dem Horizont 2000). 320 Läufe.
- **Zeit:** b = min(Ereignis, 2000). Das Ereignis ist der Trainerschritt mit der ersten Testgenauigkeit ≥ 0.95, gezählt ab Schritt 0. Der **gemeinsame Horizont 2000 gilt für alle Arme**, zwei beidseitig zensierte Läufe ergeben also genau 0. Gezeigt wird damit „frühere Generalisierung bis 2000“, nicht die Endgenauigkeit.
- **Kosten je Seed:** C(t) = Mittel über beide Richtungen von log2 b(Wechsel@t) − log2 b(nur Ziel-Split). Das Ziel von A→B ist B.

## Hypothesen (Primärfamilie, Holm über 2 bei α = 0.05)

- **H1:** C(25) > 0. Ein Wechsel bei 25 Schritten verzögert das Grokking gegenüber dem Training nur auf dem Ziel-Split.
- **H2:** C(25) − C(50) > 0. Die Verzögerung ist bei 25 größer als bei 50.
- **Test je Hypothese:** p = max(p_flip, p_Vorzeichen). p_flip ist der einseitige Vorzeichen-Permutationstest des Mittels (100 000 Züge, fester Seed, (Überschreitungen + 1)/(N + 1)). p_Vorzeichen ist der exakte einseitige Binomialtest über die Seeds mit |Wert| > 1e-9. „Bestätigt“ heißt Holm-p < 0.05. Die Effektgröße ist das Mittel mit 95-%-Bootstrap-KI und Faktor 2^Mittel (geometrisches Mittel des beschränkten Zeitverhältnisses), nur als Schätzer. Es gibt keine Mindesteffekt-Schwelle als Urteil.
- **Nullhypothese:** Innerhalb eines Seeds sind die verglichenen Arme austauschbar. Eine Ablehnung heißt „verzögert, in der vorhergesagten Richtung“.

## Sekundär (außerhalb der Familie, „gestützt“ / „nicht gestützt“)

- **S1 (Lage der Spitze):** Das t aus dem Raster mit dem größten mittleren C liegt höchstens 10 Schritte neben t_π. t_π ist der erste Wechselzeitpunkt, an dem der Median der Persistenz π(t) (N28-Definition, End-W_E, nur Seeds mit L(A) − L(B) ≥ 2) den Wert 0.5 erreicht, linear interpoliert. Das verknüpft die Zeitkosten mit der gemessenen Festlegung.
- **Beschreibend:** Mittel und Median von C(t) für alle t, Ereignisanteile je Arm, π(t).

## Stichprobe

n = 20. Die Power ergab sich aus einer Simulation der Entscheidungsregel (p = max(Vorzeichen, Flip), Holm über 2), gezogen aus den N28-Werten je Seed: n = 10 → 0.62, n = 15 → 0.92, **n = 20 → 0.99**. Die N28-Effektgröße ist nach der Auswahl dieser Hypothese vermutlich zu optimistisch (Winner's Curse), daher 20 statt 15. Bei P3 (Replikation) lag der Median bei 0.53, ähnlich.

## Gültigkeit

Alle 16 Läufe eines Seeds sind gebunden und über den gemeinsamen Lader geladen (Seed, Gerät, Schrittbudget, Split-, Test- und Wechsel-Hash, W_E-Schnappschuss am Ende endlich), dazu mindestens 2000 abgeschlossene Schritte. Die Splits sind bitgleich mit dem deterministischen Neubau. Fehlt ein Seed, ist R6 *nicht auswertbar*; es wird nicht mit weniger Seeds geurteilt.

## Was dagegen spräche

- H1 nicht bestätigt: Die Verzögerung bei 25 war eine Eigenheit von N28/P3 (gesehene Seeds) oder hängt am Block.
- H1 bestätigt, H2 nicht: Jeder frühe Wechsel verzögert; eine Spitze im Festlegungsfenster ist nicht belegt.
- S1 nicht gestützt: Die Zeitkosten messen etwas anderes als die Persistenz π.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

Die Generalisierungszeiten von N28 (Seeds 2200–2229), P3 (1050–1079), EXP-020 (30–34) und EXP-041 (20–29) wurden in Sitzung 32 gelesen (`lab/confirm/speed_switch_cost_*_s32.py`, `speed_prefix_s32.py`). Beeinflusst sind die Hypothesen, die Wahl von 25/50, das Raster, der gemeinsame Horizont 2000 und n. Kein Lauf mit Seeds 2800–2819.

## Grenzen (vorab)

Eine Aufgabe (add 113), eine Architektur, eine Optimierer-Einstellung, eine Split-Konstruktion (ω = 0). Die Wechselkosten mischen zwei Einflüsse: die Unterbrechung der Festlegung und die zusätzlichen verschiedenen Paare nach dem Wechsel. Letztere beschleunigen eher (E→R-Befund); H1 ist deshalb konservativ. EXP-020 (andere Konstruktion, CPU) zeigte @50 noch langsam: Die Lage des Fensters kann von der Konstruktion abhängen.

## Reproduktion (im Fenster; Muster wie P2f/N28)

```
python lab/tools/guarded_run.py -- python lab/tools/confirm_r6.py --selftest
# Manifest lab/confirm/R6_manifest.json = REGISTERED + python (absoluter .venv-gpu-Pfad) + registration + code_sha256 (--hash-code); committen, commit setzen, committen
python lab/tools/confirm_r6.py --splits lab/confirm/R6_manifest.json
python lab/tools/confirm_r6.py --jobs lab/confirm/R6_manifest.json > lab/confirm/R6_jobs.txt      # ohne Wächter
# Smoke: erste Jobzeile allein über parallel_queue, dann --analyze (nur Lader prüfen; nicht auswertbar erwartet)
python lab/tools/parallel_queue.py lab/confirm/R6_jobs.txt --workers 10                           # ≈ 35 min GPU
python lab/tools/guarded_run.py -- python lab/tools/confirm_r6.py --analyze lab/confirm/R6_manifest.json
```

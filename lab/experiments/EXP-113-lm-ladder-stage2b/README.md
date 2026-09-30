---
id: EXP-113
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, lm-leiter, befund/positiv, befund/unklar]
---
# EXP-113: Sprachmodell-Leiter Stufe 2b – mehr Expositionen je Fakt, Verlust nur auf der Antwort als Kontrolle

Zurück: [[LAB]] · [[FINDINGS]] · Vorgänger [[experiments/EXP-105-lm-ladder-stage2/README|EXP-105]] (Pilot „unklar“) · Stufe 1 [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]] / [[experiments/EXP-112-lm-ladder-minibatch/README|EXP-112]] · [[JOURNAL]] Sitzung 49

**Bezug zu FINDINGS:** Verallgemeinerung von K2 (Programm A, Regel 15c) auf ein kleines Sprachmodell von Grund auf (Regel 20e, Stufe 2). Exploration (2 Seeds), keine Bestätigung.

## Vorab (Sitzung 49, 10:33 Berlin gemessen, vor jedem Lauf)

- **Frage:** Steuert die Auswahl der Rechenfakten die Zahl-Embeddings eines kleinen LM (≈ 14 M Parameter, TinyStories + eingestreute Rechensätze), wenn das Modell die Fakten tatsächlich lernt? Der EXP-105-Pilot (167 Runden je Fakt, 8.7 % Rechen-Tokens) war dafür zu kurz: ein Seed begann zu lernen (Δ_pow 1.75, Testfakten 0.22/0.13), der andere nicht.
- **Hypothese:** Mit ≈ ×6 Expositionen lernen beide Seeds die Fakten; dann ist Δ_pow > 1 (K2 hält). Mit Verlust nur auf den Antwort-Tokens (Text unverändert) lernt das Modell schneller als mit Verlust auf allen Positionen (Stufe 1: Verlust auf dem Operanden b verzögert > ×10).
- **Aufbau:** `lm_stage2.py` (unverändertes Modell, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, Kontext 256) mit `--arith-facts 8` (≈ 34 % Rechen-Tokens, geschätzt aus den Schablonenlängen) und 16 000 Schritten (≈ 1 070 Runden je Fakt, Text ≈ 87 Mio. Tokens von 113.7 Mio., kein Umlauf erwartet). Modell-Seeds 3862/3863 ↔ P1-Splits der EXP-102-Seeds 3802/3803 (F/G mit gleicher Init, gleichem Text, gleichen Positionen); gemeinsame Testmenge je Seed = EXP-102 `design.build(seed)["test"]` (`tests/`). Zwei Verlust-Arme: `--loss all` (wie EXP-105) und `--loss answer` (in Rechenblöcken nur auf c). 8 Läufe, GPU-Dienst (`jobs.txt`, `make_jobs.py`), Checkpoints alle 1000 Schritte.
- **Budget/Abbruch:** geschätzt ≈ 1.3 s/Schritt bei 8 gleichzeitigen LM-Läufen → ≈ 6 h; harte Grenze je Lauf 600 min (Dienst). Abbruch bei NaN (Trainer bricht selbst ab) oder Textumlauf > 0 (wird protokolliert, dann Ergebnis mit Vermerk).
- **Messgrößen/Lesarten je Verlust-Arm (`analyze.py`, am Budgetende):** wie EXP-105-Pilot („K2 haelt im LM“: Δ_pow > 1 in beiden Seeds und Testfakten > 0.5 in ≥ 3/4 Läufen; „nur Repraesentation“: Δ_pow > 1 in beiden Seeds und Testfakten < 0.1 in ≥ 3/4; „bricht“: |Δ_pow| ≤ 1 in beiden Seeds; sonst „unklar“), mit Vorrangregel **„nicht gelernt (Budget)“**, wenn die Trainingsfakten-Genauigkeit in ≥ 3/4 Läufen < 0.1 ist. Beschreibend: Δ_pow(answer) − Δ_pow(all) je Seed; erster Schritt mit Testfakten ≥ 0.5 je Lauf.
- **Was gegen die Hypothese spräche:** Beide Seeds lernen die Fakten (Testfakten > 0.5), aber |Δ_pow| ≤ 1 → „bricht“: Im LM trägt die Faktenauswahl die Frequenzwahl nicht (das wäre die erste Stufe, auf der K2 bricht; Regel 20e).
- **Bereits gesehene Daten:** EXP-105-Pilot (Seeds 3860/3861, P1-Splits 3800/3801), Stufe-1-Ergebnisse (EXP-102/112 auf den Split-Seeds 3800–3809, also auch 3802/3803 im Stufe-1-Format). Davon beeinflusst: Wahl von K, Budget und der Kontrollarm.
- **Abweichung vom Stufe-2-Plan:** Rechenanteil ≈ 34 % statt „wenige Prozent“ – bewusst, weil die Expositionen der Engpass waren; hält K2 hier, prüft eine spätere Stufe einen kleineren Anteil.


## Nachtrag 1 (Sitzung 50, 11:43 Berlin gemessen, vor jedem fertigen Lauf): zusätzliche beschreibende Vorhersage

Die Lesarten oben bleiben unverändert. **Beobachtung vorab (Einblick in die Checkpoints, rein beschreibend, ändert keine Entscheidung):** Im Arm `answer`, Seed 3862, ist Δ_pow bis Schritt 4000 ≈ 0 (0.01, −0.00, 0.01, 0.08 bei 1000–4000), die Faktengenauigkeit liegt auf Zufallsniveau. Im EXP-105-Pilot stieg Δ_pow erst mit dem Faktenlernen (3860: ≤ 0.25 bis Schritt 7000, 1.75 bei 10 000 mit Trainingsfakten 0.78/0.73; 3861 ohne Faktenlernen ≤ 0.12). Im Spielzeugmodell ist es umgekehrt: Δ_pow ≈ 3 schon bei Schritt 250, lange vor dem Grokking (P2de post hoc).
**Vorhersage (H-folgt), festgelegt vor dem Ergebnis:** Im LM geht die Frequenzsteuerung dem Faktenlernen nicht voraus. Beschreibend geprüft je Lauf-Paar (F/G eines Seeds und Arms), das Trainingsfakten lernt: der erste Snapshot mit Δ_pow > 1 liegt nicht vor dem ersten Snapshot, an dem beide Läufe Trainingsfakten-Genauigkeit ≥ 0.1 haben. Widerlegt, wenn in mindestens der Hälfte dieser Paare Δ_pow > 1 früher erreicht wird. Paare ohne Faktenlernen zählen nicht. Auswertung mit den gespeicherten Snapshots (Abstand 250 Schritte) nach Ende aller Läufe; Exploration (2 Seeds).

**Hinweis zu Nachtrag 1 (12:52, vor dem Ende der Läufe; H-folgt unverändert registriert):** Die Begründung „im Spielzeugmodell umgekehrt“ war falsch verglichen (Test- statt Trainingsgenauigkeit). Im Spielzeugmodell setzen Steuerung und Trainingsfakten-Anpassung zusammen ein (25/50 Seeds Steuerung vorher, post hoc, EXP-114 `toy_order_s50`). Zwischenblick Seed 3862 `answer`: Δ_pow 2.05 bei 8500 bei Trainingsfakten 0.026/0.117, also ein Snapshot vor der Schwelle in F. Ausgewertet wird trotzdem nach der Regel.

## Ergebnis (Sitzung 56, 30.09. 04:08–04:14 Berlin gemessen; 8/8 Läufe ohne Fehler, GPU-Dienst `40_exp113_stage2b`)

Befehle: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze.py` → `summary.json`; `analyze_folgt.py` → `folgt_summary.json`; post hoc `commutativity_s56.py` (Lesart vorab im JOURNAL S56 Zyklus 6) → `commutativity_s56.json`.

| Arm | Seed | Δ_pow (16 000) | zurückgehalten F / G | Test ≥ 0.5 ab F / G | s_steer / s_learn |
|---|---|---|---|---|---|
| answer | 3862 | 7.00 | 0.983 / 0.950 | 9500 / 9250 | 8500 / 9000 |
| answer | 3863 | 4.79 | 0.948 / 0.947 | 7000 / 6750 | 5750 / 6250 |
| all | 3862 | 2.06 | 0.510 / 0.108 | 15 500 / – | 7000 / 9250 |
| all | 3863 | 1.76 | 0.198 / 0.317 | – / – | 5750 / 7500 |

- **Lesarten (vorab):** answer **„K2 haelt im LM“**; all **„unklar“** (Δ_pow > 1 in beiden Seeds, aber zurückgehalten weder ≥ 0.5 in 3/4 noch < 0.1 in 3/4; Trainingsfakten 0.94–0.96 gelernt). **H-folgt: widerlegt** (4/4 Paare mit Δ_pow > 1 vor dem Lernbeginn beider Arme).
- **Beschreibend:** Im Arm all war Δ_pow beim Lernbeginn 3.48 / 3.80 und fiel bis zum Ende auf 2.06 / 1.76.
- **Kommutativität (post hoc, vorab festgelegte Lesart): „teilweise“** – Tauschpaar trainiert / sonst: 3862 F 0.60 / 0.47, 3862 G 0.28 / 0.03, 3863 F 0.56 / 0.05, 3863 G 0.36 / 0.30; answer-Modelle 0.96–0.99 / 0.94–0.98.
- **Deutung (Exploration, 2 Seeds):** Bei ≈ 34 % Rechen-Tokens und Antwort-Verlust lernt und steuert das LM (wie LM1 bei 79 %). Mit Verlust auf allen Positionen lernt es die Trainingsfakten auswendig, verallgemeinert in 16 000 Schritten aber kaum; die Steuerung bleibt messbar (> 1), wird aber schwächer. Das passt zu Stufe 1 (EXP-102). Grenze: 2 Seeds, ein Budget; ein zensierter Lauf beweist nicht, dass später keine Verallgemeinerung käme.

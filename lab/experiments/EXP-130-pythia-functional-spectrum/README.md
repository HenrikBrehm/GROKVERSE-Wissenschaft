---
id: EXP-130
status: abgeschlossen
datum: 2026-09-30
tags: [exp/abgeschlossen, befund/negativ, lab/lm, neu/kandidat]
verwandt: ["[[experiments/EXP-127-pretrained-lm/README|EXP-127]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]", "[[BACKLOG]]"]
---
# EXP-130: Funktionales Frequenzspektrum eines nachtrainierten Pythia-160M (Pilot)

Zurück zu [[LAB]]. **Exploration (2 Seeds × F/G), keine Bestätigung.**

**Bezug zu FINDINGS / Regel 20 e2:** K2 beim Nachtrainieren eines vortrainierten LMs ([[experiments/EXP-127-pretrained-lm/README|EXP-127]], N58). EXP-127 misst, welche Frequenzen die *Änderung* der Zahl-Einbettung trägt, und ablatiert nur drei Sätze (eigene Ziele, fremde Ziele, 4 Kontrollen). Diese Stufe fragt: **Welche Frequenzen braucht das nachtrainierte Modell tatsächlich (Ablation jeder einzelnen Frequenz), die vortrainierten Zahlmerkmale oder die aus den Daten gewählten?**

## Vorab (Sitzung 61, 30.09., ≈ 16:25 Berlin, vor jedem EXP-130-Lauf)

**Bereits gesehene Daten, die diesen Entwurf beeinflusst haben (offen genannt):** der erste fertige EXP-127-Lauf (Seed 4000, Arm F, 4000 Schritte, Testgenauigkeit 0.987). Ablation der Eingabeseite: eigene Ziele {15, 26, 30, 38, 45} weg → 0.986 (keine Wirkung); fremde Ziele {2, 10, 43, 53, 54} weg → 0.717; Kontrollen mit 23 ({8, 23, 28, 31, 32}, {3, 23, 37, 41, 49}) → 0.705 / 0.675, die anderen zwei → 0.985 / 0.974. Das legt „Wiederverwendung vortrainierter Frequenzen (2, 3, 23?)“ nahe. Darauf beruht die Hypothese H-reuse, sie ist also **nicht unabhängig** von diesen Daten. Deshalb laufen hier andere Splits (LM1-Seeds 4002/4003), und die Lesarten stehen fest, bevor ein Lauf von EXP-130 existiert. Die übrigen EXP-127-Läufe waren beim Schreiben noch nicht fertig und nicht ausgewertet.

- **Frage:** Welche einzelnen Frequenzen k ∈ 1..56 der 113 Zahl-Token-Zeilen braucht ein auf (a + b) mod 113 nachtrainiertes Pythia-160M für die zurückgehaltene Genauigkeit, und hängt das von der Faktenauswahl (F gegen G) ab?
- **Aufbau:** genau wie EXP-127 (`ft_pythia.py` unverändert importiert; 4000 Schritte, lr 10⁻⁴, wd 0.1, Batch 32, K = 16, Operator „ @“), Splits `lab/confirm/lm1_splits/seed4002_{F,G}.npy`, `seed4003_{F,G}.npy` mit ihren Testmengen (je 2554 Fakten). Nach dem Training zusätzlich (`ft_sweep.py`): Ablation jeder einzelnen Frequenz auf der Eingabe-, der Ausgabeseite und beiden; dazu die vortrainierten Top 8 der Eingabe {1, 2, 3, 11, 4, 5, 23, 45} und der „Dezimalsatz“ {11, 23, 45} als Sätze.
- **Messgröße:** Wichtigkeit f_side(k) = Basisgenauigkeit − Genauigkeit ohne k. Top 5 = die (höchstens) fünf k mit größtem f_in, **aber nur k mit f_in ≥ 0.01** (Nachtrag vor jedem Lauf, Codeprüfung S61: sonst füllen Gleichstände bei ≈ 0 die Top 5 mit k = 1, 2, 3 … und begünstigen „Wiederverwendung“). Beschreibend je Modell: welche eigenen Ziele in den vortrainierten Top 8 liegen (Seed 4002 G: 5, 11; 4003 F: 45; 4003 G: 5 – ein reines Wiederverwendungsmodell kann dort n_own = 2 haben und fiele dann unter „gemischt“; so vorab festgelegt), Zahl der k über der Schwelle, Gleichstände am Rand der Top 5.
- **Lesarten (je Modell, dann über die 4 Modelle; Tor: Basisgenauigkeit ≥ 0.5 in ≥ 3/4, sonst „nicht auswertbar“):**
  - **„Wiederverwendung“:** In ≥ 3 von 4 Modellen liegen ≥ 3 der Top 5 (Eingabe) in den vortrainierten Top 8 **und** ≤ 1 der Top 5 ist ein eigenes Ziel. (Zufall: im Mittel 5·8/56 ≈ 0.71 bzw. 5·5/56 ≈ 0.45 Treffer.)
  - **„Datenwahl“:** In ≥ 3 von 4 Modellen sind ≥ 3 der Top 5 (Eingabe) eigene Ziele.
  - **„gemischt“:** In ≥ 3 von 4 Modellen je ≥ 2 aus beiden Mengen in den Top 5.
  - sonst **„unklar“**.
  - Reihenfolge der Prüfung wie oben (erste zutreffende Lesart gilt). Ein eigenes Ziel, das zugleich in den vortrainierten Top 8 liegt (z. B. 45 in einem Arm), zählt in beiden Mengen; das wird je Modell beschreibend angegeben.
  - Beschreibend: Spearman-ρ von f_in zwischen F und G desselben Seeds (hoch = die Faktenauswahl ändert kaum, was das Modell braucht); Wirkung der Sätze „vortrainierte Top 8“ und „Dezimal“; dieselbe Auswertung für die Ausgabeseite; Einzelwirkung gegen Satzwirkung (verteilt vs. konzentriert).
- **Was gegen „Wiederverwendung“ spräche:** Top 5 aus den eigenen Zielen oder aus Frequenzen, die weder vortrainiert stark noch Ziele sind; F und G mit verschiedenen wichtigen Frequenzen.
- **Codeprüfung (unabhängiger Agent, nur lesend, S61, vor jedem Lauf):** keine Blocker. Übernommen: Basis-Vergleich nach dem Sweep mit Toleranz 2/n statt exakt (GPU nicht bitgleich; ein exakter Assert hätte einen ganzen Lauf gekostet), zusätzlich `base_after`; Schwelle 0.01 für die Top 5; Spearman mit Durchschnittsrängen; `load()` filtert auf 4000 Schritte; Beschreibung eigener Ziele in den Top 8.
- **Nachtrag vor jedem Lauf (≈ 17:27, EXP-130 noch nicht gestartet):** `ft_sweep.py` speichert die nachtrainierten Gewichte (fp16, ≈ 0.33 GB je Lauf) nach `raw/models/model_split<seed>_<arm>.pt`, vor dem Sweep. Anlass: EXP-127 endete „bricht“, und die Vorab-Folge dort ist „Zwischenschichten messen, bevor etwas behauptet wird“; das braucht die Modelle. Lesarten unverändert; Speichern per Einheitentest geprüft (CPU, kleines Modell).
- **Nachtrag vor jedem Lauf (17:31, nach Sicht der EXP-127-Verläufe, siehe dort): zusätzliche, nur beschreibende Zählung** der Top 5 in der Menge „vortrainiert oder Parität“ = vortrainierte Top 8 ∪ {56} (k = 56 ≈ Periode 2 trug in EXP-127 die Änderung mit, liegt aber nicht in den Top 8 des Ausgangsspektrums). Die Lesarten oben bleiben unverändert (Top 8 ohne 56).
- **Grenzen vorab:** Die Ablation entfernt einen linearen Unterraum nur in den 113 Zahlzeilen; das Modell kann Information auch anders tragen (z. B. über den Positions-/Kontextweg). Einzelablation unterschätzt verteilte Kodierung (daher die Sätze). 2 Seeds → Exploration.
- **Budget:** 4 GPU-Läufe à ≈ 36 min (EXP-127-Tempo unter Last) + Sweep (≈ 174 Auswertungen à 2554 Aufgaben, geschätzt wenige Minuten), gpu_gb 5 (EXP-127 gemessen 4.4 GB), 2 Worker. Abbruch: Divergenz (Trainer bricht selbst ab) oder Tor verfehlt.

## Befehle

```
# Smoke (CPU, 2 Schritte, 100 Testaufgaben; nur Funktion):
python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-130-pythia-functional-spectrum/ft_sweep.py --seed 4002 --split-file lab/confirm/lm1_splits/seed4002_F.npy --test-file lab/experiments/EXP-130-pythia-functional-spectrum/smoke/test100.npy --targets-file lab/confirm/lm1_splits/seed4002.json --steps 2 --batch 2 --k 2 --device cpu --threads 4 --out-root lab/experiments/EXP-130-pythia-functional-spectrum/smoke/raw
# Läufe: Jobdatei lab/queue/inbox/44zz_exp130_sweep.jobs (Dienst)
# Auswertung:
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-130-pythia-functional-spectrum/analyze.py
```

## Ergebnis (Sitzung 62, 30.09., Auswertung 19:54 Berlin gemessen): „Wiederverwendung“

Dienst `44zz_exp130_sweep` 4/4 fertig (Seed 4002: 18:17–19:03, Seed 4003: 19:03–19:54). `analyze.py` (unverändert, vor jedem Lauf geschrieben) → `summary.json`. Tor erfüllt (Basis 0.994 / 0.984 / 0.986 / 0.981). **Top 5 der Einzelfrequenz-Wichtigkeit (Eingabe) in allen vier Modellen dieselbe Menge {1, 2, 11, 23, 56}** (Reihenfolge 1, 2/56, 23, 11; je 4 davon in den vortrainierten Top 8, 56 ≈ Periode 2 nicht); eigene Ziele darin: 1 (4002 F: 56; 4002 G: 11), 0 (Seed 4003). → Vorab-Lesart **„Wiederverwendung“** (≥ 3 vortrainierte und ≤ 1 eigenes Ziel in 4/4 Modellen). Wichtigkeit der Top 5: 0.23–0.50 je Frequenz; je Modell 7–8 Frequenzen über der Schwelle 0.01; je ein Gleichstand am Rand der Top 5.

**Beschreibend:** Ausgabeseite dieselbe Menge (Top 5 aus {1, 2, 3, 11, 23, 56}). Die vortrainierten Top 8 wegnehmen → Verlust 0.94–0.95 (Eingabe), den „Dezimalsatz“ {11, 23, 45} → 0.58–0.63. Eigene gegen fremde Ziele: Seed 4002 0.34 / 0.24 (F) und 0.26 / 0.38 (G), in beiden Fällen, weil die Menge 56 (F-Ziele) oder 11 (G-Ziele) enthält; Seed 4003 (Ziele ohne 1, 2, 11, 23, 56) 0.009 / 0.004 und 0.011 / 0.018. Spearman-ρ der Wichtigkeiten F gegen G: 0.66 (4002), 0.63 (4003). Die Menge deckt sich mit der, auf der sich in [[experiments/EXP-127-pretrained-lm/README|EXP-127]] die Rest-Änderung sammelte ({2, 3, 11, 23, 56}); hier an frischen Splits, nicht nur als Energie, sondern als Nutzung.

**Deutung (vorläufig, Pilot, 2 Seeds):** Das nachtrainierte Pythia-160M rechnet (a + b) mod 113 unabhängig von der Faktenauswahl mit derselben kleinen Menge von Frequenzen, die überwiegend schon vortrainiert stark sind (1 ≈ Größe, 11/23 ≈ Dezimalperioden 10/5, 2), plus 56 ≈ Parität. Das passt zu Zhou et al. 2024 (tiefe Frequenzen für die Größe, hohe für Modulo-Anteile wie gerade/ungerade), hier für einen Modul, der nicht auf die Dezimalperioden ausgerichtet ist. Offen: ob der vortrainierte Rumpf oder die vortrainierten Zahlzeilen diese Wahl festlegen → [[experiments/EXP-133-pythia-reset-numbers/README|EXP-133]]; Zwischenschichten → [[experiments/EXP-131-pythia-layer-spectrum/README|EXP-131]].

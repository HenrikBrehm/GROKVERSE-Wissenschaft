---
id: EXP-083
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, programm/B, paper]
---
# EXP-083: Nimmt der Attention-Reset nur mehr Bewegung zurück als der MLP-Reset? (Exploration, bekannte Seeds)

Zurück: [[LAB]] · [[FINDINGS]] (K4d/K4e, Grenze „MLP-Kontrolle nicht nach Verschiebung angeglichen“) · [[confirm/N29b_REGISTRATION|N29b]] · [[confirm/N29c_REGISTRATION|N29c]] · [[JOURNAL]] Sitzung 30 · Anlass: Gutachter-Durchgang zum [[paper/draft]] (Einwand O6).

**Status:** vorbereitet, Sitzung 30 (2026-09-27, 18:28 Berlin gemessen), vor jedem Lauf. Jobliste und `measure.py` fertig, **ungetestet**. Exploration an gesehenen Seeds (N29b 2300–2319, N29c 2320–2339), kein Urteil für FINDINGS, nur beschreibend fürs Paper.

## Frage und Bezug

K4d/K4e: Ein Reset von Attention (bzw. W_V/W_O) beim Wechsel nach 50 Schritten senkt den Ablationskontrast stark, der MLP-Reset (bzw. W_Q/W_K) kaum. Naheliegende Gegenerklärung eines Gutachters: Der wirksamere Reset nimmt einfach **mehr Bewegung** zurück (‖W(50) − W(0)‖), unabhängig davon, welches Modul es ist. Die Blöcke speichern die Gewichte bei Schritt 50 nicht (nur W_E), darum war das bisher nicht messbar.

## Aufbau (vorab)

- Je Seed und erstem Split (A, B) ein Lauf mit **denselben** Argumenten wie der No-Reset-Arm des Blocks, aber `--steps 50` und `--save-model` (GPU, `--threads 1`): 80 Läufe à 50 Schritte, `jobs.txt`.
- **Tore (vor jeder Zahl, sonst keine Ausgabe):** Init-Prüfsumme gleich `init_checksum_shared`; W_E bei Schritt 0 und 50 gleich dem gespeicherten W_E-Schnappschuss des eingefrorenen No-Reset-Laufs (max |Δ| ≤ 10⁻³). Damit ist gesichert, dass der Zustand bei Schritt 50 der des Blocks ist.
- **Maß:** je Teil ‖W(50) − W(0)‖_F (= was der Reset auf die Init entfernt) und relativ zu ‖W(0)‖_F; je Seed Mittel über A/B; Verhältnis groß/klein für attn/mlp (N29b-Seeds) und vo/qk (N29c-Seeds).
- **Lesart (vorab):** Ist die Verschiebung des *schwächer* wirkenden Resets (MLP bzw. QK) in ≥ 15/20 Seeds größer → Größen-Erklärung für dieses Paar widersprochen („size alternative contradicted“). Ist die des stärker wirkenden in ≥ 15/20 größer → Größen-Erklärung bleibt offen (nicht trennbar). Sonst unklar. Beides getrennt für absolut und relativ; widersprechen sich absolut und relativ, gilt „unklar“.
- **Was die Messung nicht kann:** Der Reset löscht auch den AdamW-Zustand (nicht gemessen); gleiche Verschiebung heißt nicht gleiche funktionale Wirkung. Eine Verschiebungs-angeglichene Reset-Kontrolle wäre ein eigener Versuch (nur, wenn hier „offen“ herauskommt).
- **Budget:** 80 × 50 Schritte; Laufzeit von Start/Import beherrscht, bei 8 parallel ≈ 3–5 min. Abbruch bei Torfehler: Ursache klären, nicht Toleranz ändern.

## Befehle (nur im Fenster, alles über den Wächter)

```
python lab/tools/parallel_queue.py lab/experiments/EXP-083-reset-displacement/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-083-reset-displacement/measure.py
```

## Ergebnis

(noch keins)

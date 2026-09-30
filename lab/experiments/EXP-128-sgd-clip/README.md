---
id: EXP-128
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet]
---
# EXP-128: K2 ohne Adam, zweiter Anlauf – Full-Batch-SGD mit Momentum und Gradient-Clipping

Zurück: [[LAB]] · [[FINDINGS]] · Vorläufer [[experiments/EXP-126-sgd-steering/README|EXP-126]] („nicht auswertbar“) · [[JOURNAL]] Sitzung 58

**Bezug zu FINDINGS:** Geltungsbereich von K2 (Programm A); Paper §7 (i): „all results are AdamW results“. Anlass: In EXP-126 lernte SGDm bei lr 0.05 nichts (0/8) und divergierte bei lr 0.1 (8/8, meist zwischen 1000 und 1500 Schritten); beschreibend folgte der einzige lernende Lauf der Datenauswahl (0.92 der W_E-Energie auf den eigenen Zielen).

## Stand (Sitzung 58): Code vorbereitet, NICHT angewendet

- `freq_ban.py` ist bis zur R12-Auswertung hash-gebunden (R12-Manifest) → Änderung liegt als **`trainer_sgdclip.patch`** bereit (gegen HEAD 32cd1598-Stand geprüft: `git apply --check` sauber). Inhalt: Option `--sgd-clip C` (nur mit `--optimizer sgdm`; begrenzt die globale Gradientennorm vor jedem SGD-Schritt, nach der Projektion; Zähler `events.sgd_clip.clipped_steps`; Run-ID-Suffix `_clip…`; Standard aus → Fingerabdruck unverändert).
- Tests (in einem Worktree mit angewendetem Patch, über den Wächter, 09:13–09:21): neuer Test `test_sgd_clip` (Standard ändert den Fingerabdruck nicht; winziges Clipping begrenzt den Schritt, wirkungsloses Clipping 1e6 zählt 0 Schritte und lässt den Schritt > 100× größer; ungültige Aufrufe werden abgelehnt), gesamte `test_freq_ban_fingerprint.py` (10 Blöcke) und `test_freq_ban.py` (18 Tests) grün.
- **Erweiterung (09:28–09:33 gemessen):** der Patch protokolliert zusätzlich die Gradientennorm *vor* dem Clipping (`events.sgd_clip.norms`: Schritte 1–200, dann alle 250, und jede nicht endliche Norm). Kalibrierung dann ohne Raten: ein Lauf mit wirkungslosem Clipping (1e6) liefert die Normen. Tests erneut grün (`test_sgd_clip`, `test_minibatch_order`, Fingerprint-Unit, `test_freq_ban.py` 18/18); die ganze Fingerprint-Suite lief mit der ersten Patch-Fassung (10/10), die Erweiterung berührt nur den Clipping-Pfad.
- **Nach R12:** Patch anwenden (`git apply`), Tests erneut im Fenster, dann Pilot festlegen: EXP-126-Splits/Seeds 3704–3707 (gesehen), lr 0.1, Momentum 0.9, Clipping auf einen Wert, der aus gemessenen Normen folgt (vorab festlegen: Kalibrierlauf mit `--sgd-clip 1e6` auf einem gesehenen Seed, z. B. Median der Norm in Schritt 1–200), Lesarten wie EXP-126. Bei „K2 ohne Adam“ im Pilot: Bestätigungsblock mit frischen Seeds.

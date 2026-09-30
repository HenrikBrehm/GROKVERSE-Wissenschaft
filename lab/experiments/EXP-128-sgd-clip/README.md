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
- **Erweiterung (09:26–09:29, Commit-Zeit):** der Patch protokolliert zusätzlich die Gradientennorm *vor* dem Clipping (`events.sgd_clip.norms`: Schritte 1–200, dann alle 250, und jede nicht endliche Norm). Kalibrierung dann ohne Raten: ein Lauf mit wirkungslosem Clipping (1e6) liefert die Normen. Tests erneut grün (`test_sgd_clip`, `test_minibatch_order`, Fingerprint-Unit, `test_freq_ban.py` 18/18); die ganze Fingerprint-Suite lief mit der ersten Patch-Fassung (10/10), die Erweiterung berührt nur den Clipping-Pfad.
- **Nach R12:** Patch anwenden (`git apply`), Tests erneut im Fenster, dann Pilot festlegen: EXP-126-Splits/Seeds 3704–3707 (gesehen), lr 0.1, Momentum 0.9, Clipping auf einen Wert, der aus gemessenen Normen folgt (vorab festlegen: Kalibrierlauf mit `--sgd-clip 1e6` auf einem gesehenen Seed, z. B. Median der Norm in Schritt 1–200), Lesarten wie EXP-126. Bei „K2 ohne Adam“ im Pilot: Bestätigungsblock mit frischen Seeds.

## Pilot (Sitzung 59, 30.09., vor jedem geclippten Pilotlauf festgelegt)

- **Trainer:** `freq_ban_sgdclip.py` = `freq_ban.py` @267fde1e + `trainer_sgdclip.patch` (Kopie, SHA-256 f51752ea…; `freq_ban.py` selbst bleibt bis zur R12-Auswertung unverändert). Gleiche Pfadtiefe wie das Original, importiert dasselbe `training/grokverse`.
- **Kalibrierung (gesehen, Seed 3704 F, lr 0.1, Momentum 0.9, `--sgd-clip 1e6`, 2000 Schritte, `calib/`):** Norm Schritt 1: 0.108, Median Schritt 1–200: **0.0173** (Spanne 0.016–0.108); danach 0.026 (250), 0.035 (500), 0.034 (750), 1.15 (1000), ab 1126 unendlich (Divergenz an derselben Stelle wie in EXP-126, 1000–1250).
- **Arme:** C_A = **0.017** (vorab festgelegte Regel: Median der Norm in Schritt 1–200). C_B = **0.1** (neu, vor jedem Pilotlauf: ≈ 3× die größte gemessene Norm vor dem Aufschaukeln, 0.035; kappt nur Spitzen, sonst gewöhnliches SGDm). Grund für C_B: Im Smoke mit C_A (Seed 3704 F, 3000 Schritte, gesehen, `smoke/`) wird fast jeder Schritt gekappt (2691/3000) – C_A ist praktisch normiertes SGDm mit Schrittlänge 0.0017 und lernt langsam (Train 0.010 → 0.100 bei 3000, Verlust 4.74 → 3.83, beschleunigend); keine Divergenz.
- **Sonst wie EXP-126:** EXP-100-Splits F/G der Seeds 3704–3707 (gesehen), lr 0.1, Momentum 0.9, wd entkoppelt wie dort, 20 000 Schritte ohne Frühstopp, GPU. 16 Läufe (`make_jobs.py`, Dienst `46_exp128_sgdclip`, 4 Worker, gpu_gb 0.75; ≈ 0.07–0.1 s/Schritt unter Last → 25–35 min je Lauf, Block ≈ 2 h).
- **Lesarten je Clipping-Wert (`analyze.py`, wie EXP-126):** Lauf „divergiert“ (Spektrum bei 20 000 oder Train-Genauigkeit nicht endlich **oder eine nicht endliche Gradientennorm protokolliert** – neu, weil der gepatchte Trainer bei Divergenz endliche Spektren behalten kann, gesehen im Kalibrierlauf), „nicht gelernt“ (Train < 0.99), sonst ok. **„K2 ohne Adam“**: ≥ 3 auswertbare Seeds und Δ_pow > 1 in allen; **„bricht“**: ≥ 3 auswertbar und |Δ_pow| ≤ 1 in allen; **„nicht auswertbar“**: < 3; sonst „unklar“. Beschreibend: Δ_pow bei 2000, Anteil gekappter Schritte, Generalisierung, Testgenauigkeit.
- **Deutung vorab:** „K2 ohne Adam“ in C_B (fast gewöhnliches SGDm) spricht gegen ein Adam-Artefakt; nur in C_A gilt es für normiertes SGDm (keine koordinatenweise Normierung, aber auch nicht Standard-SGD). „bricht“ bei lernendem SGD → die Steuerung braucht Adams koordinatenweise Normierung (Befund für §7 i). Pilot auf gesehenen Seeds: bei „K2 ohne Adam“ Bestätigungsblock mit frischen Seeds, sonst nur Satz in §7 (i).
- **Abbruch:** harte Grenze 120 min je Lauf; Divergenz beendet nichts.

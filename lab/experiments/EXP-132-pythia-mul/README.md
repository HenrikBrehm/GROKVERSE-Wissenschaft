---
id: EXP-132
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, lab/lm, neu/kandidat]
verwandt: ["[[experiments/EXP-127-pretrained-lm/README|EXP-127]]", "[[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]"]
---
# EXP-132: Vortrainiertes Pythia-160M auf Multiplikation mod 113 nachtrainieren – steuert die Faktenauswahl dort? (Pilot, N60)

Zurück zu [[LAB]]. **Exploration (2 Seeds × F/G), keine Bestätigung.**

**Bezug:** N60 in [[NOVEL_DIRECTIONS]]; Geltungsgrenze von K2 beim Nachtrainieren ([[FINDINGS]], Exploration S61). [[experiments/EXP-127-pretrained-lm/README|EXP-127]] (Addition) ergab „bricht“, und die Änderung trug in allen Armen vortrainierte Dezimal-/Paritätsfrequenzen (23, 11, 2, 56, 3). Frage hier: Setzt sich die Faktenauswahl durch, wenn die vortrainierten Merkmale zur Aufgabe nicht passen? Multiplikation mod 113 ist eine Addition in Log-Koordinaten; Dezimalmerkmale über a helfen dort nicht direkt.

## Vorab (Sitzung 61, 30.09., 17:52 Berlin gemessen, vor jedem EXP-132-Lauf)

**Bereits gesehen:** EXP-127 vollständig (inkl. Verlauf), die zwei ersten EXP-127-Läufe mit Ablationen. Nichts aus EXP-132 oder EXP-130.

- **Aufbau:** wie EXP-127 (`ft_pythia.py` unverändert importiert; 4000 Schritte, lr 10⁻⁴, wd 0.1, Batch 32, K = 16, Operator „ @“), nur c = a·b mod 113 (`ft_mul.py` ersetzt Stream.batch, prompts, power und projector; Basis = diskreter Logarithmus zur Wurzel 3 wie P1/EXP-043). Fakten = P1-mul113-Splits Seed 1000/1001 (F/G je 3831, Überlappung 1177/1148, Ziele in Log-Koordinaten: 1000 F {1, 12, 28, 47, 49}, G {19, 21, 26, 34, 50}; 1001 F {6, 8, 19, 28, 38}, G {18, 25, 26, 42, 47}); Test je Seed 2554 Paare mit a, b ≠ 0 außerhalb F ∪ G (`build_splits.py`).
- **Primär:** Δ_pow der Rest-Änderung U = E_in(T) − c·E_in(0) der Zahl-Eingabezeilen in der Log-Basis (k = 1..55).
- **Lesarten (wie EXP-127):** Tor: zurückgehaltene Genauigkeit ≥ 0.5 am Ende in ≥ 3 von 4 Läufen, sonst „nicht auswertbar (lernt nicht)“. **„K2 hält (mul)“:** Δ_pow > 1 in beiden Seeds. **„bricht“:** |Δ_pow| ≤ 1 in beiden. Sonst **„unklar“**.
- **Beschreibend:** Top 5 der Änderung in Log- und in additiver Basis (tauchen 23/11/56 wieder auf?), Ablation C_in/C_both (Projektion in der Log-Basis), Δ_pow der Zeilen.
- **Deutung je Ausgang (vorab):** „K2 hält (mul)“ + „bricht“ bei Addition → *die Faktenauswahl steuert ein vortrainiertes Modell dort, wo seine Zahlmerkmale nicht passen* (Wiederverwendung, wo möglich) → Bestätigung mit frischen Splits planen. „bricht“ → *auch dort keine Steuerung der Eingabeeinbettung*; die Wiederverwendungs-Lesart allein erklärt EXP-127 dann nicht. „nicht auswertbar“ → Pythia lernt mul 113 in 4000 Schritten nicht; längeres Budget nur mit neuer Begründung.
- **Grenzen vorab:** 2 Seeds; die P1-Splits sind im Spielzeugmodell benutzt (für das LM neu, aber keine frischen Splits); F und G überlappen (P1-Konstruktion), anders als die LM1-Splits; Produkte mit 0 sind Trainingsfakten, aber nicht im Test.
- **Budget:** 4 GPU-Läufe à ≈ 36 min, gpu_gb 5, 2 Worker, stall_minutes 15 (P-021). Erst einreihen, wenn EXP-130 fertig ist (Speicher) und ein Smoke grün ist.

## Stand

- `ft_mul.py --selftest-mul` grün (≈ 17:50; Etiketten, Projektor idempotent mit Spur 4, Zeile 0 unberührt, Nyquist nur Kosinus, Log-Potenz erkennt eingepflanzte Frequenzen).
- `build_splits.py` gelaufen (≈ 17:50): Splits und Testmengen unter `splits/`.
- `analyze.py` mit synthetischen Daten getestet (`test_analyze_synthetic.py`: eingepflanzte Ziele → „K2 haelt (mul)“, Δ_pow ≈ 16, Top 5 = Ziele).
- **Codeprüfung (unabhängiger Agent, nur lesend, S61, vor jedem Lauf): keine Blocker.** Patches greifen (Modul-Globale zur Aufrufzeit); Log-Basis = P1-Konvention (vom Prüfer numerisch bestätigt: die Top 5 der Maskenpotenz aller vier Splits in der Log-Basis = ihre Ziele); Testmengen ohne 0 und ohne Überlappung. Übernommen: `--out-root` muss im Versuchsordner liegen (Run-IDs kennen die Aufgabe nicht), `--selftest` gesperrt (die Prüfung in `ft_pythia.py` ist nur für Addition; Tokenizer- und Verlustpfad deckt der Smoke). Als Grenze vermerkt: Kontrollmengen der Ablation werden aus 1..56 gezogen; 56 ist in der Log-Basis Nyquist (nur Kosinus), eine Kontrolle mit 56 entfernt 9 statt 10 Dimensionen (nur beschreibend; `ft_pythia.py` bleibt hash-gebunden). Der Skalar c der Rest-Änderung schließt Zeile 0 ein (vernachlässigbar).
- **Smoke (CPU, 2 Schritte, 100 Testaufgaben, 17:53–18:05): grün** (Log-Basis-Ausgaben, Ablation vollständig; vortrainiert 1.6 % Training / 1.0 % Test, Zufall ≈ 0.9 %; lief mit der Fassung vor den zwei Schutzprüfungen, die danach einzeln getestet wurden).
- **Eingereiht 18:06** als `inbox/44zzz_exp132_mul.jobs` (hinter EXP-130; der Dienst lässt nach Speicher zu). Auswertung mit `analyze.py`.

## Befehle

```
python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-132-pythia-mul/ft_mul.py --selftest-mul
python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-132-pythia-mul/ft_mul.py --seed 1000 --split-file lab/experiments/EXP-132-pythia-mul/splits/seed1000_F.npy --test-file lab/experiments/EXP-132-pythia-mul/splits/seed1000_test.npy --targets-file lab/experiments/EXP-132-pythia-mul/splits/seed1000.json --steps 4000 --out-root lab/experiments/EXP-132-pythia-mul/raw
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-132-pythia-mul/analyze.py
```

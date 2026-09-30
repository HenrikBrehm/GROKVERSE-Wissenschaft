---
id: EXP-132
status: abgeschlossen
datum: 2026-09-30
tags: [exp/abgeschlossen, befund/unklar, lab/lm, neu/kandidat]
verwandt: ["[[experiments/EXP-127-pretrained-lm/README|EXP-127]]", "[[experiments/EXP-130-pythia-functional-spectrum/README|EXP-130]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]"]
---
# EXP-132: Vortrainiertes Pythia-160M auf Multiplikation mod 113 nachtrainieren – steuert die Faktenauswahl dort? (Pilot, N60)

Zurück zu [[LAB]]. **Exploration (2 Seeds × F/G), keine Bestätigung.**

**Bezug:** N60 in [[NOVEL_DIRECTIONS]]; Geltungsgrenze von K2 beim Nachtrainieren ([[FINDINGS]], Exploration S61). [[experiments/EXP-127-pretrained-lm/README|EXP-127]] (Addition) ergab „bricht“, und die Änderung konzentrierte sich in allen Armen auf dieselben Frequenzen {2, 3, 11, 23, 56} (11/23 vortrainiert stark, 56 ≈ Parität; beschreibend). Frage hier: Setzt sich die Faktenauswahl durch, wenn die vortrainierten Merkmale zur Aufgabe nicht passen? Multiplikation mod 113 ist eine Addition in Log-Koordinaten; Dezimalmerkmale über a helfen dort nicht direkt.

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

## Zwischenstand (Sitzung 62, 30.09., 20:37 Berlin gemessen): Tor schon verfehlt → „nicht auswertbar (lernt nicht)“ steht fest

Dienst `44zzz_exp132_mul`, Läufe #0/#1 (Seed 1000 F/G, 19:54–20:36): Training 1.000 / 1.000, **zurückgehaltene Genauigkeit 0.067 (F) und 0.014 (G)** nach 4000 Schritten (Verlauf F: 0.035 bei 1000, 0.053 bei 2250, 0.065 bei 3250). Das Tor verlangt ≥ 0.5 in ≥ 3 von 4 Läufen; mit zwei Läufen darunter ist es unabhängig von Seed 1001 verfehlt → Vorab-Lesart **„nicht auswertbar (lernt nicht)“**. Die Läufe #2/#3 (Seed 1001) laufen wie registriert zu Ende (beschreibend; `analyze.py` erst danach, nächste Sitzung). Nicht abgebrochen, weil sie die Lesart nicht ändern, aber den Piloten vollständig machen.

**Beschreibend, vorläufig:** Pythia-160M memoriert die Trainingsfakten der Multiplikation mod 113 in 4000 Schritten vollständig, verallgemeinert aber kaum (Zufall ≈ 0.009) – anders als bei der Addition (EXP-127/130: Test 0.97–0.99 mit derselben Einstellung). Das passt zur Hypothese N60, dass die vortrainierten Zahlmerkmale bei der Multiplikation nicht passen; es zeigt aber nur, dass das Modell die Aufgabe in diesem Budget nicht lernt, nicht, welche Frequenzen es sonst wählen würde. Vorab vorgesehen (EXP-127-Muster): „nicht auswertbar“ → längeres Budget oder höhere lr in einem neuen Piloten. Nach der Rückschau (JOURNAL S62) wird die Pythia-Linie nach EXP-133 geschlossen; ein neuer mul-Pilot nur mit Begründung gegen die offenen Fragen in [[FINDINGS]].

## Ergebnis (Sitzung 63, 30.09., 21:30 Berlin gemessen): „nicht auswertbar (lernt nicht)“

`analyze.py` über den Wächter, 4/4 Läufe „ok“ (`summary.json`). **Vorab-Lesart: „nicht auswertbar (lernt nicht)“** – zurückgehaltene Genauigkeit am Ende 0.067 / 0.014 (Seed 1000 F/G) und 0.042 / 0.039 (Seed 1001), Tor ≥ 0.5 in ≥ 3/4 verfehlt (0/4); Trainingsgenauigkeit ≈ 1.00 in allen vier Läufen, Zufall ≈ 0.009.

**Nur beschreibend (Tor verfehlt, keine Lesart):** Δ_pow der Rest-Änderung der Eingabezeilen in der Log-Basis +0.84 / +0.66 (unter der Schwelle 1; bei Addition EXP-127 +0.13 / −0.17); Δ_pow der Zeilen selbst 0.25 / 0.20. Die Top 5 der Änderung in der Log-Basis sind in F und G desselben Seeds fast gleich (Seed 1001: {19, 1, 9, 8, 27} und {19, 9, 1, 27, 18}), also nicht die eigenen Ziele. Ablation beim Test ≈ Zufallsniveau ohne Aussage (C_in −0.02 … +0.02).

**Entscheidung:** Kein weiterer mul-Pilot (JOURNAL S62, Rückschau nach Zyklus 6: die Pythia-Linie schließt nach EXP-133). Für das Paper höchstens ein Halbsatz in Anhang K: *„on multiplication mod 113 the fine-tuned model only memorized (held-out ≤ 0.07 in 4 runs), so steering could not be assessed there“* ([[paper/PYTHIA_DEUTUNGEN]]). Kein Befund über Steuerung.

---
id: EXP-101
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-101 (Regel 20c): Steuert die Datenauswahl auch die Merkmale einer Recursive Feature Machine (RFM)? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2) · Regel 20c · Brücke zu Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316) · Code: `lab/external/rfm-grokking` (Mallinar et al., arXiv 2407.20199; GPL-3.0, Commit 73181df8, nicht im Repo)

**Stand:** Entwurf (Sitzung 43, 2026-09-28). Noch kein Code, keine Installation. Die Abhängigkeiten (jax, neural-tangents, wandb, scipy, einops) kommen erst **nach R10** in `.venv-gpu`, mit festgehaltenen Versionen (Regel 20f).

## Frage

Wird K2 (konstruierte Trainingssplits steuern die gelernten Frequenzen) auch in einem nicht-neuronalen Lerner sichtbar, der Grokking zeigt? Tomàs Bernal et al. zeigen für RFM, dass die Symmetrie der Trainingsmenge bestimmt, was gelernt wird. Unser Hebel ist ein anderer: eine Paarmaske ohne eingebaute Symmetrie mit vorgegebenen Frequenzen. Hält K2 in RFM, spricht das dafür, dass die Steuerung eine Eigenschaft der Daten ist und nicht des Transformers.

## Plan

- **Daten:** RFM baut die Eingaben wie wir (`operation_mod_p_data`: `cartesian_prod(x, y)`, flacher Index a·p + b, one-hot, 2p Dimensionen). Unsere Split-Dateien (flache Indizes) lassen sich deshalb direkt einspeisen: `data.make_data_splits` wird in einem eigenen Wrapper ersetzt (externer Code bleibt unverändert). Aufgabe add 113, Splits F/G wie P1 (Trainingsanteil 30 %) an 10 Seeds, gleiche Testmenge.
- **Modell:** Gauß-Kern-RFM wie im Original (`--kernel_type gaussian`, Bandbreite, `agop_power` 0.5, Iterationen wie in ihrer README/ihren Skripten; vorher an einem Zufallssplit reproduzieren, dass Grokking auftritt).
- **Messgröße:** Die AGOP-Matrix M (2p × 2p) wird in die a- und b-Blöcke zerlegt und je Block in die reelle DFT-Basis gedreht. Gemessen wird die Leistung je Frequenz auf der Diagonale bzw. im Frequenzblock. Δ_pow_RFM = log[P_F(T_F)/P_F(T_G)] + log[P_G(T_G)/P_G(T_F)] wie P1.
- **Lesarten (vor dem Lauf einfrieren):** „K2 in RFM“, wenn Δ_pow_RFM-KI > 0 über Seeds; „nicht“, wenn KI ⊂ [−0.5, 0.5]. Beschreibend: Testgenauigkeit, Iteration bis zur Generalisierung.
- **Aufwand:** Kern 3831 × 3831, wenige Iterationen; CPU reicht vermutlich. Laufzeit im Smoke messen.

## Offen

Wrapper `run_rfm.py` (nach der Installation), Nachbau eines Originalergebnisses als Gleichwertigkeitsprüfung, statische Prüfung, dann Pilot.

## Fassung 2 (Sitzung 44, 2026-09-28, ≈ 20:27 Berlin, Fenster zu): ohne Installation, Code steht (ungetestet)

**Entscheidung:** Keine Installation. Der Gauß-Kern-Pfad der Originalarbeit braucht nur torch, numpy und `scipy.linalg.sqrtm`; jax/neural-tangents betreffen nur den NTK-Kern, wandb nur das Logging, sklearn nur ihren Zufallssplit. `rfm_k2.py` ist eine eigene Umsetzung desselben Algorithmus (`--kernel_type gaussian --ridge 0 --agop_power 0.5`, Zentrierung wie im Original, M₀ = I, Bandbreite 2.5), mit zwei rein numerischen Änderungen: (1) Die AGOP nutzt die One-hot-Struktur (Summe über Zeilen mit a_i = v) statt des dichten n × c × d-Produkts (O(n·m·c) statt O(n·m·c·d)); (2) die PSD-Wurzel per `eigh` (negative Eigenwerte auf 0) statt `sqrtm` (globales Python hat kein scipy; für symmetrische PSD-Matrizen dieselbe Hauptwurzel). Der externe Code wird nur im Selbsttest importiert (mit einem `sqrtm`-Ersatz), nicht im Trainingspfad, und nicht committet (GPL-3.0). Damit entfällt Regel-20f-Aufwand und jedes Risiko für `.venv-gpu`. Läuft mit dem globalen Python (torch 2.13 CPU) über den Wächter.

**Deterministisch:** keine Init-Zufälligkeit; einzige Variationsquelle ist der Split. Deshalb sind Seeds = Split-Paare.

**Messgröße (vor jedem Lauf festgelegt, Docstring):** M ist 2p × 2p (One-hot von a, dann b). Je Diagonalblock P_B(k) = 2 Re(f_kᴴ B f_k), k = 1…56; P(k) = P_aa + P_bb (Gegenstück zur W_E-Gruppenleistung, da M nach der Neural-Feature-Ansatz-Beziehung die Rolle von WᵀW spielt). Δ_pow_RFM wie P1 (`confirm_p1.delta_pow`) an der letzten Iteration (30). Sekundär: ohne Blockdiagonale („offdiag“) und bei Iteration 5.

**Lesarten (Pilot = Exploration; Splits = P1 add 113, Seeds 1000–1009, Arme R/F/G; diese Splits hat noch kein RFM gesehen, der Transformer schon):**
- **Tor:** Der Zufallsarm R (gleiche Größe, 30 %) muss in ≥ 8/10 Seeds Testgenauigkeit ≥ 0.95 an Iteration 30 erreichen. Sonst „RFM grokt bei p = 113 / 30 % mit diesen Einstellungen nicht“ → keine K2-Lesart, so berichten. Einzige vorab erlaubte Ausweichregel: Steigt die R-Genauigkeit an Iteration 30 noch (letzte 5 Iterationen +0.05 oder mehr), einmal mit 60 Iterationen wiederholen (neue Ausgabedateien, `ITERS` im Namen).
- **positiv:** mittleres Δ_pow > 0, Bootstrap-95-%-KI > 0 und ≥ 8/10 Seeds positiv → „K2 auch in RFM (Pilot)“.
- **negativ:** KI ⊂ [−0.5, 0.5] → „keine Steuerung in RFM (Pilot)“.
- sonst **unklar**.
Eine Bestätigung würde die unbenutzten P1-Splits 1010–1049 nehmen (eigene Registrierung).

**Gleichwertigkeit mit dem Original:** `--selftest` vergleicht die schnelle AGOP mit einer dichten Nachschrift von `get_grads` und, wenn `lab/external/rfm-grokking` vorhanden ist, mit deren `gaussian_M_update` selbst (Toleranz 1e-8 relativ); dazu S·S = A, Spektrum an einem Kreisblock, Δ_pow-Referenz. `--reproduce` rechnet deren Standard (p 61, 50 % Zufallssplit, 30 Iterationen); erwartet laut Arbeit Testgenauigkeit nahe 1 nach ≈ 20 Iterationen. Gelingt das nicht: Blocker, keine Pilotläufe.

**Ablauf (ab 23:59, CPU, parallel zu R10; 4 Threads):**
```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --selftest
python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --reproduce
python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --run --seeds 1000-1009 --arms R,F,G
python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --analyze --seeds 1000-1009
```
Laufzeit geschätzt (nicht gemessen): ≈ 5 s je Iteration bei n = 3831, also ≈ 2–3 min je Lauf, 30 Läufe ≈ 1–1.5 h. Im Selbsttest/Reproduce messen und hier eintragen. Speicher: D ist m × c × d = 3831 × 113 × 226 float64 ≈ 0.8 GB, Spitze ≈ 3 GB.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** Die P1-Splits und ihre Transformer-Ergebnisse (K2) sind bekannt; die RFM-Einstellungen sind die Standardwerte der Originalarbeit und wurden nicht an unseren Daten gewählt. Keine RFM-Ergebnisse gesehen.

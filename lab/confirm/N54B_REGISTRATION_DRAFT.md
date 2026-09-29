---
id: N54B
status: entwurf
datum: 2026-09-29
tags: [lab/confirm, neu/kandidat]
---
# Registrierung N54b: Skaliert das Festlegungsfenster unter Minibatch-AdamW mit √(N/B)? (Sitzung 47)

Zurück: [[LAB]] · [[FINDINGS]] (Result 3 / L0: Festlegung unter Minibatch) · [[NOVEL_DIRECTIONS]] N54 · Piloten [[experiments/EXP-107-lockin-epochs/README|EXP-107]], [[experiments/EXP-108-lockin-batch-series/README|EXP-108]], [[experiments/EXP-109-lockin-lr-pilot/README|EXP-109]]

**Einordnung (Regel 20a):** Der Satz der Kernaussagen ist eingefroren. Diese Bestätigung gehört in einen Nebenabschnitt/Anhang des Papers (Festlegung unter Minibatch, Ergänzung zu L0 und Result 3). Sie zielt auf die offene Frage aus [[FINDINGS]], wie das Festlegungsfenster unter Minibatch-Training zählt.

## Frage und Hypothesen

Unter i.i.d.-Minibatch-AdamW (lr 1e-3, wd 1) lag der Halbwertspunkt der Festlegung t½ in EXP-108 bei ≈ 31 (Full-Batch), 62 (B 1024), 127 (B 256), 290 (B 64) Schritten; Exponent α von t½ ∝ (N/B)^α = 0.54 [0.52, 0.56] (8 Seeds, Full-Batch-Punkt fest).

- **H1 (Replikation, lr 1e-3):** Mittleres α liegt im Wurzel-Band [0.3, 0.7].
- **H2 (zweite Lernrate, lr 2e-3):** Mittleres α liegt im Wurzel-Band [0.3, 0.7].
- Familie {H1, H2}, Holm, α = 0.05. Je Hypothese: TOST-p = max(p(ᾱ > 0.3), p(ᾱ < 0.7)) aus einseitigen t-Tests über Seeds. **Bestätigt** = Holm-p < 0.05 **und** Bootstrap-95-%-KI ganz in [0.3, 0.7] **und** ≤ 2 zensierte Seeds je Batchgröße. Eine Hypothese mit < 8 gültigen Seeds ist „nicht auswertbar“ und geht mit p = 1 in Holm ein (konservativ; k bleibt 2).
- **Dagegen spräche:** KI außerhalb des Bands, v. a. Richtung 1 (Epochen-Uhr) oder 0 (Schritt-Uhr); ein Bruch zwischen den Lernraten (H1 bestätigt, H2 nicht) wäre ein Befund („Wurzel-Uhr nur bei einer Lernrate“) und kommt so ins Paper.

## Aufbau

- add 113, 30 % Daten (N ≈ 3831), L0/EXP-100-Konstruktion (EXP-053/P1-Paar F/G, ω = 0, kalibriertes ε, Ziele ohne die Stride-Frequenzen O), Zielziehung aus eigenem Strom SeedSequence([100300, seed, 0]); Testmenge, Phasen, Schlüssel aus den EXP-053-Strömen wie P1/L0.
- **Seeds 3900–3909** (n = 10; Dateisuche 29.09., Sitzung 47: weder Dateinamen noch Registrierungen mit 39xx-Seeds). 3910–3999 bleiben reserviert.
- Je Seed, Lernrate (1e-3, 2e-3) und Batchgröße B ∈ {1024, 256, 64}: reine Läufe F und G; Wechsel F → G und G → F bei jedem t aus dem Raster; jeder Lauf 5000 Schritte (`--stop-after-gen 5000`), i.i.d.-Reihenfolge, AdamW (β 0.9/0.98, wd 1), GPU, 1 Thread. **840 Läufe.** **Kein Full-Batch-Arm** (Entscheidung Sitzung 47 nach der Prüfung, vor jedem Ergebnis des Blocks): Full-Batch-Läufe kosten ≈ 4× so viel GPU-Zeit, und das Sign-Drift-Modell (i) sagt eine Sättigung zum Full-Batch hin voraus (Drift ∝ erf(√(B/2)·μ/σ)), die α verzerren würde; α über die drei Minibatch-Größen (N/B 3.7–60, Faktor 16) ist der sauberere Test. EXP-108 ohne Full-Batch-Punkt: α = 0.556 [0.513, 0.595].
- Raster (Schritte): B 1024: 15, 30, 50, 75, 100, 150; B 256: 30, 60, 100, 150, 200, 300; B 64: 75, 150, 225, 300, 450, 700. *(Nach EXP-109 bestätigt oder angepasst; siehe unten.)*
- Messgröße wie EXP-107/108: π(t) = Mittel über beide Richtungen der normierten Lage von log(P_F/P_G) (W_E-Gruppenleistung bei Schritt 5000) zwischen den reinen Läufen derselben Lernrate und Batchgröße. t½ = erster Aufwärtsdurchgang durch 0.5, lineare Interpolation über (0, 0) und das Raster; kein Durchgang → t½ = t_max, zensiert (wie EXP-108). α je Seed und Lernrate = Kleinste-Quadrate-Steigung von log t½ gegen log(N/B) über die drei Batchgrößen (N = Größe des Splits, 3831). Zensierte t½ gehen mit t_max ein und verzerren α nach unten; darum höchstens 2 je Batchgröße.
- **Gültigkeit:** Jeder technische Fehler → Block „nicht auswertbar“ (reine Infrastrukturfehler dürfen vor `--analyze` mit identischer Jobzeile wiederholt werden). Ein Seed ist für eine Lernrate ungültig (nicht technisch, wird berichtet), wenn bei einer Batchgröße L_F − L_G < 0.5.
- **Sekundär, ohne Urteil:** t½ je B und Lernrate; Verhältnis t½(2e-3)/t½(1e-3) je B (geometrisches Mittel, KI; Modell (i) sagt ≈ 0.5, Modell (ii) ≈ 1, siehe [[experiments/EXP-109-lockin-lr-pilot/README|EXP-109]]); Vergleich mit den EXP-108-Mitteln (lr 1e-3: 62/127/290).

## Power

EXP-108: α je Seed 0.51–0.60, SD 0.032 mit festem Full-Batch-Punkt; ohne ihn 0.45–0.65 (KI 0.513–0.595, SD ≈ 0.06). Annahme SD 0.08: bei ᾱ = 0.54 TOST-t ≈ 6 → Power ≈ 1; bei ᾱ = 0.65 nur ≈ 50 %. Die Power ist also hoch, wenn α wie im Piloten in der Bandmitte liegt, gering nahe am Rand. 10 Seeds nach Regel 15b.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- EXP-100 (Full-Batch-Referenz, B 256/64 bei 30 000 Schritten), EXP-107 (B 256), EXP-108 (B 1024/64), alle lr 1e-3, Seeds 3700–3707 → Hypothese, Band [0.3, 0.7], Raster für lr 1e-3, Laufbudget 5000 Schritte, Messgröße.
- EXP-109 (lr 2e-3, Seeds 3700–3701) → Wahl der zweiten Lernrate bestätigt/verworfen, Raster für lr 2e-3 (siehe Nachtrag).
- Erste Literatursuche N54 (Sitzung 46): √-Skalierung als Rausch-Skalierung bekannt (Malladi et al. 2022), Messung an einer frühen Merkmalsfestlegung nicht gefunden.

## Befehle

```
python lab/tools/confirm_n54b.py --selftest                       # über den Wächter
python lab/tools/confirm_n54b.py --hash-code                      # Manifest-Hashes
python lab/tools/confirm_n54b.py --splits lab/confirm/N54B_manifest.json
python lab/tools/confirm_n54b.py --jobs lab/confirm/N54B_manifest.json > lab/confirm/N54B_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/N54B_jobs.txt --workers 10 --min-minutes 3
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_n54b.py --analyze lab/confirm/N54B_manifest.json
```

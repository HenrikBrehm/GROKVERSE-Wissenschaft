---
id: EXP-143
status: vorbereitet
datum: 2026-10-01
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-140-random-at-edge/README|EXP-140]]", "[[experiments/EXP-142-shuffled-weights/README|EXP-142]]", "[[experiments/EXP-141-alpha-test/README|EXP-141]]", "[[confirm/R15_REGISTRATION|R15]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]"]
---
# EXP-143: Menge gegen Reihenfolge im LeDoux-Regime (p = 9973, 0.30 % der Paare, Batch 256) – Pilot

Zurück zu [[LAB]]. **Exploration (ein Seed je Arm), keine Bestätigung.** [[BACKLOG]] Punkt 7; [[NOVEL_DIRECTIONS]] N64.

**Bezug zu FINDINGS:** K2 und L0 gegen den LeDoux-Einwand (Regel 20b): LeDoux 2026 (arXiv 2603.25047) findet bei p = 9973 mit 300 000 Paaren und Batch 256 dieselbe Frequenz (F = 101) „regardless of … training set composition“, aber nur für *zufällige* Teilmengen und unter einer Stride-Reihenfolge. Unsere Belege für K2 liegen bei p ≤ 613 und ≥ 1.5 % der Paare. [[experiments/EXP-140-random-at-edge/README|EXP-140]] und [[experiments/EXP-142-shuffled-weights/README|EXP-142]] (Piloten) zeigen an der Datengrenze bei p = 401: konstruierte Menge generalisiert, gleich große Zufallsmenge und gleich ungleich gewichtete Menge ohne Frequenzmuster nicht. LeDoux' 300 000 Paare bei p = 9973 sind N/p ≈ 30, genau unsere Grenzgegend. Begründung Regel 15b: der direkteste Test des wichtigsten Gutachter-Einwands, bisher nur an einem technischen Hindernis gescheitert.

## Werkzeug (Sitzung 70)

`freq_ban.py` ist hash-gebunden und baut alle p² Paare (≈ 10⁸) und wertet in einem Stück aus (≈ 12 GB Logits). Neu: [`lab/tools/freq_ban_large.py`](../../tools/freq_ban_large.py) lädt den Trainer unverändert und ersetzt nur Datentabelle (Paare werden aus dem Index berechnet), Auswertung (in Stücken; gleiche Formel), optional Auswertungs- und Spektrumstakt. Gleichwertigkeit bei p = 113 auf der CPU: `lab/tools/test_freq_ban_large.py` (Vollbatch und Batch 64 mit Stride; Gewichte bitgleich, Genauigkeit ≤ 1e-6, Verlust ≤ 1e-6 relativ). Splits: `make_splits.py` (EXP-043-Konstruktion mit denselben Zufallszügen, bei p 113/307 bitgleich zum Original geprüft; die gemeinsame Test-Stichprobe von 20 000 Paaren wird zuerst gezogen und aus jeder Trainingsmenge ausgeschlossen).

## Vorab (Sitzung 70, 2026-10-01, vor jedem p-9973-Trainingslauf)

- **Aufbau:** add p = 9973, N = 300 000 Paare (0.30 %), Batch 256, AdamW mit unseren Voreinstellungen (lr 1e-3, wd 1.0; LeDoux: 2-Schicht-Transformer d 256, wd 0.1, Cosine – wir übernehmen bewusst nur das Datenregime, nicht sein Modell), unser 1-Schicht-Modell, GPU über den Dienst. Seed 14300. Test = gemeinsame Stichprobe von 20 000 Paaren außerhalb aller Trainingsmengen.
- **Arme:** R-iid (Zufallsmenge, i.i.d.-Reihenfolge), F-iid (konstruierte Menge ε = 2, 5 Zielfrequenzen), R-stride (LeDoux' Positivkontrolle), F-stride (Konfliktarm: Menge bevorzugt die F-Ziele, Reihenfolge die Stride-Frequenz).
- **Stride-Frequenzen (vorab gerechnet):** s = ⌊√9973⌋ = 99. (a) k = 101: Periode p/101 ≈ 98.7 ≈ s in a, also nahezu eine Funktion von a mod 99 (der Sortierschlüssel); passt zu LeDoux' empirischem F = 101. (b) k = 1914: 1914 · 99 ≡ ±1 (mod 9973), das kleinste Residuum überhaupt, d. h. nahezu konstant entlang eines Stride-Laufs a, a + 99, a + 198, … (Erste, falsche Herleitung „101 · 99 ist das kleinste Residuum“ vor jedem Lauf korrigiert: 101 · 99 ≡ 26.) Lesebereiche „Stride-Frequenz“ = {100, 101, 102} ∪ {1913, 1914, 1915}; berichtet werden beide getrennt.
- **Messgrößen:** gen-Schritt (Test ≥ Primärschwelle), Test-Genauigkeit am Ende, W_E-Spektrum (Top-5; Anteil der F-Ziele; Leistung bei 100–102 relativ zum Median).
- **Lesarten (je Frage, vorab):**
  - Q1 (Inhalt statt Reihenfolge, i.i.d.): F-iid generalisiert im Budget, R-iid nicht → „Inhalt ersetzt Reihenfolge auch im LeDoux-Regime (Pilot)“. Beide nicht → „im Budget keine Aussage“. Beide ja → „mit unserem Modell generalisiert auch Zufall + i.i.d.; LeDoux' Regime nicht reproduziert“. Nur R → „unklar“.
  - Q2 (Positivkontrolle): R-stride generalisiert und hat eine Stride-Frequenz (101 ± 1 oder 1914 ± 1) in den Top-5 → „LeDoux-Effekt mit unserem Modell reproduziert“; sonst so berichten (dann ist Q3 nur eingeschränkt lesbar).
  - Q3 (Konflikt, F-stride, am Ende gemessen; gen-Zustand mit berichten): ≥ 3 F-Ziele in den Top-5 und keine Stride-Frequenz → „Menge gewinnt“; eine Stride-Frequenz in den Top-5 und ≤ 1 F-Ziel → „Reihenfolge gewinnt“; Stride-Frequenz und ≥ 2 F-Ziele → „beide“; sonst „unklar“.
- **Was dagegen spräche:** jeweils die Gegenausgänge oben; ein Lauf, der im Budget nicht generalisiert, beweist nicht, dass er es nie täte (§5).
- **Budget:** wird nach dem GPU-Smoke (Tempo, Speicher) festgelegt und hier als Nachtrag *vor* dem Einreichen eingetragen; Obergrenze ≈ 10 GPU-Stunden für alle 4 Arme. Abbruch nur bei Divergenz (NaN) oder Hänger.
- **Grenzen:** ein Seed je Arm, anderes Modell als LeDoux, ein Budget. Ergebnisse sind Pilot; ein Bestätigungsblock bräuchte frische Seeds und ein eingefrorenes Manifest.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** LeDoux' Zahlen (Volltext, S43/44), EXP-139/140/141/142 (Datengrenze bei N/p ≈ 30 für p ≤ 503), die Maske der R-Menge mit 298 380 Paaren (erster Bau, verworfen wegen falscher Paarzahl; Masken-Top-5 [95, 234, 1013, 3002, 4121], keine Zielanreicherung).

## Nachtrag Budget (Sitzung 70, 14:07 Berlin (gemessen), nach dem GPU-Smoke, vor dem Einreichen)

Smoke (R-iid, 600 Schritte, Auswertung alle 200, allein neben einem 7-GB-Dienstlauf): 0.0253 s/Schritt einschließlich Auswertungen und Spektren, 2.1 GB Grafikspeicher, ≈ 70 s Einrichtung; Train- und Testgenauigkeit auf Zufallsniveau (≈ 1e-4), Verlust ≈ 9.21 ≈ ln 9973. Festgelegt: **250 000 Schritte je Arm** (≈ 213 Epochen à 1172 Schritte; LeDoux brauchte mit Stride 487 Epochen mit seinem Modell), Stopp 5000 Schritte nach gen, Auswertung alle 1000 Schritte (gen-Auflösung 1000), Spektrum alle 5000. 4 Arme parallel beim Dienst (`gpu_gb` 2.5, `job_minutes` 330), hinter R15 p 401. Erwartet 2–4 h je Arm unter Last. Ein Arm, der in 250 000 Schritten nicht generalisiert, heißt nur „nicht im Budget“.

## Erwartung vor den Ergebnissen (Sitzung 70, 14:12 Berlin; grobe Hochrechnung, keine Lesart)

Aus den Iso-Zeit-Paarzahlen von EXP-139/141 (Vollbatch, T = 5000 Schritte): N_T ≈ 14 214 · (9973/401)^1.2 ≈ 670 000 bzw. unter N ∝ p ln p ≈ 5.84 · p ln p ≈ 536 000. LeDoux' 300 000 Paare liegen also bei etwa der Hälfte davon (N/(p ln p) ≈ 3.3; bei p ≤ 401 generalisierte keine Zufallszelle unter ≈ 4.5 in 30 000 Schritten). Erwartet daher: R-iid nicht im Budget; F-iid offen (bei p 401 half die Konstruktion an der Grenze, hier liegt N weiter darunter); Stride-Arme ohne Vorhersage, weil unser Modell und unsere Regularisierung (wd 1.0) von LeDoux abweichen und Minibatch-Schritte nicht Vollbatch-Schritten entsprechen. Diese Hochrechnung überspannt einen Faktor 25 in p und ist nur eine Einordnungshilfe.

## Maskenvergleich vor dem Start (Sitzung 70, 14:21 Berlin; erster Ordnung, kein Trainingsergebnis)

Zielleistung der Maske / Median: p 9973 F 2.05 (R 1.00) gegen p 401/14 000 F 2.33/2.28 und p 503/18 100 F 2.28/2.30 (EXP-139/141, die generalisierten). Standardisiert (Mittel der Ziele minus Mittel der übrigen, durch deren Streuung): 103 bei p 9973 gegen 26–29 bei p 401/503 – der Hintergrund ist bei großem p viel glatter (größter Nicht-Zielwert 1.04 × Median). Die Stride-Frequenzen 101 und 1914 sind in beiden Mengen neutral (0.99–1.01 × Median), die Menge bevorzugt sie also nicht; ein Stride-Signal im Konfliktarm käme allein aus der Reihenfolge. ε = 2 bleibt.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/tools/test_freq_ban_large.py
python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/make_splits.py --arms R,F --seeds 14300 --mask
python lab/experiments/EXP-143-ledoux-regime/make_jobs.py > lab/queue/staging/52a8_exp143_ledoux.jobs
```

## Ergebnis

Offen.

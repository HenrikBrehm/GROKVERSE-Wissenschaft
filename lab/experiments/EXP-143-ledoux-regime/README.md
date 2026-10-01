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
- **Stride-Frequenzen (vorab gerechnet; ersetzt durch Nachtrag d):** s = ⌊√9973⌋ = 99. (a) k = 101: Periode p/101 ≈ 98.7 ≈ s in a, also nahezu eine Funktion von a mod 99 (der Sortierschlüssel); passt zu LeDoux' empirischem F = 101. (b) k = 1914: 1914 · 99 ≡ ±1 (mod 9973), das kleinste Residuum überhaupt, d. h. nahezu konstant entlang eines Stride-Laufs a, a + 99, a + 198, … (Erste, falsche Herleitung „101 · 99 ist das kleinste Residuum“ vor jedem Lauf korrigiert: 101 · 99 ≡ 26.) Lesebereiche „Stride-Frequenz“ = {100, 101, 102} ∪ {1913, 1914, 1915}; berichtet werden beide getrennt.
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

## Erwartung vor den Ergebnissen (Sitzung 70, ≈ 14:09 Berlin (nicht gemessen, zwischen 14:07 und 14:12); grobe Hochrechnung, keine Lesart)

Aus den Iso-Zeit-Paarzahlen von EXP-139/141 (Vollbatch, T = 5000 Schritte): N_T ≈ 14 214 · (9973/401)^1.2 ≈ 670 000 bzw. unter N ∝ p ln p ≈ 5.84 · p ln p ≈ 536 000. LeDoux' 300 000 Paare liegen also bei etwa der Hälfte davon (N/(p ln p) ≈ 3.3; bei p ≤ 401 generalisierte keine Zufallszelle unter ≈ 4.5 in 30 000 Schritten). Erwartet daher: R-iid nicht im Budget; F-iid offen (bei p 401 half die Konstruktion an der Grenze, hier liegt N weiter darunter); Stride-Arme ohne Vorhersage, weil unser Modell und unsere Regularisierung (wd 1.0) von LeDoux abweichen und Minibatch-Schritte nicht Vollbatch-Schritten entsprechen. Diese Hochrechnung überspannt einen Faktor 25 in p und ist nur eine Einordnungshilfe.

## Maskenvergleich vor dem Start (Sitzung 70, 14:17 Berlin (gemessen 14:18 danach); erster Ordnung, kein Trainingsergebnis)

Zielleistung der Maske / Median: p 9973 F 2.05 (R 1.00) gegen p 401/14 000 F 2.33/2.28 und p 503/18 100 F 2.28/2.30 (EXP-139/141, die generalisierten). Standardisiert (Mittel der Ziele minus Mittel der übrigen, durch deren Streuung): 103 bei p 9973 gegen 26–29 bei p 401/503 – der Hintergrund ist bei großem p viel glatter (größter Nicht-Zielwert 1.04 × Median). Die Stride-Frequenzen 101 und 1914 sind in beiden Mengen neutral (0.99–1.01 × Median), die Menge bevorzugt sie also nicht; ein Stride-Signal im Konfliktarm käme allein aus der Reihenfolge. ε = 2 bleibt.

## Nachtrag c (Sitzung 70, 14:20 Berlin (gemessen), vor jedem Ergebnis eines p-9973-Laufs): wd 0.1 als primärer Satz

**Anlass (bereits gesehene eigene Daten, nicht EXP-143):** In L0/EXP-100/EXP-106 (p 113, 30 %) generalisiert unser Modell unter Minibatch mit wd 1.0 umso schlechter, je kleiner B relativ zur Trainingsmenge ist: Vollbatch Median 875 Schritte (59/64), B 256 1 250 (79/80), B 64 5 150 (40/47), **B 16 0/9**; mit wd 0.1 lernt B 16 (3/3, Median 8 750). Bei p 9973 ist B 256 nur 0.085 % der 300 000 Paare (B 16 bei p 113: 0.42 %). Mit wd 1.0 drohen also alle vier Arme aus einem Grund zu scheitern, der mit Menge gegen Reihenfolge nichts zu tun hat. LeDoux verwendet wd 0.1.
**Änderung:** Primär sind jetzt die vier Arme mit `--weight-decay 0.1` (Jobdatei `52a7z_exp143_wd01`, nach R15, vor dem wd-1.0-Satz); die Lesarten Q1–Q3 gelten für diesen Satz. Der bereits eingereihte wd-1.0-Satz (`52a8_exp143_ledoux`, Voreinstellung) läuft als **Nebenarm** und wird nur beschreibend berichtet (der Dienst lädt Jobzeilen nicht neu; ihn nicht zu rechnen wäre nur über eine Ablehnung der Datei gegangen, und er beantwortet nebenbei, ob wd 1.0 in diesem Regime überhaupt lernt). Längere Zeitskala bei wd 0.1 (Grokking-Zeit ∝ 1/(lr·wd)) ist bewusst in Kauf genommen; das Budget bleibt 250 000 Schritte. `analyze.py` trennt nach wd.

## Nachtrag d (Sitzung 70, 14:31 Berlin (gemessen), vor jedem Ergebnis): unabhängige Prüfung übernommen

Adversariale Prüfung (Claude-Agent, nur lesend, eigene Prüfskripte unter C:/tmp/s70review) von Wrapper und Design. Übernommen:
- **H1 Budget:** 250 000 Schritte ≈ 213 Epochen < LeDoux' 487 Epochen (≈ 571 000 Schritte) für Stride. Zusätzlich die beiden **Stride-Arme mit wd 0.1 und 600 000 Schritten** (`52a7zz_exp143_stride600k`, eigener Ausgabeordner `raw_long`, weil Run-IDs die Schrittzahl nicht enthalten; job_minutes 900). **Q2 und Q3 werden an diesen langen Armen gelesen**; die 250 000-Stride-Arme sind Zwischenstand. Generalisiert R-stride nicht, heißt Q2 „nicht im Budget“, nicht „nicht reproduziert“.
- **H2 Zeitgrenze:** job_minutes in beiden eingereihten Kopfzeilen 330 → 600 (vor dem Start; Kopfzeilen liest der Dienst neu). Abgebrochene Läufe werden nicht wiederholt.
- **H3 Stride-Frequenz:** Die Bänder {100–102} ∪ {1913–1915} waren schlecht definiert (1913/1915 haben Residuen ≈ ±100). Der Prüfer fand an der tatsächlichen Stride-Ordnung des Trainers: innerhalb eines Stapels führt k = 403 (99 · 403 ≡ 5), über 120-Stapel-Fenster k = 101; k = 1914 nur Rang 152–182. Neu und vorab: **Stride-Familie = {k : |99 k mod 9973| ≤ 26}** (26 Frequenzen: 101, 302, 403, 705, 806, …, 1914, …; Schranke = Residuum von LeDoux' F = 101); berichtet werden k = 101 einzeln, „Familie in den Top-5“ und der Leistungsanteil der Familie gegen den Gleichverteilungsanteil 26/4986 und gegen die i.i.d.-Arme. Die F-Ziele liegen nicht in der Familie (Stride-Kohärenz-Ränge 749–2621), R- und F-Menge sehen unter Stride gleich aus → keine Vermengung von Menge und Reihenfolge.
- **M1:** Q3 gilt nur, wenn der F-stride-Arm generalisiert; sonst nur beschreibend (ein auswendig lernendes W_E kann die Ziele allein aus der Maske tragen).
- **M3:** abgebrochene/divergierte Arme werden als „teilweise“ ausgewiesen statt weggelassen. **L4:** Q1 „beide ja“ heißt jetzt „mit unserem Modell generalisiert auch Zufall + i.i.d. (anders als bei LeDoux' Modell)“.
- **Nicht behoben (M2):** freq_ban.py legt vor dem Ersetzen durch die Test-Stichprobe noch ein p²-Indexfeld an (≈ 3.6 GB RAM-Spitze, ≈ 74 s je Start; Trainer hash-gebunden). Der Dienst prüft freien RAM vor jedem Start; Auslagerung möglich, kein Absturz erwartet. L1–L3 (Startwettlauf am Marker, wrapper.json nur bei fertigen Läufen, GPU-Pfad nur per Smoke geprüft) als Risiko vermerkt.

## Nachtrag e (Sitzung 70, 14:33 Berlin (gemessen), vor dem Lauf): frühe Prägung auf der CPU (Exploration, nicht Teil von Q1–Q3)

- **Frage:** Prägt im LeDoux-Regime (wd 0.1, Batch 256) schon der Anfang des Trainings W_E – die Menge ihre Ziele, die Stride-Reihenfolge ihre Familie –, wie bei p 401 im Vollbatch (Sitzung 69: Prägung ab Schritt 50–250)?
- **Aufbau:** dieselben 4 Arme (F/R × iid/stride), Seed 14300, wd 0.1, **CPU** (`--device cpu --threads 4`), 3000 Schritte (≈ 2.6 Epochen), Spektren alle 250 Schritte, Auswertung alle 1500; Ausgabeordner `raw_cpu_early` (eigener Marker). Nicht mit den GPU-Läufen vermischt (anderes Gerät, Regel 16d).
- **Änderung vor dem Lauf (14:36, nach dem Zeitlauf):** Zeitlauf F-iid 250 Schritte (`cpu_timing`, 80.8 s, T/med 0.97 = Init, noch keine Prägung nach 0.2 Epochen); daher `--threads 3`, zwei Arme parallel, Auswertung nur bei 0 und 3000 (`--eval-every 3000`); Rest unverändert.
- **Messgrößen / Lesart (vorab):** bei Schritt 3000 (und Verlauf): Zielverhältnis T/med (Median der Zielleistungen / Median aller) in F gegen R; Familienanteil in stride gegen iid. „Menge prägt früh“, wenn T/med(F) > max(T/med(R-Arme)) + 0.2 in beiden F-Armen; „Reihenfolge prägt früh“, wenn der Familienanteil in beiden stride-Armen > 1.2 × dem größeren der beiden iid-Arme; sonst „nicht in 3000 Schritten“. Ein Seed, beschreibend.

## Nachtrag f (Sitzung 70, 14:56 Berlin (gemessen), vor den Läufen): Wiederholung der frühen Prägung mit Seeds 14301, 14302 (CPU, Exploration)

Gleicher Aufbau wie Nachtrag e (4 Arme, wd 0.1, 3000 Schritte, CPU, 3 Threads, `raw_cpu_early`), neue Splits per `make_splits.py --seeds 14301,14302` (gleiche Test-Stichprobe ausgeschlossen). Lesart je Seed: (i) „Menge prägt“ wie in Nachtrag e (T/med beider F-Arme > größter R-Arm + 0.2); (ii) **neu, nach Nachtrag e explizit festgelegt:** „Stride prägt k = 101“, wenn k = 101 in beiden Stride-Armen in den Top-5 steht und in keinem i.i.d.-Arm. Ergebnis über 3 Seeds wird berichtet als Anzahl Seeds mit (i) bzw. (ii). Diese Seeds gelten danach als gesehen (keine Bestätigungs-Seeds).

## Befehle

```
python lab/tools/guarded_run.py -- python lab/tools/test_freq_ban_large.py
python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/make_splits.py --arms R,F --seeds 14300 --mask
python lab/experiments/EXP-143-ledoux-regime/make_jobs.py > lab/queue/staging/52a8_exp143_ledoux.jobs
python lab/experiments/EXP-143-ledoux-regime/make_jobs.py --wd 0.1 > lab/queue/staging/52a7z_exp143_wd01.jobs
python lab/experiments/EXP-143-ledoux-regime/make_jobs.py --wd 0.1 --steps 600000 --orders stride --raw raw_long > lab/queue/staging/52a7zz_exp143_stride600k.jobs
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/analyze.py [--root lab/experiments/EXP-143-ledoux-regime/raw_long] [--traj]
```

Split-Dateien (nicht in git, mit `make_splits.py` deterministisch nachbaubar), SHA-256:

```
c84ddbdd0069c0996c866c0b78400c590726edbf7a30814a7f482535f7a78ed4 *split_add9973_n300000_seed14300_F.npy
bee06c667831d122cee63ba72e40b497bfa7acf9c95f7aafad657c825c789039 *split_add9973_n300000_seed14300_R.npy
20dd43656d4d733f9cf46944bf16e6d849149914a58fc06c1b1875f9ade38284 *test_add9973_n20000.npy
```

## Ergebnis Nachtrag e (Sitzung 70, 14:54 Berlin (gemessen); CPU, 1 Seed, 3000 Schritte ≈ 2.6 Epochen, Exploration)

Kein Arm generalisiert in 3000 Schritten (erwartet; Test 1e-4). W_E-Spektrum bei Schritt 3000 (Top-5 nach k sortiert, nicht nach Leistung):

| Arm | Top-5 | T/med (Ziele) | k = 101 (Rang; Leistung/Median) | Familienanteil (Gleichvert. 0.0052) |
|---|---|---|---|---|
| F-iid | **1100, 1296, 1691, 2142, 2511** (= alle 5 Ziele) | **1.66** | 3605; 0.94 | 0.0052 |
| F-stride | **101**, 151, 1100, 1296, 1691 | **1.36** | **1**; 2.00 | 0.0056 |
| R-iid | 1347, 1369, 2151, 2294, 3790 | 0.98 | 732; 1.11 | 0.0052 |
| R-stride | **101**, 151, 835, 2525, 3432 | 0.93 | **1**; 2.76 | 0.0055 |

- **Lesart „Menge prägt früh“: erfüllt** (T/med F 1.66 und 1.36 > 0.98 + 0.2). Die Ziele erscheinen nach ≈ 2–2.5 Epochen (F-iid: T/med 1.00 bei 1000, 1.26 bei 2000, 1.66 bei 3000); nach 250 Schritten (0.2 Epochen) noch nichts – unter Minibatch zählt die Prägung in Epochen, nicht in Schritten (im Vollbatch bei p 401 ab Schritt 50–250, Sitzung 69).
- **Lesart „Reihenfolge prägt früh“: nach dem vorab festgelegten Kriterium nicht erfüllt** (Familienanteil stride 0.0055/0.0056 < 1.2 × 0.0052). **Beschreibend, post hoc:** k = 101 – LeDoux' F = 101 – steht in beiden Stride-Armen auf Rang 1 (R-stride schon bei Schritt 500 auf Rang 3, bei 1000 auf Rang 1), in den i.i.d.-Armen nicht (Rang 732/3605). Das Familienmaß über 26 Frequenzen verdünnt dieses Einzelsignal; die übrigen Familienmitglieder wachsen kaum. Das Kriterium war damit schlecht gewählt; es wird nicht nachträglich ersetzt, die GPU-Lesarten Q2/Q3 („Familie in den Top-5“, k = 101 gehört dazu) bleiben unverändert.
- **Konflikt (F-stride), beschreibend:** beide prägen nebeneinander – 101 auf Rang 1 und 3 der 5 Ziele in den Top-5; die Zielprägung ist schwächer als ohne Stride (T/med 1.36 gegen 1.66).
- k = 151 steht schon bei der Initialisierung in den Top-5 (Init-Eigenheit, in allen Armen).
- **Grenzen:** 1 Seed, CPU, keine Generalisierung, nur Repräsentationsenergie (keine Ablation), 3000 Schritte. Ob die frühe Prägung die spätere Lösung bestimmt, beantworten erst die GPU-Läufe.
- **Unabhängige Nachrechnung (14:55, Claude-Agent, eigener numpy-Code, nur lesend):** alle Zahlen reproduziert. Placebo (10 000 zufällige 5er-Mengen ohne Ziele, Schritt 3000): beide F-Arme p < 1e-4 (Placebo-Maximum T/med ≈ 1.22), R-Arme p 0.62 / 0.92; Schritt 2000: F-iid p < 3e-4, F-stride p = 3e-4; Schritte 500/1000 nicht signifikant (p 0.2–0.77). k = 101: 2.00 / 2.76 × Median liegt über jedem Wert der i.i.d.-Arme (deren Maximum über alle k ≈ 1.45, 99.9-%-Quantil 1.34–1.47). **Übernommene Korrekturen:** (1) Der Stride-Effekt ist **eine einzelne Frequenz** (k = 101, genau am Rand der Familie: 99 · 101 ≡ 26), keine Anreicherung der Familie (ohne 101 Familienanteil 0.0050–0.0052; nächstbeste Familienränge 16/20 bzw. 230) – eine schwache frühe Prägung, keine Fourier-Lösung. (2) Die Mengenprägung ist ab ≈ 1.7 Epochen nachweisbar; „Top-5 = Ziele“ gilt nur für F-iid bei 2.56 Epochen, in F-stride ist sie schwächer (2511 nur Rang 8). k = 151 ist schon bei der Initialisierung oben (1.39 × bei Schritt 0), eine Init-Eigenheit.

## Ergebnis Nachtrag f (Sitzung 71, 15:32 Berlin (gemessen); CPU, Seeds 14301/14302 neu, 3000 Schritte, Exploration)

Schritt 3000, T/med = Median der Zielleistungen / Median aller k; k = 101 als Leistung/Median (Rang):

| Seed | F-iid | F-stride | R-iid | R-stride | k = 101 F-stride / R-stride | (i) | (ii) |
|---|---|---|---|---|---|---|---|
| 14300 (Nachtrag e) | 1.66 (5/5 Ziele in Top-5) | 1.36 (3/5) | 0.98 | 0.93 | 2.00 (1) / 2.76 (1) | ja | ja |
| 14301 | 1.80 (5/5) | 1.54 (3/5) | 1.08 | 0.99 | 2.10 (1) / 2.25 (1) | ja | ja |
| 14302 | 1.54 (5/5) | 1.24 (2/5) | 0.92 | 0.96 | 3.17 (1) / 2.68 (1) | ja | ja |

- **(i) „Menge prägt früh“: 3/3 Seeds; (ii) „Stride prägt k = 101“: 3/3 Seeds** (k = 101 in den i.i.d.-Armen Rang 732–3605). Die Seeds 14300–14302 gelten damit als gesehen.
- In jedem Seed ist die Zielprägung unter Stride schwächer als unter i.i.d. (T/med 1.24–1.54 gegen 1.54–1.80); Seed 14302 F-stride hat k = 202 in den Top-5.
- **Oberwellen (Exploration, post hoc an gespeicherten Spektren; Vorab-Lesart im [[JOURNAL]] S71 Zyklus 1, vor dem Rechnen festgelegt; das Skript lief einmal als Probe auf 4 der 6 Stride-Arme, bevor Seed 14302 fertig war):** Ein Profil g(a mod 99) des Sortierschlüssels hat Leistung nur bei k ≈ m · p/99. Mittel der 6 Stride-Arme, z gegen alle k: 101 +29.1; 201 +3.23; 202 +2.61; **302 +3.08; 403 +2.42**; 504 +1.63 (Ränge 1, 3, 18, 5, 32, 194 von 4986). In den 6 i.i.d.-Armen alle |z| < 1.2. **Vorab-Lesart: „unklar“** (403 verfehlt z > 3). Beschreibend sind alle fünf Oberwellen im Stride-Mittel erhöht und in i.i.d. nicht, was zu einem nicht-sinusförmigen Profil des Sortierschlüssels passt (eine Spur der Epochenposition, keine einzelne Fourier-Frequenz); geprüft ist das nicht.
- **Grenzen:** CPU, 3000 Schritte, keine Generalisierung, nur Repräsentationsenergie. Über die Endlösung entscheiden die GPU-Läufe (Q1–Q3).
- **Unabhängige Nachrechnung (15:34, Claude-Agent, eigener numpy-Code, nur lesend):** alle Zahlen reproduziert (Schnappschuss, k-Indizierung, Median geprüft; k = 101 wächst von z ≈ 7 bei Schritt 500 auf ≈ 32 bei 2500). **Übernommene Einschränkung:** Das Oberwellen-Signal ist schwach. Auch ohne Ziele und k = 101 in der Nullverteilung haben 8 (Stride-Mittel) bzw. 10 (i.i.d.-Mittel) beliebige k ein z > 3 (≈ 7 erwartet) – z ≈ 3 liegt im Schwanz der Nullverteilung; im R-stride-Mittel allein sind nur 201 und 302 erhöht. Die Rangsumme der fünf vorab genannten k ist auffällig (alle fünf in den Top-200: zufällig ≈ 1e-7, post hoc, unabhängige k angenommen), trägt aber vor allem auf 201 und 302. **Der beschreibende Satz oben („passt zu einem nicht-sinusförmigen Profil“) gilt deshalb nur als schwacher Hinweis, nicht als Stütze.** Gemeint sind die Oberwellen k ≈ m · p/99 (nächste ganze Zahl), nicht die Vielfachen von 101 (303, 404, 505 sind nicht erhöht: z 1.7 / 0.2 / −1.0).

## Ergebnis

Offen.

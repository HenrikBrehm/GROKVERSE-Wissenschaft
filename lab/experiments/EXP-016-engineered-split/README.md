---
id: EXP-016
status: laufend
datum: 2026-09-26
tags: [exp/laufend, neu/kandidat]
verwandt: ["[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[experiments/EXP-014-split-vs-init/README|EXP-014]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-016: Frequenzen über die Datenauswahl steuern (konstruierter Split)

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 ~03:25 Berlin (Sitzung 4), bevor ein
Lauf mit konstruiertem Split existierte. Code: `make_split.py` (Split-Generator), Option `--split-file` in
`freq_ban.py`. Unit-Test `test_engineered_split_indexing` im Fenster ok (11/11). **Ein Trainingslauf mit
`--split-file` ist noch nicht erfolgt:** vor dem ersten echten Lauf ein Smoke-Test mit `--steps 50`.

Kandidat [[NOVEL_DIRECTIONS]] N3. Vorgänger: [[experiments/EXP-015-mask-spectrum/README|EXP-015]] (das
Masken-Spektrum M0 eines zufälligen Splits sagt K voraus, explorativ r̄ 0.307).

## Idee

Wenn die Paarstruktur des Trainingssplits die Frequenzwahl mitbestimmt (EXP-015), sollte ein **gezielt
konstruierter** Split dem Netz vorgegebene Frequenzen aufdrängen, ohne Gewichte, Architektur oder Verlust zu
ändern. `make_split.py` zieht für jedes Init-Seed i eine zufällige Zielmenge F*_i (5 aus 56, Salz 30011) und nimmt
Paare (a, b) mit Gewicht q(a, b) = max(0.05, 1 + ε · mean_{k∈F*} cos(2πka/p + φ_{k,a+b})) auf, ε = 2, genau
3831 Paare wie der Standardsplit, Test = Komplement.

Offline-Prüfung (Seeds 10–19): F*_i ist in allen 10 Fällen genau die M0-Top-5; Anteil an der M0-Leistung
0.187–0.196 (natürliche Top-5 eines Zufallssplits: 0.103–0.108).

| | |
|---|---|
| **Fragestellung** | Lernt das Netz bevorzugt die Frequenzen, die der konstruierte Split im Masken-Spektrum hervorhebt? |
| **H16** | Überlappung von K mit F*_i ist unter dem konstruierten Split größer als unter dem Zufallssplit desselben Init-Seeds |
| **Bedingungen** | `eng`: Init i, Split `splits/split_seed{i}_eps2.0.npy` · Kontrolle: EXP-003d-Baseline B_i (gleiche Init, Zufallssplit) |
| **Seeds** | 10–19 |
| **Primärgröße** | D_i = \|K_eng,i ∩ F*_i\| − \|K_{B_i} ∩ F*_i\| |
| **Test** | Vorzeichen-Permutationstest über die gültigen i, einseitig (D̄ > 0); Austauschbarkeitsannahme wie EXP-010 (kein Exaktheitsanspruch im Randomisierungssinn) |
| **Entscheidung** | *steuerbar*: D̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: D̄ > 0, p ≥ 0.05 · *widerspricht*: D̄ ≤ 0 · < 8 gültige: *nicht auswertbar* |
| **Gültig** | beide Läufe `completed` und gekreuzt (gen ≠ None); eng-Lauf hat `split_file` des richtigen Seeds; Init-Spektrum bei 0 gleich B_i |
| **Sekundär** | mittlere \|K_eng ∩ F*\| gegen Zufall 0.45 (MC); gen(eng) − gen(B) (der konstruierte Split ist ungleichmäßig, das kann das Grokking verzögern oder verhindern); Überlappung bei Schritt 250 |
| **Erwartung** | Nach EXP-015 (natürliches M0 → 1.3 von 5) etwa 1.5–2.5 von 5 unter `eng`, ≈ 0.45 unter B |
| **Was dagegen spräche** | D̄ ≤ 0: Das Masken-Spektrum ist dann nur korrelativ oder wirkt allein über den ersten Gradienten ohne Folgen für K |
| **Grenzen** | Der konstruierte Split ist nicht gleichverteilt über Paare (manche Paare selten); Unterschiede in gen sind daher nicht allein der Frequenzwahl zuzuschreiben. Nur Transformer, ε = 2 fest |
| **Budget** | 10 Läufe à ≈ 8–20 min (+ Smoke) |

## Befehle

```
python lab/experiments/EXP-016-engineered-split/make_split.py --seed I --eps 2.0     # erzeugt splits/ (reine Rechnung)
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 10 --condition baseline --steps 50 --split-file lab/experiments/EXP-016-engineered-split/splits/split_seed10_eps2.0.npy --out-root lab/experiments/EXP-016-engineered-split/raw_smoke
python lab/tools/guarded_run.py --min-minutes 33 -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed I --condition baseline --stop-after-gen 25 --split-file lab/experiments/EXP-016-engineered-split/splits/split_seed{I}_eps2.0.npy --out-root lab/experiments/EXP-016-engineered-split/raw
python lab/experiments/EXP-016-engineered-split/analyze.py
```

## Nachtrag a (2026-09-26 ~03:30 Berlin, nach Codex-Review, **vor jedem Lauf**): neues Design

Codex, geprüft und **übernommen**:
1. *Testmenge = Komplement:* Für T = 1 − M sind alle Nicht-DC-Fourierkoeffizienten die negierten von M, die
   Testmenge hat also dieselben Spitzen. Das Stoppkriterium (Test-Acc) und der Messzeitpunkt von K hängen damit von
   der Behandlung ab. → **K wird bei festem Schritt 2000 gemessen** (Top-5 von W_E), alle Läufe genau 2000 Schritte
   (`--steps 2000`), unabhängig von Testmenge und Grokking. Kein Ausschluss nicht-generalisierender Läufe.
2. *Kontrolle:* Ein Zufallssplit kontrolliert die Konstruktion nicht. → Pro Init i **zwei** konstruierte Splits
   gleicher Stärke mit **disjunkten** Zielmengen F_i und G_i (`make_split.py --arm G`; Anteil an M0 0.185–0.199).
   **Primär:** Δ_i = ov(K_F, F) + ov(K_G, G) − ov(K_F, G) − ov(K_G, F); einseitiger Vorzeichentest über die 10
   unabhängigen Init-Seeds (jeder hat seine eigenen zwei Läufe). *steuerbar*: Δ̄ > 0, p < 0.05; sonst wie oben.
   Sekundär: Top-5 der EXP-003d-Baseline bei Schritt 2000 gegen F und G.
3. *Split-Datei:* `freq_ban.py` prüft jetzt Form, Typ, Anzahl, Eindeutigkeit und Wertebereich (fail-closed); die
   Auswertung vergleicht den `split_hash` des Laufs mit dem Inhalt der .npy statt nur mit dem Dateinamen.
Budget neu: 20 Läufe × 2000 Schritte × 0.13 s ≈ 4.5 min, zusammen ≈ 90 min.
Befehl: `freq_ban.py --seed I --condition baseline --steps 2000 --split-file lab/experiments/EXP-016-engineered-split/splits/split_seed{I}_eps2.0{,_G}.npy --out-root lab/experiments/EXP-016-engineered-split/raw`

## Nachtrag b (2026-09-26 06:31 Berlin, Sitzung 5; nach 6 von 10 Seeds, **Primärgröße unverändert**)

Post hoc an Seeds 10–15 (Idee nach Sicht der Daten, daher nur explorativ): Alle 14 gelernten Nicht-Ziel-Frequenzen sind
**zweite Harmonische** fold(2k) = min(2k mod 113, 113 − 2k mod 113) einer Zielfrequenz k desselben Arms (Zufall 1.4 von
14, p 7.6e-15; Harmonische der Ziele des anderen Arms 0 von 14; dritte Harmonische auf Zufallsniveau).
Die Masken und die Init erklären sie nicht (`posthoc_m0c.py`, `posthoc_init_misses.py`). Auch unter Zufallssplits enthält
die W_E-Top-5 mehr (k, 2k)-Paare als Zufall (0.89 gegen 0.37 je Menge, 18 Seeds), die **funktionalen**
Schlüsselfrequenzen der Studie aber nicht (0.30 gegen 0.36). Deutung: 2k ist eine Oberwelle einer nicht-sinusförmigen
Embedding-Wellenform, keine eigenständig genutzte Frequenz (`posthoc_harmonics*.py`).
**Zusätzliche Sekundärgröße, vorab für Seeds 16–19 festgelegt:** K_h = die 5 stärksten W_E-Frequenzen bei Schritt 2000,
nachdem jede Frequenz entfernt wurde, die fold(2k) einer **stärkeren** Frequenz k ist (iterativ von oben). Berichtet
werden Δ_h analog zu Δ und der Anteil der Nicht-Ziel-Frequenzen in K, die Harmonische eines Ziels sind
(Vorhersage: > 50 % an Seeds 16–19). Außerdem die F-gegen-G-Asymmetrie (JOURNAL Zyklus 7).

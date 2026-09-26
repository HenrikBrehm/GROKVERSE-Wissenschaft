---
id: EXP-018
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]"]
---
# EXP-018: Beschleunigt ein spektral konzentrierter Split das Grokking?

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 ~05:58 Berlin (Sitzung 5), bevor ein
Lauf mit diesen Splits existierte. Die verwendeten Seeds 20–29 sind im Labor und in der Studie unberührt.
Code: `make_splits.py` (Splits, reine Rechnung, erzeugt `splits/`), Option `--test-file` in `freq_ban.py`,
`analyze.py`. Unit-Test `test_split_speed_sets` im Fenster ok (12/12, 05:54). **`--test-file` ist in einem echten
Trainingslauf noch nicht geprüft:** vorher Smoke mit `--steps 50`.

Anlass: In [[experiments/EXP-016-engineered-split/README|EXP-016]] generalisierten alle Läufe mit konstruiertem Split
bei Schritt 500–1100 statt 3525–11200 (Zufallssplit, gleiche Init). Das war **nicht vorab festgelegt** und hat zwei
naheliegende Artefakt-Erklärungen:
1. Die Testmenge war das Komplement des Trainingssplits und trägt damit das negierte Masken-Spektrum. Die Testmenge
   hing also von der Behandlung ab.
2. Der konstruierte Split ist nicht gleichverteilt. Irgendeine strukturierte Ungleichverteilung könnte genügen.

## Design

Pro Init-Seed i ∈ {20, …, 29}: zuerst eine gemeinsame, gleichverteilte Testmenge T*_i (20 % aller Paare). Aus dem Rest
drei Trainingsmengen mit je genau 3831 Paaren (wie der Standardsplit):

| Arm | Konstruktion | M0-Anteil der Top-5 (Seeds 20–29) |
|---|---|---|
| **R** | gleichverteilt zufällig | 0.102–0.110 |
| **E** | Gewichte wie EXP-016 (ε = 2, Zielmenge F_i = `target_set(i)`), Top-5 von M0 = F_i | 0.171–0.186 |
| **D** | (ersetzt, siehe Nachtrag a) Gewichte von E innerhalb jeder Antidiagonale permutiert | 0.103–0.108 |

Die gesamte Nicht-DC-Leistung von M0 ist in allen drei Armen gleich (Parseval für 0/1-Masken gleicher Größe,
gemessen: Quotient 0.99–1.003). E verteilt die Leistung nur auf 5 Frequenzen um. Die Häufigkeiten der Reste a, b und
a+b streuen in allen Armen ähnlich (Variationskoeffizient 0.12–0.16). Ein vorher erwogener Arm S (Gewichte von E
zufällig permutiert) wurde vor jedem Lauf verworfen: Eine Ziehung mit unstrukturierten Gewichten ist statistisch
nur eine weitere gleichverteilte Zufallsmenge, also ein Duplikat von R (die Dateien `*_train_S.npy` stammen aus
dem ersten Generatorlauf und werden nicht benutzt).

| | |
|---|---|
| **Fragestellung** | Generalisiert ein Transformer auf einer festen, gleichverteilten Testmenge früher, wenn die Trainingspaare das Masken-Spektrum auf wenige Frequenzen konzentrieren? |
| **H18** | gen(E) < gen(D) (Konzentration beschleunigt, nicht bloß strukturierte Ungleichverteilung) |
| **Primärgröße** | L_i = log2(gen(D_i) / gen(E_i)); gen = erster Schritt mit Test-Acc ≥ 0.95 auf T*_i (primäre Schwelle, Auswertung alle 25 Schritte) |
| **Zensierung** | Obergrenze 8000 Schritte. Nicht erreicht → gen = 8000 (konservativ: zensiertes D verkleinert L, zensiertes E vergrößert es nicht) |
| **Test** | Vorzeichen-Permutationstest über die 10 Seeds (alle 2^10 Vorzeichen), einseitig L̄ > 0 |
| **Entscheidung** | *beschleunigt*: L̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: L̄ > 0, p ≥ 0.05 · *widerspricht*: L̄ ≤ 0 · < 8 gültige Seeds: *nicht auswertbar* |
| **Gültig** | alle drei Läufe eines Seeds `completed`; `split_hash` = Inhalt der Datei; `test_hash` in allen drei Armen gleich |
| **Sekundär** | log2(gen(R)/gen(E)) und log2(gen(R)/gen(D)) mit demselben Test; Schwellen `sens_loose`/`sens_strict`; Überlappung der W_E-Top-5 mit F_i bei gen und bei Schritt 2000 (repliziert EXP-016 an neuen Seeds); Zeitpunkt, ab dem die Top-5 feststehen |
| **Erwartung** | Nach EXP-016: E etwa 3–8× schneller als R. Offen ist, wo D liegt |
| **Was dagegen spräche** | L̄ ≤ 0 (D so schnell wie E: dann reicht strukturierte Ungleichverteilung); E erreicht auf T* keine 95 % oder ist nicht schneller als R (dann war der EXP-016-Befund ein Artefakt der Komplement-Testmenge) |
| **Grenzen** | Nur Transformer, p = 113, ε = 2, 30 %-Trainingsgröße, eine Plattform (4 Threads). Die Trainingsmenge kommt aus 80 % statt 100 % der Paare |
| **Budget** | 30 Läufe. Erwartet E ≈ 1000, R und D ≈ 4000–8000 Schritte à 0.13 s: ≈ 20–30 min pro Seed, zusammen 3.5–5 h (mehrere Sitzungen). Abbruch eines Laufs bei NaN oder Stillstand |

## Befehle

```
python lab/experiments/EXP-018-split-speed/make_splits.py --seeds 20-29        # reine Rechnung, deterministisch
# Smoke (Pflicht vor dem ersten echten Lauf):
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 20 --condition baseline --steps 50 --split-file lab/experiments/EXP-018-split-speed/splits/seed20_train_E.npy --test-file lab/experiments/EXP-018-split-speed/splits/seed20_test.npy --out-root lab/experiments/EXP-018-split-speed/raw_smoke
# Hauptläufe, pro Seed I und Arm X in E, D, R:
python lab/tools/guarded_run.py --min-minutes 19 -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed I --condition baseline --steps 8000 --stop-after-gen 25 --split-file lab/experiments/EXP-018-split-speed/splits/seedI_train_X.npy --test-file lab/experiments/EXP-018-split-speed/splits/seedI_test.npy --out-root lab/experiments/EXP-018-split-speed/raw
python lab/experiments/EXP-018-split-speed/analyze.py
```
Warteschlange: `sh lab/experiments/EXP-018-split-speed/queue.sh` (überspringt fertige Läufe).

## Nachtrag a (2026-09-26 ~06:05 Berlin, nach Codex-Review, **vor jedem Lauf**)

Codex (`codex_review_2026-09-26.txt`, Urteil „needs-attention“), drei Befunde, selbst geprüft, alle **übernommen**:

1. *Kurze Läufe würden als zensiert bei 8000 gezählt* (z. B. ein 50-Schritt-Lauf unter `raw/`; strenge Schwelle nach
   dem Stopp 25 Schritte nach der 0.95-Kreuzung). Stimmt. → `analyze.py` prüft jetzt `exp_id`, `condition`,
   `max_steps` = 8000, `stop_after_generalization` = 25 und die Auswertetaktung. Ein Lauf ohne primäre Kreuzung ist
   nur gültig, wenn er bis 8000 lief. Ohne Kreuzung wird **beim letzten ausgewerteten Schritt** zensiert, nicht bei 8000.
   Synthetische Tests `test_analyze.py` (5/5 ok im Fenster).
2. *Der alte Arm D (Modulation über alle 56 Frequenzen, nur die latente Standardabweichung angeglichen) trennt
   Konzentration nicht von Wellenform, Clipping und Abdeckung.* Stimmt. → **Neuer Arm D:** die exakten Gewichte von E
   nach dem Clipping, **innerhalb jeder Antidiagonale a+b = c zufällig permutiert**, mit denselben Ziehungsschlüsseln
   wie E. Damit sind die Gewichtsverteilung und die erwartete Anzahl pro c identisch, zerstört ist nur die Anordnung
   entlang a, also die Fourier-Struktur. Gemessen (Seeds 20–29): M0-Top-5-Anteil E 0.173–0.189, D 0.103–0.108,
   R 0.100–0.107; Variationskoeffizient der Rest-Häufigkeiten a und c 0.11–0.16 in allen Armen; Anteil der Paare mit
   vertauschtem Partner (b, a) im Training 0.28–0.31; Anteil der Testpaare, deren vertauschtes Paar im Training
   liegt, 0.28–0.31. Alle drei Arme sind in diesen Größen gleich, nur die spektrale Konzentration unterscheidet sich.
   Die Splits wurden neu erzeugt (Tabelle oben: E/R-Werte gelten weiter, die D-Zeile ist ersetzt).
3. *Das Einsetzen von 8000 für zensierte Läufe ist nicht konservativ für eine unbeschränkte Zeit.* Stimmt. →
   **Primärgröße ist ausdrücklich die beschränkte Zeit** min(gen, 8000): L_i = log2(min(gen_D, 8000)/min(gen_E, 8000)),
   Vorzeichen-Permutationstest wie oben. **Ko-Bedingung:** ein zensierungsfester gepaarter Vorzeichentest
   (exakt binomial, einseitig) über die Seeds, deren Reihenfolge bestimmt ist (E kreuzt vor der Zensur von D oder
   umgekehrt; beide zensiert → unbestimmt, fällt heraus). *beschleunigt* nur, wenn **beide** p < 0.05. Die Aussage
   gilt dann für die Zeit bis 8000 Schritte.

Sekundär unverändert, jetzt ebenfalls als zensierungsfeste Vorzeichentests (E vs. R, D vs. R, alle drei Schwellen)
plus beschränkte log-Quotienten R/E und R/D.

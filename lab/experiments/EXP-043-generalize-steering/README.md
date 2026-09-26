---
id: EXP-043
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/GPU-001-equivalence/README|GPU-001]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-043: Verallgemeinert sich die Steuerung der Frequenzwahl über die Daten? (Addition mod 97, Multiplikation mod 113)

**Status:** vorbereitet, **nicht ausgeführt**, Code ungetestet. Definition fixiert 2026-09-26 19:19 Berlin (Sitzung 11), vor
jedem Lauf. Ziel in [[FINDINGS]]: größte offene Frage (K2 außerhalb von Addition mod 113; Regel 15c). Läuft **nur auf der GPU**
und erst nach bestandenem [[experiments/GPU-001-equivalence/README|GPU-001]].

## Idee

[[experiments/EXP-016-engineered-split/README|EXP-016]] zeigte bei Addition mod 113: Ein Split, dessen Paare entlang der
Antidiagonalen mit Zielfrequenzen oszillieren, gibt die gelernten W_E-Frequenzen vor (10/10, Δ̄ +7.7). Gilt das auch
(1) bei **anderem Modulus** (p = 97, 48 Frequenzen, 2823 Trainingspaare) und
(2) bei **Multiplikation mod 113**, einer anderen Aufgabe, die das Netz in der Basis des diskreten Logarithmus löst
(zyklische Gruppe Z_112, Primitivwurzel g = 3; Studie `docs/ADD_VS_MUL_EIGENLEISTUNG.md`; „Discrete-Log Clock“,
https://arxiv.org/abs/2606.17399)? Die Konstruktion wird dafür in **Gruppenkoordinaten** übertragen: u = log a, v = log b,
Oszillation entlang der Nebendiagonalen u + v = const. mod 112. Paare mit einer Null (2p − 1 = 225) bekommen das neutrale Gewicht 1.
Gelingt die Steuerung bei Multiplikation, liegt der Hebel an der Gruppenstruktur der Aufgabe, nicht an der Zahlendarstellung.
Gelingt sie nicht, ist K2 an die natürliche Anordnung gebunden: ebenso wichtig.

Offline-Prüfung der Splits (make_split.py, reine Rechnung): In allen 40 Fällen ist die Zielmenge genau die Top-5 des
Masken-Spektrums in Gruppenkoordinaten; Anteil 0.196–0.212 (add 97), 0.178–0.205 (mul 113), wie in EXP-016 (0.185–0.199).

| | |
|---|---|
| **Fragestellung** | Geben konstruierte Splits auch bei add mod 97 und mul mod 113 die gelernten Frequenzen vor? |
| **H43** | Je Aufgabe: Δ̄ > 0 (eigene Zielmenge häufiger in K als die fremde) |
| **Bedingungen** | Je Aufgabe und Init-Seed i ∈ 70–79: Arm F und Arm G (disjunkte Zielmengen, gleiche Stärke ε = 2, getrennte Zufallsströme), 2000 Schritte, Preset `arch25k` (Transformer, AdamW lr 1e-3, wd 1, 30 %), Test = Komplement |
| **Messgröße K** | Top-5 der W_E-Leistung bei Schritt 2000 **in der Gruppenbasis**, aus den W_E-Schnappschüssen: add 97 Zeilen a = 0..96, k = 1..48; mul 113 Zeilen g^i, i = 0..111, k = 1..55. Die Nyquist-Mode k = 56 ist nie Ziel und nie in K (ihr Rang wird berichtet) |
| **Primär** | Δ_i = ov(K_F, F) + ov(K_G, G) − ov(K_F, G) − ov(K_G, F) (wie EXP-016) |
| **Test** | Einseitiger Vorzeichen-Permutationstest über die 10 Seeds je Aufgabe; Holm über die zwei Aufgaben (α = 0.05) |
| **Urteil je Aufgabe** | *steuerbar*: Δ̄ > 0 und Holm-signifikant · *richtungsgleich, n. s.*: Δ̄ > 0 sonst · *widerspricht*: Δ̄ ≤ 0 · < 8 gültige Seeds: *nicht auswertbar* |
| **Gültig** | beide Arme `completed`, ≥ 2000 Schritte, richtige Aufgabe/p, `device = cuda`, Split-Hash = Datei, Schnappschuss bei 2000 |
| **Gesamtlesart (vorab)** | K2 „verallgemeinert sich auf diese zwei Fälle“ nur, wenn **beide** *steuerbar* sind. Nur add 97: Modulus egal, Aufgabe offen. Nur mul: unerwartet, dann Einzelwerte prüfen. Keine: K2 bleibt auf Addition mod 113 beschränkt (in [[FINDINGS]] als Grenze) |
| **Sekundär** | Überlappung mit der eigenen Zielmenge bei 50/250/500/1000; Anteil der Nicht-Ziel-Frequenzen, die fold(2k) eines Ziels sind (Gruppe Z_n); Top-5-Anteil der Leistung; gen und Test-Acc (Komplement, nur beschreibend); Zufallssplit R (ε = 0, 20 Läufe) gegen F/G als Zufallsniveau |
| **Erwartung** | add 97: wie EXP-016 (Δ̄ ≈ 7–8). mul 113: offen; ich erwarte *steuerbar*, aber schwächer, weil 1.8 % der Paare (mit Null) nicht in die Gruppenstruktur passen |
| **Was dagegen spräche** | Δ̄ ≤ 0 oder n. s. bei mul: Die Steuerung hängt dann an der additiven Anordnung, nicht an der Gruppenstruktur |
| **Grenzen** | Eine Architektur, eine Konstruktion (ε = 2), 2000 Schritte, K = W_E-Top-5 (nicht funktional); GPU statt CPU (andere torch-Version, deshalb GPU-001); Seeds 70–79 teilen die Init nicht zwischen den Aufgaben (anderes Vokabular bei p = 97) |
| **Budget** | 40 Läufe × 2000 Schritte (+ 20 R-Läufe), J parallel auf der GPU; Dauer erst nach GPU-001 bekannt (CPU wären ≈ 3 h) |

## Einordnung vor jedem Lauf (19:27 Berlin): Multiplikation ist hier fast nur ein anderer Modulus

W_E und W_U sind Nachschlagetabellen mit iid-Gauß-Init; ihre Verteilung ist invariant, wenn man die Token umbenennt. Benennt man
jeden Rest a ≠ 0 in log_g a um (Eingabe **und** Ausgabe), wird Multiplikation mod 113 auf den 112² Paaren ohne Null **exakt** zu
Addition mod 112, in Verteilung über Init und Split. Übrig bleiben das Token 0 und die 225 Paare mit einer Null (Ausgabe 0).
EXP-043 prüft deshalb in Wahrheit: **(1) anderer Primmodulus (97), (2) zusammengesetzter Modulus 112** (mit nicht treuen
Frequenzen, gcd(k, 112) > 1) plus eine kleine Störung durch die Null. Eine *wirklich* andere Aufgabe ist das nicht; die
Gesamtlesart oben wird entsprechend gelesen: *steuerbar* bei mul 113 heißt „auch bei zusammengesetztem Modulus mit Null-Token“,
nicht „bei einer anderen Rechenart“. Urteilsregeln unverändert. Echte Verallgemeinerung über die Aufgabe braucht eine nicht
zyklische Struktur (z. B. nicht-abelsche Gruppe, Chughtai et al. 2023) oder eine nicht-modulare Aufgabe; über die Architektur:
[[experiments/EXP-045-mlp-steering/README|EXP-045]] (MLP mit gemeinsamem Embedding).

## Befehle

```
python lab/experiments/EXP-043-generalize-steering/make_split.py --seed I --task add|mul --p 97|113 --arm F|G     # splits/ (erzeugt)
python lab/experiments/EXP-043-generalize-steering/make_split.py --seed I --task ... --arm R --eps 0               # Zufallsreferenz
sh lab/experiments/EXP-043-generalize-steering/queue.sh J        # Selbsttest, Smoke (mul), 40 Läufe, Auswertung, R-Läufe
python lab/tools/guarded_run.py -- python lab/experiments/EXP-043-generalize-steering/analyze.py
```

## Folgeversuch (nur wenn eine Aufgabe *steuerbar* ist)

EXP-044 (noch nicht festgelegt): frühe Festlegung (K4) in derselben Aufgabe, Datenwechsel F → G nach t ∈ {10, 25, 50, 150}
Schritten, 10 Seeds, GPU. Ohne Steuerbarkeit ist der Wechselversuch dort nicht auswertbar.

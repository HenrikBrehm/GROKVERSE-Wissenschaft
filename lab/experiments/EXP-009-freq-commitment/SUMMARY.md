---
id: EXP-009
status: abgeschlossen
datum: 2026-09-25
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[experiments/EXP-009-freq-commitment/README|EXP-009 Definition]]", "[[experiments/EXP-002-destined-ban/README|EXP-002]]", "[[experiments/EXP-010-init-swap/README|EXP-010]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-009: Ergebnis. Das Init-Embedding sagt mit, welche Frequenzen gewinnen

Definition (vorab committet, 9f3531b): [[experiments/EXP-009-freq-commitment/README|README]].
Es wird nur ausgewertet, ein Training gab es nicht. Die Auswertung lief am 2026-09-25 um ~21:52 Berlin,
außerhalb des Run-Fensters, als Sichtung gespeicherter Checkpoints (Deutung wie in Sitzung 2).
Reproduktion: `python lab/experiments/EXP-009-freq-commitment/commitment.py` (≈ 10 s),
danach `cd lab/experiments/EXP-009-freq-commitment && python controls.py`.

## Primärtest (vorab festgelegt)

| | Wert |
|---|---|
| r̄(0) über 40 Läufe (mittlerer normierter Init-Rang der späteren Top-5) | **0.386** |
| Null (Monte Carlo, 100 000) | 0.500 |
| p (einseitig) | < 1e-5 (0 von 100 000 Replikaten ≤ Statistik) |
| **Urteil** | **Init trägt Information** |

## Pro Gruppe (mitberichtet, nicht entscheidend)

| Gruppe | r̄(0) | p₀ (n=10) | r̄(500) | r̄(2000) | Anteil L < g | Median L/g |
|---|---|---|---|---|---|---|
| Transformer | 0.37 | 0.001 | 0.09 | 0.09 | 0.9 | 0.29 |
| MLP-512 | 0.25 | < 0.001 | 0.16 | 0.13 | 0.1 | 1.55 |
| MLP-572 | 0.33 | < 0.001 | 0.16 | 0.13 | 0.2 | 1.29 |
| Two-hot-MLP (m2h) | **0.58** | 0.98 | 0.30 | 0.25 | 0.0 | 1.49 |

L = Lock-in-Schritt (ab hier bei jedem späteren Grid-Schritt ≥ 4 der 5 K_final in den Top-5),
g = Generalisierungsschritt. Rohwerte in `summary.json`.

## Explorative Kontrollen (post hoc, nicht vorab festgelegt)

`controls.py`: Die Kreuz-Seed-Kontrolle nimmt den Rang von K_final aus Seed A im Init-Spektrum von
Seed B (A ≠ B, 90 Paare je Gruppe).

| Gruppe | eigener Seed | fremder Seed (± SD) | K_final in Init-Top-5 (Zufall 0.09) | Init-Top-1 ∈ K_final (Zufall 0.09) |
|---|---|---|---|---|
| Transformer | 0.375 | 0.520 ± 0.105 | 0.20 | 0.3 |
| MLP-512 | 0.255 | 0.514 ± 0.144 | 0.26 | 0.3 |
| MLP-572 | 0.332 | 0.516 ± 0.129 | 0.20 | 0.3 |
| m2h | 0.583 | 0.515 ± 0.134 | 0.04 | 0.0 |

Mit fremdem Seed liegt der Wert auf Zufallsniveau. Der Effekt ist also **seed-spezifisch** und
weder ein Artefakt der Initialisierung noch eine allgemeine Frequenzvorliebe. Plausibilität: Das
Init ist iid-normal (`nn.init.normal_`), und `ckpt_step000000` wird vor dem ersten
Optimiererschritt gespeichert (`train.py:328`).

**m2h pro Neuron** (`neuron_lottery_m2h.py` → `neuron_lottery_m2h.json`): Neuronen, deren Eingangsgewichte `W_in[:p, j]` bei 25k eine dominante Frequenz haben
(Anteil > 0.5, rund 330–365 von 512). Deren finale Frequenz lag im **Init-Spektrum desselben
Neurons** im Mittel bei Rang 0.34–0.37, bei Zufall wären es 0.5. Final und Init-argmax stimmen in
4–8 % der Fälle überein (Zufall 1.8 %), und zwar in allen 10 Seeds. Die Lotterie läuft bei m2h
also **pro Neuron**. Das aggregierte Spektrum sagt die Netzebene nicht voraus.

## Beobachtung, Deutung, Spekulation

- **Beobachtung:** Bei allen drei Architekturen mit gemeinsamem Embedding `W_E` sind die fünf
  Frequenzen, die das Netz am Ende nutzt, schon im zufälligen Init-Spektrum von `W_E`
  überdurchschnittlich stark. Bei der Two-hot-MLP ohne gemeinsames Embedding gilt das nur pro
  Neuron.
- **Deutung (vorläufig):** Die Init von `W_E` ist randomisiert und unabhängig von Split und
  übrigen Gewichten. Eine Abhängigkeit zwischen K_final und dem Init-Spektrum ist deshalb im
  Populationssinn ein **Einfluss** der W_E-Init auf die Frequenzwahl, nicht bloß eine
  Scheinkorrelation. Der Effekt ist mäßig: Etwa eine der fünf Frequenzen stammt „aus der
  Lotterie“, die übrigen nicht. Beim Transformer steht die Auswahl schon lange vor der
  Generalisierung fest (Median L/g = 0.29), bei den MLPs erst danach.
- **Spekulation:** Ein gemeinsames Embedding macht aus vielen Einzellotterien pro Neuron eine
  **gemeinsame Lotterie**. Eine Frequenz, die in `W_E` stark startet, ist für alle nachgelagerten
  Neuronen zugleich stark.

## Einordnung in die Literatur (Suche vom 2026-09-25, Details in [[NOVEL_DIRECTIONS]])

Nah verwandt ist He, Wang, Chen, Yang 2026, *On the Mechanism and Dynamics of Modular Addition:
Fourier Features, Lottery Ticket, and Grokking* (https://arxiv.org/abs/2602.16849). Dort ist
gezeigt, dass pro Neuron die Frequenz mit der größten Init-Amplitude und der kleinsten
Phasenabweichung gewinnt, bei 2-Schicht-MLPs mit One-hot-Eingabe. Unser m2h-Befund pro Neuron
**repliziert** das qualitativ. **Nicht gefunden** haben wir bei unserer Suche:
- die Vorhersage der **netzweiten** Frequenzmenge aus dem Init-Spektrum eines **gemeinsamen
  Embeddings** (Transformer, MLP mit W_E)
- den Kontrast gemeinsames Embedding ↔ Lotterie pro Neuron
- eine gemessene Lock-in-Zeit relativ zur Generalisierung

Das gilt als „nach unserer Suche vom 2026-09-25 nicht gefunden“, nicht als garantiert neu.

## Grenzen

- n = 10 pro Gruppe. Eine Plattform (Studienläufe, torch 2.12.1).
- K_final bei 25k ist eine Definition.
- Die m2h-Neuronenanalyse ist post hoc. Die Schwelle 0.5 für „dominant“ wurde ohne Sensitivitätsprüfung gesetzt.
- Die kausale Steuerbarkeit ist nicht gezeigt, siehe dazu [[experiments/EXP-010-init-swap/README|EXP-010]].

## Entscheidung

**Beibehalten und kausal weiterprüfen.** Nächster Schritt ist EXP-010: in der Init die
Fourier-Koeffizienten von `W_E` zwischen den Top-5 und fünf schwachen Frequenzen vertauschen.
Die Verteilung bleibt dabei exakt erhalten, Split und alle anderen Gewichte bleiben gleich. Die
Frage ist, ob die Frequenzwahl mitwandert. Das schärft auch [[experiments/EXP-002-destined-ban/README|EXP-002]]:
Die „Ziel“-Frequenzen sind teilweise einfach die Init-starken.

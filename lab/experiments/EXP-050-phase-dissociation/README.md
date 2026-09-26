---
id: EXP-050
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[BEFUND-split-mechanismus]]", "[[experiments/EXP-019-coherent-mask/README|EXP-019]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-050: Wählt der Transformer nach M0c oder nach M0? (Phasen-Dissoziation)

**Status:** vorbereitet, **nicht ausgeführt, ungetestet, nicht in einer Queue** (Sitzung 13, 2026-09-26, außerhalb des Fensters).
Festgelegt vor jedem Lauf. Zurück zu [[LAB]] · [[FINDINGS]] · Idee [[NOVEL_DIRECTIONS]] N26.

## Bezug zu [[FINDINGS]]

Zielt auf **Grenze 4 / K2-Mechanismus**: Welche Eigenschaft des Splits wählt die Frequenzen? Die Rechnung erster Ordnung
([[BEFUND-split-mechanismus]], Abschnitt „Herleitung erster Ordnung“) sagt für den Transformer mit gemeinsamer Einbettung: Der erste
W_E-Gradient folgt dem **kohärenten** Masken-Spektrum M0c (linke und rechte Position vor dem Betragsquadrat addiert), nicht M0. Das
passt zur Messung am ersten Gradienten (Sitzung 5: M0c 0.77 vs. M0 0.57), aber für die **finalen** Frequenzen war M0c nur post hoc
richtungsgleich ([[experiments/EXP-019-coherent-mask/README|EXP-019]]). Bei Zufallssplits und in EXP-016 ist M0c ≈ M0, deshalb waren
beide nie zu trennen. Dieser Versuch trennt sie kausal.

## Aufbau

- **Konstruktion** (EXP-016-Typ, add mod 113, ε = 2, 3831 Paare): q(a, b) = max(0.05, 1 + ε · mean_{k∈T} cos(2πka/p + φ_{k,c})), c = a + b.
  Links trägt die Frequenz k den Faktor e^{iφ}, rechts e^{−i(2πkc/p + φ)}. **sym:** φ = −πkc/p (gleichphasig, M0c = 2·M0 auf den Zielen).
  **anti:** φ = π/2 − πkc/p (gegenphasig, die Beiträge löschen sich in M0c aus). Gleiche Zielmengen F, G (je 5 aus k = 1..56,
  disjunkt) für sym und anti eines Seeds. Ströme `SeedSequence([50001, seed, arm, mode, Zweck])`. Seeds 180–189.
- **Offline (reine Rechnung, 20 Splits je Modus):** sym: Zielrang M0 2.0, M0c 2.0 (M0c-Anteil 0.270); **anti: M0 2.0, M0c 25.3**
  (Zufall 27.5; M0c-Anteil 0.091, Zufall 0.089); Häufigkeitsspektrum in beiden ≈ Zufall (25.4 / 24.9). Die Modi unterscheiden sich
  also nur im Kreuzterm, nicht in M0 und nicht in den Token-Häufigkeiten.
- **Läufe:** je Seed sym_F, sym_G, anti_F, anti_G; Transformer der Studie, 2000 Schritte, **GPU**, `freq_ban.py --split-file`
  (Läufe heißen `EXP-016_…`; maßgeblich sind Ordner `EXP-050/raw` und Split-Name). K-Messung: W_E-Spektrum bei 2000.

| | |
|---|---|
| **Fragestellung** | Folgt die Frequenzwahl des Transformers dem kohärenten Spektrum M0c oder dem Spektrum M0? |
| **H50a (M0c selektiert)** | D_i = Δ_pow,sym − Δ_pow,anti > 0 |
| **H50b (M0 steuert trotzdem)** | Δ_pow,anti > 0 |
| **Primärgröße** | Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] je Modus (wie EXP-048/049; an EXP-016 kalibriert: 8.4) |
| **Test** | je einseitiger Vorzeichen-Permutationstest über die gültigen Seeds; **Holm über {a, b}** |
| **Gültig** | alle vier Läufe eines Seeds `completed`, 2000 Schritte, cuda, p 113/add, Split-Hash = .npy, Spektren endlich; < 8 gültige Seeds: *nicht auswertbar* |
| **Urteil a** | *M0c selektiert*: D̄ > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *widerspricht*: D̄ ≤ 0 |
| **Urteil b** | *anti steuert trotzdem (M0-Anteil)*: Δ̄_anti > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *anti steuert nicht*: Δ̄_anti ≤ 0 |
| **Manipulationsprüfung (berichtet)** | Δ̄_pow,sym > 0 (sym muss steuern, sonst ist a nicht deutbar) |
| **Vorhersage erster Ordnung** | a ja, b nein (anti ≈ 0) |
| **Gegenhypothese** | Die Wahl folgt M0 (z. B. weil spätere Schritte mit nicht gleichverteilter Ausgabe oder die MLP-Nichtlinearität J_L ≠ J_R machen): D̄ ≈ 0, b ja |
| **Was die Deutung begrenzt** | Zwischenergebnis „a ja und b ja“: Kreuzterm verstärkt, M0 trägt auch. Nur Transformer; der Gegenversuch im MLP mit getrennten W_in-Hälften (Vorhersage dort umgekehrt: anti steuert, sym nicht stärker) ist ein Folgeversuch. sym hat auf den Zielen mehr M0c-Leistung als EXP-016 (0.270 vs. ≈ 0.19): Δ_pow,sym ist deshalb nicht direkt mit EXP-016 vergleichbar |
| **Budget** | 40 Läufe à 2000 Schritte auf der GPU (wie EXP-047), J parallel |

## Befehle

```
python lab/experiments/EXP-050-phase-dissociation/make_split.py --seed I        # reine Rechnung, erledigt (180–189)
sh lab/experiments/EXP-050-phase-dissociation/queue.sh J                        # Selbsttest, 40 Läufe, Auswertung
```

Nicht in `queue_gpu_s11.sh`: Die Nacht 26./27.09. hat schon sechs neue GPU-Versuche. Einreihen erst nach deren Auswertung (oder
ans Ende, falls die GPU-Queue früh fertig ist) und nach einer unabhängigen Prüfung dieses Codes.

## Literatur (Suche 2026-09-26, Sitzung 13)

Suchbegriff: „modular addition training set symmetric pairs (a,b) (b,a) phase first gradient embedding which frequencies learned“.
Nächstverwandt: He et al. 2026, *On the Mechanism and Dynamics of Modular Addition* (https://arxiv.org/abs/2602.16849): symmetrische
Paare werden zuerst memoriert, Frequenzen konkurrieren je Neuron nach Init-Betrag und Phasenlage; vollständige/zufällige Daten, keine
Konstruktion des Splits über die Phase des Kreuzterms (laut Suchtreffer-Zusammenfassung). Einordnung: #neu/kandidat, vorläufig
(„nach unserer Suche vom 2026-09-26 nicht gefunden“; nur Zusammenfassungen geprüft).

*Entscheidung (20:28):* Der MLP-Gegenarm (Vorhersage: MLP mit getrennten W_in-Hälften folgt M0, also steuert anti dort) wird erst nach [[experiments/EXP-045-mlp-steering/README|EXP-045]] festgelegt: Erst dessen K bei 2000 und 10 000 Schritten zeigt, ob das MLP nach 2000 Schritten schon eine Auswahl getroffen hat. `freq_ban.py --arch mlp` kann die EXP-050-Splits unverändert trainieren (Run-IDs enden auf `_mlp_devcuda`, kollidieren nicht mit dem Transformer-Glob).

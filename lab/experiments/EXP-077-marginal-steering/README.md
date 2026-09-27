---
id: EXP-077
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[BEFUND-split-mechanismus]]", "[[paper/draft]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-077: Steuert allein die Häufigkeit des linken Operanden die gelernten Frequenzen? (PILOT)

Zurück zu [[LAB]] · [[FINDINGS]] (Mechanismus von K2; Programm **C**: mechanistische Vorhersage an unberührten Fällen, zwischen expliziten Konkurrenzmodellen, Regel 18c).
Festgelegt 2026-09-27, Sitzung 25, 14:38 Berlin (gemessen), **vor jedem EXP-077-Lauf** (Läufe frühestens ab 00:00). **Pilot/Exploration**, 10 Seeds, kein Bestätigungsurteil.

## Anlass

Beim Ausformulieren der Theorie erster Ordnung ([[paper/draft]] §5.2, Sitzung 25) zeigte eine numpy-Prüfung: Im ersten W_E-Gradienten fällt nur die **eigene** Häufigkeit einer Zeile
exakt heraus, nicht die des anderen Operanden. Für eine Maske m(a, b) = ρ(a) hat der gemeinsame Pfad die Leistung p|ρ̂(k)|². Nach der Lesart von EXP-047 („die Steuerung läuft über die
Paarstruktur, Häufigkeiten tragen allein nicht“) sollte eine reine Häufigkeitsstruktur dagegen nichts bewirken. EXP-047 hielt die (schwachen, CV 0.14) Häufigkeiten fest und zerstörte die
Paarstruktur; hier ist es umgekehrt: **starke** Häufigkeitsstruktur eines Operanden, **keine** Paarstruktur über die Produktform hinaus.

## Konkurrenzmodelle

- **(Paar)** Nur die Anordnung der Paare entlang der Antidiagonalen steuert; Token-Häufigkeiten wirken nicht → Δ_pow ≈ 0.
- **(1. Ordnung)** Der erste Gradient (bzw. M0/M0c inklusive des Häufigkeitsanteils des anderen Operanden) steuert → Δ_pow > 0 in der Größenordnung der konstruierten Splits.

## Aufbau

- **Splits** (`make_split.py`, reine Rechnung, erledigt 14:38): q(a, b) = max(0.05, 1 + ε · mean_{k∈T} cos(2πka/113 + φ_k)), unabhängig von b; 3831 Paare ohne Zurücklegen, Test = Komplement.
  F, G je 5 disjunkte Ziele aus 1..56; Ströme `SeedSequence([77001, Seed, Arm, ε, Zweck])`; Seeds **770–779** (bisher ungenutzt).
- **Offline gemessen (vor jedem Lauf):** ε = 2: M0-Zielrang 3.0 (alle fünf Ziele oben), Zielanteil 0.191, CV der linken Häufigkeiten 0.53, rechts 0.14 (Zufallsniveau);
  ε = 1: Rang 3.46, Anteil 0.117, CV links 0.30. Vergleich (Kalibrier-Seeds 900–909, Versuchs-ID 99): konstruierte P1-Splits Rang 3.0 / Anteil 0.190, Zufall 30 / 0.089. Anteil im
  gemeinsamen Pfad erster Ordnung (zentriertes M0c): ε = 2: 0.146, ε = 1: Rang 11.3 / 0.104, konstruierte Splits 0.189.
- **Läufe:** Transformer der Studie, `freq_ban.py --split-file`, 2000 Schritte, GPU, 1 Thread, 40 Läufe (10 Seeds × F/G × ε ∈ {2, 1}), `jobs.txt`.
- **Maß:** Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] der W_E-Leistung bei 2000 (wie P1), je Seed; einseitiger exakter Vorzeichen-Permutationstest; Bootstrap-KI (beschreibend).

| | |
|---|---|
| **Primär** | ε = 2 |
| **Lesart vorab** | Δ̄ ≥ 1 und p < 0.05 → *Randverteilung steuert* (stützt 1. Ordnung) · Δ̄ < 0.5 oder p ≥ 0.2 → *keine Steuerung über die Randverteilung* (stützt Paar) · sonst *unklar* |
| **Sekundär (nur berichtet)** | ε = 1 (dort trennen sich M0 und der gemeinsame Pfad erster Ordnung: Rang 3.5 gegen 11.3); Test-Genauigkeit, gen-Schritt |
| **Gültig** | beide Läufe über den gemeinsamen Lader ok (Seed, cuda, 2000 Schritte, Split-Hash, Spektrum bei 2000 endlich); < 8 gültige Seeds → *nicht auswertbar* |
| **Was dagegen spräche** | Δ̄ ≈ 0 trotz M0-Rang 3.0: dann sagt M0 die Steuerung nicht allgemein voraus, sondern nur, wenn das Signal aus der Paarstruktur kommt; die Theorie erster Ordnung wäre für den Häufigkeitsanteil falsch |
| **Grenzen** | Pilot, 10 Seeds; starke Häufigkeitsungleichheit (CV 0.53) kann Lerngeschwindigkeit und Grokking verändern (berichtet, nicht Teil des Urteils); nur add 113, Repräsentationsmaß (Energie), keine Funktion |
| **Budget** | 40 × 2000 Schritte, GPU, ≈ 0.03 s/Schritt bei 10 parallel → ≈ 5 min |

## Literatur (Suche 2026-09-27, Sitzung 25, WebSearch)

Suchbegriffe: „token frequency imbalance training distribution determines Fourier features modular addition grokking non-uniform operand distribution“; „"modular addition" non-uniform input
distribution frequencies learned embedding skewed operand sampling transformer“; „arxiv 2026 grokking modular arithmetic "non-uniform" sampling of operands changes which frequencies are learned“.
Nächstverwandt: Arbeiten zu ungleichmäßiger Operandenstichprobe und Lernerfolg (modulare Exponentiation, https://arxiv.org/abs/2506.23679: Genauigkeit, nicht Frequenzwahl); Datenverteilung
und Grokking-Auftreten (https://arxiv.org/abs/2505.15624); keine Arbeit gefunden, die über die Häufigkeit eines Operanden steuert, **welche** Frequenzen entstehen. Einordnung #neu/kandidat,
vorläufig („nach unserer Suche vom 2026-09-27 nicht gefunden“; nur Suchtreffer/Abstracts).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

Keine Läufe dieser Splits. Gesehen: EXP-047 (Ergebnis), die offline M0-/Häufigkeitsstatistik oben; daraus ε = 2 als primär (stärkstes Signal bei gleichem M0-Rang wie P1).

## Befehle

```
python lab/experiments/EXP-077-marginal-steering/make_split.py        # erledigt, reine Rechnung
python lab/tools/parallel_queue.py lab/experiments/EXP-077-marginal-steering/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-077-marginal-steering/analyze.py
```

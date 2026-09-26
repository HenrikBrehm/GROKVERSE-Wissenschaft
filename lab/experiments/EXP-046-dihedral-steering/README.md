---
id: EXP-046
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-046: Datensteuerung der Irreps in einer nicht-abelschen Gruppe (Diedergruppe D₅₉)

**Status:** vorbereitet, **nicht ausgeführt, ungetestet** (Sitzung 12, 2026-09-26 19:35 Berlin, außerhalb des Fensters).
Festgelegt, bevor ein einziger Lauf auf D₅₉ existierte. Zurück zu [[LAB]] · [[FINDINGS]] · Idee [[NOVEL_DIRECTIONS]] N24.

## Bezug zu [[FINDINGS]]

Zielt auf die **größte offene Frage** (gilt K2 außerhalb von Addition mod 113?). Begründung aus Sitzung 11, Zyklus 5:
Multiplikation, Subtraktion und andere Moduli sind für dieses Modell nach Umbenennung der Token wieder *zyklische* Gruppen,
also kein neuer Aufgabentyp. D₅₉ (Ordnung 118, Symmetrien des 59-Ecks) ist **nicht abelsch**: Keine Umbenennung der Token
macht daraus eine zyklische Gruppe. Die „Frequenzen“ sind hier 2×2-Matrix-Darstellungen (29 zweidimensionale Irreps ρ_k,
k = 1..29, dazu trivial und Vorzeichen). Wählt das Netz auch hier die Irreps, die der Split hervorhebt?

## Aufbau

- **Aufgabe:** a ∘ b in D₅₉; Token 0..58 = Drehungen r^m, 59..117 = Spiegelungen s r^m, Token 118 = „=“. Gleiches Modell
  (1-Schicht-Transformer, Preset arch25k, AdamW lr 1e-3, wd 1, Full Batch), `p = 118` in der Konfiguration.
  Code: `dihedral.py` (Gruppe, Irreps, Maße; prüft Latin-Quadrat, Nicht-Kommutativität, Assoziativität, Homomorphie
  jeder ρ_k und Orthonormalität der Basis bei jedem Aufruf), `group_train.py` (Training), `make_split.py`, `analyze.py`.
- **Konstruierter Split** (Analogon zu EXP-016): Gewicht q(a, b) = max(0.05, 1 + ε · mean_{k∈T} tr(A_{k,c} ρ_k(a))), c = a∘b,
  A_{k,c} zufällige 2×2-Matrizen mit Frobeniusnorm 1 (dann hat tr(Aρ_k(a)) über a den Effektivwert 1/√2 wie cos in EXP-016),
  ε = 2, genau round(0.3 · 118²) = 4177 Trainingspaare ohne Zurücklegen, Test = Komplement.
- **Masken-Spektrum M0 (nicht abelsch):** für jede Ausgabe c die Indikatoren N_L(t) = [(t, t⁻¹c) ∈ Train] und
  N_R(t) = [(c t⁻¹, t) ∈ Train]; Leistung der Irrep k = 2 · ‖Σ_t N(t) ρ_k(t)‖²_F, summiert über c und beide Seiten.
  **Offline-Prüfung (reine Rechnung, 19:33):** Zielmenge = M0-Top-5 in **20/20** Splits (Seeds 140–149, Arme F und G),
  Anteil der Ziele an der M0-Leistung 0.246–0.280 (gleichverteilt 5/29 = 0.172).
- **K:** die 5 stärksten zweidimensionalen Irreps in W_E (Zeilen 0..117) bei Schritt 2000, Leistung = Quadratsumme der
  Koeffizienten auf den vier (orthonormierten) Matrixelement-Funktionen von ρ_k.

| | |
|---|---|
| **Fragestellung** | Gibt ein konstruierter Split auch in einer nicht-abelschen Gruppe die gelernten Irreps vor? |
| **H46** | Δ̄ > 0: Die Irreps unter Arm F überlappen stärker mit F, die unter G stärker mit G |
| **Bedingungen** | je Init-Seed i ∈ 140–149 zwei Läufe: Split F_i und Split G_i (disjunkte Zielmengen, je 5 aus 29), 2000 Schritte, **alle auf der GPU** |
| **Primärgröße** | Δ_i = ov(K_F, F) + ov(K_G, G) − ov(K_F, G) − ov(K_G, F) |
| **Test** | einseitiger Vorzeichen-Permutationstest über die gültigen Seeds (exakt, 2^n Vorzeichen) |
| **Gültig** | beide Läufe `completed`, ≥ 2000 Schritte, Gerät cuda, Split-Hash = Inhalt der .npy |
| **Strukturprüfung** (vorab) | Die Top-5-Irreps müssen in mindestens 8 der 20 gesteuerten Läufe ≥ 2× ihren Gleichverteilungsanteil der nicht-trivialen W_E-Leistung halten (≥ 0.342). Sonst **nicht auswertbar (keine Irrep-Struktur)**: Dann hat das Netz in 2000 Schritten gar keine Irrep-Auswahl getroffen, und ein Δ ≈ 0 wäre kein Beleg gegen H46 |
| **Entscheidung** | *steuerbar*: Δ̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: Δ̄ > 0, p ≥ 0.05 · *widerspricht*: Δ̄ ≤ 0 · < 8 gültige Seeds: *nicht auswertbar* |
| **Sekundär (nur berichtet)** | mittlere Überlappung passend/gekreuzt; Zufallssplit R (ε = 0, gleiche Seeds) gegen F und G (Zufall 5·5/29 ≈ 0.86); Train-/Test-Genauigkeit bei 2000 und gen-Schritt; Top-5-Anteil unter R (natürliche Irrep-Konzentration) |
| **Erwartung** | Nach EXP-016 (Δ̄ +7.7 von 10) ein klar positives Δ̄, falls der Mechanismus (Paarstruktur → erster Gradient an W_E) gruppenallgemein ist |
| **Was dagegen spräche** | Δ̄ ≤ 0 bei bestandener Strukturprüfung: Dann ist die Steuerung eine Eigenheit zyklischer Gruppen |
| **Grenzen** | D₅₉ enthält die zyklische Untergruppe Z₅₉ (Index 2); die Irreps ρ_k sind auf den Drehungen Frequenzen. Ein positives Ergebnis zeigt Steuerung bei nicht-kommutativer Verknüpfung, aber noch nicht bei „ganz anderen“ Gruppen (S₅: nur 5 nicht-triviale Irreps, schwache Statistik; Folgekandidat). 2000 Schritte: K ist die Auswahl vor dem Grokking, nicht zwingend die Endlösung |
| **Budget** | 30 Läufe à 2000 Schritte auf der GPU, J parallel (aus GPU-001). Schätzung aus EXP-016 (CPU 0.13 s/Schritt): ≤ 5 min pro Lauf, zusammen ≲ 40 min bei J = 4 |

## Befehle

```
python lab/experiments/EXP-046-dihedral-steering/make_split.py --seed I --arm {F,G}        # reine Rechnung, erledigt
python lab/experiments/EXP-046-dihedral-steering/make_split.py --seed I --arm R --eps 0    # erledigt
sh lab/experiments/EXP-046-dihedral-steering/queue.sh J        # Selbsttest, Smoke, 20 Läufe, Auswertung, dann R-Arme
python lab/tools/guarded_run.py -- python lab/experiments/EXP-046-dihedral-steering/analyze.py
```

Die Queue braucht `GPU-001` = PASS (Regel 16d) und stoppt bei Ablehnung des Wächters (rc 3).

## Literatur (Suche 2026-09-26, 19:40 Berlin)

Suchbegriffe: „grokking group composition which irreducible representations learned training data distribution“,
„toy model of universality irreps learned seeds dihedral S5“, „non-abelian group multiplication training set sampling
biases which representation is learned“.
- Chughtai et al. 2023, *A Toy Model of Universality* (https://arxiv.org/abs/2302.03025): Netze lernen Gruppen über
  Darstellungen (GCR), **welche** Irreps variiert über Seeds. Ursache nicht untersucht.
- He et al. 2026, *Neural Networks Provably Learn Spectral Representations for Group Composition*
  (https://arxiv.org/abs/2606.02993): Theorie, Auswahl durch zufällige Init; unvollständige/ungleichmäßige Trainingsmengen nicht betrachtet (laut Zusammenfassung).
- Marchetti et al. 2026, *Sequential Group Composition* (https://arxiv.org/abs/2602.03655): Reihenfolge der gelernten Irreps
  folgt den „Fourier-Statistiken der Kodierung“ (Eingabekodierung, nicht Trainingsauswahl). Nächstverwandt.
- Keine Arbeit gefunden, die über die **Auswahl der Trainingspaare** steuert, welche Irreps einer nicht-abelschen Gruppe
  gelernt werden. Einordnung: #neu/kandidat, vorläufig („nach unserer Suche vom 2026-09-26 nicht gefunden“).

## Nachtrag b (Sitzung 13, 2026-09-26 20:07 Berlin, gemessen; vor jedem Lauf): unabhängige Prüfung, Einschränkung der Lesart

Codex war nicht verfügbar („out of credits“, `codex_review_s13_2026-09-26.txt`). Ein unabhängiger Claude-Subagent (frischer Kontext,
nur lesend, nur numpy) hat Code, Splits und Queue geprüft: **kein Blocker**; Gruppengesetz, Irrep-Basis, nicht-abelsches M0, Run-ID-Globs,
result.json-Schlüssel, Vorzeichentest, Shell-Logik bestätigt. Übernommen, **Urteilsregeln unverändert**:
- **(Hoch) Häufigkeits-Confound ohne eigene Kontrolle:** Auch hier liegen die a/b-Häufigkeiten in den Ziel-Irreps (Zielrang ≈ 8–10 von 29,
  Zufall 14; Ausgaben c ≈ 13). Ein Urteil *steuerbar* heißt deshalb nur „**der Split steuert**“; ob über die Paarstruktur oder die
  Häufigkeiten, entscheidet erst [[experiments/EXP-047-marginal-control/README|EXP-047]] (für Z₁₁₃) bzw. ein späterer D₅₉-Mischarm.
  Die Rechnung erster Ordnung (EXP-047 Nachtrag a) gilt für jede Gruppe und sagt: Häufigkeiten wirken im ersten Gradienten nicht.
- **(Mittel) Top-5 aus 29 ist grob** (Zufallsüberlappung 0.86 je Zelle): Zusätzlich wird Δ mit Top-3 und der Log-Leistungskontrast
  Δ_pow (wie [[experiments/EXP-048-intadd-steering/README|EXP-048]]) berichtet, **ausdrücklich nicht vorab festgelegt, nur beschreibend**.
- (Niedrig) Die Zufallsströme benachbarter Seeds überschneiden sich wie in EXP-016/043 (praktisch harmlos, formal nicht unabhängig);
  `--force` löscht alte Ergebnisse nicht vorab, und fertige Läufe werden ohne Schrittprüfung übersprungen (betrifft nur Handläufe).

## Nachtrag (Sitzung 13, 2026-09-26 20:20 Berlin, gemessen; vor jedem Lauf): nicht-endliche Läufe ungültig

Eine unabhängige Prüfung (Claude-Subagent, EXP-049) fand: Ein divergierter Lauf (NaN in W_E) wäre bisher als gültig gezählt worden und hätte still ein falsches K oder sogar das Urteil *widerspricht* mit p = 0 erzeugt (`one_sided_p` mit NaN gibt 0.0). `analyze.py` wertet einen Lauf mit nicht-endlichem Spektrum bzw. W_E jetzt als **ungültig** (zählt gegen die Mindestzahl gültiger Seeds). Urteilsregeln sonst unverändert.

*Ergänzung zu Nachtrag b (20:22 Berlin, gemessen; reine numpy-Rechnung auf den 30 Splits, vor jedem Lauf):* Die Identität Σ_c L_k(c) = Σ_t n(t) ρ_k(t) gilt auch in D₅₉ (im Code geprüft); der Häufigkeitsanteil fällt also auch hier aus dem ersten W_E-Gradienten heraus. Er macht 0.9 % der M0-Leistung aus (Arm R 0.8 %). Das zentrierte M0 hält die Ziele auf Rang 2.0 von 29 (roh 2.0; Häufigkeitsspektrum allein 7.3; Zufall 14; Arm R 13.5). **Erwartung erster Ordnung:** Die Steuerung in EXP-046 läuft, falls vorhanden, über die Paarstruktur. Das ist eine Vorhersage, kein Beleg; die empirische Trennung gibt es nur für Z₁₁₃ (EXP-047).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen (Regel 18c, Sitzung 13, 20:54 Berlin)

**Art:** Pilot/Exploration für Paket A (keine Bestätigung). Bestätigung nur im reservierten Block (Seeds 1000–1099, [[FINDINGS]] „Programm“) nach eingefrorenem Analysemanifest.
**Gesehen:** Ergebnisse von EXP-016 (Steuerung in Z₁₁₃) motivierten Konstruktion und Richtung von H46; die Zielmengen-/M0-Prüfung und das Häufigkeitsspektrum der 30 D₅₉-Splits wurden offline angesehen (führten zu Nachtrag b). Keine D₅₉-Läufe gesehen.

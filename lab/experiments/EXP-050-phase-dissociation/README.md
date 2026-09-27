---
id: EXP-050
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[BEFUND-split-mechanismus]]", "[[experiments/EXP-019-coherent-mask/README|EXP-019]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-050: Wählt der Transformer nach M0c oder nach M0? (Phasen-Dissoziation)

**Status:** abgeschlossen 2026-09-27 (Sitzung 20, GPU), Ergebnis unten. Ursprünglich: vorbereitet, nicht ausgeführt, ungetestet, nicht in einer Queue (Sitzung 13, 2026-09-26, außerhalb des Fensters).
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
| **H50a (M0c selektiert)** | D_i = Δ_pow,quadlm − Δ_pow,anti > 0 (**geändert vor jedem Lauf, Nachtrag a**; vorher sym − anti) |
| **H50b (M0 steuert trotzdem)** | Δ_pow,anti > 0 |
| **Primärgröße** | Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] je Modus (wie EXP-048/049; an EXP-016 kalibriert: 8.4) |
| **Test** | je einseitiger Vorzeichen-Permutationstest über die gültigen Seeds; **Holm über {a, b}** |
| **Gültig** | alle sechs Läufe eines Seeds `completed`, 2000 Schritte, cuda, p 113/add, Split-Hash = .npy, Spektren endlich; < 8 gültige Seeds: *nicht auswertbar* |
| **Urteil a** | *M0c selektiert*: D̄ > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *widerspricht*: D̄ ≤ 0 |
| **Urteil b** | *anti steuert trotzdem (M0-Anteil)*: Δ̄_anti > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *anti steuert nicht*: Δ̄_anti ≤ 0 |
| **Manipulationsprüfung (berichtet)** | Δ̄_pow,quadlm > 0 (quadlm muss steuern, sonst ist a nicht deutbar); sekundär D_sym = Δ_pow,sym − Δ_pow,anti (durch die Spiegelpaarzahl konfundiert), gen und Train-/Test-Genauigkeit je Modus |
| **Vorhersage erster Ordnung** | a ja, b nein (anti ≈ 0) |
| **Gegenhypothese** | Die Wahl folgt M0 (z. B. weil spätere Schritte mit nicht gleichverteilter Ausgabe oder die MLP-Nichtlinearität J_L ≠ J_R machen): D̄ ≈ 0, b ja |
| **Was die Deutung begrenzt** | Zwischenergebnis „a ja und b ja“: Kreuzterm verstärkt, M0 trägt auch. Nur Transformer; der Gegenversuch im MLP mit getrennten W_in-Hälften (Vorhersage dort umgekehrt: anti steuert, sym nicht stärker) ist ein Folgeversuch. sym hat auf den Zielen mehr M0c-Leistung als EXP-016 (0.270 vs. ≈ 0.19): Δ_pow,sym ist deshalb nicht direkt mit EXP-016 vergleichbar |
| **Budget** | 60 Läufe à 2000 Schritte auf der GPU (3 Modi × F/G × 10 Seeds), J parallel |

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

## Nachtrag a (Sitzung 13, 2026-09-26 20:32 Berlin, gemessen; **vor jedem Lauf**): Spiegelpaar-Confound, Kontrollmodus quadlm

Unabhängige Prüfung (Claude-Subagent, nur numpy; Codex ohne Guthaben): Herleitung, M0/M0c gegen die Referenzimplementierungen (Abweichung 0), alle README-Zahlen, Globs, Holm, Vorzeichentest und Shell bestätigt. **Hoch, übernommen:** Über alle k summiert ist der Kreuzterm durch die Zahl der **Spiegelpaare** festgelegt ((a, b) und (b, a) beide im Training; Kreuzterm-Summe = 2p·(2·Spiegelpaare + Diagonale)). sym hat 706, anti 420, Zufall 571 Spiegelpaare. Symmetrische Paare werden früher memoriert (He et al. 2026, https://arxiv.org/abs/2602.16849); sym gegen anti hätte also auch Lerntempo/Verstärkung verglichen, nicht nur die frequenzspezifische M0c-Auswahl. **Mittel, vermerkt:** anti neigt die Reihenfolge der Operanden (Anteil a > b minus a < b: −0.041 ± 0.049, bis −0.165).

**Neuer Kontrollmodus quadlm** (make_split.py): Viertelphase φ = π/4 − πkc/p (Kreuzterm auf den Zielen genau null → M0c = M0 dort; deterministische Phase → Token-Häufigkeiten auf Zufallsniveau wie bei sym/anti; Zufallsphasen wie in EXP-016 hätten Häufigkeitsrang 12.9 ergeben und wurden deshalb verworfen), danach Spiegelpaare durch Tausch (ein Glied eines Spiegelpaares raus, ein q-gewichtetes Paar ohne neuen Spiegel rein) **exakt** auf die Zahl des anti-Splits desselben Seeds und Arms gesenkt. Offline (20 Splits je Modus):

| Modus | Zielrang M0 | Zielrang M0c | Häufigkeitsrang | Anteil M0 | Anteil M0c | Spiegelpaare | Diagonale | Reihenfolge |
|---|---|---|---|---|---|---|---|---|
| quadlm | 2.0 | 2.0 | 25.7 | 0.192 | 0.195 | 420 | 53 | −0.028 |
| anti | 2.0 | 25.3 | 24.9 | 0.193 | 0.091 | 420 | 34 | −0.041 |
| sym | 2.0 | 2.0 | 25.4 | 0.190 | 0.270 | 706 | 55 | −0.003 |

**Primärvergleich jetzt quadlm gegen anti** (gleiches M0, gleiche Häufigkeiten, gleiche Spiegelpaarzahl; verschieden nur in M0c; verbleibend: 19 Diagonalpaare mehr in quadlm, leicht verschiedene Reihenfolge-Neigung). sym gegen anti nur noch sekundär. Die sym/anti-Splitdateien sind unverändert (nur die JSON-Metadaten um Spiegelpaare/Diagonale/Reihenfolge ergänzt). 60 statt 40 Läufe.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen (Regel 18c, Sitzung 13, 20:54 Berlin)

**Art:** Paket C (nicht aktiv), Exploration. Bestätigung nur im reservierten Block (Seeds 1000–1099, [[FINDINGS]] „Programm“) nach eingefrorenem Analysemanifest.
**Gesehen:** Sitzung-5-Messung am ersten Gradienten (M0c beschreibt ihn besser als M0; Transformer 0.77 gegen 0.57, MLP umgekehrt) und EXP-019 (post hoc richtungsgleich) motivierten die Hypothese; die Herleitung erster Ordnung entstand nachträglich zu diesen Messungen. Splits offline (sym/anti/quadlm, Spiegelpaare) angesehen; Nachtrag a folgte daraus. Keine Läufe der Seeds 180–189.

## Ergebnis (Sitzung 20, 2026-09-27, Läufe 03:35–03:40 Berlin, GPU)

Befehl: `python lab/tools/night_program.py --experiments GPU-001,EXP-050`; Log `lab/runner/logs/night3_exp050.log`, `lab/runner/logs/night_20260927T013514_874246Z/EXP-050_*`,
Zahlen `summary.json`. 60 Läufe, device cuda, Commits 2525efa/5e547d4 (dazwischen nur Dokumente).

| | Wert | Urteil (vorab, Holm über {a, b}) |
|---|---|---|
| Manipulationsprüfung quadlm | Δ̄_pow 7.88, p 0.00098 | quadlm steuert, a ist deutbar |
| **a** D = Δ_pow,quadlm − Δ_pow,anti | D̄ 6.51, 10/10, p 0.00098 | ***M0c selektiert (quadlm > anti)*** |
| **b** Δ_pow,anti | 1.36, 10/10, p 0.00098 | ***anti steuert trotzdem (M0-Anteil)*** |
| sekundär D_sym = sym − anti | 7.95 (p 0.00098); Δ_pow,sym 9.32 | (durch Spiegelpaarzahl konfundiert) |

- **Lesart (vorab als „Zwischenergebnis a ja und b ja“ benannt):** Der kohärente Kreuzterm (M0c) verstärkt die Steuerung stark, und das nicht kohärente M0 trägt auch.
  Die **Vorhersage erster Ordnung stimmt nur zur Hälfte**: a ja, aber b nicht nein. anti steuert, schwach (≈ 1/6 von quadlm) und durchgängig (10/10). Mögliche Ursachen laut
  Gegenhypothese: spätere Schritte mit nicht gleichverteilter Ausgabe oder die MLP-Nichtlinearität. Nicht getrennt.
- Folgeversuch (vorab genannt): MLP mit getrennten W_in-Hälften (Vorhersage dort umgekehrt). Pilot, 10 Seeds, nur Transformer.

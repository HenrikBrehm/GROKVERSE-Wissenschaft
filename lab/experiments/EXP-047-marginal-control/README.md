---
id: EXP-047
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[BEFUND-split-mechanismus]]", "[[experiments/EXP-046-dihedral-steering/README|EXP-046]]"]
---
# EXP-047: Steuern die Token-Häufigkeiten oder die Paarstruktur? (Kontrolle mit gleichen Randverteilungen)

**Status:** vorbereitet, **nicht ausgeführt, ungetestet** (Sitzung 12, 2026-09-26 ~20:15 Berlin, außerhalb des Fensters).
Festgelegt vor jedem Lauf. Zurück zu [[LAB]] · [[FINDINGS]].

## Bezug zu [[FINDINGS]] und Anlass

Zielt auf **K2** (Frequenzwahl über den Split steuerbar, [[experiments/EXP-016-engineered-split/README|EXP-016]]): Welcher Teil
des Splits wirkt? Anlass (Sitzung 12, Zyklus 3, reine Rechnung): Die konstruierten EXP-016-Splits heben die Zielfrequenzen nicht
nur im Masken-Spektrum M0 hervor (mittlerer Zielrang 2 von 56), sondern auch im DFT-Spektrum der **bloßen Token-Häufigkeiten**
von a und b (mittlerer Zielrang 12.2, Zufall 27.5), obwohl die Häufigkeiten insgesamt nicht ungleicher sind als bei einem
Zufallssplit (Variationskoeffizient 0.14). Bisher geprüft war nur die Höhe (CV, EXP-018/022) und, post hoc an *Zufallssplits*, dass
das Häufigkeitsspektrum K nicht vorhersagt (EXP-015). Für die konstruierten Splits ist die Alternativerklärung „das Netz folgt den
Häufigkeiten, nicht der Paarstruktur“ **offen**. Dieselbe Verzerrung tritt bei D₅₉ auf ([[experiments/EXP-046-dihedral-steering/README|EXP-046]]:
Zielrang 7.8 von 29, Zufall 14).

## Aufbau

- **eng:** EXP-016-Konstruktion (ε = 2, 3831 Paare, add mod 113), neue Seeds 150–159, Arme F und G (disjunkte Zielmengen).
- **shuf:** derselbe Split, aber die b-Werte zufällig über die Paare permutiert (doppelte Paare durch zufällige Tausche repariert).
  Die Häufigkeiten von a und b bleiben **exakt** gleich (im Code geprüft, fail-closed), die Paarstruktur ist zerstört.
  **Offline gemessen (20:12, reine Rechnung):** eng: M0-Zielrang 2.0, M0-Zielanteil 0.192, Häufigkeits-Zielrang 11.6;
  shuf: M0-Zielrang 24.4 (Zufall 27.5), M0-Zielanteil 0.091 (Zufall 0.089), Häufigkeits-Zielrang 11.6 (identisch).
- Zufallsströme über `SeedSequence([47001, seed, arm, Zweck])` (EXP-016/043 teilen Ströme zwischen Nachbar-Seeds; hier vermieden).
- Alle 40 Läufe (10 Seeds × {eng, shuf} × {F, G}) 2000 Schritte auf der **GPU**, Transformer der Studie, K = Top-5 von W_E bei 2000.
  Hinweis: `freq_ban.py` beschriftet diese Läufe als `EXP-016_…` (Standard für `--split-file`); maßgeblich sind Ordner `EXP-047/raw` und Split-Name.

| | |
|---|---|
| **Fragestellung** | Wirkt die Datensteuerung über die Paarstruktur (M0) oder über die Token-Häufigkeiten? |
| **H47a** (Alternativerklärung) | Häufigkeiten allein steuern: Δ̄_shuf > 0 |
| **H47b** (Paarstruktur) | Die Paarstruktur trägt über die Häufigkeiten hinaus: D_i = Δ_eng,i − Δ_shuf,i, D̄ > 0 |
| **Primärgröße** | Δ_kind = ov(K_F, F) + ov(K_G, G) − ov(K_F, G) − ov(K_G, F), je Seed |
| **Test** | je einseitiger Vorzeichen-Permutationstest über die gültigen Seeds; **Holm über {a, b}** |
| **Gültig** | alle vier Läufe eines Seeds `completed`, ≥ 2000 Schritte, cuda, Split-Hash = Inhalt der .npy; < 8 gültige Seeds → *nicht auswertbar* |
| **Urteil a** | *Häufigkeiten steuern mit*: Δ̄_shuf > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *keine Steuerung über Häufigkeiten*: Δ̄_shuf ≤ 0 |
| **Urteil b** | *Paarstruktur trägt über die Häufigkeiten hinaus*: D̄ > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *widerspricht*: D̄ ≤ 0 |
| **Manipulationsprüfung (berichtet)** | Δ̄_eng > 0 (Replikation von EXP-016 auf der GPU an frischen Seeds); gen-Schritt und Test-Genauigkeit je Arm |
| **Erwartung** | Nach EXP-015 (Häufigkeitsspektrum sagt K nicht voraus) b ja, a nein |
| **Was dagegen spräche** | Δ̄_shuf ≈ Δ̄_eng: dann ist K2 im Kern ein Häufigkeitseffekt, und der M0-Mechanismus ([[BEFUND-split-mechanismus]]) ist falsch zugeordnet |
| **Grenzen** | Das Mischen ändert die Häufigkeiten der Ausgaben c; deren Zielrang liegt aber in beiden Armen auf Zufallsniveau (gemessen 20:17: eng 28.1, shuf 27.4, Zufall 27.5), c-Häufigkeiten sind also keine Steuergröße in diesem Vergleich. Nur add mod 113 und ein Modell |
| **Budget** | 40 Läufe × 2000 Schritte auf der GPU, J parallel; in `queue_gpu_s11.sh` nach EXP-046 |

## Befehle

```
python lab/experiments/EXP-047-marginal-control/make_split.py --seed I          # reine Rechnung, erledigt (150–159)
sh lab/experiments/EXP-047-marginal-control/queue.sh J                          # Selbsttest, 40 Läufe, Auswertung
python lab/tools/guarded_run.py -- python lab/experiments/EXP-047-marginal-control/analyze.py
```

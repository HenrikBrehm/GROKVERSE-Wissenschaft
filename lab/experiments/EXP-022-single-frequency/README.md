---
id: EXP-022
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-018-split-speed/README|EXP-018]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-022: Kann die Datenauswahl eine Ein-Frequenz-Lösung erzwingen?

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 06:43 Berlin (Sitzung 5), bevor ein Lauf
existierte. Code: `make_splits.py` (Splits erzeugt), `analyze.py`, `queue.sh`; Trainer unverändert (`--split-file`,
`--test-file` wie EXP-018).

## Idee

Netze für modulare Addition nutzen 3–8 Frequenzen, obwohl eine genügen würde. He et al. 2026
(https://arxiv.org/abs/2602.16849) erklären das mit Robustheit: Mehrere Frequenzen und Phasensymmetrie erlauben eine
„Mehrheitsabstimmung“, die das Rauschen einzelner Neuronen ausgleicht. EXP-016 zeigt: Die Datenauswahl gibt vor,
**welche** Frequenzen gelernt werden. Hier die Frage, ob sie auch vorgeben kann, **wie viele**. Suche 2026-09-26
(„force neural network to learn single Fourier frequency modular arithmetic minimal circuit fewer frequencies
generalization data intervention“, „modular addition network number of key frequencies why multiple frequencies single
frequency solution sufficient margin robustness grokking“): kein Eingriff gefunden, der eine Ein-Frequenz-Lösung
erzwingt (vorläufig).

## Design

Seeds 40–44 (frisch). Pro Seed eine gemeinsame Testmenge T* (20 %) und drei Trainingsmengen à 3831 Paare aus dem Rest:
- **S1**: eine Zielfrequenz f1 (zufällig aus `target_set(i)`), ε = 0.9 **ohne Clipping**. Mit ε = 2 erzeugte die
  Untergrenze 0.05 Harmonische 2k, 3k im Masken-Spektrum; das wurde vor jedem Lauf geändert. M0-Top-1-Anteil 0.136–0.158.
- **S5**: fünf Ziele wie EXP-018 Arm E (ε = 2), gleiche Ziehungsschlüssel wie S1. Top-5-Anteil 0.177–0.188.
- **R**: gleichverteilt. Top-1-Anteil ≈ 0.02.
Alle Läufe: `--steps 8000 --stop-after-gen 2000` (Ende bei gen + 2000 oder 8000), Messung am letzten Spektrum.

| | |
|---|---|
| **Fragestellung** | Konzentriert sich W_E unter S1 auf weniger Frequenzen als unter S5, bis hin zu einer Ein-Frequenz-Lösung? |
| **Messgröße** | n_eff = (Σ_k P_k)² / Σ_k P_k² über k = 1..56 des W_E-Leistungsspektrums am Laufende (Partizipationsverhältnis) |
| **H22** | n_eff(S1) < n_eff(S5) |
| **Test** | Vorzeichentest über die 5 Seeds, einseitig; *bestätigt* nur bei 5/5 (p = 1/32) |
| **Gültig** | alle drei Läufe eines Seeds `completed`, Hashes passen; ohne Kreuzung nur, wenn bis 8000 gelaufen |
| **Sekundär** | Top-1-Anteil von W_E; ist f1 die stärkste Frequenz?; gen auf T* (zensiert bei 8000) und End-Test-Acc je Arm; n_eff(R); Leistungsanteil auf f1 und fold(2·f1) |
| **Konkurrierende Vorhersagen** | (a) *Daten dominieren*: n_eff(S1) ≈ 1–2, S1 generalisiert. (b) *Robustheit erzwingt Vielfalt* (He et al.): n_eff(S1) ≈ n_eff(S5), weitere Frequenzen kommen aus Init oder Dynamik. (c) *Ein-Frequenz-Lösung ohne Robustheit*: S1 konzentriert sich, erreicht auf T* aber 95 % spät oder gar nicht |
| **Was gegen H22 spräche** | n_eff(S1) ≥ n_eff(S5) in mindestens einem Seed |
| **Grenzen** | S1 und S5 unterscheiden sich auch in ε (0.9 gegen 2) und damit in der Ungleichverteilung der Paare; nur Transformer, p = 113 |
| **Budget** | 15 Läufe à ≤ 8000 Schritte (≤ 17 min), erwartet eher 4–10 min: 1.5–4 h |

## Befehle

```
python lab/experiments/EXP-022-single-frequency/make_splits.py
sh lab/experiments/EXP-022-single-frequency/queue.sh
python lab/experiments/EXP-022-single-frequency/analyze.py
```

## Nachtrag a (2026-09-26 06:51 Berlin, nach Codex-Review, **vor jedem Lauf**): neues Design

Codex (`codex_review_2026-09-26.txt`, „needs-attention“), 5 Befunde, selbst geprüft, alle **übernommen**. Die Tabelle
oben gilt nur noch, wo sie hier nicht ersetzt wird.
1. [high] *n_eff von W_E misst keine genutzten Frequenzen, und Modelle wurden nicht gespeichert.* → Alle Läufe mit
   `--save-model`. **Primär funktional:** K_func = Regel `nanda` der Studie (Fourier-Norm von W_L = W_out·W_U, Schwelle
   0.25 des Maximums) am gespeicherten Modell. Dazu Ablationen in W_E: nur {DC, f1} behalten („keep_f1“) und f1 entfernen.
   n_eff nur noch beschreibend. Geprüft am Studienmodell Seed 0 (`check_functional.py`): `nanda` reproduziert die
   gespeicherte Menge exakt; nur die Schlüsselfrequenzen behalten → Test-Acc 0.995; nur eine behalten → 0.054.
2. [high] *S1 und S5 unterscheiden sich in mehr als der Zahl der Ziele* (ε, Clipping 7 % bei S5, Gewichtsverteilung).
   → **Neue Primärkontrolle D1:** die exakten Gewichte von S1 innerhalb jeder Antidiagonale permutiert, gleiche
   Ziehungsschlüssel (wie EXP-018 Arm D). Gemessen: Rest-Häufigkeiten (CV von c 0.12–0.14) und Anteil vertauschter Paare
   (0.28–0.31) wie S1; Top-1-Anteil 0.021–0.022 statt 0.136–0.158. S5 bleibt als Sekundärvergleich (Vorhersage b).
   R entfällt (EXP-018 deckt R ab).
3. [high] *Messzeitpunkt hing von der Behandlung ab.* → Alle Arme laufen **genau 6000 Schritte** ohne Frühstopp
   (`--steps 6000 --stop-after-gen 8000`), Messung bei 6000.
4. [high] *Winzige Unterschiede hätten „bestätigt“ ergeben, ohne Lernerfolg.* → **Gemeinsames Erfolgskriterium** pro
   Seed („Ein-Frequenz-Lösung“): K_func(S1) = {f1} **und** Train-Acc ≥ 0.99 **und** T*-Acc ≥ 0.95 **und** keep_f1 ≥ 0.90.
   **Entscheidung:** *erzwingbar*, wenn ≥ 4/5 Seeds den Erfolg zeigen, D1 in keinem Seed nur eine Frequenz hat und
   |K_func(S1)| < |K_func(D1)| in 5/5; *teilweise*, wenn nur Letzteres gilt; sonst *nicht erzwingbar*. Vorhersage (b)
   („Vielfalt bleibt“) gilt als gestützt, wenn |K_func(S1)| in ≥ 4/5 Seeds höchstens 1 von |K_func(S5)| abweicht.
   Robustheit gegen Rauschen (He et al.) bleibt ungetestet; das wäre ein eigener Nachtrag.
5. [medium] *Protokollprüfung zu schwach.* → `analyze.py` prüft exp_id, condition, max_steps, steps_completed,
   stop_after_generalization, Taktung, letzten Spektrumsschritt und das Modell.
Budget neu: 15 Läufe × 6000 Schritte × 0.13 s ≈ 13 min, zusammen ≈ 3.3 h.

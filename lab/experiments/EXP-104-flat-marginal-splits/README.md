---
id: EXP-104
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-104 (Exploration, N53): Steuert ein Split mit exakt flachen Häufigkeiten von a, b und c, und blockiert seine Symmetrie das Grokking?

Zurück: [[LAB]] · [[FINDINGS]] (K2, Mechanismus „Paarstruktur, nicht Häufigkeiten“; Kontrolle für die Sprachmodell-Leiter, Regel 20e) · [[NOVEL_DIRECTIONS]] N53 · Vorgänger [[experiments/EXP-047-marginal-control/README|EXP-047]] (a/b-Häufigkeiten gleich, Paare gemischt) · [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]]

**Stand:** vorbereitet (Sitzung 45, 2026-09-28, 22:03 Berlin gemessen), ungetestet. **Startet erst nach L0** als GPU-Füllarbeit in freien Plätzen (Regel 20: L0 hat Vorrang; kein Mechanismus-Detailversuch im Sinn von 20a, sondern Vorbereitung der Leiter-Kontrolle). 12 Läufe, 2 Seeds: **Exploration**, kein Urteil über K2.

**Bezug zu FINDINGS:** K2 sagt, die Auswahl der Paare steuert die Frequenzen. EXP-047 zeigte im Klassifikationsmodell, dass a/b-Häufigkeiten allein kaum steuern. In einem Sprachmodell (gebundene Embeddings, Verlust auf allen Positionen) können Token-Häufigkeiten W_E aber direkt prägen. Die P1-Splits tragen die Ziele auch in count(a), count(b) (0.165, 0.225). Ein Split ohne jedes Häufigkeitssignal ist deshalb die saubere Kontrolle für die Leiter.

## Aufbau

- Split S(1, D) = {(a, b): a − b ∈ D}, |D| = 34, |S| = 3842 (P1: 3831); jedes a, b und c = a + b kommt genau 34-mal vor. D konzentriert das Maskenspektrum auf fünf Ziele (Zielanteil 0.65–0.74).
- S ist unter allen Verschiebungen (a, b) → (a + s, b + s) invariant. Tauschzüge (m = 10, 500) brechen diese Invarianz exakt und halten die Häufigkeiten flach; bei m = 500 fällt der Zielanteil auf 0.27–0.30.
- Seeds 3850, 3851 (frei geprüft); Arme F/G mit disjunkten Zielen, gleiche Init je Seed; m ∈ {0, 10, 500}; add 113, `freq_ban.py` Standardaufbau, GPU, 8000 Schritte (Stopp 2000 nach Generalisierung), Spektren bei 250 und 2000; Test = Komplement.
- Messgrößen: Δ_pow bei 2000 (P1-Definition), Generalisierungsschritt, Endgenauigkeit.

## Lesarten (vorab, im Docstring von `analyze.py`)

- m = 0 scheitert, m = 10 generalisiert (beide Seeds) → „exakte Verschiebungsinvarianz blockiert die Generalisierung“ (Kandidat; vgl. Tomàs Bernal et al. 2026 für RFM). m = 10 scheitert, m = 500 generalisiert → „näherungsweise Invarianz blockiert“. Alles generalisiert → „die Symmetrie blockiert den Transformer nicht“. Auch m = 500 scheitert → „flache Splits groken hier nicht“, als Leiter-Kontrolle vorerst nicht brauchbar.
- Δ_pow > 1 in beiden Seeds bei einem m → „steuert bei flachen Häufigkeiten“ bei diesem m.
- **Gegen die Hypothese spräche:** Δ_pow ≤ 1 bei flachen Häufigkeiten trotz hohem Maskenanteil, dann trüge das Häufigkeitssignal einen Teil der Steuerung, entgegen der Lesart von EXP-047.

## Befehle (ab Fenster, nach L0)

```
python lab/experiments/EXP-104-flat-marginal-splits/design.py --splits      # erledigt (Sitzung 45), überschreibt nie
python lab/experiments/EXP-104-flat-marginal-splits/design.py --jobs > lab/experiments/EXP-104-flat-marginal-splits/jobs.txt   # erledigt
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-104-flat-marginal-splits/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-104-flat-marginal-splits/jobs.txt --workers 2   # nur freie GPU-Plätze, Summe ≤ 10
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-104-flat-marginal-splits/analyze.py
```

Erwartete Dauer: wie P1-Läufe bis 2000 Schritte plus Generalisierungsphase; nicht gemessen. Laufen alle 12 ohne Generalisierung bis 8000, ≈ 4× ein P1-Lauf je Job.

**Bereits gesehene Daten:** keine Läufe mit diesen Splits oder Seeds. Die Konstruktion stammt aus reiner Rechnung (`lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_*_s45.py`).

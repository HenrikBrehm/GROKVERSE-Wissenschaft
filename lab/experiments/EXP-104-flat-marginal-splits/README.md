---
id: EXP-104
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, neu/kandidat, befund/positiv]
---
# EXP-104 (Exploration, N53): Steuert ein Split mit exakt flachen Häufigkeiten von a, b und c, und blockiert seine Symmetrie das Grokking?

Zurück: [[LAB]] · [[FINDINGS]] (K2, Mechanismus „Paarstruktur, nicht Häufigkeiten“; Kontrolle für die Sprachmodell-Leiter, Regel 20e) · [[NOVEL_DIRECTIONS]] N53 · Vorgänger [[experiments/EXP-047-marginal-control/README|EXP-047]] (a/b-Häufigkeiten gleich, Paare gemischt) · [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]]

**Stand:** vorbereitet (Sitzung 45, 2026-09-28, 22:03 Berlin gemessen), ungetestet. **Startet erst nach L0** als GPU-Füllarbeit in freien Plätzen (Regel 20: L0 hat Vorrang; kein Mechanismus-Detailversuch im Sinn von 20a, sondern Vorbereitung der Leiter-Kontrolle). 12 Läufe, 2 Seeds: **Exploration**, kein Urteil über K2.

**Bezug zu FINDINGS:** K2 sagt, die Auswahl der Paare steuert die Frequenzen. EXP-047 zeigte im Klassifikationsmodell, dass a/b-Häufigkeiten allein kaum steuern. In einem Sprachmodell (gebundene Embeddings, Verlust auf allen Positionen) können Token-Häufigkeiten W_E aber direkt prägen. Die P1-Splits tragen die Ziele auch in count(a), count(b) (0.165, 0.225). Ein Split ohne jedes Häufigkeitssignal ist deshalb die saubere Kontrolle für die Leiter.

## Aufbau

- Split S(1, D) = {(a, b): a − b ∈ D}, |D| = 34, |S| = 3842 (P1: 3831); jedes a, b und c = a + b kommt genau 34-mal vor. D konzentriert das Maskenspektrum auf fünf Ziele (Zielanteil 0.65–0.74).
- S ist unter allen Verschiebungen (a, b) → (a + s, b + s) invariant. Tauschzüge (m = 10, 500) brechen diese Invarianz exakt und halten die Häufigkeiten flach; bei m = 500 fällt der Zielanteil auf 0.27–0.30.
- Seeds 3850, 3851 (frei geprüft); Arme F/G mit disjunkten Zielen, gleiche Init je Seed; m ∈ {0, 10, 500}; add 113, `freq_ban.py` Standardaufbau, GPU, 8000 Schritte (Stopp 2000 nach Generalisierung), Spektren bei 250 und 2000; gemeinsame Testmenge je Seed (Paare außerhalb aller sechs Splits: 4595 bzw. 4693), `--train-frac 0.3009` (freq_ban prüft die Splitgröße: round(0.3009·113²) = 3842).
- Messgrößen: Δ_pow bei 2000 (P1-Definition), Generalisierungsschritt, Endgenauigkeit.

## Lesarten (vorab, im Docstring von `analyze.py`)

- m = 0 scheitert, m = 10 generalisiert (beide Seeds) → „exakte Verschiebungsinvarianz blockiert die Generalisierung“ (Kandidat; vgl. Tomàs Bernal et al. 2026 für RFM). m = 10 scheitert, m = 500 generalisiert → „näherungsweise Invarianz blockiert“. Alles generalisiert → „die Symmetrie blockiert den Transformer nicht“. Auch m = 500 scheitert → „flache Splits groken hier nicht“, als Leiter-Kontrolle vorerst nicht brauchbar.
- Δ_pow > 1 in beiden Seeds bei einem m → „steuert bei flachen Häufigkeiten“ bei diesem m.
- ~~Gegen die Hypothese spräche: Δ_pow ≤ 1 …~~ **gestrichen nach der Prüfung vor dem Lauf:** ohne gleich starken, nicht flachen Vergleichsarm ist Δ_pow ≤ 1 nicht dem fehlenden Häufigkeitssignal zuzuordnen (Symmetrie, fehlende Generalisierung). Δ_pow wird je m berichtet und nie mit P1 verglichen (Maskenanteil 0.65–0.74 gegen 0.17–0.19).
- Gemischte Zellen (ein Arm generalisiert, der andere nicht) oder uneinige Seeds → „keine Lesart“; Generalisierungsschritte je Arm immer berichten.

## Befehle (ab Fenster, nach L0)

```
python lab/experiments/EXP-104-flat-marginal-splits/design.py --splits      # erledigt (Sitzung 45), überschreibt nie
python lab/experiments/EXP-104-flat-marginal-splits/design.py --test        # erledigt
python lab/experiments/EXP-104-flat-marginal-splits/design.py --jobs > lab/experiments/EXP-104-flat-marginal-splits/jobs.txt   # erledigt
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-104-flat-marginal-splits/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-104-flat-marginal-splits/jobs.txt --workers 2   # nur freie GPU-Plätze, Summe ≤ 10
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-104-flat-marginal-splits/analyze.py
```

Erwartete Dauer: wie P1-Läufe bis 2000 Schritte plus Generalisierungsphase; nicht gemessen. Laufen alle 12 ohne Generalisierung bis 8000, ≈ 4× ein P1-Lauf je Job.

**Bereits gesehene Daten:** keine Läufe mit diesen Splits oder Seeds. Die Konstruktion stammt aus reiner Rechnung (`lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_*_s45.py`).

**Prüfung vor dem Lauf (Sitzung 45, unabhängiger Claude-Agent, nur lesend; selbst im Code nachgesehen):** 2 Blocker behoben: (1) `freq_ban.py:524-527` verlangt round(train_frac·p²) = 3831 Paare, die flachen Splits haben 3842 → `--train-frac 0.3009`; (2) das Suchmuster der Auswertung hätte keinen Lauf gefunden (Name `EXP-018_…_tf0.3009_devcuda`) → exakter Name. 3 Major übernommen (gemeinsame Testmenge, vollständige Lesarten, „dagegen“-Lesart gestrichen). Minor: Anteile je Ziel werden berichtet (s3850 G: Ziel 3 nur 0.031, 25 und 50 dominieren und sind harmonisch verwandt); der json-Schlüssel `m0_target_share` meint das Maskenspektrum M0, nicht „m = 0“. Bestätigt: Splits exakt flach, ohne Duplikate, F/G disjunkt, Tauschzüge ≤ 3m Paare, nach 10 Zügen nur noch die Identität als Verschiebungssymmetrie (beste Überlappung einer Verschiebung aber noch ≈ 98.5 %), `spectra.npy` ist für add 113 dieselbe Basis wie P1 (Abweichung 2.5·10⁻¹⁵).

## Ergebnis (Sitzung 48, 2026-09-29, 07:04 Berlin gemessen; 12/12 Läufe, 2 Seeds, Exploration; `summary.json`; nicht nachgerechnet)

| Seed | m | F gen / Test am Ende | G gen / Test am Ende | Δ_pow (2000) | Zelle |
|---|---|---|---|---|---|
| 3850 | 0 | – / 0.58 | – / 0.87 | 10.10 | scheitert |
| 3850 | 10 | – / 0.63 | – / 0.86 | 9.78 | scheitert |
| 3850 | 500 | 725 / 1.00 | 350 / 1.00 | 6.02 | generalisiert |
| 3851 | 0 | – / 0.39 | 850 / 0.97 | 7.05 | gemischt |
| 3851 | 10 | – / 0.42 | 1100 / 0.98 | 7.22 | gemischt |
| 3851 | 500 | 2400 / 1.00 | 525 / 1.00 | 6.06 | generalisiert |

**Lesarten (vorab):** (a) *Steuerung:* Δ_pow > 1 in beiden Seeds bei **jedem** m → „steuert bei flachen Häufigkeiten“ (m = 0, 10, 500). Die Steuerung braucht also kein Häufigkeitssignal von a, b oder c; die Paarstruktur allein reicht (2 Seeds). (b) *Symmetrie:* m = 0 und m = 10: Seeds uneinig (3850 scheitert, 3851 gemischt) → „keine Lesart“; m = 500 generalisiert in beiden Seeds. Beschreibend: Bis 8000 Schritte generalisierten 1/8 Läufe mit m ≤ 10 gegen 4/4 mit m = 500; das passt zu „(nahezu) verschiebungsinvariante Splits bremsen oder blockieren das Grokking“ (vgl. Tomàs Bernal et al. 2026 für RFM), ist aber mit 2 Seeds keine Aussage.
**Folge für [[experiments/EXP-105-lm-ladder-stage2/README|EXP-105]]:** Nach der vorab festgelegten Regel (flache Splits nur, wenn m = 10 in beiden Seeds generalisiert) nutzt der Stufe-2-Pilot die P1-Splits (EXP-102, Seeds 3800/3801) mit dem Vermerk, dass dort auch die Häufigkeiten die Ziele tragen. Kandidat für später: flache Splits mit m = 500 (generalisieren und steuern, Δ_pow ≈ 6) als Häufigkeitskontrolle.

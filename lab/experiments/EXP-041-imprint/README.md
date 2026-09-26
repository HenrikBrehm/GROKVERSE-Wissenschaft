---
id: EXP-041
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-041: Prägt ein kurzer Vorlauf die Frequenzwahl, auch gegen einen Zufallssplit, und in beide Richtungen?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Grundlage [[experiments/EXP-020-data-switch/README|EXP-020]] (Festlegung nach
(25, 50] Schritten, beide Splits konstruiert), [[experiments/EXP-016-engineered-split/README|EXP-016]] (konstruierte Splits geben
die Frequenzen vor), Splits aus [[experiments/EXP-018-split-speed/README|EXP-018]] · Idee [[NOVEL_DIRECTIONS]] N19.

## Anlass

EXP-020 hat nur konstruiert → konstruiert geprüft. Zwei offene Fragen: (a) Hält die Prägung durch einen konstruierten Split E
auch, wenn danach ganz gewöhnlich auf einem **Zufallssplit** R trainiert wird (Anwendung: die Frequenzen eines sonst normal
trainierten Netzes per 150-Schritte-Vorlauf „programmieren“)? (b) Prägt ein spektral **schwacher** Zufallssplit genauso fest
(R → E), oder überschreibt ein stark konzentrierter Split eine schwache Festlegung? (b) ist offen: Das Masken-Spektrum von R hat
in den Top-5 nur ≈ 10 % der Leistung, E ≈ 18 % (EXP-018).

## Versuch (vorab festgelegt 2026-09-26, Sitzung 10, vor jedem EXP-041-Lauf)

| Punkt | Festlegung |
|---|---|
| **Splits** | EXP-018, Seeds 20–25: E (konstruiert, Ziele = `targets`), R (zufällig), je 3831 Paare, gemeinsame Testmenge (2554) |
| **Läufe je Seed** | nur R, nur E (je 2000 Schritte); E → R bei t = 150; R → E bei t = 150; R → E bei t = 50 (jeweils + 2000 Schritte). Init = Seed, full batch, lr konstant |
| **Maß** | K = Top-5 von W_E am Ende. Ex = Ziele(E) ∪ fold(2 · Ziele(E)), Rx = K_R ∪ fold(2 · K_R) (K_R = „nur R“ derselben Init), gemeinsame ausgenommen; d = |K ∩ Ex| − |K ∩ Rx| |
| **Gültig** | alle 5 Läufe vollständig (Schritte, Split-, Test-, Wechsel-Hashes), gleiche Init-Prüfsumme, d(nur E) > 0 > d(nur R) |
| **P41a** | E → R @150 **gehalten**, wenn d > 0 |
| **P41b** | R → E @150 **gehalten**, wenn d < 0 (die Wahl bleibt bei R) |
| **Urteil (je P41a, P41b)** | < 5 gültige Seeds → *nicht auswertbar*; einseitiger Vorzeichentest „gehalten“ p < 0.05 → ***geprägt***; „umgeschlagen“ (Gegenvorzeichen) p < 0.05 → ***überschrieben***; sonst ***gemischt*** (d = 0 zählt für keine Seite) |
| **Sekundär (beschreibend)** | R → E @50; Test-Acc aller Läufe (generalisiert das geprägte Netz?) |
| **Erwartung** | P41a *geprägt* (EXP-020: nach 150 Schritten hielt F gegen G in 5/5). P41b offen; eine Asymmetrie (R geprägt schwächer) würde heißen, dass die Festlegung von der Spektralstärke des Vorlauf-Splits abhängt |
| **Was gegen P41a spräche** | E → R endet auf R-Frequenzen: Die Festlegung aus EXP-020 wäre ein Effekt zweier konstruierter Splits |
| **Grenzen** | K_R eines Zufallssplits wird zum Teil von der Init bestimmt (EXP-014/036); 2000 Schritte nach dem Wechsel liegen um die Generalisierung, nicht lange danach; eine Architektur |
| **Budget** | 5 Läufe × ≈ 4.5 min ≈ 23 min je Seed, 6 Seeds ≈ 2.3 h; Queue beginnt mit dem Selbsttest (fail-closed) |

**Neuheit (Suche 2026-09-26 18:05):** „short curriculum prefix at start of training determines learned Fourier frequencies modular
arithmetic imprint early data then random data“. Nächstverwandt: **LeDoux 2026, „The Order Is The Message“**
(https://arxiv.org/abs/2603.25047): Die **Reihenfolge** der Minibatches über einer festen Trainingsmenge bestimmt die gelernte
Grundfrequenz (Pre-LN-Transformer, AdamW, p = 9973); laut HTML-Volltext **kein** Wechsel mitten im Training, keine Analyse,
wann die Wahl unumkehrbar wird, keine Lernraten-/Init-Abhängigkeit, keine Rolle der Zusammensetzung der Trainingsmenge. Die
hier gestellte Frage (Prägung durch einen Vorlauf auf einer anderen Trainingsmenge, in beide Richtungen): **nicht gefunden**
(vorläufig).

## Status

Vorab festgelegt, Code geschrieben, **ungetestet** (Fenster geschlossen; Selbsttest am Queue-Anfang, fail-closed).
Nicht in `queue_s10.sh` (die ist lang genug); Kandidat für die nächste Queue nach EXP-040.

## Reproduktion

```
sh lab/experiments/EXP-041-imprint/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-041-imprint/analyze.py
```

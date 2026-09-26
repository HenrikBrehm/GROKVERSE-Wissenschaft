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

## Nachtrag a (2026-09-26, Sitzung 10, nach Codex-Review `codex_review_2026-09-26.txt`, vor jedem EXP-041-Lauf): gilt allein, wo abweichend

Codex: needs-attention, 3 × hoch, 1 × mittel, alle übernommen.
1. **Maß und Gültigkeit waren zirkulär und asymmetrisch** (Ex aus den Split-Zielen, Rx aus dem Ergebnis „nur R“; d(nur R) ≤ 0
   galt per Konstruktion). **Neu, symmetrisch:** Ex = K_E ∪ fold(2 K_E), Rx = K_R ∪ fold(2 K_R), beide aus den reinen Läufen
   derselben Init (Top-5 bei Schritt 2000), gemeinsame ausgenommen. Gültig: alle Läufe bestehen den Lader, gleiche Init/Konfig,
   und beide Referenzen behalten ≥ 3 exklusive Frequenzen (kein richtungsabhängiges Ergebnis-Gate).
2. **Richtung des Vorlaufs am Wechsel nicht geprüft, Uhr nicht angeglichen.** **Neu:** Die reinen Läufe laufen 2150 Schritte,
   mit Spektren auch bei 50 und 150: K bei 2000 (gleiche Datenmenge nach dem Wechsel) für das Maß, K bei 2150 (gleiche
   Gesamtschrittzahl) und die Richtung des Vorlaufs bei Schritt 150 beschreibend. Die Aussage gilt für die gewählte Schätzgröße
   (2000 Schritte nach dem Wechsel gegen 2000 Schritte rein).
3. **Zwei entgegengesetzte einseitige Tests hielten α = 0.05 nicht.** **Neu:** P41a konfirmatorisch einseitig („gehalten“),
   P41b zweiseitig; je α = 0.025 (Bonferroni über beide). **10 Seeds (20–29)**, mindestens 8 gültige; bei m = 10 braucht P41a
   9/10 (p = 0.011), P41b 9/10 in eine Richtung. P41a sonst *nicht gezeigt*; P41b sonst *gemischt*. R → E bei t = 50 entfällt
   (Budget).
4. **Lader nicht fail-closed genug.** **Neu:** prüft run_id, Bedingung, m = 5, max_steps, Schritte, Stop-Regel, alle
   Eingriffs-Flags (Warmup, lr-Skala, Init-Skala, Wechselspiel, Rücksetzen), Frequenzliste (5 verschiedene ganze Zahlen in 1..56),
   Split-/Test-/Wechsel-Hashes, Konfiguration und Init über alle Läufe eines Seeds.
Budget neu: 4 Läufe × ≈ 4.6 min ≈ 19 min je Seed, 10 Seeds ≈ 3.1 h. Code nach dem Nachtrag **ungetestet** (Selbsttest am
Queue-Anfang, fail-closed).

**Erwartung aus H42 (N22), 18:27, vor jedem Lauf, ändert keine Regel:** Für P41b eher *überschrieben* oder *gemischt* als *geprägt*,
weil der schwache Split R in 150 Schritten einen kleineren Vorsprung aufbaut, als die Neigung von E danach ausgleichen kann.
Tritt *geprägt* ein, spricht das gegen H42 in dieser Form.

## Status

Vorab festgelegt, Code geschrieben, **ungetestet** (Fenster geschlossen; Selbsttest am Queue-Anfang, fail-closed).
Nicht in `queue_s10.sh` (die ist lang genug); Kandidat für die nächste Queue nach EXP-040.

## Reproduktion

```
sh lab/experiments/EXP-041-imprint/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-041-imprint/analyze.py
```

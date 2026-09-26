---
id: EXP-035
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-035: Verschiebt ein Lernraten-Warmup die Festlegung des Transformers? (Schrittzahl oder Parameterstrecke)

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Grundlage
[[experiments/EXP-020-data-switch/README|EXP-020]] · verwandt [[experiments/EXP-032-early-lockin/README|EXP-032]],
[[experiments/EXP-033-optimizer-lockin/README|EXP-033]].

## Anlass

EXP-020, Seed 30 (beschreibend, 13:38): Der Transformer legt seine Frequenzwahl zwischen 25 und 50 AdamW-Schritten fest; ab
150 Schritten auf F bleibt K nach 2000 G-Schritten exakt wie im Lauf „nur F“. Im Zwei-Hot-Netz (EXP-032/033) fiel die
Festlegung bei einer bestimmten Merkmalsamplitude, und der Weg dorthin (AdamW, GD, signGD) war für das Entstehen der
Neigung nicht entscheidend. Übertragen: Hängt die Festlegung an der **Zahl der Schritte** (Datenexposition) oder an der
**zurückgelegten Parameterstrecke**? Adams frühe Schritte sind vorzeichenartig und etwa so groß wie die Lernrate
(Abuduweili & Liu 2024, https://arxiv.org/abs/2412.02153), die Strecke ist also etwa die aufsummierte Lernrate Λ(t) = Σ lr_s.
Ein linearer Warmup über W = 200 Schritte macht die Strecke in den ersten Schritten viel kleiner, die Schrittzahl bleibt gleich.

## Versuch (vorab festgelegt 2026-09-26 13:41 Berlin, vor jedem EXP-035-Lauf; EXP-020 hat bis dahin nur Seed 30 fertig)

| Punkt | Festlegung |
|---|---|
| **Frage** | Verschiebt ein Warmup die kausale Festlegungszeit der Frequenzwahl (EXP-020-Protokoll) zu späteren Schritten? |
| **H35 (Strecke)** | Die Festlegung fällt bei gleicher aufsummierter Lernrate Λ. Mit Warmup (lr_t = 1e-3 · min(1, t/200)) ist Λ(25) = 1.6, Λ(50) = 6.4, Λ(100) = 25.2, Λ(141) = 50.1, Λ(150) = 56.6, Λ(250) = 150.5 (in Einheiten lr). Seed 30 (ohne Warmup (25, 50]) → mit Warmup erwartet (100, 150] |
| **Alternative (Schrittzahl)** | Das Intervall bleibt wie ohne Warmup |
| **Code** | `freq_ban.py --warmup 200` (neu, Standard 0 = unverändert; Lauf-IDs enden auf `_wu200`), sonst genau EXP-020 (Splits, 2000 G-Schritte nach dem Wechsel, „nur F“ bis 8000 mit Stop gen + 2000, K = Top-5 von W_E) |
| **Gitter** | t ∈ {0 (nur G), 25, 50, 100, 150, 250, ∞ (nur F)}, jeweils mit Warmup |
| **Seeds** | 30, 31, 32 in dieser Reihenfolge (weitere, falls Budget), nur Seeds mit gültigem EXP-020-Intervall (lo, hi] und hi ≤ 150 zählen |
| **Messung** | Festlegungsintervall mit Warmup (lo_w, hi_w] nach der EXP-020-Regel (`EXP-020/analyze.py` wiederverwendet: Gültigkeit d(0) < 0 < d(∞), Hashes, Schrittzahlen) |
| **Primär** | Verzögert: hi_w > hi (ohne Warmup) |
| **Entscheidung** | ≥ 3 auswertbare Seeds nötig. Alle verzögert → ***Festlegung folgt der Parameterstrecke (H35 gestützt)***; keiner → ***Festlegung folgt der Schrittzahl***; gemischt → ***unklar***; < 3 auswertbar → *nicht auswertbar* |
| **Sekundär** | Stimmt das Warmup-Intervall in Λ-Einheiten mit dem Intervall ohne Warmup überein (quantitative H35)? gen_F mit Warmup; Monotonie |
| **Was dagegen spräche** | hi_w = hi: Die ersten Datenkontakte legen fest, unabhängig davon, wie weit sich die Gewichte bewegen |
| **Grenzen** | Warmup ändert auch Adams Momentenschätzung und die Dynamik nach dem Warmup; eine Warmup-Länge; grobes Gitter; Seeds 30–32 sind aus EXP-020 bekannt (die Warmup-Läufe sind neu) |
| **Budget** | 7 Läufe pro Seed à 4–7 min ≈ 35 min pro Seed → 3 Seeds ≈ 1.75 h |

**Neuheit:** vorläufig; EXP-020 selbst ist nach der Suche vom 2026-09-26 nicht gefunden, Warmup als Eingriff in die kritische
Periode der Frequenzwahl ebenso wenig (nicht gezielt gesucht, nachholen).

## Nachtrag a (2026-09-26 13:47 Berlin, nach Codex-Review `codex_review_2026-09-26.txt`, vor jedem EXP-035-Lauf): gilt allein, wo abweichend

Codex: needs-attention, 3 × high, 2 × medium, alle zutreffend und **übernommen**:
1. *Der Warmup lief nach dem Wechsel weiter*, die G-Phase hätte je nach t ein anderes Lernratenbudget gehabt. → Warmup nur
   während F; ab dem ersten G-Schritt volle Lernrate. Die G-Phase ist damit in allen Armen gleich (2000 Schritte, lr 1e-3).
   Referenz t = 0 ist deshalb der EXP-020-Lauf „nur G“ (identisch), kein neuer Lauf.
2. *Σ lr ist nicht die Parameterstrecke.* → Die Hypothese heißt jetzt nur noch **„die Festlegung hängt am Lernratenplan“**
   (Richtung H35); zusätzlich wird am Umschaltschritt die gemessene Strecke ‖θ − θ₀‖ (alle Parameter und W_E) gespeichert
   und beschreibend berichtet. Eine Aussage „folgt der Parameterstrecke“ wird nicht als Urteil vergeben.
3. *Nicht monotone Kurven oder Kreuzungen nach der Generalisierung konnten mitzählen.* → Ein Seed ist nur auswertbar, wenn
   beide Kurven (mit und ohne Warmup) monoton sind, gen_F in beiden beobachtet ist und beide Kreuzungen vor gen_F liegen.
4. *Gitter-Randfall* (Grundlinie (0, 10] gegen Warmup-Gitter ab 25). → t = 10 ins Warmup-Gitter; Einordnung
   intervallsicher: **verzögert** nur, wenn lo_w ≥ hi_b; **gleich** nur bei identischem Intervall; sonst **unklar**.
5. *Metadaten ungeprüft.* → Die Auswertung prüft Warmup-Flag (200 bzw. 0), lr/Weight Decay/β und die gemeinsame
   Init-Prüfsumme aller Läufe eines Seeds, sonst nicht auswertbar.
Entscheidung neu: ≥ 3 auswertbare Seeds; alle *verzögert* → ***Festlegung hängt am Lernratenplan: Warmup verzögert***;
alle *gleich* → ***Festlegung folgt der Schrittzahl***; sonst ***unklar***. Gitter mit Warmup: t ∈ {10, 25, 50, 100, 150, 250, ∞}.
Die Warteschlange beginnt mit einem 60-Schritte-Smoke (Wechsel bei 30), der Wechsel- und Streckenereignis prüft.
Code-Commit des Nachtrags: b231fc6.

## Befehle

    sh lab/experiments/EXP-035-warmup-lockin/queue.sh 30 31 32
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-035-warmup-lockin/analyze.py

## Nachtrag b (2026-09-26 15:43 Berlin, vor jedem EXP-035-Lauf): Oberwellen-erweitertes d nur berichtet

EXP-020 Seed 33 war nur wegen einer 2k-Oberwelle nicht monoton (JOURNAL Sitzung 9, Zyklus 7). `analyze.py` berichtet
zusätzlich d_h (F-/G-Seite einschließlich fold(2k), gemeinsame ausgenommen) für Basis und Warmup. **Urteil und
Auswertbarkeit bleiben unverändert** (weiter mit d und Monotonie-Pflicht).

## Nachtrag c (2026-09-26 18:20 Berlin, Sitzung 10, vor jedem Seed-32-Lauf von EXP-035): Zustandsvergleich, Λ- gegen schrittgleich (beschreibend)

**Beobachtung (post hoc, Seeds 30, 31):** Endzustände (Top-5 von W_E) von Mischläufen stimmen über verschiedene Eingriffe hinweg
teils **exakt** überein: Seed 30 (6, 19, 29, 34, 47) mit Warmup und Wechsel bei t = 100 **und** in EXP-037 (Wechselspiel, A = 25);
Seed 31 (4, 8, 36, 42, 46) ohne Warmup bei t = 10 (Λ = 10) **und** mit Warmup bei t = 50 (Λ = 6.4). Seed 30: Λ-gleiche Paare
überlappen im Mittel 3.0 von 5, schrittgleiche 2.3.
**P35d (nur Seed 32, dessen Warmup-Läufe noch nicht existieren):** Λ-gleiche Paare (Warmup t' ↔ ohne Warmup t: (50, 10), (100, 25),
(150, 50)) überlappen im Mittel stärker als schrittgleiche ((10, 10), (25, 25), (50, 50)) → *erfüllt*, sonst *nicht erfüllt*.
Seeds 30, 31 nur als Exploration. Ein Seed ist nur ein Hinweis, kein Urteil. Code `state_match.py` (in `queue_s10.sh` nach
`analyze.py`). Grenze: Die Λ-Paare sind nur angenähert gleich (6.4/10, 25.2/25, 56.6/50).

## Nachtrag d (18:26 Berlin, Sitzung 10, nach Codex `codex_conclusion_review_2026-09-26.txt`, vor jedem Seed-32-Lauf): P35d zurückgezogen

Codex (needs-attention): (1, hoch) Die „wenigen, exakt wiederkehrenden Endzustände“ sind vor allem die Plateaus „nur F“/„nur G“;
ohne sie bleiben bei Seed 30 sieben Mischläufe mit sechs Mengen, die gezeigten Übereinstimmungen sind post hoc aus vielen möglichen
Paaren gesucht, und es fehlt jeder Zufallsvergleich für einen eingeschränkten Kandidatenvorrat. (2, hoch) Der Λ-/Schritt-Vergleich
bewertet verschiedene Läufe (Λ: Warmup 50/100/150; Schritt: 10/25/50, fast reine G-Läufe); jede bloße Verzögerung durch Warmup erfüllte
P35d, und ein zusätzliches gemeinsames Frequenzelement genügte. (3, mittel) `state_match.py` prüft Eingaben nicht fail-closed.
**Übernommen, alles:** P35d ist **zurückgezogen** (kein Urteil, auch nicht beschreibend), `state_match.py` ist aus der Queue
entfernt und bleibt nur als Werkzeug liegen. Die Beobachtung aus Nachtrag c gilt nur noch als **unkalibrierte Top-5-Kollision**
(zwei exakte Übereinstimmungen von Mischzuständen über verschiedene Eingriffe), ohne Aussage über Attraktoren oder eine Λ-Uhr.
Ein sauberer Test bräuchte gleiche Warmup-Läufe gegen die jeweils vorhergesagten Kontrollen (fehlender Kontrollpunkt t = 100
ohne Warmup), eine vorab festgelegte Effektgröße und eine Zufalls-Null über mehrere frische Seeds. Die Λ-Frage prüft EXP-039.

## Nachtrag e (18:50 Berlin, Sitzung 10): Seed 34 zusätzlich (vom Design erlaubt, Regeln unverändert)

Die Queue läuft jetzt über die Seeds 30, 31, 32, **34** („weitere, falls Budget“ in der Festlegung; 33 ist ohne Warmup nicht monoton
und deshalb nicht auswertbar). Die Entscheidungsregel bleibt: ≥ 3 auswertbare Seeds, **alle** *verzögert* → Urteil. Ein vierter Seed
kann das Urteil nur erschweren, nicht erleichtern. Anlass: Robustheit, falls ein Seed an den Gültigkeitsregeln scheitert.

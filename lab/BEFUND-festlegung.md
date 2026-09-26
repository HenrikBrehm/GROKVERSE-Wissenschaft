---
id: BEFUND-festlegung
status: explorativ
datum: 2026-09-26
tags: [befund/positiv, befund/unklar, neu/kandidat]
verwandt: ["[[experiments/EXP-020-data-switch/README|EXP-020]]", "[[experiments/EXP-035-warmup-lockin/README|EXP-035]]", "[[experiments/EXP-037-alternation-conflict/README|EXP-037]]", "[[experiments/EXP-033-optimizer-lockin/README|EXP-033]]", "[[NOVEL_DIRECTIONS]]"]
---
# Befund: Wann und warum legt sich die Frequenzwahl fest? (Stand Sitzung 10)

Zurück zu [[LAB]] · Einzelheiten im [[JOURNAL]] (Sitzungen 7–10) und in den verlinkten Versuchen. Beobachtung, Deutung und
Spekulation sind getrennt markiert. „Neu“ heißt immer: nach unserer Suche vom 2026-09-26 nicht gefunden.

## Beobachtet (Messungen)

- **Frühe Festlegung im Transformer** ([[experiments/EXP-020-data-switch/README|EXP-020]], 5 Seeds): Wird nach t Schritten von
  Split F auf Split G gewechselt (danach 2000 Schritte G), endet das Netz ab t ∈ (25, 50] auf den F-Frequenzen (5/5 Seeds,
  beschreibend; das vorab festgelegte Urteil war *nicht bestätigt*, 4/5, wegen einer Oberwelle in Seed 33). Das liegt vor der
  Memorisierung und weit vor dem Grokking.
- **Nach der Festlegung** wachsen unter G-Daten die F-Frequenzen weiter wie unter F, die G-Ziele schrumpfen (5/5, post hoc,
  JOURNAL Sitzung 10 Zyklus 20).
- **Warmup verschiebt die Festlegung** ([[experiments/EXP-035-warmup-lockin/README|EXP-035]], bisher Seed 30 vollständig, Seed 31
  teilweise, kein Urteil): Seed 30 mit Warmup (100, 150].
- **Wiederholtes Wechseln** in der kritischen Periode erzeugt je Seed wiederkehrende „fremde“ Frequenzen
  ([[experiments/EXP-037-alternation-conflict/README|EXP-037]], nur an den 3 explorierten Seeds).
- **Adam-Strecke:** ‖ΔW_E‖ ≈ 0.11 · Λ (Λ = aufsummierte Lernrate in lr-Einheiten) bis Λ ≈ 60 (post hoc, Sitzung 10).
- **Anderes Modell, gleiche Richtung:** Mit Aktivierungswechsel legt ein Netz seine Neigung schon in ≤ 20 Schritten fest
  ([[experiments/EXP-032-early-lockin/README|EXP-032]]), und das hängt am erreichten Amplitudenzustand, nicht am Optimierer
  ([[experiments/EXP-033-optimizer-lockin/README|EXP-033]], *zustandsbestimmt*).

## Einschränkungen (wichtig)

- F und G teilen ≈ 73 % ihrer Trainingspaare: Die Festlegung ist bisher nur gegen einen **Teilwechsel** (≈ 27 % neue Paare) gezeigt.
  Der harte Test mit ≈ 63 % neuen Paaren ist [[experiments/EXP-041-imprint/README|EXP-041]] (vorbereitet).
- Eine Architektur (Transformer, p = 113), Splits aus einem Generator, Top-5-Maß anfällig für 2k-Oberwellen.
- Die exakt wiederkehrenden Mischzustände (Sitzung 10, Zyklus 12) sind nach Codex nur eine **unkalibrierte** Beobachtung.

## Deutungen (Hypothesen, vorab festgelegte Tests in der Nacht-Queue)

| Hypothese | Aussage | Test |
|---|---|---|
| **Λ-Uhr** (N17) | Die Wahl fällt bei fester aufsummierter Lernrate Λ ∈ (25, 50] | [[experiments/EXP-039-lr-clock/README\|EXP-039]] (lr × 2 / × 0.5) |
| **H40, Amplitudenschwelle** (N18) | Die Wahl fällt, wenn das Datensignal in W_E die Init-Amplitude einholt; unter Adam ∝ Λ, deshalb sieht es wie eine Λ-Uhr aus | [[experiments/EXP-040-we-init-scale/README\|EXP-040]] (W_E-Init × 0.5 / × 2), Zahl-Vorhersage R ≈ 1 |
| **H42, Vorsprung gegen Neigung** (N22) | Jede Frequenzmenge löst die Aufgabe; der Split neigt nur. Festgelegt, sobald der Vorsprung die Neigung des neuen Splits überwiegt | [[experiments/EXP-042-bias-strength/README\|EXP-042]] (stärker konzentriertes G) |
| **Prägung** (N19) | Ein kurzer Vorlauf legt die Frequenzen auch gegen einen Zufallssplit fest; ob ein schwacher Split genauso prägt, ist offen | [[experiments/EXP-041-imprint/README\|EXP-041]] |
| **Init bei Konflikt** (N15) | Heben sich F und G auf, entscheidet die Init | [[experiments/EXP-036-init-conflict/README\|EXP-036]] |

## Nächstverwandte Literatur

LeDoux 2026 (https://arxiv.org/abs/2603.25047): Minibatch-Reihenfolge bestimmt die Grundfrequenz. He et al. 2026
(https://arxiv.org/abs/2602.16849): Frequenz-Lotterie über Init-Betrag und Phase. Kunin et al. 2025 (https://arxiv.org/abs/2506.06489):
Fourier-Merkmale werden nacheinander gelernt und bleiben. Achille et al. 2019: kritische Perioden allgemein. Keine dieser Arbeiten
misst nach unserer Suche eine kausale Festlegungszeit der Frequenzwahl per Datenwechsel oder deren Abhängigkeit von Lernrate,
Init-Skala oder Split-Neigung.

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
  Split F auf Split G gewechselt (danach 2000 Schritte G), wird das Dominanzmaß d = (Anzahl F-Ziele) − (Anzahl G-Ziele) in den End-Top-5
  zwischen t = 25 und t = 50 positiv (5/5 Seeds, beschreibend; das vorab festgelegte Urteil war *nicht bestätigt*, 4/5, wegen einer
  Oberwelle in Seed 33). Bei t = 50 ist d nur +1 bis +3, die Endzustände sind dort noch **gemischt** (G- und fremde Frequenzen);
  exakt gleich wie „nur F“ ist K erst ab t = 150. Der Vorzeichenwechsel liegt vor der Memorisierung und weit vor dem Grokking.
- **Nach der Festlegung** wachsen unter G-Daten die F-Frequenzen weiter wie unter F, die G-Ziele schrumpfen (5/5, post hoc,
  JOURNAL Sitzung 10 Zyklus 20).
- **Warmup verschiebt die Festlegung** ([[experiments/EXP-035-warmup-lockin/README|EXP-035]], bisher Seed 30 vollständig, Seed 31
  teilweise, kein Urteil): Seed 30 mit Warmup (100, 150].
- **Wiederholtes Wechseln** in der kritischen Periode erzeugt je Seed wiederkehrende „fremde“ Frequenzen
  ([[experiments/EXP-037-alternation-conflict/README|EXP-037]], nur an den 3 explorierten Seeds).
- **Adam-Strecke:** ‖ΔW_E‖ ≈ 0.11 · Λ (Λ = aufsummierte Lernrate in lr-Einheiten) bis Λ ≈ 60 (post hoc, Sitzung 10).
- **Anderes Modell, gleiche Richtung:** Mit Aktivierungswechsel legt ein Netz seine Neigung schon in ≤ 20 Schritten fest
  ([[experiments/EXP-032-early-lockin/README|EXP-032]]). In [[experiments/EXP-033-optimizer-lockin/README|EXP-033]] erzeugte reiner
  Gradientenabstieg in der frühen Phase bei angeglichener Amplitude ebenfalls eine bleibende, gleichgerichtete Neigung; AdamW ist in
  Phase 1 also **nicht nötig**. Nicht gezeigt ist dort, dass der erreichte Zustand allein entscheidet (die Zustände am Umschaltpunkt
  unterschieden sich, Phase 2 lief immer mit AdamW); das Etikett *zustandsbestimmt* wurde dort selbst eingeschränkt.

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

## Vorab festgelegte Lesart der Ergebniskombinationen (18:53 Berlin, vor allen Läufen von EXP-039 bis EXP-042)

Die Urteile der einzelnen Versuche bleiben wie in deren READMEs festgelegt; hier steht nur, was eine **Kombination** für die
Gesamtaussage bedeuten soll, damit sie nicht nachträglich zurechtgelegt wird.
1. **Unabhängig von EXP-041** gelten die Uhr-Aussagen (EXP-035/039/040/042) nur für ihr eigenes Protokoll (Teilwechsel F → G,
   ≈ 27 % neue Paare).
2. **EXP-041 P41a** beschreibt nur, ob die 150-Schritte-Prägung durch E den Wechsel auf R (≈ 63 % neue Paare) unter dem Top-5-Maß
   überdauert: *geprägt* = ja (für diesen Eingriff); *nicht gezeigt* heißt **nicht** „kippt auf R“ (es umfasst auch gemischte Ausgänge
   wie 8/10); ein Überschreiben wäre nur aus den Einzelwerten d < 0 beschreibend abzulesen.
3. **EXP-039 *Λ* und EXP-040 *H40-Muster*:** gemeinsame Lesart „Amplitudenschwelle unter Adam“ (N18); nur Assoziation, kein Mechanismus.
   **EXP-039 *Λ*, EXP-040 *unverändert*:** Optimierer-Uhr ohne Init-Bezug (oder Schwelle mit exponentiellem Wachstum, EXP-040 Einordnung).
   **EXP-039 *Schritt*:** Uhr in Schritten (z. B. Adams Momenten-Horizont); H40 in linearer Fassung dann unwahrscheinlich.
4. **EXP-042 *später*:** Der Zeitpunkt hängt auch vom zweiten Split ab (Neigung und Überlappung nicht getrennt); eine reine,
   vom zweiten Split unabhängige Uhr reicht dann nicht. Zusammen mit 3. hieße das höchstens: eine mit H40 assoziierte Schwelle **plus**
   eine noch nicht identifizierte Abhängigkeit vom zweiten Split; den Mechanismus „Vorsprung gegen Neigung“ (H42) belegt das nicht.
   **EXP-042 *gleich*:** keine Verschiebung bei dieser Gitterauflösung.
5. Jede Kombination mit *unklar* wird als *unklar* berichtet, nicht durch die anderen Versuche „aufgefüllt“.
6. Kein Versuch erlaubt eine Aussage über andere Architekturen oder Aufgaben.

*Korrektur (18:59, nach Codex `codex_befund_festlegung_review_2026-09-26.txt`, vor allen betroffenen Läufen):* EXP-020-Kern
präzisiert (d > 0, nicht „F-Frequenzen“), EXP-033 richtig wiedergegeben, Lesart 1/2 und 4 auf die Urteilskategorien der Versuche
zurückgeführt.

## Kontinuierliche Sicht (Sitzung 14, post hoc an gespeicherten Läufen, explorativ)

Persistenz π ∈ [0, 1] (0 = wie nur zweiter Split, 1 = wie nur erster), aus der Elastizität β (log W_E-Leistung auf log M0 je Split) oder,
gleichwertig, aus dem Log-Verhältnis der Zielleistung (beide Maße weichen höchstens 0.05 im Mittel voneinander ab):
- **Zeitverlauf** ([[experiments/EXP-020-data-switch/README|EXP-020]], 5 Seeds): π = 0.15 / 0.38 / 0.72 / 1.00 bei Wechsel nach 10 / 25 / 50 / 150
  Schritten; glatt, Halbwert ≈ 30–35 Schritte, Spanne über Seeds ≤ 0.28.
- **Uhr** ([[experiments/EXP-035-warmup-lockin/README|EXP-035]], 1–2 Seeds): Mit Warmup folgt π früh der aufsummierten Lernrate Λ, nicht der
  Schrittzahl; später hält es stärker fest als Λ allein vorhersagt.
- **Wettlauf** ([[experiments/EXP-037-alternation-conflict/README|EXP-037]], 3 Seeds): 100 F-Schritte am Stück → π ≈ 1.0; dieselben 100 F-Schritte
  mit G verschränkt → 0.52–0.75.
Alles an bereits gesehenen Daten, wenige Seeds, F/G mit ≈ 73 % geteilten Paaren: keine Bestätigung. Nutzen: ein trennscharfes Maß für P3
([[BACKLOG]] „Persistenzmaß für P3“) und Konkurrenzmodelle mit Zeitstruktur.

*Korrektur (Sitzung 14, nach adversarieller Prüfung):* π misst die Aufteilung der Leistung zwischen F- und G-Zielen (β fügt nichts
darüber hinaus hinzu); π ≈ 1 ab t = 150 (Werte > 1 sind Endschritt-Artefakt). **Uhr:** Warmup verzögert, aber *weder* Schritt- *noch*
Λ-Uhr passen (bei gleichem Λ halten Warmup-Läufe mehr fest). **Verschränkung:** π liegt über der Vorhersage „nur der erste F-Block zählt“,
spätere F-Blöcke tragen also bei; „Wettlauf“ bleibt Deutung.

## Nächstverwandte Literatur

LeDoux 2026 (https://arxiv.org/abs/2603.25047): Minibatch-Reihenfolge bestimmt die Grundfrequenz. He et al. 2026
(https://arxiv.org/abs/2602.16849): Frequenz-Lotterie über Init-Betrag und Phase. Kunin et al. 2025 (https://arxiv.org/abs/2506.06489):
Fourier-Merkmale werden nacheinander gelernt und bleiben. Achille et al. 2019: kritische Perioden allgemein. Keine dieser Arbeiten
misst nach unserer Suche eine kausale Festlegungszeit der Frequenzwahl per Datenwechsel oder deren Abhängigkeit von Lernrate,
Init-Skala oder Split-Neigung.

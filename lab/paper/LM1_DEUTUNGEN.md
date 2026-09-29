---
id: paper-LM1-deutungen
status: vorbereitet
datum: 2026-09-29
tags: [lab/paper]
verwandt: ["[[paper/draft_short]]", "[[confirm/LM1_REGISTRATION|LM1]]", "[[experiments/EXP-115-lm-flat-marginals/README|EXP-115]]", "[[experiments/EXP-117-lm-untied/README|EXP-117]]"]
---
# LM1 (+ EXP-115, EXP-117): Deutungssätze je Ausgang, vor jedem Ergebnis festgelegt (Sitzung 51, 2026-09-29, ≈ 14:35 Berlin)

Zurück: [[paper/STATUS]] · Kurzfassung Anhang K · Lesarten maschinell in `lab/confirm/confirm_lm1.py --analyze` (eingefroren 2b70d8b9), `EXP-105…/analyze_pilot.py` (EXP-115), `EXP-117…/analyze.py`.
Zweck wie [[paper/L0_DEUTUNGEN]]: Die Deutung jedes Ausgangs steht fest, bevor die Läufe ausgewertet sind. Beim Einsetzen nur Zahlen ergänzen (Mittel, KI, n, p); Abweichungen vom Wortlaut im JOURNAL begründen. **Stand beim Schreiben:** keine LM1-, EXP-115- oder EXP-117-Auswertung gesehen; gesehen sind nur Logzeilen (Genauigkeiten) der ersten LM1-Läufe und des ersten EXP-115-Laufs.

**Ort im Paper:** Anhang K (Towards language models). LM1 ist ein Nebenbefund zur Verallgemeinerung, kein vierter Hauptbefund (Regel 20a: Satz der Kernaussagen eingefroren). Höchstens ein Satz in §7 (ii) *Scope*.

## LM1 (primär, bestätigend)

- **„bestätigt“:** *In a 14 M-parameter language model trained from scratch on TinyStories with interleaved arithmetic sentences (about 79 % arithmetic tokens, loss on text and answers, tied embeddings), the engineered fact splits steered the number-token embedding on 10 fresh seeds (mean Δ_pow … [CI], above the registered minimum effect 1; p …; held-out fact accuracy ≥ 0.5 in …/20 runs).* Immer dazu: *This is one configuration with a high arithmetic share and an energy measure on tied embeddings; it does not show steering at a few percent arithmetic data or functional use.* §7 (ii): *Steering also held in one small language-model configuration (Appendix K).*
- **„unter Mindesteffekt“ (gespiegelter Test: Mittel sicher < 1):** *With the same design the steering stayed below the registered minimum effect (mean Δ_pow … [CI]): in this language model, fact selection does not steer the number embeddings measurably although the facts are learned.* Das ist die erste Stufe der Leiter, auf der K2 bricht (Regel 20e) → so in Anhang K und §7 (ii) benennen; nicht auf Seeds oder Budget schieben, wenn das Tor bestanden ist.
- **„unklar“ (weder bestätigt noch sicher darunter):** *The mean Δ_pow was … [CI], which neither exceeds the registered minimum effect nor falls clearly below it; we report the language-model result as inconclusive.* Keine Ausdeutung einzelner Seeds als Beleg.
- **„nicht auswertbar (Budget)“ (Tor verfehlt):** *Fewer than 16 of 20 runs reached held-out fact accuracy 0.5 within 6000 steps, so the registered test was not evaluable; this says nothing about steering.*
- **„nicht auswertbar (defekt/fehlt)“:** nur technischer Vermerk mit Grund; Läufe nach der Ausfallregel neu einreihen, bevor irgendetwas berichtet wird.
- **Sekundär H-folgt (beschreibend):** unabhängig vom Ausgang nur als Häufigkeit berichten (*in … of … pairs the first snapshot with Δ_pow > 1 did not precede the fit onset*); keine Aussage „folgt“ ohne diese Zählung.

## Zusatzsätze aus den Kontrollen (nur wenn LM1 „bestätigt“; Explorationen, 2 Seeds)

- **EXP-115 „Paarstruktur reicht“:** *With exactly equal counts of every number in every role (flat-marginal splits, exploration, 2 seeds), Δ_pow was … and …, so the steering does not require different number frequencies.*
- **EXP-115 „braucht Häufigkeiten“:** *With exactly equal number counts the steering vanished (Δ_pow … and …; exploration), so in the language model the effect may run through number frequencies rather than pair structure.* Dann ausdrücklich: LM1 nicht als Beleg für Paarstruktur im LM lesen.
- **EXP-117 „Eingabe gesteuert“:** *With untied input and output embeddings (exploration, 2 seeds) the input rows of the number tokens were steered (Δ_in … and …), so the effect is not only a property of shared output vectors.* Δ_out beschreibend dazu.
- **EXP-117 „nur Ausgabe gesteuert“:** *With untied embeddings only the output rows were steered (Δ_in …, Δ_out …; exploration); the tied-embedding value of LM1 should be read as a property of the output vectors, not of the number representation.*
- **EXP-117 „keine Steuerung“:** *With untied embeddings neither input nor output rows were steered although the facts were learned (exploration); LM1's steering may depend on tying.*
- **„nicht gelernt (Budget)“ / „unklar“ in einer Kontrolle:** nur *not evaluable / inconclusive at this budget*; keine Richtung ableiten.

## Nachtrag (Sitzung 51, ≈ 15:05, vor jedem EXP-116-Lauf): EXP-116 (≈ 8.7 % Rechen-Tokens, 2 Seeds, Exploration)

- **„K2 haelt im LM“:** *With only about 9 % arithmetic tokens (exploration, 2 seeds, 16 000 steps), the model learned the facts (held-out … / …) and the fact selection again steered the number embedding (Δ_pow … and …).* Nur Anhang K; keine Bestätigung.
- **„bricht“:** *At about 9 % arithmetic tokens the facts were learned but the number embedding was not steered (|Δ_pow| ≤ 1 in both seeds; exploration)* → erste Stufe, auf der K2 bricht (Regel 20e); eine Bestätigung mit 10 frischen Seeds wäre der nächste Schritt, bevor das in den Haupttext kommt.
- **„nur Repraesentation“:** *The embedding was steered although held-out facts stayed near chance (exploration).*
- **„nicht gelernt (Budget)“:** *At about 9 % arithmetic tokens the model did not learn the facts within 16 000 steps, so steering could not be assessed.* Keine Aussage über K2; Hinweis auf die Faktenzahl-Tendenz (Journal S51, Zyklus 7).
- **„unklar“:** *inconclusive at this budget.*

## Nachtrag (Sitzung 52, 19:09 gemessen, vor jedem EXP-119-Lauf): EXP-119 (R5 im LM, 2 Seeds, Exploration)

- **„constructed faster“:** *In the small language model (exploration, 2 seeds), held-out facts from engineered splits reached accuracy 0.5 earlier than from a uniform random split of the same size (ratio q = … and …). Because the language model learns training and held-out facts almost together, this is a shift of the learning onset itself, not a shorter grokking delay as in the toy model; the engineered splits also carry the targets in the number counts, so a count effect is not excluded.*
- **„no advantage“:** *In the small language model the random split was learned as early as the engineered splits (q = … and …; exploration). The speed-up of Result 2 is therefore tied to the grokking regime of the toy model and was not seen in a language model that learns without a grokking delay.* → als Grenze in §7 bzw. Anhang (LM), nicht verschweigen.
- **„unclear“ / „not learned (budget)“:** nur *inconclusive (exploration)*; keine Richtung ableiten.
- **ρ (Maskenspektrum ↔ Zahl-Zeilen) je Arm:** nur beschreibend nennen; ein positives ρ beim Zufallssplit R wäre ein Hinweis, dass auch im LM ein gewöhnlicher Split die Frequenzen mitprägt (R4-Analogon), mit 2 Seeds kein Befund.

## Nachtrag (Sitzung 53, 21:20 gemessen, vor der LM1-F-Auswertung): LM1-F (funktional, bestätigend)

**Stand beim Schreiben:** LM1 ist „bestätigt“. Von LM1-F gesehen: die ersten Ergebniszeilen im Job-Log (Seed 4000 F/G: eigene Ziele weg 0.086 / 0.214, fremde weg 0.740 / 0.977, Kontrollen 0.88–0.98; C̄ = 0.709) und die Werte der unabhängigen Nachrechnung für denselben Seed. Die Sätze unten hängen davon nicht ab (sie sind je Ausgang formuliert).

- **„bestätigt“:** *In the ten LM1 models, removing the Fourier subspace of the run's own five target frequencies from the number-token rows lowered held-out fact accuracy far more than removing the other split's targets (mean C̄ … [CI], above the registered minimum effect of 0.1; p …; … of 10 seeds with C̄ > 0); removing any of four control sets left accuracy near its baseline (…–…). With tied embeddings this ablation acts on input and output vectors alike, so it shows that the steered frequencies are used by the model, not whether the input or the output side uses them.* §7 (iii) *Measures* bleibt unverändert (gilt für das Spielzeugmodell); höchstens Halbsatz in Anhang J.
- **„unter Mindesteffekt“:** *In the ten LM1 models, removing the own targets did not lower held-out accuracy clearly more than removing the other split's targets (mean C̄ … [CI], below the minimum effect 0.1): in this language model the steered frequencies carry energy but are not measurably used.* Dann in Anhang J den EXP-118-Satz ausdrücklich als nicht bestätigt kennzeichnen.
- **„unklar“:** *The functional contrast was … [CI], neither clearly above nor below 0.1; inconclusive.*
- **„nicht auswertbar“:** technischer Vermerk mit Grund, keine Aussage.
- Unabhängige Nachrechnung (`LM1F_independent_recompute.py`) vor jedem Paper-Satz; bei Abweichung zuerst klären.

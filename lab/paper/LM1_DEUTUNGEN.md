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

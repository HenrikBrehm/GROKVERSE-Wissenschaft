---
id: LESART-nacht-2026-09-28
status: vorab
datum: 2026-09-27
tags: [lab/synthese]
verwandt: ["[[FINDINGS]]", "[[STATE]]", "[[JOURNAL]]", "[[experiments/EXP-040-we-init-scale/README|EXP-040]]", "[[experiments/EXP-073-part-rewind/README|EXP-073]]", "[[experiments/EXP-074-reset-other-tasks/README|EXP-074]]", "[[experiments/EXP-075-mlp-lockin/README|EXP-075]]", "[[confirm/P2f_REGISTRATION|P2f]]"]
---
# Vorab-Lesart der Nacht 27./28.09.2026 (vor jedem Lauf festgelegt)

Zurück zu [[FINDINGS]] · [[LAB]]. Geschrieben in Sitzung 24 (2026-09-27, 14:15 Berlin, gemessen), **bevor** ein Lauf von EXP-040 (dieser Fassung), EXP-073, EXP-074, EXP-075 oder P2f existierte.
Die Einzelurteile regeln die READMEs bzw. die Registrierung; hier steht nur, was die **Kombination** für [[FINDINGS]] und die nächste Planung heißt.

## Bausteine

| Versuch | Frage | stützt | spricht dagegen |
|---|---|---|---|
| [[confirm/P2f_REGISTRATION\|P2f]] (Bestätigung) | K2-Funktion bei D₅₉ | K2-Funktion auf vier Aufgaben (Kernaussage, eng: folgt der Energie) | K2-Funktion bleibt zyklisch; D₅₉ nur Repräsentation |
| [[experiments/EXP-040-we-init-scale/README\|EXP-040]] (vorab seit Sitzung 10) | verschiebt die W_E-Init-Skala das Festlegungsfenster (H40, Amplitudenrennen)? | H40: Festlegung = Datensignal holt Init-Amplitude ein | Init-Skala ohne Einfluss → reine Λ- bzw. Schrittuhr |
| [[experiments/EXP-073-part-rewind/README\|EXP-073]] (Pilot) | welcher Teil ist für die Zeitabhängigkeit empfindlich? | W_E / Rest / beide / Redundanz (vier Lesarten) | technisch ungültig, wenn rwall ≠ ref25 |
| [[experiments/EXP-074-reset-other-tasks/README\|EXP-074]] (Pilot) | Reset-Muster bei add 97 / mul 113 | Muster verallgemeinert (Attention/Wertepfad, nicht MLP) | Attention-Reset wirkt dort kaum |
| [[experiments/EXP-075-mlp-lockin/README\|EXP-075]] (Pilot) | Festlegung ohne Attention (MLP)? | ähnlich früh → Festlegung ist nicht an Attention gebunden | deutlich später/keine → Attention nötig |

## Regeln für die Zusammenschau

1. **Nur P2f kann eine Kernaussage ändern.** EXP-040 ist ein Seed-Urteil mit 3–4 bekannten Seeds, EXP-073/074/075 sind Piloten an bekannten Seeds: Sie ändern FINDINGS nur unter „Explorationen“ und
   bestimmen, welche Bestätigung als Nächstes registriert wird.
2. **Konsistente Geschichte „Amplitudenrennen“** (dann Bestätigung planen): EXP-040 *H40 gestützt* **und** EXP-075 *ähnlich früh* **und** EXP-073 nicht „unempfindlich für beide“.
   Dann lautet die nächste Frage: Welche Amplitude (W_E oder Wertepfad) setzt die Uhr? → Bestätigung des EXP-073-Musters an frischen Seeds mit skalierter Init des empfindlichen Teils.
3. **Konsistente Geschichte „Attention-gebunden“**: EXP-075 *deutlich später oder keine* **und** EXP-074 *Reset-Muster verallgemeinert*. Dann ist K4d/e mehr als Reset-Empfindlichkeit wert, eine
   mechanistische Bestätigung (Wertepfad) wird Programm B.
4. **Widersprüchlich** (z. B. EXP-075 ähnlich früh, aber EXP-073 „empfindlich nur für Rest-Rückspulen“): Das ist möglich (andere Architektur, anderer Ort) und wird als offene Frage geführt,
   **nicht** zu einer Geschichte geglättet.
5. **EXP-073 technisch ungültig** (rwall ≠ ref25 in einer Richtung): Werkzeug reparieren (höchstens drei Versuche), keine Deutung der übrigen Arme.
6. **EXP-074 unklar oder nur bei einer Aufgabe verallgemeinert:** K4d/e bleibt ausdrücklich add-113-spezifisch; keine Ausweitung in FINDINGS oder im Paper.
7. Paper ([[paper/STATUS]]): Piloten gehen nur in den Abschnitt „Explorations“, egal wie deutlich.

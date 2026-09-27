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

## Ergänzung Sitzung 25 (14:58, vor jedem Lauf): EXP-077

8. **EXP-077 positiv** (Δ̄ ≥ 1, p < 0.05): „Häufigkeiten allein können steuern“ – nur als Pilot; die Lesart von EXP-047 („nur Paarstruktur“) wird in FINDINGS **nicht** sofort umgeschrieben,
   sondern ein Bestätigungsblock mit Trennung der zwei Wege (EXP-077 Nachtrag a) geplant. **Negativ:** Die Theorie erster Ordnung ist für den Fremd-Häufigkeitsanteil falsch → §5.2 im
   Paper entsprechend einschränken. **Unklar:** keine Folgerung, höchstens n erhöhen.

## Ergänzung Sitzung 26 (15:40, vor jedem Lauf): EXP-078, R3 und die Verbindung zu EXP-040

9. **EXP-078** (2 Schichten): *überträgt sich* → im Paper nur als Pilot (§4), Bestätigung an frischen Seeds in P4-Art planen; *keine Steuerung* → wichtige Grenze, sofort als solche in FINDINGS
   (Grenze 3) und Paper §6; *unklar* → n erhöhen, nichts folgern.
10. **R3 und EXP-040 zusammen** (falls R3 schon heute Nacht läuft): R3 *Λ-Uhr bestätigt* **und** EXP-040 *H40 gestützt* → Amplitudenrennen ist die führende Erklärung (weiter: welcher Teil setzt die
    Amplitude, EXP-073). R3 *Λ-Uhr bestätigt*, EXP-040 *unverändert* → Uhr in Λ, aber nicht über die W_E-Init-Amplitude; andere Amplitude (Wertepfad?) prüfen. R3 *nicht bestätigt* und
    Sekundär *passt zur Schrittuhr* → N37 (β₂-Horizont) als nächster Test. Kein Satz in FINDINGS über einen Mechanismus, bevor R3 ausgewertet ist.

## Ergänzung Sitzung 29 (vor 18:10 Berlin, gemessen, vor jedem EXP-040-Lauf): Vorprüfung von H40 bei Init-Skala 1

Post hoc an den gesehenen EXP-039-Läufen (`lab/confirm/EXP039_posthoc_R.py`, `.json`; gleiche Formel wie `EXP-040/analyze.py::target_displacement`): In den 7 vollständigen, monotonen Zellen liegt die zielgenaue Strecke der F-Ziele beim Festlegen (obere Intervallgrenze) bei R(hi) = 0.37–1.02 der Median-Init-Amplitude (Median 0.62; 6/7 in [0.5, 2]), an der unteren Grenze bei 0.17–0.55. Je Seed ist eine gemeinsame Schwelle über c = 0.5 und 2 möglich (Seed 30: (0.32, 0.37], 34: (0.37, 0.61], 31: (0.37, 0.62]). R wächst fast linear in Λ (log-log-Steigung 0.91–1.01), die Voraussetzung „lineares Wachstum unter Adam“ für die Vorhersage „Fenster ∝ s“ ist also erfüllt.
11. **Lesart:** Die quantitative Fassung von H40 (Nachtrag c) ist bei s = 1 **nicht widerlegt**: Die Wahl fällt, wenn die Zielverschiebung etwa ein Drittel bis zwei Drittel der Init-Amplitude erreicht (nicht erst bei voller Gleichheit).
12. **Vorsicht beim Invarianzvergleich (Nachtrag b):** Bei s = 1 sind R und Λ fast proportional; die c-Zellen von EXP-039 unterscheiden die beiden Uhren darin nicht, sie verdünnen den Vergleich nur. Aussagekräftig ist allein der Vergleich über die s-Zellen von EXP-040 (Pure Λ-Uhr: R(hi) ∝ 1/s; H40: R(hi) konstant). Die Statistik `R_less_variable` über alle Zellen nicht als Beleg lesen; zusätzlich R(hi) getrennt nach s = 0.5 / 2 berichten (beschreibend, ändert keine Regel).

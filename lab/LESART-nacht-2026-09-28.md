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

13. **EXP-018 (neu in dieser Nacht, Sitzung 30):** Die Entscheidungsregel steht in der README (Primär E gegen D, beschränkte Zeit bis 8000, zensierungsfeste Ko-Bedingung). Vorab bekannt: E gegen R ist über EXP-041 schon gesehen (9/10 gegen 0/10 bis 2150 Schritte) und keine Bestätigung. Neu ist nur D. Lesart: *beschleunigt* (E vor D) heißt „die Anordnung entlang a wirkt, nicht die Gewichtsverteilung“, mit dem Vorbehalt, dass D die realisierten Anzahlen je Ausgabe nur ungefähr trifft (≈ 3 von ≈ 34). *widerspricht* (D so schnell wie E) heißt „jede so strukturierte Ungleichverteilung beschleunigt“. Das wäre für die Paper-Aussage wichtig, denn dann trägt die Frequenzkonzentration nicht. Beides nur als Pilot berichten; die Bestätigung ist R5 (frische Seeds).
14. **EXP-083:** Lesart vorab in der README (≥ 15/20 Seeds). Ein Torfehler (Init-Prüfsumme oder W_E bei 50 ≠ Block) heißt: Ursache klären, Toleranz nicht ändern.

## Ergänzung Sitzung 31 (20:11 Berlin, gemessen, vor jedem Lauf dieser Nacht)

15. **EXP-018 → R5:** R5 (Fassung 2, Code ungetestet) baut D anders als EXP-018: exakt gleiche Anzahl je Ausgabe aus der *realisierten* E-Maske, nicht permutierte Gewichte. Ist EXP-018 *beschleunigt*, bleibt das für R5 ein Pilot mit leicht anderem D; ist D dort so schnell wie E, prüft R5 H-ED trotzdem (Regel der Fassung 1). Nur n kommt aus EXP-018 (`R5_power_sim.py`, Liste 20–60 inkl. 50). Nicht vorschnell aus dem Pilot schließen: Die E-Zeiten der EXP-018-Seeds sind über EXP-041 gesehen. **Zusätzlich beschreibend lesen:** den W_E-Zielanteil der Arme bei frühen Schritten, falls gespeichert. Nach Sitzung 31 (post hoc, EXP-020/042) ist er über ε gleich geordnet wie die Generalisierungszeit.
16. **EXP-042 π-Lesart (`pi_window.py`, Sekunden):** EXP-042 ist fertig (Urteil *unklar*, Top-5-Kreuzung verschiebt sich etwa wie vom reinen Takt vorhergesagt). π entscheidet C (fester Takt) gegen O (Stärke von G verschiebt das Fenster). *C* passt zur Lesart „Festlegung = Uhr + lineare Überlagerung“ und damit zu EXP-040 als Test der Uhr-Form. *O* wäre der erste Hinweis auf einen Vorsprung-gegen-Neigung-Mechanismus (H42). Nachtrag c: Mit n = 4 heißt C nur „keine Verschiebung > ≈ 0.2“.


## Ergänzung Sitzung 32 (21:06 Berlin, gemessen, vor jedem Lauf dieser Nacht)

17. **EXP-084 gegen die Vorhersage:** Nach `analyze.py` die Größe `log2_e32_over_e8_median` mit V1 in der README vergleichen (Commit 6d0231f): ≥ −0.40 → M_share (Sättigung nach dem M0-Anteil), ≤ −0.60 → M_eps, dazwischen unentschieden, ≥ +0.25 → Umkehr, beide falsch. Danach V2 (Median b(ε 4) in [450, 575]) und V3 (ε 0.5 etwa wie R) nur beschreibend. Wichtig: Es gibt keine Nachkalibrierung am Ergebnis; ein Fehlschlag wird als Fehlschlag berichtet.
18. **R6 (falls eingefroren und gerechnet):** Die Primärfamilie ist H1 C(25) > 0 und H2 C(25) − C(50) > 0. Mit n = 30 ist das Urteil klar. Ist H1 bestätigt und H2 nicht, heißt das „jeder frühe Wechsel kostet“, nicht „Spitze im Fenster“. S1 ist nur sekundär. Die Deutung bleibt ein Regimevergleich (siehe Registrierung); ein „Mechanismus“ ist daraus nicht belegt. Zwischen den Seeds sagte |π(25) − 0.5| die Kosten nicht voraus (Sitzung 32, Zyklus 9); eine Spitze im Mittel ist kein Zusammenhang je Seed.
19. **EXP-074 Zeitkosten (Nachtrag Sitzung 32, vor dem Lauf):** Q1 (VO langsamer als QK, gepoolt über 20 Einheiten) ist die prospektive Prüfung des N29c-Musters in zwei anderen Aufgaben. Trifft es zu, stützt das die Lesart „Resets verzögern in der Reihenfolge der Persistenzsenkung“. Die Alternative „zerstörte Funktion“ schließt das weiterhin nicht aus.
20. **R2 Zeitkontraste (falls R2 läuft; Zusatz Sitzung 32, vor dem Lauf):** Nach `confirm_r2.py --analyze` `python lab/confirm/R2_time.py`. T1/T2 prüfen, ob die Kosten eines Wechsels im Festlegungsfenster auch bei wd 0.3 bzw. lr 2e-3 auftreten; T3 nur beschreibend. Das gehört nicht zum R2-Urteil.
21. **R6-Zusätze und EXP-086 (Sitzung 32, vor den Läufen):** `R6_decompose.py` (Lückenanteil > 0.5) und `R6_fitroute.py` (Fitten über feste Merkmale bei 50) sind beschreibend und nicht Teil des Urteils. EXP-086 entscheidet, ob die Kosten bei 25 einen Frequenzkonflikt brauchen: Kostet A→A2 (gleiche Frequenzen) etwa so viel wie A→B, ist die Deutung „Frequenzkonflikt“ in N43/FINDINGS/Paper zu streichen oder als Phasenkonflikt offen zu lassen.

---
id: FINDINGS
status: laufend
datum: 2026-09-26
tags: [lab/synthese]
verwandt: ["[[LAB]]", "[[BEFUND-split-mechanismus]]", "[[BEFUND-festlegung]]", "[[NOVEL_DIRECTIONS]]"]
---
# FINDINGS: Kernaussagen des Labors (eine Seite)

Zurück zu [[LAB]]. **Nachtrag Sitzung 21 (27.09., 04:46): P1 und P2 sind eingefroren** (Manifest 733e829, Seeds 1000–1049; [[confirm/P1_REGISTRATION_DRAFT|P1]], [[confirm/P2_REGISTRATION_DRAFT|P2]]). P2 misst jetzt das log-Loss-Verhältnis bei halber Dosis statt der Genauigkeit. P3-Pilot [[experiments/EXP-056-overlap-persistence/README|EXP-056]] läuft. **Nachtrag Sitzung 20: Pilotnacht mit neuen Läufen, siehe Abschnitt unten.** Nachtrag Sitzung 14: nur Vorbereitung und Nachrechnung gespeicherter Läufe, keine neuen Läufe, Kernaussagen unverändert. Stand 2026-09-26, Sitzung 13 (nach 48 angelegten Versuchen; Kernaussagen seit Sitzung 11 unverändert, keine neuen Läufe). „Neu“ heißt immer: nach unserer Suche vom
2026-09-26 nicht gefunden, vorläufig. **Alle Aussagen gelten bisher nur für eine Aufgabe (Addition mod 113) und im Kern eine
Architektur (1-Schicht-Transformer der Studie, AdamW, lr 1e-3, wd 1).** Einzelheiten: [[BEFUND-split-mechanismus]], [[BEFUND-festlegung]].

## BESTÄTIGT (Sitzung 21, 27.09., 06:04 Berlin): P3, starke Wirkung einer 25-Schritt-Vorgeschichte gegen paar-disjunktes Weitertraining #befund/positiv

**Kernaussage K4-bestätigt** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 06:10): *Nach 25 Schritten auf dem ersten konstruierten Split lagen die Wechselmodelle nach 2000 Schritten auf
einem paar-disjunkten zweiten Split im Mittel noch bei 0.351 der normierten log-W_E-Leistungsdistanz zwischen dem reinen Endpunkt des zweiten und dem des ersten Splits. Der registrierte
Überschuss über jede geprüfte statische additive W_E-Spur betrug 0.293 [0.263, 0.322] (30 frische Seeds, 30/30 > 0; add 113; bestätigt).* Der Befund zeigt eine **starke Wirkung der
frühen Trainingsvorgeschichte**. Er trennt aber eine Festlegung im Netz **nicht** von Optimiererzustand oder allgemein verlangsamter Anpassung (Codex: Der reine Lauf des zweiten Splits ist
der richtige Nullpunkt für den Gesamteffekt, nicht für eine A-spezifische Festlegung; dafür fehlen B→B/A→A mit 2025 Schritten und ein Optimierer-Reset beim Wechsel).
**Sekundär:** In den registrierten, auf gleiche Steuerstärke kalibrierten Konstruktionen war kein Einfluss der Überlappung nachweisbar: Δπ(0.4 − 0) = 0.005 [−0.030, 0.042].
Das ist kein Äquivalenztest, und ε unterscheidet sich zwischen den Stufen.
**Post hoc (06:13, beschreibend, nach Ergebnis und Codex):** In den Wechselläufen tragen die Ziele des *ersten* Splits im Mittel 20 % der W_E-Leistung (Zufall 8.9 %, reiner Lauf des zweiten Splits 2.7 %;
über Zufall in 48/60 Richtungen). Die Ziele des zweiten Splits tragen 48 % statt 78 %. Ein bloß träges, diffuses Modell läge bei höchstens Zufallsniveau. Es gibt also Hinweise auf **beides**:
eine A-spezifische Erhaltung und eine langsamere Anpassung. Belege: [[confirm/P3_REGISTRATION_DRAFT|P3]], Manifest f8adf45, `P3_summary.json`, `lab/confirm/p3_posthoc_decompose.py`.
Zusammenhang: Pilot [[experiments/EXP-056-overlap-persistence/README|EXP-056]], [[experiments/EXP-038-where-lockin/README|EXP-038]] (Festlegung doppelt vorhanden, Pilot). **Größte offene Frage jetzt:**
Ist die Erhaltung A-spezifisch im Netz, oder steckt sie im Optimiererzustand? Nächster Versuch: Wechsel mit Adam-Reset und Kontrollen gleicher Länge.
**Erster Hinweis (Pilot [[experiments/EXP-057-optim-reset/README|EXP-057]], 06:21, 10 bekannte Seeds, keine Bestätigung):** Setzt man beim Wechsel nur den AdamW-Zustand zurück (Gewichte bleiben), fällt π von 0.30 auf 0.11, und die Ziele des ersten Splits sinken unter Zufall (7.1 % gegen 8.9 %). Die A-spezifische Erhaltung nach 25 Schritten sitzt demnach vor allem im **Optimiererzustand**. Die gleich lange Referenz ändert nichts (0.304). Formal *teilweise*; eine Bestätigung an frischen Seeds und die Trennung m / v / Schrittzähler stehen aus.
*Korrektur (Codex, eingearbeitet 06:31):* Nicht identifiziert, ob das Gedächtnis im Zustand sitzt oder ob die vorzeichenartigen Schritte nach dem Reset die kleine Spur überschreiben. Gestützt ist nur: Eine volle Neuinitialisierung des Optimierers senkt die spätere A-Persistenz. „Unter Zufall“ ist nicht signifikant (t = −1.2).
**Folgepilot [[experiments/EXP-058-optim-part/README|EXP-058]] (06:50, 10 bekannte Seeds):** Nur das erste Moment (m) zu löschen senkt π genauso (0.30 → 0.12) wie der volle Reset (0.11), obwohl die ersten Schritte danach **kleiner** sind (Update-Norm 0.25 gegen 0.27 normal, 0.42 beim vollen Reset). Das Überschreiben erklärt den Abfall also nicht, das **Momentum der ersten 25 Schritte trägt den größten Teil der Persistenz** (Pilot, Bestätigung an frischen Seeds ausstehend). Kandidat [[NOVEL_DIRECTIONS]] N28.
**Einordnung nach [[experiments/EXP-059-momentum-exposure/README|EXP-059]] (Sitzung 22, 07:22, 10 bekannte Seeds, Pilot):** Der Momentum-Anteil ist **verlängerte Exposition**, kein eigenes Gedächtnis: Mit gelöschtem m und 10 zusätzlichen A-Schritten liegt π mindestens so hoch wie normal bei t = 25 (0.36 gegen 0.30); m zu löschen kostet ≈ 6–10 A-Schritte. Die frühe Festlegung ist **sehr steil**: π_normal = 0.01 / 0.19 / 0.30 / 0.56 / 1.05 bei t = 10 / 20 / 25 / 35 / 50. Größte offene Frage für Programm B bleibt damit, **was** in den ersten ≈ 50 Schritten die Wahl so fest macht (nicht wo sie im Optimierer liegt). Bestätigung der engen Aussage: [[confirm/N28_REGISTRATION|N28]] (Entwurf).

## BESTÄTIGT (Sitzung 21, 27.09., 05:39 Berlin): P1, Steuerung der W_E-Repräsentation durch konstruierte Splits #befund/positiv

**Kernaussage K2-bestätigt** (Wortlaut nach Codex-Prüfung der Schlussfolgerung, 05:47): *Bei Schritt 2000 verschiebt eine konstruierte Auswahl der Trainingspaare die relative
W_E-Energie hin zu fünf vorgegebenen zyklischen Fourier-Frequenzen (bzw. D₅₉-Irreps), gemessen gegen fünf disjunkte Vergleichskomponenten. Das gilt in je 50 vorab registrierten,
frischen Seed/Split-Paaren für vier nach dem Pilot gewählte Aufgaben mit dem 1-Schicht-Transformer der Studie.* Das ist eine **zurückgehaltene Replikation** (held-out) der
Repräsentationssteuerung, **kein** Beleg für funktionale Nutzung.

| Aufgabe | Δ_pow (95-%-KI) | positiv | Holm-p (ungünstigster Fall) |
|---|---|---|---|
| add 113 (primär) | 8.24 [7.92, 8.54] | 50/50 | 1.5·10⁻⁵ |
| mul 113 | 8.09 [7.75, 8.43] | 50/50 | 1.5·10⁻⁵ |
| add 97 | 6.11 [5.79, 6.43] | 50/50 | 1.5·10⁻⁵ |
| D₅₉ | 2.64 [2.55, 2.73] | 50/50 | 1.5·10⁻⁵ |

Belege: [[confirm/P1_REGISTRATION_DRAFT|Registrierung + Ergebnis]], Manifest 733e829, 420 gebundene Läufe, `lab/confirm/P1_summary.json`. **Grenzen:** keine natürlichen Splits, keine
unverzerrte Aufgabenpopulation, eine Architekturfamilie, ein Zeitpunkt (2000). Δ_pow misst die relative Anreicherung eigener gegen fremde Ziele, keine Konzentration gegenüber der Init.
Der Kreuzblock (5 Einheiten × 3 Inits) zeigt „stabil über diese Inits“; der ICC ist bei 5 Einheiten ungenau und enthält die Wechselwirkung Init × Split.
**P2 (funktionale Nutzung): nicht auswertbar** (3/50 Modelle bei Schritt 2000 nicht generalisiert, Regel „alle gültig“). Beschreibend R̄ = 0.12 über 47, womöglich durch die Auswahl verzerrt.
Die Funktionsfrage bleibt **offen**; Nachfolger: [[confirm/P2_REGISTRATION_DRAFT|P2]] Ergebnisabschnitt. **P3** (Persistenz ohne geteilte Daten) ist eingefroren und läuft ([[confirm/P3_REGISTRATION_DRAFT|P3]]).

## Pilotnacht 27.09. (Sitzung 20, Stand 03:23 Berlin): K2 hält außerhalb von Addition mod 113

Alle Urteile vorab festgelegt, GPU nach bestandenem [[experiments/GPU-001-equivalence/README|GPU-001]] (gleichwertig zur CPU, ≈ 17× schneller). **Alles Piloten**, keine unabhängige Bestätigung.

| Fall | Versuch | Δ̄ (Maß) | n positiv | p | Urteil |
|---|---|---|---|---|---|
| Addition mod 97 | [[experiments/EXP-043-generalize-steering/README\|EXP-043]] | 7.7 (Top-5-Δ) | 10/10 | 0.001 (Holm) | *steuerbar* |
| Multiplikation mod 113 (≈ Z₁₁₂ + Null) | EXP-043 | 7.7 | 10/10 | 0.001 (Holm) | *steuerbar* |
| Diedergruppe D₅₉ (nicht-abelsch, Irreps) | [[experiments/EXP-046-dihedral-steering/README\|EXP-046]] | 9.6 | 10/10 | 0.001 | *steuerbar* |
| a + b ohne mod | [[experiments/EXP-048-intadd-steering/README\|EXP-048]] | 2.2 (Δ_pow, trendbereinigt) | 10/10 | 0.001 | *steuerbar* |
| 4× breiter (d = 512) | [[experiments/EXP-049-width-steering/README\|EXP-049]] | 7.8 (Δ_pow); d = 128: 8.7 | 10/10 | 0.001 | *steuerbar* |
| MLP statt Transformer (10 000 Schritte, nach dem Grokking) | [[experiments/EXP-045-mlp-steering/README\|EXP-045]] | 7.9 (Top-5-Δ; bei 2000: 10.0) | 10/10 | 0.001 | *steuerbar* |
| Mechanismus: Häufigkeiten gegen Paarstruktur (Z₁₁₃) | [[experiments/EXP-047-marginal-control/README\|EXP-047]] | Häufigkeiten 0.3 (n. s.); Paarstruktur 6.8 | 10/10 | 0.001 | *Paarstruktur trägt* |
| K4 frühe Festlegung (Wechsel F→G, ≈ 38 % geteilt) | [[experiments/EXP-044-generalize-lockin/README\|EXP-044]] | d(150) 3.3 / 3.5; Kipp zwischen t 25 und 50 | 10/10 je Aufgabe | 0.001 (Holm) | *festgelegt* (add 97, mul 113) |
| K1 an unberührten Fällen (eingefrorene Vorhersage, Paket C) | [[experiments/EXP-052-oos-mask-prediction/README\|EXP-052]] | ρ eigen 0.34–0.45, fremd ≈ 0 | 4/4 Fälle | 0.0002 (Holm) | *K1 gilt hier* (Assoziation) |
| Mechanismus: kohärentes M0c gegen M0 (Phasen-Dissoziation, Paket C) | [[experiments/EXP-050-phase-dissociation/README\|EXP-050]] | quadlm − anti 6.5; anti allein 1.4 | 10/10 / 10/10 | 0.001 (Holm) | *M0c selektiert*, aber M0 trägt auch (erste Ordnung nur halb) |
| Funktion (P2) | [[experiments/EXP-051-functional-ablation/README\|EXP-051]], [[experiments/EXP-055-ablation-dose/README\|EXP-055]] | Genauigkeit am Boden; ΔL primär n. s., Teildosen 10/10 (post hoc) | – | – | *unklar* |

**Lesart nach [[LESART-nacht-2026-09-27]] Regel 2:** Drei echt andere Aufgaben sind *steuerbar*, gefordert waren zwei. **K2 gilt damit über die gezeigten Aufgaben hinweg** (Pilotstufe):
anderer Primmodulus, zusammengesetzter Modulus, nicht-abelsche Gruppe, nicht-modulare Addition, 4× Breite. Grenze 4 (Mechanismus) ist für Z₁₁₃ zugunsten der Paarstruktur (M0) entschieden,
wie die Theorie erster Ordnung vorab vorhersagte. Offen bleiben: Bestätigung an frischen Seeds und Splits (P1), funktionale Nutzung je Energieeinheit (P2; Test-Loss bei Teildosis,
BACKLOG), Persistenz (K4) in den neuen Aufgaben (EXP-044), andere Architektur (EXP-045 MLP), Häufigkeiten gegen Paarstruktur in D₅₉ und int-add.
Nebenbefund (post hoc, [[NOVEL_DIRECTIONS]] Nachprüfung s20): Die gepflanzte Wahl klingt nach dem Grokking bis Schritt 2000 nicht ab. Das ist der Unterschied zu Zhou et al. 2024, der nächsten bekannten Vorarbeit.

## Programm (Regel 18c, festgelegt 2026-09-26 20:45 Berlin; Planungsgrundlage für alle neuen Versuche)

**Arbeitshypothese (Astra-Review Punkt 4):** Die *Zusammensetzung einer festen Trainingsmenge* (Full-Batch) steuert, welche
Frequenzen/Irreps ein Netz repräsentiert und nutzt, und diese Wahl ist nach kurzer Zeit gegen einen Datenwechsel persistent.
„Daten beeinflussen Frequenzen“ allein ist als Neuheit zu breit (Zhou et al. 2024, LeDoux 2026, AGF, He et al. 2026).

| Paket | Frage | Stand | Aktiv? |
|---|---|---|---|
| **A** | Split-Steuerung unabhängig replizieren, verallgemeinern **und funktional** nachweisen | Pilot/Verallgemeinerung vorbereitet: EXP-043, 045, 046, 047, 048, 049. Funktionaler Pilot: [[experiments/EXP-051-functional-ablation/README|EXP-051]] (Ablation an den EXP-047-Modellen gegen energiegleiche Kontrolle). K1 an unberührten Fällen (add 97, mul 113, D₅₉), Vorhersage vor den Läufen eingefroren: [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]]. **Fehlt:** unabhängiger Bestätigungsblock | ja |
| **B** | Persistenz nach Datenwechsel: F→G **und** G→F, kontrollierte Überlappung, festes Nachtrainingsbudget; „festgelegt“ = „nach B Schritten persistent“ | EXP-044 (bedingt auf EXP-043); CPU EXP-035–042 (`night_program.py --cpu`). Konkurrenzmodell: effektive Lernrate steuert die Merkmalsersetzung (Lyle et al. 2025, https://arxiv.org/abs/2507.20057) → EXP-039/040 trennen ELR und Datenauswahl. *Sitzung 14:* kontinuierliches Persistenzmaß π (post hoc an EXP-020: 0.15/0.38/0.72/≈1 bei t = 10/25/50/150), Überlappungskonstruktion [[experiments/EXP-053-p3-overlap-design/README|EXP-053]] (Entwurf), eingefrorene Uhr-Vorhersagen für EXP-039 und Lesarten (i)/(ii) für EXP-044 | ja |
| **C** | Eine mechanistische Vorhersage an unberührten Fällen | EXP-050 (M0c gegen M0, Kontrolle quadlm), Theorie erster Ordnung ([[BEFUND-split-mechanismus]]); *Sitzung 14:* [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]] (40 Vorhersagen aus dem Split, per Commit vor den Läufen eingefroren; läuft ohne eigene Läufe mit den Nacht-R-Armen) | vorbereitet, nicht aktiv |

Höchstens zwei Pakete aktiv (derzeit A und B). Andere Linien nur, wenn sie zwischen ausdrücklich genannten Konkurrenzmodellen entscheiden.

**Primäre Kernaussagen (vorläufig; werden erst nach der Pilotnacht mit Analysemanifest eingefroren):**
- **P1 (A):** Konstruierte Splits erhöhen die Leistung der Zielfrequenzen in W_E: Δ_pow > 0 auf frischen Seeds und Splits
  (Transformer, add 113), praktischer Mindesteffekt Δ_pow ≥ 1.
- **P2 (A, funktional):** Das Entfernen der Zielfrequenzen senkt die Testgenauigkeit stärker als das Entfernen energiegleicher anderer Frequenzen.
- **P3 (B):** Nach einem Wechsel bei t = 150 überwiegen die Frequenzen des ersten Splits nach 2000 Schritten auf dem zweiten, in beiden Richtungen. *Vor dem Einfrieren prüfen (Sitzung 14):* bei t = 150 liegt die Persistenz π an EXP-020 schon an der Decke (1.00 ± 0.04); empfindlicher ist t = 25 ([[BACKLOG]] „Wechselzeitpunkt für P3“).
- **Eine Bestätigungsfamilie P1–P3, Holm.** Effektgrößen mit 95-%-Konfidenzintervall (Bootstrap über Seeds) primär berichten.
- **Stichprobengröße:** Pilot EXP-016: Δ_pow 8.41 ± 1.20 (n = 10; ohne den doppelten Seed 19: 8.27 ± 1.19). Für P1 reicht damit
  der kontinuierliche Vorzeichen-Permutationstest mit wenigen Seeds; für neue Aufgaben ist die Streuung unbekannt → n aus der Pilotnacht.
  Nur-Vorzeichen-Zählregeln sind schwach (exakt gerechnet: n = 10 braucht ≥ 9/10, Power 38 % bei q = 0.8, 74 % bei q = 0.9;
  n = 12 braucht ≥ 10/12, 89 % bei q = 0.9). Ziel: Power ≥ 80 % für den vorab genannten Mindesteffekt.
- **Nullkalibrierung von Δ_pow (21:02, reine Nachrechnung gespeicherter Läufe):** Zufallssplits (EXP-003d-Baselines 10–19, Schritt 2000), zufällige disjunkte Zielmengen, F- und G-Lauf aus verschiedenen Seeds, 20 000 Ziehungen: Mittel −0.01, SD 0.48, 95-%-Quantil 0.79, |Δ_pow| ≥ 1 in 4 %. Der Mindesteffekt 1 liegt damit bei ≈ 2 Null-SD. Bei einer Streuung wie im Pilot EXP-016 (SD 1.2) braucht ein einseitiger Test auf Mittel ≥ 1 mit 80 % Power grob 10–12 Seeds (Normalnäherung, d ≈ 0.8); für neue Aufgaben mit der Pilotstreuung der Nacht neu rechnen.
- **Bestätigungsblock reserviert:** Init-Seeds **1000–1099**, Splits über `SeedSequence([1000001, Versuch, Seed, Arm, Zweck])`. *Präzisiert (Sitzung 14, vor jeder Nutzung):* `[1000001, Versuch, Aufgabe, p, Seed, Arm, Zweck]`, damit add 113 und mul 113 bei gleichem Seed keinen Strom teilen; Werkzeug `lab/tools/confirm_splits.py`, schreibt nur mit eingefrorenem Manifest. *Gekreuzter Split×Init-Block (Astra 5, Sitzung 16, vor jedem Lauf festgelegt, ungetestet):* Die ersten 5 Seeds von add 113 trainieren dieselben F/G-Splits zusätzlich mit 2 weiteren Inits (s + 200, s + 300, reserviert 1200–1399; 20 Zusatzläufe). Das ist sekundär und beschreibend und gehört nicht zur Holm-Familie. P1 zählt weiter nur ein Δ je Seed. Berichtet werden die Varianzanteile Einheit (Split-Paar + Ziele) gegen Init. Lesart: „stabil über Inits“ bei ≥ 90 % Δ > 0 und Init-SD < Mittel/2; „init-abhängig“ bei < 75 % oder Init-SD ≥ Mittel; sonst „gemischt“. Die P1-Einheit hält die Init schon fest (F und G mit derselben Init) und zieht Init, Ziele und beide Splits aus getrennten Strömen. Der Kreuzblock ergänzt die fehlende Richtung: derselbe Split mit anderer Init.
  Erst öffnen, wenn das Analysemanifest (Commit-ID) eingefroren ist. Jede Registrierung nennt „bereits gesehene Daten und davon
  beeinflusste Entscheidungen“. Bereits ausgewertete Seeds sind keine unabhängige Bestätigung.
- **Zweiter Bestätigungsblock reserviert (Sitzung 22, 2026-09-27, vor jeder Nutzung):** Seeds **2000–2099** für [[confirm/P2b_REGISTRATION|P2b]] (Splits `confirm_splits` mit Versuchs-ID 2), **2200–2229** für [[confirm/N28_REGISTRATION|N28]] (EXP-053-Splits, ω = 0). 2230–2299 bleiben frei. *Nachtrag 08:06:* P2b abgebrochen (Designfehler, Seeds 2000–2099 verbraucht); **2100–2199** für [[confirm/P2c_REGISTRATION|P2c]] (Versuchs-ID 3), vor jeder Nutzung. Familie Sitzung 22 = {N28-H1, N28-H2, P2b}, Holm.
- **Messgrößen getrennt:** Repräsentationsenergie (Δ_pow, kontinuierlich), funktionale Nutzung (Ablation), Persistenz (nach B Schritten).
  Korrelationen nicht als direkte Wirkung formulieren (z. B. EXP-030 nur als konditionale Assoziation).

**Einschränkung zu K2 (Astra Punkt 5, selbst geprüft):** EXP-016 ist ein starker Befund, aber die Unabhängigkeit der Seeds ist
eingeschränkt: Seed 12/G und 19/F haben einen identischen Split, 10/G ↔ 17/F und 11/G ↔ 18/F teilen Phasen und Zufallsschlüssel
(EXP-016 Nachtrag c). Die Sensitivität „ohne Seed 19“ (n = 9) beseitigt nicht alle Abhängigkeiten. Neue Versuche (ab EXP-047)
nutzen getrennte Ströme (`SeedSequence`); für eine Bestätigung zählen nur unabhängige Seeds und Splits.

## Kernaussagen mit Belegen

| # | Aussage | Beleg (vorab festgelegt, sofern nicht anders markiert) | Literatur |
|---|---|---|---|
| K1 | **Der Trainingssplit sagt die gelernten Frequenzen voraus** (Masken-Spektrum M0, ohne Gewichte). | [[experiments/EXP-015-mask-spectrum/README\|EXP-015]]: frische Seeds 10–17, r̄ 0.277 vs. fremde Masken 0.499, p 2.5e-5. Assoziation. | Frequency Principle (Zhou et al. 2024) verwandt, andere Aufgaben; M0 für Z_p nicht gefunden |
| K2 | **Die Frequenzwahl ist über die Daten steuerbar.** Konstruierte Splits geben die gelernten Frequenzen vor. | [[experiments/EXP-016-engineered-split/README\|EXP-016]]: 10/10 Seeds, Δ̄ +7.7 von 10, p ≈ 0.001; Abweichungen 2k-Oberwellen der Ziele | LeDoux 2026 (Datenreihenfolge), He et al. 2026 (Init-Lotterie); kausale Split-Steuerung nicht gefunden |
| K3 | Der erste Gradient an W_E sagt die Wahl besser voraus als die Init. | [[experiments/EXP-012-init-gradient/README\|EXP-012]]: r̄ 0.254 vs. 0.369, p 0.031 | — |
| K4 | **Die Wahl legt sich sehr früh fest**, weit vor Memorisierung und Grokking. | [[experiments/EXP-020-data-switch/README\|EXP-020]] (5 Seeds): Dominanzmaß kippt bei Wechsel nach (25, 50] Schritten in 5/5 (beschreibend; Urteil *nicht bestätigt* 4/5); exakt „nur F“ ab t = 150. [[experiments/EXP-032-early-lockin/README\|EXP-032]] (Zwei-Hot-Netz, anderes Protokoll): halbe End-Neigung nach 5 Schritten, p 1e-4. *Post hoc kontinuierlich (Sitzung 14):* Persistenz π(t) an EXP-020 0.15 / 0.38 / 0.72 / 1.00 bei t = 10 / 25 / 50 / 150 (5 Seeds, enge Streuung). *Sitzung 15 (post hoc):* π und die ganze Spektrumsform ändern sich nach Schritt 250 in der G-Phase kaum (Mischung spätestens dann gesetzt); Top-5-Kreuzungen hängen auch unter reinem Takt von der Stärke des zweiten Splits ab → Zeitfragen mit π | Kritische Perioden (Achille 2019) allgemein; Festlegungszeit der Frequenzwahl nicht gefunden |
| K5 | Die frühe Festlegung braucht AdamW in der ersten Phase nicht. | [[experiments/EXP-033-optimizer-lockin/README\|EXP-033]]: GD 10/10 (eingeschränkt: Phase 2 immer AdamW) | — |
| K6 | Datenauswahl und Aktivierung zusammen bestimmen die Frequenzen (ReLU folgt dem Split, x² nur richtungsgleich). | [[experiments/EXP-024-quadratic-agf-mask/README\|EXP-024]] (ReLU bestätigt, aber memorierend; x² n. s.) | AGF (Kunin et al. 2025) |

**Negativ / nicht gezeigt:** Die natürliche Split-Konzentration sagt die Grokking-Zeit nicht voraus (Sitzung 5, post hoc);
Breitenabhängigkeit der Split-Auswahl verworfen ([[experiments/EXP-027-width-selection/README\|EXP-027b]]); Init-Tausch
([[experiments/EXP-010-init-swap/README\|EXP-010]]) bisher 1/10 Paare.

## Wichtigste Grenzen

1. **Eine Aufgabe, ein Modulus, im Kern eine Architektur.** Nichts ist an Multiplikation, anderem p, tieferen Modellen oder einer
   nicht-modularen Aufgabe geprüft.
2. K4 nur gegen einen Teilwechsel (F und G teilen ≈ 73 % der Paare); der harte Test [[experiments/EXP-041-imprint/README|EXP-041]] läuft nachts.
3. Viele Einzelversuche mit 3–5 Seeds; ab jetzt ≥ 10 Seeds für Urteile (Regel 15b).
4. **K2-Mechanismus nicht eindeutig (Sitzung 12):** Die konstruierten Splits verzerren auch das Spektrum der bloßen Token-Häufigkeiten
   zu den Zielen hin (Zielrang 14.5 von 56, Zufall 27.5). Ob die Steuerung über die Paarstruktur (M0) oder über die Häufigkeiten läuft,
   prüft [[experiments/EXP-047-marginal-control/README|EXP-047]] (gemischte Kontrolle mit exakt gleichen a/b-Häufigkeiten).
   *Theorie (Sitzung 13, erste Ordnung, vorab notiert):* Bei gleichverteilter Ausgabe fällt der Häufigkeitsanteil aus dem ersten
   W_E-Gradienten exakt heraus (er sieht nur das „zentrierte M0“); Erwartung für EXP-047 deshalb: Häufigkeiten allein steuern nicht.

## Größte offene Frage

*Stand Sitzung 20: für K2 im Pilot beantwortet (ja, siehe „Pilotnacht“ oben). Neue größte offene Frage: Hält K2 im vorab eingefrorenen Bestätigungsblock, und gilt K4 in den neuen Aufgaben?* **Verallgemeinern K2 (Steuerung über die Daten) und K4 (frühe Festlegung) über Addition mod 113 hinaus?** Nächster Test:
[[experiments/EXP-043-generalize-steering/README|EXP-043]] (Modulus 97 und Multiplikation mod 113, GPU, 10 Seeds je Aufgabe;
Multiplikation ist nach Umbenennung der Token fast exakt Addition mod 112, also vor allem ein Test eines *zusammengesetzten*
Modulus), [[experiments/EXP-044-generalize-lockin/README|EXP-044]] (K4 dort, bei ≈ 62 % neuen Paaren) und
[[experiments/EXP-045-mlp-steering/README|EXP-045]] (andere Architektur) und
[[experiments/EXP-046-dihedral-steering/README|EXP-046]] (**nicht-abelsche** Gruppe D₅₉, erste echt andere Aufgabe).
[[experiments/EXP-048-intadd-steering/README|EXP-048]] (**nicht-modulare** Addition a + b, deren bekannte Lösung eine Zahlengerade ist;
Primärgröße Log-Leistungskontrast, an EXP-016 kalibriert).
Wie die Kombination der Nachtergebnisse zu lesen ist, steht vorab in [[LESART-nacht-2026-09-27]].
Danach: Uhr-Frage (Λ-Uhr / Amplitudenschwelle, EXP-039/040) nur, soweit die Verallgemeinerung trägt.

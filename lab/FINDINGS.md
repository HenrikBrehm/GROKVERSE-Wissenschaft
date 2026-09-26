---
id: FINDINGS
status: laufend
datum: 2026-09-26
tags: [lab/synthese]
verwandt: ["[[LAB]]", "[[BEFUND-split-mechanismus]]", "[[BEFUND-festlegung]]", "[[NOVEL_DIRECTIONS]]"]
---
# FINDINGS: Kernaussagen des Labors (eine Seite)

Zurück zu [[LAB]]. Stand 2026-09-26, Sitzung 13 (nach 48 angelegten Versuchen; Kernaussagen seit Sitzung 11 unverändert, keine neuen Läufe). „Neu“ heißt immer: nach unserer Suche vom
2026-09-26 nicht gefunden, vorläufig. **Alle Aussagen gelten bisher nur für eine Aufgabe (Addition mod 113) und im Kern eine
Architektur (1-Schicht-Transformer der Studie, AdamW, lr 1e-3, wd 1).** Einzelheiten: [[BEFUND-split-mechanismus]], [[BEFUND-festlegung]].

## Programm (Regel 18c, festgelegt 2026-09-26 20:45 Berlin; Planungsgrundlage für alle neuen Versuche)

**Arbeitshypothese (Astra-Review Punkt 4):** Die *Zusammensetzung einer festen Trainingsmenge* (Full-Batch) steuert, welche
Frequenzen/Irreps ein Netz repräsentiert und nutzt, und diese Wahl ist nach kurzer Zeit gegen einen Datenwechsel persistent.
„Daten beeinflussen Frequenzen“ allein ist als Neuheit zu breit (Zhou et al. 2024, LeDoux 2026, AGF, He et al. 2026).

| Paket | Frage | Stand | Aktiv? |
|---|---|---|---|
| **A** | Split-Steuerung unabhängig replizieren, verallgemeinern **und funktional** nachweisen | Pilot/Verallgemeinerung vorbereitet: EXP-043, 045, 046, 047, 048, 049. **Fehlt:** funktionaler Test (gespeicherte Modelle, Ablation der Zielfrequenzen auf gemeinsamer Testmenge gegen energiegleiche Kontrollablation) und ein unabhängiger Bestätigungsblock | ja |
| **B** | Persistenz nach Datenwechsel: F→G **und** G→F, kontrollierte Überlappung, festes Nachtrainingsbudget; „festgelegt“ = „nach B Schritten persistent“ | EXP-044 (bedingt auf EXP-043); CPU EXP-035–042 in queue_s10 (historisch festgelegt, laufen zu Ende) | ja |
| **C** | Eine mechanistische Vorhersage an unberührten Fällen | EXP-050 (M0c gegen M0, Kontrolle quadlm), Theorie erster Ordnung ([[BEFUND-split-mechanismus]]) | vorbereitet, nicht aktiv |

Höchstens zwei Pakete aktiv (derzeit A und B). Andere Linien nur, wenn sie zwischen ausdrücklich genannten Konkurrenzmodellen entscheiden.

**Primäre Kernaussagen (vorläufig; werden erst nach der Pilotnacht mit Analysemanifest eingefroren):**
- **P1 (A):** Konstruierte Splits erhöhen die Leistung der Zielfrequenzen in W_E: Δ_pow > 0 auf frischen Seeds und Splits
  (Transformer, add 113), praktischer Mindesteffekt Δ_pow ≥ 1.
- **P2 (A, funktional):** Das Entfernen der Zielfrequenzen senkt die Testgenauigkeit stärker als das Entfernen energiegleicher anderer Frequenzen.
- **P3 (B):** Nach einem Wechsel bei t = 150 überwiegen die Frequenzen des ersten Splits nach 2000 Schritten auf dem zweiten, in beiden Richtungen.
- **Eine Bestätigungsfamilie P1–P3, Holm.** Effektgrößen mit 95-%-Konfidenzintervall (Bootstrap über Seeds) primär berichten.
- **Stichprobengröße:** Pilot EXP-016: Δ_pow 8.41 ± 1.20 (n = 10; ohne den doppelten Seed 19: 8.27 ± 1.19). Für P1 reicht damit
  der kontinuierliche Vorzeichen-Permutationstest mit wenigen Seeds; für neue Aufgaben ist die Streuung unbekannt → n aus der Pilotnacht.
  Nur-Vorzeichen-Zählregeln sind schwach (exakt gerechnet: n = 10 braucht ≥ 9/10, Power 38 % bei q = 0.8, 74 % bei q = 0.9;
  n = 12 braucht ≥ 10/12, 89 % bei q = 0.9). Ziel: Power ≥ 80 % für den vorab genannten Mindesteffekt.
- **Bestätigungsblock reserviert:** Init-Seeds **1000–1099**, Splits über `SeedSequence([1000001, Versuch, Seed, Arm, Zweck])`.
  Erst öffnen, wenn das Analysemanifest (Commit-ID) eingefroren ist. Jede Registrierung nennt „bereits gesehene Daten und davon
  beeinflusste Entscheidungen“. Bereits ausgewertete Seeds sind keine unabhängige Bestätigung.
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
| K4 | **Die Wahl legt sich sehr früh fest**, weit vor Memorisierung und Grokking. | [[experiments/EXP-020-data-switch/README\|EXP-020]] (5 Seeds): Dominanzmaß kippt bei Wechsel nach (25, 50] Schritten in 5/5 (beschreibend; Urteil *nicht bestätigt* 4/5); exakt „nur F“ ab t = 150. [[experiments/EXP-032-early-lockin/README\|EXP-032]] (Zwei-Hot-Netz, anderes Protokoll): halbe End-Neigung nach 5 Schritten, p 1e-4 | Kritische Perioden (Achille 2019) allgemein; Festlegungszeit der Frequenzwahl nicht gefunden |
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

**Verallgemeinern K2 (Steuerung über die Daten) und K4 (frühe Festlegung) über Addition mod 113 hinaus?** Nächster Test:
[[experiments/EXP-043-generalize-steering/README|EXP-043]] (Modulus 97 und Multiplikation mod 113, GPU, 10 Seeds je Aufgabe;
Multiplikation ist nach Umbenennung der Token fast exakt Addition mod 112, also vor allem ein Test eines *zusammengesetzten*
Modulus), [[experiments/EXP-044-generalize-lockin/README|EXP-044]] (K4 dort, bei ≈ 62 % neuen Paaren) und
[[experiments/EXP-045-mlp-steering/README|EXP-045]] (andere Architektur) und
[[experiments/EXP-046-dihedral-steering/README|EXP-046]] (**nicht-abelsche** Gruppe D₅₉, erste echt andere Aufgabe).
[[experiments/EXP-048-intadd-steering/README|EXP-048]] (**nicht-modulare** Addition a + b, deren bekannte Lösung eine Zahlengerade ist;
Primärgröße Log-Leistungskontrast, an EXP-016 kalibriert).
Wie die Kombination der Nachtergebnisse zu lesen ist, steht vorab in [[LESART-nacht-2026-09-27]].
Danach: Uhr-Frage (Λ-Uhr / Amplitudenschwelle, EXP-039/040) nur, soweit die Verallgemeinerung trägt.

---
id: FINDINGS
status: laufend
datum: 2026-09-27
tags: [lab/synthese]
verwandt: ["[[LAB]]", "[[FINDINGS_DETAILS]]", "[[BEFUND-split-mechanismus]]", "[[BEFUND-festlegung]]", "[[NOVEL_DIRECTIONS]]"]
---
# FINDINGS: Kernaussagen des Labors (eine Seite)

Zurück zu [[LAB]]. Stand Sitzung 24, 2026-09-27, 13:00 Berlin. Wortlaute, Konfidenzintervalle, Registrierungen und die Programmgeschichte stehen unverändert in [[FINDINGS_DETAILS]].
**Geltungsbereich aller Aussagen:** 1-Schicht-Transformer der Studie (arch25k), AdamW (lr 1e-3, wd 1), Full-Batch, konstruierte Splits. „Neu“ heißt immer: nach unserer Suche nicht gefunden, vorläufig.

## Kernaussagen (bestätigt an frischen, vorab reservierten Seeds mit eingefrorenem Analysemanifest)

| | Aussage (kurz) | Beleg | Stand |
|---|---|---|---|
| **K2** | Konstruierte Trainingssplits steuern, welche Frequenzen/Irreps W_E lernt: add 113, mul 113, add 97, D₅₉ | P1 (50 Seeds je Aufgabe) | bestätigt |
| **K2-Funktion** | Gleich große W_E-Schritte entlang der gesteuerten Frequenzen senken den Logit-Abstand stärker als entlang von Kontrollen: add 113, mul 113, add 97 | P2d, P2e (je 20 Seeds) | bestätigt; **folgt der Energie**, keine Nutzung darüber hinaus belegt (EXP-068) |
| **K4 / K4b** | Schon 25 Schritte auf dem ersten Split prägen das Endspektrum nach einem Wechsel; ein gelöschtes Adam-Momentum wirkt wie weniger Vorschritte | P3, N28 | bestätigt |
| **K4c** | Wechsel nach 25 Schritten: Endmodell auf die neuen Frequenzen angewiesen; nach 50: auf die alten | N29 | bestätigt (Ablationskontrast) |
| **K4d** | Reset der Attention (Gewichte + AdamW-Zustand) beim Wechsel nach 50 Schritten senkt diesen Kontrast stark, stärker als der geprüfte MLP-Reset | N29b | bestätigt (Reset-Empfindlichkeit, kein Speicherort) |
| **K4e** | Reset des Wertepfads (W_V, W_O) wirkt stärker als der gleich große Reset des Musters (W_Q, W_K) | N29c | bestätigt (Reset-Empfindlichkeit) |

**Explorationen mit Gewicht für die Planung (bekannte Seeds, kein Urteil):**
- **D₅₉ groks, die Steuerung überlebt** ([[experiments/EXP-072-d59-grok/README|EXP-072]], 5 Seeds × 2 Arme): 9/10 generalisieren (erster Test ≥ 0.9 bei Median 4575 Schritten); am Ende tragen die eigenen Ziel-Irreps 0.90–0.99 der W_E-Energie;
  Irrep-Form des K2-Funktionsmaßes D = 0.22 ± 0.02 (5/5). K2 aus P1 (2000 Schritte) betraf also nur die Phase vor dem Grokking. Bestätigung: [[confirm/P2f_REGISTRATION|P2f]] (vorbereitet).
- **Festlegung ist keine Schwelle:** π steigt glatt mit der Zahl der Schritte auf dem ersten Split (EXP-059: 0.01 → 1.05 für t = 10 → 50). Weder der W_E-Vorsprung (EXP-060) noch die OV-Ausrichtung
  (EXP-070, [[experiments/EXP-071-ov-lead-predicts/README|EXP-071]]) erklären den zeitlichen Verlauf besser als die Schrittzahl; OV sagt π je Seed höchstens schwach voraus (r = 0.45, p = 0.09, n = 10).

## Grenzen

1. **Funktion folgt Energie** (EXP-064 post hoc, EXP-068): Bei gleicher entfernter Energie hat die dominante Menge keinen Vorteil. Alle Funktionsbefunde sind mit „mehr Amplitude, entlang derer das Netz empfindlich ist“ vereinbar.
2. Persistenz- und Reset-Befunde (K4–K4e) nur bei add 113 und einer Architektur; Resets zeigen Empfindlichkeit, keinen Mechanismus (Gewichte und Optimiererzustand gemeinsam).
3. Keine nicht-modulare Aufgabe bestätigt; keine tiefere Architektur bestätigt.
4. K2 bei EXP-016 hatte abhängige Seeds (Astra 5); die Bestätigungen P1ff. nutzen getrennte Ströme.

## Einordnung in die Literatur (Suchen dokumentiert in [[NOVEL_DIRECTIONS]] und [[FINDINGS_DETAILS]])

- *Bekannt:* Daten und Training beeinflussen, welche Frequenzen gelernt werden (Frequency Principle, Zhou et al. 2024; Datenreihenfolge, LeDoux 2026; Init-Lotterie, He et al. 2026; AGF, Kunin et al. 2025;
  **Reihenfolge der Irreps durch die Fourier-Statistik der Eingabekodierung bei gleichverteilten Daten, auch D_n: Marchetti et al., ICML 2026**);
  kritische Perioden allgemein (Achille et al. 2019); Merkmalsersetzung über die effektive Lernrate (Lyle et al. 2025).
  *Ergänzt Sitzung 25 (Volltextprüfung, [[paper/fulltext_check_2026-09-27]]):* Teil-Resets in Transformern: in Sprachmodellen stellt ein Re-Init der Query-Key-Anteile die Lernfähigkeit her, Value-Anteile nicht (Dong 2026, arXiv 2607.27281); Frequenzidentität im selben Modelltyp über die Gewichtsrichtung übertragbar (Khanh 2026, arXiv 2607.06628).
  *Ergänzt Sitzung 26:* Vorwärtszitate über die Semantic-Scholar-API (9 Ausgangsarbeiten, zitierende Arbeiten bis 2026-09-23; [[paper/related_work]] Nachtrag) ohne einschränkenden Treffer; Kernel-Vorläufer zu K2: Tomàs Bernal et al. 2026 (Symmetriebruch der Trainingsmenge entscheidet, *ob* ein RFM-Kernel generalisiert); Komponentenrollen im gleichen Modelltyp ohne Resets: Jia 2026.
- *Nach unserer Suche nicht gefunden (vorläufig):* kausale Steuerung der Frequenz-/Irrep-Wahl über die Split-Zusammensetzung, auch in einer nicht-abelschen Gruppe (K2);
  eine gemessene Festlegungszeit der Frequenzwahl von ≈ 25–50 Schritten gegen einen Datenwechsel (K4–K4c); die Reset-Empfindlichkeit des Attention-Wertepfads dafür (K4d/e, N32; „Attention-Reset > MLP-Reset“ allein ist nach Dong 2026 nicht neu, unsere Reihenfolge Wertepfad > QK ist dort umgekehrt).

## Programm (Regel 18c)

**A** (aktiv) Verallgemeinerung: nächster Block P2f (D₅₉, Funktionsmaß). **B** (aktiv) Persistenz: Mechanismus der glatten Festlegung offen. **C** ruht.
**Veröffentlichung** (Regel 19, gleichgewichtig): [[paper/STATUS]] · Entwurf [[paper/draft]] · Literatur [[paper/related_work]] · Robustheit [[confirm/R1_REGISTRATION_DRAFT|R1]], Piloten [[confirm/P4_REGISTRATION_DRAFT|P4]].

## Größte offene Frage

**Was macht die frühe Wahl gegen einen Datenwechsel fest, wenn keine gemessene Zustandsgröße den Zeitverlauf besser erklärt als die Schrittzahl?** Die Reset-Befunde (K4d/e) zeigen, *wo* ein Eingriff wirkt,
nicht *warum* die Festlegung glatt mit den Vorschritten wächst. Kandidaten vorab: **Amplitudenrennen unter Adam** (Zielamplituden wachsen ≈ linear in der aufsummierten Lernrate und legen fest, sobald sie die Init-Amplitude der
Konkurrenz einholen; H40, direkter Test [[experiments/EXP-040-we-init-scale/README|EXP-040]], passt zu EXP-039 „Λ-Uhr besser“ und EXP-059 „Momentum = Vorschritte“); welcher Netzteil dafür empfindlich ist
([[experiments/EXP-073-part-rewind/README|EXP-073]]); Zustand des Adam-Zweitmoments. Zweite offene Frage: Hält K2-Funktion bei D₅₉ (P2f)?

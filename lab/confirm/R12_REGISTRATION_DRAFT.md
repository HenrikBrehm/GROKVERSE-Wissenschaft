---
id: R12
status: eingefroren
datum: 2026-09-30
tags: [lab/confirm, programm/A, paper, exp/vorbereitet]
---
# R12: Beschleunigen konstruierte Splits das Grokking auch bei add 97 und mul 113? (Registrierungsentwurf, Sitzung 57)

Zurück: [[LAB]] · [[FINDINGS]] · Vorlage: [[confirm/R5_REGISTRATION_DRAFT|R5]] (add 113, bestätigt) · Pilot: [[experiments/EXP-043-generalize-steering/README|EXP-043]] · [[JOURNAL]] Sitzung 57.

Geschrieben 2026-09-30 ab 05:55 Berlin (gemessen), **vor jedem R12-Lauf**. Code: `lab/tools/confirm_r12.py` (Selbsttest grün, 05:54, über den Wächter).

## Warum (Bezug zu FINDINGS / Paper)

Ergebnis 2 des Papers (R5: konstruierte Splits generalisieren ×6.5 früher als Zufall, ×7.5 früher als die je Ausgabe abgeglichene Kontrolle D) gilt bisher **nur für add 113**; die Kurzfassung nennt das in §7 (ii) als Grenze. Regel 15c/19a: Verallgemeinerung eines Hauptbefunds vor Detailversuchen. Pilot: EXP-043 zeigt die Beschleunigung post hoc bei add 97 und mul 113 (je 10/10 Seeds, Komplement-Testmengen, nur E gegen R, ohne D, Ereignis „erste Kreuzung“). Kein neuer Kernsatz, sondern der Geltungsbereich eines bestehenden (Regel 20a).

## Aufbau (gilt; Einzelheiten im Docstring von `confirm_r12.py`)

- **Wie R5**, übertragen in die Gruppenkoordinaten von EXP-043 (add p: u = a, v = b; mul p: diskreter Logarithmus, Gruppe Z_{p−1}; Paare mit einer 0 behalten Gewicht 1). Dosis-Arme von R5 entfallen.
- **Aufgaben:** add 97 und mul 113. Je Aufgabe **20 Einheiten**, Init-Seeds reserviert **add 97: 4200–4219, mul 113: 4220–4239** (eingefrorene Zufallszuordnung `INIT_PERM`), eigene Zufallsströme `SeedSequence([20260930, Aufgabe, Einheit, …])`, keiner aus dem Init-Seed.
- **Je Einheit:** gemeinsame Testmenge T*_u (20 % aller p² Paare), fünf Trainingsmengen à round(0.3 p²) Paare (add 97: 2823, mul 113: 3831): **R** gleichverteilt; **E2_0/E2_1** EXP-043-Konstruktion (ε = 2, Ziele A bzw. B, je 5 aus k = 1..(n−1)/2, unabhängig von der Init); **D_0/D_1** je Ausgabewert c = a ∘ b mod p genau so viele Paare wie die realisierte E-Maske, Positionen gleichverteilt, neu gezogen bis zu den R5-Toleranzen (Grad-CV, Tauschanteil, Test-Tauschanteil ≤ 0.04; Testnachbarschaft ≤ 0.02; zusammenhängend; M0-Zielanteil ≤ M/K + 0.031, d. h. add 97 0.135, mul 113 0.122 – gleicher Abstand zum Gleichverteilungsanteil wie R5s 0.12 bei add 113).
- *Klarstellungen nach der Codeprüfung (vor dem Smoke-Check um 06:05):* Die Zielmengen A und B werden unabhängig gezogen und dürfen sich überschneiden (wie R5; über die 20 Einheiten 10 bzw. 7 gemeinsame Ziele); E2_0 und E2_1 teilen Pool und Schlüsselvektor. D wird gegen E auf allen fünf R5-Größen abgeglichen (Grad-CV von a und von b, Tauschanteil, Test-Tauschanteil, Testnachbarschaft). Der Lader prüft zusätzlich `train_frac` = 0.3 und wertet eine fehlende oder nicht endliche Endgenauigkeit als Defekt.
- **Offline-Kennzahlen der Splits (vor jedem Lauf, alle 40 Einheiten):** M0-Zielanteil E 0.196 / 0.183, D 0.105 / 0.090, R 0.105 / 0.091 (add 97 / mul 113); D-Unterstrom höchstens 1.
- **Training:** freq_ban, GPU, `--threads 1`, 8000 Schritte ohne vorzeitigen Stopp, Spektrum bei 250; 200 Läufe in eingefrorener Zufallsreihenfolge, über den GPU-Dienst (Regel 21).
- **Ereignis und Zeit wie R5:** erste Testauswertung s mit Test ≥ 0.95 bei s, s+25, s+50 und vorheriger Memorisation (Train ≥ 0.99); sonst zensiert bei 8000; b = min(Ereignis, 8000).
- **Primärfamilie (Holm über 4 bei 0.05; je Kontrast p = max(p_flip, p_Vorzeichen), scharfe Randomisierungs-Null wie R5), je Aufgabe:**
  - **H-ER:** L = log2 b(R) − log2 b(E2_0) > 0.
  - **H-ED:** L = Mittel_j [log2 b(D_j) − log2 b(E2_j)] > 0.
- **Effektgröße:** 2^L̄ (geometrisches Mittel des Verhältnisses der beschränkten Zeiten) mit 95-%-Bootstrap-KI. Kein Schwellenwert als Urteilskriterium.
- **Gültigkeit:** ein fehlender oder defekter Lauf, eine fehlerhafte Verlaufsaufzeichnung oder eine Identitätsverletzung (Seed, Gerät, Budget, Split-/Test-Hash, Aufgabe/p, Init-Prüfsumme je Einheit) → **ganzer Block nicht auswertbar**; Ausfälle werden vorher identisch neu eingereiht (Lauf-Wiederholung, kein neues Design).
- **Beschreibend (kein Urteil):** Ereignisse je Arm bis 2000/8000, Median der beschränkten Zeiten, erste Kreuzung, Endgenauigkeit; W_E-Zielanteil bei 250 **nur für add 97** (spectra.npy ist die additive DFT, für mul nicht die Gruppenbasis).

## Stichprobengröße (ehrlich)

n = 20 je Aufgabe wie R5, **keine Poweranalyse**: Für H-ER gibt es einen Pilot (EXP-043, 10/10 je Aufgabe, bei R5 lag die Power bei n = 20 mit ähnlichen Effekten über 0.8); **für H-ED gibt es auf diesen Aufgaben keinen Pilot**. Ein „nicht bestätigt“ bei H-ED ist deshalb kein Beleg für Wirkungslosigkeit.

## Was dagegen spräche

- H-ER nicht bestätigt: Die Beschleunigung ist eine Eigenheit von add 113 (oder hängt an p/Gruppenordnung); Ergebnis 2 bleibt auf add 113 beschränkt.
- H-ER bestätigt, H-ED nicht: Auf diesen Aufgaben reicht die Ausgabeverteilung der konstruierten Maske; die Deutung „Anordnung innerhalb der Ausgabeklassen“ gilt dann nur für add 113.
- Unterschiedliche Ausgänge für add 97 und mul 113 → Befund „hängt von der Aufgabe ab“, so ins Paper.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-043 (Seeds 70–79, add 97/mul 113, E gegen R, 2000 Schritte; beeinflusst: Wahl der Aufgaben, Erwartung für H-ER), EXP-044 und R11 (Seeds 80–89 bzw. 3620–3649, gleiche Aufgaben, Festlegung, nicht Geschwindigkeit ausgewertet), R5 (add 113, beeinflusst: das gesamte Design, Toleranzen, n). **Smoke (Sitzung 57):** ein add-97-Lauf (E2_0) und ein mul-113-Lauf (D_1) auf den Splits von Einheit 0 mit Init-Seed **4299** (außerhalb des reservierten Bereichs), in `lab/confirm/r12_smoke/`; geprüft werden nur technische Felder (Lader, Verlaufsraster, Hashes; `lab/confirm/R12_smoke_check.py` → `R12_smoke.txt`, 06:05 grün, falsche Split-Datei wird abgelehnt). Offen gesehen, weil der Trainer sie ins Log schreibt: erste Kreuzung E2_0 add 97 bei 1175, D_1 mul 113 bei 6300 (je 1 Lauf, anderer Init-Seed); am Design ändert das nichts. Laufzeit unter Last 0.065 bzw. 0.043 s/Schritt. Kein Lauf mit den reservierten Seeds vor dem Einfrieren.

## Grenzen (vorab)

Eine Architektur (1-Schicht-Transformer), eine Optimierer-Einstellung (AdamW lr 1e-3, wd 1, Full-Batch), ε = 2, 30 % Trainingsanteil; „schneller“ heißt früherer stabiler Testanstieg auf T*, Horizont 8000 Schritte.

## Ergebnis (Sitzung 60, 30.09., 15:50 Berlin gemessen; eingefrorene Auswertung, Manifest-Commit 8e6f9b3f)

Befehl: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r12.py --analyze lab/confirm/R12_manifest.json` → `R12_summary.json`. 200/200 Läufe (Dienst `44_r12`, 0 Fehlschläge), 0 technische Ausfälle.

| Aufgabe | Hypothese | Zeitverhältnis (geom.) [95 %-KI] | Einheiten mit richtiger Ordnung | p (Holm über 4) | Urteil |
|---|---|---|---|---|---|
| add 97 | H-ER (E2_0 gegen R, Zielmenge A) | ×4.50 [3.76, 5.40] | 20/20 | 4·10⁻⁵ | bestätigt |
| add 97 | H-ED (E2 gegen D, Mittel über beide Zielmengen) | ×4.60 [4.02, 5.24] | 20/20 | 4·10⁻⁵ | bestätigt |
| mul 113 | H-ER | ×7.42 [5.92, 9.06] | 20/20 | 4·10⁻⁵ | bestätigt |
| mul 113 | H-ED | ×7.14 [6.00, 8.36] | 20/20 | 4·10⁻⁵ | bestätigt |

p = Auflösungsgrenze des Permutationstests (1/100 001) vor Holm. Beschreibend: Medianzeit (zensiert bei 8 000) add 97 R 6 513, E2_0 1 338, D_0 8 000, E2_1 1 388, D_1 7 238; mul 113 R 6 813, E2_0 863, D_0 6 538, E2_1 938, D_1 7 300. Beobachtete Generalisierung bis 8 000: R 14/12, D_0 9/15, D_1 14/11 von 20 (add 97/mul 113; also NICHT generalisiert: R 6/8, D_0 11/5, D_1 6/9); konstruierte Arme 20/20. Korrektur der Tabellenbeschriftung H-ED nach Textprüfung (16:00): der Code mittelt über beide Zielmengen. Die Kontrollen erreichen die Grenze oft nicht; die Zensierung ist in der Auswertung registriert.

**Unabhängige Nachrechnung** (`R12_independent_recompute.py --analyze`, 15:52): identische Verhältnisse, Zeiten, p-Werte und Urteile („bestätigt“ ×4); KI weichen nur durch andere Bootstrap-Ziehungen ab (z. B. add 97 H-ER [3.76, 5.42]).

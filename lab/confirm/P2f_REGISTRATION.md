---
id: P2f-registrierung
status: vorbereitet
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[confirm/P2e_REGISTRATION|P2e]]", "[[confirm/P2d_REGISTRATION|P2d]]", "[[experiments/EXP-072-d59-grok/README|EXP-072]]", "[[experiments/EXP-046-dihedral-steering/README|EXP-046]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# P2f-Bestaetigung (P2d-Mass in Irrep-Form bei D59): Registrierung (Sitzung 24). **VORBEREITET, NOCH NICHT EINGEFROREN**

Zurueck zu [[FINDINGS]] (Programm A, "K2-Funktion (P2d)"; Regel 15c: Verallgemeinerung auf die einzige nicht-abelsche Aufgabe) · Pilot [[experiments/EXP-072-d59-grok/README|EXP-072]] ·
Vorgaenger [[confirm/P2e_REGISTRATION|P2e]] (mul 113, add 97, bestaetigt).

- **Aussage P2f:** In D59-Modellen (arch25k, group_train.py) mit konstruiertem Split senkt ein Parameterschritt gleicher Norm entlang der **eigenen Ziel-Irreps** (isotypische Komponenten
  der 2-dim Irreps in den Elementzeilen von W_E) den mittleren Logit-Abstand auf ungesehenen Paaren staerker als derselbe Schritt entlang gleich grosser Kontroll-Irrep-Mengen.
  Aussage ueber eine lokale endliche Stoerung (delta = 2 % von ||X||), nur W_E, eine Perturbationsform; Mittel ueber alle 20 Seeds nach 12000 Schritten.
- **Modelle:** frische Seeds **2340-2359** (n = 20), je Arm F und G, `confirm_splits.build` mit Versuchs-ID **6**, Aufgabe D, n = 59, eps 2.0,
  `group_train.py --steps 12000 --save-model`, GPU, 1 Thread. 40 Laeufe.
- **Mass:** wie EXP-072 Nachtrag a: X = W_E[:118], P_S = Projektion auf die 4 Spalten je Irrep k in S der Basis `dihedral.irrep_basis(59)`; u_S = P_S X / ||P_S X||, X' = X - delta u_S;
  drop_S = Logit-Abstand vorher - nachher auf den Paaren in keinem der beiden Splits. 4 Kontrollmengen je Arm aus 1..29 ohne eigene, fremde Ziele und fold(2k) der eigenen
  (RNG [6, 59, Seed, Arm]). **Primaer:** D_s = Mittel ueber beide Arme von (drop_eigen - Mittel drop_Kontrolle). Einseitiger t-Test (Mittel > 0), 95-%-Bootstrap-KI.
- **Familie:** eine Hypothese (keine Holm-Korrektur noetig).
- **Sekundärhypothese S1 (eigene Bezeichnung, nicht Teil des primären Urteils; ergänzt Sitzung 24, 13:27, vor dem Einfrieren, nach EXP-072 Nachtrag b):** Seeds mit höherem Energieanteil der eigenen
  Ziel-Irreps an der W_E-Irrep-Leistung bei Schritt 2000 groken früher. Je Seed x = Mittel beider Arme des Anteils bei 2000, y = Mittel beider Arme des Generalisierungsschritts (nie generalisiert:
  12001, als spätester gezählt). Spearman ρ(x, y) über 20 Seeds, einseitiger Permutationstest (20000). „S1 bestätigt“ = ρ < 0 und p < 0.05; technischer Ausfall → nicht auswertbar.
  Grundlage: post hoc ρ = −0.75 an 10 EXP-072-Läufen (gesehen). Im Geist bekannt (Fortschrittsmaße, Nanda et al. 2023).
- **Urteil:** Jeder technische Ausfall (auch Lade- oder Rechenfehler) -> *nicht auswertbar*; sonst **"bestaetigt" = p < 0.05 und KI-Untergrenze >= 0.05** (Logit-Einheiten), sonst *nicht bestaetigt*.
  Primaer zaehlen alle 20 Seeds; wie viele Modelle generalisiert haben (>= 0.9 in beiden Armen), wird berichtet, dazu beschreibend D nur an diesen Seeds und der Median-Energieanteil der
  eigenen Irreps in W_E.
- **Stichprobe:** Pilot EXP-072 (5 Seeds, 20000 Schritte): D = 0.223 ± 0.024. Falls sich Effekt und Streuung auf 12000 Schritte uebertragen, liegt die KI-Untergrenze bei n = 20 weit ueber 0.05.
  n = 20 wie P2e, damit die Aufgaben vergleichbar bleiben (nicht aus einer Poweranalyse; die Power ist bei dieser Streuung ohnehin nahe 1).
- **Warum 12000 Schritte:** EXP-072: erster Test >= 0.9 bei Median 4575, Maximum 8150; ein Lauf (1004 F) blieb bis 20000 bei 0.83. 12000 = Maximum + Reserve. *Nach Codex (s24) offengelegt:* Bei Schritt 12000 waren im Pilot 9/10 Arme >= 0.9; Seed 1004 F lag bei 0.23 (0.83 erst bei 20000), und der Pilotwert D = 0.223 stammt von 20000-Schritt-Modellen, nicht von 12000. Alle Seeds zaehlen,
  das Urteil haengt also nicht davon ab, wie viele generalisieren.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-072 an P1-Splits (Seeds 1000-1004): Schrittzahl, Mass (post hoc gewaehlt, Uebertragung des P2e-Masses),
  delta und Mindesteffekt wie P2d/P2e. D59-Spektren aus P1 und EXP-046 (K2). Seeds 2340-2359 wurden nie benutzt; Versuchs-ID 6 erzeugt eigene Splits und Ziele.
- **Deutung vorab eingeschraenkt:** Nach [[experiments/EXP-068-matched-sensitivity/README|EXP-068]] folgt die Empfindlichkeit bei gleicher Schrittnorm der Amplitudenverteilung in W_E.
  "Bestaetigt" heisst nur: Auch in D59 reagiert der Logit-Abstand staerker auf gleich grosse Schritte entlang der gesteuerten Irreps; das belegt keine Nutzung ueber die Energie hinaus.
- **Grenzen:** eine nicht-abelsche Gruppe (D59 enthaelt Z59 mit Index 2), eine Architektur, eine Dosis, eine lokale endliche Stoerung.
- **Vor dem Einfrieren:** Codex-Pruefung (Regel 18c); ein echter Job bis zum Ende durch den eingefrorenen Lader (im Fenster); Manifest mit Code-Hashes und Commit.
- **Codex-Pruefung (Sitzung 24, ca. 12:51-12:57 Berlin, `P2f_codex_review.txt`):** keine Blocker (Projektion, Elementreihenfolge, Eingabeformat, Run-ID, Lader-Felder, Kontrollpool, Ein-Hypothesen-Design geprueft).
  Uebernommen: (1) 12000-Schritt-Befund des Piloten offengelegt (oben); (2) `--analyze` loescht zuerst eine alte `P2f_summary.json`, damit ein abgebrochener Lauf keine veraltete Zusammenfassung hinterlaesst;
  (3) Selbsttest prueft den fold(2k)-Ausschluss jetzt mit einer Menge, deren Harmonische ausserhalb von eigenen und fremden Zielen liegen.
- Code: `lab/tools/confirm_p2f.py` (Selbsttest ok, Sitzung 24, 12:50 Berlin, vor den Codex-Aenderungen; **der geaenderte Selbsttest ist noch nicht gelaufen** (Fenster zu ab 12:58), inkl. End-zu-End-Mass an einem Zufallsmodell und Import-Pruefung gegen die Hash-Liste).

```
python lab/tools/confirm_p2f.py --splits lab/confirm/P2f_manifest.json
python lab/tools/confirm_p2f.py --jobs lab/confirm/P2f_manifest.json > lab/confirm/P2f_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/P2f_jobs.txt --workers 10
python lab/tools/guarded_run.py -- python lab/tools/confirm_p2f.py --analyze lab/confirm/P2f_manifest.json
```

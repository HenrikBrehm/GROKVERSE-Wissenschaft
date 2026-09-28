---
id: R2-registrierung
status: abgeschlossen
datum: 2026-09-27
tags: [lab/bestaetigung, lab/paper, exp/abgeschlossen, befund/unklar]
verwandt: ["[[paper/robustness_plan]]", "[[paper/STATUS]]", "[[confirm/N29_REGISTRATION|N29]]", "[[confirm/R1_REGISTRATION_DRAFT|R1]]", "[[FINDINGS]]", "[[experiments/EXP-039-lr-clock/README|EXP-039]]", "[[JOURNAL]]"]
---
# R2-Bestätigung (Regel 19a): Hält der K4c-Übergang bei doppelter Lernrate und kleinerem Weight Decay? Registrierungsentwurf (Sitzung 26)

Zurück zu [[paper/robustness_plan]] · [[paper/STATUS]] · Vorlage [[confirm/N29_REGISTRATION|N29]] (K4c, eingefroren 087e042, bestätigt).
Entwurf 2026-09-27, Sitzung 26, zwischen 15:17 und 15:22 Berlin (gemessen), **vor jedem R2-Lauf**. Code `lab/tools/confirm_r2.py` (ungetestet bis zum nächsten Fenster).

- **Aussage (Robustheit von K4c):** Das N29-Muster (früher Wechsel → Endmodell hängt an den neuen Frequenzen; Wechsel nach 50 Schritten → an den alten) besteht auch bei
  (a) **lr 2e-3** (wd 1) und (b) **wd 0.3** (lr 1e-3). Je Zelle genau eine Abweichung vom Standard (lr 1e-3, wd 1.0, train_frac 0.3).
- **Protokoll:** genau wie N29 (ω = 0, EXP-053-Splits über `overlap_split.build`, beide Richtungen A→B und B→A, 4000 Schritte nach dem Wechsel, `--stop-after-gen` ≥ Schritte, `--save-model`,
  W_E[:113] auf das Komplement der 5 alten bzw. 5 neuen Zielfrequenzen projiziert, Genauigkeit auf der zurückgehaltenen Testmenge des Seeds; je Seed Mittel über beide Richtungen).
- **Wechselzeiten:** Zelle lr2: t ∈ {12, 25, 50}; Zelle wd03: t ∈ {25, 50}.
- **Primäre Familie (Holm über 4, einseitiger t-Test, 95-%-Bootstrap-KI; „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0):**

| Hypothese | Zelle | t | Kontrast (minus Mindestdifferenz 0.3) |
|---|---|---|---|
| H1_lr2 (Festhalten) | lr 2e-3 | 50 | (acc_neu − acc_alt) − 0.3 |
| H2_lr2 (Umstieg) | lr 2e-3 | 12 | (acc_alt − acc_neu) − 0.3 |
| H1_wd03 (Festhalten) | wd 0.3 | 50 | (acc_neu − acc_alt) − 0.3 |
| H2_wd03 (Umstieg) | wd 0.3 | 25 | (acc_alt − acc_neu) − 0.3 |

  acc_alt = Genauigkeit nach Entfernen der alten Ziele, acc_neu = nach Entfernen der neuen (wie N29). **„Übergang robust“ je Zelle nur, wenn H1 und H2 dieser Zelle bestätigt sind.**
- **Warum t = 12 für H2 bei lr 2e-3:** Ob die Festlegung in Schritten oder in aufsummierter Lernrate Λ tickt, ist offen (EXP-039: ***unklar***, Λ in 5/8 Zellen). Bei 12 Schritten mit doppelter Lernrate
  ist Λ ≈ 0.024 (Standard: 24 Schritte), also unter beiden Uhren im Umstiegsbereich von N29. So prüft H2_lr2, ob es den Umstieg bei doppelter Lernrate gibt, ohne auf eine der beiden Uhren zu wetten.
- **Sekundär, ohne Urteil (Zeitverlauf):** Zelle lr2 bei t = 25 (Λ = 0.05 wie der Standard bei t = 50): D25 = acc_neu − acc_alt, Mittel und 95-%-KI. Lesart vorab (vor Codex): KI ganz > 0 → *passt zur Λ-Uhr*
  (Festhalten wie beim Standard bei 50); KI ganz < 0 → *passt zur Schrittuhr* (Umstieg wie beim Standard bei 25); sonst *unklar*. Nicht in der Holm-Familie; ein Ergebnis hier ist Exploration. *Nach Codex (s26):* D25 ist **kein Test der Uhren**, weil lr 2e-3 auch nach dem Wechsel gilt (schnellere Anpassung an B begünstigt den Umstieg); die Etiketten heißen deshalb neutral *Festhalten bei t = 25* / *Umstieg bei t = 25* / *unklar*. Ein Uhrentest braucht die Lernrate nur vor dem Wechsel (wie EXP-039).
- **Stichprobe und Ausfälle:** Primär zählen **alle** Seeds, auch nicht generalisierte (wie N29, Codex s23: ein Genauigkeitsfilter wäre ergebnisabhängig). Jeder technische Ausfall (fehlt, nicht gebunden,
  Lader-Fehler, nicht endlich) → *nicht auswertbar*. Generalisierung (Basis ≥ 0.9 in allen Läufen beider Zellen) wird berichtet, die Teilmenge nur beschreibend ohne Urteil.
- **Stichprobengröße aus der Pilotstreuung (N29):** H2-Kontrast 0.603 (SD 0.240), H1 0.903 (SD 0.124). Normalnäherung, einseitig, α = 0.05/4: bei unverändertem Effekt Power ≈ 1 schon bei n = 20;
  bei halbiertem Abstand über der Mindestdifferenz (H2 0.45, SD 0.24) n = 20 → 0.71, **n = 30 → 0.88**; bei zusätzlich 1.25-facher Streuung n = 30 → 0.69. **Gewählt n = 30** (Seeds **2510–2539**,
  reserviert in [[FINDINGS_DETAILS]], nie benutzt). 30 × (6 + 4) = **300 Läufe** à t + 4000 Schritte, GPU, 1 Thread. Zeit nach N29 (80 Läufe in 17 min mit 7 Arbeitern): ≈ 60 min mit 7, ≈ 45 min mit 10.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** N29 (Seeds 2250–2269: Maß, Mindestdifferenz, Budget, Streuung für die Stichprobengröße); EXP-039 (bekannte Seeds 30–34; Wahl von t = 12
  und der Sekundärfrage); EXP-020/059 (t = 25/50). Keine Läufe mit lr 2e-3 oder wd 0.3 im Wechselprotokoll gesehen. Die Zellen folgen dem [[paper/robustness_plan]] (Sitzung 24, vor jedem Ergebnis).
- **Grenzen:** eine Aufgabe (add 113), eine Architektur, ω = 0; nur zwei Zellen (lr 0.5e-3, wd 3, train_frac bleiben offen); Genauigkeit nach Ablation statt Logit-Abstand; bei wd 0.3 kann das Grokking in
  4000 Schritten ausbleiben (dann misst der Ablationskontrast die Abhängigkeit eines nicht generalisierten Netzes; berichtet).
- **Familie:** eigene (nur R2), getrennt von R1.
- **Vor dem Einfrieren:** Selbsttest im Fenster; Codex-Prüfung (Regel 18c); Manifest mit Code-Hashes und Commit; ein echter Job bis zum Ende durch den eingefrorenen Lader (Smoke).

```
python lab/tools/guarded_run.py -- python lab/tools/confirm_r2.py --selftest
python lab/tools/confirm_r2.py --hash-code                      # -> code_sha256 ins Manifest
# Manifest lab/confirm/R2_manifest.json = REGISTERED + python + registration + code_sha256; committen, Commit-ID in "commit", erneut committen
python lab/tools/confirm_r2.py --splits lab/confirm/R2_manifest.json
python lab/tools/confirm_r2.py --jobs lab/confirm/R2_manifest.json > lab/confirm/R2_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/R2_jobs.txt --workers 10
python lab/tools/guarded_run.py -- python lab/tools/confirm_r2.py --analyze lab/confirm/R2_manifest.json
```

## Codex-Prüfung (Sitzung 26, `R2_codex_review_s26.txt`, vor jedem Lauf)

Keine Blocker. Bestätigt: Run-IDs wie `freq_ban.py`, `lr`/`weight_decay` in der result.json geprüft, alt/neu je Richtung, Vorzeichen, Joborder, Holm über 4, Power-Zahlen. Übernommen: (1) D25-Konfundierung (oben); (2) die ergebnisabhängig ausgewählte Teilmenge der generalisierten Seeds enthält keine t-, p- oder Holm-Werte mehr; (3) `train_frac` = 0.3 wird in jeder result.json mitgeprüft. Nur vermerkt: Der Selbsttest über geladene Module erfasst per `exec_module` geladene Dateien nicht vollständig; Codex hat die Ketten von Hand verfolgt und keine Lücke in `CODE_FILES` gefunden (gleiche Einschränkung wie N29). Code danach weiter ungetestet (nur `py_compile`).

- **Eingefroren (Sitzung 37, 2026-09-28, Berlin):** Selbsttest grün (Sitzung 37), Codex-Prüfung Sitzung 26 ohne Blocker, Punkte eingearbeitet. Manifest `lab/confirm/R2_manifest.json` (Entwurf ohne Notiz + `code_sha256`), Commit-ID im Feld `commit`. Das C2-Code-Tor liegt vor diesem Commit. Bereits gesehene Daten: wie oben; kein Lauf mit den R2-Seeds 2510–2539 vor dem Einfrieren.

## Ergebnis (Sitzung 38, 2026-09-28, 07:34 Berlin gemessen; Block 300/300 ok, GPU, 06:20–07:30; `--analyze` über den Wächter, `R2_summary.json`, Log `R2_block_s38.log`/`R2_analyze_s38.log`)

n = 30 (Seeds 2510–2539), 0 technische Ausfälle. Holm über 4:
- **lr 2e-3: Übergang robust** (beide bestätigt). H1_lr2 (Festhalten bei 50): 0.97, minus 0.3 **+0.67** [0.64, 0.69], 30/30, Holm-p 7e-29. H2_lr2 (Umstieg bei 12): 0.61, minus 0.3 **+0.31** [0.22, 0.41], 26/30 über 0.3, Holm-p 3.6e-7.
- **wd 0.3: Übergang *nicht* robust.** H1_wd03 (Festhalten bei 50): 0.83, minus 0.3 **+0.53** [0.47, 0.59], 30/30, *bestätigt*. H2_wd03 (Umstieg bei 25): nur 0.18, minus 0.3 **−0.12** [−0.18, −0.07], 5/30, *nicht bestätigt*.
- **Generalisierung (registriert berichtet):** alle lr2-Läufe bis auf einen mit Basis ≥ 0.9; bei wd 0.3 nach Wechsel bei 25 nur 2/30 bzw. 5/30 (Median-Basisgenauigkeit 0.34/0.46), nach Wechsel bei 50 24/30 bzw. 25/30. Nur 1/30 Seeds in allen Läufen generalisiert (daher keine beschreibende Teilmenge). **H2_wd03 misst also überwiegend die Abhängigkeit nicht generalisierter Netze** (registrierte Grenze); das Ergebnis heißt „bei wd 0.3 nach Wechsel bei 25 und 4000 Schritten kein Umstieg auf die neuen Frequenzen und meist keine Generalisierung“, nicht „bei wd 0.3 wird festgehalten“.
- Sekundär (ohne Urteil): lr2 bei t = 25: D25 = 0.56 [0.47, 0.65], 30/30 → *Festhalten bei t = 25* (nicht als Uhrtest lesbar, Codex s26).
- **C2** (eigene Familie, an den t = 50-Läufen): Die alten Ziele behalten ihre Rangfolge vom Wechselzeitpunkt, ρ̄ = **0.61** [0.54, 0.68], Überschuss über die Nicht-Ziel-Kontrolle 0.45 [0.38, 0.51], bereinigt 0.60 [0.53, 0.66], 30/30, p ≤ 5·10⁻⁶ (Monte-Carlo-Untergrenze) → ***bestätigt*** (`C2_summary.json`).
- **R2_time** (vor jedem R2-Lauf festgelegt, beschreibend, außerhalb der Familie): T1 wd 0.3, Wechsel @25 langsamer als @50: +1.34 log2, 29/29 ohne Gleichstand, p 1.9e-9 → *gestützt* (b bei @25 meist bei 4000 zensiert, also Untergrenze; Prüfagent: 54/60 Läufe @25, 11/60 @50); T2 lr 2e-3, @12 langsamer als @50: +2.03, 30/30 → *gestützt*; T3 lr 2e-3 @25 gegen @50: +1.47, 30/30 (beschreibend; die Λ-Uhr ließe ≈ 0 erwarten, aber lr bleibt nach dem Wechsel verdoppelt). b = min(erster Test ≥ 0.95, 4000).

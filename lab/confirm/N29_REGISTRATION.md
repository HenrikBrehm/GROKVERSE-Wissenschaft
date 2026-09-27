---
id: N29-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-064-functional-regimes/README|EXP-064]]", "[[confirm/N28_REGISTRATION|N28]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# N29-Bestätigung (funktionaler Übergang: Umstieg bei t = 25, Festhalten bei t = 50): Registrierung (Sitzung 23). **ENTWURF**

Zurück zu [[FINDINGS]] (Programm B, „Zwei spektrale Signaturen“) · Pilot [[experiments/EXP-064-functional-regimes/README|EXP-064]] (nicht auswertbar, 7/10) ·
[[NOVEL_DIRECTIONS]] „N29: Zwei Regime nach einem frühen Datenwechsel“ (der zweite Eintrag mit dieser Nummer; der ältere N29 zu Loss-Gewichten ist nicht gemeint).

- **Aussage:** Nach einem Datenwechsel A → B (add 113, ω = 0, EXP-053-Splits) und langem Nachtraining stützt sich das Endmodell (Mittel über beide Wechselrichtungen und alle 20 Seeds)
  - **H1 (Festhalten):** bei einem Wechsel nach t = 50 Schritten auf die **alten** Zielfrequenzen: Entfernen der alten schadet der Testgenauigkeit um mindestens 0.3 mehr als Entfernen der neuen;
  - **H2 (Umstieg):** bei einem Wechsel nach t = 25 Schritten auf die **neuen**: Entfernen der neuen schadet um mindestens 0.3 mehr als Entfernen der alten.
- **Modelle:** frische Seeds **2250–2269** (n = 20), Splits wie N28 (`overlap_split.build`, ω = 0, eps aus `calibration.json`), je Seed A→B und B→A bei t ∈ {25, 50},
  danach **4000** Schritte (`--steps t+4000 --stop-after-gen t+4000 --save-model`), GPU, 1 Thread. 80 Läufe.
- **Eingriff und Maß (wie EXP-064):** Am Endmodell W_E[:113] auf das Komplement der Fourier-Unterräume der 5 alten bzw. 5 neuen Zielfrequenzen projizieren (vollständige Entfernung, Rest des Netzes
  unverändert). Genauigkeit auf der zurückgehaltenen Testmenge des Seeds (20 % aller Paare, disjunkt zu A und B). Je Seed und t Mittel beider Richtungen:
  acc_alt (alte entfernt), acc_neu (neue entfernt).
- **Primär:** X1 = (acc_neu(50) − acc_alt(50)) − 0.3, X2 = (acc_alt(25) − acc_neu(25)) − 0.3. Eine Familie {H1, H2}, Holm, einseitiger t-Test (Mittel > 0), 95-%-Bootstrap-KI.
  **„bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0** (die Mindestdifferenz 0.3 steckt im getesteten Kontrast). **„Übergang bestätigt“ nur, wenn H1 und H2 beide bestätigt sind.**
- **Stichprobe und Ausfälle (nach Codex):** **Primär zählen alle 20 Seeds**, auch nicht fertig generalisierte (im Piloten hatten die ausgeschlossenen Seeds kleinere H2-Effekte; ein
  Genauigkeitsfilter würde das Ergebnis also zugunsten von H2 auswählen). Jeder technische Ausfall (fehlend, nicht gebunden, Lader-Fehler, nicht endliche Gewichte, Verluste oder Abstände)
  → *nicht auswertbar*. Wie viele Seeds generalisiert haben (Basis-Genauigkeit ≥ 0.9 in allen vier Läufen), wird berichtet, dazu beschreibend der Test nur an diesen Seeds.
- **Stichprobe:** Pilot EXP-064 (7 gültige Seeds, 2000 Schritte): acc_alt(25) − acc_neu(25) = 0.66 (SD 0.19; alle 10 Seeds: 0.51), acc_neu(50) − acc_alt(50) ≈ 0.94. Grobe Heuristik aus 7 ausgewählten Seeds mit anderem Budget: Bei n = 20 dürfte die KI-Untergrenze über 0.3 liegen;
  die Teststärke hängt vor allem daran, ob 4000 Schritte das Bild verändern (das ist Teil der Frage).
- **Warum 4000 statt 2000 Schritte:** Im Piloten waren 3/10 Seeds nach 2000 Schritten nicht fertig generalisiert. Längeres Nachtraining ist zugleich ein härterer Test des Festhaltens
  („festgelegt“ = nach B Schritten persistent, Regel 18c). Weicht das Ergebnis vom Piloten ab, kann das am Budget liegen; das wird so berichtet.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-064 (Seeds 400–409: Richtung beider Hypothesen, Maß, Schwelle 0.9); EXP-059/062/063 (Seeds 400–409) und N28 (Seeds 2200–2229,
  Spektren; Wahl von t = 25 und 50). Die Mindestdifferenz 0.3 ist nach dem Piloten gewählt (deutlich unter den Pilotwerten). Seeds 2250–2269 wurden vorher nie benutzt.
- **Grenzen:** eine Aufgabe (add 113), eine Architektur, ω = 0; Entfernung aller 5 Frequenzen ist grob (keine Dosis); nur W_E; Genauigkeit statt Logit-Abstand.
- **Familie:** eigene (nur N29).
- **Vor dem Einfrieren:** Codex-Prüfung (Regel 18c); ein echter Job bis zum Ende durch den eingefrorenen Lader (Lehre aus P2b); Manifest mit Code-Hashes und Commit.
- Code: `lab/tools/confirm_n29.py` (Selbsttest ok, Sitzung 23, 09:43; nach Codex geändert, Selbsttest erneut ok vor 09:54).

## Codex-Prüfung (Sitzung 23, Ergebnis vor 09:54 Berlin, gemessen)

Zwei Blocker, beide selbst geprüft und übernommen: (1) Genauigkeitsfilter ist ergebnisabhängig (Pilot: H2 0.66 bei geeigneten, 0.15 bei ausgeschlossenen Seeds) → primär alle Seeds;
(2) `EXP-056/make_splits.py` wird ausgeführt, war aber nicht im Code-Hash → ergänzt, dazu ein Selbsttest, der alle geladenen lab-Module gegen die Hash-Liste prüft. Weiter übernommen: gemeinsames Urteil
„Übergang“ nur bei H1 und H2; nicht endliche Verluste/Abstände/Gewichte als technischer Ausfall; SD ausdrücklich benannt; Aussage als Mittel über Richtungen und Seeds.
Keine Fehler gefunden bei Testmenge, alt/neu je Richtung, Schrittzahl, `--stop-after-gen`, Run-ID.
Nachprüfung (Codex): 4/5 geschlossen; offen waren die Endlichkeit aller Gewichte (jetzt alle Parameter geprüft) und ein Urteilslabel in der beschreibenden Teilanalyse (entfernt, Selbsttest prüft es).

```
python lab/tools/confirm_n29.py --splits lab/confirm/N29_manifest.json
python lab/tools/confirm_n29.py --jobs lab/confirm/N29_manifest.json > lab/confirm/N29_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/N29_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_n29.py --analyze lab/confirm/N29_manifest.json
```

## EINGEFROREN (Sitzung 23)

Manifest-Commit **087e042** (Code nach Codex und Nachprüfung), Splits und Jobs committet. Vor dem Einfrieren kein Lauf mit Seeds 2250–2269. Ein echter Job (Seed 2250, A→B bei 25) lief 09:58–09:59 als Smoke
und passierte den eingefrorenen Lader (gebunden; er zählt als regulärer Lauf). Block 09:59–10:16 (Log), 7 GPU-Arbeiter, 80/80 ok.

## ERGEBNIS (Sitzung 23, Auswertung 10:16–10:17 Berlin; `lab/confirm/N29_summary.json`): ***Übergang bestätigt***

80/80 Läufe gebunden, 0 technische Ausfälle, 19/20 Seeds generalisiert (Basis ≥ 0.9 in allen vier Läufen); primär alle 20.

| | Mittel acc_alt (alte entfernt) | Mittel acc_neu (neue entfernt) | Kontrast | 95-%-KI des Kontrasts | Seeds über 0.3 |
|---|---|---|---|---|---|
| **H1**, Wechsel bei t = 50 | 0.035 | 0.938 | acc_neu − acc_alt = **0.903** (SD 0.124) | [0.846, 0.953] | 20/20 |
| **H2**, Wechsel bei t = 25 | 0.703 | 0.101 | acc_alt − acc_neu = **0.603** (SD 0.240) | [0.498, 0.700] | 17/20 |

Holm-p: H1 7·10⁻¹⁵, H2 1·10⁻⁵. Beschreibend nur an den 19 generalisierten Seeds: 0.898 und 0.591 (gleiches Bild).
**Post hoc (nach dem Ergebnis, beschreibend, `lab/confirm/n29_posthoc_energy.py`):** Nach 4000 Schritten zeigt auch die W_E-Energie in dieselbe Richtung (t = 25: neue Energie größer in 38/40 Läufen;
t = 50: alte größer in 40/40). Ablation und Energie sind hier also nicht getrennt: Der Befund sagt, *auf welche Menge das Netz angewiesen ist*, nicht, dass Funktion und Spektrum auseinanderfallen.

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
- **Stichprobe und Ausfälle (nach Codex, 09:55):** **Primär zählen alle 20 Seeds**, auch nicht fertig generalisierte (im Piloten hatten die ausgeschlossenen Seeds kleinere H2-Effekte; ein
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
- Code: `lab/tools/confirm_n29.py` (Selbsttest ok, Sitzung 23, 09:43; nach Codex geändert, Selbsttest erneut ok 09:57).

## Codex-Prüfung (Sitzung 23, 09:44–09:53 gemessen)

Zwei Blocker, beide selbst geprüft und übernommen: (1) Genauigkeitsfilter ist ergebnisabhängig (Pilot: H2 0.66 bei geeigneten, 0.15 bei ausgeschlossenen Seeds) → primär alle Seeds;
(2) `EXP-056/make_splits.py` wird ausgeführt, war aber nicht im Code-Hash → ergänzt, dazu ein Selbsttest, der alle geladenen lab-Module gegen die Hash-Liste prüft. Weiter übernommen: gemeinsames Urteil
„Übergang“ nur bei H1 und H2; nicht endliche Verluste/Abstände/Gewichte als technischer Ausfall; SD ausdrücklich benannt; Aussage als Mittel über Richtungen und Seeds.
Keine Fehler gefunden bei Testmenge, alt/neu je Richtung, Schrittzahl, `--stop-after-gen`, Run-ID.

```
python lab/tools/confirm_n29.py --splits lab/confirm/N29_manifest.json
python lab/tools/confirm_n29.py --jobs lab/confirm/N29_manifest.json > lab/confirm/N29_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/N29_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_n29.py --analyze lab/confirm/N29_manifest.json
```

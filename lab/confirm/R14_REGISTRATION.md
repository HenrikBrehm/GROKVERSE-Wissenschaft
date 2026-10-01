---
id: R14
status: ausgewertet
datum: 2026-10-01
tags: [lab/confirm, programm/A, paper, exp/abgeschlossen, befund/positiv]
---
# R14: Steuert die Trainingsmenge bei add 307 mit nur 10 % Daten die Frequenzen, gemessen nach der Generalisierung? (Registrierung, Sitzung 67)

Zurück: [[LAB]] · [[FINDINGS]] · Pilot: [[experiments/EXP-137-modulus-density/README|EXP-137]] (davor [[experiments/EXP-136-large-modulus/README|EXP-136]]) · Vorlage [[confirm/P1_REGISTRATION_DRAFT|P1]] · [[JOURNAL]] Sitzung 67.

Geschrieben 2026-10-01 07:33–07:34 Berlin (gemessen), **vor jedem R14-Blocklauf**. Code: `lab/tools/confirm_r14.py` (Selbsttest grün 07:33 über den Wächter).

## Warum (Bezug zu FINDINGS / Paper)

Gutachter-Einwand LeDoux 2026 (p = 9973, 0.3 % Daten: Frequenz „regardless of … training set composition“). K2 ist bei p = 97/113 mit 30 % bestätigt. Der Pilot EXP-137 fand bei add 307 mit 10 % Daten (9425 Paare) in 6/6 Läufen Generalisierung und danach Δ_pow 8.2–10.9, jeweils über dem 99-%-Quantil eines Placebos; bei p = 211 mit 10 % (4452 Paare) generalisierte dagegen keiner von 6 Läufen in 30 000 Schritten – „geringe Dichte“ heißt hier also ≈ 9425 Paare, nicht ein Anteil an sich. R14 prüft das an frischen Seeds/Splits, damit Grenze (ii) des Papers eine bestätigte Aussage zu einem größeren Modulus bei geringer Dichte tragen kann. Keine neue Kernaussage (Regel 20a), Ort: Anhang A + Grenze (ii).

## Aufbau (Einzelheiten im Docstring von `confirm_r14.py`)

- **Trainer:** `freq_ban.py` unverändert (1-Schicht-Transformer, AdamW lr 1e-3, wd 1, Full-Batch, GPU, `--threads 1`), `--p 307 --task add --train-frac 0.1`, höchstens 30 000 Schritte, Stopp 2000 Schritte nach der Generalisierung, W_E-Schnappschüsse bei 50, 250, 500 und alle 1000 Schritte. Test = Komplement.
- **Splits:** P1-Konstruktion (`confirm_splits`, ε = 2, je 5 Ziele F/G disjunkt aus k = 1..153) mit **Versuchs-ID 14** (eigene SeedSequence-Ströme) und Anteil 0.1 (9425 Paare; die Modulkonstante wird nur innerhalb von `build` überschrieben und wiederhergestellt).
- **Seeds (frisch, reserviert):** 4430–4441 (n = 12), gleiche Init für F und G eines Seeds. Nicht verwendet im Labor (R13 nutzt 4400–4429; Smoke nutzt 4499).
- **Messung je Arm:** erster Schnappschuss ≥ eigenes gen + 1000 (gen = `transitions.primary.generalization.first_crossing_step`, Test ≥ 0.95); Δ_pow (P1-Formel, W_E-Gruppenleistung) aus diesen zwei Spektren; q99 = 99-%-Quantil von |Placebo-Δ_pow| (2000 zufällige disjunkte 5+5-Mengen außerhalb F ∪ G, Strom `SeedSequence([14, Seed])`).
- **Primär je Seed:** D = Δ_pow − q99. Ein Seed mit einem nie generalisierenden Arm (oder ohne Schnappschuss ≥ gen + 1000) geht mit **D = −(größtes q99 der auswertbaren Seeds)** ein (−1, falls keiner auswertbar; zählt wie ein Seed auf Placebo-Niveau, wird berichtet; nach der Prüfung vor dem Einfrieren strenger als die erste Fassung D = −1). Ein Lauf, dessen Schrittzahl nicht der Stoppregel folgt, ist ein technischer Ausfall.
- **Test (eine Hypothese, kein Holm):** exakter einseitiger Vorzeichen-Flip-Test für Mittel D > 0 (2¹² Muster), 95-%-Bootstrap-KI. **„bestätigt“:** p < 0.05 **und** KI-Untergrenze > 0 **und** D > 0 in ≥ 10/12 Seeds (einseitiger Binomial-p 0.019; im Selbsttest vor dem Einfrieren ergänzt, weil sonst ein Mittel aus der Hälfte der Seeds genügen könnte). Technischer Ausfall eines Laufs → „nicht auswertbar“.
- **Beschreibend:** Δ_pow, q99, Generalisierungsschritte, Δ_pow bei 2000 und am letzten Schnappschuss vor gen, Top-5-Überlappung.

## Stichprobengröße

n = 12. Pilot (3 Seeds, gesehen): D = Δ_pow − q99 ≈ 4.4 / 5.2 / 5.6. Selbst bei halbem Effekt ist die erwartete KI-Untergrenze > 0; das Hauptrisiko ist nicht die Streuung, sondern dass Seeds nicht generalisieren (Pilot 6/6 innerhalb 6125–11 500 Schritten, Budget 30 000). Ein 3-Seed-Pilot kann den Effekt überschätzen.

## Was dagegen spräche

- „nicht bestätigt“, weil mehrere Seeds nicht generalisieren → kein Befund über K2, aber über die Datengrenze (so berichten).
- „nicht bestätigt“ bei generalisierenden Seeds (Δ_pow im Placebo-Band) → K2 hängt bei größerem p an der Dichte; Grenze (ii) so schreiben.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-136 (p 211/307, 30 % und 3831 Paare) und EXP-137 (p 211/307 × 10/15/20 %, alle Ergebnisse, inkl. Placebo-Werte, gen-Schritte, Nachrechnung) – beeinflusst: Wahl p = 307 und 10 % (kleinste Zelle, in der der Pilot generalisierte), Budget 30 000, Messpunkt nach gen, Placebo-Kriterium, n. R14-Smoke (Seed 4499, 2000 Schritte, außerhalb des Blocks): Laufkennung, Konfiguration, Schnappschuss-Liste geprüft; gen None bis 2000 (wie im Pilot erwartet). Andere p/Anteile: nicht Teil von R14. Die Pilot-Splits stammen aus `EXP-043/make_split.py` (gleiche Wellen-/Schlüsselgewichtung, aber andere Zufallsströme und Zielziehung) – R14 nutzt die P1-Konstruktion.

## Wiederholungen (vorab)

Nur bei Infrastrukturfehlern (kein result.json, GPU nicht verfügbar, Abbruch durch Wächter/Dienst), nie wegen eines Ergebnisses.

## Einfrieren (Ablauf)

Manifest `lab/confirm/R14_manifest.json` = REGISTERED (experiment 14, p 307, eps 2.0, train_frac 0.1, device cuda, threads 1, steps 30000, stop_after_gen 2000) + python + seeds 4430–4441 + registration + code_sha256; committen, Commit-ID eintragen, erneut committen; `--splits`, `--jobs` → Dienst (gpu_gb 2.0 – im Pilot gemessen 1.7 GB max., workers 6, job_minutes 120).

## Grenzen (vorab)

Ein Modulus (307), ein Anteil (10 %), eine Architektur, AdamW; p und Paarzahl nicht getrennt; Messpunkt je Arm 1000–2000 Schritte nach der eigenen Generalisierung; Einbettungsenergie, keine Ablation; weit weg von LeDoux' Regime (p = 9973, 0.3 %).

## Ergebnis (Sitzung 67, 01.10., 08:21 Berlin gemessen; eingefrorene Auswertung, Manifest-Commit 68a0209c)

`PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r14.py --analyze lab/confirm/R14_manifest.json` → `R14_summary.json`. 24/24 Läufe (Dienst `51_r14`, 0 Fehlschläge), alle 24 Arme generalisiert (gen 5850–23 000), 0 technische Ausfälle.

**bestätigt:** mittleres D = Δ_pow − q99 = **5.28 [4.72, 5.81]**, 12/12 Seeds positiv, exakter Vorzeichen-Flip p = 2.4·10⁻⁴ (= 2⁻¹²). Mittel Δ_pow 10.57 (Spanne 7.92–12.06), mittleres q99 5.30 (4.48–6.26); Top-5 nach gen: 3–5 eigene Ziele je Arm. **Unabhängige Nachrechnung und Paper-Text: nächste Sitzung** (Vorlage [[paper/R14_DEUTUNGEN]], „bestätigt“).

*Unabhängige Nachrechnung (Sitzung 68, fertig 08:33 Berlin gemessen; Claude-Agent, eigener numpy-Code, ohne `confirm_r14.py`; Skripte nur in C:/tmp/r14check):* alle 24 gen-Schritte, Messschritte und Δ_pow reproduziert (Abweichung ≤ 2·10⁻¹⁵); Stoppregel in allen 24 Läufen eingehalten; Ziele disjunkt, Split-Hashes = Dateien, gleiche Init je Seed, Maske jedes Splits hat genau die eigenen Ziele als Top-5. q99 schwankt zwischen unabhängigen Placebo-Ziehungen je Seed um bis zu 1.9; **post hoc mit der ungünstigsten von 20 Ziehungen je Seed: mittleres D 4.97 [4.39, 5.50], 12/12 positiv, Urteil unverändert**. LOW: in 7/24 Armen fällt die Testgenauigkeit nach dem ersten Überschreiten kurz unter 0.95 (Regel „erstes Überschreiten“ gilt); Messschritte je Arm 7000–24 000. Δ_pow bei Schritt 2000 (vor gen) 2.37–3.54, in allen Seeds unter dem q99 nach gen (beschreibend). Paper-Text in Grenze (ii) und Anhang A.2 eingetragen (Sitzung 68), unabhängig textgeprüft.

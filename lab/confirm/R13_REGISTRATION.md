---
id: R13
status: ausgewertet
datum: 2026-10-01
tags: [lab/confirm, programm/A, paper, exp/abgeschlossen, befund/positiv]
---
# R13: Steuert die Trainingsmenge das W_E-Spektrum auch ohne Adam – unter Full-Batch-SGD mit Momentum und Gradient-Clipping? (Registrierung, Sitzung 67)

Zurück: [[LAB]] · [[FINDINGS]] · Vorlagen: [[confirm/P1_REGISTRATION_DRAFT|P1]] (K2), [[confirm/P4_REGISTRATION_DRAFT|P4]] (Steuerung ohne Generalisierung bei Integer-Addition) · Piloten: [[experiments/EXP-126-sgd-steering/README|EXP-126]], [[experiments/EXP-128-sgd-clip/README|EXP-128]] · [[JOURNAL]] Sitzung 67.

Geschrieben 2026-10-01 ab 06:10 Berlin (gemessen), **vor jedem R13-Blocklauf**. Code: `lab/tools/confirm_r13.py` (Selbsttest grün 06:09, über den Wächter; Smoke außerhalb des Blocks siehe unten).

## Warum (Bezug zu FINDINGS / Paper)

Grenze (i) des Papers: „all results are AdamW results“. Der naheliegende Gutachter-Einwand: Ist die Datensteuerung (K2) eine Eigenheit von Adams koordinatenweiser Normierung? EXP-126 (SGDm ohne Clipping) und EXP-128 (SGDm mit Clipping) waren nach ihrer Vorab-Regel „nicht auswertbar“, weil die Regel eine Anpassung an die Trainingsmenge verlangte. **Post hoc** (nach der EXP-128-Textprüfung, gesehene Seeds 3704–3707) war Δ_pow bei Schritt 2000 aber in jedem Seed groß: 7.19–7.62 (Clip 0.1) und 3.95–4.52 (Clip 0.017), meist ohne Anpassung. R13 prüft diese **Repräsentationsaussage** an frischen Seeds und Splits – wie P4 bei Integer-Addition („Steuerung des W_E-Spektrums ohne Generalisierung“), nicht als Aussage über einen gelernten Algorithmus. Werte post hoc: `lab/experiments/EXP-128-sgd-clip/posthoc_dpow_s67.py/.json`.

**Vorab zur Aussagekraft (nach der Prüfung vor dem Einfrieren, 06:18):** Die Theorie erster Ordnung (Maskenspektrum im Gradienten) sagt diese Richtung für jedes Gradientenverfahren voraus, und c0017 ist praktisch normiertes Gradientenverfahren, das in 2000 Schritten kaum trainiert. Ein „bestätigt“ ist deshalb wenig überraschend und eine Robustheitsbestätigung gegen den Einwand „nur Adam“; ein „nicht bestätigt“ wäre informativ. **Was nicht getrennt wird:** Unter AdamW zeigte EXP-047 („shuf“: gleiche Randverteilungen der Zahlen a/b, Paarstruktur zerstört, Δ_pow 0.02 ± 0.65), dass die Steuerung aus der Paarstruktur und nicht aus Token-Häufigkeiten kommt. Unter SGD fehlt diese Kontrolle; die Token-Zählungen der Splits tragen selbst Zielenergie (eigener Zielanteil ≈ 0.19 gegen Zufall ≈ 0.09, laut Prüfer), und ohne Adams koordinatenweise Normierung könnte ein Zähleffekt stärker durchschlagen. R13 zeigt daher höchstens: **Die Trainingsmenge steuert das W_E-Spektrum auch unter geclipptem SGDm – ob über die Paarstruktur oder über Token-Häufigkeiten, bleibt unter SGD offen.** (Ein „shuf“-Arm unter SGD wäre der Folgeversuch.)

## Aufbau (gilt; Einzelheiten im Docstring von `confirm_r13.py`)

- **Trainer:** `lab/experiments/EXP-128-sgd-clip/freq_ban_sgdclip.py` (Kopie von `freq_ban.py` @267fde1e + Clipping-Patch, wie EXP-128; Hash im Manifest gebunden). 1-Schicht-Transformer, add 113, Full-Batch, `--optimizer sgdm --sgd-lr 0.1 --sgd-momentum 0.9`, Weight Decay entkoppelt wie EXP-126/128 (10⁻³ je Schritt = AdamW-lr × wd; schrumpft die Init bis Schritt 2000 auf ≈ e⁻², deshalb wächst Δ_pow von ≈ 0.3 bei 250 auf 4–7.6 bei 2000; Δ_pow-Beträge nicht über Optimierer vergleichen, nur das Urteil), GPU, `--threads 1`, **genau 2000 Schritte** (`--stop-after-gen 100000`), Spektren bei 250 und 2000. Test = Komplement.
- **Bedingungen (Holm über 2):** **c01** `--sgd-clip 0.1`, **c0017** `--sgd-clip 0.017` (Werte aus EXP-128 übernommen, dort vor jedem Pilotlauf festgelegt).
- **Einheit:** Seed mit F/G-Paar (gleiche Init für F und G, wie P1/P4). Splits: P1-Konstruktion (`confirm_splits.build`, ε = 2, 30 %, Ziele F/G disjunkt je 5 aus k = 1..56) mit **Versuchs-ID 13** (eigene Zufallsströme `SeedSequence([1000001, 13, add, 113, Seed, Arm, Zweck])`, nie aus dem Init-Seed abgeleitet).
- **Seeds (frisch, reserviert, disjunkt):** c01 4400–4414, c0017 4415–4429 (n = 15 je Bedingung). Nirgends im Labor verwendet (geprüft: keine Laufverzeichnisse, keine Manifeste mit 44xx).
- **Primär je Bedingung:** Δ_pow (Formel wie P1: log-Verhältnis der W_E-Leistung auf eigenen gegen fremde Ziele, über F- und G-Lauf summiert; additive DFT aus `spectra.npy`, k = 1..56) bei Schritt 2000; exakter einseitiger Vorzeichen-Flip-Test (n = 15, 2¹⁵ Muster), Holm über 2 bei 0.05, 95-%-Bootstrap-KI. **„bestätigt“:** alle 15 Paare gültig, Holm-p < 0.05 **und** KI-Untergrenze ≥ 1 (Mindesteffekt wie P1/P4).
- **Gültigkeit:** ein fehlender oder defekter Lauf, Bindungs-/Hashverletzung (Split-Bytes, Code), abweichende Optimierereinstellungen (Optimierer, lr, Momentum, Clip-Wert in `events.sgd_clip`), nicht endliches Spektrum → Bedingung „nicht auswertbar“ (p = 1 in der Familie). Läufe nur über `confirm_r13.py --run` (Bindung an Manifest und Code).
- **Beschreibend (kein Urteil):** Δ_pow bei 250; Train-/Testgenauigkeit am Ende; Zahl der Arme mit Train ≥ 0.99; Generalisierungsschritt; Anteil gekappter Schritte; nicht endliche protokollierte Gradientennormen.

## Stichprobengröße

n = 15 je Bedingung wie P4. Pilotstreuung (EXP-128, gesehen, 4 Seeds): c01 Mittel 7.40, SD ≈ 0.18; c0017 Mittel 4.20, SD ≈ 0.28. Selbst bei halbem Effekt und fünffacher SD liegt die erwartete KI-Untergrenze über 1 (c0017 knapp, ≈ 1.4); das Vorzeichen-Kriterium erreicht bei 15/15 positiven p = 2⁻¹⁵. Die Power ist damit praktisch 1 für den Pilot-Effekt; ein Pilot aus 4 Seeds kann den Effekt aber überschätzen (Gedächtnisnotiz „power from small pilots“) – deshalb kein Schluss aus der Power, nur das Urteil.

## Was dagegen spräche

- „nicht bestätigt“ in c01: Die Steuerung des Spektrums unter geclipptem SGDm ist nicht robust über frische Seeds/Splits; Grenze (i) bleibt unverändert.
- c01 bestätigt, c0017 nicht: hängt vom Clipping-Regime ab (stark gekapptes = fast normiertes SGDm verhält sich anders) – so berichten.
- Beide bestätigt: Die Trainingsmenge steuert das W_E-Spektrum auch unter geclipptem SGDm (in diesem Aufbau, bei Schritt 2000, ohne Aussage über gelernte Lösungen, da die meisten SGD-Läufe die Trainingsmenge in 2000 Schritten nicht anpassen, und ohne Trennung Paarstruktur/Token-Häufigkeit).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- EXP-128-Kalibrierlauf (3704 F, Clip 10⁶, 2000 Schritte: Gradientennormen) und EXP-128-Smokes (C_A 3000, C_B 2500 Schritte, 3704 F) – sie legten die Clip-Werte fest.
- Die Piloten nutzten **andere Splits**: EXP-100-Konstruktion (ω = 0, kalibriertes ε ≈ 2.23) mit eigener 20-%-Testmenge (Run-ID-Präfix EXP-018); R13 nutzt die P1-Konstruktion (ε = 2, Test = Komplement). Die Maskenanteile der eigenen Ziele sind vergleichbar (R13-Konstruktion an Nicht-Block-Seeds 4380–4399: 0.179–0.207; Piloten 0.179–0.194, laut Prüfer).
- EXP-126 (Seeds 3704–3707, SGDm ohne Clipping; lr 0.05 lernt nichts, lr 0.1 divergiert) und EXP-128 (gleiche Seeds, Clip 0.017/0.1, 20 000 Schritte, alle Ergebnisse gelesen, inkl. post hoc Δ_pow bei 50/250/2000/5000/20 000 und W_E-Energieanteile auf eigenen Zielen 0.73–0.998). **Beeinflusst:** die ganze Frage, Wahl des Messschritts 2000 (dort im Pilot schon groß, vor der Divergenzzone von EXP-126 bei 1000–1500 – die mit Clipping in EXP-128 nicht auftrat), beide Clip-Werte, n.
- Smoke (06:06–06:09, außerhalb des Blocks, Seed 4399 nicht reserviert, R13-Konstruktion, c01, 2000 Schritte, `lab/confirm/r13_smoke/`): fand einen Fehler in der Run-ID-Regel (Präfix EXP-016 statt EXP-018 ohne Testdatei; korrigiert vor dem Einfrieren); Lader liest, Optimiererfelder stimmen, Train 0.45 / Test 0.22 bei 2000. Δ_pow wurde nicht berechnet (nur ein Arm).
- P1/P4/R7 (K2 unter AdamW) – das Design ist von dort übernommen.

## Wiederholungen (vorab)

Ein Lauf wird nur bei einem Infrastrukturfehler neu gestartet (kein result.json, GPU nicht verfügbar, Abbruch durch Wächter/Dienst), nie wegen eines Ergebnisses. Ein Lauf, der wegen nicht endlicher Artefakte im Zustand „finalizing“ bleibt, wird **nicht** wiederholt → Bedingung „nicht auswertbar“. Eine protokollierte nicht endliche Gradientennorm bei endlichen Spektren ist gültig und wird nur beschreibend berichtet (anders als die Divergenzregel von EXP-128, die eine Anpassung verlangte).

## Einfrieren (Ablauf)

Manifest `lab/confirm/R13_manifest.json` = REGISTERED-Felder (experiment 13, p 113, eps 2.0, device cuda, threads 1, steps 2000, stop_after_gen 100000, sgd_lr 0.1, sgd_momentum 0.9, clip {c01: 0.1, c0017: 0.017}) + python (`.venv-gpu/Scripts/python.exe`, im Job absolut) + seeds {c01: 4400–4414, c0017: 4415–4429} + registration + code_sha256 (`confirm_r13.py --hash-code`); committen, Commit-ID als „commit“ eintragen und erneut committen; dann `--splits`, `--jobs` → Dienstdatei (gpu_gb 0.75, workers 4, ≤ 10 GPU-Prozesse gesamt).

## Grenzen (vorab)

Eine Architektur, eine Aufgabe (add 113), eine Lernrate (0.1) mit Momentum 0.9 und AdamW-angepasster entkoppelter Gewichtsabnahme (10⁻³/Schritt), zwei Clip-Werte, keine Trennung von Paarstruktur und Token-Häufigkeit, ε = 2, 30 % Daten; Messung nur bei Schritt 2000 und nur Einbettungsenergie (keine Ablation, keine Aussage über eine gelernte Lösung); Full-Batch. Keine Aussage über SGD ohne Clipping oder über Minibatch-SGD.

## Ergebnis (Sitzung 67, 01.10., 06:54 Berlin gemessen; eingefrorene Auswertung, Manifest-Commit a77dbebb)

Befehl: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r13.py --analyze lab/confirm/R13_manifest.json` → `R13_summary.json`. 60/60 Läufe (Dienst `49_r13`, 0 Fehlschläge), 0 technische Ausfälle.

| Bedingung | Δ_pow bei 2000, Mittel [95-%-KI] | SD | positiv | p (Holm über 2) | Urteil |
|---|---|---|---|---|---|
| c01 (Clip 0.1) | **7.80** [7.51, 8.07] | 0.57 | 15/15 | 6.1·10⁻⁵ | **bestätigt** |
| c0017 (Clip 0.017) | **4.78** [4.59, 4.96] | 0.38 | 15/15 | 6.1·10⁻⁵ | **bestätigt** |

Beschreibend: Δ_pow bei 250 im Mittel 0.31 / 0.19; Train ≥ 0.99 in 7/30 (c01, Median 0.75, 5 Arme generalisiert) bzw. 0/30 Armen (c0017, Median 0.06); Median gekappter Anteil 0.49 / 0.78; keine nicht endliche Norm. **Deutung nach Vorlage [[paper/R13_DEUTUNGEN]] („beide bestätigt“, enge Fassung):** Die Trainingsmenge steuert das W_E-Spektrum auch unter geclipptem Full-Batch-SGDm; das beantwortet den Einwand „Artefakt von Adams Normierung“ für die Repräsentation, nicht für gelernte Lösungen, Festlegung oder Tempo. Mechanismus-Kontrolle als Pilot: [[experiments/EXP-138-sgd-shuf/README|EXP-138]] („Paarstruktur trägt“ bei beiden Clip-Werten). **Unabhängige Nachrechnung (Sitzung 67, 06:56 gemessen; Claude-Agent, eigener numpy-Code ohne Import von confirm_r13/confirm_p1):** 60/60 Läufe, Konfiguration und Split-Hashes geprüft, Δ_pow je Seed bei 2000 und 250 ohne Abweichung, exakter p = 2⁻¹⁵, Holm 6.1·10⁻⁵, Bootstrap-KI bis auf Resampling-Rauschen gleich ([7.518, 8.073] / [4.593, 4.960]), gleiche Urteile. EXP-138 ebenso ohne Abweichung; die shuf-Splits haben exakt dieselben a/b-Zählungen wie eng.

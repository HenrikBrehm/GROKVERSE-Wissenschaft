---
id: R15
status: registriert
datum: 2026-10-01
tags: [lab/confirm, programm/A, paper, exp/vorbereitet]
---
# R15: Ermöglicht eine spektral konstruierte Trainingsmenge die Generalisierung an der Datengrenze, wo eine gleich große Zufallsmenge es nicht tut? (Registrierung, Sitzung 69)

Zurück: [[LAB]] · [[FINDINGS]] · Pilot: [[experiments/EXP-140-random-at-edge/README|EXP-140]] (Zellen aus [[experiments/EXP-139-pair-count/README|EXP-139]]) · Vorlage [[confirm/R14_REGISTRATION|R14]] · [[confirm/R5_REGISTRATION_DRAFT|R5]] · [[JOURNAL]] Sitzung 69.

Geschrieben 2026-10-01 11:49–11:55 Berlin (gemessen), **vor jedem R15-Blocklauf**. Code: `lab/tools/confirm_r15.py` (Selbsttest grün 11:48 über den Wächter).

## Warum (Bezug zu FINDINGS / Paper)

Regel 20b (LeDoux 2026: bei p = 9973 und 0.3 % Daten generalisiert dort eine Zufallsteilmenge in i.i.d.-Reihenfolge nicht; „Bedeutung der Reihenfolge sinkt mit der Adäquanz des Inhaltssignals“, §6.4) und Kernaussage R5 (konstruierte Splits groken ≈ 6–7× früher, bestätigt bei 30 % Daten). Pilot EXP-140 (add 401, 14 000 Paare = 8.7 %, 3 Seeds): alle 3 Zufallsarme ohne Generalisierung in 30 000 Schritten, die konstruierten Arme derselben Seeds bei 5 013–6 150. R15 prüft das an frischen Seeds/Splits und an einer zweiten Zelle. Keine neue Kernaussage (Regel 20a); Ort: Anhang A + Grenze (ii) bzw. LeDoux-Absatz.

## Aufbau (Einzelheiten im Docstring von `confirm_r15.py`)

- **Zellen (Familie, Holm über 2):** H1 add 401, N = 14 000 Paare (Pilotzelle); H2 add 307, N = 9 425 Paare (10 %; **kein R-Pilot**, E-Arme generalisierten in EXP-137/R14 alle, 5 850–23 000).
- **Trainer:** `freq_ban.py` unverändert (1-Schicht-Transformer, AdamW lr 1e-3, wd 1, Full-Batch, GPU, `--threads 1`), höchstens 30 000 Schritte, Stopp 2000 nach gen. Test = Komplement.
- **Splits:** P1-Konstruktion (`confirm_splits`) mit **Versuchs-ID 15** (eigene SeedSequence-Ströme), Anteil N/p²; Arme F, G (ε = 2, je 5 disjunkte Ziele) und R (ε = 0: gleichverteilte Zufallsteilmenge mit genau N Paaren, eigener Schlüsselstrom). Gleiche Init für F, G, R eines Seeds. Selbsttest: Masken-Top-5 von F/G = eigene Ziele bei beiden p.
- **Seeds (frisch, reserviert):** 4500–4509 (n = 10), im Labor nicht verwendet (Smoke: 4599).
- **Je Arm:** gen = `transitions.primary.generalization.first_crossing_step` (Test ≥ 0.95), ohne gen zensiert bei 30 000 (untere Schranke).
- **Primär je Seed:** L = ln(g_R / g_E), g_E = Mittel der zensierten g_F, g_G. Nur R zensiert → L ist eine untere Schranke (konservativ); alle zensiert → L = 0.
- **Test je Zelle:** exakter einseitiger Vorzeichen-Flip-Test für Mittel L > 0 (2¹⁰ Muster), Holm über H1/H2, 95-%-Bootstrap-KI. **„bestätigt“:** Holm-p < 0.05 **und** KI-Untergrenze > 0 **und** L > 0 in ≥ 9/10 Seeds (einseitiger Binomial-p 0.011). **Beschreibung (vorab):** bestätigte Zelle „ermöglicht“, wenn R in ≤ 2/10 Seeds generalisiert und beide E-Arme in ≥ 8/10; sonst „beschleunigt“. Technischer Ausfall eines Laufs (fehlt, ungebunden, Konfiguration, Stoppregel) → „nicht auswertbar“.
- **Beschreibend:** gen je Arm, Test-Genauigkeit am Ende, Median g_E, Zahl generalisierender R-Arme.

## Stichprobengröße

n = 10 je Zelle. Pilot H1 (gesehen): L ≥ ln(30 000 / 6 150) = 1.58, 1.79, 1.74 (alle zensiert). Erreicht jeder Seed L > 0, ist p = 2⁻¹⁰ (Holm 2·2⁻¹⁰). Das Hauptrisiko ist nicht Streuung, sondern dass R in mehreren Seeds doch im Budget generalisiert oder E-Arme ausfallen (Pilot: E 6/6 bei 4 425–6 575). H2 ohne Pilot: Teststärke unbekannt – ein „nicht bestätigt“ dort ist ein Befund über die Zelle, nicht gegen H1.

## Was dagegen spräche

- H1 „nicht bestätigt“ (R generalisiert in mehreren Seeds ähnlich schnell): Der Pilot war ein Zufallstreffer; „Inhalt ersetzt Dichte“ hält nicht.
- H2 „nicht bestätigt“: Der Effekt hängt von der Zelle ab (z. B. bei 307/9425 generalisiert auch R) → so im Paper berichten.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-140 (alle 3 R-Läufe bei 401/14 000), EXP-139 (alle bisherigen Zellen inkl. Spektren der nicht lernenden Zellen, S69-Nachauswertung), EXP-141 (bisher 3 Läufe bei 503/16 100), EXP-137 und R14 (alle Ergebnisse bei 307/9425, nur E-Arme). Beeinflusst: Wahl der Zellen (401/14 000 = Pilotzelle; 307/9425 = einzige weitere Zelle nahe der Grenze mit sicher generalisierenden E-Armen), Budget 30 000, n = 10, Kriterium ≥ 9/10. p = 503 nicht aufgenommen (7 GB je Lauf, gen nahe am Budget).

## Wiederholungen (vorab)

Nur bei Infrastrukturfehlern (kein result.json, GPU nicht verfügbar, Abbruch durch Wächter/Dienst), nie wegen eines Ergebnisses.

## Einfrieren (Ablauf)

Manifest `lab/confirm/R15_manifest.json` = REGISTERED (experiment 15, cells {401: 14000, 307: 9425}, eps 2.0, device cuda, threads 1, steps 30000, stop_after_gen 2000) + python + seeds 4500–4509 + registration + code_sha256; unabhängige Prüfung von Registrierung und Code vor dem Einfrieren; committen, Commit-ID eintragen, erneut committen; `--splits`; Smoke (Seed 4599, außerhalb des Blocks) durch den Lader; `--jobs` → Dienst in zwei Dateien (p 401: gpu_gb 4.0, workers 3; p 307: gpu_gb 2.0, workers 5; job_minutes 120), hinter EXP-141.

## Grenzen (vorab)

Zwei Zellen, ein Budget (zensierte Läufe beweisen nicht, dass R nie generalisiert), Full-Batch, eine Architektur, AdamW; eine Zufallsteilmenge ohne Reihenfolge ist kein Nachbau von LeDoux' Aufbau (Minibatch, 2 Schichten, p = 9973); gen-Zeit, keine Ablation.

## Ergebnis

Offen.

---
id: LM1
status: registriert
datum: 2026-09-29
tags: [confirm, lm-leiter]
---
# LM1: Steuert die Faktenauswahl die Zahl-Embeddings eines kleinen Sprachmodells? (Bestätigungsblock, Sitzung 50)

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, Verallgemeinerung von K2; Regel 20e Stufe 2) · Pilot [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] · [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] · Code `lab/confirm/confirm_lm1.py`

## Fassung 1 (Sitzung 50, 12:31 Berlin gemessen, vor jedem Lauf dieses Blocks)

**Frage.** K2 (die Auswahl der Trainingspaare steuert, welche Fourier-Frequenzen die Einbettung trägt) ist im Spielzeugmodell und auf allen Sprossen von Stufe 1 der Leiter bestätigt bzw. gesehen. Hält K2 in einem kleinen Sprachmodell (≈ 14 M Parameter, 6 Schichten, gebundene Embeddings), das TinyStories-Text und eingestreute Rechensätze von Grund auf lernt, **wenn es die Fakten lernt**?

**Aufbau (eingefroren).** Trainer `lm_stage2.py` (EXP-105; Code-Hash im Manifest), 19 Rechensätze je Sequenz (≈ 79 % Rechen-Tokens; Maximum bei Kontext 256), Verlust auf Text und Antwort-Tokens (`--loss answer`), 6000 Schritte, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, GPU (alle 20 Läufe auf demselben Gerät). Je Seed ein konstruiertes Split-Paar F/G und eine gemeinsame zurückgehaltene Testmenge aus der P1-/EXP-053-Konstruktion (`EXP-102 design.build`, ε kalibriert, fünf disjunkte Zielfrequenzen je Arm). F und G eines Seeds teilen Init, Text, Schablonen und Einfügepositionen (Modell-Seed = Split-Seed + 100); nur die Fakten unterscheiden sich. **Frische Seeds 4000–4009** (vorher von keinem Versuch, keiner Registrierung und keiner Jobdatei verwendet; geprüft über alle Manifeste, Jobdateien und Split-Metadaten, Sitzung 50).

**Messgröße.** Δ_pow (P1-Definition) auf den 113 Zahl-Token-Zeilen der gebundenen Einbettung bei Schritt 6000.

**Tor.** Zurückgehaltene Faktengenauigkeit ≥ 0.5 am Ende in ≥ 16 von 20 Läufen; sonst „nicht auswertbar (Budget)“ (dann keine Aussage über K2).

**H1 (einzige primäre Hypothese, Familie = {H1}).** Mittleres Δ_pow > 1 (registrierter Mindesteffekt wie P1). **„bestätigt“**, wenn die untere Grenze des 95-%-Perzentil-Bootstrap-KI (10 000 Ziehungen, rng 4001) über 1 liegt und der einseitige exakte Vorzeichen-Permutationstest gegen 1 (2¹⁰ Vorzeichen) p < 0.05 gibt; **„widerlegt (bricht)“**, wenn die obere KI-Grenze unter 1 liegt; sonst „unklar“.

**Bindung.** Die Auswertung nimmt nur Läufe, deren result.json den Trainer-Hash des Manifests, die Split- und Test-Hashes des Seeds, den Modell-Seed, alle eingefrorenen Hyperparameter, Status „completed“ nach 6000 Schritten, endliche Snapshots und keinen Text-Umlauf trägt; sonst „defekt“, dann ist der Block „nicht auswertbar (defekt/fehlt)“. Der Code darf sich nach dem Einfrieren nicht ändern (Hash-Prüfung in `--analyze`).

**Sekundär (beschreibend, kein Urteil).** Zurückgehaltene Genauigkeit je Lauf; Seeds mit Δ_pow > 0; je Paar s_learn (erster Snapshot mit Trainingsfakten ≥ 0.1 in F und G) und s_steer (erster Snapshot mit Δ_pow > 1), also H-folgt aus EXP-113 an frischen Seeds.

**Stichprobengröße.** n = 10 Seeds (20 Läufe) nach Regel 15b. Keine Poweranalyse aus Pilotstreuung möglich (Pilot EXP-114: 1 Seed, Δ_pow 5.60 bei 4000). Annahme für die Planung: Liegt das wahre Mittel bei ≥ 3 und die Seed-Streuung bei SD ≤ 2.5 (im Spielzeugmodell P1: SD ≈ 1.1 bei add 113), ist die untere KI-Grenze bei n = 10 mit hoher Wahrscheinlichkeit > 1. Ist die Streuung größer oder lernen Seeds die Fakten nicht, fällt der Block eher „unklar“ oder „nicht auswertbar“ aus; das wird so berichtet.

**Budget.** 20 Läufe à 6000 Schritte über den GPU-Dienst (4 Worker, job_minutes 240). Pilot: 4000 Schritte in ≈ 36 min unter voller GPU-Last → ≈ 55 min je Lauf, Block ≈ 4–5 h.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen.** EXP-114 (Seed 3862 / Split 3802, K = 19, 4000 Schritte: Fakten ab Schritt 2000 gelernt, Δ_pow 5.60, zurückgehalten 0.98) → Wahl von K = 19, `--loss answer`, 6000 Schritte (Faktenlernen bei ≈ 2000 im Pilot, Reserve ×3), Tor bei 0.5. EXP-113 bis Schritt ≈ 6500 (K = 8, noch kein Faktenlernen) → K = 8 nicht gewählt. EXP-105-Pilot, EXP-102/112 (Stufe 1). Keine der Seeds 4000–4009 wurde je trainiert.

**Einordnung, falls bestätigt.** Aussage nur für diesen Aufbau: kleines LM, 79 % Rechen-Tokens, Verlust auf Text + Antworten, P1-artige konstruierte Splits, Energiemaß. Kein Beleg für „wenige Prozent“ Rechenanteil (Regel 20e); das wäre die nächste Sprosse. Funktionale Nutzung nicht gemessen.

**Smoke.** Vor dem Einreihen der 20 Läufe: ein Lauf (Seed 4000 F) mit 250 Schritten in einem getrennten Ordner (`lm1_smoke`, nicht gezählt) und ein Probelauf des Laders an diesem Lauf (Bindung außer Schrittzahl); Ergebnis unten.

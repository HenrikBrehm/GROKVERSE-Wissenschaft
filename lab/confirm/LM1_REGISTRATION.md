---
id: LM1
status: abgeschlossen
datum: 2026-09-29
tags: [confirm, lm-leiter]
---
# LM1: Steuert die Faktenauswahl die Zahl-Embeddings eines kleinen Sprachmodells? (Bestätigungsblock, Sitzung 50)

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, Verallgemeinerung von K2; Regel 20e Stufe 2) · Pilot [[experiments/EXP-114-lm-dilution-pilot/README|EXP-114]] · [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] · Code `lab/confirm/confirm_lm1.py`

## Fassung 1 (Sitzung 50, 12:31 Berlin gemessen, vor jedem Lauf dieses Blocks)

**Frage.** K2 (die Auswahl der Trainingspaare steuert, welche Fourier-Frequenzen die Einbettung trägt) ist im Spielzeugmodell und auf allen Sprossen von Stufe 1 der Leiter bestätigt bzw. gesehen. Hält K2 in einem kleinen Sprachmodell (≈ 14 M Parameter, 6 Schichten, gebundene Embeddings), das TinyStories-Text und eingestreute Rechensätze von Grund auf lernt, **wenn es die Fakten lernt**?

**Aufbau (eingefroren).** Trainer `lm_stage2.py` (EXP-105; Code-Hash im Manifest), 19 Rechensätze je Sequenz (≈ 79 % Rechen-Tokens; Maximum bei Kontext 256), Verlust auf Text und Antwort-Tokens (`--loss answer`), 6000 Schritte, AdamW lr 6·10⁻⁴, wd 0.1, Warmup 500, Batch 32, GPU (alle 20 Läufe auf demselben Gerät). Je Seed ein konstruiertes Split-Paar F/G und eine gemeinsame zurückgehaltene Testmenge aus der P1-/EXP-053-Konstruktion (`EXP-102 design.build`, ε kalibriert, fünf disjunkte Zielfrequenzen je Arm). F und G eines Seeds teilen Init, Text, Schablonen und Einfügepositionen (Modell-Seed = Split-Seed + 100); nur die Fakten unterscheiden sich. **Frische Seeds 4000–4009, Modell-Seeds 4100–4109** (vorher von keinem Versuch, keiner Registrierung und keiner Jobdatei verwendet; geprüft über alle Manifeste, Jobdateien und Split-Metadaten, Sitzung 50).

**Messgröße.** Δ_pow (P1-Definition) auf den 113 Zahl-Token-Zeilen der gebundenen Einbettung bei Schritt 6000.

**Tor.** Zurückgehaltene Faktengenauigkeit ≥ 0.5 am Ende in ≥ 16 von 20 Läufen; sonst „nicht auswertbar (Budget)“ (dann keine Aussage über K2).

**H1 (einzige primäre Hypothese, Familie = {H1}).** Mittleres Δ_pow > 1 über alle 10 Seeds (registrierter Mindesteffekt wie P1; auch Seeds, deren Läufe die Fakten nicht lernen, zählen mit, sofern das Tor bestanden ist; das ist konservativ). **„bestätigt“**, wenn die untere Grenze des 95-%-Perzentil-Bootstrap-KI (10 000 Ziehungen, rng 4001) über 1 liegt und der einseitige exakte Vorzeichen-Permutationstest gegen 1 (2¹⁰ Vorzeichen) p < 0.05 gibt; **„unter Mindesteffekt“**, wenn die obere KI-Grenze unter 1 liegt und der gespiegelte Test (Mittel < 1) p < 0.05 gibt; sonst „unklar“. Der Vorzeichentest nimmt unter H0 Symmetrie um 1 an (das Design garantiert nur Symmetrie um 0 beim Tausch F/G); das wird so berichtet. Das Perzentil-KI ist bei n = 10 eher zu schmal.

**Bindung.** Die Auswertung nimmt nur Läufe, deren result.json den Trainer-Hash des Manifests, die Split-, Test- und Zielmetadaten-Hashes des Seeds, den Modell-Seed, die eingefrorenen Hyperparameter (Schritte, Batch, Kontext, Breite, Schichten, Köpfe, lr, Warmup, wd, K, Gerät, Verlust), die Laufkonstanten des Smoke-Laufs (Tokenizer-Hash, Textlänge, Schablonen), Status „completed“ nach 6000 Schritten, endliche Snapshots und keinen Text-Umlauf trägt; F und G eines Seeds müssen bis auf den Split-Hash dieselbe Konfiguration haben; im Rohordner dürfen nur die 20 erwarteten Laufordner liegen. **Ausfälle:** Ein Lauf ohne Ergebnis (Absturz, Zeitgrenze) wird vor der Auswertung mit identischem Befehl neu gestartet (der Trainer setzt am Checkpoint fort). Ein Lauf mit Status „error“ (nicht-endlicher Verlust) oder verletzter Bindung ist „defekt“, wird nicht ersetzt und macht den Block „nicht auswertbar (defekt/fehlt)“. Der Code darf sich nach dem Einfrieren nicht ändern (Hash-Prüfung in `--analyze`).

**Sekundär (beschreibend, kein Urteil).** Zurückgehaltene Genauigkeit je Lauf; Seeds mit Δ_pow > 0; je Paar s_learn (erster Snapshot mit Trainingsfakten ≥ 0.1 in F und G) und s_steer (erster Snapshot mit Δ_pow > 1), also H-folgt aus EXP-113 an frischen Seeds.

**Stichprobengröße.** n = 10 Seeds (20 Läufe) nach Regel 15b. Keine Poweranalyse aus Pilotstreuung möglich (Pilot EXP-114: 1 Seed, Δ_pow 5.60 bei Schritt 4000). Annahme für die Planung (Simulation des Prüfagenten mit derselben Regel, n = 10): bei wahrem Mittel 3 und SD 2.5 ≈ 75 % Wahrscheinlichkeit für „bestätigt“, bei SD 1.1 (P1, add 113) ≈ 100 %; Fehler 1. Art bei Mittel 1, SD 2.5: ≈ 5 %. Ist die Streuung größer oder lernen Seeds die Fakten nicht, fällt der Block eher „unklar“ oder „nicht auswertbar“ aus; das wird so berichtet.

**Budget.** 20 Läufe à 6000 Schritte über den GPU-Dienst (4 Worker, job_minutes 240). Pilot: 4000 Schritte in ≈ 36 min unter voller GPU-Last → ≈ 55 min je Lauf, Block ≈ 4–5 h.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen.** EXP-114 (Seed 3862 / Split 3802, K = 19, 4000 Schritte: Fakten ab Schritt 2000 gelernt, Δ_pow 5.60, zurückgehalten 0.98) → Wahl von K = 19, `--loss answer`, 6000 Schritte (Faktenlernen bei ≈ 2000 im Pilot, Reserve ×3), Tor bei 0.5. EXP-113 bis Schritt ≈ 6500 (K = 8, noch kein Faktenlernen) → K = 8 nicht gewählt. EXP-105-Pilot, EXP-102/112 (Stufe 1). Keine der Seeds 4000–4009 wurde je trainiert.

**Einordnung, falls bestätigt.** Aussage nur für diesen Aufbau: kleines LM, 79 % Rechen-Tokens, Verlust auf Text + Antworten, P1-artige konstruierte Splits, Energiemaß. Kein Beleg für „wenige Prozent“ Rechenanteil (Regel 20e); das wäre die nächste Sprosse. Funktionale Nutzung nicht gemessen.

**Smoke.** Vor dem Einreihen der 20 Läufe: ein Lauf (Seed 4000 F) mit 250 Schritten in einem getrennten Ordner (`lm1_smoke`, nicht gezählt) und ein Probelauf des Laders an diesem Lauf (Bindung außer Schrittzahl); Ergebnis unten (vor dem Einfrieren).

**Smoke (12:34 gemessen, Dienst `29_lm1_smoke`, 114.5 s):** Seed 4000 F, 250 Schritte, `lm1_smoke/lm2_seed4100_seed4000_F_steps250_0c896dda7304b68d`, completed. Lader (`AP.load`) liest den Lauf, Snapshots [0, 250], Ziele F = {15, 26, 30, 38, 45}; die Bindungsprüfung meldet nur „config steps“ (250 statt 6000, erwartet). Permutationstest-Probe: zehnmal 5.0 → p = 1/1024; Werte um 1 → p = 0.56. Der Smoke-Lauf zählt nicht.

**Unabhängige Prüfung vor dem Einfrieren (Claude-Agent, nur lesend; Codex ohne Guthaben):** kein Blocker; 6 Punkte übernommen: Zielmetadaten (`seed*.json`) im Manifest gebunden; Laufkonstanten (Tokenizer, Textlänge, Schablonen) aus dem Smoke gebunden und F/G-Konfigurationsgleichheit geprüft; Absturzpfade der Auswertung abgefangen (werden „defekt“); Ausfallregel vorab festgelegt; „widerlegt (bricht)“ → „unter Mindesteffekt“ mit gespiegeltem Test; nur die 20 erwarteten Laufordner zulässig (Präfix mit Schrittzahl). Texte korrigiert (Power ≈ 75 % statt „hoch“, Modell-Seeds frisch, Tor-Formulierung). Nachgeprüft am Smoke: Bindung meldet nur „config steps“; fehlender G-Lauf → „defekt“, Block „nicht auswertbar“.

## Ergebnis (Sitzung 53, 20:50 gemessen; eingefrorene Auswertung, danach unabhängig nachgerechnet)

Alle 20 Läufe fertig (GPU-Dienst `31_lm1`, 0 Fehlschläge), Code-Stand = Einfrier-Commit 2b70d8b9 (`git log` auf `confirm_lm1.py`), Bindung ohne Befund, keine defekten Läufe. Befehl: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/confirm_lm1.py --analyze` → `LM1_summary.json`.
- **Tor:** 20/20 Läufe mit zurückgehaltener Faktengenauigkeit ≥ 0.5 (0.898–0.995).
- **H1:** mittleres Δ_pow bei 6000 = **5.32 [4.86, 5.73]** (Perzentil-Bootstrap), 10/10 Seeds > 1 (Spanne 3.96–6.40), exakter Vorzeichen-Permutationstest gegen 1: p = 1/1024 (kleinstmöglicher Wert bei 10 Seeds); gespiegelter Test p = 1.0 → **„bestätigt“**.
- **Unabhängige Nachrechnung** (`LM1_independent_recompute.py`, getrennt geschriebener Lader): Mittel, KI, p, Tor, Lesart identisch; 20 Läufe gültig, keine Bindungsprobleme.
- **Sekundär (beschreibend):** je Paar s_steer (erster Snapshot mit Δ_pow > 1) gegen s_learn (erster Snapshot mit Trainingsfakten ≥ 0.1 in F *und* G): in 9/10 Paaren früher (8 × eine Snapshot-Stufe = 250 Schritte, 1 × zwei Stufen: 4005, 2250 gegen 2750), 1/10 gleichzeitig (4002, 2500), nie später. *(Erste Fassung dieses Satzes nannte „9/10 eine Stufe“; von der unabhängigen Prüfung korrigiert, Sitzung 53.)* Weil s_learn beide Arme verlangt, kann „früher“ heißen, dass die Steuerung mit dem Lernbeginn des ersten Arms kommt; keine Aussage „Steuerung vor dem Lernen“.
- **Einordnung (nach [[paper/LM1_DEUTUNGEN]], vorab):** Ein Aufbau mit hohem Rechenanteil (≈ 79 %), Energiemaß auf gebundenen Embeddings; kein Beleg für wenige Prozent Rechendaten oder für funktionale Nutzung (LM1-F läuft seit 20:51 als Dienst-Job `32_lm1f`). Die P1-Splits tragen die Ziele auch in den Zahl-Häufigkeiten ([[experiments/EXP-115-lm-flat-marginals/README|EXP-115]] „unklar“), LM1 ist deshalb kein Beleg für einen reinen Paarstruktur-Effekt.

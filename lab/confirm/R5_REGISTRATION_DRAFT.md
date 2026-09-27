---
id: R5
status: entwurf
datum: 2026-09-27
tags: [lab/confirm, programm/A, paper, exp/vorbereitet, neu/kandidat]
---
# R5: Beschleunigt ein spektral konstruierter Split das Grokking? Bestätigung an frischen Seeds (Registrierungsentwurf, ohne Code)

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, funktionale Wirkung der Split-Steuerung) · Pilot: [[experiments/EXP-018-split-speed/README|EXP-018]] · Literatur: [[paper/lit_grokking_speed_2026-09-27]] · [[JOURNAL]] Sitzung 30, Zyklen 11–12.

**Status:** Entwurf, Sitzung 30 (2026-09-27, bis 19:20 Berlin, gemessen), **vor jedem R5-Lauf, vor dem EXP-018-Kontrollarm D**. Kein Code. Der Code (`lab/tools/confirm_r5.py`, nach dem Muster von `confirm_r4.py`) wird erst nach dem EXP-018-Ergebnis geschrieben, danach folgen Codex-Prüfung, Selbsttest und Einfrieren. Ändert EXP-018 etwas an diesem Entwurf, wird das hier unter „Änderungen nach dem Pilot“ protokolliert, bevor ein R5-Lauf existiert.

## Warum

Post hoc (Sitzung 30): Konstruierte Splits generalisieren (Test ≥ 0.95) im Median nach ≈ 700 Schritten, zufällige gleich großer Größe nach ≈ 6000 oder gar nicht innerhalb von 2000 Schritten. Das gilt auch mit gemeinsamer Testmenge (EXP-041-Läufe auf den EXP-018-Splits: 9/10 gegen 0/10 bis 2150 Schritte) und bei gleichen Token-Häufigkeiten (EXP-047: 20/20 gegen 0/20). Bekannt ist eine Beschleunigung durch Datenauswahl über Token-Häufigkeiten (AlQuabeh et al. 2025). Eine Beschleunigung durch die Konzentration des Paarspektrums wurde nach unserer Suche nicht gefunden (vorläufig). Alle bisherigen Zahlen sind gesehen oder post hoc; eine Kernaussage braucht frische Seeds.

## Aufbau (vorläufig)

- add 113, 1-Schicht-Transformer (arch25k), AdamW lr 1e-3, wd 1, Trainingsmenge 3831 Paare, GPU, `--threads 1`, Obergrenze 8000 Schritte (`--stop-after-gen 25`), Testauswertung alle 25 Schritte, `generalization_step` des Trainers (Test ≥ 0.95).
- Je Einheit (frische Init-Seeds, Bereich nach 2719 zu reservieren) eine gemeinsame gleichverteilte Testmenge T* (20 %) und drei Trainingsmengen aus dem Rest, Konstruktion wie EXP-018 (`make_splits.build`): **E** (ε = 2, fünf Ziele), **D** (Gewichte von E innerhalb jeder Antidiagonale permutiert, gleiche Ziehungsschlüssel), **R** (gleichverteilt). Die Split-Zufallsströme werden **nicht** aus dem Init-Seed gezogen (eigener Schlüssel, Regel 18a6).
- **Primärgröße** wie EXP-018: beschränkte Zeit min(gen, 8000), L = log2(min(gen_X, 8000) / min(gen_E, 8000)).
- **Hypothesen (Holm über 2):** **H-ER:** E generalisiert früher als R (L_RE > 0). **H-ED:** E generalisiert früher als D (L_DE > 0). Je Hypothese: einseitiger Vorzeichen-Permutationstest über die Einheiten und, als Ko-Bedingung, ein zensierungsfester exakter Vorzeichentest (wie EXP-018 Nachtrag a); „bestätigt“ nur, wenn beide nach Holm p < 0.05 erfüllen. Effektgröße: mittleres L mit 95-%-Bootstrap-KI, Faktor 2^L̄.
- **Mindesteffekt:** L̄ ≥ 1 (Faktor 2) als KI-Untergrenze für die Paper-Aussage „mindestens doppelt so schnell“; darunter wird nur „schneller“ berichtet.
- **Stichprobe (Regel, fest vor dem Pilot):** n = max(20, n_D), n_D aus der Pilotstreuung von L_DE in EXP-018 (SD über die 10 Seeds, Normalnäherung, 80 % Power für einen wahren Effekt L = 1 bei α = 0.025 einseitig), gedeckelt bei 60. Ist L_DE im Pilot ≤ 0 (D so schnell wie E), wird H-ED nicht verworfen, sondern bleibt als Test bestehen (dann mit n = 60), und die Deutung „spektrale Konzentration“ entfällt für den Pilot.
- **Beschreibend:** L_RD, Anteile generalisierter Läufe je Arm bei 2000/8000, Überlappung der W_E-Top-5 mit den Zielen bei gen.
- **Budget:** 3n Läufe, E ≈ 1000 Schritte, D/R bis 8000; bei n = 20 ≈ 30 min GPU (10 parallel).

## Was dagegen spräche

- H-ER nicht bestätigt an frischen Seeds: Die Beobachtung war ein Zufall oder hängt am CPU-Pfad bzw. an den EXP-018-Seeds.
- H-ER bestätigt, H-ED nicht: Die Beschleunigung braucht keine spektrale Konzentration; jede Ungleichverteilung dieser Art reicht (Gewichtsverteilung und Abdeckung pro Antidiagonale).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-016 und EXP-003d (Seeds 10–19), P1 (Seeds 1000–1049), EXP-047 (Seeds 150–159), EXP-041 (E/R auf den EXP-018-Seeds 20–29 mit T*). Das Skript dazu: `lab/confirm/speed_posthoc_gen_steps.py`, `lab/confirm/EXP041_posthoc_speed.py`. Beeinflusst: die Hypothesen, die Wahl der Arme (aus EXP-018 übernommen), die Obergrenze 8000 und der Mindesteffekt. Kein Lauf mit R5-Seeds.

## Grenzen (vorab)

Eine Aufgabe, eine Architektur, eine Optimierer-Einstellung, ε = 2, 30 % Trainingsanteil; „schneller“ heißt früherer Testanstieg auf T*, nicht bessere Endgenauigkeit.

## Codex-Designprüfung (Sitzung 30, `lab/confirm/R5_codex_design_review_s30.txt`, vor jedem Lauf): nicht einfrierbar, Punkte für die Überarbeitung nach EXP-018

Selbst geprüft und **alle übernommen** (Umsetzung beim Schreiben des Codes, dann erneute Codex-Prüfung):
1. **BLOCKER, bestätigt:** D gleicht nur die Zieh-Gewichte je Antidiagonale an, nicht die gezogene Maske. An den EXP-018-Splits (Seeds 20–22) weichen die realisierten Anzahlen je Ausgabe c zwischen E und D im Mittel um 2.8–2.9 Paare ab (höchstens 10 bei ≈ 34 je c); die Streuung ist ähnlich (CV E 0.12–0.13, D 0.13–0.14, R 0.14). → Für R5 D aus der **realisierten E-Maske** bauen, per Permutation innerhalb jeder Antidiagonale (Anzahl je c exakt gleich). Dazu Abgleich je Seed für die Grade von a und b, den Tauschanteil (b, a), die Testnachbarschaft und den Zusammenhang, mit eingefrorenen Toleranzen und Verwerfungsregel.
2. **BLOCKER:** Schätzgröße ausdrücklich T₈₀₀₀ = min(T, 8000); Aussagen nur für diesen Horizont. Ereignis erst bei ≥ 3 aufeinanderfolgenden Auswertungen mit Test ≥ 0.95 (`--stop-after-gen ≥ 75`) und vorheriger Memorisation (Train ≥ 0.99); sonst „frühere Generalisierung“ statt „Grokking“.
3. **BLOCKER:** Je Kontrast p_j = max(p_L, p_Vorzeichen), danach Holm über die zwei Kontraste; Regeln für Gleichstand, Doppelzensur, fehlende Läufe und KI festschreiben.
4. **BLOCKER:** „Faktor 2“ nur als Punktschätzer berichten (geometrisches Mittel des beschränkten Zeitverhältnisses) oder die Power für die Untergrenze L > 1 auslegen. n per **Simulation der vollständigen Entscheidungsregel** (Zensur, Ko-Bedingung, Holm) aus der Pilotverteilung bestimmen, mit festgelegter Rundung und Deckel.
5. **MAJOR:** Explizite Listen für Init-, Test-, Ziel- und Ziehungs-Seeds in getrennten Namensräumen, zufällige Zuordnung Split-ID ↔ Init-ID, Hashes; vorzugsweise mehrere unabhängige Splits je Init.
6. **MAJOR:** Zielfrequenzen unabhängig von der Init wählen und mindestens zwei Zielmengen je Init kreuzen; die Aussage auf wd = 1 beschränken (keine Weight-Decay-Replikation geplant).
7. **MINOR:** Post-hoc-Belege nur als hypothesenbildend; 2^L̄ als geometrisches Mittel des beschränkten Zeitverhältnisses benennen; Laufreihenfolge zufällig und eingefroren.

*Werkzeug (19:26):* `lab/confirm/R5_power_sim.py` simuliert die vollständige Entscheidungsregel (Obergrenze, p = max(p_L, p_Vorzeichen), Holm) aus den Pilotzeilen von EXP-018 (`summary_cuda.json`), optional mit verschobener Effektgröße. Ungetestet; Selbsttest nur im Fenster. Das Ereignis im Pilot ist noch „erste Kreuzung“, nicht „3 aufeinanderfolgende“, daher nur eine Näherung.

## Nachtrag Sitzung 31 (2026-09-27, 19:34 Berlin, gemessen; post hoc, vor jedem R5-Lauf): Dosis-Wirkung als Designvorschlag

**Neu gesehene Daten:** Die Nur-G-Läufe von EXP-020 (ε = 2) und EXP-042 (ε = 1, ε = 8) teilen je Seed (30, 31, 32, 34) Init und Testmenge (Prüfsummen gleich), die Trainingsmenge hat immer 3831 Paare, die Streuung der Zeilen-, Spalten- und Ausgabezahlen ist bei allen ε ähnlich (SD 3.9–5.6). Nur die Konzentration ändert sich (Zielanteil von M0: 0.115 / 0.18 / 0.36). Generalisierung (Test ≥ 0.95, erste Kreuzung) innerhalb von 2000 Schritten: **ε = 8: 450, 425, 425, 450**; **ε = 2: 750, 900, 700, 800**; **ε = 1: keine** (Test am Ende 0.80, 0.07, 0.07, 0.06). Strenge Ordnung ε 8 < 2 < 1 in 4/4 Seeds (`lab/experiments/EXP-042-bias-strength/posthoc_speed_dose.py`). Die Memorisation liegt bei allen ε bei 110–140 Schritten. Die F-Läufe von EXP-042 wiederholen die Generalisierungsschritte von EXP-020 exakt (950, 625, 1225, 650), obwohl der Code-Stand ein anderer ist.
**Vorschlag für die Überarbeitung (nicht übernommen, bis R5 nach EXP-018 neu gefasst wird):** zusätzlich oder statt eines Teils von D eine **Dosis-Wirkungs-Hypothese** über ε ∈ {1, 2, 8} (oder den Zielanteil als stetige Größe) mit derselben Init und Testmenge je Einheit, getestet als Trend (z. B. Page-Test oder Vorzeichentest der Ordnung je Einheit, zensierungsfest). Das trennt „Konzentration wirkt abgestuft“ von „jede Ungleichverteilung reicht“ auf einem zweiten Weg. Eine Grenze gilt dabei: Mit ε ändert sich die Ziehung und damit, welche Paare im Split liegen; ein reiner Dichteeffekt ohne Spektrum ist dadurch nicht ausgeschlossen.
**Beeinflusst:** Seeds 30–34 sind damit auch für die Geschwindigkeit gesehen (vorher nur für die Festlegung).
**Ergänzung (19:41, post hoc, gleiche Läufe):** Der W_E-Anteil auf den Zielen bei Schritt 250 ist in 4/4 Seeds gleich geordnet (ε 8 / 2 / 1: 0.49–0.50 / 0.30–0.34 / 0.12–0.15; `posthoc_speed_amplitude.py`). Vorschlag: diese Größe in R5 je Arm beschreibend mitberichten (Frage: Läuft die Beschleunigung über das frühe Zielsignal?), ohne sie zur Hypothese zu machen.


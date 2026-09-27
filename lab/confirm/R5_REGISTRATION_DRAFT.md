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

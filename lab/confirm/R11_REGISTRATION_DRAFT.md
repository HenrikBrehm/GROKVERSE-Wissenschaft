---
id: R11
status: entwurf
datum: 2026-09-28
tags: [confirm/entwurf]
---
# R11-Bestätigung (Entwurf): Legt sich die frühe Wahl auch bei add 97 und mul 113 zwischen 25 und 50 Schritten fest?

Zurück: [[LAB]] · [[FINDINGS]] (Grenze 2: Persistenz K4–K4e nur bei add 113 bestätigt; Regel 15c/19b) · Pilot [[experiments/EXP-044-generalize-lockin/README|EXP-044]] · Vorbilder [[confirm/R10_REGISTRATION_DRAFT|R10]], [[confirm/N28_REGISTRATION|N28]] · [[paper/STATUS]]

**Status:** Fassung 2 (siehe unten) mit Code, Sitzung 43. `lab/tools/confirm_r11.py`, **ungetestet** (nur Syntax), **nicht eingefroren**. **Einfrieren erst nach dem Commit des L0-Trainer-Patches** (STATE Schritt 8), Block mit `--workers 5` neben L0. Vor dem Einfrieren: unabhängige Prüfung von Design und Code (Codex ohne Guthaben → Claude-Agent, nur lesend), Selbsttest über den Wächter (ab 00:00), dann Einfrieren wie R10.

## Frage und Bezug

K4 (P3, N28, N29; add 113): Nach 25 Schritten auf dem ersten Split setzt sich ein Datenwechsel überwiegend durch, nach 50 Schritten hält das Netz an der ersten Wahl fest. Bei add 97 und mul 113 gibt es dazu nur den Piloten EXP-044 (10 Seeds, beschreibend π): add 97 π(25) 0.37 / π(50) 0.86, mul 113 0.22 / 0.72. Das Paper braucht für die Aussage „die Festlegung verallgemeinert sich“ eine Bestätigung an frischen Seeds mit eingefrorenem Manifest (Regel 18c, 19b).

## Hypothesen (Familie, Holm über 6 = 2 Aufgaben × 3, α = 0.05)

Protokoll wie EXP-044: je Aufgabe und Seed eine gemeinsame Testmenge (20 % aller p² Paare) und zwei konstruierte Trainingsmengen F und G (je 30 %, disjunkte Zielmengen aus je 5 Frequenzen, EXP-043-Konstruktion in Gruppenkoordinaten, ε = 2, unabhängige Schlüssel, Überlappung ≈ 37 %). Läufe: rein F, rein G, F → G bei t = 25 und bei t = 50, jeweils danach 2000 Standardschritte (AdamW lr 1e-3, wd 1, β 0.9/0.98; GPU). π(t) = (L(t) − L(G)) / (L(F) − L(G)), L = log[P(F-Ziele)/P(G-Ziele)] der W_E-Gruppenleistung am Ende (EXP-044-Definition).
Je Aufgabe (add 97, mul 113):
- **H1 (Festlegung wächst):** d = π(50) − π(25) > 0. Einseitiger t-Test; bestätigt = Holm-p < 0.05 **und** 95-%-Bootstrap-KI-Untergrenze > 0. Pilot: add 97 +0.49 (SD 0.16), mul 113 +0.49 (SD 0.20).
- **H2 (Persistenz bei 50):** π(50) − 0.5 > 0 (mehr als die Hälfte der F-Neigung bleibt). Wie H1. Pilot: +0.36 (SD 0.13) / +0.22 (SD 0.15).
- **H3 (Umstieg bei 25):** 0.5 − π(25) > 0 (der zweite Split setzt sich überwiegend durch). Wie H1. Pilot: +0.13 (SD 0.12) / +0.28 (SD 0.17).
- **Lesart:** alle 6 → „K4 verallgemeinert bestätigt“, sonst Liste der bestätigten. Nicht bestätigte H3 bei bestätigten H1/H2 hieße: Die Festlegung wächst und hält bei 50, aber schon bei 25 überwiegt die erste Wahl (früheres Fenster als bei add 113). Das wäre ein Befund, kein Fehlschlag.
- **Beschreibend:** π-Mittel je t und Aufgabe (im Code); der Vergleich mit dem Piloten und mit add 113 (EXP-020: 0.41 / 0.74) erfolgt nur im Text.
- **Was die Bestätigung heißt und was nicht:** W_E-Energiemaß (π), keine Funktion/Ablation (K4c bleibt add 113). Eine Architektur (1 Schicht), eine Richtung (F → G).

## Umfang, n

4 Läufe je Seed und Aufgabe → **n = 30 Seeds (3620–3649, frisch: Dateisuche 28.09. Sitzung 43 ohne Treffer), 240 GPU-Läufe** (je ≈ 2000–2050 Schritte; ≈ 40 min mit 8 Workern). **Power** (Normalnäherung des t-Tests mit Holm über 6, 2000 Wiederholungen, Sitzung 43): voller Piloteffekt ≈ 1.0 überall; halber Effekt bei Pilot-SD: add 97 H3 0.90, mul 113 H2 0.98, sonst ≥ 0.99; 0.75 × Effekt bei 1.5 × SD: add 97 H3 0.89, sonst ≥ 0.98; halber Effekt bei 1.5 × SD: add 97 H3 0.54, mul 113 H2 0.74 (n = 20 lag bei halbem Effekt für add 97 H3 bei 0.71 → n = 30, weil kleine Piloten die Streuung unterschätzen).

## Verbindliche Einzelheiten (wie im Code)

- **Splits:** `EXP-044/make_splits.build(seed, task, p)` und `EXP-043 make_split.target_set` deterministisch aus dem Seed; Dateien `lab/confirm/r11_splits/r11_{task}{p}_seed{s}_{test,train_F,train_G}.npy` + `.json`. Bei `--analyze` wird jeder Split neu gebaut und byte-genau verglichen (sonst ist die Bestätigung nichtig).
- **Gültigkeit:** jeder Lauf über den gemeinsamen Lader (Seed, Gerät cuda, Schritte, Split-/Test-/Wechselhash, p/task, lr 1e-3, wd 1, train_frac 0.3, β 0.9/0.98, keine Vor-Wechsel-Optionen, Schnappschuss am Ende, endliche Werte) und die Bindung (Manifest-Commit, Code-Hashes). Jeder technische Fehler → ganzer Block *nicht auswertbar*. Seeds mit L(F) − L(G) < 2 werden je Aufgabe ausgeschlossen und gezählt (Pilot: Minimum 4.3 bzw. 5.4); mehr als 4 in einer Aufgabe → deren drei Hypothesen *nicht auswertbar* (sie verlassen die Holm-Familie).
- **Einfrieren (ab 00:00, nach R10-Ende und nach bestandener Prüfung):** `python lab/tools/guarded_run.py -- python lab/tools/confirm_r11.py --selftest` (grün) → Manifest `lab/confirm/R11_manifest.json` = `REGISTERED` + `python` (absoluter venv-Pfad wie R10) + `registration` + `code_sha256` (`--hash-code`), committen, Commit-ID in `commit`, erneut committen → `python lab/tools/confirm_r11.py --splits lab/confirm/R11_manifest.json` → `python lab/tools/confirm_r11.py --jobs lab/confirm/R11_manifest.json > lab/confirm/R11_jobs.txt` (ohne Wächter) → Splits/Jobs committen → Smoke: `python lab/tools/confirm_r11.py --smoke-jobs lab/confirm/R11_manifest.json > lab/confirm/R11_smoke.txt` (erste Jobzeile und ihre beiden Wechselzeilen) über `parallel_queue.py --workers 3`, dann `python lab/tools/guarded_run.py -- python lab/tools/confirm_r11.py --smoke-check lab/confirm/R11_manifest.json` (Laderstatus, keine Werte) → Block `parallel_queue.py lab/confirm/R11_jobs.txt --workers 5` (neben L0; allein bis 8) → `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r11.py --analyze lab/confirm/R11_manifest.json`.
- **Reihenfolge zum Trainer-Patch von EXP-097:** R11 bindet den Hash von `freq_ban.py`. Entweder R11 vor dem Anwenden des EXP-097-Patches einfrieren und vollständig rechnen und auswerten, oder erst nach dem Patch-Commit einfrieren. Niemals den Trainer zwischen Einfrieren und `--analyze` ändern.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-044 (Seeds 80–89, beide Aufgaben: π bei 25/50/150, Gültigkeitsmaße L(F) − L(G), Wahl von t = 25/50 und der Schwellen 0.5 und 2), EXP-020/P3/N28/N29 (add 113), EXP-096 benutzt dieselbe Splitkonstruktion mit anderen Seeds (3560–3575). Keine R11-Seeds wurden je benutzt.

## Fassung 2 (Sitzung 43, nach der Prüfung vor dem Einfrieren, vor jedem R11-Lauf): verbindlich, ersetzt Abweichendes oben

Unabhängige Prüfung (Claude-Agent, nur lesend; Codex ohne Guthaben): **kein Blocker, nichts Größeres.** Geprüft und bestätigt: Run-IDs (gleiches Muster wie die EXP-044-Rohdaten), 240 eindeutige Jobzeilen, die `check_job` annimmt; Lader-Erwartungen an gespeicherten Pilotläufen (config p/task/lr/wd/train_frac/β, Schnappschuss am Ende); Importe (keine Namenskollision EXP-043/046, alle geladenen Module in CODE_FILES); π identisch mit `pi_persistence.py`; Holm nur über auswertbare Hypothesen; Selbsttest-Fälle; Splits (Größen, Überlappung ≈ 0.375, disjunkte Ziele, Neubau identisch). Übernommen:
- **Nicht-endliche Log-Verhältnisse** gelten jetzt als technischer Fehler (vorher als Ausschluss).
- **Offenlegung Zufallsströme:** Der Split-Strom von Seed s (`default_rng(s + 44017)`, EXP-044) ist derselbe Generator wie der G-Zielstrom von Seed s + 16 (`default_rng(s' + 44001)`, EXP-043); in 3620–3649 betrifft das s = 3620–3633 (bei mul ebenso, +500000 auf beiden Seiten). Die statistische Abhängigkeit ist vernachlässigbar (verschiedene Verwendungen der Ziehungen). Wir ändern das Protokoll nicht, legen es aber offen.
- **Power mit KI-Regel** (Simulation des Prüfers): add 97 H3 bei halbem Effekt und Pilot-SD 0.85 statt 0.89 (t-Test allein), bei 1.5 × SD 0.53 statt 0.60.
- **Gleiche Init-Seeds für beide Aufgaben, nur Richtung F → G:** Aufgaben werden getrennt ausgewertet; Holm gilt bei beliebiger Abhängigkeit; F und G sind nach Konstruktion austauschbar.
- Smoke-Befehle `--smoke-jobs` / `--smoke-check` ergänzt (siehe oben).

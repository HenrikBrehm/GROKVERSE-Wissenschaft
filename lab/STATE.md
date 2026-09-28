---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-28, 19:51 Berlin (Sitzung 43; **Regel 20 Wochenplan gilt**; Rechenfenster durchgehend 28.09. 23:59 bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Sitzung 43 hat STATE gekürzt (Astra-Punkt 17). Die alten Abschnitte „Lage“ und „Nächste Schritte“ der Sitzungen 26–42 stehen unverändert in den Abschlussberichten im [[JOURNAL]] und in `git show 7f9d56d4:lab/STATE.md`. Alle dort genannten Nachtschritte vom 28.09. (P2f, R1–R9, EXP-018 … EXP-095, Repro-Paket) sind erledigt.*

## Lage

- **Bestätigt (Kernaussagen, [[FINDINGS]]):** K2 (Split steuert Frequenzen, 4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (inkl. D₅₉), K4–K4e (Festlegung in 25–50 Schritten, Reset-Rollen), R2–R9 (Robustheit, Wechselkosten, Zufallssplit, Uhr), **K5** (Festlegung tickt in Λ bei in Λ gemessenen β-Fenstern, R9).
- **Neueste Exploration:** [[experiments/EXP-095-gradient-feedback/README|EXP-095]] „Auswertungen zählen“: Bei 24 Adam-Schritten legen 3 Gradientenauswertungen so schwach fest wie 3 große Schritte (e8 +0.141 [0.060, 0.211]). Nur der Anfangsgradient bewegt W_E weiter, aber unselektiver (Nicht-Ziele ×1.48, post hoc). **Sitzung 43 (Nachtrag b):** Das ist Vorzeichenabstieg (Adam mit festem g₀); Binarisieren erklärt ≈ 56 % der Zielanteil-Lücke. Nur g24 ist betroffen (g8/c8b weniger quantisiert als n24). Trennender Versuch [[experiments/EXP-097-sign-vs-staleness/README|EXP-097]] vorbereitet.
- **Paper:** [[paper/draft]] §1–§5 mit allen Bestätigungen; Repro-Paket vollständig (9/9 Skripte reproduzieren); One-Pager fertig. Offene Nutzerentscheidungen in [[paper/STATUS]].

## Aktive Queue / laufende Jobs

- **Keine Prozesse** (Sitzung 43, 18:21 geprüft).
- **R10 halb gerechnet:** eingefroren 7b583bdb (n = 48, Seeds 3500–3547, 480 GPU-Läufe). 268/480 gebunden, 0 Fehler, Wächterstopp 17:52 regulär. **Ergebnisse ungesehen, nicht ansehen vor 480/480.** Regel 20a: zu Ende rechnen, Ergebnis in den Anhang (K5/R9/R10-Nebenabschnitt).
- **Zurückgestellt nach Regel 20a (Mechanismus-/Detailversuche, NICHT starten; Vorbereitung bleibt erhalten):** EXP-096 (a3bd9415), EXP-097 (Patch `trainer_psu.patch`), EXP-098 (45d66cad), EXP-099 (Patch `trainer_wef.patch`, setzt auf psu auf). Entwurf R11 (Festlegung K4 bei add 97/mul 113, `confirm_r11.py`, Fassung 2): als GPU-Füllarbeit nach dem L0-Patch-Commit einfrieren (siehe Schritt 8).
- **Trainer-Hash:** R10 bindet `freq_ban.py` (da4d7bc0…). Änderungen am Trainer (z. B. Minibatch für L0) erst nach `confirm_r10.py --analyze` committen; bis dahin nur als Patch.

## Nächste Schritte (Regel 20, verbindliche Reihenfolge; Läufe ab 28.09. 23:59 über guarded_run.py / parallel_queue.py)

1. `python lab/tools/guarded_run.py --check` (ab 23:59 allowed); kein STOP; Prozesse prüfen. In `lab/confirm/r10_raw/` nach `run.lock` ohne `result.json` suchen: beiseitelegen (`.stale_s42`), nicht löschen.
2. **R10 fertig:** `python lab/tools/parallel_queue.py lab/confirm/R10_jobs.txt --workers 8` (≈ 212 Läufe, 30–40 min; GPU-Prozesse ≤ 10). Danach `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r10.py --analyze lab/confirm/R10_manifest.json`; Ergebnis in R10, FINDINGS, Paper-Anhang (Entscheidungstabelle in [[paper/STATUS]]). **Die unabhängige Nachrechnung VOR dem L0-Patch-Commit** (danach verweigert `check_code`; sonst nur über `git worktree add <dir> 7b583bdb`). **Parallel zu R10 (CPU, keine gebundene Datei):** Nanda-Skript (Schritt 4).
3. **PRIORITÄT 1, L0 „Menge gegen Reihenfolge“ (Regel 20b):** (a) LeDoux-Methode: erledigt (Sitzung 43, [[paper/related_work]] letzter Nachtrag). (b) Trainer-Optionen **liegen als Patch vor**: `lab/experiments/EXP-100-set-vs-order/trainer_l0.patch` (`--batch-size`, `--order iid|fixed|stride`, `--optimizer sgdm`; Test `test_minibatch_order`; Prüfbefund im JOURNAL Sitzung 43). Nach R10 `--analyze`: `git apply` → Trainer-Tests über den Wächter → commit. Entwurf [[experiments/EXP-100-set-vs-order/README|EXP-100]]; `design.py` (Splits für Seeds 3700–3707 committet), `calib.txt`, `smoke.txt` und `analyze.py` (Lesarten im Docstring, ungetestet, statisch geprüft) stehen. **Fassung 2 nach Prüfung** (1 Blocker + 3 Major behoben). Ablauf: Patch anwenden → Tests → commit → `analyze.py --selftest` → Smoke (`raw_smoke`, s/Schritt messen) → **Machbarkeit** `feas.txt` (wirkt Stride bei 30 % Daten? Ausweichregel in der README) → Kalibrierung `calib.txt` → `SGD_LR` setzen → `--jobs` → commit → Block (112 Läufe) → `analyze.py`. Details in der README. (c) Pilot (bekannte oder frische Seeds, als Exploration gekennzeichnet): K2 (Δ_pow) und R5 (Zeit bis Grokking); sekundär Wechsel bei 25/50 unter Minibatch. (d) Registrierung: Gerüst [[confirm/L0_REGISTRATION_DRAFT|L0]] (H1/H2 vorab, Seeds 3720–3799 reserviert); n/H3 nach dem Piloten, dann `confirm_l0.py`, Prüfung, Einfrieren, Block. Jeder Ausgang ist ein Befund.
4. **Absicherung ohne neues Training (Regel 20c):** (i) Nanda: `lab/confirm/P2_nanda_s43.py` (nanda_exact der Studie, eigene Ziele gegen fremde, P2d add 113 + P2e add 97; Lesarten im Docstring; ungetestet) → `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/P2_nanda_s43.py --selftest`, dann ohne `--selftest` (CPU, lädt 80 Modelle). Offen: mul 113 (Gitter nach diskretem Log umordnen), D₅₉ (Irrep-Projektion). (ii) RFM: Code geklont nach `lab/external/rfm-grokking` (Commit 73181df8, 261 KB, **GPL-3.0**, nicht ins Repo committen). Er braucht jax, neural-tangents, wandb, scipy und einops. **Installation nur, wenn KEIN `.venv-gpu`-Job läuft** (auch nicht R11/L0), zuerst `pip install --dry-run` mit einer Constraints-Datei, die numpy (2.5.3) und torch (2.9.1+rocm7.2.1) festhält. jax läuft unter Windows nur auf der CPU. Versionen festhalten, `--wandb_offline`. Entwurf [[experiments/EXP-101-rfm-k2/README|EXP-101]] (Datenformat identisch, Split per Wrapper; Δ_pow auf den AGOP-Blöcken).
5. **Paper schärfen (Regel 20d, Ziel ≈ Do 01.10.):** [[paper/draft_short]] hat Abstract (1659 Zeichen + L0-Platz), Einleitung, Aufbau, Ergebnisse 1–3, L0-Methode und Grenzen (≈ 4100 Wörter), jeder Abschnitt unabhängig geprüft und korrigiert. Offen: L0-Ergebnis, Abbildungsauswahl, Anhang-Struktur, Tomàs Bernal im PDF. Zenodo: Entwurf `lab/paper/zenodo/` (Metadaten mit Nutzer-Platzhaltern, `make_package.py --dry-run`: 4753 Dateien, 82 MB), nicht hochladen.
6. **Täglich (Regel 20h):** `lab/paper/erklaerung/ERKLAERUNG_<datum>.md` (eine Seite, einfaches Deutsch, 3 Jury-Fragen mit Antworten), in [[LAB]] verlinken.
7. Ab ≈ Fr 02.10. nach L0: Sprachmodell-Leiter (Regel 20e), Stufe 1 entworfen: [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]] (eigener kleiner Trainer nötig); Checkpoints (20g) ab Stufe 2; Downloads nur nach 20f, alles im JOURNAL.
8. **GPU-Auslastung (Regel 20i) und Trainer-Hash, empfohlene Reihenfolge:** R10 fertig und ausgewertet → L0-Patch anwenden, testen, committen → **erst jetzt** R11 einfrieren (bindet dann den Trainer mit L0-Optionen; Standardverhalten unverändert) und als GPU-Füllarbeit neben den seriellen L0-Schritten (Smoke, Machbarkeit, Kalibrierung) rechnen: **R11 mit `--workers 5`, L0 mit höchstens 5** (Smoke 3), zusammen ≤ 10 GPU-Prozesse; die Worker-Zahlen in R11-Registrierung und EXP-100-README sind entsprechend gesetzt. Danach den Trainer bis zum Ende von R11 und L0 nicht mehr ändern. R11 stärkt Kernaussage 3 des Papers (bisher nur add 113) und ist kein Mechanismus-Detailversuch.

## Prioritäten (Regel 20 geht vor; 18c + 19)

1. **L0** Menge gegen Reihenfolge unter Minibatch (Pilot → Registrierung → Bestätigung).
2. **Absicherung** Nanda restricted/excluded (P2d/e/f), K2 in RFM.
3. **Paper** ≤ 8 Seiten, 3 Kernaussagen + L0, Zenodo-Paket; tägliche ERKLAERUNG.
4. R10 zu Ende (Anhang). Mechanismus-Versuche (EXP-096–099) ruhen.

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit Sitzung 33). Ersatz: unabhängige Claude-Agenten, nur lesend. Nicht umgehen (Regel 12).
- **HIP-Startfehler** „No HIP GPUs are available“ bei 12–14 gleichzeitigen GPU-Prozessen: ≤ 10 halten, betroffene Läufe mit weniger Workern neu.
- **`lab/confirm/rank_tools.py` NICHT ändern** (Code-Tore C1–C4). C1/C2-Selbsttests nur über `lab/confirm/C12_selftest_wrapper.py`.
- Eingefrorene Blöcke prüfen Code-Hashes: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`). Smoke durch den eingefrorenen Lader vor jedem Block ist Pflicht.
- `--analyze`/`analyze.py` brauchen `PYTHONIOENCODING=utf-8` (Bash-Syntax; in PowerShell `$env:PYTHONIOENCODING='utf-8'`). Auswertungen und Selbsttests laufen mit dem globalen Python über den Wächter; `.venv-gpu` nur für die Trainer-Jobzeilen. Jobdateien per `--jobs` ohne Wächter erzeugen (sonst landen `[guard]`-Zeilen darin).
- `freq_ban.py` stoppt standardmäßig 2000 Schritte nach der Generalisierung (`--stop-after-gen`); `group_train.py` läuft voll.
- Gelegentlich WinError 5 bei `os.replace` von result.json: Queue neu starten genügt.
- Globales Python ohne scipy. Uhrzeiten nur gemessen (Python zoneinfo).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`, `lab/paper/outreach/`) **nicht committen**; immer einzelne Pfade.
- CRLF: kein `sed -i` auf Notizen.
- Eine Runner-Sitzung endet mit der Antwort: laufende Jobs im Vordergrund beobachten, nie „Wecker stellen und aufhören“.

---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 11:45 Berlin (Sitzung 50 läuft, Deadline 14:29) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (Nanda 20/20, nachgerechnet), K4–K4e, R2–R10, K5, **R11** (Festlegung auch add 97 / mul 113), **L0** (K2 unter i.i.d.-Minibatch B 256/64, 10 frische Seeds, eingefroren 26419818, nachgerechnet).
- **Explorationen Sitzung 46:** EXP-100-Pilot (Reihenfolge wirkt bei B 256/64 nicht; SGD nicht kalibrierbar; B 16 lernt bei wd 1 nicht), Wechselläufe (unter B 256 keine Festlegung bis 50 Schritte), **EXP-106** (B 16, wd 0.1: Menge steuert; Reihenfolge verschiebt nur auf Zufallssplits, kostet auf konstruierten ×1.6 Zeit; nachgerechnet), **EXP-107** (unter B 256 Fenster bei 100–200 Schritten, t½ ≈ 133 = 8.9 Epochen; nachgerechnet), **EXP-108** (Batch-Reihe: Festlegung skaliert ≈ √(N/B), α = 0.54 [0.52, 0.56]; nachgerechnet; ohne Full-Batch-Punkt α = 0.556 [0.513, 0.595]), EXP-103 (lr·wd-Uhr ab ≈ 250 Schritten, früh zählt lr), EXP-101 (RFM ohne K2-Lesart).
- **Paper:** Langfassung §3.16 (R10), §3.17 (R11); Kurzfassung §5 (R11), §6 mit L0-Pilot, Bestätigung, EXP-106/107, Grenzen angepasst. Abb. 4 aus echten Daten (Titel noch deutsch). §6 und Abstract nach unabhängiger Textprüfung korrigiert (19 Punkte, Sitzung 46); Abstract 1875 Zeichen.

- **Sitzung 47 (29.09., 03:29–06:29):** **N54b bestätigt** (Festlegung unter Minibatch ≈ √(N/B): α(1e-3) 0.583 [0.560, 0.606]; doppelte lr hilft bei kleinen Batches weniger: Δα +0.139 [0.098, 0.178]; eingefroren 624c2213, nachgerechnet) → Paper §6/§7, Langfassung §3.19, FINDINGS-Zeile. Explorationen: EXP-109 (lr 2e-3), EXP-110/111 (lr 4e-3 bei B 64: auf 2 Seeds später, auf 2 anderen etwas früher → nicht belastbar), Modellvergleich (Drift + ≈ 2 Epochen), Memorisierungsuhr (unklar), **EXP-102 Leiter Stufe 1** (Format hält; Verlust auf allen Positionen verzögert Grokking > ×10, Steuerung reduziert, wächst).

- **Sitzung 50 (ab 11:30):** Kurzfassung gekürzt (≈ 4 300 Wörter Haupttext, Anhang M mit den wörtlich verschobenen Passagen, geprüft), neue Abb. 4 (`fig13`, nur L0 + N54b), Tabelle 1 ergänzt, Literatur-Nachsuche (Khanh 2026b). EXP-113 Nachtrag 1: Vorhersage **H-folgt** (im LM folgt Δ_pow dem Faktenlernen) vor dem Ergebnis festgelegt.

## Aktive Queue / laufende Jobs (Stand Ende Sitzung 49, 11:20 Berlin)

- **GPU-Dienst (Regel 21)**, Stand `lab/queue/status.json`: `34_repro_r4` (240 Läufe, läuft) und **`40_exp113_stage2b`** (8 LM-Läufe à 16 000 Schritte, erste 2 laufen seit ≈ 11:18; voll parallel erst nach R4; geschätzt mehrere Stunden; Checkpoints alle 1000 Schritte, setzt nach Absturz fort).
- **Repro-Paket (S49):** L0 (H1 bitgleich; H2 3/20 Läufe spät abweichend = GPU-Nichtdeterminismus, an 3728 F belegt → nach Regel „not reproduced“, Urteil gleich), R5, R6, R8 **exakt reproduziert**. Offen: R4 → `python lab/tools/guarded_run.py -- python lab/paper/repro/r4.py --device cuda --compare-r4`, dann Zeile in [[paper/repro/README]] und Anhang R der Kurzfassung.
- **EXP-113** am Budgetende: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze.py` (Lesarten vorab im README). Zwischendurch Logs `lab/queue/logs/40_exp113_stage2b/` (Durchsatz, `arith share`, Textumlauf).

## Nächste Schritte (Regel 20)

1. Repro R4 vergleichen, in [[paper/repro/README]] und Anhang R (Kurzfassung, geprüft) eintragen.
2. EXP-113 beobachten (Durchsatz, Textumlauf) und am Budgetende nach Vorab-Lesarten auswerten; danach Stufe-2-Entscheidung (Anteil senken, 10 Seeds, oder „bricht“ dokumentieren).
3. Paper (Ziel Do 01.10.): Kurzfassung final lesen; Anhang K ist auf Stand S49 (geprüft).
4. Festlegungsuhr/lr-Fragen (EXP-110/111) ruhen; L0b niedrigere Priorität.

## Prioritäten

1. **Paper** (Regel 20d, Ziel Do 01.10.): L0 ist bestätigt → §6/Abstract fertigstellen, Textprüfung.
2. **N54b / L0b** (Minibatch-Uhr der Festlegung; Reihenfolge bei langen Epochen) — beide als saubere Registrierungen.
3. Mechanismus-Versuche (EXP-096–099) ruhen (Regel 20a).

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
- **Trainer eingefroren bis Ende L0** (Pilot, Switch, Bestätigung): `freq_ban.py` nicht ändern (R11 ist fertig; L0-Läufe vergleichen gegen denselben Trainer). Ressourcen: GPU-Prozesse zusammen ≤ 10, CPU-Threads zusammen ≤ 12 (jeder GPU-Prozess zählt 1).

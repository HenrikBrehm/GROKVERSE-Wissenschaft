---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 12:40 Berlin (Sitzung 50 läuft, Deadline 14:29) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (Nanda 20/20, nachgerechnet), K4–K4e, R2–R10, K5, **R11** (Festlegung auch add 97 / mul 113), **L0** (K2 unter i.i.d.-Minibatch B 256/64, 10 frische Seeds, eingefroren 26419818, nachgerechnet).
- **Explorationen Sitzung 46:** EXP-100-Pilot (Reihenfolge wirkt bei B 256/64 nicht; SGD nicht kalibrierbar; B 16 lernt bei wd 1 nicht), Wechselläufe (unter B 256 keine Festlegung bis 50 Schritte), **EXP-106** (B 16, wd 0.1: Menge steuert; Reihenfolge verschiebt nur auf Zufallssplits, kostet auf konstruierten ×1.6 Zeit; nachgerechnet), **EXP-107** (unter B 256 Fenster bei 100–200 Schritten, t½ ≈ 133 = 8.9 Epochen; nachgerechnet), **EXP-108** (Batch-Reihe: Festlegung skaliert ≈ √(N/B), α = 0.54 [0.52, 0.56]; nachgerechnet; ohne Full-Batch-Punkt α = 0.556 [0.513, 0.595]), EXP-103 (lr·wd-Uhr ab ≈ 250 Schritten, früh zählt lr), EXP-101 (RFM ohne K2-Lesart).
- **Paper:** Langfassung §3.16 (R10), §3.17 (R11); Kurzfassung §5 (R11), §6 mit L0-Pilot, Bestätigung, EXP-106/107, Grenzen angepasst. Abb. 4 aus echten Daten (Titel noch deutsch). §6 und Abstract nach unabhängiger Textprüfung korrigiert (19 Punkte, Sitzung 46); Abstract 1875 Zeichen.

- **Sitzung 47 (29.09., 03:29–06:29):** **N54b bestätigt** (Festlegung unter Minibatch ≈ √(N/B): α(1e-3) 0.583 [0.560, 0.606]; doppelte lr hilft bei kleinen Batches weniger: Δα +0.139 [0.098, 0.178]; eingefroren 624c2213, nachgerechnet) → Paper §6/§7, Langfassung §3.19, FINDINGS-Zeile. Explorationen: EXP-109 (lr 2e-3), EXP-110/111 (lr 4e-3 bei B 64: auf 2 Seeds später, auf 2 anderen etwas früher → nicht belastbar), Modellvergleich (Drift + ≈ 2 Epochen), Memorisierungsuhr (unklar), **EXP-102 Leiter Stufe 1** (Format hält; Verlust auf allen Positionen verzögert Grokking > ×10, Steuerung reduziert, wächst).

- **Sitzung 50 (ab 11:30):** Kurzfassung gekürzt (≈ 4 300 Wörter Haupttext, Anhang M mit den wörtlich verschobenen Passagen, zweimal unabhängig geprüft), neue Abb. 4 (`fig13`, nur L0 + N54b), Tabelle 1 ergänzt, Literatur-Nachsuche (Khanh 2026b). **EXP-114** (K = 19 Rechensätze, 1 Seed): „Verdünnung nicht gestützt“ – die Steuerung kommt im LM mit dem Faktenlernen (das gilt auch im Spielzeugmodell, gemessen an der Trainingsgenauigkeit: `toy_order_s50`; das LM beginnt nur viel später zu lernen); lernt das LM die Fakten, steuert die Auswahl deutlich (Δ_pow 5.6, zurückgehalten 0.98). → **Bestätigungsblock LM1** eingefroren (2b70d8b9, 10 frische Seeds 4000–4009, K = 19, 6000 Schritte, H1 Δ_pow > 1).

## Aktive Queue / laufende Jobs (Stand Sitzung 50, 12:40 Berlin)

- **GPU-Dienst (Regel 21)**, `lab/queue/status.json`: `31_lm1` (20 LM-Läufe, 4 Worker, ≈ 55 min je Lauf, bekommt Plätze vor R4), `34_repro_r4` (59/240 fertig), `40_exp113_stage2b` (Läufe 1–2 bei ≈ 12 000/16 000; die übrigen 6 erst nach R4 → EXP-113 insgesamt noch viele Stunden).
- **LM1 auswerten**, sobald 20/20 fertig: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/confirm_lm1.py --analyze` (Ausfallregel: Lauf ohne Ergebnis mit identischem Befehl neu einreihen; Code nach dem Einfrieren NICHT ändern). Danach unabhängige Nachrechnung, dann FINDINGS/Anhang K.
- **Repro-Paket:** L0, R5, R6, R8 fertig (S49). Offen: R4 → `python lab/tools/guarded_run.py -- python lab/paper/repro/r4.py --device cuda --compare-r4`, dann [[paper/repro/README]] und Anhang R.
- **EXP-113** am Budgetende: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze.py` und `analyze_folgt.py` (H-folgt, Nachtrag 1); danach `EXP-114…/analyze.py` (Vergleich bei gleicher Faktenzahl). Arm `answer` lernt die Fakten ab ≈ 10 000 Schritten.
- **`lm_stage2.py` nicht ändern**, solange EXP-113 oder LM1 laufen (Hash in Run-ID und LM1-Manifest).

## Nächste Schritte (Regel 20)

0. LM1 auswerten (s. o.), falls fertig.
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

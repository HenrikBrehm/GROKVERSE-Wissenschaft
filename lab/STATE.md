---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 19:05 Berlin (Sitzung 52, Deadline 19:49) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (Nanda 20/20, nachgerechnet), K4–K4e, R2–R10, K5, **R11** (Festlegung auch add 97 / mul 113), **L0** (K2 unter i.i.d.-Minibatch B 256/64, 10 frische Seeds, eingefroren 26419818, nachgerechnet).
- **Explorationen Sitzung 46:** EXP-100-Pilot (Reihenfolge wirkt bei B 256/64 nicht; SGD nicht kalibrierbar; B 16 lernt bei wd 1 nicht), Wechselläufe (unter B 256 keine Festlegung bis 50 Schritte), **EXP-106** (B 16, wd 0.1: Menge steuert; Reihenfolge verschiebt nur auf Zufallssplits, kostet auf konstruierten ×1.6 Zeit; nachgerechnet), **EXP-107** (unter B 256 Fenster bei 100–200 Schritten, t½ ≈ 133 = 8.9 Epochen; nachgerechnet), **EXP-108** (Batch-Reihe: Festlegung skaliert ≈ √(N/B), α = 0.54 [0.52, 0.56]; nachgerechnet; ohne Full-Batch-Punkt α = 0.556 [0.513, 0.595]), EXP-103 (lr·wd-Uhr ab ≈ 250 Schritten, früh zählt lr), EXP-101 (RFM ohne K2-Lesart).
- **Paper:** Langfassung §3.16 (R10), §3.17 (R11); Kurzfassung §5 (R11), §6 mit L0-Pilot, Bestätigung, EXP-106/107, Grenzen angepasst. Abb. 4 aus echten Daten (Titel noch deutsch). §6 und Abstract nach unabhängiger Textprüfung korrigiert (19 Punkte, Sitzung 46); Abstract 1875 Zeichen.

- **Sitzung 47 (29.09., 03:29–06:29):** **N54b bestätigt** (Festlegung unter Minibatch ≈ √(N/B): α(1e-3) 0.583 [0.560, 0.606]; doppelte lr hilft bei kleinen Batches weniger: Δα +0.139 [0.098, 0.178]; eingefroren 624c2213, nachgerechnet) → Paper §6/§7, Langfassung §3.19, FINDINGS-Zeile. Explorationen: EXP-109 (lr 2e-3), EXP-110/111 (lr 4e-3 bei B 64: auf 2 Seeds später, auf 2 anderen etwas früher → nicht belastbar), Modellvergleich (Drift + ≈ 2 Epochen), Memorisierungsuhr (unklar), **EXP-102 Leiter Stufe 1** (Format hält; Verlust auf allen Positionen verzögert Grokking > ×10, Steuerung reduziert, wächst).

- **Sitzung 50 (ab 11:30):** Kurzfassung gekürzt (≈ 4 300 Wörter Haupttext, Anhang M mit den wörtlich verschobenen Passagen, zweimal unabhängig geprüft), neue Abb. 4 (`fig13`, nur L0 + N54b), Tabelle 1 ergänzt, Literatur-Nachsuche (Khanh 2026b). **EXP-114** (K = 19 Rechensätze, 1 Seed): „Verdünnung nicht gestützt“ – die Steuerung kommt im LM mit dem Faktenlernen (das gilt auch im Spielzeugmodell, gemessen an der Trainingsgenauigkeit: `toy_order_s50`; das LM beginnt nur viel später zu lernen); lernt das LM die Fakten, steuert die Auswahl deutlich (Δ_pow 5.6, zurückgehalten 0.98). → **Bestätigungsblock LM1** eingefroren (2b70d8b9, 10 frische Seeds 4000–4009, K = 19, 6000 Schritte, H1 Δ_pow > 1).

- **Sitzung 51 (ab 14:10):** Kopplung Steuerung ↔ Lernbeginn hält über ×4 Lernrate (post hoc, „coupled“, trennt aber keine gemeinsame Uhr ab). Manuskript-Generator `lab/paper/build_manuscript.py` → [[paper/manuscript]] mit Zitatprüfung (3 fehlende Literatureinträge ergänzt); Kurzfassung auf 4 147 Wörter (dritter Kürzungsdurchgang, geprüft, Originale in Anhang M); Abb. K1 (`fig14_lm_onset.py`). **EXP-116** (K = 2, ≈ 8.7 % Rechen-Tokens) und **EXP-117** (ungekoppelte Embeddings, eigener Trainer `lm_untied.py`, Selbsttest grün) vorab festgelegt und eingereiht; [[paper/LM1_DEUTUNGEN]] vor jedem Ergebnis; unabhängige LM1-Nachrechnung vorbereitet (`lab/confirm/LM1_independent_recompute.py`). **Später in S51:** EXP-114-Vergleich „Verdünnung nicht gestützt“ (K 8 lernt nach ≈ 1.9× mehr Wiederholungen, Δ_pow 7.0); **EXP-118 „Ziele funktional“** (Ablation im LM: eigene Ziele weg → 0.03–0.30, fremde/Kontrollen → 0.93–0.99; Exploration); **LM1-F eingefroren** (bfdab8d8, gleiche Ablation an den 20 LM1-Modellen); **EXP-115 „unklar“** (flache Häufigkeiten: 4.35 / 0.96, Gipfel bei 2500, danach Rückgang).
- **Sitzung 52 (ab 16:50):** EXP-115 Nachtrag 1 (post hoc): Rückgang von Δ_pow bei flachen Splits = Verdünnung durch nachwachsende, meist nicht maskengetriebene Frequenzen; im Spielzeugmodell mit denselben Splits kein Rückgang (Anhang K ergänzt). Literaturliste: MISSING-Felder aus der arXiv-API gefüllt. **EXP-119** (R5 im LM: F/G gegen Zufallssplit R, Lernzeitpunkt, 2 Seeds) vorab festgelegt, als `36_exp119_lm_r5.jobs` eingereiht. Außerdem: im LM keine Grokking-Lücke (post hoc, 9 Läufe); **EXP-117 „Eingabe gesteuert“** (Δ_in 6.44 / 5.54, 2 Seeds; Anhang K); **Paper:** LaTeX-Export `lab/paper/build_tex.py` (ungetestet), Zitatprüfung inkl. Anhang (+9 Literatureinträge), simulierte Gutachter-Prüfung (6/10, Zahlen alle richtig) mit 10 übernommenen Textpunkten; offen für den Nutzer: Wortlaut der Festlegungsaussage, Nennung der GROKVERSE-Studie, Platz der KI-Offenlegung (paper/STATUS).

## Aktive Queue / laufende Jobs (Stand Sitzung 52, 19:06 Berlin)

- **GPU-Dienst (Regel 21)**, `lab/queue/status.json`: neuer Code mit Speicherschutz (höchstens 3 LM-Läufe à gpu_gb 3.5, strenge Namens-Priorität, unterbrochene Läufe zuerst; DRAIN-Neustart durch den Nutzer-Assistenten ab 14:29). Reihenfolge: EXP-113 #0/#1 (Checkpoint 13 000) → `31_lm1` (2/20 fertig um 14:45) → `32_exp115_flat` (1–2/4) → `33_exp117_untied` (4) → `34_repro_r4` (72/240; ruht mehrere Stunden, bewusst) → `40_exp113_stage2b` (6 übrige) → `41_exp116_lowshare` (4). **PROBLEME.md nicht selbst bearbeiten** (Absprache mit dem Nutzer-Assistenten): Probleme ins JOURNAL oder per Nachricht.
- **Dienst-Stand 19:06:** 31_lm1 13/20; 34_repro_r4 122/240; 40_exp113_stage2b 2/8; 41_exp116_lowshare 0/4; 36_exp119_lm_r5 0/6 (fertig/gesamt). Reihenfolge: 31_lm1 → 34_repro_r4 → 36_exp119_lm_r5 → 40_exp113 → 41_exp116. LM1: 7 Läufe offen bei 2 Workern (≈ 25 min je Lauf) → grob 20:30–21:00 fertig (Schätzung).
- **LM1 auswerten**, sobald 20/20 fertig: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/confirm_lm1.py --analyze` (Ausfallregel: Lauf ohne Ergebnis mit identischem Befehl neu einreihen; Code nach dem Einfrieren NICHT ändern). Danach unabhängige Nachrechnung, dann FINDINGS/Anhang K.
- **Repro-Paket:** L0, R5, R6, R8 fertig (S49). Offen: R4 → `python lab/tools/guarded_run.py -- python lab/paper/repro/r4.py --device cuda --compare-r4`, dann [[paper/repro/README]] und Anhang R.
- **EXP-113** am Budgetende: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze.py` und `analyze_folgt.py` (H-folgt, Nachtrag 1); danach `EXP-114…/analyze.py` (Vergleich bei gleicher Faktenzahl). Arm `answer` lernt die Fakten ab ≈ 10 000 Schritten.
- **`lm_stage2.py` nicht ändern**, solange EXP-113 oder LM1 laufen (Hash in Run-ID und LM1-Manifest).

## Nächste Schritte (Regel 20)

0. **Zuerst Dienst-Lage prüfen** (`lab/queue/status.json`, Log-Fortschritt, Perf-Zähler „GPU Adapter Memory … Shared Usage“). Stand 13:31: Stillstand durch Auslagerung; **14:00: Dienst neu gestartet, neue Kopfzeilen greifen (LM1 2, EXP-115 1, EXP-113 2 Worker), Speicher 13.2 GB + 0.8 GB geteilt.** Nach einem DRAIN-Neustart (Nutzer) laufen die abgebrochenen Läufe mit denselben Befehlen neu an und setzen an ihren Checkpoints fort (lm_stage2 speichert alle 1000 Schritte), mit den gesenkten Kopfzeilen. Ohne Neustart: LM1-Läufe enden an job_minutes 240 → identisch neu einreihen (neue Datei, workers=2).
0b. LM1 auswerten (s. o.), falls fertig; dann `python lab/confirm/LM1_independent_recompute.py` vergleichen; **danach LM1-F**: `python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/confirm/confirm_lm1f.py` (CPU ≈ 1–1.5 h → im Hintergrund oder als Dienst-Job mit gpu_gb=1; braucht `LM1_summary.json`). Deutung nach [[paper/LM1_DEUTUNGEN]]; Abb. K1 mit `fig14_lm_onset.py --root lab/confirm/lm1_raw --pairs …` erst nach der Auswertung. Dann ~~EXP-117~~ (erledigt S52), EXP-116 (`EXP-116…/analyze.py`), EXP-113 (alle 8 Läufe; `analyze.py`, `analyze_folgt.py`).
0c2. **LM1-F als Dienst-Job** (erst NACH `confirm_lm1.py --analyze`, weil es `LM1_summary.json` braucht; CPU ≈ 1–1.5 h): Datei `lab/queue/inbox/32_lm1f.jobs` mit den zwei Zeilen `#! workers=1 job_minutes=180 min_minutes=5 crash_minutes=0 gpu_gb=1` und `C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/confirm/confirm_lm1f.py` (vorher prüfen, dass kein gleicher Job läuft; Zeitschätzung aus Sitzung 51, nicht gemessen).
0d. **EXP-119** auswerten, sobald 6/6 fertig: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-119-lm-speed-r5/analyze.py` (Lesarten im README; bei „constructed faster“ Folgefrage Häufigkeitskontrolle).
0c. ~~EXP-118 Nachtrag 1~~ erledigt (S51 16:42): 3850 „funktional“, 3851 „unklar“; Kontrollen senken bei flachen Häufigkeiten mit (README EXP-118).
1. Repro R4 vergleichen, in [[paper/repro/README]] und Anhang R (Kurzfassung, geprüft) eintragen.
2. EXP-113 beobachten (Durchsatz, Textumlauf) und am Budgetende nach Vorab-Lesarten auswerten; danach Stufe-2-Entscheidung (Anteil senken, 10 Seeds, oder „bricht“ dokumentieren).
3. Paper (Ziel Do 01.10.): Kurzfassung final lesen; Anhang K ist auf Stand S49 (geprüft).
4. Festlegungsuhr/lr-Fragen (EXP-110/111) ruhen; L0b niedrigere Priorität.

## Prioritäten

1. **Paper** (Regel 20d, Ziel Do 01.10.): L0 ist bestätigt → §6/Abstract fertigstellen, Textprüfung.
2. **N54b / L0b** (Minibatch-Uhr der Festlegung; Reihenfolge bei langen Epochen) — beide als saubere Registrierungen.
3. Mechanismus-Versuche (EXP-096–099) ruhen (Regel 20a).

## Blocker / Hinweise

- **GPU-Speicher überbucht (Sitzung 50, ab ≈ 12:59):** 8 LM-Läufe + R4 → 19 GB dediziert + 12 GB ausgelagert, freier RAM 1.8 GB; LM-Läufe ≈ 2.4 s/Schritt statt 0.3. Kopfzeilen meiner Jobdateien gesenkt (LM1 2, EXP-115 1, EXP-113 2 Worker; höhere job_minutes), greifen erst nach DRAIN-Neustart des Dienstes (Nutzer/Assistent gebeten). LM1-Läufe, die an job_minutes 240 enden, nach der Ausfallregel identisch neu einreihen (Checkpoint). **Künftig LM-Läufe höchstens 2–3 gleichzeitig.** **Neue Jobdateien: `gpu_gb=` in die Kopfzeile** (lm_stage2 ≈ 3.3, kleine train.py-Läufe ≈ 1; ohne Angabe rechnet der Dienst mit 3.5 GB); der neue Dienstcode (Nutzer-Assistent, P-009 in [[PROBLEME]]) liest geänderte Kopfzeilen dann ohne Neustart und startet unterbrochene Läufe (EXP-113 bei 13 000) zuerst.
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

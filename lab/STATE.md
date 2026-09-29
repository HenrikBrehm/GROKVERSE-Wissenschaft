---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-09-29, 22:03 Berlin (Ende Sitzung 53) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] (eine Seite) · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ältere STATE-Fassungen: `git show b6430af4:lab/STATE.md` (Sitzung 45, mit den Nachtschritten 28./29.09. und Klarstellungen zu Ressourcen), `git show 7f9d56d4:lab/STATE.md`.*

## Lage

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion (Nanda 20/20, nachgerechnet), K4–K4e, R2–R10, K5, **R11** (Festlegung auch add 97 / mul 113), **L0** (K2 unter i.i.d.-Minibatch B 256/64, 10 frische Seeds, eingefroren 26419818, nachgerechnet).
- **Explorationen Sitzung 46:** EXP-100-Pilot (Reihenfolge wirkt bei B 256/64 nicht; SGD nicht kalibrierbar; B 16 lernt bei wd 1 nicht), Wechselläufe (unter B 256 keine Festlegung bis 50 Schritte), **EXP-106** (B 16, wd 0.1: Menge steuert; Reihenfolge verschiebt nur auf Zufallssplits, kostet auf konstruierten ×1.6 Zeit; nachgerechnet), **EXP-107** (unter B 256 Fenster bei 100–200 Schritten, t½ ≈ 133 = 8.9 Epochen; nachgerechnet), **EXP-108** (Batch-Reihe: Festlegung skaliert ≈ √(N/B), α = 0.54 [0.52, 0.56]; nachgerechnet; ohne Full-Batch-Punkt α = 0.556 [0.513, 0.595]), EXP-103 (lr·wd-Uhr ab ≈ 250 Schritten, früh zählt lr), EXP-101 (RFM ohne K2-Lesart).
- **Paper:** Langfassung §3.16 (R10), §3.17 (R11); Kurzfassung §5 (R11), §6 mit L0-Pilot, Bestätigung, EXP-106/107, Grenzen angepasst. Abb. 4 aus echten Daten (Titel noch deutsch). §6 und Abstract nach unabhängiger Textprüfung korrigiert (19 Punkte, Sitzung 46); Abstract 1875 Zeichen.

- **Sitzung 47 (29.09., 03:29–06:29):** **N54b bestätigt** (Festlegung unter Minibatch ≈ √(N/B): α(1e-3) 0.583 [0.560, 0.606]; doppelte lr hilft bei kleinen Batches weniger: Δα +0.139 [0.098, 0.178]; eingefroren 624c2213, nachgerechnet) → Paper §6/§7, Langfassung §3.19, FINDINGS-Zeile. Explorationen: EXP-109 (lr 2e-3), EXP-110/111 (lr 4e-3 bei B 64: auf 2 Seeds später, auf 2 anderen etwas früher → nicht belastbar), Modellvergleich (Drift + ≈ 2 Epochen), Memorisierungsuhr (unklar), **EXP-102 Leiter Stufe 1** (Format hält; Verlust auf allen Positionen verzögert Grokking > ×10, Steuerung reduziert, wächst).

- **Sitzung 50 (ab 11:30):** Kurzfassung gekürzt (≈ 4 300 Wörter Haupttext, Anhang M mit den wörtlich verschobenen Passagen, zweimal unabhängig geprüft), neue Abb. 4 (`fig13`, nur L0 + N54b), Tabelle 1 ergänzt, Literatur-Nachsuche (Khanh 2026b). **EXP-114** (K = 19 Rechensätze, 1 Seed): „Verdünnung nicht gestützt“ – die Steuerung kommt im LM mit dem Faktenlernen (das gilt auch im Spielzeugmodell, gemessen an der Trainingsgenauigkeit: `toy_order_s50`; das LM beginnt nur viel später zu lernen); lernt das LM die Fakten, steuert die Auswahl deutlich (Δ_pow 5.6, zurückgehalten 0.98). → **Bestätigungsblock LM1** eingefroren (2b70d8b9, 10 frische Seeds 4000–4009, K = 19, 6000 Schritte, H1 Δ_pow > 1).

- **Sitzung 51 (ab 14:10):** Kopplung Steuerung ↔ Lernbeginn hält über ×4 Lernrate (post hoc, „coupled“, trennt aber keine gemeinsame Uhr ab). Manuskript-Generator `lab/paper/build_manuscript.py` → [[paper/manuscript]] mit Zitatprüfung (3 fehlende Literatureinträge ergänzt); Kurzfassung auf 4 147 Wörter (dritter Kürzungsdurchgang, geprüft, Originale in Anhang M); Abb. K1 (`fig14_lm_onset.py`). **EXP-116** (K = 2, ≈ 8.7 % Rechen-Tokens) und **EXP-117** (ungekoppelte Embeddings, eigener Trainer `lm_untied.py`, Selbsttest grün) vorab festgelegt und eingereiht; [[paper/LM1_DEUTUNGEN]] vor jedem Ergebnis; unabhängige LM1-Nachrechnung vorbereitet (`lab/confirm/LM1_independent_recompute.py`). **Später in S51:** EXP-114-Vergleich „Verdünnung nicht gestützt“ (K 8 lernt nach ≈ 1.9× mehr Wiederholungen, Δ_pow 7.0); **EXP-118 „Ziele funktional“** (Ablation im LM: eigene Ziele weg → 0.03–0.30, fremde/Kontrollen → 0.93–0.99; Exploration); **LM1-F eingefroren** (bfdab8d8, gleiche Ablation an den 20 LM1-Modellen); **EXP-115 „unklar“** (flache Häufigkeiten: 4.35 / 0.96, Gipfel bei 2500, danach Rückgang).
- **Sitzung 52 (ab 16:50):** EXP-115 Nachtrag 1 (post hoc): Rückgang von Δ_pow bei flachen Splits ~~= Verdünnung~~ (**falsch, korrigiert S53**: Δ_pow ist ein Verhältnis; fremde Ziele wachsen schneller als eigene, nicht maskengetrieben); im Spielzeugmodell mit denselben Splits kein Rückgang (Anhang K ergänzt). Literaturliste: MISSING-Felder aus der arXiv-API gefüllt. **EXP-119** (R5 im LM: F/G gegen Zufallssplit R, Lernzeitpunkt, 2 Seeds) vorab festgelegt, als `36_exp119_lm_r5.jobs` eingereiht. Außerdem: im LM keine Grokking-Lücke (post hoc, 9 Läufe); **EXP-117 „Eingabe gesteuert“** (Δ_in 6.44 / 5.54, 2 Seeds; Anhang K); **Paper:** LaTeX-Export `lab/paper/build_tex.py` (ungetestet), Zitatprüfung inkl. Anhang (+9 Literatureinträge), simulierte Gutachter-Prüfung (6/10, Zahlen alle richtig) mit 10 übernommenen Textpunkten; offen für den Nutzer: Wortlaut der Festlegungsaussage, Nennung der GROKVERSE-Studie, Platz der KI-Offenlegung (paper/STATUS).

- **Sitzung 53 (ab 19:29):** **LM1 bestätigt** (Δ_pow 5.32 [4.86, 5.73], 10/10 > 1, p = 1/1024, Tor 20/20; unabhängig nachgerechnet, identisch) → Registrierung, FINDINGS, LAB, Paper Anhang J + §7 (ii) (Absatz unabhängig geprüft, Zählfehler beim Sekundärmaß korrigiert). **EXP-115-Deutung korrigiert** (nicht Verdünnung: Δ_pow ist ein Verhältnis; fremde Ziele wachsen schneller, nicht maskengetrieben). **Logikprüfungen** Anhang J (4) und Haupttext (9, 8 übernommen) + Gegenprüfung (3) eingearbeitet; Abstract 1918 Zeichen. BACKLOG-Kandidat LM2 (flache Splits im LM). Klassifikator-Störung 20:18–20:22 überstanden. **Repro R4 fertig:** Vorab-Tor verfehlt durch genau einen Lauf; 239/240 bitgleich; Ursache geklärt (der *eingefrorene* Lauf war ein einmaliger GPU-Ausreißer: 2 `train.py`-Wiederholungen + `freq_ban.py` am Einfrier-Commit sind untereinander bitgleich); Urteile unberührt.

## Aktive Queue / laufende Jobs (Stand Sitzung 53, 21:44 Berlin)

- **GPU-Dienst (Regel 21)**, `lab/queue/status.json`. Offen: `32_lm1f` (LM1-F, läuft seit 20:51, CPU; 8/20 Modelle um 21:44, ≈ 6.6 min je Modell gemessen → Ende ≈ 23:05, harte Grenze 23:51) → `36_exp119_lm_r5` (0/6) → `40_exp113_stage2b` (2/8) → `41_exp116_lowshare` (0/4). **PROBLEME.md nicht selbst bearbeiten**: Probleme ins JOURNAL.
- **`lm_stage2.py` nicht ändern**, solange EXP-113/116/119 laufen (Hash in Run-IDs).

## Nächste Schritte (Regel 20)

0. Dienst-Lage prüfen (status.json, Logs).
1. **LM1-F auswerten**, sobald `32_lm1f` fertig: Ergebnis steht im Job-Log `lab/queue/logs/32_lm1f/job_000.log` bzw. in der von `confirm_lm1f.py` geschriebenen Zusammenfassung (lab/confirm/); Deutung nach [[paper/LM1_DEUTUNGEN]] bzw. [[confirm/LM1F_REGISTRATION]]; unabhängig nachrechnen: NACH LM1-F (CPU-Konkurrenz) als Dienst-Job `lab/queue/inbox/33_lm1f_indep.jobs` mit `#! workers=1 job_minutes=240 min_minutes=5 crash_minutes=0 gpu_gb=1` und `C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/confirm/LM1F_independent_recompute.py --threads 4 --out lab/confirm/LM1F_independent_summary.json` (≈ 5–9 min je Modell, gemessen im Smoke; Seed 4000 stimmt bereits exakt); Deutungssätze vorab in LM1_DEUTUNGEN (Nachtrag S53); dann Anhang J (Satz „LM1-F is running“ ersetzen), FINDINGS, LAB. Optional Abb. K1 mit `fig14_lm_onset.py --root lab/confirm/lm1_raw --pairs …`.
2. **EXP-119** (6/6) → `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-119-lm-speed-r5/analyze.py`; **EXP-116** (4/4) → `EXP-116…/analyze.py`; **EXP-113** (8/8) → `analyze.py`, `analyze_folgt.py`, danach `EXP-114…/analyze.py`. Deutungssätze stehen vorab in LM1_DEUTUNGEN.
3. ~~Repro R4~~ erledigt (S53; README + Anhang-Tabelle). Optional: `lab/paper/repro/README.md` Tabelle Z. 121 (Stand S49) ist durch die Nachträge unten überholt.
4. **Paper (Ziel Do 01.10.):** Anhänge C/D logisch geprüft und korrigiert (S53, [[paper/logic_audit_S53_appC_D]], Diff geprüft); **als Nächstes Logikprüfung der Anhänge A, B, E–I** (je Anhang: Prüfagent → selbst nachprüfen → einarbeiten → Diff-Prüfung). Nutzerentscheidungen in [[paper/STATUS]] (Wortlaut „25–50 Schritte“ mit neuem Argument aus der Logikprüfung, GROKVERSE-Studie, KI-Offenlegung). Nach jeder Textänderung Zahlen- UND Logikprüfung getrennt.
5. LM2 (BACKLOG S53) erst nach LM1-F und EXP-116 entscheiden.

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

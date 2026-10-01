---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-10-01, 07:45 Berlin (Sitzung 67) (**Regel 20 Wochenplan gilt**; Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ausführliche ältere Fassung mit allen Sitzungsnotizen 46–63: `git show 546b8874:lab/STATE.md`; davor `b6430af4`, `7f9d56d4`.*

## Lage (Kurzform)

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion, K4–K4e, R2–R12, K5, L0 (Minibatch), N54b (Festlegung ≈ √(N/B)), LM1/LM1-F, LM3/LM3-F. **Neu S66: L0b teilweise bestätigt** (B = 16: Reihenfolge verschiebt O-Anteil auf Zufallssplits +0.063, H1; auf konstruierten +0.022, H2 *nicht* bestätigt → keine Aussage „Menge gewinnt“; Steuerung bleibt H3; Verzögerung ×1.5 H4; unabhängig nachgerechnet). Paper §6, Anhang J (Abb. J1), Grenzen, Abstract (1916 Zeichen), unabhängig geprüft und eingearbeitet; Manuskript neu gebaut. **EXP-136** (S66): K2 hält bei p 211/307 mit 30 % (Δ_pow 8.5–12.4); mit 3831 Paaren generalisiert kein Lauf (Pilot; S67 in Anhang A). **Neu S67: R13 bestätigt** – K2 (W_E-Spektrum) auch unter geclipptem SGDm (7.80 / 4.78, je 15/15); EXP-138: Paarstruktur trägt; Paper Grenze (i) + Anhang J, unabhängig nachgerechnet und geprüft.
- **Piloten LM (Anhang K):** EXP-129 (≈ 4.5 % Rechen-Tokens, K2 hält, S67), EXP-125 (29.5 M), EXP-134 (Text-Vortraining; Zahlzeilen-Wachstum = 96 % gemeinsame Verschiebung, S66), **EXP-135 „Festlegung mit dem Lernen“** (S66: Wechsel bei 250/1000 überschrieben, bei 3000 hält F).
- **Pythia-Linie geschlossen.** Paper laborseitig fertig; offen nur Nutzerentscheidungen ([[paper/STATUS]]).

## Beim GPU-Dienst (Regel 21, `lab/queue/status.json`)

1. `51_r14` (**R14**, eingefroren 68a0209c: K2 bei add 307 mit 10 % Daten nach der Generalisierung, Seeds 4430–4441, 24 Läufe; gestartet 07:44, Dienst nach Leerlauf-Ende per Start-ScheduledTask neu gestartet).

Fertig und ausgewertet in S67: EXP-128 („nicht auswertbar“), **R13 bestätigt** (a77dbebb), EXP-138 („Paarstruktur trägt“), EXP-129 („K2 hält im LM“ bei ≈ 4.5 %), EXP-137 („K2 hält bei p mit weniger Daten“, beide p). Vor dem Ablegen status.json prüfen; Jobdateien außerhalb von inbox schreiben, dann `mv`. Hinweis: Der Dienst beendet sich bei leerer Warteschlange; neue Dateien ggf. mit `powershell -NoProfile -Command "Start-ScheduledTask -TaskName GROKVERSE-GPU-Daemon"` sofort starten.

## Nächste Schritte

1. **R14 auswerten**, wenn 24/24: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r14.py --analyze lab/confirm/R14_manifest.json`; dann unabhängige Nachrechnung (eigener numpy-Code) und Paper nach [[paper/R14_DEUTUNGEN]] (Grenze (ii) + Anhang A.2), Textprüfung.
2. Paper ist sonst laborseitig aktuell (S67: Anhang A.2 EXP-136/137, Grenze (i) R13/EXP-138, Anhang J R13, Anhang K EXP-129, Abbildungsnummern). Offen nur Nutzerentscheidungen ([[paper/STATUS]]).
3. GPU-Folgearbeit (nur mit Begründung, Regel 15b): (a) shuf-Block unter SGD (BACKLOG 4) nur, falls das Paper es braucht; (b) Mindest-Paarzahl statt Anteil (EXP-137: 9425 Paare generalisieren, 4452 nicht) – Pilot bei p 211 mit ≈ 9425 Paaren (≈ 21 %)? schon durch f20/f15 abgedeckt; eher p 401 mit ≈ 9425 Paaren (5.9 %).
4. Tageserklärung ab 02.10.: [[paper/erklaerung/ERKLAERUNG_2026-10-02]] (R14, EXP-137, EXP-129).

## Nicht ändern (Hashes gebunden)

- `lab/experiments/EXP-001-freq-ban/freq_ban.py`, `lab/tools/confirm_l0b.py`, `lab/confirm/l0b_splits/` (L0b-Manifest).
- `lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py` (LM1/LM3-Manifeste; EXP-134/135 nutzen ihn nur über Wrapper), `confirm_lm3*.py`, `confirm_r12.py` + R12-Splits.
- `ft_pythia.py`, `ft_reset.py`; `lab/confirm/rank_tools.py` (Code-Tore C1–C4).
- Eingefrorene Blöcke: `--analyze` am Manifest-Commit reproduzieren (`git worktree add <dir> <commit>`); Smoke durch den eingefrorenen Lader vor jedem Block.

## Blocker / Hinweise

- **Codex ohne Guthaben** (seit S33): Prüfungen durch unabhängige Claude-Agenten (nur lesend).
- **P-021:** Pythia-Läufe hängen beim Beenden; Jobdateien mit HF-Modellen immer `stall_minutes=15`. Nicht selbst beenden (Regel 22: Hinweis in LIVE + Nachricht an den Assistenten).
- GPU: ≤ 10 Prozesse (HIP-Fehler bei 12–14), `gpu_gb` immer angeben (lm_stage2 3.5, d 512 6.0, freq_ban 0.75). LM-Läufe höchstens 2–3 gleichzeitig.
- GPU-Läufe sind nicht bitgleich wiederholbar (nichtdeterministische Kernel); Wiederaufnahme-Tests auf der CPU.
- `--analyze`/`analyze.py` brauchen `PYTHONIOENCODING=utf-8`; Auswertungen mit globalem Python über den Wächter, Trainer mit `.venv-gpu` (absoluter Pfad).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`, `runner-state.json`, `parallel_queue.py`, `lab/paper/outreach/`, Dienstdateien) **nicht committen**; immer einzelne Pfade.
- Notizen: CRLF/LF je Datei erkennen, kein `sed -i` auf Notizen. **Uhrzeiten nur gemessen** (Python zoneinfo) – in S61–S64 mehrfach geschätzt und korrigiert.
- Eine Runner-Sitzung endet mit der Antwort: Jobs im Vordergrund beobachten, nie „Wecker stellen und aufhören“.

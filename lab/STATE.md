---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]])

_Zuletzt aktualisiert: 2026-10-02, 00:31 Berlin (Sitzung 103, Lagekontrolle; zuvor S72 19:26; **Regel 23: Pause aktiv – LeDoux-Linie vollständig ausgewertet**) (Rechenfenster durchgehend bis 06.10. 00:00, dann bis 13:00)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[FINDINGS_DETAILS]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]] · [[paper/STATUS]] · [[reviews/ASTRA_2026-09-26|Astra-Review]]

*Ausführliche ältere Fassung mit allen Sitzungsnotizen 46–63: `git show 546b8874:lab/STATE.md`; davor `b6430af4`, `7f9d56d4`.*

## Lage (Kurzform)

- **Bestätigt ([[FINDINGS]]):** K2 (4 Aufgaben + MLP/4× Breite/Integer/2 Schichten), K2-Funktion, K4–K4e, R2–R12, K5, L0 (Minibatch), N54b (Festlegung ≈ √(N/B)), LM1/LM1-F, LM3/LM3-F. **Neu S71: R15 bestätigt** (an der Datengrenze 401/14 000 und 307/9425: konstruierte Mengen generalisieren 10/10, gleich große Zufallsmenge 0/10 in 30 000 Schritten, Holm-p 0.002, „ermöglicht“; nachgerechnet; Paper Anhang A.2 + §3-Satz + Grenze (ii)). **Neu S66: L0b teilweise bestätigt** (B = 16: Reihenfolge verschiebt O-Anteil auf Zufallssplits +0.063, H1; auf konstruierten +0.022, H2 *nicht* bestätigt → keine Aussage „Menge gewinnt“; Steuerung bleibt H3; Verzögerung ×1.5 H4; unabhängig nachgerechnet). Paper §6, Anhang J (Abb. J1), Grenzen, Abstract (1916 Zeichen), unabhängig geprüft und eingearbeitet; Manuskript neu gebaut. **EXP-136** (S66): K2 hält bei p 211/307 mit 30 % (Δ_pow 8.5–12.4); mit 3831 Paaren generalisiert kein Lauf (Pilot; S67 in Anhang A). **Neu S67: R14 bestätigt** (K2 bei add 307 mit 10 % Daten nach gen, über Placebo, 12/12; S68 unabhängig nachgerechnet, im Paper: Grenze (ii), Anhang A.2, Tabelle 1). **R13 bestätigt** – K2 (W_E-Spektrum) auch unter geclipptem SGDm (7.80 / 4.78, je 15/15); EXP-138: Paarstruktur trägt; Paper Grenze (i) + Anhang J, unabhängig nachgerechnet und geprüft.
- **Piloten LM (Anhang K):** EXP-129 (≈ 4.5 % Rechen-Tokens, K2 hält, S67), EXP-125 (29.5 M), EXP-134 (Text-Vortraining; Zahlzeilen-Wachstum = 96 % gemeinsame Verschiebung, S66), **EXP-135 „Festlegung mit dem Lernen“** (S66: Wechsel bei 250/1000 überschrieben, bei 3000 hält F).
- **Pythia-Linie geschlossen.** Paper laborseitig fertig; offen nur Nutzerentscheidungen ([[paper/STATUS]]).

## Beim GPU-Dienst (Regel 21, `lab/queue/status.json`)

**Stand S72 (19:26) – REGEL 23, PAUSE AKTIV:** EXP-144 (4/4) und der EXP-143-Nebenarm wd 1.0 (4/4) sind fertig und ausgewertet; der Dienst hat keine offenen Dateien der LeDoux-Linie mehr. Keine neuen Jobdateien, nichts aus `lab/queue/parked/` wieder einreihen. **Stand S71 (17:24) – REGEL 23 (Pause nach der LeDoux-Linie, Nutzer ≈ 17:15):** keine neuen Experimente/Jobdateien/Trainingsläufe. Dienst im DRAIN; danach laufen nur noch `52a7zzz_exp144_width` (EXP-144, 4 Läufe d 512, ≈ 1.8 h je Lauf) und die Reste von `52a8_exp143_ledoux` (wd-1.0-Nebenarm; F-iid fertig). EXP-139-Reste geparkt in `lab/queue/parked/` – **nicht wieder einreihen**. Ältere Angaben unten sind Historie.

Reihenfolge (14:10 gemessen): `52a6_exp141_alpha` (**EXP-141**, 11/12 fertig) → `52a7_r15_p401` (**R15** p 401, 30 Läufe, gpu_gb 4) → **`52a7z_exp143_wd01`** (**EXP-143 primär**, wd 0.1, 4 Läufe à 250 000 Schritte, gpu_gb 2.5, neu S70) → **`52a7zz_exp143_stride600k`** (2 Stride-Arme wd 0.1, 600 000 Schritte, raw_long; Q2/Q3 werden hier gelesen) → `52a8_exp143_ledoux` (Nebenarm wd 1.0) → `52b_exp139_p503` → `52c_exp139_p613`. Fertig: 52a, 52a5, 52a55 (EXP-140), **52a56 (R15 p 307, 30/30)**, **52a57 (EXP-142)**. Statuseinträge `52bz_…`/`52bzz_…` = Geister umbenannter Dateien (P-023; laufen am Ende leer). **Keine Jobdateien bei laufendem Dienst umbenennen** (Reihenfolge nur über neue Präfixe).

**R15** ([[confirm/R15_REGISTRATION]], eingefroren a8033017; Smoke grün): konstruierte (F/G) gegen gleich große Zufallsmenge (R) an der Datengrenze, 401/14 000 (H1) und 307/9425 (H2), Seeds 4500–4509. Auswertung nach 60/60: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_r15.py --analyze lab/confirm/R15_manifest.json`; dann unabhängig nachrechnen, Wortwahl „konstruiert (ε 2, frequenzgezielt) gegen gleichverteilt“.

**EXP-141 ausgewertet (S70, nachgerechnet):** 503/16 100 und 18 100 generalisieren (12/12) → passt zu α ≈ 1 (Grenze N/p ≈ 28–31), nicht p^(5/3); K2 hält; Iso-Zeit-Exponent 1.30 (95 %-KI 1.09–1.58). **EXP-143 Vorbefund (S70, CPU, 1 Seed, nachgerechnet):** bei p 9973/0.30 %/B 256/wd 0.1 prägt die F-Menge W_E nach ≈ 2 Epochen auf ihre Ziele (Placebo p < 1e-4), Stride hebt nur k = 101 (LeDoux' F) auf Rang 1; Wiederholung mit Seeds 14301/14302 läuft auf der CPU (`raw_cpu_early`, Nachtrag f; Auswertung `analyze.py --root lab/experiments/EXP-143-ledoux-regime/raw_cpu_early --traj`). Literatur S70: Gromov 2023 §5.2 vermutet schon, dass die Stichprobenwahl die kritische Datenmenge senkt → bei R15 im Paper zitieren ([[paper/R15_DEUTUNGEN]]).

**S69-Befunde:** EXP-140 „Konstruktion ermöglicht Generalisierung“ (401/14 000: R 0/3 in 30 000, E ≈ 5 500; Pilot). EXP-142 „Frequenzstruktur nötig“ (permutierte F-Gewichte U 0/3; Pilot). Post hoc EXP-139: W_E ist auch in nie generalisierenden Zellen gesteuert (Δ_pow 2.0–3.6 ≫ Placebo-q99 0.3–0.4, 6/6; `posthoc_nolearn_s69.json`). Iso-Zeit-Paarzahlen wachsen ≈ p^1.2 (oder p ln p, nicht trennbar; beschreibend). Beides unabhängig nachgerechnet; Prägung schon bei Schritt 50–250 (frühe Gradienten-Einprägung, nicht „Memorisierung“).

**EXP-143 läuft seit 15:48 beim Dienst (S71):** wd-0.1-Arme ≈ 100 Schritte/s je Lauf (250 000 Schritte ≈ 45–60 min); bei Start Train ≈ 0.2, Test ≈ 0. **Nachtrag f ausgewertet (S71, nachgerechnet):** frühe Prägung durch Menge 3/3 Seeds, Stride k = 101 3/3; Oberwellen „unklar“ (schwach). Seeds 14300–14302 gesehen. **EXP-143 läuft seit 15:48 beim Dienst (S71):** wd-0.1-Arme ≈ 100 Schritte/s je Lauf (250 000 Schritte ≈ 45–60 min); bei Start Train ≈ 0.2, Test ≈ 0. **Nachtrag f ausgewertet (S71, nachgerechnet):** frühe Prägung durch Menge 3/3 Seeds, Stride k = 101 3/3; Oberwellen „unklar“ (schwach). Seeds 14300–14302 gesehen. **EXP-143** ([[experiments/EXP-143-ledoux-regime/README|README]], neu S70, Pilot): LeDoux-Regime p = 9973, 300 000 Paare, Batch 256; Arme R/F × iid/stride, Seed 14300; Lesarten Q1–Q3 vorab, gelten für den wd-0.1-Satz (Nachtrag c: wd 1.0 lernt bei kleinem B/N in L0 nicht); Nachtrag d (unabhängige Prüfung): Stride-Familie |99k mod p| ≤ 26, Q3 nur bei generalisiertem Arm, Q2/Q3 an den 600k-Armen. Erst nach R15 (Dienst). Läuft über den neuen Wrapper `lab/tools/freq_ban_large.py` (gestückelte Auswertung, Trainer unverändert; Gleichwertigkeit bei p 113 bitgleich geprüft). Auswertung: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/analyze.py [--traj]` (gen, Top-5, Ziel- und Stride-Leistung 101 ± 1 / 1914 ± 1, getrennt nach wd).

## Nächste Schritte (Regel 23 – Pause aktiv)

1. **Pause aktiv.** Die LeDoux-Linie ist abgeschlossen: EXP-143 (primär + Nebenarm wd 1.0) und EXP-144 (d 512) ausgewertet und nachgerechnet. Ergebnis: Kein Arm generalisiert in irgendeiner Einstellung; die Frage „Menge gegen Reihenfolge“ im LeDoux-Regime bleibt offen (Grenze (ii) im Paper unverändert). EXP-144: i.i.d. lernt mit d 512 auswendig (Train Spitze 0.91), Stride nicht (≈ 0.26); in den Stride-Armen dominieren 303 > 202 > 101.
2. Jede weitere Sitzung: kurze Lagekontrolle (STOP, Dienst, LIVE), dann mit „Pause aktiv (Regel 23)“ in LIVE beenden, bis der Nutzer die Pause aufhebt. Keine neuen Experimente, Jobdateien oder Trainingsläufe; keine neuen Ergebnisse ins Paper.
3. Erlaubt: Leitfragen/Leseliste für den Nutzer ([[paper/erklaerung/LEITFRAGEN_LEDOUX]]), Tageserklärung.

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

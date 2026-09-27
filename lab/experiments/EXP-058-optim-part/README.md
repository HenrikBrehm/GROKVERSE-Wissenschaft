---
id: EXP-058
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-057-optim-reset/README|EXP-057]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-058: Trägt das Adam-Momentum die Persistenz, oder überschreibt ein voller Reset nur die Spur? (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (größte offene Frage aus P3) · Vorgänger [[experiments/EXP-057-optim-reset/README|EXP-057]] · [[NOVEL_DIRECTIONS]] N28.
Festgelegt 2026-09-27 06:36 Berlin (Sitzung 21), **vor jedem EXP-058-Lauf** (nur Smokes an Seed 400 mit 60 Schritten). **Pilot**, bekannte Seeds 400–409.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-056/057 an diesen Seeds (π_normal 0.30, voller Reset 0.11), Codex-Einwand (voller Reset = Zustand weg **und**
vorzeichenartige Schritte). Smokes (Seed 400, 60 Schritte, 06:34): mittlere Update-Norm der Schritte 31–36 normal 0.27–0.34, voller Reset 0.48–0.38, nur m 0.18–0.36, m + v 0.25–0.41.

| | |
|---|---|
| **Frage** | Sinkt die Persistenz auch, wenn nur das Momentum m gelöscht wird (v und Schrittzähler bleiben, die ersten Schritte werden **kleiner** statt größer)? |
| **Arme** (je A→B und B→A, t = 25, danach 2000) | normal · ro (voller Reset, Wiederholung von EXP-057) · rom (nur exp_avg = 0) · romoments (exp_avg und exp_avg_sq = 0, Schrittzähler bleibt); alle mit `--log-update-norms 10` |
| **Seeds / Splits** | 400–409, ω = 0 (EXP-056); reine Läufe aus EXP-056 wiederverwendet; 80 neue Läufe, GPU |
| **Maß** | π wie EXP-056; frühe Update-Norm = Mittel der Gesamt-Update-Norm der Schritte 26–30 |
| **Primär** | Δ_m = π_normal − π_rom, einseitiger t-Test |
| **Urteil** | < 8 gültig → *nicht auswertbar* · Δ̄_m > 0, p < 0.05 → ***Momentum (m) trägt einen Teil der Persistenz*** (Überschreiben scheidet dort aus, weil die frühen Schritte kleiner sind) · 90-%-KI in [−0.1, 0.1] → ***m trägt die Persistenz nicht*** (dann erklärt eher v, der Neustart der Bias-Korrektur oder das Überschreiben den Abfall in EXP-057) · sonst ***unklar*** |
| **Sekundär** | π je Arm; frühe Update-Normen je Arm (Prüfung, ob rom wirklich kleinere, ro größere Schritte macht); Wiederholung von EXP-057 (π_ro) |
| **Grenzen** | Pilot, bekannte Seeds; nur t = 25; „nur m“ lässt v stehen, v trägt aber auch Information aus A (Skala je Koordinate) |
| **Budget** | 80 Läufe à 2025 Schritte, GPU 8 parallel ≈ 8–10 min |

Trainer-Option: `freq_ban.py --reset-optim-part m|moments`, `--log-update-norms N` (041f7a8; 17/17 Tests, GPU-Smokes; Codex-Prüfung siehe [[JOURNAL]]).

```
python lab/tools/parallel_queue.py lab/experiments/EXP-058-optim-part/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-058-optim-part/analyze.py
```

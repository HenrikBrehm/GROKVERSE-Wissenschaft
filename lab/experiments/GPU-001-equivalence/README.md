---
id: GPU-001
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, werkzeug]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[FINDINGS]]"]
---
# GPU-001: Gleichwertigkeit CPU/GPU, Regressionstest und Durchsatz (Regel 16)

Technische Prüfung, kein Forschungsversuch. Zweck: Die AMD RX 7900 XT (ROCm, `.venv-gpu`, torch 2.9.1+rocm7.2.1) soll für neue
Versuche benutzt werden, v. a. für die Verallgemeinerung [[experiments/EXP-043-generalize-steering/README|EXP-043]]
([[FINDINGS]], größte offene Frage). **Status: vorbereitet, ungetestet** (Sitzung 11, außerhalb des Fensters geschrieben).

## Änderung an `freq_ban.py` (Sitzung 11)

`--device` (Standard `cpu`): Das Modell wird wie bisher auf der CPU initialisiert (identische Gewichte) und danach mit
Trainings- und Testdaten, Projektoren und Hilfstensoren auf das Gerät gelegt; alle Rückwege nach numpy über `.cpu()`.
GPU-Läufe bekommen das Suffix `_devcuda` in der Run-ID (nie mit CPU-Läufen verwechselbar). `result.json` enthält `device`,
`device_name` und bei GPU `cuda_max_mem_mb`. Außerdem `--p` und `--task` für EXP-043 (Standard 113/add = unverändert).
Die Warteschleifen in `queue_s10.sh`, `queue_s5.sh`, EXP-041 und EXP-042 ignorieren jetzt `guarded_run`-Prozesse mit
`--device cuda` (sonst hätten GPU-Läufe die CPU-Queue blockiert; Regel 16c).

## Akzeptanzkriterien (vorab festgelegt, 2026-09-26 ~19:45 Berlin, vor jedem GPU-Lauf)

1. **Regression (CPU):** Der geänderte `freq_ban.py` reproduziert den gespeicherten 50-Schritte-Smoke von EXP-016 (Seed 10)
   **exakt** (alle Dense-Kurven Differenz 0, gleiche Top-5). *Scheitert das:* `queue_s10.sh` **nicht** mit dem geänderten Code
   starten, sondern `git checkout a91ef0d -- lab/experiments/EXP-001-freq-ban/freq_ban.py` und Fehler suchen.
2. **Gleichwertigkeit:** GPU-Wiederholung der gespeicherten CPU-Läufe EXP-016 Seeds 10, 11, 12 (Arm F, 2000 Schritte).
   - A1: Top-5 der W_E-Frequenzen bei Schritt 2000 überlappen in jedem Seed ≥ 4/5.
   - A2: bei den Schritten 250, 500, 1000 Überlappung ≥ 4/5 in ≥ 8 von 9 Vergleichen.
   - A3: gleicher Generalisierungsausgang, Schritt innerhalb max(100, 15 %) des CPU-Werts.
   Bitgleichheit wird nicht erwartet (andere torch-Version 2.9.1 gegen 2.13, andere Rechenreihenfolge). Berichtet werden
   zusätzlich relative Verlustabweichungen bei Schritt 1/10/50 und der erste Schritt mit > 1 % Abweichung.
   *Scheitert eines von A1–A3:* GPU für Urteile nicht verwenden, Blocker in [[STATE]]; höchstens drei Reparaturversuche (Regel 16e).
3. **Durchsatz:** J = 1, 2, 4, 8 parallele GPU-Prozesse à 500 Schritte; s/Schritt je Prozess, Gesamtdurchsatz, Speicher.
   Gewählt wird das J mit dem höchsten Gesamtdurchsatz (bei Gleichstand das kleinere).

## Befehle

```
sh lab/experiments/GPU-001-equivalence/queue.sh          # alles; stoppt bei Fehlschlag von 1 oder 2
python lab/experiments/GPU-001-equivalence/compare.py regression|equivalence|throughput   # nur lesend
```

Laufzeit (geschätzt, ungeprüft): Regression ≈ 10 s; Gleichwertigkeit 3 × 2000 Schritte auf der GPU (unbekannt; CPU wären
3 × 4.5 min); Durchsatz 15 Prozesse × 500 Schritte.

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

## Akzeptanzkriterien (vorab festgelegt, 2026-09-26 19:16 Berlin, vor jedem GPU-Lauf)

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

## Nachtrag Sitzung 12 (2026-09-26 ~19:55 Berlin, nach Codex, **vor jedem Lauf**)

Codex-Prüfung `EXP-043-generalize-steering/codex_review_s12_2026-09-26.txt` (2 Blocker, 1 hoch, 2 mittel, 3 niedrig), übernommen:
Queues scheitern nicht mehr „offen“ (Ablehnung des Wächters rc 3 in parallelen Läufen stoppt alles, andere Fehler werden gezählt,
die Queue endet dann mit rc 1 „done WITH FAILURES“); GPU-001-Durchsatz zählt eine Stufe J nur, wenn alle J Läufe fertig sind, die
Hauptqueue verlangt Regression, Gleichwertigkeit und Durchsatz bestanden; `freq_ban.py --force` löscht den alten `result.json`;
Auswertungen werten fehlende/abgebrochene Läufe als ungültig statt abzustürzen; EXP-044 prüft den Test-Hash und rechnet Holm
über **alle gelaufenen** Aufgaben (wie hier vorab festgelegt, der Code wich ab). Diagnose-Schrittnummern in GPU-001 korrigiert.
Nicht geändert: `config.device` bleibt „cpu“ (maßgeblich ist das Feld `device` oben im result.json; alle Auswertungen nutzen es);
Seed 70/99 wurden früher schon benutzt, aber bei anderem p bzw. anderer Architektur, also andere Init (Einschränkung notiert).
Urteilsregeln unverändert.

## Nachtrag (Sitzung 13, 2026-09-26 20:25 Berlin, gemessen; vor jedem Lauf): Ablehnungen im Durchsatztest

Unabhängige Prüfung (Claude-Subagent, nur lesend; Codex ohne Guthaben) der Änderungen aus 2b19820: **kein Blocker**; Regression, Kriterien A1–A3, Format von `verdict_throughput.json` und die Übergabe an `queue_gpu_s11.sh` passen. **Hoch, behoben:** Durchsatzläufe liefen im Hintergrund, eine Ablehnung des Wächters ging im `wait` unter; alte `raw_par`-Ergebnisse konnten sich mit neuen mischen, und ein Verdikt mit fehlenden Stufen hätte J dauerhaft gedeckelt. Jetzt: `raw_par` wird vor dem Test gelöscht; rc 3 oder 124 eines Durchsatzlaufs → Ende mit rc 3 **ohne** Verdikt (nächster Start wiederholt den Test). Im Master zählt rc 124 von GPU-001 als Ablehnung. Logik an Stub-Befehlen geprüft (kein Training). *Nicht geändert:* Auswertungs-Ablehnungen am Queue-Ende zählen als Fehler (rc 1) – harmlos, weil die Wiederaufnahme ohnehin dieselbe Queue neu startet und Fertiges überspringt. *Offen (niedrig):* Ob torch 2.9.1 (GPU-venv) dieselbe CPU-Init erzeugt wie torch 2.13, prüft GPU-001 nicht direkt; A1–A3 würden eine Abweichung schlucken. Diagnose-Indizes 1/10/50 sind Schritte 10/100/500.

## Nachtrag (Sitzung 13, 20:53 Berlin, vor jedem Lauf): Astra-Review Punkt 10

Kriterien unverändert. (1) Durchsatz = J·500 Schritte / Wandzeit der ganzen Stufe (inkl. Prozess- und ROCm-Start), J nur bei vollständiger Stufe. (2) Jedes Verdikt trägt ein **Siegel** (SHA-256 über `freq_ban.py`, `compare.py`, `torch/version.py` der GPU-venv); ändert sich eines davon, gilt GPU-001 als nicht bestanden und läuft neu. (3) **Diagnose, kein Kriterium:** Seed 10 zusätzlich auf der CPU mit der Torch-Version der GPU-venv (2.9.1) → `version_diagnostic` trennt Versions- von Geräteeffekten (gleiche Init? Top-5-Überlappung bei 2000? gen-Schritt?). Ausführung jetzt über `lab/tools/night_program.py` (die `queue.sh` hier ist Historie).

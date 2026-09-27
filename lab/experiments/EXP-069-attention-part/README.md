---
id: EXP-069
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-067-exclusion-part/README|EXP-067]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-069: Muster oder Werte? Welcher Teil der Attention hält die frühe Frequenzwahl fest (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B) · [[NOVEL_DIRECTIONS]] N32 · Vorgänger [[experiments/EXP-067-exclusion-part/README|EXP-067]] (Attention-Reset bei t = 50 hebt den Ausschluss auf, 10/10).
Festgelegt 2026-09-27 (Sitzung 23), **vor jedem EXP-069-Lauf** und vor dem N29b-Ergebnis. **Pilot**, bekannte Seeds 400–409. Braucht `--reset-at-switch qk|vo` (Trainer-Erweiterung erst nach dem N29b-Block).

**Bereits gesehene Daten:** EXP-059/062/063/064/067 an diesen Seeds (normal b = 4.25; rsattn b = 0.10, Funktion neu).

| | |
|---|---|
| **Frage** | Hebt der Reset nur des Aufmerksamkeitsmusters (W_Q, W_K) oder nur des Wertepfads (W_V, W_O) beim Wechsel bei t = 50 den Ausschluss auf? |
| **Konkurrenzmodelle** | Q: Das Muster (welche Position wie stark gelesen wird) ist auf die alten Frequenzen eingestellt → rsqk senkt b stark. V: Der Wertepfad trägt die alten Frequenzen an das MLP weiter und filtert neue Richtungen → rsvo senkt b stark. Beide: nur der ganze Block wirkt (keins allein). |
| **Arme** (A→B und B→A, Wechsel bei 50, danach 2000 Schritte, `--save-model`) | rsqk, rsvo; Vergleich normal (EXP-059), rsattn (EXP-067). 40 Läufe, GPU. |
| **Maß** | wie EXP-067: a, b (Endspektren gegen reine Läufe), Funktion wie EXP-064 beschreibend |
| **Primär** | Δb_X = b50(normal) − b50(rsX) je Seed |
| **Urteil je Teil** | wie EXP-067: Δb > 1 in ≥ 8/10 → ***trägt den Ausschluss mit*** · Δb < 0.5 in ≥ 8/10 → ***allein nicht nötig*** · sonst ***unklar*** |
| **Was die Frage offen ließe** | Beide Teile „tragen mit“ (redundant) oder keiner (nur zusammen) |
| **Grenzen** | Pilot, bekannte Seeds, ein Zeitpunkt, Reset auf Init; W_Q/W_K bzw. W_V/W_O haben je gleich viele Parameter (32 768), also größengleich |
| **Budget** | 40 Läufe à 2050 Schritte, 6 GPU-Arbeiter, ≈ 5–8 min |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-069-attention-part/jobs.txt --workers 6
python lab/tools/guarded_run.py -- python lab/experiments/EXP-069-attention-part/analyze.py
```

## Ergebnis (Sitzung 23, Läufe 11:35–11:40 (Log), Auswertung 11:40 Berlin; `summary.json`)

Trainer-Option `qk|vo` seit 1c6e480 (18/18 Tests; **ohne Codex-Prüfung**, kein Guthaben). 40/40 Läufe ok, 10/10 Seeds gültig.

| Arm (Wechsel bei 50) | a | **b** | Urteil Δb | Genauigkeit ohne alte / ohne neue |
|---|---|---|---|---|
| normal | 3.66 | 4.25 | – | (EXP-064: 0.02 / 0.96) |
| rsattn (EXP-067) | 1.50 | 0.10 | trägt mit | 0.74 / 0.08 |
| **rsqk** (W_Q, W_K) | 3.58 | 3.17 | ***unklar*** (Δb −0.6 … 2.8) | 0.05 / 0.81 |
| **rsvo** (W_V, W_O) | 3.08 | **0.49** | ***trägt den Ausschluss mit*** (Δb 1.5 … 4.7, 10/10) | **0.14 / 0.17** |

- **Lesart (Pilot):** Den Ausschluss neuer Frequenzen trägt vor allem der **Wertepfad** der Attention: Setzt man W_V und W_O zurück, werden die neuen Frequenzen gelernt (b 0.49). Funktional stützt sich das Netz
  danach aber auf **beide** Mengen (Entfernen der alten oder der neuen kostet fast alles). Erst der Reset der ganzen Attention führt zum vollständigen Umstieg. Das Muster (W_Q, W_K) allein ist nicht nötig.
- **Deutung (Spekulation):** W_V/W_O bilden die W_E-Richtungen auf den Residualstrom ab, den das MLP liest. Sind sie nach 50 Schritten auf die alten Frequenzen ausgerichtet, erhalten neue W_E-Richtungen
  kaum Gradient. Das Muster (Attention-Gewichte) scheint dagegen die Wahl allein nicht festzuhalten.
- **Grenzen:** Pilot, bekannte Seeds, 2000 Schritte, Reset auf Init; ohne Codex-Prüfung der Trainer-Erweiterung.
- **Nächster Schritt:** Bestätigung an frischen Seeds (rsvo gegen rsqk und normal, Funktionsmaß wie N29b); Messung, wie stark W_V/W_O bei t = 25 gegen 50 auf die alten Frequenzen ausgerichtet sind.

---
id: EXP-067
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-063-exclusion-locus/README|EXP-063]]", "[[experiments/EXP-064-functional-regimes/README|EXP-064]]", "[[confirm/N29_REGISTRATION|N29]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-067: Welcher Teil des „Rests“ trägt den Ausschluss neuer Frequenzen bei t = 50? (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B) · [[BACKLOG]] „N29-Ursache“ · Vorgänger [[experiments/EXP-063-exclusion-locus/README|EXP-063]] (Rest-Reset senkt b50 von 4.25 auf 1.05, 10/10).
Festgelegt 2026-09-27 (Sitzung 23), **vor jedem EXP-067-Lauf**. **Pilot**, bekannte Seeds 400–409. Braucht eine Trainer-Erweiterung (unten), die erst nach den laufenden Blöcken N29/P2e
eingespielt wird (`freq_ban.py` steht in deren Code-Hash).

**Bereits gesehene Daten:** EXP-059/062/063/064 an diesen Seeds (normal@50: b = 4.25; rsrest: b = 1.05; rswe: b = 0.44; Funktion: bei t = 50 wird mit den alten Frequenzen gerechnet).

| | |
|---|---|
| **Frage** | Hebt das Zurücksetzen nur der Attention (W_Q, W_K, W_V, W_O), nur des MLP (W_in, W_out) oder nur der Unembedding-Matrix W_U beim Wechsel bei t = 50 den Ausschluss auf? |
| **Konkurrenzmodelle** | U: W_U „liest“ schon die alten Frequenzen, neue Richtungen in W_E bekommen keinen Gradienten → rsunembed senkt b stark. M: die MLP-Merkmale sind auf die alten Frequenzen eingestellt → rsmlp senkt b. A: Die Attention mischt nur die Positionen (bei dieser Aufgabe fast fest) → rsattn senkt b kaum. |
| **Arme** (A→B und B→A, Wechsel bei 50, danach 2000 Schritte, `--save-model`) | rsattn, rsmlp, rsunembed (neue Werte von `--reset-at-switch`: Parameter auf ihre Init, ihr AdamW-Zustand gelöscht; wie EXP-038). Vergleich: normal, rsrest aus EXP-059/063. 60 Läufe, GPU. |
| **Maß** | a, b wie EXP-062/063 (Endspektren gegen die reinen Läufe aus EXP-056), je Seed Mittel beider Richtungen. Beschreibend zusätzlich die Funktion wie EXP-064 (Genauigkeit nach Entfernen der alten/neuen Ziele). |
| **Primär** | Δb_X = b50(normal) − b50(rsX) je Seed und Teil X |
| **Urteil je Teil** | Δb_X > 1 in ≥ 8/10 → ***trägt den Ausschluss mit*** · Δb_X < 0.5 in ≥ 8/10 → ***allein nicht nötig*** · sonst ***unklar***. (Schwellen wie EXP-063.) |
| **Was gegen „ein Teil trägt ihn“ spräche** | Kein Einzel-Reset erreicht Δb > 1, obwohl rsrest es tut: Der Ausschluss wäre verteilt (Koadaptation mehrerer Teile). |
| **Grenzen** | Pilot, bekannte Seeds; ein Reset auf die Init entfernt alles Gelernte des Teils, nicht nur die Ausrichtung (Codex zu EXP-063): Das ist Reset-Empfindlichkeit, kein Mechanismusnachweis. |
| **Budget** | 60 Läufe à 2050 Schritte, GPU, ≈ 10–15 min bei 6 Arbeitern |

**Trainer-Erweiterung (vor dem Lauf, Codex-Prüfung nach Regel 18c):** `--reset-at-switch` bekommt zusätzlich `attn`, `mlp`, `unembed`. Auswahl über die Parameternamen
(`named_parameters`), sonst unverändert (Init-Kopie, AdamW-Zustand löschen, Prüfung `check`). Für `we` und `rest` bleibt das Verhalten bitgleich; Selbsttest: je ein Lauf `rest` gegen EXP-063 (gleiche Endgewichte).

```
python lab/tools/parallel_queue.py lab/experiments/EXP-067-exclusion-part/jobs.txt --workers 6
python lab/tools/guarded_run.py -- python lab/experiments/EXP-067-exclusion-part/analyze.py
```

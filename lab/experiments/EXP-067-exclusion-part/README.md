---
id: EXP-067
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
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

## Durchführung (Sitzung 23)

Trainer-Option eingespielt (5d84666, 18/18 Tests, Codex: keine Fehler). Gleichwertigkeit `rest` alt gegen neu (60 Schritte, CPU, Seed 400): W_E-Schnappschüsse und Reset-Ereignis **bitgleich**.
Läufe ab 10:52 Berlin (gemessen), 6 GPU-Arbeiter. (Der Selbsttest lief als Vergleich alter gegen neuer Code statt gegen EXP-063, das auf der GPU lief.)

## Ergebnis (Sitzung 23, Läufe 10:52–10:57 (Log), Auswertung 10:57–10:58 Berlin; `summary.json`)

60/60 Läufe ok, 10/10 Seeds gültig, Reset je Lauf mit `check` vermerkt.

| Arm (Wechsel bei 50) | zurückgesetzte Parameter | a (alt erhalten) | **b (neu fehlt)** | Urteil Δb | Genauigkeit ohne alte / ohne neue Ziele |
|---|---|---|---|---|---|
| normal (EXP-059) | – | 3.66 | 4.25 | – | (EXP-064: 0.02 / 0.96) |
| rsrest (EXP-063) | alles außer W_E | 3.10 | 1.05 | trägt mit (10/10) | – |
| **rsattn** | 65 536 (W_Q, W_K, W_V, W_O) | 1.50 | **0.10** | ***trägt den Ausschluss mit*** (Δb 1.9–5.2, 10/10) | **0.74 / 0.08** |
| rsmlp | 131 072 (W_in, W_out) | 3.75 | 3.14 | ***unklar*** (Δb −0.4–2.2) | 0.03 / 0.90 |
| rsunembed | 14 592 (W_U) | 3.75 | 4.50 | ***allein nicht nötig*** (9/10 < 0.5) | 0.02 / 0.98 |

- **Lesart (Pilot, bekannte Seeds):** Gegen meine Vorab-Erwartung (Modell A: Attention unwichtig) hebt **allein das Zurücksetzen der Attention** den Ausschluss vollständig auf, stärker als der Reset
  des ganzen Rests. Das Netz lernt die neuen Frequenzen und rechnet danach mit ihnen (Umstieg wie bei t = 25). MLP-Reset (doppelt so viele Parameter) und W_U-Reset tun das nicht: **Die Größe des
  Eingriffs erklärt es nicht.** Die alte Energie sinkt beim Attention-Reset ebenfalls (a 1.50).
- **Deutung (Spekulation, ungeprüft):** In diesem Modell hängt die Attention-Gewichtung von den Frequenzen der Eingaben ab (vgl. Nanda et al. 2023, Attention-Muster periodisch in a und b). Nach 50 Schritten
  könnte die Attention auf die alten Frequenzen eingestellt sein und neue Richtungen in W_E nicht weiterreichen. Das ist eine Hypothese, kein Befund; Reset-Empfindlichkeit ist kein Mechanismusnachweis (Codex zu EXP-063).
- **Grenzen:** Pilot, n = 10 bekannte Seeds, ein Zeitpunkt, 2000 Schritte, Reset auf Init (entfernt alles Gelernte des Teils).
- **Nächster Schritt:** Bestätigung an frischen Seeds mit Funktionsmaß (wie N29): Kontrast normal gegen rsattn und rsmlp gegen rsattn, 4000 Schritte.

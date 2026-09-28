---
id: paper-L0-deutungen
status: vorbereitet
datum: 2026-09-28
tags: [lab/paper]
verwandt: ["[[paper/draft_short]]", "[[experiments/EXP-100-set-vs-order/README|EXP-100]]", "[[NOVEL_DIRECTIONS]]"]
---
# L0: Deutungssätze je Ausgang, vor jedem Ergebnis festgelegt (Sitzung 44, 2026-09-28, 21:32 Berlin)

Zurück: [[paper/STATUS]] · Kurzfassung §6 · Lesarten maschinell in `lab/experiments/EXP-100-set-vs-order/analyze.py`, `feas_read.py`, `switch_analyze.py`.
Zweck: Die Deutung jedes möglichen Ausgangs steht fest, bevor die Läufe da sind. Beim Einsetzen nur Zahlen (Mittel, KI, n) ergänzen; Abweichungen vom Wortlaut im JOURNAL begründen. Alles Pilot-Wortlaut (Exploration, 8 Seeds); eine Bestätigung (L0-R) hat eigene Sätze.

## K2 unter Minibatch (`K2_MB`)
- **„Menge steuert unter Minibatch“:** *With i.i.d. minibatches of 256 and of 64 pairs, the engineered splits still steer the learned frequencies (Δ_pow … [CI] and … [CI]); the steering of Result 1 is not a full-batch artefact in this setting.* Zusatz, falls fb ≥ iid256 ≥ iid64 bei 2000 Schritten: *As expected from the dilution of the set signal within the lock-in window, it is weaker at batch 64.*
- **„Menge steuert kaum“:** *Under minibatch training the engineered splits no longer steer the frequencies measurably (upper CI bounds below 1). Result 1 is then a property of full-batch training in this setting.* (Hauptaussage im Abstract anpassen.)
- **„gemischt“:** *Steering holds at batch 256 but not at batch 64 (or vice versa); …* mit Verweis auf die Verdünnung des Mengensignals bei kleinen Batches (erste Ordnung, §6).

## Konflikt Menge gegen Reihenfolge (`Konflikt`, ggf. `Konflikt_B64`)
- **„Konflikt nicht prüfbar (Reihenfolge wirkt nicht)“ bei B 256 und 64:** *At 30 % data a fixed stride order did not shift the learned frequencies at either batch size, as a first-order estimate predicted for batch 256 (an epoch of 15 steps is shorter than the lock-in window); the order effect reported by LeDoux (2026) at 0.3 % data (an epoch of ≈ 1170 steps) does not appear in this regime.* (Regime-Aussage N52 als Hypothese, nicht als Befund.)
- **„Menge gewinnt“ (nur möglich, wenn die Reihenfolge nachweislich wirkt):** *The stride order moves energy towards its own frequencies, but the set's targets still dominate (peak outside O in ≥ 75 % of runs, Δ_pow … [CI]).*
- **„Reihenfolge gewinnt“:** *The stride order overrides the set: the peak frequency lies in O in ≥ 75 % of runs and the set steering vanishes (Δ_pow CI includes 0).* Dann ausdrücklich: Result 1 gilt nur, wenn die Reihenfolge das Festlegungsfenster nicht beherrscht.
- **„beide wirken“:** *Both the set and the order leave a mark (order share … [CI], Δ_pow … [CI]).*
- **Nur bei B 64 wirksam:** *The order acts only when an epoch (60 steps) is longer than the lock-in window, consistent with the first-order estimate; at batch 256 (15 steps) it is washed out.* (Stützt N52; eine Batchgrößen-Reihe wäre der Test.)

## Reihenfolge allein (`Reihenfolge_allein`, Zufallssplit R)
- **„wirkt“:** *On a random split the stride order alone selects its dual frequency, replicating LeDoux's effect at 30 % data.*
- **„wirkt nicht“:** *On a random split the stride order alone does not select its frequencies at 30 % data.*

## Festlegungsfenster unter Minibatch (`switch_analyze.py`)
- **„Fenster wie Full-Batch“:** *The early lock-in of Result 3 also appears under i.i.d. minibatches of 256 (a switch after 50 steps keeps more of the old choice than after 25).*
- **„verschoben/fehlt (legt vor 25 fest)“:** *Under minibatches the choice persists already after 25 steps.* **„(nach 50 oder nicht)“:** *… not yet after 50 steps.* **„umgekehrt“:** berichten und nicht deuten.
- **„Referenz nicht repliziert“:** *The full-batch reference did not replicate on these 8 pilot seeds; the minibatch result is descriptive.*

## Abgleich mit den Vorhersagen dieser Sitzung (immer berichten, egal wie es ausgeht)
Erste Ordnung sagte: B 256 ausgewaschen (klar), B 64 an der Kante. Satz: *The first-order estimate predicted … ; the feasibility runs showed … .* Eine falsche Vorhersage wird genauso berichtet (Grenze der ersten Ordnung: Adam, Nichtlinearität).

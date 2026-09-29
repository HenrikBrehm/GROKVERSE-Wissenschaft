---
id: EXP-106
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/positiv]
---
# EXP-106 (L0, Exploration): Menge gegen feste Reihenfolge bei langen Epochen (B = 16, weight decay 0.1)

Zurück: [[LAB]] · [[FINDINGS]] (vorrangige offene Frage der Woche: L0, Regel 20b) · Vorgänger [[experiments/EXP-100-set-vs-order/README|EXP-100]] (Machbarkeit und B16-Sonde) · [[BACKLOG]] (Sitzung 46) · [[confirm/L0_REGISTRATION_DRAFT|L0]] · LeDoux 2026 (arXiv 2603.25047)

**Stand:** festgelegt in Sitzung 46 (2026-09-29, ≈ 01:33 Berlin), **vor jedem EXP-106-Lauf**. Code: `design.py` (64 Jobzeilen), `analyze.py` (Selbsttest grün über den Wächter; Lader an den Sondenläufen geprüft).

## Frage und Bezug

Die Kernaussage K2 (die Trainingsmenge steuert die Frequenzen) ist Full-Batch gemessen. LeDoux 2026 findet einen Reihenfolge-Effekt vor allem bei sehr langen Epochen (p = 9973, 0.3 % Daten, ≈ 1170 Schritte je Epoche). In EXP-100 wirkt eine feste Reihenfolge bei B = 256 (15 Schritte je Epoche) gar nicht, bei B = 64 kaum, bei B = 16 (240 Schritte je Epoche) stark – dort lernt das Netz mit den Standardwerten aber nicht. Die B16-Sonde fand eine Einstellung, in der es lernt: **weight decay 0.1** (Test 0.99–1.00 in 3/3, i.i.d. und stride). Frage: **Steuert die Menge auch im Regime langer Epochen, und was gewinnt, wenn eine feste Reihenfolge andere Frequenzen bevorzugt?**

## Aufbau

- Splits von EXP-100 (Seeds 3700–3707; F/G konstruiert mit disjunkten Zielmengen, R zufällig; O = {11, 12, 22, 23, 34, 45} = Frequenzen der stride-Reihenfolge, in allen Splits auf Zufallsniveau).
- Arme, alle AdamW lr 1e-3, **weight decay 0.1**, 30 000 Schritte (volles Budget, `--stop-after-gen 30000`), GPU:
  - `fbw` Full-Batch auf F und G (K2-Referenz bei gleichem weight decay),
  - `iid16w` B = 16, i.i.d. auf F, G und R,
  - `stride16w` B = 16, feste stride-Reihenfolge auf F, G und R.
- 8 × (3 × 2 + 2) = **64 Läufe**, Ausgabe `raw/`. Laufzeit: ≈ 4–5 min je Lauf bei 10 GPU-Prozessen → ≈ 1 h mit 5 Workern.

## Messgrößen und Lesarten (vor dem Lauf festgelegt, Docstring von `analyze.py` ist maßgeblich)

- **K2-B16:** Δ_pow(iid16w) am Ende, KI-Untergrenze > 0 → „Menge steuert bei B = 16“; KI-Obergrenze < 1 → „kaum“; sonst „gemischt“.
- **Konflikt:** dieselbe Regel wie EXP-100 (Fassung 2): Die Reihenfolge muss erst nachweislich wirken (R allein „wirkt“ oder KI von o(stride) − o(iid) auf F/G über 0), dann „Menge gewinnt“ / „Reihenfolge gewinnt“ / „beide wirken“ nach Δ_pow(stride16w) und dem Anteil der stride-Läufe mit Spitze in O (Schwelle 75 %).
- **Beschreibend:** Zeitverhältnis log₂ t_gen(stride16w)/t_gen(iid16w), Anzahl nicht generalisierter Läufe je Arm, Δ_pow(fbw).
- Gültig: Seed mit allen drei Armen auf F und G ladbar und endlichem Δ_pow; < 6 gültige Seeds → „nicht auswertbar“.

**Erwartung (vorläufig, aus der Sonde, n = 3, gesehen):** Die Reihenfolge wirkt (o steigt um 0.05–0.30), setzt die Spitze aber nicht auf O und verzögert die Generalisierung um ≈ 0.3 log₂. Vermutete Lesart: „Menge gewinnt“ oder „beide wirken“. **Dagegen spräche:** stride-Spitze in O in ≥ 75 % oder Δ_pow(stride16w) nicht über 0.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

B16-Sonde (EXP-100 `raw_b16probe_v1..v3`, R-Split der Seeds 3700–3702): Wahl von weight decay 0.1 und B = 16; die R-Läufe von 3700–3702 wiederholen genau die Sonden-Konfiguration (R-allein wird zusätzlich ohne sie berichtet). EXP-100-Machbarkeit (B-Wahl). Die F/G-Splits aller acht Seeds sind bei B = 16 / wd 0.1 ungesehen.

**Einordnung:** Exploration (8 Seeds). Eine Bestätigung bräuchte eine eigene Registrierung mit frischen Seeds (Kandidat für L0, [[confirm/L0_REGISTRATION_DRAFT|L0]] H3).

## Reproduktion

```
python lab/experiments/EXP-106-l0-b16-long-epochs/design.py --jobs > lab/experiments/EXP-106-l0-b16-long-epochs/jobs.txt
python lab/tools/parallel_queue.py lab/experiments/EXP-106-l0-b16-long-epochs/jobs.txt --workers 5 --min-minutes 10
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-106-l0-b16-long-epochs/analyze.py
```

## Ergebnis (Sitzung 46, 2026-09-29, 02:51 Berlin; Exploration, 8 Seeds, noch nicht unabhängig nachgerechnet)

64/64 Läufe fehlerfrei (Log `/tmp/e106_pq.log` → `lab/runner/logs/pq_*`), 8/8 Seeds gültig, alle 48 F/G-Läufe generalisiert.
- **K2-B16: „Menge steuert bei B = 16“** — Δ_pow iid16w **9.21 [8.82, 9.60]**; Full-Batch bei gleichem wd 9.40 [8.55, 10.20]; stride16w 8.62 [7.59, 9.52].
- **Konflikt (vorab festgelegte Regel): „nicht prüfbar (Reihenfolge wirkt nicht)“**: Auf F/G keine Verschiebung zu O (o 0.013 → 0.017, KI der Differenz [−0.005, 0.012]; stride-Spitze in O 0/16); R allein „unklar“ (Spitze in O bei 3/8 der R-stride-Läufe, zwischen 25 % und 75 %).
- **Beschreibend:** Auf dem Zufallssplit R **wirkt** die Reihenfolge deutlich: o(R-stride) − o(R-iid) KI [0.07, 0.24] (ohne die in der Sonde gesehenen Seeds 3700–3702: Mittel +0.14), 3/8 Spitzen in O. Auf den konstruierten Splits verschiebt sie die Frequenzen nicht, **verzögert aber die Generalisierung** um 0.67 log₂ [0.42, 0.93] (≈ ×1.6; 16 Paare). Δ_pow(stride) − Δ_pow(iid) −0.60 [−1.41, 0.12].
- **Deutung (vorsichtig, n = 8, Exploration):** Im Regime langer Epochen wirkt eine feste Reihenfolge auf das Spektrum dort, wo die Menge selbst wenig vorgibt (Zufallssplit), nicht dort, wo die Menge die Frequenzen stark betont (konstruierte Splits); sie kostet dort nur Zeit. Das passt zu LeDoux §6.4 („importance scales inversely with content signal adequacy“). Die formale Konflikt-Lesart bleibt „nicht prüfbar“, weil die Reihenfolge-Wirkung vorab an F/G oder an ≥ 75 % Spitzen auf R gebunden war.
- **Für L0b (eigene Registrierung, nächste Sitzung):** Kandidaten H3a „Reihenfolge verschiebt o auf R“ (einseitig > 0), H3b „keine Verschiebung auf F/G“ (Äquivalenz, Grenze vorab), H3c „stride verzögert die Generalisierung auf F/G“ (log₂ > 0); Power mit `lab/confirm/L0_power_s46.py --exp106` (liest dieses summary.json).

**Nachrechnung (Sitzung 46, 02:55; unabhängiger Agent, nur numpy, `recheck_s46.py`):** alle Mittel gleich (≤ 2·10⁻¹⁵), 64/64 Läufe integer. Ergänzungen: (1) R-stride Seed 3704 generalisiert nicht (R: 15/16). (2) **Auf R keine Zeitverzögerung** (log₂-Verhältnis +0.09, n = 7, gemischte Vorzeichen); der Zeitverlust ×1.6 gilt nur auf F/G (15/16 Paare positiv). (3) R-Wirkung: 5 Seeds +0.18…+0.30, 3 Seeds ≈ 0 — genau die, deren R-iid ohnehin viel Energie auf O hat (0.20–0.24; Decken-/Ausgangswert-Effekt, ungeprüft).

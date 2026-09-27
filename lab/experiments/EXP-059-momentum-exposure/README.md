---
id: EXP-059
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-058-optim-part/README|EXP-058]]", "[[experiments/EXP-057-optim-reset/README|EXP-057]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-059: Ist das Momentum-Gedächtnis nur verlängerte A-Exposition? (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B, größte offene Frage aus P3) · Vorgänger [[experiments/EXP-058-optim-part/README|EXP-058]] · [[NOVEL_DIRECTIONS]] N28 · [[BACKLOG]] „N28-Bestätigung“.
Festgelegt 2026-09-27 (Sitzung 22), **vor jedem EXP-059-Lauf**. **Pilot**, bekannte Seeds 400–409 (keine Bestätigung).

**Warum vor der N28-Bestätigung:** EXP-058 zeigt, dass das Löschen von m beim Wechsel π von 0.30 auf 0.12 senkt. Zwei Konkurrenzmodelle erklären das:
- **M2 (verlängerte Exposition, trivial):** m enthält die A-Gradienten; im normalen Lauf schiebt der Momentum-Schwanz (β₁ = 0.9, Summe der Gewichte ≈ 9) das Netz nach dem Wechsel noch einige
  Schritte in A-Richtung. Das wirkt wie ein paar zusätzliche A-Schritte. Ist π(t) zwischen t = 25 und 35 steil, reicht das für den Abfall.
- **M1 (Optimierergedächtnis über die Exposition hinaus):** Der Schwanz wirkt stärker als dieselbe Zahl gewöhnlicher A-Schritte (z. B. weil er in eine Phase fällt, in der B-Gradienten
  und A-Momentum zusammen wirken).
Nur unter M1 wäre N28 („das Gedächtnis sitzt im Adam-Zustand“) mehr als eine Umformulierung von „mehr A-Schritte → mehr Persistenz“. Die Bestätigung soll erst nach dieser Trennung formuliert werden.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-056/057/058 an diesen Seeds (π_normal(25) 0.303, π_rom(25) 0.117; frühe Update-Norm rom < normal). Die Wahl von 10
Zusatzschritten für den Primärvergleich folgt aus 1/(1 − β₁) = 10, nicht aus Daten. Ein π(t)-Verlauf für diese Splits ist noch nicht gemessen.

| | |
|---|---|
| **Frage** | Erreicht ein Lauf mit 10 zusätzlichen A-Schritten und gelöschtem m (rom, t = 35) mindestens die Persistenz des normalen Laufs bei t = 25? |
| **Arme** (je A→B und B→A, danach 2000 Schritte) | normal bei t = 10, 15, 20, 30, 35, 50 (t = 25 aus EXP-058) · rom (`--reset-optim-part m`) bei t = 30, 35, 40, 50 (t = 25 aus EXP-058); alle `--log-update-norms 10` wie EXP-058 |
| **Seeds / Splits** | 400–409, ω = 0 (EXP-056-Splits), reine Läufe aus EXP-056; 200 neue Läufe, GPU (alle Arme auf demselben Gerät wie EXP-056/058) |
| **Maß** | π wie EXP-056 (Anteil der A-Wahl im logarithmischen Energieverhältnis, Mittel beider Richtungen) |
| **Primär** | D = π_rom(35) − π_normal(25) je Seed; einseitiger t-Test auf D < 0, 90-%-KI, Marge 0.05 |
| **Urteil** | < 8 gültig → *nicht auswertbar* · D̄ < 0, p < 0.05 und KI-Obergrenze < −0.05 → ***mehr als verlängerte Exposition*** (M1 gestützt) · KI-Untergrenze > −0.05 → ***verlängerte Exposition genügt*** (M2 reicht; N28 wird zur Aussage über die Steilheit von π(t)) · sonst ***unklar*** |
| **Sekundär (beschreibend)** | Verläufe π_normal(t) und π_rom(t) mit SD; Verschiebung δ(t′) = t′ − t_eq, wobei t_eq die Stelle ist, an der die mittlere Normalkurve π_rom(t′) erreicht (lineare Interpolation). M2 erwartet δ ≲ 10, M1 δ > 10 oder außerhalb des Messbereichs. Wann das Momentum keine Rolle mehr spielt: π_normal(50) − π_rom(50). |
| **Gültigkeit je Seed** | alle 24 benötigten Läufe über den gemeinsamen Lader ok, Reset im Lauf geprüft, L(A) − L(B) ≥ 2 |
| **Grenzen** | Pilot, n = 10 bekannte Seeds; eine Aufgabe (add 113), ω = 0; „10 Schritte“ ist eine grobe Äquivalenz (Adam-Normierung und B-Gradienten mischen sich in den Schwanz) |
| **Budget / Abbruch** | 200 Läufe à 2010–2050 Schritte, GPU 8 parallel, ≈ 30–40 min (EXP-058: 80 Läufe ≈ 12 min). Abbruch bei NaN oder wenn die Läufe deutlich langsamer als 2× EXP-058 sind. |

Selbsttest der Auswertung: `guarded_run.py -- python lab/experiments/EXP-059-momentum-exposure/analyze.py --selftest`.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-059-momentum-exposure/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-059-momentum-exposure/analyze.py
```

## Ergebnis (Sitzung 22, Läufe 07:02–07:22, Auswertung 07:22 Berlin; `summary.json`)

200/200 Läufe ok, 10/10 Seeds gültig.

- **Primär:** D = π_rom(35) − π_normal(25) = **+0.059**, SD 0.062, 90-%-KI [0.023, 0.095] → ***verlängerte Exposition genügt*** (M2). 8/10 Seeds D > 0, Minimum −0.012.
- **π-Kurven (Mittel, SD ≈ 0.1–0.2):** normal t = 10 / 15 / 20 / 25 / 30 / 35 / 50: **0.01 / 0.07 / 0.19 / 0.30 / 0.39 / 0.56 / 1.05**; nur m t = 25 / 30 / 35 / 40 / 50: 0.12 / 0.20 / 0.36 / 0.60 / 0.97.
- **Verschiebung δ** (wie viele A-Schritte das Löschen von m kostet): 8.1 / 9.6 / 6.5 / 3.8 / 2.4 bei t = 25 / 30 / 35 / 40 / 50. Das passt zu einem Momentum-Schwanz von ≲ 1/(1 − β₁) = 10 Schritten,
  der mit wachsendem t relativ an Gewicht verliert (π_normal − π_rom: 0.19 bei t = 25 und 35, 0.08 bei t = 50).
- **Lesart (Pilot, bekannte Seeds):** Der Abfall nach dem Löschen des Momentums (EXP-058) erklärt sich vollständig dadurch, dass dem Netz einige A-Schritte fehlen. Ein eigenes „Gedächtnis im Adam-Zustand“
  (M1) ist nicht nötig. Die Deutung von N28 wird entsprechend zurückgestuft. Der eigentliche Befund ist die **Steilheit der Festlegung**: π steigt zwischen t = 10 und 50 von ≈ 0 auf ≈ 1,
  also um ≈ 0.02–0.03 je A-Schritt. Nach 50 A-Schritten ändern 2000 Schritte auf einem paar-disjunkten B die Präferenz im Mittel nicht mehr (π ≈ 1; ein Seed 0.68).
- **Grenzen:** Pilot, n = 10 bekannte Seeds, eine Aufgabe, ω = 0. δ ist aus Mittelkurven interpoliert.
- **Folge:** N28-Bestätigung ([[confirm/N28_REGISTRATION|N28]]) mit H1 (m-Reset senkt π) und H2 (Nichtunterlegenheit: m@35 ≥ normal@25 − 0.05) sowie normal@50 beschreibend.

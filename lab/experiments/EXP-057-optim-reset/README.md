---
id: EXP-057
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[confirm/P3_REGISTRATION_DRAFT|P3]]", "[[experiments/EXP-056-overlap-persistence/README|EXP-056]]", "[[experiments/EXP-038-where-lockin/README|EXP-038]]", "[[JOURNAL]]"]
---
# EXP-057: Sitzt die Persistenz nach einem frühen Wechsel im AdamW-Zustand oder in den Gewichten? (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]]: Zielt auf die **größte offene Frage** aus P3 („Festlegung im Netz oder Optimiererzustand?“, Codex-Prüfung 06:10).
Festgelegt 2026-09-27 06:16 Berlin (Sitzung 21), **vor jedem EXP-057-Lauf**. **Pilot** (10 Seeds, bekannte Seeds 400–409 aus EXP-056).

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-056 (π(0) = 0.30 an genau diesen Seeds, deren Läufe hier wiederverwendet werden), P3 (π(0) = 0.35, bestätigt),
P3-Zerlegung (Ziele des ersten Splits 20 % gegen Zufall 8.9 %), Codex-Einwand (Optimiererzustand/verlangsamte Anpassung nicht getrennt).

| | |
|---|---|
| **Frage** | Trägt der AdamW-Zustand (Momente, Schrittzähler) nach 25 Schritten auf A die Persistenz, oder tragen sie die Gewichte? |
| **Eingriff** | `freq_ban.py --reset-optim-at-switch` (neu, 5aa8c34): Beim Wechsel wird der AdamW-Zustand **aller** Parameter gelöscht, die Gewichte bleiben (im Lauf geprüft) |
| **Läufe** | Seeds 400–409, ω = 0 (EXP-056-Splits). Neu: A→B_ro, B→A_ro (25 + 2000), nur A / nur B mit 2025 Schritten (gleich lange Referenzen). Wiederverwendet: EXP-056 nur A, nur B, A→B, B→A. 40 neue Läufe, GPU |
| **Maß** | π wie EXP-056 (Normierung mit den reinen 2000-Schritt-Läufen). π_normal (EXP-056-Läufe), π_ro (mit Reset) |
| **Primär** | Δ_s = π_normal − π_ro, einseitiger t-Test Δ̄ > 0 |
| **Urteil** | < 8 gültig → *nicht auswertbar* · Δ̄ > 0 signifikant und π̄_ro ≤ 0.1 → ***Optimiererzustand trägt die Persistenz*** · Δ̄ signifikant und π̄_ro > 0.1 → ***teilweise*** · 90-%-KI von Δ̄ in [−0.1, 0.1] → ***Gewichte tragen die Persistenz*** · sonst ***unklar*** |
| **Gültig** | alle 8 Läufe ok (Lader, Hashes, Reset im Lauf protokolliert), L(A) − L(B) ≥ 2 |
| **Sekundär** | π relativ zu den gleich langen 2025-Schritt-Referenzen; Anteil der Ziele des ersten Splits in den Reset-Läufen gegen Zufall (5/56) |
| **Erwartung** | offen. EXP-038 (Rücksetzen von Gewichten, AdamW-Zustand der zurückgesetzten Teile gelöscht, Festlegung blieb) spricht eher für die Gewichte |
| **Grenzen** | Der Reset startet auch die Bias-Korrektur neu (die ersten Schritte danach sind wie ein frischer Adam). Eine Lernraten-Uhr ist damit nicht getrennt. Pilot, bekannte Seeds |
| **Budget** | 40 Läufe à 2025 Schritte, GPU 8 parallel ≈ 5 min |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-057-optim-reset/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-057-optim-reset/analyze.py
```

## Ergebnis (Sitzung 21, Läufe 06:17–06:21, Auswertung 06:21 Berlin; `summary.json`)

40/40 neue Läufe ok, 10/10 Seeds gültig, Reset in jedem Lauf protokolliert (`check = true`).

- **Primär:** Δ̄ = π_normal − π_ro = **0.195**, SD 0.112, t = 5.5, p = 0.0002, 90-%-KI [0.13, 0.26]; π̄_ro = **0.108** (knapp über der Schwelle 0.1) → formal
  ***teilweise: Optimiererzustand trägt einen Teil, Gewichte den Rest***.
- π_normal 0.303; mit gleich langen Referenzen (2025 Schritte) 0.304. Die Schrittzahl spielt also keine Rolle.
- **Beschreibend, entscheidend für die Lesart:** Mit Reset tragen die Ziele des ersten Splits nur **7.1 %** der W_E-Leistung (Zufall 8.9 %; über Zufall nur in 3/10 Seeds).
  Ohne Reset sind es 20 % (P3, 48/60 Richtungen über Zufall). π_ro je Seed −0.25 … 0.26.
- **Lesart (vorsichtig, Pilot, bekannte Seeds):** Die **A-spezifische** Erhaltung nach 25 Schritten verschwindet mit dem AdamW-Zustand fast ganz. Was von π übrig bleibt (≈ 0.1),
  passt eher zu einer unspezifisch verlangsamten Anpassung als zu erhaltener A-Präferenz, denn die A-Ziele liegen dann unter Zufall. Das Gedächtnis der ersten 25 Schritte sitzt demnach
  vor allem in den **Adam-Momenten** (bzw. im Schrittzähler/der Bias-Korrektur), nicht in den Gewichten. Das widerspricht meiner Erwartung aus EXP-038. EXP-038 lag aber bei t = 150,
  und dort behielt der jeweils nicht zurückgesetzte Teil seinen AdamW-Zustand.
- **Offen:** Momente (m) gegen zweite Momente (v) gegen Schrittzähler trennen; derselbe Eingriff bei t = 50/150 (wann geht das Gedächtnis vom Optimierer in die Gewichte über?);
  eine Bestätigung an frischen Seeds.

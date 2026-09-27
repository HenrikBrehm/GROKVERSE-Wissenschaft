---
id: EXP-063
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-062-rate-race/README|EXP-062]]", "[[experiments/EXP-038-where-lockin/README|EXP-038]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-063: Wo sitzt der Ausschluss neuer Frequenzen bei t = 50? W_E oder der Rest des Netzes (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B) · [[NOVEL_DIRECTIONS]] N29 · [[BACKLOG]] „N29-Ursache“ (K2) · Vorgänger [[experiments/EXP-062-rate-race/README|EXP-062]].
Festgelegt 2026-09-27 (Sitzung 22), **vor jedem EXP-063-Lauf**. **Pilot**, bekannte Seeds 400–409.

**Bereits gesehene Daten:** EXP-059/062 an diesen Seeds (normal@50: b50 = 4.25 im Mittel, π = 1.05), EXP-038 (bei t = 150 genügt W_E allein oder der Rest allein, 5/5).

| | |
|---|---|
| **Frage** | Verschwindet der Ausschluss (großes b bei t = 50), wenn beim Wechsel der Rest des Netzes auf seine Init zurückgesetzt wird (W_E bleibt)? Und bleibt er, wenn nur W_E zurückgesetzt wird? |
| **Arme** (A→B und B→A, Wechsel bei 50, danach 2000) | rsrest (`--reset-at-switch rest`), rswe (`--reset-at-switch we`); Vergleich normal@50 aus EXP-059; alle GPU, `--log-update-norms 10` wie EXP-059 |
| **Maß** | a, b wie EXP-062 (Endspektren, reine Läufe aus EXP-056), je Seed Mittel beider Richtungen; dazu π |
| **Primär** | Δb_rest = b50(normal) − b50(rsrest) je Seed |
| **Urteil** | Δb_rest > 1 in ≥ 8/10 Seeds → ***Ausschluss sitzt (auch) im Rest des Netzes*** · Δb_rest < 0.5 in ≥ 8/10 → ***Rest-Reset hebt den Ausschluss nicht auf*** · sonst ***unklar***. Beschreibend: b50(rswe) (bleibt er groß, genügt der Rest allein für den Ausschluss). |
| **Grenzen** | Pilot; ein Reset auf die Init entfernt auch alles andere Gelernte (nicht nur die Ausrichtung); nur t = 50 |
| **Budget** | 40 Läufe à 2050 Schritte, GPU, 2 Arbeiter neben den Bestätigungsblöcken |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-063-exclusion-locus/jobs.txt --workers 2
python lab/tools/guarded_run.py -- python lab/experiments/EXP-063-exclusion-locus/analyze.py
```

---
id: EXP-063
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv]
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

## Ergebnis (Sitzung 22, Läufe 07:54–08:14, ein Lauf nach Speicherfehler 08:14 mit demselben Befehl nachgeholt; Auswertung 08:14–08:17 Berlin; `summary.json`)

40/40 Läufe ok, 10/10 Seeds gültig, Reset je Lauf im Ergebnis vermerkt.

- **Primär:** Δb_rest = b50(normal) − b50(rsrest) > 1 in **10/10** Seeds (1.43 … 4.45, Mittel 3.2) → ***Ausschluss sitzt (auch) im Rest des Netzes***.
- **Mittel:** normal a = 3.66, b = 4.25 · Rest zurückgesetzt a = 3.10, **b = 1.05** · nur W_E zurückgesetzt a = 2.51, **b = 0.44**.
- **Lesart (Pilot, bekannte Seeds):** Beide Resets heben den Ausschluss weitgehend auf: Die neuen Frequenzen werden wieder gelernt. Die alten bleiben in beiden Fällen stark erhalten, auch wenn W_E
  auf seine Init zurückgesetzt wird (der Rest des Netzes baut sie in W_E wieder auf, vgl. [[experiments/EXP-038-where-lockin/README|EXP-038]]). Also: **Das Erhalten der alten Wahl ist doppelt vorhanden
  (W_E oder Rest genügt), der Ausschluss der neuen braucht W_E und Rest zusammen.** Das Zwei-Regime-Bild aus EXP-062 bekommt damit einen Ort: Bei t = 50 ist das ganze Netz so aufeinander eingestellt,
  dass neue Frequenzen nicht mehr entstehen.
- **Grenzen:** Pilot, n = 10, nur t = 50; ein Reset auf die Init entfernt alles Gelernte des Teils, nicht nur die Ausrichtung; b nach W_E-Reset ist gegen ein reines Y-Modell gemessen, das von derselben Init startet.
- **Nächste Frage:** Welcher Teil des Rests (Attention, MLP, Unembedding)? Und K1 (Weight Decay) aus dem [[BACKLOG]].
*Wortlaut nach Codex (08:34):* „hebt auf“ ist zu stark; b sinkt stark, aber nicht auf 0. Beide Resets sind grobe Init-Resets und lokalisieren keinen Mechanismus: Reset-Empfindlichkeit und mögliche Koadaptation, keine funktionale Aussage.

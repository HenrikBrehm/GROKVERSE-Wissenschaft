---
id: EXP-075
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-045-mlp-steering/README|EXP-045]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[experiments/EXP-073-part-rewind/README|EXP-073]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[JOURNAL]]"]
---
# EXP-075: Legt sich die Frequenzwahl auch in einem Netz ohne Attention früh fest? (PILOT)

Zurück zu [[LAB]] · [[FINDINGS]] „Größte offene Frage“ und Grenze 2/3 (eine Architektur) · Regel 15c. Festgelegt 2026-09-27, Sitzung 24, **vor jedem EXP-075-Lauf** (Läufe ab 00:00).
**Pilot**, bekannte Seeds 400–409 (EXP-056-Splits ω = 0), kein Urteil.

- **Frage:** Die Reset-Befunde (K4d/K4e) zeigen, dass die Persistenz im Transformer empfindlich für den Attention-Wertepfad ist. Ist die frühe Festlegung deshalb an die Attention gebunden, oder
  entsteht sie genauso in der MLP-Architektur mit geteilter Einbettung (`--arch mlp`, EXP-045: dort sind die Frequenzen ebenso steuerbar, Grokking bei ≈ 3500–7600 Schritten)?
- **Konkurrenzmodelle:** (Att) Die Festlegung braucht den Attention-Wertepfad → in der MLP-Architektur keine oder eine viel spätere Festlegung. (Gen) Die Festlegung ist eine allgemeine Eigenschaft
  gelernter Einbettungen unter AdamW (z. B. Amplitudenrennen, H40) → ähnlich früh wie im Transformer.
- **Läufe:** `--arch mlp`, GPU, 1 Thread: reine Läufe A und B (2000 Schritte) und Wechsel A→B, B→A bei t ∈ {10, 25, 50, 100, 200}, danach 2000 Schritte; `--stop-after-gen 100000`
  (kein vorzeitiger Stopp). 120 Läufe.
- **Maß:** π wie EXP-056/059 aus den End-W_E; mittlere Kurve π(t) über gültige Seeds; t½ = erste Wechselzeit, an der die mittlere Kurve 0.5 erreicht (lineare Interpolation).
  Transformer-Referenz aus EXP-059 (gleiche Seeds, Splits, Budget): **t½ = 33.3** (vor dieser Festlegung gesehen).
- **Lesart vorab:** t½ ≤ 2 × 33.3 → *ähnlich früh wie im Transformer* (stützt Gen, die Attention ist dann nicht nötig für die Festlegung, nur ein Ort, an dem sie im Transformer empfindlich ist);
  t½ > 4 × 33.3 oder π(200) < 0.5 → *deutlich später oder keine Festlegung im Messbereich* (stützt Att); sonst *unklar*.
- **Gültigkeit:** je Seed alle 12 Läufe über den gemeinsamen Lader ok (inkl. `config.arch = mlp`), L(A) − L(B) ≥ 2; ≥ 8 gültige Seeds.
- **Grenzen:** Die MLP-Architektur lernt anders schnell; ein Unterschied in t½ kann auch aus einer anderen Lerngeschwindigkeit kommen (dann Λ bzw. Strecke von W_E am Wechsel vergleichen,
  `we_snapshots` bei t sind gespeichert). Pilot mit bekannten Seeds. π ist ein Energiemaß.
- **Budget:** 120 Läufe à ≤ 2200 Schritte, 0.004 s/Schritt (EXP-045) → wenige Minuten bei 8 parallel.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-075-mlp-lockin/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-075-mlp-lockin/analyze.py
```

## Ergebnis (Sitzung 36, 2026-09-28, Läufe 02:14–02:18, Auswertung 02:18 Berlin, gemessen)

120/120 Läufe ok (GPU, `--workers 8`, Log `lab/runner/logs/exp075_s36.log`). **Urteil nach Regel: *nicht auswertbar*.** Nur 5/10 Seeds gültig (≥ 8 verlangt): Bei
400, 401, 402, 406 und 408 trennen sich die reinen MLP-Läufe A und B im Maß L(A) − L(B) nur um 1.67–1.86 (< 2). Das MLP bildet die beiden Frequenzmengen also weniger getrennt aus als der
Transformer. **Nur beschreibend, kein Urteil:** Die 5 gültigen Seeds haben π(10) ≈ 0, π(25) 0.08–0.16, π(50) 0.48–0.60, π(100) 0.93–1.22, π(200) 1.17–1.64. Die mittlere Kurve
erreicht 0.5 nahe t = 50, also innerhalb von 2 × 33.3. Das wäre die Richtung „ähnlich früh“ (Gen), bei ausgewählten Seeds. Kriterien nicht nachträglich geändert. Ein sauberer Nachfolger bräuchte
frische Seeds mit MLP-eigener Trennprüfung vor der Zuordnung (neue Registrierung, kein Nachtrag). [[JOURNAL]] Sitzung 36.

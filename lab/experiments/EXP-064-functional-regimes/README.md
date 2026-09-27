---
id: EXP-064
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-062-rate-race/README|EXP-062]]", "[[experiments/EXP-063-exclusion-locus/README|EXP-063]]", "[[confirm/N28_REGISTRATION|N28]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-064: Sind die zwei Spektralsignaturen auch funktional? (Pilot)

Zurück zu [[LAB]] · [[FINDINGS]] („Zwei spektrale Signaturen“, Funktion nicht geprüft) · [[NOVEL_DIRECTIONS]] N29 · Vorgänger [[experiments/EXP-062-rate-race/README|EXP-062]].
Festgelegt 2026-09-27 (Sitzung 22), **vor jedem EXP-064-Lauf**. **Pilot**, bekannte Seeds 400–409.

**Bereits gesehene Daten:** EXP-059/062/063 an diesen Seeds (Spektren, π, a/b), N28 an frischen Seeds. Codex-Einwand (08:34): a/b zeigen nur Spektralsignaturen.

| | |
|---|---|
| **Frage** | Nutzt das Endmodell nach einem Wechsel bei t = 25 **beide** Frequenzmengen (funktionale Koexistenz) und nach t = 50 nur noch die alten (funktionaler Ausschluss)? |
| **Läufe** | Seeds 400–409, EXP-056-Splits (ω = 0), A→B und B→A, Wechsel bei t ∈ {25, 50}, danach 2000 Schritte, `--save-model`; 40 Läufe, GPU (Läufe identisch mit normal@t aus EXP-058/059, nur mit gespeichertem Modell) |
| **Eingriff** | Am Endmodell die Zeilen W_E[:113] auf das Komplement der Fourier-Unterräume einer Zielmenge projizieren (alle 5 Frequenzen vollständig entfernt): „alt entfernt“ bzw. „neu entfernt“. Rest des Netzes unverändert. |
| **Maß** | Genauigkeit auf der gemeinsamen Testmenge des Seeds (Paare in keinem Split) vor und nach dem Eingriff; je Seed Mittel beider Richtungen. acc_alt, acc_neu = Genauigkeit nach Entfernen der alten bzw. neuen Ziele. |
| **V1 (Funktion folgt dem Spektrum)** | (acc_neu − acc_alt) bei t = 50 größer als bei t = 25 in ≥ 8/10 Seeds (bei 50 schadet das Entfernen der neuen weniger, relativ zu den alten). |
| **V2 (Koexistenz bei 25)** | acc_alt < 0.9 **und** acc_neu < 0.9 bei t = 25 in ≥ 8/10 Seeds (beide Mengen werden gebraucht). |
| **V3 (Ausschluss bei 50)** | acc_neu ≥ 0.9 bei t = 50 in ≥ 8/10 Seeds (die neuen werden nicht gebraucht). |
| **Urteil** | V1–V3 → ***funktionale Zwei Regime (Pilot)***; nur V1 → ***Funktion folgt dem Spektrum, Regime nicht scharf***; sonst ***Spektralsignaturen nicht funktional***. Basis-Genauigkeit < 0.9 in einem Arm → Seed ungültig (< 8 gültig: nicht auswertbar). |
| **Grenzen** | Pilot, bekannte Seeds; vollständige Entfernung (keine Dosis); nur W_E; Genauigkeit ist grob. |
| **Budget** | 40 Läufe à 2025/2050 Schritte, 1 GPU-Arbeiter (Speicher), ≈ 25–30 min |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-064-functional-regimes/jobs.txt --workers 1
python lab/tools/guarded_run.py -- python lab/experiments/EXP-064-functional-regimes/analyze.py
```

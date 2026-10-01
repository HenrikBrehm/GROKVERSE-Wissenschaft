---
id: EXP137_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# EXP-137 (Datendichte-Leiter bei p 211/307): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[LAB]] · [[experiments/EXP-137-modulus-density/README|EXP-137]] · [[paper/EXP136_DEUTUNGEN]]

**Geschrieben in Sitzung 67 (01.10.2026, 05:48 Berlin gemessen), bevor ein Blocklauf von EXP-137 fertig war** (3 von 36 gestartet, keiner gelesen). Bekannt: alle EXP-136-Ergebnisse und ein Lader-Test (Seed 13700, p 211, 10 %, nur Arm F, 1000 Schritte, nicht generalisiert). EXP-137 ist eine **Exploration mit 3 Seeds je Zelle**: höchstens ein Satz im Anhang A.2 (an den EXP-136-Absatz angehängt) und eine Änderung des Halbsatzes in Grenze (ii). **Kein Abstract, keine neue Kernaussage.** Zahlen nach `analyze.py`, unabhängige Textprüfung wie immer.

## Satz im Anhang A.2 (an den EXP-136-Absatz), je Gesamtlesart (p 211 und p 307 getrennt; bei verschiedenen Lesarten je p ein Halbsatz)

- **„K2 hält bei p mit weniger Daten“:** *A follow-up pilot (EXP-137, three seeds per cell) used 10, 15 and 20 % data; where both arms generalized (… of … seeds), the engineered splits steered the embedding frequencies after generalization (Δ_pow 1000–2000 steps after generalization …–…, down to … % data at mod …).*
- **„Steuerung schwindet mit der Dichte“:** *… at 20 % data the splits still steered the frequencies after generalization (Δ_pow …–…), but at … % data, where the networks still generalized, they did not (Δ_pow …–…, threshold 1). In this pilot the steering weakened with data density before generalization failed, which is consistent with LeDoux's (2026) report at much lower density.*
- **„kein Lernen im Budget“ (alle Anteile):** *… with 10–20 % data … of … runs generalized within 30 000 steps, too few to read the steering after generalization.*
- **„beschreibend“ (gemischt):** *A follow-up pilot with 10–20 % data (EXP-137) gave no consistent picture (…).* + die Zahlen der auswertbaren Zellen.

## Grenze (ii), Halbsatz (ersetzt den EXP-136-Halbsatz „… so the pilot was inconclusive and steering at low data density remains open“)

- hält: *…; a follow-up with 10–20 % data found steering after generalization down to … % (Appendix A)*
- schwindet: *…; a follow-up found steering at 20 % but not at … % data after generalization (Appendix A)*
- sonst: Halbsatz bleibt unverändert, mit „(also EXP-137)“.

## Was ausdrücklich nicht gesagt wird

- nichts über p = 9973 oder 0.3 % (LeDoux' Regime); p ≤ 307, Anteile ≥ 10 %;
- Paarzahl und Anteil nicht getrennt; Messpunkt (gen + 1000…2000) ist je Arm verschieden – keine Aussage über spätere Konvergenz;
- kein Vergleich der Δ_pow-Beträge mit EXP-136 (andere Seeds, anderer Messpunkt) außer beschreibend;
- Einbettungsenergie, keine Ablation (Funktion nicht geprüft);
- Mittel über 3 Seeds sind keine Effektschätzung; keine KI, keine p-Werte.

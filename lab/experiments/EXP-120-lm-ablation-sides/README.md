---
id: EXP-120
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, lm-leiter, befund/unklar]
---
# EXP-120: Ablation getrennt nach Ein- und Ausgabeseite im ungekoppelten Sprachmodell

Zurück: [[LAB]] · [[FINDINGS]] · Bezug [[confirm/LM1F_REGISTRATION|LM1-F]] (bestätigt; Vorbehalt: gebundene Einbettung, Seiten nicht getrennt), [[experiments/EXP-117-lm-untied/README|EXP-117]] (ungekoppelte Modelle, „Eingabe gesteuert“), [[experiments/EXP-118-lm-ablation/README|EXP-118]] (Ablation, gebunden) · [[JOURNAL]] Sitzung 54

**Bezug zu FINDINGS:** offene Grenze von LM1-F (Sitzung 54): Nutzt das LM die gesteuerten Frequenzen beim Lesen der Zahlen (Eingabe) oder beim Antworten (Ausgabe)? Exploration an bekannten Modellen, kein Training; entscheidet nur, wie der LM1-F-Satz im Paper eingeschränkt wird.

## Vorab (Sitzung 54, 22:54 Berlin gemessen, vor jeder Rechnung)

- **Frage:** In den vier ungekoppelten EXP-117-Modellen (Seeds 3862/3863, F/G, K = 19, 6000 Schritte): Kostet das Entfernen des eigenen Zielfrequenz-Unterraums nur in der Eingabe-Einbettung, nur in der Ausgabeschicht oder in beiden Genauigkeit auf zurückgehaltenen Fakten?
- **Hypothese:** „beide Seiten“ (Δ_in 6.4/5.5 und Δ_out ≈ 4 in EXP-117, beide gesteuert). Alternative „nur Eingabe“ wäre auch plausibel (Δ_in wächst weiter, Δ_out stagniert).
- **Eingriff:** wie EXP-118/LM1-F (Projektion der 113 Zahl-Zeilen, Konstante unberührt), Seiten in / out / beide; Mengen: eigene Ziele, fremde Ziele, 4 Kontrollmengen (`SeedSequence([120, split_seed])`).
- **Maß:** C_Seite = acc(fremd) − acc(eigen) je Lauf.
- **Lesarten (im Skript festgelegt):** „beide Seiten“: C_in > 0.3 und C_out > 0.3 in 4/4; „nur Eingabe“: C_in > 0.3 in 4/4 und |C_out| < 0.1 in 4/4; „nur Ausgabe“ gespiegelt; „keine Seite allein“: |C_in|, |C_out| < 0.1 und C_beide > 0.3 in 4/4; sonst „unklar“. Kontrolle: Basisgenauigkeit = geloggte Endgenauigkeit (|Δ| < 10⁻⁶), sonst „nicht auswertbar“.
- **Was gegen die Hypothese spräche:** jede andere Lesart. „nur Eingabe“ hieße: Die Zahl-Repräsentation selbst trägt die Fakten über die Zielfrequenzen; „nur Ausgabe“: Der LM1-F-Befund wäre vor allem eine Eigenschaft der Ausgabevektoren.
- **Grenzen, vorab:** 2 Seeds, bekannte Modelle, ungekoppelt ≠ LM1 (gekoppelt); eine Ablationsart. Übertragung auf LM1 nur als Hinweis.
- **Budget:** 4 Modelle × 19 Auswertungen auf der CPU (4 Threads), geschätzt 10–20 min; Abbruch bei Fehler.
- **Bereits gesehen:** EXP-117 Δ_in/Δ_out und Genauigkeiten; LM1-F-Ergebnis (Anlass). Keine Ablation an EXP-117-Modellen.

**Befehl:** `python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/experiments/EXP-120-lm-ablation-sides/ablate_sides.py`

## Ergebnis (Sitzung 54, 23:20 Berlin gemessen; GPU, 78.6 s; `summary.json`, `run.log`)

**Ablauf:** Der erste Lauf auf der CPU (Start 22:54) war unter der Last des Dienstes zu langsam (nach 24 min noch kein Modell fertig, Schätzung ≈ 25 min je Modell) und wurde abgebrochen (`run_cpu_killed.log`, kein Ergebnis). Danach `--device cuda` ergänzt (einzige Codeänderung, im Skriptkopf vermerkt; Lesarten unverändert) und neu gestartet. Kontrolle bestanden: Basis = geloggte Endgenauigkeit (|Δ| ≤ 2.7·10⁻⁸).

**Vorab-Lesart: „unklar“.** C_in > 0.3 in 4/4, C_out in 3/4 > 0.3, im vierten 0.270. Also weder „beide Seiten“ (Schwelle in einem Lauf knapp verfehlt) noch „nur Eingabe“ (|C_out| < 0.1 in keinem Lauf).

| Seed/Arm | Basis | Eingabe eigen / fremd (C_in) | Ausgabe eigen / fremd (C_out) | beide eigen (C_beide) | Kontrollen Eingabe / Ausgabe |
|---|---|---|---|---|---|
| 3862 F | 0.966 | 0.054 / 0.969 (0.915) | 0.658 / 0.970 (0.312) | 0.056 (0.917) | 0.947 / 0.964 |
| 3862 G | 0.920 | 0.018 / 0.921 (0.903) | 0.546 / 0.926 (0.380) | 0.011 (0.916) | 0.909 / 0.921 |
| 3863 F | 0.954 | 0.065 / 0.953 (0.888) | 0.693 / 0.963 (0.270) | 0.087 (0.868) | 0.912 / 0.940 |
| 3863 G | 0.954 | 0.019 / 0.939 (0.920) | 0.401 / 0.958 (0.557) | 0.014 (0.931) | 0.949 / 0.959 |

**Beschreibend (nicht vorab festgelegt):** Die Eingabe-Ablation allein kostet so viel wie die Ablation beider Seiten (eigene Genauigkeit 0.02–0.07 gegen 0.01–0.09). Die Ausgabe-Ablation kostet 27–56 Punkte, also deutlich, aber nicht alles. Die ungekoppelten Modelle nutzen die gesteuerten Frequenzen demnach vor allem beim Lesen der Zahlen und teilweise beim Antworten. Das passt zu EXP-117 (Δ_in > Δ_out am Ende).
**Folge für LM1-F (nur Hinweis):** Es ist unwahrscheinlich, dass der LM1-F-Befund allein von den Ausgabevektoren getragen wird. Die LM1-Modelle sind aber gekoppelt, deshalb ist das keine Aussage über LM1. Im Paper höchstens als Satz in Anhang J mit „exploration, 2 seeds, untied models“.
**Grenzen:** 2 Seeds, bekannte Modelle, eine Ablationsart, Schwelle 0.3 willkürlich (vorab).

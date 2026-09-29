---
id: EXP-120
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
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

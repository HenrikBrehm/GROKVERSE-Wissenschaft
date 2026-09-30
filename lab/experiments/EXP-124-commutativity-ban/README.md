---
id: EXP-124
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-124 (Entwurf): Entsteht die frühe Kommutativität konstruierter Splits über die Zielfrequenzen?

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage N57, Sitzung 55) · Vorgänger [[experiments/EXP-123-commutativity-stages/README|EXP-123]] · [[NOVEL_DIRECTIONS]] N57 · [[JOURNAL]] Sitzung 55 Zyklus 15

**Status: Entwurf (02:58, Sitzung 55), kein Code, nichts gerechnet.** Vor dem Einfrieren: Code (`swap_trace.py` um einen festen Frequenzbann nach der Semantik von freq_ban erweitern: projizierter Gradient ab Schritt 1, Projektion von W_E[:p] und exp_avg), Smoke (ohne Bann bitgleich zu EXP-123), blinde Code-Prüfung, Abwägung gegen Regel 20 (Paper/LM-Leiter haben Vorrang; nur wenn die GPU Platz hat).

- **Beobachtung:** Konstruierte Splits (E2_0) erreichen die Kommutativitätsstufe ≈ 11× früher als Zufallssplits (EXP-123, post hoc), und t_swap hängt in E2_0 so eng an der frühen W_E-Zielenergie wie t_gen (ρ −0.80). Korrelation trennt nicht: Kommutativität *über* die Fourier-Struktur oder beides nur gemeinsam schneller?
- **Eingriff:** Auf den E2_0-Splits der R5-Einheiten u0–u9 (Init-Seeds wie EXP-123) die fünf eigenen Zielfrequenzen der Einheit ab Schritt 1 aus W_E bannen (Arm T) gegen einen Bann von fünf zufälligen Nicht-Zielfrequenzen (Arm C, feste Ziehung je Einheit). 20 Läufe, höchstens 8000 Schritte, Messung wie EXP-123 (acc_swap/acc_other alle 25 Schritte).
- **Maß:** L_swap = log2 t_swap(T) − log2 t_swap(C) je Einheit (zensiert als 8000); L_other entsprechend.
- **Lesarten (Entwurf):** „Kommutativität über die Zielstruktur“: Mittel L_swap ≥ 1 (×2) und ≥ 8/10 positiv; „eigener Pfad“: |Mittel L_swap| < 0.3 bei Mittel L_other ≥ 1; sonst „unklar“. Beschreibend: Liegt t_swap(T) nahe am R-Niveau (EXP-123 Median 4150)?
- **Was dagegen spräche:** L_swap ≈ 0: Die frühe Kommutativität braucht die Zielfrequenzen nicht.
- **Bereits gesehen:** EXP-123 (alle Zeiten der E2_0- und R-Arme dieser Einheiten), R5-Zeiten. Der Bann ist eine starke Veränderung (EXP-001: Netz weicht auf andere Frequenzen aus); ein Befund betrifft „ohne Zielfrequenzen“, nicht „ohne Fourier-Struktur“.
- **Grenzen:** 10 Einheiten, eine Aufgabe; Exploration.

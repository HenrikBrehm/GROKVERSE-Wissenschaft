---
id: EXP-123
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-123: Zwei Stufen vor dem Grokking – Kommutativität, dann der Rest; verkürzt die Datenauswahl die zweite Stufe?

Zurück: [[LAB]] · [[NOVEL_DIRECTIONS]] N57 · Pilot [[experiments/EXP-122-toy-commutativity/README|EXP-122]] (4 + 4 Läufe) · LM-Anlass [[experiments/EXP-119-lm-speed-r5/README|EXP-119]] · [[JOURNAL]] Sitzung 55

**Bezug zu FINDINGS:** Kernaussage **R5** (konstruierte Splits generalisieren ≈ 6.5× früher). Frage: *Wo* im Ablauf gewinnen sie die Zeit? Hypothese aus EXP-122: nicht bei der Kommutativität (Stufe 1), sondern bei den Paaren ohne trainiertes Tauschpaar (Stufe 2). Kein neuer Kernaussage-Kandidat für das eingefrorene Paper (Regel 20a); Ergebnis gehört höchstens in einen Anhang.

## Vorab (Sitzung 55, 30.09., vor jedem Hauptlauf; Commit dieser Datei = Einfrierpunkt)

- **Aufbau:** Die 20 R5-Einheiten (u0–u19; Init-Seed je Einheit aus `lab/confirm/r5_splits/r5_uN.json`, gemeinsame Testmenge T* = 2554 Paare), Arme **R** (gleichverteilt), **E2_0** (konstruiert, ε = 2), **D_0** (je Antidiagonale gleich viele Paare wie E, Lage zufällig). Tauschanteile in allen Armen abgeglichen (R5: 0.30 ± 0.04). 60 Läufe, `swap_trace.py` (Full-Batch, Lernpfad = `repro/train.py` = freq_ban), GPU, höchstens 8000 Schritte, Abbruch 250 Schritte nach Test ≥ 0.95. Alle 25 Schritte: Train-, Test-Genauigkeit, **acc_swap** (Testpaare, deren Tauschpaar (b, a) trainiert ist, ≈ 30 %) und **acc_other**.
- **Maße:** t_swap / t_other = erster Schritt mit acc_swap / acc_other ≥ 0.5 (zensiert, wenn nicht erreicht); **m** = acc_other zum Zeitpunkt t_swap („wie weit ist der Rest, wenn die Kommutativität halb da ist“).
- **H1 (Arm R, Kommutativität zuerst):** Einheit positiv, wenn t_swap beobachtet und t_other ≥ t_swap + 100 (oder zensiert). Einseitiger exakter Vorzeichentest. „gestützt“: Holm-p < 0.05, ≥ 10 bestimmbare Einheiten, ≥ 80 % positiv.
- **H2 (Datenauswahl verkürzt Stufe 2):** d = m(E2_0) − m(R) je Einheit (beide t_swap beobachtet). Einseitiger exakter Vorzeichen-Permutationstest auf den Mittelwert, Bootstrap-KI. „gestützt“: Holm-p < 0.05, n ≥ 10, Mittel d ≥ 0.05 (Mindesteffekt); Holm-p < 0.05 bei kleinerem Mittel: „Richtung ja, unter Mindesteffekt“.
- **Familie:** Holm über {H1, H2}. **Sekundär, beschreibend:** Arm D_0 (m, t_swap, t_other gegen R und E2_0: Liegt die Wirkung an der spektralen Anordnung oder an der Antidiagonal-Zählung?); t_swap relativ zu t_mem (Train ≥ 0.99) und t_gen je Arm; wird auch Stufe 1 verkürzt (t_swap R/E2)?
- **Technik:** Test-Kurve jedes Laufs = eingefrorene R5-Kurve (gleicher Seed/Split) bis auf ≤ 2 Vorhersagen an allen gemeinsamen Schritten, sonst „technisch“ (ausgeschlossen); mehr als 3 fehlende/defekte/technische Läufe → „nicht auswertbar“. Smoke (u0_E2_0, `smoke/`): Kurve bitgleich zu R5 (Abweichung 0.0 an 35 Schritten), t_gen 600 = R5; dort t_swap 275, t_other 425, m 0.141.
- **Erwartung:** H1 gestützt (EXP-122: 4/4); H2 gestützt (EXP-122: bei 50 % des Weges acc_other 0.05–0.33 konstruiert gegen ≤ 0.03 zufällig). **Gegen die Hypothese spräche:** m(E2) ≈ m(R), d. h. auch konstruierte Splits lernen erst die Kommutativität und dann den Rest, nur insgesamt schneller.
- **Bereits gesehen und davon beeinflusst:** R5-Generalisierungszeiten aller 60 Läufe (Grundlage für die 8000-Schritt-Grenze und die Wahl der Arme), EXP-122 (Wahl der Maße, Richtung der Hypothesen), der Smoke-Lauf u0_E2_0. Die Tauschpaar-Kurven der R5-Läufe sind ungesehen. **Keine unabhängige Bestätigung im Sinne der eingefrorenen Blöcke** (Seeds/Splits bekannt); vorab festgelegte Exploration mit neuer Messgröße.
- **Grenzen:** eine Aufgabe (add 113), ein Modell, ein Schwellenwert 0.5 (±-Empfindlichkeit wird beschreibend bei 0.3/0.7 nachgereicht, falls nötig, als post hoc markiert).
- **Literatur (Suche 30.09., Begriffe im JOURNAL Sitzung 55):** He et al. 2026 (arXiv 2602.16849, §3.3) beschreiben bei zufälligem Split, dass das Modell die Tauschpartner der Trainingsdaten richtig beantwortet, sonst nicht – aber in einem Netz mit Eingabe h_x + h_y, wo Kommutativität eingebaut ist. Park et al. 2024 (2405.16658) und Salah & Yevick 2024 (2411.05353): Hinzufügen/Entfernen von Tauschpaaren ändert die Grokking-Zeit. Dass ein Transformer (Kommutativität nicht eingebaut) zuerst die Kommutativität lernt und die Datenauswahl die zweite Stufe verkürzt: nach unserer Suche nicht gefunden (vorläufig).

**Befehle:** Jobdatei beim GPU-Dienst `lab/queue/inbox/38_exp123_commutativity.jobs` (= `jobs.txt`) · Auswertung `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-123-commutativity-stages/analyze.py`

## Ergebnis

(noch nicht ausgeführt)

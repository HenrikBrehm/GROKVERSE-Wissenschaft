---
id: EXP-127
status: vorbereitet
datum: 2026-09-30
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-127: Steuert die Faktenauswahl beim Nachtrainieren eines vortrainierten LM (Pythia-160M) die Frequenzen der Zahl-Einbettungen?

Zurück: [[LAB]] · [[FINDINGS]] · [[JOURNAL]] Sitzung 58 · Vorläufer [[experiments/EXP-117-lm-untied/README|EXP-117]] (ungekoppelt, von Grund auf), [[experiments/EXP-120-lm-ablation-sides/README|EXP-120]] (Ablation je Seite), LM1/LM1-F ([[FINDINGS]])

**Bezug zu FINDINGS:** K2 (Split-Steuerung) über das Spielzeugmodell hinaus (Programm A, Regel 15c); Auftrag des Nutzers 30.09. (Regel 20 e2): vortrainiertes kleines LM nachtrainieren, Ein- und Ausgabe-Einbettung getrennt. **Pilot (Exploration, 2 Seeds), keine Bestätigung.**

## Vorab (Sitzung 58, 2026-09-30, vor jedem Pilotlauf)

- **Frage:** Wenn ein vortrainiertes Sprachmodell (Pythia-160M, 162 M Parameter, ungebundene Ein-/Ausgabe-Einbettung) auf Rechenfakten a @ b = (a + b) mod 113 nachtrainiert wird: Bestimmt die Auswahl der Trainingsfakten, welche Fourier-Frequenzen sich in den Zahl-Einbettungen ausbilden, und nutzt das Modell sie?
- **Vorprüfungen (erledigt, JOURNAL S58):** Zahlen 0–112 sind in GPT-2 und Pythia je ein Token (mit/ohne Leerzeichen); Pythia hat `embed_in`/`embed_out` getrennt. Vortrainiertes Modell trifft mod 113 fast nie (0.077 auf 13 Proben; Test-Genauigkeit 0.009 bei Schritt 0). Ausgangsspektrum: Anteil der F-Ziele von Seed 4000 an der Leistung der Eingabezeilen 0.075, G-Ziele 0.105 (Ausgabe 0.076 / 0.117; 5 von 56 Frequenzen = 0.089 bei Gleichverteilung).
- **Aufbau:** `ft_pythia.py` (Selbsttest grün: Tokens, Maskierung, Verlustpfad gleich dem vollen Logit-Pfad bis 1e-6, Projektor, Spektrum). Pythia-160M @ 50f5173d (fp32), alle Parameter trainiert, AdamW lr 1e-4, β 0.9/0.95, wd 0.1 auf Matrizen, Warmup 100, konstant; Batch 32 Sequenzen × 16 Fakten („<eot> a @ b = c\n …“), Verlust nur auf den Antworten; jeder Fakt gleich oft (fester Zyklus, je Runde neu gemischt). Neutraler Operator „ @“, damit die vortrainierte Ganzzahl-Addition nicht über „+“ angesprochen wird. **4000 Schritte** (≈ 535 Präsentationen je Fakt).
- **Splits:** LM1-Splits `lab/confirm/lm1_splits/seed4000/4001` (F/G, gemeinsame Testmenge, fünf disjunkte Zielfrequenzen je Arm). **Gesehen:** diese Splits wurden in LM1 (anderes Modell) ausgewertet; für einen Piloten zulässig, eine Bestätigung braucht frische Splits. Der Smoke (Seed 4000 F, 250 Schritte) ist gesehen: Train 0.94, Test 0.41, Zeilen bewegen sich wenig (mittlere Änderung 0.038 bei Zeilennorm 0.79 Eingabe; 0.022 / 3.16 Ausgabe).
- **Messgrößen (Auswertung `analyze.py`, vor jedem Pilotlauf geschrieben und an den Smoke-Daten getestet):** primär **Δ_pow der Änderung der Eingabezeilen** (E_in(T) − E_in(0), P1-Definition), weil die vortrainierten Zeilen die Energie dominieren und sich wenig bewegen; sekundär Δ_pow der Zeilen selbst (Ein-/Ausgabe), der Ausgabe-Änderung, zurückgehaltene Genauigkeit, Ablation C_in/C_out/C_both = Genauigkeit ohne fremde Ziele − ohne eigene Ziele (wie EXP-120; 4 Kontrollsätze).
- **Lesarten:** Tor: zurückgehaltene Genauigkeit ≥ 0.5 am Ende in ≥ 3 von 4 Läufen, sonst „nicht auswertbar (lernt nicht)“. **„K2 hält beim Nachtrainieren“**: Tor und Δ_pow(Änderung, Eingabe) > 1 in beiden Seeds; **„bricht“**: Tor und |Δ_pow(Änderung, Eingabe)| ≤ 1 in beiden; sonst „unklar“. Beschreibend „genutzt“, wenn C_both > 0.3 in allen 4 Läufen.
- **Was gegen die Hypothese spräche:** Das Modell generalisiert, aber die Änderung der Zahl-Einbettungen trägt die Zielfrequenzen nicht bevorzugt (|Δ_pow| ≤ 1) → im vortrainierten Modell entsteht die Rechnung anderswo (tiefere Schichten) oder mit vorhandenen Merkmalen; dann Δ_pow an Zwischenrepräsentationen als nächster Schritt.
- **Budget:** Smoke 250 Schritte in ≈ 390 s unter voller GPU-Last (≈ 1.4–1.6 s/Schritt; allein vermutlich deutlich schneller), Spitze 4.4 GB (`gpu_gb=5`). 4 Läufe à 4000 Schritte: unter Last ≈ 1.5–1.8 h je Lauf, harte Grenze job_minutes 300. Nach dem Ende hängt der Prozess ≈ 2–3 min im ROCm-Abbau (Ergebnisse sind vorher atomar geschrieben).
- **Reihenfolge (Regel 20 e2):** als `46_exp127_pythia` hinter LM3/R12/EXP-125 eingereiht (der Dienst startet ihn erst, wenn der Speicher reicht).

## Deutung je Ausgang (vorab)

- „K2 hält“: *Beim Nachtrainieren eines vortrainierten 160-M-Modells bestimmte die Faktenauswahl in 2 Pilot-Seeds, welche Frequenzen die Änderung der Zahl-Eingabeeinbettung trägt* → Bestätigungsblock mit frischen Splits (10 Seeds, eingefroren) planen; Paper nur Ausblick bis zur Bestätigung.
- „bricht“: Befund „im vortrainierten Modell nicht über die Eingabeeinbettung“ → Zwischenschichten messen, bevor etwas behauptet wird.
- „nicht auswertbar“: längeres Budget oder höhere lr in einem neuen Piloten.

## Ergebnis

(offen)

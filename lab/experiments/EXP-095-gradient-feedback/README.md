---
id: EXP-095
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-095: Braucht die frühe Festlegung frische Gradienten entlang des Wegs? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage nach EXP-093/094: Was macht die frühe Bewegung zielgenau?) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-094-evaluations-vs-window/README|EXP-094]], [[experiments/EXP-093-lag-clock-range/README|EXP-093]]

**Festgelegt vor jedem EXP-095-Lauf** (Sitzung 42, 2026-09-28; `design.py`, `analyze.py`, Selbsttest grün über den Wächter; Trainer-Option `--pre-switch-grad-every` neu in dieser Sitzung, Tests grün).

## Bezug und Frage

EXP-094: Bei Λ = 24 und in Λ angeglichenen Adam-Fenstern bleibt bei wenigen großen Schritten ein Rückstand, der mit c wächst (d8 = +0.174 bei 3 Schritten). Zwei Erklärungen sind dort nicht getrennt: **(E) Auswertungen / Rückkopplung:** Die frühe Bewegung wird zielgenau, weil der Gradient unterwegs neu ausgewertet wird. Die gerade wachsenden Zielkomponenten verstärken ihren eigenen Gradienten, und das ist eine Rückkopplung, die über die erste Ordnung hinausgeht. Wenige Auswertungen = wenig Rückkopplung. **(S) Adam-Schritt:** Der grobe Adam-Schritt selbst (β₁′ 0.2, β₂′ 0.84 über 3 Schritte, Überschießen) ist das Problem, nicht die Zahl der Auswertungen.

**Eingriff:** Arm gk macht die normalen 24 Adam-Schritte (Lernrate, β 0.9/0.98, Weight Decay unverändert), wertet den Gradienten vor dem Wechsel aber nur alle k Schritte neu aus (dazwischen derselbe gespeicherte Gradient). g8 hat also dieselben 3 Auswertungen wie c8b, aber feine Adam-Schritte. g24 nutzt nur den Anfangsgradienten: Das ist ein direkter Test, ob die erste Ordnung (Richtung am Start) für die Festlegung bis Λ = 24 reicht.

## Aufbau

Wie EXP-094 (add 113, ω = 0-Splitpaare, Wechsel A → B und B → A bei t, danach 2000 Standardschritte, π gegen reine Läufe; GPU). **Seeds 3470–3485** (frisch, Dateisuche 28.09. ohne Treffer). Zellen: **n24** (Standard), **g4**, **g8**, **g24** (je t = 24, Gradient alle k Schritte), **c8b** (c = 8, t = 3, β′ 0.2/0.84; Replikation aus EXP-094). 12 Läufe je Seed, **192 GPU-Läufe** (≈ 17 min mit 8 Workern wie EXP-094).

## Vorhersagen und Lesarten (verbindlich, im Code)

e_k = π(n24) − π(gk), d8 = π(n24) − π(c8b), r8 = π(g8) − π(c8b); gepaarte Bootstrap-KIs über Seeds (10 000, rng 95).
- **„nicht trennbar“:** KI-Untergrenze von d8 ≤ 0.03 (Rückstand aus EXP-094 repliziert nicht).
- **„Auswertungen zählen“** (E): KI-Untergrenze von e8 > 0.03 und mittleres e8 ≥ 0.5 · mittleres d8.
- **„Adam-Schritt“** (S): KI von e8 innerhalb ±0.05.
- sonst **„teilweise“**; < 10 gültige Seeds → *nicht auswertbar*.
- **Beschreibend:** e4, e24, r8, Ordnung e4 ≤ e8 ≤ e24; Zellmittel von π, Zielanteil f und Norm N beim Wechsel; prospektive Prüfung der Geraden π(f) aus EXP-092/093 (MAE).
- **Erwartung (vorab):** eher (E). Mit eingefrorenem Gradienten sind Adams Schritte innerhalb eines Blocks fast gleich (m̂ = g, v̂ = g² ab Start), also ähnlich einem großen Vorzeichen-Schritt. Deshalb sollte g8 nahe bei c8b liegen, und g24 sollte am schwächsten festlegen. Gegen (E) spräche g8 ≈ n24. Dann trüge bis Λ = 24 die erste Ordnung, und der c8b-Rückstand läge am groben Adam-Schritt.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-094 (d8 = +0.174, Lesart „teilweise“, Frage), EXP-093 (Λ = 24, Schwelle 0.03), R9 (β′-Regel), Post-hoc-Gerade π(f). Keine Seeds aus diesen Blöcken. Die Wahl von k ∈ {4, 8, 24} folgt den EXP-094-Zellen (6 und 3 Auswertungen) plus dem Extremfall.

## Befehle

```
python lab/experiments/EXP-095-gradient-feedback/design.py          # Splits (schon erzeugt)
python lab/tools/guarded_run.py -- python lab/experiments/EXP-095-gradient-feedback/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-095-gradient-feedback/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-095-gradient-feedback/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-095-gradient-feedback/analyze.py
```

## Ergebnis

Sitzung 42, 2026-09-28; Block 16:13–16:52 Berlin (Queue-Zeitstempel), 192/192 ok (6 Worker, GPU geteilt mit der Repro-Kette); `analyze.py` über den Wächter (16:52); `summary.json`. 16/16 Seeds gültig.
**Registrierte Lesart: „Auswertungen zählen“** (e8-KI-Untergrenze 0.060 > 0.03; e8 = d8).
- **e8 = π(n24) − π(g8) = +0.141** [0.060, 0.211] (13/16); **d8 = +0.141** [0.084, 0.194] (14/16; Replikation von EXP-094: +0.174); **r8 = π(g8) − π(c8b) = +0.000** [−0.036, 0.035] (10/16). Drei Gradientenauswertungen ergeben mit 24 feinen Adam-Schritten genau denselben Rückstand wie mit 3 großen Schritten.
- Dosis: **e4 +0.020** [−0.008, 0.050] (9/16, 6 Auswertungen reichen fast), **e8 +0.141**, **e24 +0.187** [0.111, 0.266] (13/16, nur der Anfangsgradient); Ordnung e4 ≤ e8 ≤ e24 erfüllt.
- Zellmittel π: n24 0.284, g4 0.263, g8 0.143, g24 0.097, c8b 0.143. Zielanteil f: 0.180 / 0.167 / 0.157 / 0.142 / 0.162. Norm N: 2.36 / 2.30 / 2.25 / **2.87** / 2.18. Mit dem Anfangsgradienten allein bewegt sich W_E *weiter*, aber am wenigsten zielgenau.
- **Prospektive Prüfung der Geraden π(f):** MAE 0.062. Ordnung getroffen, aber für die g-Zellen zu niedrig (g24: −0.05 vorhergesagt, 0.097 beobachtet). Der Zielanteil f ist nicht die ganze Zustandsgröße.

**Einordnung (Exploration, eine Aufgabe):** Der Rückstand großer Schritte bei angeglichenen Fenstern (EXP-094) liegt nicht am groben Adam-Schritt, sondern daran, wie oft der Gradient unterwegs neu ausgewertet wird. Die frühe Festlegung bis Λ = 24 braucht neu ausgewertete Gradienten entlang des Wegs. Ob über Selbstverstärkung der Zielkomponenten (Rückkopplung, vorab vermutet) oder über die Korrektur der veralteten Anfangsrichtung (Überschießen: g24 bewegt sich weiter, aber weniger zielgenau), ist nicht getrennt (Prüfung Sitzung 42). Der Anfangsgradient allein (erste Ordnung, [[paper/draft]] §5) legt nur schwach fest (π 0.10 gegen 0.28). Etwa alle 4 Schritte eine Auswertung genügt fast. **Grenzen:** r8 ≈ 0 vergleicht Zellen mit verschiedenem Adam-Zähler nach dem Wechsel (c8b 3, g8 24; der erste neue Gradient geht in m̂ mit 0.29 gegen 0.11 ein), kann also auch eine Aufhebung sein (Prüfung R10, Sitzung 42); Anzahl und Abstand der Auswertungen sind bei festem Λ nicht getrennt; W_E-Energiemaß; Adam mit eingefrorenem Gradienten macht fast vorzeichenartige Schritte, g24 ist also „erste Ordnung unter Adam“, nicht unter Gradientenfluss; eine Aufgabe (add 113), 16 Seeds, Pilot.

## Nachtrag a (Sitzung 42, 17:58 Berlin gemessen, post hoc an gesehenen Daten, Exploration): Welche Komponente der frühen Bewegung fehlt?

Skript `posthoc_components_s42.py` (Lesarten im Docstring vor dem Rechnen festgelegt und committet, 12093947); Ergebnis `posthoc_components_s42.json`. Gruppenleistung der Bewegung W_E(t) − W_E(0), getrennt nach Zielen T (fünf Ziele des ersten Splits) und Rest R, Verhältnis der Zellmittel zu n24 (geometrische Mittel je Seed mit KI fast gleich):
- **g24** (nur Anfangsgradient): T ×**1.12** [1.09, 1.13], R ×**1.48** [1.47, 1.49] → vorab festgelegte Lesart **„Korrektur fehlt“**: Die Ziele wachsen so stark wie mit frischen Gradienten, aber die übrigen Frequenzen wachsen fast um die Hälfte mehr (veraltete, fast vorzeichenartige Adam-Schritte bewegen alles).
- **g8** (3 Auswertungen): T ×**0.75** [0.73, 0.76], R ×**0.88** [0.86, 0.89]; **c8b**: T ×0.71, R ×0.81; **g4**: T ×0.87, R ×0.96. Hier wachsen vor allem die Ziele *weniger* (nach den Schwellen des Skripts wäre das „Selbstverstärkung fehlt“; für g8 nicht vorab als Lesart festgelegt, nur beschreibend).
- **Einordnung (Hinweis, kein Test):** Zwei Wege zur schwächeren Festlegung. Ohne jede Auffrischung bewegen sich die Nicht-Ziele zu stark, mit seltener Auffrischung wachsen die Ziele zu wenig. π folgt dabei nicht T allein (g24 hat das größte T, aber das kleinste π), sondern dem Verhältnis. Die engen KIs spiegeln kleine Streuung der Verhältnisse zwischen Seeds, nicht Unabhängigkeit von der Auswahl. Gesehene Daten; ein Test bräuchte frische Seeds (z. B. als beschreibender Zusatz in R10: f und N werden dort ohnehin berechnet).

## Nachtrag b (Sitzung 43, ≈ 18:26 Berlin (Skript-Commit 18:25), Fenster zu, post hoc an gesehenen Daten, nur numpy, Exploration): Ist g24 „erste Ordnung“ oder ein Vorzeichen-Artefakt?

Skript `posthoc_sign_s43.py` (Lesarten im Docstring vor dem Rechnen festgelegt und committet, 541ade73); Ergebnis `posthoc_sign_s43.json`. Mit eingefrorenem Gradienten sind Adams Momente exakt m̂ = g₀, v̂ = g₀², jeder Schritt ist also lr · sign(g₀) je Element. D = W_E(24) − (1 − lr·wd)²⁴ W_E(0).
- **P1 (Vorbedingung) erfüllt:** 99.9 % der g24-Einträge von D liegen innerhalb von 10 % der Einheit 0.0237 (reine Vorzeichenschritte). Bei n24 sind es auch 54 % (Adams erste Schritte sind ebenfalls fast vorzeichenartig).
- **P2:** Binarisiert man die n24-Bewegung (0.0237 · sign(D_n24)), fällt ihr Zielanteil f von 0.182 auf 0.160. g24 liegt bei 0.143. Die Binarisierung allein erzeugt also **56 % [53, 59]** der f-Lücke → vorab festgelegte Lesart **„teilweise“**.
- Beschreibend: Der Anteil der reinen dritten Harmonischen {3k} an der Nicht-Ziel-Energie ist in allen drei Fällen ≈ 9 % (n24 0.092, g24 0.093, binarisiert 0.092), etwa so viel wie bei Gleichverteilung (5/51). Die Streuung trifft also keine erkennbar harmonische Struktur.
- **Einordnung (Hinweis, kein Test):** Die Aussage „nur der Anfangsgradient legt schwach fest, die erste Ordnung trägt wenig“ ist etwa zur Hälfte mit Adams Vorzeichen-Quantisierung verwechselt. g24 ist „erste Ordnung unter signSGD“. Der Paper-Text nennt diese Einschränkung schon („nearly sign-like“), ihre Größe war aber unbekannt. Ersatzgröße: sign(D_n24) ist nicht sign(g₀). Trennender Versuch vorbereitet: [[experiments/EXP-097-sign-vs-staleness/README|EXP-097]] (2 × 2: Adam gegen linear normierte Schritte, frisch gegen nur Anfangsgradient, Adam-Zustand im Schatten).
- **Zusatz (beschreibend, `posthoc_signshare_cells_s43.py`):** Anteil reiner Vorzeichenschritte in D je Zelle (q) und mittleres |D|/Einheit: n24 0.54 / 0.78, g4 0.50 / 0.75, **g8 0.45 / 0.72**, g24 1.00 / 1.00, **c8b 0.33 / 0.68**. g8 und c8b sind *weniger* quantisiert als n24. Die Vorzeichen-Verwechslung betrifft also nur den g24-Arm (e24), nicht den Hauptkontrast e8 („Auswertungen zählen“) und nicht g8 ≈ c8b. Ein zusätzlicher linearer Arm mit 3 Auswertungen in EXP-097 ist deshalb nicht nötig.

## Nachtrag c (Sitzung 43, 18:41 Berlin gemessen, post hoc, numpy, Exploration): Sagt das Arkussinus-Gesetz die Streuung durch sign() voraus?

Skript `posthoc_arcsine_s43.py` (Lesart vor dem Rechnen festgelegt und committet, c64b2226); Ergebnis `posthoc_arcsine_s43.json`. Für einen gaußschen Prozess entlang der Token-Achse hat sign(x) die Autokorrelation (2/π)·arcsin(ρ) (Van Vleck). Daraus folgt das Spektrum von sign(D) allein aus dem Spektrum von D (Plausibilitätsprüfung: reiner Kosinus → Grundwellenanteil 0.811 = 8/π², wie bei der Rechteckwelle).
- Vorhersage für die binarisierte n24-Bewegung: f_pred = **0.148**, gemessen f_bin = **0.160** (Ausgang 0.182) → Fehler 0.012 → vorab festgelegte Lesart **„grob“** (≤ 0.01 wäre „erklärt“). Die Faustregel f ≈ (2/π) f + (1 − 2/π) · 5/56 liefert dasselbe (0.148).
- Das Gesetz überschätzt die Streuung. Plausibel ist, dass D_n24 nicht gaußsch ist: 54 % der Einträge sind schon volle Vorzeichenschritte, und bereits binäre Anteile verlieren beim Binarisieren nichts mehr.
- Nur als Hinweis (nicht festgelegt, nicht getestet): Die Vorhersage 0.148 liegt nahe am g24-Wert 0.143. Wäre die Richtung von g₀ so verteilt wie eine gaußsche Bewegung mit f ≈ 0.18, erklärte die Quantisierung fast die ganze Zielanteil-Lücke. Ob das so ist, zeigt EXP-097 (Q1).

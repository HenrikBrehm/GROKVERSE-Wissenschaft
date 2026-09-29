---
id: EXP-103
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen]
---
# EXP-103: Frühe Steuerungskurve des P1-Presets (dichte Spektren bis Schritt 250)

Zurück: [[LAB]] · [[FINDINGS]] (K2, R1) · [[NOVEL_DIRECTIONS]] N50 · Anlass: R1-Nachauswertung Sitzung 44 (`lab/confirm/R1_posthoc_lrwd_time_s44.py`, JOURNAL Zyklus 4)

**Stand:** vorbereitet (Sitzung 44, Fenster zu), ungetestet. Exploration, Füllarbeit mit niedriger Priorität (Regel 20: nach R10, neben L0, höchstens 2–4 GPU-Worker).

**Frage:** Die vier R1-Zellen mit geänderter Lernrate bzw. Weight Decay liegen ab τ = t·lr·wd/10⁻³ ≥ 250 innerhalb von ≈ 4 % auf der P1-Kurve Δ_pow(τ) (post hoc). Die vorab festgelegte Lesart war nur „teilweise“, weil die Punkte mit τ < 250 stark abwichen. Dort ist die P1-Kurve aber nur zwischen Schritt 0 und 250 linear interpoliert. Ist die Abweichung ein Interpolationsartefakt?

**Aufbau:** P1-Preset add 113, dieselben Seeds 1000–1049, Splits, Trainer (`freq_ban.py`), Gerät (cuda) wie P1, nur 250 Schritte mit Spektren bei 10, 25, 50, …, 250; eigener Ausgabeordner `raw` (Run-IDs enthalten die Schrittzahl nicht). 100 Läufe à 250 Schritte (`jobs.txt`), Minuten.

**Lesarten (vor jedem Lauf, `analyze.py`):** Prüfung: Δ_pow bei 250 muss je Seed mit dem gespeicherten P1-Wert übereinstimmen (±10⁻⁴), sonst „nicht vergleichbar“. **Artefakt:** alle vier frühen R1-Punkte (wd 0.3 bei τ = 75/150/225, lr 5e-4 bei τ = 125) mit |log(Zelle/P1_dicht(τ))| < 0.10. **Echt:** mindestens zwei > 0.20 (dann frühe Steuerung nicht in lr·wd, Vergleich mit Σ lr). Sonst unklar.

**Befehle:**
```
python lab/tools/parallel_queue.py lab/experiments/EXP-103-early-steering-curve/jobs.txt --workers 4
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-103-early-steering-curve/analyze.py
```

**Bereits gesehene Daten:** P1 (alle 50 Seeds, Schritte 0–2000 im 250er-Raster), R1 (alle Zellen, Schritte 0–2000), die Nachauswertung Sitzung 44. Die Zellwerte bei τ < 250 sind bekannt; unbekannt ist nur die dichte P1-Kurve.

**Fassung 2 (Sitzung 44, nach der unabhängigen Nachrechnung, vor jedem Lauf):** Zusätzlich beschreibend der Vergleich derselben vier Punkte mit der dichten Kurve in Σ lr (τ_lr = t·lr/10⁻³): Zwei-Phasen-Alternative des Prüfers (frühe, vom Weight Decay unabhängige Ausrichtung durch Adams lr-große Schritte, danach eine lr·wd-Drift). Das würde auch erklären, warum die Zellen mit kleinem lr·wd bei freier Anpassung 11–15 % „schneller“ laufen als lr·wd vorhersagt und warum lr 5e-4 und wd 0.3 bei t = 250 fast gleich sind (2.87/2.80). Ändert die Lesart oben nicht. **Nicht abgedeckt, für später:** eine gekreuzte Zelle mit gleichem lr·wd wie das Preset (z. B. lr 2e-3 mit wd 0.5), die Produktform lr·wd gegen getrennte Exponenten, und Läufe über 2000 Schritte (lr 2e-3 fällt nach Schritt 1500 wieder ab).

**Teil B (Sitzung 44, vor jedem Lauf): Produktform lr·wd.** Zwei gekreuzte Zellen mit demselben lr·wd wie das Preset: lr 2e-3 mit wd 0.5 und lr 5e-4 mit wd 2. P1-Seeds 1000–1009 mit ihren P1-Splits und derselben Init, 2000 Schritte, also **gepaart** mit den gespeicherten P1-Läufen (nur lr und wd verschieden). 40 Läufe (`jobs_cross.txt`, eigene Ausgabeordner `raw_x_*`). **Lesart** (`analyze.py --cross`): m = Mittel über t = 250…2000 von |log(Mittel_X(t)/Mittel_P1(t))|; „Produktform hält“, wenn m < 0.10 in beiden Zellen; „nicht nur das Produkt“, wenn m > 0.20 in einer Zelle (Richtung berichten); sonst unklar. Beschreibend: gepaarter log-Quotient je Seed bei 2000 mit KI. Befehl: `python lab/tools/parallel_queue.py lab/experiments/EXP-103-early-steering-curve/jobs_cross.txt --workers 4`, dann `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-103-early-steering-curve/analyze.py --cross`.
Teil B trennt auch die Zwei-Phasen-Alternative: Wenn die frühe Ausrichtung nur an Σ lr hängt, liegt lr 2e-3/wd 0.5 früh (t ≤ 500) über P1 und lr 5e-4/wd 2 darunter, obwohl lr·wd gleich ist; bei reiner lr·wd-Zeit liegen beide überall auf P1. Die Werte bei t = 250 und 500 werden dafür beschreibend berichtet.

**Teil B, Ergänzung (20:52, vor jedem Lauf):** Die gekreuzten Läufe zeichnen Spektren zusätzlich bei 10, 25, 50, 75, 100, 150, 200 Schritten auf. Beschreibend (ändert die Lesart nicht): Differenz Δ_pow(lr 2e-3/wd 0.5) − Δ_pow(lr 5e-4/wd 2) je Seed bei 10…200 Schritten mit KI. Bei gleicher lr·wd-Zeit sagt eine frühe Σ lr-Uhr (N51) eine positive Differenz voraus, reine lr·wd-Zeit keine. Anlass: Gegenhinweis in N51 (bei t = 250 wirkt Weight Decay schon).

**Reihenfolge der Lesung (Sitzung 44, vor jedem Lauf):** Teil B wird mit gespeicherten P1-Läufen gepaart, die mit einem älteren Stand von `freq_ban.py` gerechnet wurden (P1-Manifest). Ob der heutige Trainer im Standardpfad dieselben Zahlen liefert, zeigt die Prüfung in Teil A (Δ_pow bei Schritt 250 je Seed gleich ±10⁻⁴). **Teil B erst lesen, wenn Teil A diese Prüfung bestanden hat**; sonst Teil B nur beschreibend und die Paarung als eingeschränkt vermerken. Beide Teile lassen sich gemeinsam rechnen (Teil A ist in Minuten fertig).

**Worker (Sitzung 44, nach Konsistenzprüfung):** Die Zahl 4 in den Befehlen ist ein Höchstwert. Maßgeblich: alle GPU-Prozesse zusammen ≤ 10 (neben R11 mit 5 und L0 mit 5 ist kein Platz; dann warten). **Einordnung nach Regel 20a:** kein Mechanismus-Detailversuch zur Festlegung, sondern Anhang-Stütze für die Robustheit R1 im Paper (19a/20d) und GPU-Füllarbeit (20i).

**Vorsicht bei der Lesung von Teil A (Sitzung 44, 21:47, vor jedem Lauf):** Der Punkt wd 0.3 bei τ = 225 (Zellmittel 3.33) liegt über dem Preset bei Schritt 250 (3.22). Ist die dichte Preset-Kurve monoton, kann er nicht ganz ein Interpolationsartefakt sein; er zeigt dann einen echten Versatz von ≥ 3 %, wie ihn die Nachrechnung auch bei τ ≥ 250 fand (lr 5e-4 +5 bis +8 %, freie Anpassung: Zellen mit kleinem lr·wd laufen 11–15 % „schneller“). Die Lesart „Artefakt“ (alle vier Punkte innerhalb |log| < 0.10) schluckt solche Versätze. Deshalb zusätzlich berichten: die vorzeichenbehafteten log-Quotienten der vier Punkte; „Artefakt“ heißt nur „kein großer früher Bruch“, nicht „exakte lr·wd-Zeit“.

## Ergebnis (Sitzung 46, 2026-09-29, 03:05 Berlin; Exploration, nicht unabhängig nachgerechnet)

Teil A 100/100 und Teil B 40/40 (der fehlende Lauf von Sitzung 45 wiederholt), 0 Fehler. **Teil A:** Vergleichsprüfung bei Schritt 250 **exakt** (0 Abweichungen). Lesart **„unclear“**: |log(Zelle/P1-dicht)| wd 0.3 bei τ = 75: **0.73**, τ = 150: 0.050, τ = 225: 0.059; lr 5e-4 bei τ = 125: 0.068. Die Fehlanpassung bei τ < 250 war also für drei Punkte Interpolation, nicht aber für den frühesten (τ = 75, t = 250 bei wd 0.3). **Teil B:** Lesart **„product form holds“** (m < 0.10 in beiden Zellen über t = 250 … 2000); früh aber große gepaarte Unterschiede zwischen lr 2e-3/wd 0.5 und lr 5e-4/wd 2 bei gleichem lr·wd: t = 100 +1.83 [1.73, 1.94], 150 +1.18 [1.10, 1.27], 200 +0.34 [0.29, 0.40] (je 10/10). **Deutung (vorsichtig):** Ab ≈ 250 Schritten zählt die Steuerung in lr·wd; davor zählt die Lernrate allein (größere Schritte steuern früher) — passt zur Hypothese „zwei Uhren“ (N51). Für das Paper (Anhang A, R1-Absatz): „time rescaling in lr·wd holds from about 250 steps on; earlier, the learning rate alone sets the pace (EXP-103, exploration)“.

---
id: EXP-093
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/negativ, neu/kandidat]
---
# EXP-093: Bis zu welcher Lernrate gilt die Momentum-Verzögerungs-Uhr? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (K5, offene Mechanismusfrage) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-092-momentum-lag-clock/README|EXP-092]] · [[confirm/R9_REGISTRATION_DRAFT|R9]]

**Festgelegt vor jedem EXP-093-Lauf** (Sitzung 41, 2026-09-28, 14:29 Berlin gemessen; `design.py`, `analyze.py`, Selbsttest grün über den Wächter).

## Warum dieser Versuch (Bezug, Regel 15b)

EXP-092 stützte die Lag-Uhr Λ_eff = c·t − c·lag(β₁, t) in vier von fünf neuen Zellen (Abweichung ≤ 0.015), verfehlte aber c = 4, t = 6 deutlich (−0.107 [−0.16, −0.06]). Bevor K5 um die Lag-Uhr erweitert oder eine Bestätigung (R10) entworfen wird, muss ihr **Gültigkeitsbereich** bekannt sein. Kein Nachtrag zu EXP-092, sondern ein eigener Versuch mit frischen Seeds; c = 4 wird dabei repliziert.

## Aufbau

Wie EXP-092 (add 113, ω = 0-Splitpaare, Wechsel A → B und B → A, danach 2000 Standardschritte, π gegen reine Läufe; GPU). **Seeds 3420–3435** (frisch: Dateisuche 28.09. ohne Treffer). Eichung n20/n25/n30 (Standard); **Λ = 24 fest**, Lernratenfaktor c in den Schritten 1 … t: c2 (t = 12), c3 (8), c4 (6), c6 (4), c8 (3). 18 Läufe je Seed, **288 GPU-Läufe** (6 Worker neben dem Repro-Paket, erwartet ≈ 55 min).

Vorhergesagte relative Lage (Lag-Uhr, geeicht auf n25 = 0, n30 = 1): c2 −0.57, c3 −0.64, c4 −0.62, c6 −0.49, c8 −0.31 (n20 −0.95). Die Lag-Uhr sagt also für c2–c8 fast gleiche π, bei c8 sogar etwas höher (kürzeres Momentum-Fenster in Λ, weil nur 3 Schritte).

## Lesarten (verbindlich, im Code)

Je Zelle Residuum r_c = π(c) − Lag-Vorhersage (je Seed über n25/n30 geeicht), Bootstrap-KI. *trifft*: KI in ±0.03; *verfehlt*: KI-Obergrenze < −0.03 (oder Untergrenze > +0.03); sonst *offen*. Lesart über c2 … c8: **„Grenze zwischen c_a und c_b“** (erst nur *trifft*, dann nur *verfehlt*), **„keine Grenze bis c = 8“**, **„Uhr verfehlt schon bei c = 2“**, sonst **„gemischt“**. < 10 gültige Seeds → *nicht auswertbar*.
**Erwartung vor dem Lauf** (aus R9: c = 2 lag post hoc auf der Kurve; EXP-092: c = 4 darunter): Grenze zwischen c2 und c4, Residuum wachsend mit c. **Zwei Post-hoc-Kandidaten für den Fehlschlag** (nicht getrennt prüfbar mit diesem Aufbau, nur beschreibend): (a) Adams erste Schritte sind fast vorzeichenartig und unselektiv, ihr Anteil an Λ wächst wie ≈ 2/t → Residuum folgt 2/t; (b) Überschießen großer Schritte → Residuum folgt c. Hier sind c und 2/t fast gleich geordnet; ein trennender Test braucht eine Trainer-Option (z. B. erste k Schritte mit lr × 1, dann × c), die erst nach Prüfung gebaut wird.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-092 (Wahl der Frage, Λ = 24 wie dort c4, Schwelle ±0.03 wie dort), R9 (c = 2 post hoc auf der Kurve), EXP-091 (c = 2 stabil). Keine Seeds aus diesen Blöcken.

## Nachtrag a (Sitzung 41, 14:55 Berlin, während des Blocks, **vor dem Lesen jedes EXP-093-Ergebnisses**; beschreibend, ändert die Lesart nicht)

Zweites Modell zum Vergleich: **Lag + halber Schritt**. Jeder Schritt wendet seinen Gradienten c Λ-Einheiten lang an (Euler-Diskretisierung), das ergibt zusätzlich ≈ c/2 Verzögerung: x = c·t − c·lag(β₁, t) − c/2. Post hoc an EXP-092 (gesehen): c05 unverändert gut, c4-Residuum −0.107 → ≈ −0.07 (nur zum Teil erklärt). Relative Vorhersage (n25 = 0, n30 = 1): c2 −0.68, c3 −0.86, c4 −0.96, c6 −1.06, c8 −1.11 (reine Lag-Uhr: −0.57, −0.64, −0.62, −0.49, −0.31). Die beiden Modelle trennen sich vor allem bei c6/c8: Lag allein sagt dort *höhere*, Lag + c/2 *niedrigere* Festlegung als bei c4. Nach dem Lauf wird beschreibend die MAE beider Modelle über c2–c8 berichtet.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-093-lag-clock-range/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-093-lag-clock-range/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-093-lag-clock-range/jobs.txt --workers 6
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-093-lag-clock-range/analyze.py
```

## Ergebnis (Sitzung 41, 2026-09-28; Block 14:30–15:30 Berlin, 288/288 ok; `analyze.py` über den Wächter; `summary.json`)

16/16 Seeds gültig. **Registrierte Lesart: „gemischt“** (c2 *offen*, c3–c8 *verfehlt*; keine Zelle *trifft*).
- Residuum gegen die Lag-Uhr (je Seed geeicht): c2 **−0.039** [−0.074, −0.004], c3 −0.099 [−0.156, −0.045], c4 −0.132 [−0.185, −0.078] (repliziert EXP-092: −0.107), c6 −0.176 [−0.238, −0.113], c8 **−0.247** [−0.312, −0.182]; Eichprüfung n20 −0.044 [−0.092, +0.009]. Streng monoton in c (Spearman −1; ebenso gegen 2/t, beide Ordnungen fallen hier zusammen).
- Zellmittel π bei **festem Λ = 24**: c2 0.271, c3 0.204, c4 0.173, c6 0.143, c8 0.092 (n20 0.225, n25 0.373, n30 0.485). Die Lag-Uhr sagte für c2–c8 fast gleiche Werte voraus (c8 sogar leicht höher).
- **Selektivität und Größe der frühen Bewegung** (beschreibend): Norm ‖W_E(t) − W_E(0)‖ bei allen c fast gleich (2.31 → 2.27), Zielanteil fällt monoton (0.175 → 0.161; n25 0.186).
- **Nachtrag a (vorher notiert):** MAE über c2–c8 Lag-Uhr 0.138, Lag + c/2 0.093; beobachtete relative Lage (n25 = 0, n30 = 1): c2 −0.92, c3 −1.52, c4 −1.81, c6 −2.08, c8 −2.53 (Lag + c/2 sagte −0.68 … −1.11). Die Euler-Verzögerung erklärt also nur einen Teil.

**Einordnung (Exploration, negativ für die Lag-Uhr als allgemeines Gesetz):** Die Momentum-Verzögerungs-Uhr gilt in diesem Aufbau nur für c ≤ 1 (EXP-092: c = 0.5, β₁-Änderungen, t = 20) und knapp nicht mehr bei c = 2 (hier −0.04; in R9 lag c = 2 bei t = 15 post hoc auf der Kurve). Bei gleichem Λ gilt: **Je größer und seltener die Schritte, desto schwächer die Festlegung**, obwohl die Bewegung gleich groß ist. Sie ist nur weniger zielgenau. Das passt zur Tiefpass-Lesart aus Zyklus 3/4 in allgemeinerer Form: Die Zielgenauigkeit wächst mit der Zahl der *Gradientenauswertungen*, nicht nur mit Λ. Wenige große Schritte wenden frühe, breite Gradienten lange an. Offen und nicht getrennt: Diskretisierung (Lag + c/2 erklärt einen Teil), vorzeichenartige frühe Adam-Schritte, Überschießen. **Folgen:** K5 (R9) bleibt unberührt, betrifft aber nur c = 0.25 und c = 2 mit angeglichenen β. Die Lag-Uhr darf nicht als allgemeine Festlegungsuhr formuliert werden. Ein trennender Versuch braucht eine Trainer-Option (z. B. Gradienten k-mal pro großem Schritt neu auswerten = c Unterschritte à lr, gegen einen Schritt à c·lr bei gleichem Adam-Zustand) → nächste Sitzung vorbereiten, vorher prüfen. **Grenzen:** Pilot, 16 Seeds, eine Aufgabe, π = W_E-Energiemaß, lineare Eichung (Extrapolation bis −2.5 Eichabstände).

**Post hoc (Sitzung 41, 15:33, `posthoc_state_s41.py`/`.json`):** Über die 15 Zellmittel von EXP-092 und EXP-093 ist π fast linear im Zielanteil f der frühen Bewegung beim Wechsel (R² 0.93); die Norm N fügt fast nichts hinzu (R² 0.94; N allein 0.56). Das schließt die Fehlschläge der Lag-Uhr bei großem c ein. **Lesart (Hinweis, kein Befund):** Die Persistenz wird davon bestimmt, *wie zielgenau* die frühe Bewegung ist, nicht *wie weit* sie ging. Grenzen: Zellmittel (ökologisch), f und π sind beide W_E-Energiemaße auf denselben Zielmengen (gemeinsame Messbasis), post hoc. Prospektiv prüfbar: π in neuen Zellen aus f vorhersagen.

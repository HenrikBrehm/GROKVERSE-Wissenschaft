---
id: EXP-140
status: vorbereitet
datum: 2026-10-01
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-139-pair-count/README|EXP-139]]", "[[confirm/R5_REGISTRATION|R5]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-140: Generalisiert eine konstruierte Menge an der Datengrenze, wo eine gleich große Zufallsmenge es nicht tut? (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds je Zelle), keine Bestätigung.** Kontrollarm zu [[experiments/EXP-139-pair-count/README|EXP-139]].

**Bezug zu FINDINGS:** Kernaussage R5 (konstruierte Splits generalisieren ≈ 6–7× früher, bestätigt bei 30 % Daten, add 113/97, mul 113) und der LeDoux-Einwand (Regel 20b). LeDoux 2026 (§6.4) schreibt, die Bedeutung der Reihenfolge sinke mit der „Adäquanz des Inhaltssignals“; bei p = 9973 und 0.3 % generalisiert dort eine Zufallsteilmenge in i.i.d.-Reihenfolge gar nicht. Wenn eine spektral konstruierte Menge an unserer Datengrenze generalisiert, eine gleich große Zufallsmenge aber nicht, dann ersetzt Inhalt (welche Paare) dort Dichte – das wäre R5 an der Grenze und die Mengen-Seite von LeDoux' Satz. Begründung Regel 15b: kein Mini-Nachtrag, sondern die fehlende Kontrolle, ohne die EXP-139 nichts über „Konstruktion vs. Dichte“ sagt.

## Vorab (Sitzung 68, 2026-10-01, geschrieben 08:43–08:45 Berlin, vor jedem EXP-139- und EXP-140-Ergebnis; EXP-139: nur Status/Schritt gelesen)

- **Frage:** Generalisieren Zufallssplits (EXP-043-Konstruktion mit ε = 0, Arm R, genau N Paare) in den EXP-139-Zellen, in denen die konstruierten Arme F/G generalisieren?
- **Hypothese:** In Zellen nahe der Grenze generalisiert R im Budget (30 000 Schritte) nicht oder viel später („Konstruktion ermöglicht Generalisierung“ bzw. „beschleunigt“).
- **Konkurrenz:** gleiche Generalisierung wie E (Dichte allein entscheidet) → „kein klarer Unterschied“.
- **Zellenauswahl (Regel, vorab):** alle EXP-139-Zellen mit p ≤ 503, deren konstruierte Arme generalisieren (≥ 2 Seeds mit beiden Armen, `generalises` in EXP-139/summary.json). p = 613 ausgelassen (9 GB je Lauf, nur einer gleichzeitig).
- **Aufbau:** wie EXP-139, gleiche Seeds 13900–13902 (gleiche Init wie F/G), ein R-Lauf je Seed und Zelle, höchstens 30 000 Schritte.
- **Lesart je Zelle (`analyze.py`):** R generalisiert in ≤ 1 von 3 Seeds → „Konstruktion ermöglicht Generalisierung“; sonst Median über Seeds von gen_R / gen_E (gen_E = Mittel aus F und G desselben Seeds): > 1.5 → „Konstruktion beschleunigt“, < 1/1.5 → „Zufall schneller“, sonst „kein klarer Unterschied“; fehlende R-Läufe → „nicht auswertbar“. Gesamt: alle Zellen „ermöglicht“ → „Inhaltssignal ersetzt Dichte (im Budget)“, sonst „gemischt“.
- **Was dagegen spräche:** R generalisiert so schnell wie E.
- **Budget:** ≤ 6 Zellen × 3 Läufe; 401 ≈ 3.7 GB je Lauf (gemessen in EXP-139), 503 geschätzt ≈ 6 GB; 0.04 s/Schritt → ≤ 20–30 min je Lauf.
- **Grenzen:** 3 Seeds, ein Budget (ein abgebrochener Lauf beweist nicht, dass R nie generalisiert); R ist eine Zufallsteilmenge ohne Reihenfolge (Full-Batch) – kein Nachbau von LeDoux' Aufbau (Minibatch, 2 Schichten, p = 9973).
- **Bereits gesehen:** EXP-136/137, R5 (alle Ergebnisse); EXP-139 nur Status und Schrittzahl. Die Zellenauswahl hängt vom EXP-139-Generalisierungsausgang ab (Regel oben, vorab), nicht von R.

## Befehle

```
python lab/experiments/EXP-140-random-at-edge/make_jobs.py > lab/queue/staging/exp140_all.txt   # Abschnitte "=== <datei>" je p, getrennt ablegen
python lab/experiments/EXP-140-random-at-edge/make_jobs.py --check
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-140-random-at-edge/analyze.py [--selftest]
```

## Ergebnis

Offen (vorbereitet; startet, sobald EXP-139 p 401/503 ausgewertet ist).

---
id: EXP-121
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, lm-leiter, befund/unklar]
---
# EXP-121: Zufallsarm mit flachen Häufigkeiten im EXP-115-Block – schließt die Paarstruktur die Lücke im Sprachmodell?

Zurück: [[LAB]] · [[FINDINGS]] · Bezug [[experiments/EXP-119-lm-speed-r5/README|EXP-119]] (Zufallssplit R: Plateau ≈ 0.3), [[experiments/EXP-115-lm-flat-marginals/README|EXP-115]] (flache F/G-Splits), [[experiments/EXP-104-flat-marginal-splits/README|EXP-104]] (Konstruktion) · BACKLOG „LM2“ · [[JOURNAL]] Sitzung 54 Zyklen 6–8

**Bezug zu FINDINGS:** R5 (konstruierte Splits generalisieren früher) im LM, Programm A (Verallgemeinerung, Regel 20e). EXP-119 zeigt den Vorteil im LM, kann aber Paarstruktur und Zahl-Häufigkeiten nicht trennen. Pilot (Exploration, 2 Läufe), der den fehlenden Zufallsarm zum EXP-115-Block ergänzt; entscheidet, ob LM2 als Bestätigungsblock lohnt.

## Vorab (Sitzung 54, 23:29 Berlin gemessen, vor jedem Lauf)

- **Frage:** Generalisiert ein Split mit exakt flachen Häufigkeiten, aber *ohne* Zielbetonung in der Paarstruktur, im LM so schnell wie die flachen konstruierten Splits (EXP-115, Lücke 25–300 Schritte) oder bleibt er wie der Zufallssplit R (EXP-119) nach der Memorisation hängen?
- **Aufbau:** Rf = S(1, D) mit zufälliger Differenzmenge D (|D| = 34, rng [121, s]) und 500 Tauschzügen (EXP-104 `swap`), je EXP-104-Seed s = 3850/3851; Modell-Seeds 3950/3951 wie EXP-115 (gleiche Init, Text, Schablonen). Unveränderter Trainer `lm_stage2.py`, K = 19, Antwort-Verlust, 4000 Schritte (wie EXP-115). Split-Statistik (`splits/*.json`): n = 3842, jede Zahl in jeder Rolle 34-mal; Anteil der stärksten fünf Maskenfrequenzen 0.16 (F/G: 0.27–0.30).
- **Testmenge:** gemeinsame EXP-104-Testmenge minus Rf-Paare (3228 bzw. 3382 statt 4595 bzw. 4693 Fakten) – eine Teilmenge, nicht identisch mit der Testmenge von F/G.
- **Maß:** t_train, t_test = erster interpolierter Schritt mit Genauigkeit ≥ 0.5 (`EXP-119 analyze.cross`); Lücke = t_test − t_train; Endgenauigkeiten.
- **Lesarten (vorab):** Tor: t_train existiert in beiden Seeds, sonst „nicht gelernt (Budget)“. **„Paarstruktur schließt die Lücke“**: Rf erreicht t_test in keinem Seed bis 4000 (bzw. Lücke ≥ 1000 in beiden) → die Zielbetonung der Paarstruktur, nicht die flachen Häufigkeiten oder die S(1, D)-Bauart, macht F/G schnell. **„Flache Bauart reicht“**: Lücke ≤ 300 in beiden Seeds → schnell auch ohne Zielbetonung; der Plateau-Befund von EXP-119 R hinge dann an der ungleichmäßigen Paarstruktur eines gewöhnlichen Zufallssplits. Sonst **„unklar“**.
- **Was gegen die Hypothese („Paarstruktur schließt die Lücke“) spräche:** „Flache Bauart reicht“.
- **Grenzen, vorab:** 2 Läufe (Pilot); andere Testmenge als F/G; S(1, D) bleibt nach 500 Tauschzügen teilweise strukturiert; 4000 Schritte (ein zensierter Lauf beweist nichts über später). Der Vergleich mit EXP-115 F/G nutzt deren schon gesehene Lücken (89/152/300/25).
- **Budget:** ≈ 30–45 min je Lauf auf der GPU (3.5 GB), 2 parallel; über den Dienst (`lab/queue/inbox/37_exp121_flat_random.jobs`), harte Grenze 240 min.
- **Bereits gesehen:** EXP-115 (alles), EXP-119 (alles), EXP-104-Spielzeugergebnisse. Davon beeinflusst: Wahl des Pilots, Schwellen 300/1000.

**Befehle:** `python lab/experiments/EXP-121-lm-flat-random-arm/design.py --splits` (erledigt, 23:29) · `… --jobs > lab/queue/inbox/37_exp121_flat_random.jobs` · Auswertung: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-121-lm-flat-random-arm/analyze.py` (vor den Läufen geschrieben, Lesarten wie oben; Smoke ohne Läufe: „nicht auswertbar“, EXP-115-Lücken korrekt gelesen).

## Ergebnis (Sitzung 55, 30.09. 01:07 Berlin gemessen; 2/2 Läufe ohne Fehler, GPU-Dienst `37_exp121_flat_random`)

**Vorab-Lesart: „unklar“** (Tor erfüllt; Lücke 570 bzw. 223 Schritte: weder ≤ 300 in beiden noch ≥ 1000 in beiden).

| Modell-Seed / Split | t_train | t_test | Lücke | Train / Test am Ende (4000) |
|---|---|---|---|---|
| 3950 / s3850 Rf | 2209 | 2779 | 570 | 0.997 / 0.779 |
| 3951 / s3851 Rf | 2409 | 2631 | 223 | 1.000 / 0.985 |

Zum Vergleich (gesehen, EXP-115, gleiche Modell-Seeds, flache konstruierte F/G): Lücken 89, 152, 300, 25. EXP-119 (gewöhnlicher Zufallssplit R, andere Seeds): Plateau ≈ 0.3, Lücke ≥ 3900 (zensiert).

**Zusatzmessung (post hoc, Lesart vorab im JOURNAL S55 Zyklus 4; `commutativity_s55.py`/`.json`): „über Kommutativität hinaus“.** Zurückgehaltene Fakten mit Tauschpaar im Split 0.996 / 1.000, ohne 0.677 / 0.979.

**Deutung (Exploration, 2 Läufe):** Ein Zufallssplit mit exakt flachen Häufigkeiten bleibt im LM nicht auf dem Kommutativitäts-Plateau stehen, sondern generalisiert innerhalb von 223–570 Schritten nach der Memorisation, etwas langsamer als die flachen konstruierten Splits (25–300), aber um eine Größenordnung schneller als der gewöhnliche Zufallssplit R in EXP-119. Die Zielbetonung der Paarstruktur ist also nicht nötig, um das Plateau zu verlassen; eher hängt das R-Plateau an den ungleichmäßigen Zahl-Häufigkeiten oder der ungleichmäßigen Paarstruktur eines gewöhnlichen Zufallssplits. **Grenzen:** andere Seeds/Testmengen als EXP-119; S(1, D) bleibt nach 500 Tauschzügen teilweise strukturiert (Top-5-Anteil 0.16); R und Rf unterscheiden sich in mehr als den Häufigkeiten. **Folge für LM2:** Ein sauberer Test braucht im selben Block R, Rf und F/G mit denselben Modell-Seeds; die Frage lautet dann „Häufigkeiten oder Paarstruktur – was hält R auf dem Plateau?“.

**Korrektur der Deutung (Sitzung 55, 01:27; JOURNAL Zyklus 6, post hoc):** Rf ist nicht „ohne Betonung“. Die S(1, D)-Bauart konzentriert das M0-Maskenspektrum auch bei zufälligem D auf einzelne zufällige Frequenzen (Top-5-Anteil 0.16; größte Einzelfrequenz 2.5–2.7·10⁴ gegen 1.28–1.33·10⁴ beim gewöhnlichen Zufallssplit R von EXP-119 und 2.2–2.4·10⁴ bei dessen schnellen P1-F/G). Ungleichmäßige Häufigkeiten erklären das R-Plateau nicht (P1-F/G sind genauso ungleichmäßig, CV 0.13–0.16, und schnell). Lesart jetzt: Nicht die Wahl der Zielfrequenzen, sondern irgendeine Spektralspitze der Maske scheint nötig (post hoc, drei Blöcke, nicht direkt getestet). Der Satz „Die Zielbetonung der Paarstruktur ist also nicht nötig“ oben gilt nur im Sinn von „keine *gewählten* Ziele nötig“.

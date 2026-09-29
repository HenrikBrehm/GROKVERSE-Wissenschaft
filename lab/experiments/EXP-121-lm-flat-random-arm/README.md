---
id: EXP-121
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
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

---
id: EXP-088
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat, programm/C]
verwandt: ["[[experiments/EXP-087-planted-signal-mediation/README|EXP-087]]", "[[confirm/R5_REGISTRATION_DRAFT|R5]]", "[[NOVEL_DIRECTIONS]]", "[[FINDINGS]]", "[[JOURNAL]]"]
---
# EXP-088: Liegen datengesteuertes und eingepflanztes frühes W_E-Zielsignal auf *einer* Dosiskurve „Anteil bei 250 → Grokking-Zeit“?

Zurück: [[LAB]] · Vorgänger [[experiments/EXP-087-planted-signal-mediation/README|EXP-087]] (Pilot *unklar*, Kalibrierung überschoss) · [[confirm/R5_REGISTRATION_DRAFT|R5]] · [[NOVEL_DIRECTIONS]] N47 · [[JOURNAL]] Sitzung 39.

**Status:** vorbereitet, Sitzung 39 (2026-09-28, Entwurf ab 09:25 Berlin gemessen), **vor jedem EXP-088-Lauf**. Code `design.py` (Selbsttest grün 09:24 über den Wächter). Trainer unverändert seit c8b59b48 (`--plant-*`).

**Ziel in FINDINGS:** Programm C (mechanistische Vorhersage an unberührten Fällen) und Einordnung von R5: Ist die bestätigte Split-Beschleunigung vollständig über den frühen W_E-Zielanteil vermittelt? EXP-087 hat gezeigt, dass Einpflanzen allein reicht (×11), aber der Mediationstest war wegen der Dosis-Fehlanpassung formal unentschieden. Der saubere Test vergleicht beide Wege auf derselben Dosis-Achse.

## Konkurrenzmodelle

- **M-curve (gemeinsamer Mittler):** Die Grokking-Zeit hängt nur vom Zielanteil bei 250 ab, gleich woher er kommt. Eingriffsarme liegen auf der Kurve der Datenarme (Residuum ≈ 0).
- **M-data (Daten tragen mehr bei):** Die Splits wirken über den frühen Anteil hinaus (z. B. über die Paarstruktur während des Schaltkreisaufbaus). Eingriffsarme sind langsamer, als ihr Anteil vorhersagt (Residuum > 0).
- **M-plant (Eingriff wirkt stärker):** Das eingepflanzte Signal ist wirksamer als ein gleich großes gelerntes, z. B. weil es schon bei Schritt 0 da ist oder saubere Phasen hat. Residuum < 0. EXP-087 deutet post hoc leicht in diese Richtung (R+P 489 Schritte bei Anteil 0.40 gegen ≈ 550 interpoliert aus R5).

## Versuch

| Punkt | Festlegung |
|---|---|
| **Einheiten** | 20, Init-Seed 3230 + u (reserviert in [[FINDINGS_DETAILS]]); eigene Ströme `SeedSequence([20261088, u, …])` für Testmenge (20 %), Pool, R-Split, Zielmenge (5 aus k = 1..56), Wellenphasen und Schlüssel |
| **Arme (gleiche Init, Testmenge, Ziele)** | Datenarme **E2, E4, E8** (EXP-018/R5-Konstruktion, ε 2/4/8, gleiche Schlüssel und Phasen); Eingriffsarme **P1, P2, P4** = R-Split + eingepflanzte Zielleistung C × Median der Init-Leistung, C = 1/2/4 (`plant.py` aus EXP-087); **R** (nur beschreibend) |
| **Dosis-Überlappung** | C aus der EXP-087-Kalibrierung gewählt (C 0.5/2/8 → Anteil bei 250 0.14/0.40/0.62; R5: E2 0.30, E8 0.48), damit die Eingriffsarme im Bereich der Datenarme liegen (erwartet ≈ 0.28–0.52). Keine eigene Kalibrierung |
| **Lauf** | `freq_ban.py`, GPU, `--threads 1`, 8000 Schritte, `--stop-after-gen 8000`, W_E-Spektrum bei 250 |
| **Ereignis** | wie R5: Test ≥ 0.95 bei s, s + 25, s + 50 nach Train ≥ 0.99; b = min(Ereignis, 8000); y = log2 b; s = W_E-Zielanteil bei 250 |
| **Primär** | Datenkurve y = a_u + β·s, kleinste Quadrate über die drei Datenarme (Einheits-Achsenabschnitte, gemeinsame Steigung). Residuum eines Eingriffsarms = y − (a_u + β·s). Einheitswert r_u = Mittel der Residuen seiner **zulässigen** Eingriffsarme (Anteil im Bereich der Datenarme der Einheit ± 0.03; keine Extrapolation). Statistik: Mittel von r_u; Einheits-Bootstrap (20 000, Kurve je Stichprobe neu angepasst) |
| **Lesart (vorab, Äquivalenzgrenze 0.5 log2 ≈ ×1.41)** | 90-%-KI ganz in [−0.5, 0.5] → **gemeinsame Kurve** (M-curve gestützt, TOST mit α = 0.05 je Seite); sonst 95-%-KI-Untergrenze > 0.5 → **Eingriff langsamer als sein Anteil** (M-data); 95-%-KI-Obergrenze < −0.5 → **Eingriff schneller als sein Anteil** (M-plant); sonst **unklar**. Weniger als 15 Einheiten mit zulässigen Eingriffsarmen → *nicht auswertbar* |
| **Gültigkeit** | Jeder Lauf über den gemeinsamen Lader (Seed, Gerät, Schrittbudget, Split- und Testhash, endliches Spektrum bei 250) und die R5-Dichteprüfung; Init-Prüfsumme je Einheit gleich. Ein technischer Ausfall → ganzer Versuch *nicht auswertbar*. Eine Einheit mit zensiertem Daten- oder Eingriffsarm (kein Ereignis bis 8000) fällt aus der Primärauswertung und wird gezählt |
| **Sekundär (beschreibend)** | β und die Richtung (erwartet negativ); Mittel von r_u mit Vorzeichenanzahl; Anteil und geometrisches Zeitmittel je Arm; finale Top-5 auf den Zielen je Arm (steuert das Einpflanzen die Endwahl so stark wie die Daten?); Krümmung (quadratischer Term der Datenkurve) |
| **Budget** | 7 Arme × 20 Einheiten = 140 GPU-Läufe à 8000 Schritte; bei 8 Workern ≈ 3 Läufe/min (R4, Sitzung 39) → ≈ 50 min |
| **Was dagegen spräche (M-curve)** | Residuen deutlich ≠ 0: Dann hängt die Zeit nicht nur vom frühen Anteil ab, und der Anteil ist kein vollständiger Mittler |
| **Grenzen** | Der Anteil bei 250 wird *nach* dem Eingriff gemessen; bei den Eingriffsarmen enthält er den eingepflanzten Teil (das ist gewollt: gleiche Dosis-Achse), aber die Dosis entsteht auf verschiedenen Wegen (bei Schritt 0 gesetzt oder bis 250 gelernt). Die eingepflanzten Richtungen sind zufällig, nicht gelernt. Eine Architektur, add 113. Lineare Datenkurve über einen schmalen Anteilsbereich. Äquivalenz heißt „innerhalb ×1.41“, nicht Gleichheit |

## Nachtrag a (Sitzung 39, vor jeder Auswertung; Läufe gestartet ≈ 09:31, kein Ergebnis gelesen)

Nach der Vorab-Prüfung (Claude-Agent, nur lesend; kein Blocker):
1. **Kurvenform:** Die R5-Punkte sind in log2 b gegen s konvex. Eine lineare Datenkurve verschiebt die Residuen je nach Lage um bis zu ≈ ±0.17 (in der Mitte negativ, an den Rändern positiv). **Registrierte Sensitivitätsanalyse:** je Einheit die stückweise lineare Kurve durch ihre drei Datenarme (keine gemeinsame Steigung; jenseits der Enden wird das Endsegment verlängert, höchstens 0.03 durch die Zulässigkeit). Dieselbe Lesart mit Bootstrap über Einheiten. **Weichen primäre und Sensitivitätslesart voneinander ab, lautet das Urteil „abhängig von der Kurvenform“.**
2. **Schätzer:** Die Kurve wird auf allen unzensierten Einheiten angepasst, im Punktschätzer wie in jeder Bootstrap-Stichprobe. Resampelt werden alle unzensierten Einheiten, gemittelt wird r_u über die zulässigen.
3. **Tragweite:** P1 und P4 liegen voraussichtlich oft am Rand des Datenbereichs. Das Urteil stützt sich deshalb vor allem auf P2. Residuen je Eingriffsarm werden beschreibend berichtet. P1/P2/P4 teilen je Einheit dieselben Richtungen (nur die Skala unterscheidet sich) und sind nicht unabhängig.
4. **Grenzen ergänzt:** Messfehler in s schwächt β um ≈ 5–10 %; am Rand verschiebt das die Residuen um ≈ 0.05. Das Ereignisgitter (25 Schritte ≈ 0.14 log2 bei b ≈ 250) kann P4 am Boden abflachen.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-087 (Seeds 3200–3212, Pilot und Kalibrierung, alle Arme gesehen), R5 (Seeds 2720–2779, Anteil und Zeit je Arm, post hoc innerhalb der Arme). Beeinflusst: Wahl der Dosis-Achse (Anteil bei 250), der C-Werte (aus der EXP-087-Kalibrierung), der ε-Werte (Bereich der R5-Arme), der Äquivalenzgrenze (EXP-087: R+P gegen E2 −0.63 log2 bei um 0.09 höherem Anteil; die R5-Kurve fällt um ≈ 1.3 log2 je 0.18 Anteil) und die Zulässigkeitsregel (keine Extrapolation). Die Richtung des EXP-087-Befunds (Eingriff leicht schneller) ist bekannt. Deshalb ist die Primärfrage zweiseitig (Äquivalenz), nicht einseitig. Keine Läufe mit den Seeds 3230–3249.

## Befehle (nur im Fenster, alles über den Wächter)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-088-common-dose-curve/design.py --selftest
python lab/tools/guarded_run.py -- python lab/experiments/EXP-088-common-dose-curve/design.py --splits
python lab/experiments/EXP-088-common-dose-curve/design.py --jobs > lab/experiments/EXP-088-common-dose-curve/jobs.txt
python lab/tools/parallel_queue.py lab/experiments/EXP-088-common-dose-curve/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-088-common-dose-curve/design.py --analyze
```

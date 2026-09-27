---
id: EXP-062
status: laufend
datum: 2026-09-27
tags: [exp/laufend, befund/positiv, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[experiments/EXP-061-grad-alignment/README|EXP-061]]", "[[confirm/N28_REGISTRATION|N28]]", "[[JOURNAL]]"]
---
# EXP-062: Erhaltene alte oder unterdrückte neue Frequenzen? Zwei Regime der Persistenz (Exploration + vorab festgelegte Vorhersage)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B: *was* macht die Wahl fest?) · Daten aus [[experiments/EXP-059-momentum-exposure/README|EXP-059]] und EXP-056 (keine neuen Läufe) · Vorgänger [[experiments/EXP-061-grad-alignment/README|EXP-061]].

## Teil 1: Exploration (Sitzung 22, 07:50 gemessen, Seeds 400–409, post hoc)

Zerlegung des Zählers von π (L_switch − L_rein-Y) in zwei Teile, exakt additiv (`analyze.py`):
**a** = log E_alt(Wechsel) − log E_alt(rein Y) (erhaltene alte Energie), **b** = log E_neu(rein Y) − log E_neu(Wechsel) (fehlende neue Energie), jeweils am Ende (Y-Schritt 2000).

| t | 10 | 15 | 20 | 25 | 30 | 35 | 50 |
|---|---|---|---|---|---|---|---|
| a (Ende) | 0.09 | 0.49 | 1.39 | 2.12 | 2.57 | 3.06 | 3.66 |
| b (Ende) | 0.03 | 0.08 | 0.15 | 0.26 | 0.43 | 1.22 | **4.25** |

- **Bis t ≈ 30: Koexistenz.** Die alten Frequenzen bleiben erhalten und wachsen mit (bei t = 25 etwa e^2.1 ≈ 8× mehr alte Energie als im reinen Y-Modell), die neuen wachsen fast wie ohne Vorgeschichte (b klein).
  Das Netz nutzt am Ende beide Mengen.
- **Ab t ≈ 35–50: Ausschluss.** Jetzt fehlen die neuen Frequenzen (bei t = 50 etwa e^4.25 ≈ 70× weniger). Der Sprung von π auf ≈ 1 kommt vom Ausschluss der neuen Frequenzen, nicht nur vom Erhalten der alten.
- Je Seed: a25 > b25 in 10/10; b50 − b25 > 0.5 in 10/10 (Minimum 1.47).
- **Einordnung:** Das passt zu EXP-061 (der Gradient der neuen Daten baut die alte Struktur erster Ordnung ab): Die alte Wahl wird nicht durch den neuen Gradienten verstärkt, sondern sie bleibt,
  und ab einem Punkt blockiert sie das Entstehen der neuen. Warum (Kapazität unter Weight Decay, Rest des Netzes schon auf die alten Frequenzen eingestellt) ist offen.

## Teil 2: Vorhersage an den frischen N28-Seeds (festgelegt VOR jedem Blick auf N28-Ergebnisse)

Festgelegt 2026-09-27 (Sitzung 22), während der N28-Block lief und bevor irgendeine N28-Auswertung, ein N28-Spektrum oder ein N28-π angesehen wurde. Code: `lab/confirm/n28_regimes.py`
(liest nur gebundene N28-Läufe; Arme normal@25, normal@50, rein A, rein B). **Außerhalb der Holm-Familie**, eigene Zählregel.

- **V1 (Koexistenz bei t = 25):** a25 − b25 > 0 in ≥ 24 von 30 Seeds.
- **V2 (Ausschluss bei t = 50):** b50 − b25 > 0.5 in ≥ 24 von 30 Seeds.
- **Urteil:** beide → ***zwei Regime bestätigt (Vorhersage)***; genau eine → ***teilweise***; keine → ***nicht bestätigt***; ein fehlender oder nicht gebundener Lauf → ***nicht auswertbar***.
- **Bereits gesehene Daten:** EXP-062 Teil 1 (Seeds 400–409), aus dem Schwellen (24/30, 0.5) und Zeitpunkte stammen.

```
python lab/tools/guarded_run.py -- python lab/confirm/n28_regimes.py          # nach dem N28-Block
```

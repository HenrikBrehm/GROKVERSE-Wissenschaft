---
id: EXP-068
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[confirm/N29_REGISTRATION|N29]]", "[[experiments/EXP-064-functional-regimes/README|EXP-064]]", "[[confirm/P2d_REGISTRATION|P2d]]", "[[JOURNAL]]"]
---
# EXP-068: Reagiert das Netz auf alte und neue Frequenzen gleich, wenn der Eingriff gleich groß ist? (EXPLORATION, keine neuen Läufe)

Zurück zu [[LAB]] · [[FINDINGS]] K4c (offene Frage: Funktion ohne Energie?) · Modelle aus [[confirm/N29_REGISTRATION|N29]] (dort mit anderem Maß ausgewertet).
Festgelegt 2026-09-27 (Sitzung 23), **vor der Rechnung**. **Exploration**, kein Urteil.

- **Anlass:** In N29 und EXP-064 zeigen vollständige Ablation und absolute W_E-Energie immer in dieselbe Richtung. Ist die Empfindlichkeit des Netzes also nur eine Frage der Energie, oder reagiert es
  auf die „genutzte“ Menge auch **je Einheit** stärker?
- **Maße je Endmodell (80 N29-Modelle) und Menge S ∈ {alt, neu}:**
  (i) *gleiche Schrittnorm* (P2d-Maß): W' = W − δ·u_S, u_S = P_S W / ‖P_S W‖, δ = 0.02·‖W‖; Abfall des Logit-Abstands auf der Testmenge des Seeds.
  (ii) *gleiche entfernte Energie:* aus beiden Mengen dieselbe absolute Energie E = 0.5·min(E_alt, E_neu) entfernen (Skalierung der Koeffizienten, EXP-051 `remove_energy`); Abfall des Logit-Abstands.
- **Kennzahl je Lauf:** log(Abfall_dominant / Abfall_schwach), dominant = Menge mit größerer Energie. Zusammenfassung je t (25, 50): Median, Anteil > 0.
- **Lesart (vorab):** Liegt die Kennzahl bei (ii) nahe 0, ist die Empfindlichkeit „nur Energie“ (gleiche Energie, gleiche Wirkung). Deutlich > 0 bei (ii): Das Netz reagiert auf die dominante Menge auch je
  Energieeinheit stärker (Hinweis auf funktionale Nutzung über die Energie hinaus). Bei (i) ist wegen der Amplitudengewichtung von u_S ein Vorteil der dominanten Menge ohnehin zu erwarten.
- **Grenzen:** bekannte Modelle (N29 schon ausgewertet), eine Dosis, Abfälle können ≤ 0 sein (dann Kennzahl nicht definiert, Anteil berichten), nur W_E.
- **Budget:** 80 Modelle, CPU-Vorwärtsrechnungen, wenige Minuten.

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-068-matched-sensitivity/analyze.py
```

## Ergebnis (Sitzung 23, Rechnung 10:22–10:23 Berlin, gemessen; `summary.json`): Exploration

80 gebundene N29-Modelle. Kennzahl log(Abfall dominant / Abfall schwach), nur wo beide Abfälle > 0:

| Wechsel | Maß | definiert | Median | Anteil > 0 | Median Abfall dominant / schwach |
|---|---|---|---|---|---|
| t = 25 | gleiche Schrittnorm | 36/40 | +0.65 | 97 % | 0.248 / 0.091 |
| t = 25 | gleiche entfernte Energie | 36/40 | **−0.28** | 42 % | 0.713 / 1.571 |
| t = 50 | gleiche Schrittnorm | 34/40 | +2.55 | 100 % | 0.285 / 0.014 |
| t = 50 | gleiche entfernte Energie | 32/40 | **−0.18** | 44 % | 0.025 / 0.019 |

- **Lesart (Exploration):** Bei gleicher Schrittnorm gewinnt die dominante Menge, wie wegen der Amplitudengewichtung von u_S zu erwarten. Bei **gleicher entfernter Energie** gibt es **keinen Vorteil
  der dominanten Menge**; bei t = 25 schadet das Entfernen derselben Energie aus der *schwachen* (alten) Menge sogar mehr (1.57 gegen 0.71). Dort ist das aber die Hälfte ihrer Energie, bei der dominanten
  ein kleiner Bruchteil: Das Maß vertauscht nur die Dosisgeometrie (wie P2c). **Ein „Funktion über die Energie hinaus“ zeigt keines der beiden Maße.**
- **Folgerung für FINDINGS:** Die funktionalen Aussagen K2-Funktion (P2d) und K4c beschreiben Empfindlichkeit, die mit der Energie- bzw. Amplitudenverteilung in W_E einhergeht. Welcher Anteil
  darüber hinausgeht, ist mit Ablationen dieser Art nicht zu trennen (absolute Dosis gegen relative Dosis). Eine saubere Trennung bräuchte einen Eingriff, der die Energie konstant hält und nur die
  Richtung (z. B. Phase) der Frequenzkomponenten ändert.
- **Grenzen:** bekannte Modelle, eine Dosis je Maß, Abfälle teils ≤ 0.

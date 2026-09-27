---
id: EXP-065
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv]
verwandt: ["[[FINDINGS]]", "[[confirm/P2c_REGISTRATION|P2c]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-065: P2d-Pilot: lokale Empfindlichkeit je gleicher Schrittnorm (EXPLORATION, keine neuen Läufe)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm A) · [[BACKLOG]] „P2d“ · Modelle aus [[confirm/P2c_REGISTRATION|P2c]] (schon für R gesehen, für dieses Maß nicht).
Festgelegt 2026-09-27 (Sitzung 22), vor der Rechnung. **Exploration**: kein Urteil, dient nur der Planung von P2d.

- **Maß:** Je Modell (P2c, 4000 Schritte, gebunden) und Menge S (eigene 5 Ziele; 4 Kontrollmengen aus je 5 Frequenzen, zufällig aus der P2-Kontrollmenge, RNG fest je Seed):
  u_S = P_S W / ‖P_S W‖ (W = W_E[:113]); W' = W − δ·u_S mit gleichem δ für alle Mengen, δ = 0.02·‖W‖.
  Größe: Abfall des mittleren Logit-Abstands (richtige Klasse minus beste falsche) auf der gemeinsamen Testmenge, float64. Kennzahl je Modell: log(Abfall_eigen / Mittel Abfall_Kontrolle), nur wenn beide > 0.
- **Umfang:** die ersten 40 geeigneten P2c-Seeds (Basis-Genauigkeit ≥ 0.9 in beiden Armen), beide Arme.
- **Frage für die Planung:** Ist die Empfindlichkeit entlang der eigenen Ziele je Schrittnorm größer als entlang gleich großer Kontrollmengen? Streuung → Stichprobe für P2d.

## Ergebnis (Sitzung 22, 09:14–09:15 Berlin, gemessen; `summary.json`) — Exploration

80 Modelle (40 Seeds × 2 Arme). Abfall des Logit-Abstands bei gleicher Schrittnorm (δ = 2 % von ‖W_E‖):
**eigene Ziele im Median 0.25 (Minimum 0.136), Kontrollen (Mittel von 4 gleich großen Mengen) im Median 0.0007 (Spanne −0.006 … 0.037)**. Eigene > Kontrolle in **80/80** Modellen;
je Seed Differenz 0.254 ± 0.038 (n = 40, Minimum 0.188). Das Log-Verhältnis ist nur für 46/80 definiert (Kontrollabfall sonst ≤ 0), dort 4.45 ± 1.16 (≈ 85-fach).
- **Lesart (Exploration):** Je Parameterschritt gleicher Größe reagiert das Netz entlang der gesteuerten Frequenzen um Größenordnungen empfindlicher als entlang gleich großer Kontrollmengen.
  Das spricht dafür, dass die Umkehrung in P2c an der Dosisgeometrie lag (2.4 % gegen 50 % der jeweiligen Energie), nicht an fehlender Nutzung. Belegt ist das erst mit einer vorab festgelegten Bestätigung (P2d).
- **Grenzen:** dieselben Modelle wie P2c (dort schon ausgewertet), Maß nach dem P2c-Ergebnis gewählt, ein δ, lokale Größe (erste Ordnung), Kontrollen zufällig aus der P2-Kontrollmenge.
- **Für P2d:** Effekt riesig und einheitlich; schon 10–20 frische Seeds reichen für jede sinnvolle Schwelle. Primär z. B. Differenz der Abfälle (immer definiert) statt Log-Verhältnis.

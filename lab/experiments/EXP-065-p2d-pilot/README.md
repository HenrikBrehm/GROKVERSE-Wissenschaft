---
id: EXP-065
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
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

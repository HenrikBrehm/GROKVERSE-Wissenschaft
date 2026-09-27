---
id: C2-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/B]
verwandt: ["[[FINDINGS]]", "[[confirm/R2_REGISTRATION_DRAFT|R2]]", "[[confirm/C1_REGISTRATION|C1]]", "[[JOURNAL]]"]
---
# C2: Behalten die alten Ziele nach einem Wechsel bei t = 50 ihre Rangfolge vom Wechselzeitpunkt? (Programm B, feine Persistenz)

Zurück zu [[FINDINGS]] (Programm B) · Datenquelle: [[confirm/R2_REGISTRATION_DRAFT|R2]] (frische Seeds 2510–2539, noch **kein** Lauf). Registriert Sitzung 28 (2026-09-27, ≈ 17:05 Berlin),
vor jedem R2-Lauf; gilt mit dem Commit dieser Datei.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- N29 (Seeds 2250–2269, beide Richtungen, t = 25/50; gesehen) → Exploration `lab/confirm/N29_posthoc_within.py`, Ergebnis `N29_posthoc_within.json`. Rangkorrelation über die fünf **alten** Ziele
  zwischen W_E-Energie beim Wechsel und am Ende (t + 4000): t = 50: 0.58 (p < 5·10⁻⁵, 40 Läufe), t = 25: 0.17 (p 0.03). Spektrum des ersten Splits bei t = 50: 0.37; Spektrum des
  zweiten Splits an den alten Zielen: 0.02 (n. s.). Je Seed (Mittel beider Richtungen) bei t = 50: Mittel 0.580, SD 0.283, 19/20 positiv.
- **Davon beeinflusst:** Wahl des Prädiktors (Energie beim Wechsel), t = 50 als primärer Zeitpunkt, Mindesteffekt 0.10 und die Power-Rechnung.
- Ein erster Lauf des Explorationsskripts hatte die B→A-Läufe mit vertauschten alt/neu-Rollen gelesen; korrigiert vor jeder Deutung (Zahlen oben sind korrigiert).

## Aussage C2

Nach einem Datenwechsel bei t = 50 behalten die fünf alten Zielfrequenzen im Endmodell (t + 4000) die Rangfolge ihrer W_E-Energie vom Wechselzeitpunkt, auch bei lr 2e-3 und bei wd 0.3.
Deutung, falls bestätigt: Die Festlegung erhält nicht nur die Menge der alten Frequenzen (K4/K4c), sondern auch ihre innere Ordnung. Das ist beschreibende Persistenz, kein Mechanismus.

## Daten, Maß, Test (fest)

- **Daten:** alle R2-Läufe mit Wechsel bei t = 50 (Zellen lr2 und wd03, je 30 Seeds × beide Richtungen = 120 Läufe), geladen über den eingefrorenen R2-Lader (nur gültige Läufe).
- **Maß je Lauf:** Spearman über die fünf alten Ziele (Ziele des ersten Splits) zwischen der W_E-Gruppenenergie (`group_power`, add 113) im Snapshot bei Schritt t und bei t + 4000.
  **Einheit = Seed:** Mittel über alle gültigen t = 50-Läufe des Seeds (bis zu 4: zwei Zellen × zwei Richtungen; dieselbe Init).
- **Primärtest:** einseitiger Vorzeichen-Permutationstest Mittel > 0 (200 000 Ziehungen), α = 0.05; 95-%-Bootstrap-KI über Seeds (10 000). **Bestätigt** = p < 0.05 **und**
  KI-Untergrenze ≥ 0.10. Eigene Familie (Programm B, eine Hypothese), nicht in der R2-Holm-Familie. **Nicht auswertbar**, wenn weniger als 20 Seeds mindestens einen gültigen t = 50-Lauf haben.
- **Power:** N29-Streuung (SD 0.283 je Seed bei zwei Läufen) bei halbiertem Mittel (0.29): n = 30 → Power ≈ 0.92 (Bootstrap-Simulation); mit vier Läufen je Seed eher höher.
- **Beschreibend (kein Test):** je Zelle getrennt; t = 12 und t = 25 (Zelle lr2) bzw. t = 25 (wd03); Prädiktoren Spektrum des ersten Splits und Spektrum des zweiten Splits an den alten Zielen;
  dasselbe für die neuen Ziele.
- **Was dagegen spräche:** Mittel ≤ 0 oder KI-Untergrenze < 0.10.

## Umsetzung

Kein neues Training: die Auswertung liest R2-Läufe (Snapshots bei t und t + 4000 sind in den R2-Jobzeilen enthalten: `--spectra-at t,t+250,t+2000,t+4000`). Das Auswerteskript
`lab/confirm/C2_analyze.py` wird **vor** dem Öffnen der R2-Ergebnisse geschrieben und committet und ändert nichts an Maß, Einheit, Test oder Schwellen. Wird R2 geändert, muss C2 neu registriert werden.

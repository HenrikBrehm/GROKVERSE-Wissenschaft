---
tags: [lab/live]
---
# LIVE: Laborsitzung 41

- **Sitzungsstart:** 2026-09-28 13:20 Berlin (11:20Z, vom Runner)
- **Deadline:** 2026-09-28 16:19 Berlin (14:19Z)
- **Zuletzt aktualisiert:** 13:35 Berlin
- **Run-Fenster:** heute bis 18:00 (Deadline früher).

## Gerade

GPU rechnet zwei Dinge parallel: (1) das **Reproduktionspaket** fürs Paper vollständig (9 Skripte, Log `repro_s41.log`), (2) **EXP-092** (256 Läufe): Sagt eine „Momentum-Verzögerungs-Uhr“ die frühe Festlegung in neuen Einstellungen voraus? Währenddessen: K5 in FINDINGS.

## Als Nächstes

EXP-092 auswerten (Schätzung ≈ 14:20, 6 Worker neben dem Repro-Paket), Repro-Zahlen mit FINDINGS vergleichen.

## Verlauf dieser Sitzung

- 13:33 **Neu (Nachauswertung R9):** Eine kürzere Momentum-Verzögerung macht die frühe Bewegung *zielgenauer* (+13.6 % Zielanteil), mehr Trainingszeit macht sie vor allem *größer* (+19 % Norm). Beides nicht dasselbe.
- 13:32 EXP-092 vorab festgelegt, Smoke ok, Block gestartet.
- 13:27 Reproduktionspaket gestartet (Hinweis des Nutzers: GPU nicht leer laufen lassen).
- 13:26 Paper §3.15 (R9) + Abstract geschrieben, unabhängig geprüft; Literaturfehler korrigiert (Malladis Regel ist 1−β ∝ lr², nicht ∝ lr).
- 13:20 Start: kein STOP, Fenster offen, keine Python-Prozesse.

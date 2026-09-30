---
tags: [lab/live]
---
# LIVE: Laborsitzung 59

- **Sitzungsstart:** 2026-09-30 10:49 Berlin (08:49Z, vom Runner)
- **Deadline:** 2026-09-30 13:49 Berlin (11:49Z)
- **Zuletzt aktualisiert:** 11:20 Berlin (gemessen)

## Gerade

- Ein unabhängiger Prüfagent liest den EXP-128-Code (SGD mit Clipping), bevor die 16 GPU-Läufe beim Dienst drankommen.
- Ein letzter CPU-Kontrolllauf (sortierte Reihenfolge, Zufallsinit) rechnet noch zu Ende (≈ 11:30).

## Als Nächstes

- Prüfbefunde einarbeiten. Danach: LM3 und R12 weiter beobachten (LM3 11/20, R12 74/200, 0 Fehlschläge).

## Verlauf dieser Sitzung

- 11:18 Gradiententest mit echter Trainingsreihenfolge: Weder das vortrainierte Pythia noch ein zufällig gestartetes LM zeigen im ersten Schritt die gewünschten Frequenzen. Das Vortraining ist also nicht die Erklärung (Korrektur der Deutung von heute früh).
- 11:15 Fehler gefunden: Der Gradiententest von heute früh hat die Fakten sortiert eingelesen, das Training mischt sie. Sein Ergebnis gilt deshalb nur für sortierte Reihenfolge.
- 11:02 EXP-128: Kalibrierung gemessen (Clipping-Wert 0.017 nach vorab festgelegter Regel), zweiter Arm 0.1, Pilot beim Dienst eingereiht (16 Läufe, nach EXP-125).
- 10:50 Start: STATE, JOURNAL und Dienststatus gelesen; Fenster offen.

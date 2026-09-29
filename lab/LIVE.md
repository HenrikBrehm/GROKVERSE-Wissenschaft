---
tags: [lab/live]
---
# LIVE: Laborsitzung 50

- **Sitzungsstart:** 2026-09-29 11:30 Berlin (09:30Z, vom Runner)
- **Deadline:** 2026-09-29 14:29 Berlin (12:29Z)
- **Zuletzt aktualisiert:** 12:32 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## Gerade

- Bestätigungsblock **LM1** vorbereitet (10 frische Seeds: steuert die Faktenauswahl die Zahl-Embeddings eines kleinen Sprachmodells, wenn es die Fakten lernt?). Smoke läuft beim GPU-Dienst, unabhängige Prüfung läuft; danach einfrieren und einreihen (≈ 4–5 h Rechenzeit im Dienst).
- GPU-Dienst sonst: R4 ≈ 50/240, EXP-113 Läufe 1–2 bei ≈ Schritt 8000.

## Als Nächstes

Prüfbefunde einarbeiten → Manifest + Commit (Einfrieren) → 20 Läufe einreihen.

## Verlauf dieser Sitzung

- 12:28 **EXP-114: Verdünnung nicht gestützt**; aber: lernt das LM die Fakten, steuert die Auswahl deutlich (Δ_pow 5.6, zurückgehaltene Fakten 0.98; 1 Seed).
- 12:09 EXP-114 (79 % Rechensätze): Lauf F lernt die Fakten schon bei Schritt 2000 (Training 0.80, zurückgehalten 0.33); EXP-113 (34 %) bei Schritt 6500 noch auf Zufall.
- 11:49 EXP-114 vorab festgelegt (Lesarten + Auswertecode vor dem Lauf) und eingereiht.
- 11:46 Zweite unabhängige Prüfung eingearbeitet (Abb. 4: falsche Mindesteffekt-Linie entfernt).
- 11:46 Auswertecode für H-folgt vor dem Ergebnis geschrieben und an Pilotdaten getestet.
- 11:43 LM-Checkpoints angesehen: bis Schritt 4000 keine Steuerung (Δ_pow ≈ 0); Vorhersage „H-folgt“ vorab festgelegt.
- 11:41 Nachauswertung N54b: kleine Päckchen verschieben das Festlege-Fenster, verbreitern es nicht (Exploration).
- 11:39 Literatur-Nachsuche: nichts Vorwegnehmendes; Khanh 2026b als Grenze zitiert.
- vor 11:39 Kurzfassung 4 944 → ≈ 4 300 Wörter, unabhängig geprüft (9 Korrekturen); Abb. 4 neu (L0 + N54b); Tabelle 1 um R10/R11/L0/N54b ergänzt.
- 11:33 Lage geprüft (kein STOP, Fenster offen, Dienst läuft).

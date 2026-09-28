---
tags: [lab/live]
---
# LIVE: Laborsitzung 43

- **Sitzungsstart:** 2026-09-28 18:19 Berlin (16:19Z, vom Runner)
- **Deadline:** 2026-09-28 21:19 Berlin (19:19Z)
- **Zuletzt aktualisiert:** 18:34 Berlin
- **Run-Fenster:** zu (heute bis 18:00). Ab 29.09. 00:00–13:00. Diese Sitzung trainiert und testet nicht.

## Gerade

Warte auf die unabhängige Prüfung des EXP-097-Codes (Trainer-Patch + Auswertung). Daneben: Paper-Absatz zu EXP-095 um die Vorzeichen-Einschränkung ergänzen.

## Als Nächstes

Prüfbefunde einarbeiten; danach Paper §4 (EXP-095-Grenze quantifizieren) mit unabhängiger Prüfung.

## Verlauf dieser Sitzung

- 18:36 JOURNAL, LAB, BACKLOG, FINDINGS, NOVEL_DIRECTIONS nachgeführt.
- 18:32 **EXP-097 vorbereitet** (Veraltung gegen Vorzeichenschritt, 2 × 2, 160 GPU-Läufe). Designfehler vor dem Lauf behoben (leerer Adam-Zustand hätte den Boden getroffen). Trainer-Option als Patch, weil R10 den Trainer-Hash bindet.
- 18:26 **Nachtrag b zu EXP-095:** Mit eingefrorenem Gradienten macht Adam reine Vorzeichenschritte; das erklärt ≈ 56 % [53, 59] des Selektivitätsverlusts von g24 („teilweise“).
- 18:25 STATE.md auf 51 Zeilen gekürzt.
- 18:22 EXP-096: Splits/Jobs/Smoke erzeugt und committet (nur numpy).
- 18:21 Start: kein STOP, keine Prozesse, Wächter verweigert (Exit 3, Fenster zu). Stand gelesen.

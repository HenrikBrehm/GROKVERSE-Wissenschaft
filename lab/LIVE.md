---
tags: [lab/live]
---
# LIVE: Laborsitzung 43

- **Sitzungsstart:** 2026-09-28 18:19 Berlin (16:19Z, vom Runner)
- **Deadline:** 2026-09-28 21:19 Berlin (19:19Z)
- **Zuletzt aktualisiert:** 18:39 Berlin
- **Run-Fenster:** zu (heute bis 18:00). Ab 29.09. 00:00–13:00. Diese Sitzung trainiert und testet nicht.

## Gerade

Nachprüfung der geänderten EXP-097-Punkte läuft (Agent, nur lesend). Danach nächste Denkfrage: Was folgt aus EXP-095/097 für die Theorie im Paper (§5)?

## Als Nächstes

Prüfbefund einarbeiten; dann Nacht-Checkliste in STATE final prüfen.

## Verlauf dieser Sitzung

- 18:38 EXP-097 Fassung 2 nach Prüfung (kein Blocker; W_E-Token-Block normiert, primär sA, relativer Boden, schärferer Test). Paper §4 nach Prüfung korrigiert (1 Zahl: 45 % statt 46 %).
- 18:35 Nur g24 ist Vorzeichenabstieg; g8 und die großen Schritte sind weniger quantisiert als normal → Hauptbefund „Auswertungen zählen“ nicht direkt betroffen.
- 18:36 JOURNAL, LAB, BACKLOG, FINDINGS, NOVEL_DIRECTIONS nachgeführt.
- 18:32 **EXP-097 vorbereitet** (Veraltung gegen Vorzeichenschritt, 2 × 2, 160 GPU-Läufe). Designfehler vor dem Lauf behoben (leerer Adam-Zustand hätte den Boden getroffen). Trainer-Option als Patch, weil R10 den Trainer-Hash bindet.
- 18:26 **Nachtrag b zu EXP-095:** Mit eingefrorenem Gradienten macht Adam reine Vorzeichenschritte; das erklärt ≈ 56 % [53, 59] des Selektivitätsverlusts von g24 („teilweise“).
- 18:25 STATE.md auf 51 Zeilen gekürzt.
- 18:22 EXP-096: Splits/Jobs/Smoke erzeugt und committet (nur numpy).
- 18:21 Start: kein STOP, keine Prozesse, Wächter verweigert (Exit 3, Fenster zu). Stand gelesen.

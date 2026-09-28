---
tags: [lab/live]
---
# LIVE: Laborsitzung 43

- **Sitzungsstart:** 2026-09-28 18:19 Berlin (16:19Z, vom Runner)
- **Deadline:** 2026-09-28 21:19 Berlin (19:19Z)
- **Zuletzt aktualisiert:** 19:00 Berlin
- **Run-Fenster:** zu (heute bis 18:00). Ab 29.09. 00:00–13:00. Diese Sitzung trainiert und testet nicht.

## Gerade

Nachtplan steht (R10 → R11 + EXP-096 + EXP-098 → EXP-097). Ich prüfe noch einmal die Befehlsfolge in STATE auf Lücken.

## Als Nächstes

Abschlussbericht vorbereiten; bis zur Deadline weitere Denkarbeit.

## Verlauf dieser Sitzung

- 19:00 R9 nachgesehen: Beim K5-Effekt ist die frühe Bewegung mit kurzen Adam-Fenstern kaum vorzeichen-quantisiert und selektiver (36/36), bei lr × 2 nicht (Hinweis).
- 18:58 FINDINGS wieder auf eine Seite gebracht (Historie wortgleich nach FINDINGS_DETAILS). Paper-Folgen der Nachtergebnisse vorab festgelegt.
- 18:57 EXP-098 geprüft (kein Blocker), Offenlegungen ergänzt.
- 18:54 **EXP-098 vorbereitet** (K5 bei anderen Aufgaben). Abb. 9 (R9) fürs Paper erstellt. R11 nach Prüfung Fassung 2 (kein Blocker).
- 18:50 Neue Kandidatenidee N49: Adam in Fourier-Koordinaten für W_E (Vorzeichen je Frequenz statt je Token). Nachtplan geordnet: R10 → R11 + EXP-096 → EXP-097.
- 18:47 **R11 vorbereitet**: Bestätigung der frühen Festlegung bei add 97 / mul 113 (n = 30, Power ≥ 0.89 bei halbem Effekt).
- 18:42 Arkussinus-Gesetz sagt die Vorzeichen-Streuung grob voraus (0.148 statt 0.160).
- 18:38 EXP-097 Fassung 2 nach Prüfung (kein Blocker; W_E-Token-Block normiert, primär sA, relativer Boden, schärferer Test). Paper §4 nach Prüfung korrigiert (1 Zahl: 45 % statt 46 %).
- 18:35 Nur g24 ist Vorzeichenabstieg; g8 und die großen Schritte sind weniger quantisiert als normal → Hauptbefund „Auswertungen zählen“ nicht direkt betroffen.
- 18:36 JOURNAL, LAB, BACKLOG, FINDINGS, NOVEL_DIRECTIONS nachgeführt.
- 18:32 **EXP-097 vorbereitet** (Veraltung gegen Vorzeichenschritt, 2 × 2, 160 GPU-Läufe). Designfehler vor dem Lauf behoben (leerer Adam-Zustand hätte den Boden getroffen). Trainer-Option als Patch, weil R10 den Trainer-Hash bindet.
- 18:26 **Nachtrag b zu EXP-095:** Mit eingefrorenem Gradienten macht Adam reine Vorzeichenschritte; das erklärt ≈ 56 % [53, 59] des Selektivitätsverlusts von g24 („teilweise“).
- 18:25 STATE.md auf 51 Zeilen gekürzt.
- 18:22 EXP-096: Splits/Jobs/Smoke erzeugt und committet (nur numpy).
- 18:21 Start: kein STOP, keine Prozesse, Wächter verweigert (Exit 3, Fenster zu). Stand gelesen.

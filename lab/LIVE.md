---
tags: [lab/live]
---
# LIVE: Laborsitzung 43: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 18:19 Berlin (16:19Z, vom Runner)
- **Deadline:** 2026-09-28 21:19 Berlin (19:19Z)
- **Zuletzt aktualisiert:** 20:09 Berlin
- **Run-Fenster:** zu; laut Regel 20 **durchgehend ab heute 23:59 bis 06.10.** (Wächter geprüft). Diese Sitzung trainiert nicht.

## Gerade

**Sitzung beendet** (20:09). Keine Läufe aktiv. Abschlussbericht im JOURNAL.

## Als Nächstes

Nächste Sitzung **21:54 Berlin** (Runner). Läufe ab **23:59**: R10 fertig, Nanda (CPU), dann L0 (EXP-100) und R11 als GPU-Füllarbeit.

## Verlauf dieser Sitzung

- 20:09 Sitzung beendet. Zuletzt: L0-Bestätigungsgerüst (geprüft), Tomàs Bernal im Volltext geprüft, Zenodo-Scan, Abb. 11 vorbereitet.
- 20:00 Abschlussbericht. Nachtplan geprüft (1 Blocker behoben). Nanda-Skript deckt jetzt auch mul 113 ab (geprüft, 1 Blocker behoben). Abb. 10 (R5).
- 19:38 Kurzfassung: Einleitung + Ergebnisse 1–3 + Grenzen (≈ 2900 Wörter), Zahlen unabhängig bestätigt, viele Vorbehalte ergänzt.
- 19:30 EXP-100 (L0) Fassung 2 nach Prüfung (eigene Ausgabeordner, Machbarkeitstest, fb30k).
- 19:29 Paper-Schnittplan (≤ 8 Seiten) mit gemessenen Umfängen; Nanda-Skript und RFM-Code für Regel 20c vorbereitet.
- 19:24 EXP-100 (L0): Splits, Trainer-Patch (geprüft, kein Blocker) und Auswertung stehen.
- 19:14 **Regel 20 übernommen**: EXP-096 bis EXP-099 zurückgestellt, R10 läuft zu Ende, L0 hat Priorität. Erste tägliche Erklärung geschrieben.
- 19:09 **EXP-099 vorbereitet** (Adam in Fourier-Koordinaten für W_E, neue Trainer-Option als Patch hinter EXP-097).
- 19:04 R9-Nachauswertung korrigiert: Das Maß hängt an der Toleranz, und die Lesart bleibt „unklar“. Die EXP-095-Aussage ist bei allen Toleranzen stabil. N49 hat jetzt zwei konkurrierende Vorhersagen.
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

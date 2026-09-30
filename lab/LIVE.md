---
tags: [lab/live]
---
# LIVE: Laborsitzung 59

- **Sitzungsstart:** 2026-09-30 10:49 Berlin (08:49Z, vom Runner)
- **Deadline:** 2026-09-30 13:49 Berlin (11:49Z)
- **Zuletzt aktualisiert:** 13:25 Berlin (gemessen)
- **Status: Sitzung beendet.** Nächster Start laut Runner: 30.09. 14:24 Berlin (vorläufig, der Runner setzt ihn neu).

## Gerade

- Keine Sitzung aktiv. Der GPU-Dienst rechnet weiter: LM3 14/20 (+3), R12 129/200 (+4), danach Pythia-Pilot EXP-127, EXP-125, EXP-128.

## Als Nächstes

1. LM3 und R12 auswerten, sobald fertig (Deutungssätze liegen bereit). 2. EXP-127, dann EXP-128 auswerten. 3. Nach R12: Clipping-Patch in freq_ban.py übernehmen.

## Verlauf dieser Sitzung

- 13:25 Sitzungsende; Dienst ohne Fehlschläge.

- 12:04 Literatur-Nachsuche vor dem Paper-Ziel: 3 neue Arbeiten, keine schränkt unsere Kernaussagen ein.
- 12:02 Vergleichswert gemessen: Im kleinen Spielzeugmodell zeigt die erste Lernrichtung die Wunschfrequenzen genauso deutlich (1.28/1.45) wie das LM mit einem Fakt je Zeile.
- 12:01 Pythia-Aufbau frisch gestartet: Wunschfrequenzen wieder an der Spitze → das Hemmnis ist eher das Vortraining (nach Vorab-Regel „unklar“).
- 11:56 Kurzfassung oben in der heutigen Tageserklärung; One-Pager-Prüfpunkte übernommen.

- 11:48 Unabhängige Prüfung aller heutigen Notizen: Zahlen richtig; 2 Fehler (Beschreibung des Clipping-Arms C_B) und mehrere zu starke Formulierungen korrigiert.
- 11:46 Test: Ein Fakt mit Text davor zeigt die Wunschfrequenzen weiter; Text stört nicht, nur andere Fakten. Meine Erklärung von 11:35 war damit falsch.
- 11:40 One-Pager auf den heutigen Stand gebracht (Minibatch, kleines Sprachmodell).

- 11:38 Paper-Sätze für jeden möglichen EXP-128-Ausgang vorab festgelegt ([[paper/EXP128_DEUTUNGEN]]).
- 11:37 STATE, FINDINGS (Explorationsnotiz), BACKLOG aktualisiert; Tageserklärung 30.09. korrigiert.
- 11:35 Gespeicherte LM-Läufe: bei Schritt 1000 nirgends Steuerung, egal wie viele Fakten je Zeile („unklar“ nach Vorab-Regel). Diese Mechanismus-Linie ist damit geschlossen.
- 11:32 Mit nur einem Fakt je Zeile zeigt ein zufällig gestartetes LM im ersten Schritt genau die fünf Wunschfrequenzen, das vortrainierte Pythia nicht. Es gibt also zwei getrennte Bremsen.
- 11:30 EXP-128-Codeprüfung: keine Blocker; Smoke für den zweiten Clipping-Wert nachgeholt.

- 11:18 Gradiententest mit echter Trainingsreihenfolge: Weder das vortrainierte Pythia noch ein zufällig gestartetes LM zeigen im ersten Schritt die gewünschten Frequenzen. Das Vortraining ist also nicht die Erklärung (Korrektur der Deutung von heute früh).
- 11:15 Fehler gefunden: Der Gradiententest von heute früh hat die Fakten sortiert eingelesen, das Training mischt sie. Sein Ergebnis gilt deshalb nur für sortierte Reihenfolge.
- 11:02 EXP-128: Kalibrierung gemessen (Clipping-Wert 0.017 nach vorab festgelegter Regel), zweiter Arm 0.1, Pilot beim Dienst eingereiht (16 Läufe, nach EXP-125).
- 10:50 Start: STATE, JOURNAL und Dienststatus gelesen; Fenster offen.

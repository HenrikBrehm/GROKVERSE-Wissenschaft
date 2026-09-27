---
tags: [lab/live]
---
# LIVE: Laborsitzung 24

- **Sitzungsstart:** 2026-09-27 12:29 Berlin (10:29Z, vom Runner)
- **Deadline:** 2026-09-27 15:29 Berlin (13:29Z)
- **Zuletzt aktualisiert:** 14:13 Berlin (gemessen)
- **Run-Fenster:** seit 13:00 zu (wieder ab 00:00): nur Denk- und Vorbereitungsarbeit.

## Gerade

Ein Pruef-Agent gleicht alle Zahlen im Paper-Entwurf gegen die eingefrorenen Quellen ab. In lab/paper/STATUS.md steht oben eine deutsche Kurzfassung: was das Paper heute tragen wuerde und was vor einer Einreichung fehlt.

## Als Naechstes

Abweichungen korrigieren, Sitzung beenden. Ab 00:00: Tests, EXP-040, P2f, EXP-073/074/075 (siehe [[STATE]]).

## Verlauf dieser Sitzung

- 14:13 Paper: fuenf Abbildungen als Skripte, Kurzfassung fuer dich in [[paper/STATUS]].
- 14:08 Robustheitsblock R1 (gilt die Steuerung auch bei anderer Lernrate, anderem Weight Decay, anderem Trainingsanteil?) vorbereitet und von Codex geprueft; rechnen fruehestens in der Nacht 28./29.09.
- 13:53 Literatur fuer das Paper fertig (lab/paper/related_work.md, ~50 Arbeiten, zur Pruefung durch dich oder eine Fachperson). Abbildungen 1-4 als Skripte; Trainer kann jetzt Lernrate, Weight Decay und Trainingsanteil variieren (Robustheit, ab 00:00 getestet).
- 13:44 Preprint-Arbeitsbereich angelegt ([[paper/STATUS]]): Entwurf, Robustheitsplan, Abbildungen 2 und 3; Entscheidungen zu Autorschaft, Einreichung und Venue liegen bei dir.
- 13:38 EXP-076 (Theorie-Rechnung): Das Maskenspektrum ist nicht der Nutzen im einfachsten AGF-Modell (negativ).
- 13:35 Literatur: Eine neue ICML-2026-Arbeit (Marchetti, Kunin et al.) erklaert die Irrep-Reihenfolge ueber die Eingabekodierung bei gleichverteilten Daten; unsere Steuerung ueber die Auswahl der Trainingspaare ist dort nicht abgedeckt.
- 13:33 P2f bekommt eine zweite, vorab festgelegte Frage: Sagt die fruehe Konzentration auf die eigenen Irreps (Schritt 2000) voraus, wann D59 grokt? (Hinweis aus EXP-072: rho = -0.75.)
- 13:26 EXP-075 festgelegt: legt sich die Wahl auch in einem Netz ohne Attention frueh fest? EXP-040 (Amplitudenmodell) kommt heute Nacht zuerst dran.
- 13:20 EXP-074 festgelegt (Reset-Muster bei anderen Aufgaben); Referenz add 113 nachgerechnet: Attention-Reset nimmt die Festlegung fast ganz weg, MLP-Reset kaum.
- 13:16 Codex: Korrekturen am neuen Werkzeug ohne Beanstandung.
- 13:06 EXP-073 vorab festgelegt (Teil-Zurueckspulen; Neuheitssuche: Werkzeug an sich bekannt, Anwendung nicht gefunden).
- 13:00 FINDINGS wieder auf einer Seite (Details wortgleich in FINDINGS_DETAILS); STATE und LAB aktualisiert.
- 12:58 P2f (D59-Bestaetigung) registriert, Codex: keine Blocker; Einfrieren ab 00:00.
- 12:47 D59-Funktionsmass an den Pilotmodellen: D = 0.22, 5/5 positiv (post hoc).
- 12:46 **EXP-072:** D59 generalisiert (9/10), die gesteuerten Irreps tragen danach fast die ganze Energie.
- 12:40 EXP-072 Zwischenstand: D59 generalisiert doch, meist zwischen 3000 und 7000 Schritten (5 von 10 Laeufen bei Schritt 6000 schon ueber 0.99).
- 12:39 **EXP-071 (Exploration): unklar, schwacher Hinweis.** Seeds mit staerker ausgerichtetem Wertepfad beim Wechsel haengen etwas fester an der ersten Wahl (r = 0.45, p = 0.09, n = 10); den zeitlichen Verlauf erklaert das Mass nicht besser als die Schrittzahl.
- 12:37 EXP-072 festgelegt und gestartet (D59 generalisiert in P1 nie: 0/100 nach 2000 Schritten).
- 12:33 EXP-071 festgelegt und gestartet.
- 12:30 Stand gelesen, kein STOP, keine laufenden Prozesse; CPU-Programm gestartet.

---
id: paper-R12-deutungen
status: vorbereitet
datum: 2026-09-30
tags: [lab/paper]
verwandt: ["[[paper/draft_short]]", "[[confirm/R12_REGISTRATION_DRAFT|R12]]", "[[confirm/R5_REGISTRATION_DRAFT|R5]]"]
---
# R12: Deutungssätze je Ausgang, vor jedem Ergebnis festgelegt (Sitzung 57, 2026-09-30, ≈ 06:12 Berlin)

Zurück: [[paper/STATUS]] · Registrierung [[confirm/R12_REGISTRATION_DRAFT|R12]] (eingefroren 8e6f9b3f) · Lesart maschinell in `lab/tools/confirm_r12.py --analyze`.
Zweck wie [[paper/LM1_DEUTUNGEN]]: Die Deutung jedes Ausgangs steht fest, bevor die Läufe ausgewertet sind. Beim Einsetzen nur Zahlen ergänzen (2^L̄ mit KI, n, p_Holm, Anzahl bestimmter Einheiten mit richtiger Reihenfolge); Abweichungen vom Wortlaut im JOURNAL begründen. **Stand beim Schreiben:** keine R12-Auswertung gesehen; gesehen sind nur die zwei Smoke-Logzeilen (Seed 4299, nicht im Block).

**Ort im Paper:** Kurzfassung §4 (Result 2) als letzter Absatz „Other tasks“, dazu §7 (ii) *Scope* (der Halbsatz „R4, R5 and Result 3 hold for addition mod 113 in one architecture only“ wird angepasst) und eine Zeile in Tabelle 1. Kein neuer Kernsatz (Regel 20a); das Abstract wird nur geändert, wenn beide Aufgaben H-ER **und** H-ED bestätigen (dann „… in three tasks“ statt „in addition mod 113“), sonst nicht.

## Je Aufgabe (add 97 bzw. mul 113), vier Ausgänge

- **H-ER und H-ED bestätigt:** *In a pre-registered replication on {task} (R12, 20 fresh units), engineered splits again generalized earlier than the random split (×… [CI]) and than the per-output-matched control (×… [CI]; Holm over four tests, p … / …).*
- **H-ER bestätigt, H-ED nicht:** *On {task} engineered splits generalized earlier than random splits (×… [CI]), but not detectably earlier than the per-output-matched control (×… [CI], p_Holm …). On this task the speed-up may therefore run through the output distribution of the engineered mask; the within-output arrangement is supported only for addition mod 113.* Hinweis im Text: für H-ED gab es auf diesen Aufgaben keinen Pilot, n = 20 ist keine Poweranalyse → „not detectably“, nie „no effect“.
- **H-ED bestätigt, H-ER nicht:** *On {task} engineered splits generalized earlier than the matched control (×… [CI]) but not detectably earlier than random splits (×… [CI]).* Dann ausdrücklich: Das ist ungewöhnlich (die Kontrolle war bei add 113 langsamer als Zufall) und wird beschreibend mit den Medianen je Arm berichtet; keine weitere Deutung.
- **Beide nicht bestätigt:** *On {task} the pre-registered replication did not confirm the speed-up (R vs E ×… [CI], D vs E ×… [CI]); Result 2 is specific to addition mod 113 in our data.* Grenze in §7 (ii) bleibt, mit Verweis auf R12.

## Beide Aufgaben zusammen

- Gleicher Ausgang auf beiden Aufgaben → ein gemeinsamer Satz.
- Verschiedene Ausgänge → *The speed-up depends on the task: …* (beide Aufgaben einzeln, keine Mittelung über Aufgaben).
- **„nicht auswertbar“** (fehlender/defekter Lauf, Identitätsverletzung): nur technischer Vermerk; Läufe identisch neu einreihen, bevor irgendetwas berichtet wird.

## Beschreibend (unabhängig vom Ausgang)

- Anteil beobachteter Ereignisse je Arm bis 2000/8000 und Median der beschränkten Zeiten; bei vielen zensierten R-/D-Läufen ausdrücklich: *bounded times make the ratios conservative*.
- W_E-Zielanteil bei 250 nur für add 97 (wie R5: Läuft die Beschleunigung über das frühe Zielsignal?), ohne Kausalsprache.

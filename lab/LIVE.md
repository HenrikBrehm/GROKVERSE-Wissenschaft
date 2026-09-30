---
tags: [lab/live]
---
# LIVE: Laborsitzung 60

- **Sitzungsstart:** 2026-09-30 13:29 Berlin (11:29Z, vom Runner)
- **Deadline:** 2026-09-30 16:29 Berlin (14:29Z)
- **Zuletzt aktualisiert:** 15:55 Berlin (gemessen)
- **Status: Sitzung beendet.** Nächster Start laut Runner: 30.09. ≈ 17:04 Berlin (vorläufig, der Runner setzt ihn neu).

## Gerade

- Keine Sitzung aktiv. Der GPU-Dienst rechnet weiter: LM3-F (Funktionstest, CPU, ≈ 2 × 2 h), Pythia-Pilot EXP-127, dann EXP-125, EXP-128, EXP-129.

## Als Nächstes

1. LM3-F auswerten, sobald fertig. 2. Paper: R12 ins Abstract („in three tasks“), Tabelle 1, Abbildung. 3. EXP-127 auswerten.

## Verlauf dieser Sitzung

- 16:00 **R12 ins Paper** (Abschnitt 4, Einleitung, Grenzen); Prüfer fand einen Zählfehler von mir (vertauschte Anzahlen), korrigiert.
- 15:52 **R12 bestätigt:** Konstruierte Datensätze beschleunigen das Grokking auch bei Addition mod 97 (×4.5) und Multiplikation mod 113 (×7.4), je 20/20; unabhängig nachgerechnet.
- 15:50 **LM3 ins Paper** (Anhang K, Abschnitt 7), unabhängig geprüft.
- 15:45 **LM3 bestätigt:** Auch bei nur ≈ 8.7 % Rechen-Tokens steuert die Faktenauswahl die Zahl-Einbettung (Δ_pow 5.99 [4.64, 6.99], 20/20 lernen); unabhängig nachgerechnet. Funktionstest LM3-F eingereiht.

- 14:15 Literatur zur Schritt-Uhr: Zucchet et al. 2025 finden, dass Wiederholung das Lernen stark beschleunigen kann – das passt nicht ganz zu unseren alten Läufen; EXP-129 prüft es mit gleichen Seeds.

- 13:52 Vorwissen aus alten Läufen: Das Sprachmodell lernt die Rechenfakten eher nach einer festen Zahl von Trainingsschritten als nach einer festen Zahl von Wiederholungen je Fakt (beschreibend, 8 Läufe).
- 13:50 Unabhängige Prüfung von EXP-129: kein Blocker, 6 kleine Punkte übernommen.

- 13:45 **EXP-129 vorbereitet und eingereiht:** nächste Stufe der Sprachmodell-Leiter mit nur einem Rechensatz je Zeile (≈ 4.5 % statt 8.7 % Rechen-Tokens). Vorher gerechnet: Der Text reicht bis Schritt 14 477.

- 13:33 Start; STATE, JOURNAL, Dienststatus gelesen; Fenster offen (durchgehend bis 06.10.).

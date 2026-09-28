---
tags: [lab/live]
---
# LIVE: Laborsitzung 41: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 13:20 Berlin (11:20Z, vom Runner)
- **Deadline:** 2026-09-28 16:19 Berlin (14:19Z)
- **Zuletzt aktualisiert:** 15:57 Berlin
- **Run-Fenster:** heute bis 18:00 (Deadline früher).

## Gerade

**Sitzung beendet.** Keine Läufe aktiv. Heute: R9 ins Paper, One-Pager, Reproduktionspaket (5 Blöcke exakt reproduziert), und neue Mechanismus-Piloten zur Frage, *wann* sich die frühe Wahl festlegt: Es kommt darauf an, wie zielgenau die ersten Schritte sind. Große, seltene Schritte sind unselektiver. Adams Mittelungsfenster erklären davon nur einen Teil. Nächster geplanter Start laut runner-state.json: **16:54 Berlin** (Fenster heute bis 18:00).

## Als Nächstes

Repro-Rest (k4b, mul/add 97, P2e) weiterrechnen; Unterschritt-Versuch entwerfen (Trainer-Option, vorher prüfen).

## Verlauf dieser Sitzung

- 15:55 **EXP-094: teilweise.** Gleicht man Adams Fenster an, halbiert sich der Nachteil großer Schritte; ein mit der Schrittgröße wachsender Rest bleibt.
- 15:37 Repro-Kette angehalten, damit EXP-094 vor der Deadline fertig wird (wird später fortgesetzt).
- 15:36 EXP-094 vorab festgelegt und gestartet.
- 15:33 **Neu (post hoc):** Über 15 Einstellungen hängt die Persistenz fast nur davon ab, *wie zielgenau* die frühe Bewegung ist (R² 0.93), nicht wie weit sie ging.
- 15:31 **EXP-093: Die Lag-Uhr gilt nicht allgemein.** Bei gleicher Lernratensumme legen größere, seltenere Schritte immer schwächer fest (0.27 → 0.09).
- 15:30 Repro: auch K4e und K2-Funktion exakt reproduziert.
- 14:45 Paper-Abschnitte zu EXP-092 und Mechanismus unabhängig geprüft (keine Zahlenfehler; eine Literaturaussage zu Sweeney auf das Belegte reduziert).
- 14:39 **Repro K4d bitgenau** (Attention-Reset). Jetzt K4e.
- 14:30 EXP-093 vorab festgelegt und gestartet (Gültigkeitsbereich der Uhr, Lernrate ×2 bis ×8).
- 14:28 **EXP-092: Lag-Uhr gestützt.** Sie sagt neue Einstellungen gut voraus (Fehler 0.03 gegen 0.07/0.15 für die einfachen Uhren), versagt aber bei 4-facher Lernrate (wenige große Schritte, unselektive Bewegung).
- 14:20 Neuheitsprüfung des Nutzer-Assistenten eingearbeitet (Sweeney, Kleinman, LeDoux, He).
- 14:03 **Repro K4c bitgenau reproduziert** (0.903 / 0.603, Abweichung zu N29 exakt 0). Jetzt K4d/K4e (Resets).
- 13:52 One-Pager nach Prüfung überarbeitet (Zahlen alle richtig, 14 Formulierungen vorsichtiger), Literatur zu Sprachmodellen ergänzt.
- 13:40 One-Pager für Anfragen an Forschende geschrieben (`paper/ONE_PAGER.md`, Englisch), wird unabhängig geprüft.
- 13:38 **Repro K2 (add 113) bitgenau reproduziert:** 8.24 [7.92, 8.54], 50/50, Abweichung zur eingefrorenen Zahl 4e-15. Weiter mit K4c.
- 13:38 Post hoc: Persistenz liegt über alle R9-Vorgeschichten fast auf einer Kurve der W_E-Trennung beim Wechsel (R² 0.97).
- 13:33 **Neu (Nachauswertung R9):** Eine kürzere Momentum-Verzögerung macht die frühe Bewegung *zielgenauer* (+13.6 % Zielanteil), mehr Trainingszeit macht sie vor allem *größer* (+19 % Norm). Beides nicht dasselbe.
- 13:32 EXP-092 vorab festgelegt, Smoke ok, Block gestartet.
- 13:27 Reproduktionspaket gestartet (Hinweis des Nutzers: GPU nicht leer laufen lassen).
- 13:26 Paper §3.15 (R9) + Abstract geschrieben, unabhängig geprüft; Literaturfehler korrigiert (Malladis Regel ist 1−β ∝ lr², nicht ∝ lr).
- 13:20 Start: kein STOP, Fenster offen, keine Python-Prozesse.

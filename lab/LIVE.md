---
tags: [lab/live]
---
# LIVE: Laborsitzung 50

- **Sitzungsstart:** 2026-09-29 11:30 Berlin (09:30Z, vom Runner)
- **Deadline:** 2026-09-29 14:29 Berlin (12:29Z)
- **Zuletzt aktualisiert:** 13:31 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe über den GPU-Dienst (Regel 21).

## ⚠ Hinweis für den Nutzer (13:01)

GPU-Speicher ist überbucht (19.0 GB dediziert + 10.0 GB in den Arbeitsspeicher ausgelagert): 6 Sprachmodell-Läufe gleichzeitig laufen ≈ 7× langsamer als 2. Ich darf den GPU-Dienst nicht neu starten; die Kopfzeilen meiner Jobdateien sind gesenkt (LM1 2 Worker, EXP-115 1, EXP-113 2) und greifen erst nach einem **Neustart des Dienstes per DRAIN**. Bitte, wenn möglich, den Dienst so neu starten. Details im JOURNAL. **Update 13:31:** jetzt 10 LM-Läufe gleichzeitig (EXP-115 hat alle 4 Plätze), R4 läuft gar nicht mehr; LM1-Lauf 0 seit ≈ 25 min bei Schritt 750. Bitte um Eingriff bleibt bestehen (siehe unten).

**Update 13:11:** jetzt 8 LM-Läufe, 12.1 GB ausgelagert, nur 1.8 GB Arbeitsspeicher frei (über der Grenze aus Regel 17).

**Update 13:21: Stillstand.** In 10 min kein Fortschritt mehr in allen LM-Läufen, R4-Läufe hängen seit 43 min. Mein Versuch, die zwei eigenen EXP-115-Läufe abzubrechen, wurde vom Sicherheitsfilter abgelehnt. **Bitte:** Dienst per DRAIN neu starten und/oder die Prozesse von EXP-115 (PIDs 29648, 31352 + Wächter 18600, 22580) und EXP-113 (2808, 3344 + Wächter 24084, 18152) beenden. Beides lässt sich danach ohne Verlust fortsetzen (Checkpoints).

## Gerade

- GPU-Dienst: LM1 1 laufend / 0 fertig von 20; R4 60/240; EXP-113 Läufe 1–2 kurz vor dem Ende (Fakten gelernt, zurückgehalten ≈ 0.95).
- Ich warte auf das Ende von EXP-113 Läufen 1–2 (≈ 13:00–13:10) für einen beschreibenden Blick auf H-folgt.

## Als Nächstes

LM1 läuft ≈ 4–5 h im Dienst weiter (Auswertung in einer späteren Sitzung). Sitzungsende 14:29.

## Verlauf dieser Sitzung

- 12:39 **LM1 eingefroren** (nach unabhängiger Prüfung, 6 Punkte übernommen) und 20 Läufe eingereiht.
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

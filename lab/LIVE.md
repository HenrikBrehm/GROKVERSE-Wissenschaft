---
tags: [lab/live]
---
# LIVE: Laborsitzung 47

- **Sitzungsstart:** 2026-09-29 03:29 Berlin (01:29Z, vom Runner)
- **Deadline:** 2026-09-29 06:29 Berlin (04:29Z)
- **Zuletzt aktualisiert:** 05:13 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

**Folgetest Sprachmodell-Leiter (40 Läufe à 10 000 Schritte, Start 05:14):** Lernt das Netz mit „Verlust auf allen Positionen“ nur später (und die Steuerung kommt zurück), oder blockiert dieses Ziel die Steuerung? Parallel: unabhängige Nachrechnung des Leiter-Piloten.

## Als Nächstes

Folgetest auswerten (Lesarten vorab), dann Abschlussbericht (Deadline 06:29).

## Verlauf dieser Sitzung

- 05:12 **Leiter Stufe 1 (Pilot):** Operator-Token, volle Softmax und gebundene Embeddings ändern die Steuerung nicht. Verlust auf allen Positionen senkt sie um 80 %, aber diese Netze haben bis Schritt 2000 gar nicht generalisiert → Folgetest.
- 05:05 Paper: §6/§7 und Langfassung §3.19 mit N54b, nach unabhängiger Prüfung korrigiert.

- 04:55 Leiter-Trainer bitgleich zum bisherigen Trainer → Pilot EXP-102 gestartet.
- 04:53 Modellvergleich: „Drift + etwa zwei Durchgänge durch die Daten“ beschreibt die Festlegungszeit am besten (nachträglich, Hypothese).
- 04:51 **N54b BESTÄTIGT (10 neue Netze, eingefroren, nachgerechnet):** Festlegungszeit wächst etwa mit √(Schritte pro Durchgang) (α = 0.58); doppelte Lernrate hilft bei kleinen Päckchen weniger (Δα = +0.14, 10/10).

- 04:15 Paper: §6 um die Batch-Reihe (Wurzel-Uhr, Exploration) ergänzt; Literatur eingetragen. Sprachmodell-Leiter: Selbsttests bestanden, Gleichwertigkeitsprüfung vorbereitet.

- 04:10 Modellvergleich für die N54b-Daten vorab festgelegt (reine Sign-Drift / Drift + Diffusion / frei).
- 04:09 Repro-Smoke abgebrochen: CPU-Lauf neben 10 GPU-Prozessen überlastete die Kerne (Pfad-Aufruf selbst funktioniert).
- 04:08 Paper: §3.18 und EXP-103-Satz nach Quellenprüfung korrigiert (keine Zahlenfehler).
- 04:06 Nachträglich: Festlegung liegt immer bei ≈ ¼ der Zeit bis 50 % Trainingsgenauigkeit, also vor der Memorisierung; Lesart „unklar“.

- 03:49 **N54b eingefroren** (624c2213) und gestartet; Smoke ok.

- 03:46 **EXP-109:** doppelte Lernrate halbiert die Festlegungszeit bei großen Batches (1024: 31 statt 62 Schritte), bei B 64 nur ×0.75 → Registrierung umgestellt (H2: gepaarte Exponent-Differenz > 0).

- 03:40 Prüfung des Bestätigungsskripts: kein Blocker; 4 Punkte übernommen. Full-Batch-Arm gestrichen (teuer; Modell sagt Sättigung dort) → 840 Läufe.
- 03:40 Literatur: keine Arbeit mit dieser Wurzel-Skalierung gefunden; Adam/Sign-Modell sagt α = 0.5 und Halbierung bei doppelter Lernrate voraus.
- 03:40 Paper: Abb. 4 englisch; Langfassung §3.18 (L0-Bestätigung).

- 03:36 Bestätigungsskript confirm_n54b.py: Selbsttest ok.
- 03:33 EXP-109 festgelegt (Commit 9804ce01) und gestartet.
- 03:30 Stand gelesen; keine laufenden Prozesse; Fenster offen.

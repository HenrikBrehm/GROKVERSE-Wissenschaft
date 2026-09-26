---
tags: [lab/live]
---
# LIVE: Laborsitzung 11

- **Sitzungsstart:** 2026-09-26 19:10 Berlin (17:09Z, vom Runner)
- **Deadline:** 2026-09-26 22:09 Berlin (20:09Z)
- **Zuletzt aktualisiert:** 19:24 Berlin
- **Run-Fenster:** zu (heute bis 18:00), wieder ab 00:00. Diese Sitzung: nur Denk-, Code- und Vorbereitungsarbeit.

## Gerade

Codex (OpenAI) prüft gerade den neuen Versuch EXP-043 und die GPU-Änderung auf Fehler, bevor heute Nacht irgendetwas läuft.

## Als Nächstes

Codex-Einwände einarbeiten; Übergabe für die Nacht schreiben (ab 00:00: GPU-Prüfung → CPU-Queue → EXP-043 parallel auf der GPU).

## Verlauf dieser Sitzung

- 19:19 **Neuer Versuch [[experiments/EXP-043-generalize-steering/README|EXP-043]] festgelegt:** Klappt die Steuerung der Frequenzen über die Daten auch bei Modulus 97 und bei *Multiplikation*? Bei Multiplikation rechnet das Netz „im Logarithmus“; die Splits sind dafür umgebaut. Alle 40 Splits erzeugt, die Konstruktion trifft ihre Zielfrequenzen. Literatur: „Discrete-Log Clock“ (2026) beschreibt den Multiplikations-Mechanismus, aber keine Steuerung über die Daten.
- 19:16 **Grafikkarte vorbereitet:** Das Trainingsprogramm kann jetzt auf der AMD-Karte rechnen (`--device cuda`), noch ungetestet. Prüfung [[experiments/GPU-001-equivalence/README|GPU-001]] mit festen Kriterien: gleiche Frequenzen und gleicher Grokking-Zeitpunkt wie auf der CPU, sonst keine GPU. Die CPU-Queue wartet nicht mehr auf GPU-Läufe.
- 19:13 [[FINDINGS]] angelegt: sechs Kernaussagen mit Belegen auf einer Seite; größte offene Frage: gilt das alles auch außerhalb von „Addition mod 113“?
- 19:12 Stand gelesen; kein Training läuft (nur zwei GPU-Abfragen des Nutzers von 19:09), Fenster zu.

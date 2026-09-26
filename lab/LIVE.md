---
tags: [lab/live]
---
# LIVE: Laborsitzung 11

- **Sitzungsstart:** 2026-09-26 19:10 Berlin (17:09Z, vom Runner)
- **Deadline:** 2026-09-26 22:09 Berlin (20:09Z)
- **Zuletzt aktualisiert:** 19:29 Berlin
- **Run-Fenster:** zu (heute bis 18:00), wieder ab 00:00. Diese Sitzung: nur Denk-, Code- und Vorbereitungsarbeit.

## Gerade

Codex (OpenAI) prüft gerade den neuen Versuch EXP-043 und die GPU-Änderung auf Fehler, bevor heute Nacht irgendetwas läuft.

## Als Nächstes

Codex-Einwände einarbeiten. Plan für die Nacht steht in [[STATE]]: ab 00:00 GPU-Queue (Prüfung → EXP-043 → EXP-044 → EXP-045) und parallel die CPU-Queue.

## Verlauf dieser Sitzung

- 19:28 GPU-Sammelqueue `queue_gpu_s11.sh` geschrieben: erst die Gleichwertigkeitsprüfung, dann die drei neuen Versuche, so viele Läufe gleichzeitig wie die Karte am schnellsten schafft.
- 19:26 **EXP-045 festgelegt:** Klappt die Steuerung auch in einem ganz anders gebauten Netz (MLP statt Transformer)? 10 Seeds, 10 000 Schritte.
- 19:25 **Selbstkritik vor dem Lauf:** Multiplikation mod 113 ist für dieses Netz nach Umbenennen der Zahlen fast genau „Addition mod 112“. EXP-043 prüft also eher einen anderen Modulus als eine andere Rechenart. Ehrlich im README vermerkt.
- 19:24 **Korrektur:** Meine Uhrzeiten in den Notizen waren geschätzt und lagen in der Zukunft. Jetzt mit der Uhr des Wächters gemessen und korrigiert.
- 19:22 **EXP-044 festgelegt:** Legt sich das Netz auch bei den neuen Aufgaben früh fest, selbst wenn fast alle Trainingsbeispiele ausgetauscht werden? Läuft nur, wenn EXP-043 klappt.
- 19:19 **Neuer Versuch [[experiments/EXP-043-generalize-steering/README|EXP-043]] festgelegt:** Klappt die Steuerung der Frequenzen über die Daten auch bei Modulus 97 und bei *Multiplikation*? Bei Multiplikation rechnet das Netz „im Logarithmus“; die Splits sind dafür umgebaut. Alle 40 Splits erzeugt, die Konstruktion trifft ihre Zielfrequenzen. Literatur: „Discrete-Log Clock“ (2026) beschreibt den Multiplikations-Mechanismus, aber keine Steuerung über die Daten.
- 19:16 **Grafikkarte vorbereitet:** Das Trainingsprogramm kann jetzt auf der AMD-Karte rechnen (`--device cuda`), noch ungetestet. Prüfung [[experiments/GPU-001-equivalence/README|GPU-001]] mit festen Kriterien: gleiche Frequenzen und gleicher Grokking-Zeitpunkt wie auf der CPU, sonst keine GPU. Die CPU-Queue wartet nicht mehr auf GPU-Läufe.
- 19:13 [[FINDINGS]] angelegt: sechs Kernaussagen mit Belegen auf einer Seite; größte offene Frage: gilt das alles auch außerhalb von „Addition mod 113“?
- 19:12 Stand gelesen; kein Training läuft (nur zwei GPU-Abfragen des Nutzers von 19:09), Fenster zu.

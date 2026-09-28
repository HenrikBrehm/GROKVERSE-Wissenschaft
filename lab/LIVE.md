---
tags: [lab/live]
---
# LIVE: Laborsitzung 38

- **Sitzungsstart:** 2026-09-28 05:19 Berlin (03:19Z, vom Runner)
- **Deadline:** 2026-09-28 08:19 Berlin (06:19Z)
- **Zuletzt aktualisiert:** 07:44 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

- GPU: **R4-Block** (≈ 54/240, 2 Worker) läuft bis zur Deadline; Rest in Sitzung 39 (dann mit 8 Workern).
- CPU: EXP-014 (Job 8).
- Schreibe den Abschlussbericht.

## Als Nächstes

Sitzung 39: R4 fertig rechnen und auswerten, ins Paper; danach EXP-087 / EXP-081 (Trainer-Sperre fällt nach R4).

## Verlauf dieser Sitzung

- 07:42 R2/C2-Paperabschnitt geprüft (Zensur der Zeitkosten bei wd 0.3 ergänzt).
- 07:36 **R2:** Übergang bei lr 2e-3 bestätigt, bei wd 0.3 nicht (Umstieg fehlt, dort kaum Generalisierung). **C2 bestätigt** (alte Ziele behalten ihre Rangfolge, ρ̄ 0.61).
- 07:07 Abstract ergänzt, unabhängig geprüft (zwei Überdehnungen korrigiert).
- 06:56 R7-Abschnitt geprüft (keine Fehler); neuer Versuchsentwurf **EXP-087** (Mediation der Beschleunigung).
- 06:44 **R7 bestätigt:** K2 auch im 2-Schicht-Transformer (Δ_pow 6.15, 10/10). R4 gestartet.
- 06:33 P4/C3-Paperabschnitt geprüft (Testname korrigiert, MLP-Init-Ordnung ergänzt).
- 06:23 **P4 bestätigt** in allen drei Bedingungen (MLP, 4× Breite, Integer-Addition; je 15/15); **C3 bestätigt** (S = 0.30).
- 06:08 R3-Paperabschnitt geprüft (Zahlen richtig, Formulierungen vorsichtiger).
- 05:57 **R3 fertig:** Schrittuhr widerlegt (beide Zellen 0/20); Λ-Uhr registriert *nicht bestätigt* (doppelte Lernrate bestätigt, halbe nur in der Richtung).
- 05:43 **EXP-078:** Steuerung überträgt sich auf 2 Schichten (Δ_pow 5.84, 10/10); **R7 eingefroren** (n = 10), Block läuft.
- 05:28 **EXP-040 fertig:** *unklar* (registriert); die W_E-Init-Skala verschiebt das Festlegungsfenster nicht (3/4 Seeds) → gegen die Amplitudenschwelle.
- 05:26 Neue Idee N47 (Mediation der R5-Beschleunigung über frühes W_E-Signal); verwandte Arbeit Howe 2026 eingeordnet.
- 05:23 R5 §3.9 unabhängig geprüft: Zahlen richtig, 7 Formulierungen korrigiert. Post hoc: früher Zielanteil sagt Tempo innerhalb der E-Arme vorher (ρ ≈ −0.7).
- 05:21 R5 als §3.9 ins Paper (Prüfung läuft).
- 05:20 EXP-078 (GPU) und EXP-040/014 (CPU) gestartet.

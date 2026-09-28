---
tags: [lab/live]
---
# LIVE: Laborsitzung 38: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 05:19 Berlin (03:19Z, vom Runner)
- **Deadline:** 2026-09-28 08:19 Berlin (06:19Z)
- **Zuletzt aktualisiert:** 07:59 Berlin
- **Nächster geplanter Start:** 2026-09-28 08:54 Berlin (runner-state.json `next_start_utc` 06:54Z)
- **Run-Fenster:** heute bis 18:00.

## Gerade

**Sitzung beendet.** Heute bestätigt: **P4, R7, C2, C3**; R2 gilt nur in einem Bereich; R3 *Λ-Uhr nicht bestätigt*. R4 (85/240) läuft bis zur Deadline 08:19 und wird dann vom Wächter beendet; EXP-014 (CPU) ist regulär gestoppt (9 Läufe fertig). Nächster Start: **08:54 Berlin**.

## Als Nächstes

Sitzung 39 (08:54): R4 mit 8 Workern fertig rechnen, auswerten, ins Paper.

## Verlauf dieser Sitzung

- 07:59 Sitzung beendet (Paper §5b/§6 aktualisiert und geprüft).
- 07:42 Abschlussbericht.
- 07:40 R2/C2-Paperabschnitt geprüft (Zensur der Zeitkosten bei wd 0.3 ergänzt).
- 07:35 **R2:** Übergang bei lr 2e-3 bestätigt, bei wd 0.3 nicht (Umstieg fehlt, dort kaum Generalisierung). **C2 bestätigt** (alte Ziele behalten ihre Rangfolge, ρ̄ 0.61).
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

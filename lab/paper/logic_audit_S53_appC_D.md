---
id: logic-audit-s53-appCD
status: offen
datum: 2026-09-29
tags: [lab/paper]
---
# Logikprüfung Anhänge C und D (Sitzung 53, 21:53 Berlin) – NOCH NICHT SELBST NACHGEPRÜFT

Zurück: [[paper/STATUS]] · [[JOURNAL]] Sitzung 53. Unabhängiger Claude-Agent, nur lesend. **Vor dem Einarbeiten jeden Punkt an der genannten Stelle selbst prüfen** (Sitzung 53: 3 von 16 Vorschlägen brauchten eine Korrektur des Vorschlags selbst). Die Texte stammen aus `draft.md` (Langfassung, über `build_manuscript.py` eingebunden), nicht aus `draft_short.md`. Nach dem Einarbeiten: Diff-Prüfung durch einen zweiten Agenten.

1. **C.4, fehlende Zensierung (laut Prüfer: Fehler).** „delayed grokking … ≈ 1.8“, „largest mean cost at t = 20“, „94 % of the delay lies in the gap“: C ist bei 2000 zensiert (R6_REGISTRATION_DRAFT.md:21-22); laut R6_summary.json erreichten 18/60 gewechselte Läufe bei t = 25 und 27/60 bei t = 20 die 0.95 nie. Kosten sind untere Schranken; die 94 % (R6_decompose.py:33-42) nutzen nur 42 unzensierte Paare in linearen Schritten. Vorschlag: „C is censored at 2000 (18/60 runs at t = 25, 27/60 at t = 20 did not generalize), so the costs are lower bounds; the decomposition covers the 42 uncensored pairs, in steps.“ (Der Haupttext §5 hat den Vorbehalt bereits.)
2. **C.4-Titel und R8 (Überdehnung).** „but only if the target frequencies change“, „did not delay grokking“, „it requires a different target set“: R8 prüfte nur D > 0 und S1 (C_AA2 < ½ C_AB), nur t = 25 (R8_REGISTRATION_DRAFT.md:31-32). Vorschlag: „…delays grokking much more when the target frequencies change (t = 25)“; „A→A2 cost far less (C_AA2 = −0.15, not tested against 0)“. (Im Haupttext in S53 schon so geändert.)
3. **C.3, Größenprüfung passt nicht zum Reset (laut Prüfer: Fehler).** „‖W(50) − W(0)‖_F per reset part, i.e. what each reset removes“: Die Resets setzen auch den AdamW-Zustand zurück (manuscript.md:262, 264), gemessen ist nur die Gewichtsverschiebung. Vorschlag: „…the weight displacement each reset undoes (the optimizer state it also clears is not measured)“.
4. **„exposure“ doppelt (C.1 gegen C.4).** C.1 = Exposition gegenüber dem alten Split vor dem Wechsel (N28 M2), C.4 = weniger Ziel-Updates (R6). Vorschlag: „pre-switch exposure“ bzw. „fewer destination updates“ (wie im Haupttext S53).
5. **D.2-Titel (Äquivalenz nur bei c = 0.25).** Vorschlag: „Rescaling Adam's β windows to Λ removes most of the step dependence (equivalent within ±0.1 at c = 0.25; direction confirmed at c = 2)“ (wie §7 (iv) S53).
6. **C.1 „Persistence was nevertheless the same (π 0.351 vs 0.355…)“** – ω = 0.4 war beschreibend, kein Äquivalenztest (P3_REGISTRATION_DRAFT.md:29, 67); ε unterscheidet sich. Vorschlag: „did not differ detectably (0.005 [−0.030, 0.042]; no equivalence test)“.
7. **D.1 Zuschreibung auf das erste Moment** – R9 skalierte β₁ und β₂ gemeinsam, π-Maß statt R3-Zellen. Vorschlag: „…from Adam's moment windows (β₁ and β₂ rescaled together)“.
8. **D.1 kausale Formulierung ohne Kontrollarm** – R3 hat keinen Standardarm; „vorgezogen/verzögert“ relativ zu N29 auf anderen Seeds (Standardwerte 0.81–0.90 je Block); halbe Rate nur beschreibend (Test verfehlt). Vorschlag: „relative to the default values of N29 (other seeds), doubling … appears to bring it forward; at half rate the shift is in the Λ direction but below the registered bar.“

Keine Befunde laut Prüfer: C.2, D.3, D.4.

## Selbst nachgeprüft (21:54 gemessen)

- **Punkt 1 ✓:** `R6_summary.json` (events = generalisiert ja/nein bis 2000): ohne Ereignis bei t = 20: 27/60, t = 25: 18/60, t = 50: 1/60; nur Ziel-Split: 0/60. Registrierung Z. 21: b = min(Ereignis, 2000). Die 94 %-Zerlegung (R6_decompose.py) noch nicht angesehen.
- **Punkt 3 ✓:** manuscript.md Z. 262/264: Resets setzen Gewichte *und* AdamW-Zustand zurück; die Größenprüfung (Z. 268) misst nur ‖W(50) − W(0)‖_F.
- **Punkte 2, 4, 5:** derselbe Befund wie im Haupttext (R8 ohne Äquivalenztest; „exposure“ doppelt; R9-Äquivalenz nur bei c = 0.25), dort in Sitzung 53 an den Registrierungen geprüft und korrigiert.
- **Punkte 6, 7, 8:** noch offen (P3 Z. 29/67; R9 β₁/β₂ gemeinsam; R3 ohne Standardarm).

- **Nachtrag (21:55 gemessen): Punkte 6, 7 ✓, 8 plausibel.** P3 Z. 29 („Δπ … beschreibend mit KI; keine Entscheidung“) und Z. 67 („ε unterscheidet sich zwischen den Stufen“); R9 Z. 16: β′ = 0.975/0.995, also β₁ und β₂ gemeinsam; R3 Z. 31–32: nur die Arme lrs2/lrs05, Vergleich „wie Standard“ gegen N29 – ein eigener Standardarm ist in der Tabelle nicht zu sehen (die Varianz der N29-Standardwerte 0.81–0.90 selbst nicht nachgeprüft). **Damit sind alle 8 Punkte als Befund gestützt; nächste Sitzung: in draft.md einarbeiten (Wortlaut der Vorschläge vorher prüfen), Manuskript neu erzeugen, Diff prüfen lassen.**

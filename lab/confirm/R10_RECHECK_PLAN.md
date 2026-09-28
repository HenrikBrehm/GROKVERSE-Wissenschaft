---
tags: [lab/confirm]
---
# R10: Plan für die unabhängige Nachrechnung (vorbereitet Sitzung 44, vor dem Ansehen der Ergebnisse)

Zurück: [[confirm/R10_REGISTRATION_DRAFT|R10]] · [[STATE]] Schritt 2

**Wann:** direkt nach `confirm_r10.py --analyze` und **vor** dem L0-Patch-Commit (danach verweigert `check_code`; sonst nur über `git worktree add <dir> 7b583bdb`).

**Auftrag an den Prüf-Agenten (nur lesend, eigener Code, `confirm_r10.py` NICHT importieren):**
1. Aus `lab/confirm/R10_manifest.json` Seeds (3500–3547), Zellen (n24, g8, c8b, g24, reine Läufe) und Budget lesen; Läufe in `lab/confirm/r10_raw/` über Run-ID-Muster finden; je Lauf `status == completed`, Schrittzahl, Split-Hash gegen `lab/confirm/r10_splits/` prüfen.
2. π je Seed und Zelle nach der EXP-056-Definition selbst nachbauen (Definition im Code von EXP-056 und in der R10-Registrierung lesen, nicht aus `confirm_r10.py` übernehmen), beide Richtungen A→B/B→A wie registriert mitteln.
3. e₈ = π(n24) − π(g8), r₈ = π(g8) − π(c8b), e₂₄ = π(n24) − π(g24): Mittel, SD, einseitige gepaarte t-Tests, TOST ±0.05 für r₈, Holm über 3, 95-%-Bootstrap-KI; mit `R10_summary.json` vergleichen (Toleranz 1e-6 bzw. Bootstrap-Streuung).
4. Lesart nach der Registrierung („alle drei → Auswertungen-Befund bestätigt“, sonst Liste) selbst ableiten.
5. Einschränkungen aus der Registrierung (Zählerunterschied c8b/g8, Vorzeichenschritte bei eingefrorenem Gradienten, H1-Kriterium schwächer als im Pilot) in der Bewertung nennen.

**Danach:** Ergebnis in R10-Registrierung (Ergebnisabschnitt), FINDINGS (K5/R10-Nebenabschnitt), Paper-Anhang D; jede Paper-Zahl erneut unabhängig prüfen lassen.

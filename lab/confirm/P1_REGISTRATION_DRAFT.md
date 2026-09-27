---
id: P1-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# P1-Bestätigung: Registrierungsentwurf (Sitzung 20, 2026-09-27 03:30 Berlin, gemessen). **NICHT eingefroren**

Zurück zu [[FINDINGS]]. Eingefroren ist erst eine Fassung `P1_manifest.json` mit Feld `commit`, die unverändert in diesem Commit liegt
(`confirm_splits.check_manifest`). Vorher: Codex-Prüfung (Regel 18c), Befunde selbst prüfen, dann einfrieren.

- **Aussage P1:** Konstruierte Splits erhöhen die Leistung der Zielfrequenzen/-Irreps in W_E: Δ_pow > 0 auf frischen Seeds **und** frischen Splits.
- **Entwurf** `P1_manifest_DRAFT.json`: Seeds 1000–1049 (50 von 100 reservierten; 1050–1099 bleiben für P2/P3), ε = 2, Aufgaben add 113 (Kern), mul 113, add 97, D₅₉;
  GPU (`.venv-gpu`, 1 Thread; `confirm_p1.interp` macht daraus einen absoluten Pfad), Kreuzblock add 113 Seeds 1000–1004 × 2 Inits (sekundär, Sitzung 16).
- **Analyse (Code `lab/tools/confirm_p1.py`, eingefroren mit dem Manifest):** je Aufgabe Mittel Δ_pow, einseitiger Vorzeichen-Permutationstest, 95-%-Bootstrap-KI;
  Holm über alle Aufgaben + zwei Platzhalter (P2, P3 mit p = 1); „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze > 0; Mindesteffekt 1 berichtet.
- **Stichprobe:** `pilot_power.py` (Sitzung 20): add 113 n ≈ 25–27 (konservativ 44), mul 113 26–49, add 97 8–11, D₅₉ 7. 50 deckt alle konservativen Werte außer mul 113 (49, knapp).
- **Offene Entscheidungen vor dem Einfrieren:** (1) Mindesteffekt je Aufgabe relativ statt fest 1 (Skalen verschieden: Pilotmittel D₅₉ 2.7, add 7.7)? (2) int-add
  (EXP-048) fehlt, weil `confirm_splits` nur add/mul/D kennt. Nachrüsten oder als Grenze nennen. (3) Holm über vier Aufgaben + 2 Platzhalter = Familie 6: gewollt?
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-016 (add 113, Seeds 10–19), EXP-043 (add 97, mul 113; 70–79), EXP-046 (D₅₉; 140–149),
  EXP-047 (add 113 GPU; 150–159), EXP-048 (int-add; 160–169), EXP-049 (add 113 d128/512; 170–179), EXP-052 (R-Läufe), `pilot_power` auf diesen Piloten.
  Beeinflusst: Aufgabenwahl (nur im Pilot *steuerbare* Aufgaben), n = 50 (aus der Pilotstreuung), GPU statt CPU (GPU-001). Keine Seeds 1000–1099 wurden je benutzt.

## Codex-Prüfung (Sitzung 20, 03:41) → Reparaturliste vor dem Einfrieren (Einzelheiten und Begründung: [[JOURNAL]] Sitzung 20, Zyklus 14)

- [x] (B1, Sitzung 20 umgesetzt, Selbsttest grün: `confirm_splits.py --hash-code` liefert das Feld `code_sha256`; `check_manifest` prüft es bei Splits, `--jobs`, `--analyze`. Rest-Lücke: der Lader prüft den `git_commit` der Läufe nicht; eine Änderung zwischen `--jobs` und `--analyze`, die wieder zurückgenommen wird, bliebe unbemerkt) Code-Hashes (Trainer, Splits, Analyse, Lader) ins Manifest, bei `--jobs`/`--analyze` prüfen, Läufe gegen Hashes/Commit prüfen
- [x] (B2, Sitzung 20 umgesetzt, Selbsttest grün: Manifestfeld `primary_task`, `confirm_p1.family_adjust`) Familie festlegen: P1 = add 113 primär (P1–P3-Holm über 3), übrige Aufgaben als P1b sekundär mit eigener Holm-Familie
- [x] (H3, Sitzung 20 umgesetzt, Selbsttest grün) „bestätigt“ = Holm-p < 0.05 **und** KI-Untergrenze ≥ 1 (Mindesteffekt Teil der Aussage)
- [x] (B4, Sitzung 20 umgesetzt, Selbsttest grün; Wiederholungsregel für Infrastrukturfehler noch in die Registrierung schreiben) alle 50 Paare verlangen; nicht-endliches Δ / Zielsumme ≤ 0 → ungültig; sonst *nicht auswertbar*
- [x] (H5, mit B2 erledigt: P1 = add 113 bei α/3 → n 25–27, konservativ 44 ≤ 50; P1b-Familie über 3 Aufgaben ebenfalls α/3 im ungünstigsten Fall, mul 113 konservativ 49 ≤ 50, knapp) Power mit der endgültigen Familie und dem endgültigen Test neu rechnen (bei B2: α/3)
- [x] (H6, Sitzung 20 umgesetzt, Selbsttest grün) bei `--analyze` Split-Indizes und Ziele aus `build()` neu erzeugen und exakt vergleichen
- [ ] (H7) Symmetrie-Annahme des Vorzeichentests ausdrücklich registrieren; t-Test sekundär berichten
- [ ] (M8/M9) Design als seed-gepaart beschreiben; P1 als Replikation in pilotgewählten Fällen formulieren
- verworfen: Mindesteffekt relativ zum Pilotmittel (Δ ist dimensionslos)

### Textbausteine für die Registrierung (Sitzung 20, H7/M8/M9)

- **Test (H7):** einseitiger Vorzeichen-Permutationstest. Nullhypothese: Die Verteilung von Δ_pow ist symmetrisch um 0. Begründung: F und G sind gleich konstruiert (gleiche ε, disjunkte
  Ziele aus einer Permutation, gleiche Init), unter „kein Einfluss des Splits“ sind die Arme vertauschbar, und Vertauschen kehrt das Vorzeichen von Δ um. Sekundär wird ein
  studentisierter t-Test berichtet.
- **Design (M8):** seed-gepaart. F und G teilen die Init, alle Aufgaben nutzen dieselben Seeds. Die Split-Ströme sind nach Aufgabe, p, Seed, Arm und Zweck getrennt.
- **Aussage (M9):** P1 ist eine **unabhängige Replikation in vier nach dem Pilot gewählten Fällen** (add 113 primär, dazu mul 113, add 97, D₅₉ als P1b),
  keine Verallgemeinerung auf eine unverzerrte Aufgabenpopulation.
- **Wiederholungsregel (B4):** Scheitert ein Lauf an der Infrastruktur (Wächter-Abbruch, Absturz ohne Ergebnis), wird **derselbe** eingefrorene Job wiederholt. Fehlt danach ein Paar, gilt die Aufgabe als *nicht auswertbar*.
- Noch offen vor dem Einfrieren: Nachprüfung der geänderten Stellen durch Codex (nur B1, B2, B4, H3, H6), danach Manifest mit `code_sha256` und `commit` einfrieren.


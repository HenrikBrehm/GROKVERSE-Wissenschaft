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

- [ ] (B1) Code-Hashes (Trainer, Splits, Analyse, Lader) ins Manifest, bei `--jobs`/`--analyze` prüfen, Läufe gegen Hashes/Commit prüfen
- [ ] (B2) Familie festlegen: P1 = add 113 primär (P1–P3-Holm über 3), übrige Aufgaben als P1b sekundär mit eigener Holm-Familie
- [ ] (H3) „bestätigt“ = Holm-p < 0.05 **und** KI-Untergrenze ≥ 1 (Mindesteffekt Teil der Aussage)
- [ ] (B4) alle 50 Paare verlangen; nicht-endliches Δ / Zielsumme ≤ 0 → ungültig; sonst *nicht auswertbar*
- [ ] (H5) Power mit der endgültigen Familie und dem endgültigen Test neu rechnen (bei B2: α/3)
- [ ] (H6) bei `--analyze` Split-Indizes und Ziele aus `build()` neu erzeugen und exakt vergleichen
- [ ] (H7) Symmetrie-Annahme des Vorzeichentests ausdrücklich registrieren; t-Test sekundär berichten
- [ ] (M8/M9) Design als seed-gepaart beschreiben; P1 als Replikation in pilotgewählten Fällen formulieren
- verworfen: Mindesteffekt relativ zum Pilotmittel (Δ ist dimensionslos)


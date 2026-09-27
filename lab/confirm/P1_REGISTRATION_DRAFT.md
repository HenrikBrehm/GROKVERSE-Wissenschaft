---
id: P1-registrierung
status: eingefroren
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
  **Familien (B2):** `primary_task` add 113 = P1, Holm über {P1, P2, P3} (P2/P3 als p = 1, bis sie vorliegen); mul 113, add 97, D₅₉ = P1b, eigene Holm-Familie (sekundär).
  **„bestätigt“ (B4/H3) = alle 50 Paare gültig, Holm-p < 0.05 und untere Grenze des 95-%-KI ≥ 1 (Mindesteffekt).** Sonst *nicht bestätigt*. Fehlt ein Paar: *nicht auswertbar*.
- **Stichprobe:** `pilot_power.py` (Sitzung 20): add 113 n ≈ 25–27 (konservativ 44), mul 113 26–49, add 97 8–11, D₅₉ 7. 50 deckt alle konservativen Werte außer mul 113 (49, knapp).
- **Entschieden (Sitzung 20):** Mindesteffekt fest 1 (Δ ist ein dimensionsloses Log-Verhältnis, Codex). Familien wie oben. int-add (EXP-048) ist nicht im Block,
  weil `confirm_splits` nur add/mul/D kennt: Das ist eine **Grenze**, P1 sagt nichts über nicht-modulare Aufgaben.
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
- [x] (H7, Text unten „Textbausteine“, Teil der Registrierung; t-Test sekundär noch nicht im Code, wird beschreibend nachgereicht) Symmetrie-Annahme des Vorzeichentests ausdrücklich registrieren; t-Test sekundär berichten
- [x] (M8/M9, Text unten, Teil der Registrierung) Design als seed-gepaart beschreiben; P1 als Replikation in pilotgewählten Fällen formulieren
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

## Codex-Nachprüfung (Sitzung 20, 03:54) der Korrekturen

- B2, B4/H3, H6 im Code bestätigt. Text oben entsprechend nachgezogen (war noch alt).
- [x] `lab/tools/paket_a_device.py` in `CODE_FILES` (wird über EXP-043 `analyze.py` ausgeführt). Die Starter `parallel_queue.py` und `guarded_run.py` sind **ausdrücklich ausgenommen**:
  kein wissenschaftlicher Code, unversionierte Dateien des Nutzers (sie setzen Zeitfenster und Parallelität durch, ändern keine Rechnung).
- [x] **B1 (Sitzung 21 gelöst, siehe unten):** Die Läufe werden nicht an den eingefrorenen Code gebunden. Eine Codeänderung zwischen `--jobs` und `--analyze`, die wieder zurückgenommen wird,
  bliebe unbemerkt. Lösung: Die Trainer bekommen `--manifest`, prüfen beim Start `check_code`, schreiben den geprüften Digest in `result.json`, und der Lader vergleicht ihn beim Auswerten.
  Das ändert den gemeinsamen Trainer, also vorher Codex-Prüfung (Regel 18c). Nächste Sitzung.

## B1 umgesetzt (Sitzung 21, 2026-09-27 04:24 Berlin, Commit feedd8f), anders als oben skizziert

Statt den gemeinsamen Trainer zu ändern, läuft **jeder Job über einen Wrapper**: `confirm_p1.py --run <Manifest> -- <Trainerbefehl>`
(`--jobs` erzeugt nur noch solche Zeilen). Der Wrapper prüft Manifest und Code-Hashes vor dem Start, startet den Trainer, prüft den Code
danach erneut und schreibt eine **Bindung** nach `lab/confirm/bindings/` (Code-Digest, Manifest-Commit, Exit-Code, sha256 jeder Datei, die der
Lauf in seinem eigenen Laufverzeichnis geschrieben hat). `--analyze` nimmt einen Lauf nur an, wenn **jede** Datei seines Verzeichnisses durch eine
erfolgreiche Bindung mit passendem Digest und Commit gedeckt ist. Läufe außerhalb des Wrappers, geänderte oder zusätzliche Dateien → *defekt*.
Vorteil: `freq_ban.py`/`group_train.py` bleiben unverändert (keine neue Gleichwertigkeitsprüfung nötig). Selbsttest grün (inkl. Ende-zu-Ende mit
Scheintrainer). Codex-Nachprüfung: siehe unten / [[JOURNAL]] Sitzung 21.
## EINGEFROREN (Sitzung 21, 2026-09-27 04:46 Berlin, gemessen)

P1 ist mit dem Manifest `lab/confirm/P1_manifest.json` eingefroren: **Manifest-Commit 733e829** (enthält `code_sha256` über 60 Dateien, darunter
`confirm_p1.py` und `confirm_p2.py`), Commit-Feld nachgetragen in 0cd5ee5. Es gelten die Regeln dieses Dokuments einschließlich aller Abschnitte
„Codex-Prüfung“ und „Änderung vor dem Einfrieren“, jeweils mit ihren Übernahmen. Letzte Codex-Nachprüfung (04:45): zwei Punkte als Restrisiko abgelehnt
(Ändern und Zurücknehmen innerhalb von 2 s; untergeschobenes .pyc im Cache): Beides setzt absichtliche Manipulation voraus, gegen die ohnehin keine Datei geschützt ist.
Übernommen: Die Bindung speichert das Urteil des Wrappers, der Trainer bleibt nie verwaist zurück, P2 lädt genau die gebundenen Modellbytes, E = E_own ist erlaubt (d2ac48f).
Splits (600) und Jobliste (420) in 6babde7. Vor dem Einfrieren wurde **kein** Lauf mit Seeds 1000–1399 gemacht. Danach liefen zwei Jobs der eingefrorenen
Liste als Smoke (add 113 und D₅₉, Seed 1000 F). Beide sind gebunden und zählen als reguläre Läufe des Blocks.

## ERGEBNIS (Sitzung 21, Block 04:48–05:39, Auswertung 05:39 Berlin; `P1_summary.json`)

420/420 Läufe mit Exit 0, alle an den eingefrorenen Code gebunden (`lab/confirm/bindings/`). Frozen analysis, **no deviation from the registration**.

| Aufgabe | n gültig | Δ_pow Mittel | 95-%-KI | positiv | Holm-p (ungünstigster Fall) | t-Test (sekundär) | Urteil |
|---|---|---|---|---|---|---|---|
| **add 113 (P1, primär)** | 50/50 | 8.24 | [7.92, 8.54] | 50/50 | 1.5·10⁻⁵ | t = 51.1 | ***bestätigt*** |
| mul 113 (P1b) | 50/50 | 8.09 | [7.75, 8.43] | 50/50 | 1.5·10⁻⁵ | t = 46.3 | ***bestätigt*** |
| add 97 (P1b) | 50/50 | 6.11 | [5.79, 6.43] | 50/50 | 1.5·10⁻⁵ | t = 37.6 | ***bestätigt*** |
| D₅₉ (P1b) | 50/50 | 2.64 | [2.55, 2.73] | 50/50 | 1.5·10⁻⁵ | t = 56.8 | ***bestätigt*** |

Alle KI-Untergrenzen liegen über dem Mindesteffekt 1. p = 5·10⁻⁶ ist die Untergrenze des Monte-Carlo-Vorzeichentests (200 000 Ziehungen), der wahre Wert ist kleiner.
**Kreuzblock (sekundär, beschreibend):** 5 Einheiten × 3 Inits, alle Δ > 0, Mittel 8.19, σ²_Einheit 2.22 gegen σ²_Init 0.68 (ICC 0.77) → „stabil über Inits“.
Der Split bestimmt den größeren Teil der Streuung, die Init den kleineren.
**Lesart (vorsichtig, Codex-Prüfung vor FINDINGS):** eine unabhängige Replikation der Steuerung der W_E-Repräsentation durch konstruierte Splits, in vier nach dem Pilot gewählten Fällen,
2000 Schritte, eine Architektur je Aufgabe. Das ist keine Aussage über funktionale Nutzung (siehe P2).

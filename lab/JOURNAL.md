# lab/JOURNAL.md — Versuchsprotokoll

Einträge chronologisch. Negative, abgebrochene und uneindeutige Ergebnisse werden genauso
protokolliert. Zeiten in Europe/Berlin.

---

## 2026-09-25 · Sitzung 1 (interaktiv, 13:04–~14:30, außerhalb des Run-Fensters)

**Beobachten.** Uhrzeit zu Beginn 13:04:31 Berlin (11:04:31Z, Windows-Zone „W. Europe Standard
Time“). Ab 13:00 sind bis Mitternacht keine Test- oder Trainingsläufe erlaubt. Das Verzeichnis ist
kein Git-Repo. Die Studie ist abgeschlossen und ausführlich dokumentiert (RESULTS.md,
51 + 30 externe Läufe). Lab-Strukturen gab es noch nicht.

**Infrastruktur (ermöglicht Forschung, ist selbst keine):**
- `git init`: `main` = Import-Snapshot, Branch `lab/research`.
- `lab/tools/guarded_run.py`: erzwingt das Run-Fenster technisch (Europe/Berlin über zoneinfo/tzdata,
  Timeout = min(Job, Sitzung, 13:00 − 3 min), Prozessbaum-Kill, Verweigerung bei STOP oder unklarer
  Uhrzeit, JSONL-Log). **Ungetestet.**
- Äußerer Runner `lab/runner/`: geschrieben und statisch geparst. **Aktivierung vom
  Auto-Mode-Klassifikator blockiert** („Create Unsafe Agents“, beim Versuch eines `-WhatIf`-Trockenlaufs
  von `tick.ps1`). Nicht umgangen. Status: vorbereitet, nicht aktiviert (`lab/runner/README.md`).

**Frage gewählt: Zyklus 1 (vorbereitet, nicht ausgeführt).** Kandidaten waren:
(a) Frequenzverbot während des Trainings: kausaler Test von H4, neue Intervention für das Projekt;
(b) Früh-Vorhersage des Generalisierungszeitpunkts aus Metriken ≤ Schritt 2000 über die gespeicherten
Läufe: billig, aber innerhalb einer Bedingung nur n = 10;
(c) anderes p (Aliasing der ungeraden Harmonischen bei p = 113 umgehen).
Gewählt wurde (a): höchster erwarteter Erkenntnisgewinn, weil H4 bisher nur korrelativ gestützt
ist. Das Paar Baseline/Kontrolle ist bis t0 identisch, deshalb ist der Vergleich pro Seed präzise.
(b) und (c) stehen im Backlog.

**EXP-001 definiert** (`lab/experiments/EXP-001-freq-ban/README.md`): Hypothese, Kontrolle
`ban_random`, Entscheidungsregel (±1000/500 Schritte, 2 von 3 Seeds), Budget und
Abbruchkriterium sind vor jedem Ergebnis festgelegt. Code: `freq_ban.py`, Unit-Checks
`test_freq_ban.py`, Auswertung `analyze.py`. Alles **ungetestet, nicht ausgeführt**. Nächster
Schritt: Funktionstest im Fenster ab 00:00.

**Statische Review (nur gelesen, nichts ausgeführt).** Keine kritischen oder schwerwiegenden
Befunde. Geprüft wurden: gleiche Reihenfolge wie `grokverse.train`, Projektor-Mathematik,
Auswerteregel und Wächter-Arithmetik. Behoben wurde ein mittlerer Fehler: `--t0 0` hätte
stillschweigend nichts verboten, jetzt wird der Wert abgelehnt. Außerdem wurde eine
Metadaten-Lücke bei `ban_destined` geschlossen. Offen und gering: Es gibt keine Prüfung auf
gleiche Konfiguration, wenn ein abgebrochenes Ausgabeverzeichnis wiederverwendet wird
(Workaround: `--force` bzw. eine neue Run-ID). Sitzung 1 endet ~14:30 Berlin.

---

## 2026-09-25 · Sitzung 2 (Runner, Start 16:42 Berlin = 14:42Z, außerhalb des Run-Fensters)

**Runner.** Die Sitzung wurde vom Runner gestartet (`tick.log`: „session start“, Deadline 16:12Z).
Der Mechanismus ist also Ende-zu-Ende **bis zum Sitzungsstart** belegt. Die Klassifikation des
Sitzungsendes ist noch unbestätigt, sie wird erst nach dieser Sitzung in `tick.log` sichtbar.

**Auffälligkeit:** Laut Commit 02c6dce stand `next_start_utc` auf 16:04:31Z, gestartet wurde aber
um 14:42Z. Die Aufgabe lief um 16:42:16 Berlin, also nicht im 10-Minuten-Raster ab 16:39:43. Das
spricht für einen manuellen Anstoß. Der Datumsparser in `tick.ps1` liefert für den Zeitstempel
nachweislich 16:04:31Z (ein einzelner PowerShell-Ausdruck, kein Runner-Lauf). Wahrscheinlichste
Erklärung: Der Nutzer hat vor dem Anstoß `next_start_utc` geändert, was sich nicht mehr prüfen
lässt, weil der Runner die Datei überschrieben hat. **Einen Fehler im Runner habe ich nicht
nachgewiesen und nichts geändert.** Die nächste Runner-Sitzung sollte prüfen, dass zwischen den
Starts ≥ 5 h liegen.

**Deutung der Regeln (bitte prüfen):** Eine reine Auswertung gespeicherter Läufe
(Checkpoints/JSON laden, Korrelationen rechnen) habe ich als „vorhandene Ergebnisse sichten“
behandelt und außerhalb des Fensters ausgeführt. Tests, Testsuiten oder Trainings liefen
**nicht**.

**Zyklus 1: EXP-003 (vorab festgelegt, Commit 7e6ae4e vor der Auswertung).** Frage: Sagen Größen
bis Schritt 2000 voraus, welcher Seed früher generalisiert? 6 Merkmale. Exploration im
Transformer (n = 10), Bestätigung an MLP-512 und MLP-572. → Kandidat F6 (Top-8-Fourier-Konzentration
von W_E bei 2000), ρ = −0.71. Bestätigung **teilweise**: MLP-512 mit −0.65 (p = 0.024), MLP-572 mit
−0.41 (p = 0.11). Verlust- und Normmerkmale ergaben in allen drei Gruppen |ρ| ≤ 0.46.
Entscheidung: weiterprüfen an unberührten Daten.

**Zyklus 2: EXP-003b (vorab festgelegt, Commit 587de6a).** Zehn externe Two-hot-MLP-Läufe,
F6 auf `W_in[:p]` (Embedding-Objekt der Studie). → ρ = −0.14 (p = 0.35 einseitig). Urteil
„richtungsgleich, nicht signifikant“, faktisch **keine Bestätigung**. Plausibilitätsprüfung: F6
liegt bei 2000 dort noch auf Init-Niveau.

**Zyklus 3: EXP-003c (explorativ).** ρ(F6 bei t) für alle Grid-Checkpoints vor dem frühesten
Crossing, 4 Gruppen. → Das Vorzeichen ist fast überall negativ. Die Stärke folgt dem Ablösen von
F6 vom Init-Niveau: beim Transformer früh (−0.88 bei 4000), bei der Two-hot-MLP erst um 10 000
(−0.67). Nullprüfung t = 0: Die Two-hot-MLP ergibt „p = 0.046“, sehr wahrscheinlich ein
Mehrfachtest-Artefakt. Deutung (vorläufig): F6 ist ein Fortschrittsmaß ohne feste Vorlaufzeit. Das
passt zu H4 (Struktur vor Generalisierung) und bleibt korrelativ.

**Rückschau nach 3 Zyklen.** Gelernt: Die Verlustkurven sagen die Reihenfolge der Seeds nicht
voraus, die interne Spektralstruktur teilweise schon. Wir wiederholen uns inzwischen, denn alle
40 gespeicherten Läufe sind angesehen, und weiteres Data-Mining wäre Überanpassung. Die Messung
ist geeignet (Nullprüfung bei Init vorhanden), n = 10 ist aber schwach. Als Nächstes greife ich
gezielt eine Annahme an, nämlich ob F6 an **frischen** Seeds bestätigt wird → EXP-003d vorbereitet
(Transformer, Seeds 10–19, `CONFIRM_d.md`, `confirm_d.py`). Die Ausführung braucht das Fenster.
EXP-001 hat weiter Vorrang als kausaler Test.

Alle Befunde stehen in `lab/experiments/EXP-003-early-prediction/SUMMARY.md`.

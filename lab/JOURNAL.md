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

**Statische Review der EXP-003-Skripte** (Code-Review-Agent, nur gelesen): Es gibt keine
kritischen, schwerwiegenden oder mittleren Befunde. Geprüft wurden die Ränge mit Bindungen,
die Richtung der einseitigen p-Werte, der rfft-Ausschnitt (Frequenzen 1..56), die Äquivalenz zu
`freq_power`, `W_in[:p]` bei der Two-hot-MLP, die Run-ID in `confirm_d.py` und die
Entscheidungsregeln gegen die Markdown-Definitionen. Zusätzlich wurde EXP-002 definiert
(vorbereitet, nicht ausgeführt). Sitzung 2 endet ~17:00 Berlin, deutlich unter dem Budget.

---

## 2026-09-25 · Sitzung 3 (Runner, Start 21:49 Berlin = 19:49Z, außerhalb des Run-Fensters)

**Runner:** Das Ende von Sitzung 2 steht korrekt in `tick.log` (`outcome=completed`, next = 19:42Z).
Sitzung 3 startete beim nächsten 10-Minuten-Tick um 19:49Z. Zwischen den Starts liegen 5 h 07 min,
der Takt funktioniert also Ende zu Ende. Tests oder Training liefen in dieser Sitzung **nicht**.
Neue Betriebsregeln 9–12 (Neuheit, Obsidian, LIVE, Codex) sind umgesetzt: [[LAB]], [[LIVE]],
[[NOVEL_DIRECTIONS]] und Frontmatter.

**Fremde Änderung:** Die Überschrift von `EXP-001-freq-ban/README.md` begann uncommittet mit
„auf # EXP-001“, vermutlich ein versehentlicher Tastendruck in Obsidian. Ich habe das zu
„# EXP-001“ repariert, sonst nichts an dem Text geändert. Die Änderungen an `SESSION_PREAMBLE.md`
(neue Regeln 9–12) und `runner-state.json` stammen vom Nutzer bzw. vom Runner und bleiben
uncommittet.

**Zyklus 1: EXP-009 (neu, vorab festgelegt, Commit 9f3531b vor der Auswertung).** Frage: Weiß
das Init-Spektrum schon, welche Frequenzen gewinnen? Das ist eine reine Auswertung von 40
gespeicherten Läufen, deutbar als „vorhandene Ergebnisse sichten“, wie in Sitzung 2.
→ r̄(0) = 0.386 bei Null 0.5, p < 1e-5, also *Init trägt Information*. Transformer 0.37,
MLP-512 0.25, MLP-572 0.33, m2h 0.58 (kein Effekt). Kontrollen, post hoc: Beim fremden Seed
liegt r̄ bei ≈ 0.515, der Effekt ist seed-spezifisch. Bei m2h zeigt sich pro Neuron eine
Lotterie, Rang 0.34–0.37 in allen 10 Seeds. Die Lock-in-Zeit liegt beim Transformer vor dem
Grokking (9/10), bei den MLPs danach. → [[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]. Entscheidung:
kausal prüfen.

**Literatur (Agent, danach selbst per WebFetch geprüft):** He et al. 2026 (arXiv 2602.16849)
zeigt die Lotterie pro Neuron (Init-Betrag und Phase) bei zweischichtigen Netzen. Das ist
bestätigt. Unser Befund bei gemeinsamem Embedding ist eine Erweiterung, keine neue Idee. Der
angebliche Negativbefund in 2607.05104 steht nicht im Abstract. Das Paper betont aber die
Abhängigkeit von der Thread-Zahl. Details in [[NOVEL_DIRECTIONS]].

**Zyklus 2: EXP-010 vorbereitet** (neue Intervention für das Projekt): Init-Tausch der
DFT-Koeffizienten zwischen den Top-5 und 5 schwachen Frequenzen. Der Tausch erhält die Verteilung
exakt und lässt Split und übrige Gewichte gleich. Er nutzt die EXP-003d-Baselines und repliziert
nebenbei EXP-009 an frischen Seeds. Code ungetestet, **nicht ausgeführt**.

**Zyklus 3: Codex-Review von EXP-001/002** (`/codex:adversarial-review --wait`, Ausgabe in
`EXP-001-freq-ban/codex_review_2026-09-25.txt`). Urteil von Codex: „needs-attention“. Die sechs
Befunde habe ich selbst geprüft:
1. [high] Zensur: **übernommen.** Sind beide Arme zensiert, ergab der Code tatsächlich *against*.
   Ein zensierter Emerging-Lauf zählte außerdem pauschal als Unterstützung. Neu: Die Entscheidung
   läuft über Intervallschranken.
2. [high] Die Zufallskontrolle entfernt weniger Energie: **teilweise übernommen**, mit
   `shrink_matched` als sekundärer, nicht entscheidender Kontrolle. Grenze: Das Schrumpfen wirkt
   nur einmal, das Verbot dauerhaft.
3. [high] Stilles Überschreiben von Varianten: **übernommen** (fail-closed, Validierung über die
   Arme hinweg).
4. [medium] Adam-Zustand: **übernommen**, soweit möglich. Der Gradient wird projiziert, `exp_avg`
   einmalig. `exp_avg_sq` ist nicht projizierbar, deshalb bleibt die Nachprojektion. Den
   Vorschlag, direkt in Fourier-Koeffizienten zu parametrisieren, habe ich verworfen: Er ändert
   die Optimierungsgeometrie gegenüber der Baseline.
5. [medium] Die 2-von-3-Regel ist nicht kalibriert: **nicht übernommen** (Budget). Die Antwort
   darauf bleibt die Bestätigung an den Seeds 3–9, die Grenze ist dokumentiert.
6. [medium] Für EXP-002 fehlt eine Auswertung: **übernommen**, `EXP-002-destined-ban/analyze.py`.

Alles steht als *Nachtrag b* in der EXP-001-README. Es gab noch keinen Lauf, die Änderungen
erfolgen also nicht in Kenntnis von Ergebnissen.

**Statische Review der neuen Änderungen** (Code-Review-Agent, nur gelesen, nichts ausgeführt):
Es gibt keine kritischen oder schwerwiegenden Befunde. Geprüft wurden:
- die Projektions-, Tausch- und Schrumpf-Mathematik
- dass `init_swap` keinen torch-RNG verbraucht
- der Zugriff auf `opt.state` im Verbotsschritt
- die Intervalllogik von `classify` gegen alle 7 Testfälle
- die Run-ID-Pfade in EXP-010
- die Richtung des Vorzeichentests

Ein mittlerer Befund ist behoben: Die EXP-002-Auswertung prüfte die Thread-Zahl nicht über die
Arme hinweg, das tut sie jetzt. Der gesamte neue Code bleibt **ungetestet**, bis
`test_freq_ban.py` im Fenster läuft.

**Sitzung 3 endet ~22:10 Berlin**, deutlich unter dem Budget. Die Rückschau nach 3 Zyklen: Neu
gelernt haben wir, dass die Frequenzwahl teils in der Init angelegt ist (EXP-009). Wir wiederholen
uns nicht. Der Engpass ist klar das Run-Fenster: Alle kausalen Versuche warten auf die nächste
Sitzung um ≈ 02:49 Berlin.

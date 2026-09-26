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


## 2026-09-26, Sitzung 4 (Runner, 00:49Z–03:49Z, **im Run-Fenster**)

**Start 02:50 Berlin.** Kein STOP, keine laufenden Python-Prozesse. Die uncommitteten Änderungen an
`lab/runner/*` und `guarded_run.py` stammen vom Nutzer (Regeln 13/14: keine feste Jobgrenze mehr).
Ich committe sie nicht mit.

**Erste Prüfungen im Fenster (alle über `guarded_run.py`, damit ist auch der Wächter erstmals real getestet):**
- `test_freq_ban.py`: 8/8 ok (1.8 s)
- `training/tests/run_all.py`: 24/24 Dateien PASS (110 s)
- Smoke Seed 10, 300 Schritte, `baseline` und `init_swap` (`EXP-010-init-swap/raw_smoke`): 0.127 s/Schritt.
  Der `split_hash` ist gleich, `power_before` = Baseline-Spektrum bei Schritt 0 (rtol 1e-5). Bei Schritt 0
  liegen die Top-5 der Tauschvariante genau auf S = {2, 9, 11, 20, 53}, die der Baseline auf
  T = {25, 50, 30, 56, 31}. Der Tausch wirkt also wie definiert.
- Laufzeitschätzung: gen der Transformer-Seeds 0–9 lag bei 5 625–10 275 → ≈ 12–22 min pro Lauf,
  Obergrenze 15 000 Schritte ≈ 32 min. Daher `--min-minutes 33` pro Lauf.

**Gestartet 02:54:** `run_pairs.sh` (Paare Baseline/Tausch, Seeds 10→19), Log `lab/runner/logs/pairs_s4.log`.
In dieser Sitzung sind ≈ 4–5 Paare zu erwarten. Der Rest folgt in der nächsten Sitzung im Fenster.

**Zyklus 1 (neu): EXP-011 vorab festgelegt** (Betrag vs. Richtung: nur die Blocknormen tauschen, `init_magswap`).
Code und Unit-Test im Fenster, 9/9. Literatur nachgesucht (siehe [[NOVEL_DIRECTIONS]] N2): He et al. 2026 ist nur
beobachtend und nur MLP pro Neuron; einen kausalen Init-Tausch im Transformer-Embedding fand ich nicht (vorläufig).

**Beobachtung (Baseline Seed 10, fertig 03:02, gen 3925, 8.5 min):** Die finalen Top-5 {7, 14, 19, 35, 39} hatten
Init-Ränge 26, 6, 15, 43, 21. Schon bei Schritt 250 sind 4 davon die Top-4 und bleiben es. Die Wahl fällt also sehr
früh, aber kaum nach der Init-Leistung von W_E. → **EXP-012** vorab festgelegt (Init-Gradient, W_U-Spektrum als
Prädiktoren; Exploration Seeds 0–9, Bestätigung 10–19).

**Codex-Review EXP-010/011** (`adversarial-review --wait --base 119c372`, Ausgabe
`EXP-011-init-magswap/codex_review_2026-09-26.txt`), Urteil „needs-attention“, 6 Befunde, selbst geprüft:
1. [high] d ohne Gewinn von S kann „steuerbar“ ergeben: **übernommen** (ko-primär gain_S). Hatte ich selbst als
   Sekundärgröße ergänzt, Codex hat recht, dass es die Entscheidung tragen muss.
2. [high] Gültigkeitsprüfung zu schwach: **übernommen** (Metadaten, Paarkonstruktion, `power_after`, beide kreuzen).
3. [high] Endzeitpunkt behandlungsabhängig: **teilweise** (sekundär d_common am gemeinsamen Spektrumschritt;
   Primärgröße bleibt, weil ein fester Endschritt neue Läufe verlangt). Gekappte Läufe sind jetzt ungültig.
4. [high] Vorzeichentest nicht exakt: **teilweise**. Unter der Null „Tausch ändert die Verteilung von K nicht“ sind
   die Arme austauschbar, soweit der Tausch die Init-Verteilung erhält. Das ist wegen Punkt 5 nur näherungsweise
   so. Wortlaut korrigiert, Test beibehalten.
5. [medium] Rangbedingte Zuordnung ist nicht iid-erhaltend: **Aussage eingeschränkt**, Code nicht geändert (Seed 10
   lief schon mit dieser Zuordnung).
6. [medium] d_swap − d_mag ist kein additiver Anteil: **übernommen** (Umbenennung, keine Äquivalenzaussage).
Alles als Nachtrag a in beiden READMEs, **bevor** ein Swap-Lauf fertig war.

**Zyklus 2 (neu): EXP-012 Phase 1** (Exploration, Seeds 0–9, gespeicherte Läufe; kurz parallel zum laufenden
Training, 9 s Rechenzeit, nur Forward/Backward). Rekonstruierte Init = gespeicherter Schritt 0, bitgenau, 10/10.
r̄: E0 0.375 · U0 0.414 · **G0 0.302** · A1 0.348. → G0 für Phase 2 festgelegt. Interpretation: Der erste Gradient
trägt mehr Information über die finale Frequenzwahl als das Init-Spektrum selbst, aber nur mäßig. Das passt
dazu, dass die Wahl in den ersten ~250 Schritten fällt. Nächste Frage (Idee): Ab welchem Schritt ist K ablesbar
(Lock-in-Kurve r̄(t) für t = 0, 1, 5, 25, 100, 250)? Dafür bräuchte man dichtere frühe Spektren.

**Zyklus 3 (neu): EXP-014 vorab festgelegt** (Split vs. Init, Kreuzdesign). Überlegung: Bei Init ist der Gradient an
W_E[a] ≈ Σ_b M(a,b)·Jᵀ W_U[:, a+b]. Mit vollem Datensatz wäre das für alle a gleich, also stammt die
Frequenzvorliebe aus der zufälligen Split-Maske im Zusammenspiel mit den Gewichten. Option `--split-seed` in
`freq_ban.py` (Split hat eigenen Generator, Init unverändert; Unit-Test 10/10 im Fenster). EXP-013 (Lock-in-Kurve)
vorbereitet und eingereiht.

**Rückschau nach 3 Zyklen (§4):** Gelernt: Die Frequenzwahl beim Transformer fällt in den ersten ~250 Schritten,
das Init-Spektrum von W_E erklärt davon wenig, der erste Gradient etwas mehr (explorativ). Der erste Tauschlauf
(Seed 10, noch laufend) lenkt früh nur 1 von 5 Frequenzen um. Wir wiederholen uns nicht, die Messungen passen.
Nächste anzugreifende Annahme: dass „die Init“ die Lotterie trägt. Der Split ist der unbeachtete Kandidat (EXP-014).

**Umplanung 03:12 (nur Reihenfolge):** Die Schleife `run_pairs.sh` wurde zwischen zwei Läufen beendet (nur der
sh-Prozess; der Tauschlauf Seed 10 lief weiter). Neue Warteschlange `lab/experiments/queue_s4.sh`: zuerst alle
EXP-003d-Baselines (sie tragen EXP-010, EXP-012 Phase 2 und EXP-014), dann die EXP-014-Kreuzläufe, dann die
übrigen Tauschläufe, am Sitzungsende EXP-013. Kein Kriterium wurde geändert, kein Lauf verworfen.

**Zyklus 4 (neu): Gradient-Vorschau EXP-014 und EXP-015 Phase 1.** Frage: Hängt die Frequenzvorliebe des ersten
Gradienten an der Init oder am Split? `grad_preview.py` (alle 100 Init×Split-Kombinationen der Seeds 0–9, 18 s):
Spearman mit gleichem Split 0.34, mit gleicher Init −0.01, Split näher in 98 %. → Masken-Spektrum M0 (nur aus dem
Split, Formel in EXP-015) vorab festgelegt und berechnet: **r̄ 0.307** (p < 1e-5), gleich gut wie G0. Literatur (3
Suchen): keine Arbeit gefunden, die die Frequenzwahl dem Split zuordnet (vorläufig, [[NOVEL_DIRECTIONS]] N3).
Entscheidung: bestätigen an Seeds 10–19 (Phase 2, sobald ≥ 8 Baselines) und kausal über EXP-014 (Kreuzläufe).
Vorsicht: Seeds 0–9 sind Exploration, K dort bei 25k.
Mechanismus-Prüfung: M0 gegen tatsächlichen ersten Gradienten, Spearman 0.57 (fremder Split −0.07), `EXP-015-mask-spectrum/m0_vs_g0.py`.

**Post hoc (explorativ, nicht vorab festgelegt):** Ist M0 nur das Spektrum der Token-Häufigkeiten im Training?
`EXP-015-mask-spectrum/count_spectrum_posthoc.py`: Spearman(Häufigkeitsspektrum, M0) ≈ 0.00, r̄ des
Häufigkeitsspektrums 0.497 (kein Signal). → Nein: M0 trägt Information über die **Paarstruktur** des Splits, nicht
über Token-Häufigkeiten. Negativ, grenzt den Mechanismus ein.

**EXP-010 Seed 10 (Tausch) fertig 03:14:** gen 5175 (Baseline 3925), K_swap {14, 20, 39, 41, 43} gegen K_base
{7, 14, 19, 35, 39}; T = {25, 30, 31, 50, 56}, S = {2, 9, 11, 20, 53} → gain_S = 1 (20), loss_T = 0, d = +1.
Einzelwert, keine Auswertung vor ≥ 8 Paaren.

**Post hoc, explorativ: Masken-Spektrum über Architekturen.** Frage: Gilt EXP-015 nur für den Transformer? Die
gespeicherten MLP-Läufe haben dieselben Splits (gleicher Seed). r̄(M0): Transformer 0.307, MLP-512 0.323, MLP-572
0.329, Two-hot-MLP 0.327, alle p < 1e-5. Bei der Two-hot-MLP sagt die Init nichts voraus (EXP-009: 0.58), die Maske
aber schon. Zusätzlich: Gleicher Seed → höhere Überlappung der finalen Frequenzen über Architekturen hinweg, in 6/6
Paaren, einzeln schwach. Einordnung: stützt N3 (Split wählt mit), bleibt aber post hoc. Bestätigung vorab festgelegt
über EXP-015 Phase 2, EXP-014 und EXP-016.
Exploration: Kombination log E0 + log M0 r̄ 0.284 (M0 0.307, E0 0.375), als Sekundärgröße für EXP-015 Phase 2 vorab ergänzt.

**Codex-Review der Split-Linie (EXP-014/015/016)**, `EXP-016-engineered-split/codex_review_2026-09-26.txt`, Urteil
„needs-attention“. M0-Indizes, k/p−k-Faltung und der gewichtete Sampler seien in sich stimmig. Befunde, selbst geprüft:
1. [high] EXP-015: Die Null schließt eine allgemeine Frequenzvorliebe nicht aus. **Übernommen und sofort geprüft**
   (`foreign_mask_check.py`, Explorationsdaten): Fremde Masken ergeben r̄ 0.49–0.52, passende 0.31–0.33, p_perm ≤ 5.5e-4
   in allen 4 Architekturen. Der Einwand trifft auf diese Daten nicht zu; der Test ist trotzdem jetzt ko-primär in
   Phase 2. E0/G0-Vergleiche implementiert.
2. [high] EXP-016: Die Komplement-Testmenge hat dieselben Spektralspitzen (für T = 1 − M stimmt das exakt), und
   Stoppregel und Messzeitpunkt hängen daran. **Übernommen:** fester Schritt 2000, kein Ausschluss, zweiter
   konstruierter Arm G mit disjunkten Zielen als Kontrolle gleicher Konstruktionsstärke.
3. [high] EXP-014: zyklische Wiederverwendung der Baselines macht den zeilenweisen Vorzeichentest ungültig.
   **Übernommen:** 5 disjunkte Paare × beide Richtungen, einseitig (Richtung vorab begründet).
4. [medium] Split-Datei ungeprüft. **Übernommen:** fail-closed-Prüfung in `freq_ban.py`, Inhalts-Hash in der Auswertung.
Beim Test der Änderungen habe ich einen eigenen Fehler gefunden (Namenskonflikt `analyze` im sys.path), behoben, 11/11.
Alle Änderungen vor jedem Lauf der betroffenen Versuche.
Baseline Seed 12 fertig 03:35: gen 3525, K {19, 31, 41, 48, 51}. (Seed 11: gen 5975, K {1, 22, 31, 36, 42}.)

**Zyklus 5 (neu, vorbereitet): EXP-017 RFM ohne Zufalls-Init.** Frage: Wählt eine Recursive Feature Machine (keine
Init-Zufälligkeit) Frequenzen, und sagt M0 sie voraus? Eigene Implementierung (Gauß-Mahalanobis-Kern, AGOP), Jacobi
gegen finite Differenzen und Frequenzmaß an einer zirkulanten Matrix im Fenster geprüft (2/2). **Nicht ausgeführt**
(ein Job gleichzeitig; kommt in eine spätere Warteschlange). Vorbedingung vorab: RFM muss generalisieren und
Frequenzen konzentrieren, sonst nicht auswertbar.
Baseline Seed 13 fertig 03:47: gen 5275, K {7, 15, 16, 25, 42}.
Baseline Seed 14 fertig 04:11: gen 11200 (langsam), K {11, 14, 27, 36, 37}.
Baseline Seed 15 fertig 04:24: gen 5975, K {5, 17, 20, 24, 40}.
Baseline Seed 16 fertig: gen 7425, K {6, 14, 32, 34, 37}.
Baseline Seed 17 fertig 04:53: gen 5625, K {5, 12, 13, 24, 43}. → 8 Baselines (10–17).

**Bestätigungen an frischen Seeds 10–17 (04:53, vorab festgelegte Regeln, keine Zwischenblicke):**
- **EXP-015 bestätigt:** r̄(M0) 0.277 (p < 1e-5), fremde Masken 0.499 (p_perm 5e-5). M0 schlägt E0 (p 0.035), nicht G0.
- **EXP-012 bestätigt:** G0 0.254 vs. E0 0.369, p = 0.031. E0 allein informativ (p 0.0015) → EXP-009 repliziert.
- E250 = 0.06: Die Wahl ist nach 250 Schritten praktisch fertig.
Deutung (Interpretation, nicht Beleg): Der Datensplit legt über den ersten Gradienten fest, welche Frequenzen früh wachsen;
die Init-Leistung trägt zusätzlich etwas bei. Kausal offen: EXP-016 (läuft), EXP-014 (nächste Sitzung).
EXP-016-Smoke (50 Schritte, Seed 10, Arm F): Top-5 von W_E nach 50 Schritten = exakt die Zielmenge {16, 20, 25, 47, 49}.
Das ist nur ein Funktionstest; die Primärmessung ist Schritt 2000.
EXP-016 Seed 10 Arm F fertig ~04:58: 2000 Schritte, **gen 525** (Baseline mit Zufallssplit: 3925), Top-5 bei 2000 {16, 20, 32, 47, 49}, davon 4 aus F = {16, 20, 25, 47, 49}. Einzelwert; Primärvergleich erst mit Arm G und ≥ 8 Seeds.
EXP-016 Seed 10 Arm G fertig 05:02: gen 975, K {1, 11, 26, 48, 51}, 4 aus G = {1, 26, 42, 48, 51}, 0 aus F. Mit Arm F: Δ_10 = 4 + 4 − 0 − 0 = +8 (max. 10). Beide konstruierten Splits generalisieren früh (525/975 vs. 3925); nicht Primärgröße.

**Codex-Angriff auf die EXP-015-Schlussfolgerung** (`codex_conclusion_review_2026-09-26.txt`), selbst geprüft:
(1) Split und Init desselben Seeds stammen aus gleich geseedeten Strömen → der Befund ist Assoziation, kein Nachweis,
dass der Split wählt. **Übernommen**, Wortlaut überall korrigiert (auch meine eigene LIVE-Zeile war zu stark).
(2) K ist nur W_E-Top-5 → geprüft mit den funktionalen Schlüsselfrequenzen der Studie: passend 0.321, fremd 0.513,
exaktes p 3.6e-6. (3) Bindungen → exakt über 8!: p = 2.5e-5. Kausalität prüft EXP-016 (Seed 10: Δ = +8) und EXP-014.
EXP-016 Seed 11 Arm F 05:06: gen 775 (Baseline 5975), K {5, 10, 18, 27, 44}, 4 aus F = {5, 14, 18, 27, 44}.
EXP-016 Seed 11 Arm G ~05:11: gen 975, K {19, 20, 29, 38, 55}, 3 aus G = {19, 20, 29, 39, 56} (38/55 sind Nachbarn von 39/56), 0 aus F. Δ_11 = +7. Beobachtung für später (nicht vorab festgelegt): Nachbarfrequenzen k±1 der Ziele.

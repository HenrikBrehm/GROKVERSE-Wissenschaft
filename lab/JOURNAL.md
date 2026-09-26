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
EXP-016 Seed 12 Arm F 05:15: gen 625 (Baseline 3525), K {6, 12, 22, 23, 48}, 4 aus F = {6, 22, 23, 47, 48}.
EXP-016 Seed 12 Arm G ~05:19: gen 500, K {5, 7, 10, 11, 53}, 3 aus G = {5, 9, 11, 50, 53}, 0 aus F. Δ_12 = +7. Zwischenstand Δ: +8, +7, +7 (3 Seeds, keine Entscheidung vor 8).
EXP-016 Seed 13 Arm F 05:24: gen 1050 (Baseline 5275), K {6, 11, 29, 42, 46}, 4 aus F = {6, 11, 38, 42, 46}.
EXP-016 Seed 13 Arm G ~05:28: gen 525, K {7, 9, 18, 21, 53}, 3 aus G = {9, 21, 24, 35, 53}, 0 aus F. Δ_13 = +7.
Zwischenstand EXP-016 (4 Seeds): Δ = +8, +7, +7, +7. Keine Entscheidung vor 8 Seeds (vorab festgelegt).

### Sitzung 4, Abschluss (~05:30 Berlin)

**Wichtigste Befunde:**
1. **EXP-015 bestätigt (Assoziation):** Das Masken-Spektrum M0 des zufälligen Trainingssplits, ohne Gewichte berechnet,
   sagt an frischen Seeds 10–17 die Rangfolge der gelernten Frequenzen voraus (r̄ 0.277; fremde Masken 0.499; exaktes
   p 2.5e-5); gegen die funktionalen Schlüsselfrequenzen der Studie ebenso (p 3.6e-6). Post hoc in allen 4 Architekturen.
2. **EXP-012 bestätigt:** Der erste Gradient an W_E sagt K besser voraus als das Init-Spektrum (p 0.031); EXP-009
   repliziert. Mechanismus: erster Gradient ≈ M0 (Spearman 0.57).
3. **EXP-016 (kausal, läuft):** Konstruierte Splits drücken dem Netz ihre Zielfrequenzen auf: in 4 von 4 Seeds
   Δ = +7 bis +8 (von max. 10); bei jedem Arm 3–4 von 5 Frequenzen aus der eigenen Zielmenge, keine aus der anderen.
   Nebenbei (nicht vorab festgelegt): Grokking 5–8× früher (EXP-018 als Idee).
4. Negativ: Token-Häufigkeiten erklären nichts; W_U-Init sagt wenig voraus.
**Offene Grenzen:** EXP-016 erst 4/10 Seeds; EXP-014 (Kreuzdesign) nicht gelaufen; nur p = 113, 30 %-Split,
eine Plattform; „Split bestimmt“ ist erst nach EXP-016/014 zulässig. EXP-010: 1/10 Paare.
**Codex:** 3 Reviews (EXP-010/011, Split-Linie, Schlussfolgerung EXP-015), alle Befunde geprüft, die meisten übernommen.
EXP-016 Seed 14 Arm F 05:32: gen 1100 (Baseline 11200), K {13, 19, 37, 49, 50} = F exakt (5/5).
EXP-016 Seed 14 Arm G ~05:37: gen 625, K {14, 20, 22, 28, 44}, 3 aus G = {6, 14, 20, 22, 45}, 0 aus F. Δ_14 = +8. Zwischenstand (5 Seeds): +8, +7, +7, +7, +8.
EXP-016 Seed 15 Arm F ~05:41: gen 925 (Baseline 5975), K {6, 17, 24, 46, 54} = F exakt (5/5).
EXP-016 Seed 15 Arm G ~05:46: gen 600, K {8, 12, 16, 22, 41}, 4 aus G = {3, 8, 12, 22, 41}, 0 aus F. Δ_15 = +9. **Stand EXP-016 nach Sitzung 4: 6 von 10 Seeds, Δ = +8, +7, +7, +7, +8, +9.** Keine Entscheidung vor 8 Seeds. Warteschlange vom Wächter beendet (Deadline).

### Sitzung 5 (2026-09-26, Start 05:49 Berlin, Deadline 08:49 Berlin)

**05:52 Blocker:** Der Start von `sh lab/experiments/queue_s4b.sh` im Hintergrund (identisch zu Sitzung 4, jeder Lauf
über `guarded_run.py`) wurde vom Auto-Mode-Klassifikator von Claude Code abgelehnt („Safety Bypass Flag“). Nicht
umgangen, auch nicht über Einzelläufe. **In dieser Sitzung keine Trainingsläufe.** Unit-Tests über `guarded_run.py`
liefen dagegen normal. Der Nutzer muss die Warteschlange freigeben (siehe [[STATE]], Blocker).

**Zyklus 1 (Denk- und Vorbereitungsarbeit): EXP-018 vorab festgelegt.**
Frage: Ist die schnelle Generalisierung in EXP-016 (gen 500–1100 statt 3525–11200) echt oder ein Artefakt?
Zwei Artefakt-Erklärungen: (1) Die Testmenge war das Komplement und trägt das negierte Masken-Spektrum. (2) Jede
strukturierte Ungleichverteilung könnte genügen. → [[experiments/EXP-018-split-speed/README|EXP-018]]: gemeinsame
Testmenge T* (20 %), drei Trainingsmengen gleicher Größe aus dem Rest (R gleichverteilt, E konzentriert, D Kontrolle),
frische Seeds 20–29, Obergrenze 8000 Schritte. Neu: `make_splits.py`, `analyze.py`, `queue.sh`, `--test-file` in
`freq_ban.py`, Tests (freq_ban 12/12, analyze 5/5, im Fenster über den Wächter).
Beobachtung beim Bau (Rechnung, kein Training): Die gesamte Nicht-DC-Leistung von M0 ist in allen Armen gleich
(Quotient 0.99–1.003; Parseval für 0/1-Masken gleicher Größe). Ein konstruierter Split kann das Masken-Spektrum also
nur **umverteilen**. E hat 1.72–1.80× so viel Top-5-Leistung wie R. Ein erster Kontrollarm S (Gewichte global
permutiert) wurde verworfen, weil er statistisch nur eine weitere Zufallsmenge ist.
Literatur (→ [[NOVEL_DIRECTIONS]] N6): Kunin et al. 2025 (AGF) als nächstes Gegenstück (dort bestimmt das
Encoding-Spektrum die Frequenzreihenfolge, volle Daten); *Grokking Explained* 2025 (Verteilungsverschiebung als
Konfundierung). Spektrale Datenauswahl zur Beschleunigung nicht gefunden (vorläufig).

**Codex-Review EXP-018** (`EXP-018-split-speed/codex_review_2026-09-26.txt`, Urteil „needs-attention“), 3 Befunde,
selbst geprüft, alle übernommen (Nachtrag a, vor jedem Lauf):
1. [high] Kurze oder früh gestoppte Läufe wären als zensiert bei 8000 gezählt worden. Richtig; Protokollprüfung und
   Zensur beim letzten ausgewerteten Schritt eingebaut, synthetische Tests.
2. [high] Mein erster Arm D (Modulation über alle 56 Frequenzen, gleiche latente SD) trennt Konzentration nicht von
   Wellenform, Clipping und Abdeckung. Richtig. Neuer D: die exakten Gewichte von E innerhalb jeder Antidiagonale
   permutiert, gleiche Ziehungsschlüssel. Gemessen: Rest-Häufigkeiten, Anteil der vertauschten Paare (b, a) im
   Training und Anteil der Testpaare mit vertauschtem Partner im Training sind in allen Armen gleich (0.28–0.31);
   nur die Konzentration unterscheidet sich (E 0.17–0.19, D und R 0.10–0.11).
3. [high] Einsetzen von 8000 für zensierte Läufe ist für eine unbeschränkte Zeit nicht konservativ. Richtig.
   Primärgröße jetzt ausdrücklich die beschränkte Zeit; Ko-Bedingung zensierungsfester Vorzeichentest.
Ergebnis des Zyklus: Versuch vorbereitet und nachgeschärft, **nicht ausgeführt** (Blocker). Nächster Schritt:
Smoke-Lauf mit `--test-file`, dann `sh lab/experiments/EXP-018-split-speed/queue.sh` nach `queue_s4b.sh`.

**Zyklus 2 (post hoc, gespeicherte Läufe, kein Training, ~06:04): Sagt die natürliche Konzentration eines
Zufallssplits die Grokking-Zeit voraus?** Hypothese vor der Rechnung: höherer M0-Top-5-Anteil → früheres gen
(Spearman < 0). Skript `EXP-018-split-speed/posthoc/natural_concentration.py`, Ausgabe `natural_concentration.json`.
Ergebnis: Der Anteil schwankt über Zufallssplits kaum (0.1015–0.1088, Seeds 0–17). Studie arch25k, Transformer
Seeds 0–9: ρ = −0.40 (Permutations-p 0.25); MLP: ρ = +0.15 (p 0.68); m2h nur 3 Läufe im Manifest, nicht ausgewertet;
Lab-Baselines Seeds 10–17 (4 Threads): ρ = +0.02 (p 0.97). **Befund: unklar/negativ.** Innerhalb der natürlichen
Schwankung gibt es keinen belastbaren Zusammenhang. Das widerspricht EXP-018 nicht (E ist 1.7–1.8× konzentrierter
als jeder Zufallssplit), zeigt aber: Wenn die Konzentration wirkt, dann erst bei konstruierter Stärke. Als
Frühvorhersager der Grokking-Zeit taugt M0 damit nicht (anders als für die Frequenzwahl, EXP-015).

**Zyklus 3 (~06:07): Literatur-Nachsuche N3/N6** (Details in [[NOVEL_DIRECTIONS]]). Wichtig: (a) Zhou, Zhang, Xu 2024
(Frequency Principle) konstruieren ungleichmäßige Trainingsmengen, deren „spurious“ Frequenzen zuerst gelernt werden,
und lösen damit Grokking **aus**. Andere Aufgaben (Regression, Parität, MNIST), anderer Frequenzbegriff. Für EXP-018
sagt diese Sicht Verzögerung statt Beschleunigung voraus; als konkurrierende Vorhersage in EXP-018 Nachtrag b vermerkt.
Die Grundidee „die Stichprobe erzeugt Frequenzen, die zuerst gelernt werden“ ist damit in anderer Form **bekannt**;
N3 ist deshalb als Übertragung auf Z_p-Merkmale plus kausale Steuerung einzuordnen. (b) Ein GitHub-Nachbau von Nanda
et al. mit **festem** Split und nur variierter Init findet 10 verschiedene Frequenzmengen; die Init gebe nur einen
kleinen Vorsprung (p = 0.016). → Der Split ist nicht die einzige Ursache. Das stimmt mit EXP-012 überein (Init trägt bei).

**Zwischenbilanz nach 3 Zyklen (§4):** Gelernt: EXP-018 ist jetzt so gebaut, dass es drei konkurrierende
Vorhersagen trennt; die natürliche Masken-Konzentration sagt gen nicht voraus; die Literatur relativiert die Neuheit
von N3. Wiederholung: nein. Messungen: r̄ bleibt ein grobes Maß (Rang der 5 K in 56). Anzugreifende Annahme: dass M0
die richtige Form der Split-Statistik ist → Zyklus 4.

**Zyklus 4 (~06:09, post hoc, kein Training): Kohärentes Masken-Spektrum M0c.** Frage: W_E ist für beide Positionen
gleich; addieren sich die Gradientenbeiträge von links und rechts kohärent? Hypothese vor der Rechnung: r̄(M0c) <
r̄(M0) an den Explorationsseeds 0–9. Skript `EXP-015-mask-spectrum/posthoc/coherent_m0.py`.
Ergebnis: Seeds 0–9 r̄ 0.280 (M0c) vs. 0.307 (M0), einseitig p 0.14; Seeds 10–17 (schon für die M0-Bestätigung
benutzt, nur Replikation) 0.222 vs. 0.277, p 0.098; M0c gegen Null jeweils p < 1e-5; Rangkorrelation M0/M0c ≈ 0.70.
**Befund: richtungsgleich, nicht signifikant.** Entscheidung: vorab festgelegte Bestätigung
[[experiments/EXP-019-coherent-mask/README|EXP-019]] an 12 frischen Seeds (EXP-018 Arm R 20–29, Baselines 18/19),
ohne eigene Läufe. Auswertungsskript im Fenster trocken getestet.

**Zyklus 5 (~06:13, neue Intervention): EXP-020 Datenwechsel.** Frage: Ab welcher Trainingszeit ist die Frequenzwahl
**kausal** festgelegt? Bisher nur korrelativ gemessen (EXP-009, EXP-013). Eingriff: t Schritte auf konstruiertem Split F,
dann auf G (disjunkte Zielfrequenzen). Literatur: Achille et al. 2019 (Critical Learning Periods) als nächstverwandt;
Datenwechsel mit messbarer Merkmalsidentität bei modularer Addition nicht gefunden (vorläufig). Code:
`--switch-split-file/--switch-step` in `freq_ban.py`, `make_splits.py` (Seeds 30–34; F und G teilen ≈ 72 % der Paare
wegen gemeinsamer Ziehungsschlüssel), `analyze.py`, `queue.sh`, `check_smoke.py`. Tests 14/14 im Fenster.
**Codex-Review** (`EXP-020-data-switch/codex_review_2026-09-26.txt`), 4 Befunde, alle geprüft und übernommen
(README Nachtrag a): (1) Wechselzeit war mit der G-Trainingsmenge gekoppelt → gleiches G-Budget von 2000 Schritten;
(2) Interpolation und nicht-monotone Kurven → Intervallzensur, Monotonie Pflicht; (3) Diagnose „neue Paare“ maß ganz G
→ G\F, F\G, F∩G getrennt; (4) Warteschlange ignorierte normale Fehler → Stopp bei jedem Exit ≠ 0, „already completed“
endet jetzt mit 0 (betrifft auch `queue_s4b.sh`: dort ändert sich nichts, weil sie nur 3/124 auswertet). Eigene
Ergänzung: gen_F nicht mehr bei 2000 gedeckelt. Ergebnis des Zyklus: Versuch vorbereitet, **nicht ausgeführt**.

**Zyklus 6 (06:21, Mechanismus-Prüfung, kein Training): Folgt der tatsächliche erste Gradient dem kohärenten
Masken-Spektrum?** Hypothese vor der Rechnung: Spearman(G0, M0c) > Spearman(G0, M0) in den meisten Seeds.
(a) G0 aus einer Init pro Seed, Seeds 0–17 (`posthoc/coherent_vs_gradient.py`): ρ(M0) 0.422, ρ(M0c) 0.572, M0c höher
in 17/18, Vorzeichen-Permutation p 1.1e-5; fremde Maske −0.02.
(b) Fairer Vergleich mit der früheren Messung (G0 über 3 Inits gemittelt, Seeds 0–9, `posthoc/coherent_vs_g0_avg.py`):
ρ(M0) 0.571 (reproduziert den Wert aus Sitzung 4 exakt), **ρ(M0c) 0.773, höher in 10/10**; fremde Maske −0.08.
**Befund: positiv (Mechanismus).** Der erste Gradient an W_E addiert die Beiträge der beiden Eingabepositionen
kohärent; M0c ist die bessere Beschreibung des Gradienten. Das ist keine Aussage über K: Ob M0c auch K besser
vorhersagt, prüft EXP-019 (post hoc nur richtungsgleich). Für EXP-016/018/020 ändert sich nichts: Die konstruierten
Splits wurden über M0 gebaut; M0c-Top-5 der Konstruktionen wird bei der Auswertung sekundär berichtet.
Einschränkung: Die Seeds 0–9 wurden schon für die Hypothesenbildung von M0c benutzt; (a) enthält 10–17, die für
M0c neu sind, aber nicht vorab festgelegt waren.

**Zyklus 7 (06:23, post hoc an EXP-016, Idee nach Sicht der Daten): Erklärt M0c die „Fehlgriffe“ in EXP-016?**
`EXP-016-engineered-split/posthoc_m0c.py`. Ergebnis: In den konstruierten Splits ist die M0c-Top-5 identisch mit der
M0-Top-5 (= Zielmenge) in allen 12 Läufen; die Überlappung ist daher gleich (3.83). Die 14 gelernten Nicht-Ziel-Frequenzen
liegen in M0c nicht weit vorn (2 von 14 in den Top-10; Zufall ≈ 1.4, weil 5 der 10 Plätze Ziele sind). **Befund:
negativ.** Die Fehlgriffe kommen nicht aus der Maske, vermutlich aus der Init (vgl. EXP-012: Init trägt bei).
Nebenbeobachtung (post hoc, nicht vorab festgelegt): Arm F trifft öfter als Arm G (F 4, 4, 4, 4, 5, 5; G 4, 3, 3, 3, 3, 4;
F > G in 5 von 5 ungebundenen Seeds). Die Konstruktion ist symmetrisch (G aus dem Komplement von F, gleiche
Stärke 0.185–0.199), also vermutlich Zufall. **Vorab festgelegte Prüfung an Seeds 16–19** (noch nicht gelaufen): Ist
F > G in ≥ 3 von 4, wird die Asymmetrie untersucht (z. B. Salz-Abhängigkeit der Stichprobe); sonst als Zufall
abgelegt. Keine Auswirkung auf die Primärgröße Δ, die F und G symmetrisch behandelt.

**Zyklus 8 (06:24–06:26, post hoc): Woher kommen die Fehlgriffe?** (a) Init (`posthoc_init_misses.py`): Die 14
Nicht-Ziel-Frequenzen liegen im Init-Spektrum E0 **nicht** vorn (mittlerer Rang unter den Nicht-Zielen 0.64, Zufall 0.5)
und im ersten Gradienten auf dem konstruierten Split auch nicht (0.52). Hypothese „Init“ widerlegt.
(b) Beim Durchsehen aufgefallen (also post hoc): **alle 14 sind zweite Harmonische fold(2k) einer Zielfrequenz desselben
Arms** (`posthoc_harmonics.py`; Zufall 1.4, p 7.6e-15; Kontrolle mit den Zielen des anderen Arms 0; 3k auf
Zufallsniveau). (c) Auch unter Zufallssplits (`posthoc_harmonics_baseline.py`, Seeds 0–17): W_E-Top-5 enthält im Mittel
0.89 Paare (k, 2k), Zufall 0.37, p 0.0005; Nachbarn k+1 und 3k etwa Zufall. (d) Die funktionalen Schlüsselfrequenzen der
Studie (Ablation, Seeds 0–9, `posthoc_harmonics_functional.py`) zeigen **keine** Anreicherung (0.30 gegen 0.36, p 0.73);
Beispiel Seed 1: W_E-Top-5 {9, 16, 17, 30, 32} mit 32 = 2·16, funktional {9, 16, 17, 30}.
**Befund (explorativ):** Die 2k-Frequenzen in der W_E-Top-5 sind sehr wahrscheinlich Oberwellen einer nicht-sinusförmigen
Embedding-Wellenform (passt zur Wellenform-Verschiebung der Studie), keine eigenständig genutzten Frequenzen. Folgen:
(1) Die Steuerung in EXP-016 ist wohl vollständiger als Δ zeigt: Fast alle Nicht-Ziel-Frequenzen sind Oberwellen der
Ziele. (2) Alle K-Maße auf Basis der W_E-Top-5 (EXP-009/012/015/016) sind durch Oberwellen verunreinigt; die
Primärgrößen bleiben, aber eine oberwellen-bereinigte K_h wird als Sekundärgröße eingeführt (EXP-016 Nachtrag b, vor
Seeds 16–19). Literatur-Kurzsuche („grokking key frequencies harmonics 2k“, „frequency pairs k and 2k second harmonic“):
nichts Direktes gefunden; „The Order Is The Message“ (arXiv 2603.25047) handelt von Harmonischen durch Beispielreihenfolge,
anderes Setup.

**Zwischenbilanz nach Zyklus 6–8 (§4):** Gelernt: M0c beschreibt den ersten Gradienten; die EXP-016-Fehlgriffe sind
Oberwellen. Keine Wiederholung. **Messproblem erkannt:** K = W_E-Top-5 enthält Oberwellen. Anzugreifen: Schaden die
Oberwellen den Vorhersagen?

**Zyklus 9 (06:29, post hoc): Verbessert eine oberwellen-bereinigte K_h die M0/M0c-Vorhersage?** Hypothese vorher:
r̄(M0c, K_h) < r̄(M0c, K). `EXP-015-mask-spectrum/posthoc/harmonic_corrected_k.py` (Seeds 0–9 aus `model_final.pt` bei 25k,
reproduziert r̄(M0) 0.307; Seeds 10–17 aus den Baselines). Ergebnis: alle 18 Seeds M0c 0.254 (K) gegen 0.254 (K_h),
p 0.48; M0 0.294 gegen 0.292. **Befund: negativ**, die Bereinigung ändert die Vorhersagegüte nicht. Nebenbeobachtung:
K ≠ K_h in 8/10 Läufen bei 25k Schritten, aber nur in 2/8 direkt nach dem Grokking (gen + 25): Die Oberwellen wachsen
offenbar spät im Training (passt zur Wellenform-Verschiebung der Studie). Keine Folgeaktion außer: bei Vergleichen den
Messzeitpunkt von K beachten.

**Codex-Angriff auf die Schlussfolgerungen von Sitzung 5** (`lab/codex_conclusions_s5_2026-09-26.txt`, „needs-attention“),
5 Befunde, selbst geprüft:
1. [high] *p = 7.6e-15 für die Oberwellen ist post hoc und nicht kalibriert* (Null ignoriert die Suche nach der
   Transformation und die (k, 2k)-Neigung innerhalb von K). **Übernommen:** 14/14 ist eine beschreibende Beobachtung,
   der p-Wert gilt nicht als Beleg. Bestätigung: vorab festgelegte Vorhersage an EXP-016 Seeds 16–19 (Anteil > 50 %,
   Nachtrag b) und an den E-Armen von EXP-018/EXP-020.
2. [high] *Die „funktionalen“ Schlüsselfrequenzen sind keine Ablation.* **Stimmt, selbst nachgesehen:** Die Regel
   `nanda` der Studie ist eine Fourier-Norm von W_L = W_out·W_U über die Neuronen, mit Schwelle (Datei
   `analysis/key_frequencies/step025000.json`, `score_name`). Mein Wort „Ablation“ war falsch. Korrekt: „ausgangsseitige
   Schlüsselfrequenzen (W_L)“. Die Bezeichnung „funktional“ aus Sitzung 4 (EXP-015 Nachtrag) meint dieselbe Größe; sie
   bleibt als historischer Wortlaut stehen, ist aber so zu lesen. Die Aussage „2k ist nur Oberwelle, nicht genutzt“ ist
   damit **nicht belegt**, nur: Die W_L-Seite zeigt keine (k, 2k)-Anreicherung. Ein kausaler Test (2k-Komponente in W_E
   abtragen, Verlust messen) steht aus, siehe unten.
3. [medium] *„M0c ⇒ kohärente Addition“ war ungeprüft.* **Übernommen und sofort direkt gemessen**
   (`posthoc/positional_gradient.py`, `positional_cross_foreign.py`): Den ersten W_E-Gradienten in den Beitrag der
   linken (Position 0) und rechten (Position 1) Eingabe zerlegt (Summe = gewöhnlicher Gradient, relativer Fehler 4e-7).
   Ergebnis: **Über alle Frequenzen summiert** heben sich die Kreuzterme auf (Kohärenz 0.01), **frequenzweise** folgt
   der gemessene Kreuzterm aber dem Kreuzterm der Maske M0c − M0: ρ 0.50 (Pearson 0.53), positiv in **18/18** Seeds
   (0.25–0.65), mit fremder Maske −0.09; ohne Diagonalpaare a = b 0.46. Richtige Formulierung also: Die beiden
   Positionen **interferieren frequenzweise so, wie es der Kreuzterm der Maske vorhersagt**; das ist der Grund, warum
   M0c die Gradientenleistung besser beschreibt. „Kohärent addiert“ im Sinn gleicher Phase war zu stark.
4. [medium] *„Fehlgriffe kommen nicht aus Maske/Init“ zu weit.* **Übernommen:** Geprüft sind nur die Rangprädiktoren
   M0, M0c, E0 und G0 bei Schritt 0. Maske oder Init können über die Trainingsdynamik (Phasen, Richtungen) trotzdem
   beitragen.
5. [medium] *„Oberwellen wachsen spät“ ist ein Kohortenvergleich.* **Übernommen:** zurückgestuft auf „Seeds 0–9 bei 25k
   zeigen häufiger K ≠ K_h als Seeds 10–17 direkt nach dem Grokking“. Ein Zeitverlauf an denselben Seeds steht aus
   (Studien-Checkpoints existieren, reine Auswertung).

**Zyklus 10 (06:37, post hoc, Inferenz an Studienmodellen, kein Training): Oberwelle oder eigenständig genutzte
Frequenz?** `EXP-016-engineered-split/posthoc_overtone_test.py`, Seeds 0–9 (25k, `model_final.pt`), alle 10 Paare
(k, fold(2k)) in der W_E-Top-5. (1) **Ablation** (Frequenz aus W_E[:p] herausprojiziert, Testverlust auf dem Studien-
Testsplit): In allen 8 Paaren, in denen 2k das schwächere Glied ist (Leistungsverhältnis 0.02–0.38), kostet das
Entfernen von 2k **weniger als das Entfernen jedes anderen Top-5-Glieds** (Δloss 0.0007–0.12, Acc ≥ 0.96; andere
Top-5-Glieder 0.005–22; k selbst 0.9–8.5). Unter Zufall (je Paar 1 von 4 Kandidaten) wäre 8/8 ≈ 1.5e-5; das Kriterium
wurde aber erst beim Lesen der Tabelle gewählt, also explorativ. Eine zufällige Nicht-K-Frequenz kostet ≈ 0, 2k also
etwas mehr als nichts. (2) **Phasenkopplung** über die Embedding-Dimensionen (axiale Resultante von ψ_j − 2φ_j, nur
Dimensionen mit beiden Amplituden über dem Median): Mittel 0.31 gegen 0.15 in der Kontrolle (k mit anderen Top-5-Gliedern),
deutlich nur in 3/10 Paaren (0.69, 0.56, 0.39), sonst auf Kontrollniveau.
**Befund (explorativ, gemischt):** Die schwächeren 2k-Glieder sind funktional nachrangig (am wenigsten wichtig in der
Top-5), aber nicht bedeutungslos; eine reine Oberwelle einer gemeinsamen Wellenform ist nur in einem Teil der Paare
nachweisbar. Die Formulierung „nur Oberwelle“ ist zu ersetzen durch: **„nachrangige, teils phasengekoppelte
2k-Komponente“**. Nebenbefund: Auch nicht-harmonische Top-5-Glieder können fast unwichtig sein (Seed 5, k = 14:
Δloss 0.002). Die W_E-Top-5 ist also als K-Definition verrauscht; die Studie hat dafür eigene Regeln (`nanda` u. a.).

**Zyklus 11 (06:39, post hoc, gleiche Seeds über die Zeit; Codex-Punkt 5):** `posthoc_overtone_timecourse.py`,
8 Paare (2k schwächer) aus Seeds 0–9, `embeddings.npy` (125 Zeitpunkte). Ergebnis: Das Leistungsverhältnis 2k/k **fällt**
über das Training (z. B. Seed 0: 0.84 bei Init → 0.16 bei 25k), k wächst also schneller. Aber in **5/8** Paaren kommt 2k erst
**nach** der Generalisierung in die Top-5 (Schritt 6421–17797 gegen gen 5605–8427), weil andere Frequenzen beim
Aufräumen schneller verschwinden; in 3/8 (Seeds 1, 3, 6) war 2k schon ab Init unter den stärksten 5–8.
**Befund:** Innerhalb derselben Seeds taucht 2k meist spät in der Top-5 auf (Rang), nicht durch relatives Wachstum.
Die Kohortenaussage aus Zyklus 9 ist damit für den Rang bestätigt, für die Leistung widerlegt.

**Zyklus 12 (06:40, Theorie):** M0c geschlossen hergeleitet: M0c(k) = 4 Σ_c |N̂_L|² cos²(arg N̂_L + πkc/p), M0 = 2 Σ_c |N̂_L|²
(EXP-019 README). Numerisch exakt bestätigt (≤ 5e-15); bei kommutationssymmetrischen Masken M0c = 2·M0. Der Unterschied
M0c − M0 misst also nur die Kommutations-Asymmetrie des Splits. Literatur: Symmetrie und Grokking-Tempo bekannt
(2411.05353), Bezug zur Frequenzwahl nicht gefunden → [[NOVEL_DIRECTIONS]] N8, niedrige Priorität, nicht vorbereitet.

**Zyklus 13 (06:41–06:43, neue Frage): EXP-022 „Ein-Frequenz-Lösung per Datenauswahl?“ vorbereitet.** Frage: Kann die
Datenauswahl nicht nur vorgeben, **welche**, sondern auch **wie viele** Frequenzen gelernt werden? Literatur: Mehrere
Frequenzen gelten als Robustheitsmechanismus (He et al. 2026, Mehrheitsabstimmung); ein Eingriff, der eine
Ein-Frequenz-Lösung erzwingt, wurde nicht gefunden (vorläufig). Beim Bau gefunden und vor jedem Lauf behoben: Mit ε = 2
und nur einem Ziel erzeugt das Clipping q ≥ 0.05 Harmonische 2k, 3k, 6k im Masken-Spektrum (Seed 42: 14 → 28, 42, 29).
S1 nutzt deshalb ε = 0.9 ohne Clipping (Top-1-Anteil 0.136–0.158 statt ≈ 0.02). Drei konkurrierende Vorhersagen im README.
Nicht ausgeführt.

**Codex-Review EXP-022** (`EXP-022-single-frequency/codex_review_2026-09-26.txt`), 5 Befunde, alle geprüft und übernommen
(README Nachtrag a, 06:51): funktionale Primärgröße (Regel `nanda` auf W_L, gespeicherte Modelle, keep/drop-Ablation von
f1) statt W_E-n_eff; neue Primärkontrolle D1 (S1-Gewichte innerhalb der Antidiagonalen permutiert, gleiche Abdeckung,
Top-1-Anteil 0.02 statt 0.14); feste 6000 Schritte für alle Arme; gemeinsames Erfolgskriterium; strenge Protokollprüfung.
Prüfung der Messwerkzeuge am Studienmodell Seed 0: `nanda` reproduziert die gespeicherte Schlüsselmenge exakt; nur die
Schlüsselfrequenzen in W_E behalten → Test-Acc 0.995, nur eine (15) behalten → 0.054. Ein normal trainiertes Netz braucht
also tatsächlich mehrere Frequenzen; das ist der Vergleichspunkt für S1.

**Zyklus 14 (06:52, Designprüfung an vorhandenen Daten):** EXP-016-Spektren: Überlappung der W_E-Top-5 mit der Zielmenge
bei Schritt 0/250/500/1000/2000 in allen 12 Läufen (Seeds 10–15): 0–2 / **5** / 4–5 / 3–5 / 3–5; im Smoke schon bei
Schritt 50 5/5. Die Daten prägen die Frequenzen also sofort auf; später ersetzen 2k-Harmonische einzelne Ziele (passt zu
Zyklus 7–8). Folge: EXP-020-Gitter vor jedem Lauf um t = 10 und 25 ergänzt (Nachtrag b). Die Überlappung bei 250 ist eine
vorab festgelegte Sekundärgröße von EXP-016; hier nur als Zwischenblick, keine Entscheidung.

**Technik (06:52):** Beim Prüfen gefunden: Meine Python-Bearbeitungen haben mehrere Dateien auf CRLF umgestellt, darunter
`queue_s5.sh` und `EXP-020-data-switch/queue.sh`, die unter `sh` gebrochen wären (`sh -n` meldet das nicht). Alle in
dieser Sitzung geänderten oder neuen Dateien, die zu Sitzungsbeginn LF hatten oder neu sind, wieder auf LF gestellt;
Tests danach 14/14 und 5/5. Hinweis in STATE. Zwei Probe-`summary.json` (Trockenläufe, „nicht auswertbar“) aus Git entfernt.

**Zyklus 15 (06:54, post hoc an EXP-016 Seeds 10–15): Welche Ziele werden nach Schritt 250 verdrängt?** Hypothese vorher: die
Ziele mit der niedrigsten Masken- bzw. Init-Leistung. `posthoc_dropped_targets.py`. 14 verdrängte Ziele in 12 Läufen.
Rang unter den 5 Zielen (1 = stärkstes): nach Leistung bei Schritt 250 **alle 14 auf Rang 4 oder 5** (Zufall 5.6), Mittel 4.64;
nach M0 Rang 4–5 in 10/14 (Mittel 3.86; binomial p ≈ 0.02); nach Init-Leistung E0 in 9/14 (Mittel 3.64; p ≈ 0.06).
**Befund (explorativ):** Verdrängt werden die früh schwächsten Ziele; deren Schwäche geht teils auf die Maske, teils auf
die Init zurück. Zusammen mit Zyklus 7/8: Die Daten legen die Frequenzmenge sofort fest; in der späteren Dynamik ersetzen
2k-Harmonische stärkerer Ziele die schwächsten Ziele. Läufe nicht streng unabhängig (F und G teilen die Init).

**Zyklus 16 (06:54, post hoc): Kombinierter Prädiktor log E0 + log M0c.** `posthoc/combined_predictor.py`. Seeds 0–9:
r̄ 0.252 gegen 0.280 (M0c allein), p 0.098; Seeds 10–17: 0.212 gegen 0.222, p 0.375; E0 allein 0.37. **Befund: schwach
richtungsgleich.** Als Sekundärgröße in EXP-019 aufgenommen (Nachtrag b), bevor die frischen Läufe existieren.

**Zyklus 17 (06:56, Vorbereitung): EXP-014 Nachtrag b.** Sekundärgröße mit M0c: sagt die Maske des **benutzten** Splits
die Frequenzen des Kreuzlaufs besser voraus als die Maske des eigenen Splits der Init? Bausteine an Baseline 10 geprüft
(eigener Split r̄ 0.175, fremder 0.669, E0 0.404). Primärgröße unverändert.

**Zyklus 18 (06:58, Architektur-Kontrast, Vorhersage vor der Rechnung): Gilt der Positions-Mechanismus auch in der MLP?**
Vorhersage (vorher notiert): In der MLP mit gemeinsamem Embedding laufen linker und rechter Operand durch **verschiedene**
Hälften von W_in (unabhängige Zufallsmatrizen) → der Kreuzterm folgt der Maske **nicht**, M0 beschreibt den Gradienten
mindestens so gut wie M0c. `posthoc/mlp_contrast.py`, Seeds 0–9, Studien-MLPs (arch25k). Ergebnis: Kreuzterm gegen
Masken-Kreuzterm ρ **0.05** (Transformer 0.50); Gradientenleistung ρ(M0) **0.37** > ρ(M0c) 0.24 (Transformer umgekehrt:
0.42 < 0.57); auch für die finalen W_E-Frequenzen r̄(M0) 0.323 < r̄(M0c) 0.351 (Transformer umgekehrt).
**Befund: Vorhersage bestätigt** (an vorhandenen, für diese Frage aber noch nicht betrachteten Daten; eine Konfiguration,
10 Seeds). Der Mechanismus „geteilter Wertepfad → Interferenz der Positionen“ erklärt, warum M0c im Transformer und M0 in
der MLP die bessere Statistik ist.

**Zyklus 19 (06:58, In-silico-Eingriff, Vorhersage vor der Rechnung): Ist der geteilte Wertepfad die Ursache?**
`posthoc/value_path_intervention.py`, Seeds 0–9, nur Init + ein Rückwärtsdurchlauf. Position 1 bekommt im ersten
Gradienten eine **eigene** Wertematrix W_V′ (bzw. eigene Ausgabematrix W_O′, gleiche Init-Verteilung). Ergebnis:
Kreuzterm gegen Masken-Kreuzterm ρ unverändert **0.468** (10/10 positiv; reproduziert die frühere Messung exakt),
mit eigenem W_V′ **−0.026** (4/10), mit eigenem W_O′ **0.074** (7/10). **Befund: Vorhersage bestätigt.** Die Interferenz der
beiden Positionen im ersten Gradienten entsteht durch den geteilten Wertepfad der Attention (W_V, W_O). Zusammen mit
dem MLP-Kontrast (Zyklus 18) ist das der bislang stärkste Beleg für den Mechanismus hinter M0c. Grenze: nur der erste
Gradient bei Init; ob das die finale Frequenzwahl kausal ändert, zeigt erst ein Training mit getrennten Wertepfaden
(nicht vorbereitet).

**Zyklus 20 (07:00–07:09, Vorbereitung): EXP-023 „getrennte Wertepfade“.** Frage: Bestimmt die Positions-Interferenz auch
die **finale** Frequenzwahl? Eingriff im Training: Position 1 bekommt eine eigene Wertematrix W_V1 (Variante im Labor,
Studiencode unverändert, `--split-value`). **Codex-Review** (`EXP-023-split-value/codex_review_2026-09-26.txt`), 5
Befunde, alle übernommen (Nachtrag a): Arme rand und copy, frische Seeds 50–59 mit eigenen Baselines, feste 3000 Schritte
für alle, Init-Prüfsumme, Lader mit Rundlauf-Test. Tests 15/15. Nebenbei: Das Skript `value_path_intervention.py` rechnete
beim Import; `__main__`-Schutz ergänzt (Ergebnis-JSON unverändert, deterministisch).

**Betriebsprüfung (07:19): Codex prüft `queue_s5.sh` als Ganzes** (`lab/codex_queue_s5_review_2026-09-26.txt`), 2 Befunde:
(1) [high] Mit dem **committeten** `guarded_run.py` (Jobgrenze 20 min) würden alle `--min-minutes 33`-Läufe abgelehnt.
Geprüft: Im Arbeitsverzeichnis liegt die uncommittete Nutzerfassung ohne Jobgrenze (Regel 14); damit liefen in Sitzung 4
dieselben Aufrufe. Kein Betriebsfehler hier, aber eine Abhängigkeit → in STATE vermerkt; der Commit bleibt beim Nutzer.
(2) [medium] `result.json` wurde nicht atomar geschrieben; ein Abbruch durch den Wächter mitten im Schreiben hätte jeden
Neustart blockiert. **Übernommen:** Schreiben über Temp-Datei + `os.replace`, unlesbare Metadaten gelten als
unfertiger Lauf (`previous_status`), Test mit abgeschnittener Datei; 16/16.

**Zyklus 21 (07:19, post hoc): Ist M0c konzentrierter als M0?** Anlass: Die Studie findet im Transformer ~4–5, in der MLP
~11 Schlüsselfrequenzen und lässt offen, warum (RESULTS §16.4/16.5). Wenn M0c die Statistik des Transformers und M0 die der
MLP ist (Zyklus 18), könnte eine stärkere Konzentration von M0c beitragen. `posthoc/concentration_m0_vs_m0c.py`,
Splits der Seeds 0–17: M0c ist in **18/18** konzentrierter (CV 0.132 gegen 0.093; Top-5-Anteil 0.112 gegen 0.105;
n_eff 55.0 gegen 55.5). **Einordnung: fast trivial und klein.** M0c = M0 + Kreuzterm mit Mittel ≈ 0 über k, der Streuung
hinzufügt; die Richtung ist damit nahezu durch Konstruktion gegeben, und beide Spektren sind fast flach. Kein Beleg für eine
Erklärung des Frequenzzahl-Unterschieds; eine Prüfung bräuchte Training (z. B. Frequenzzahl im EXP-023-Arm rand gegen
Baseline nach dem Grokking). Nicht vorbereitet.

**Konsistenzprüfung der Befundnotiz (07:28)** durch Codex (`lab/codex_befund_review_2026-09-26.txt`), 4 Befunde, alle geprüft
und übernommen: (1) Der EXP-016-Abschnitt war kausal formuliert, obwohl erst 6 von mindestens 8 Seeds vorliegen und Schritt
50 nur ein Smoke-Lauf ist → als unvollständige Vorschau gekennzeichnet, Rangbefunde ohne Ursachenzuschreibung.
(2) **Rechenfehler meinerseits:** „M0c − M0 misst die Kommutations-Asymmetrie“ ist falsch. Aus der geschlossenen Form folgt
M0c − M0 = 2 Σ_c |N̂|² cos(2θ), ein **Symmetrie**-Term (maximal = M0 bei symmetrischen Splits). Korrigiert in der
Befundnotiz, im EXP-019-README (Nachsatz) und in N8; die Aussage in Zyklus 12 oben ist entsprechend zu lesen. Zudem:
Aufhebung der Kreuzterme nur näherungsweise (0.01), Fremdmasken-Kontrolle nur n = 10. (3) MLP-Kontrast: „bestätigt“ nur für
den ersten Gradienten (9/10, p ≈ 0.003); für die finalen Frequenzen 6/10, p ≈ 0.21, nur beschreibend. (4) Negative Befunde
vorsichtiger formuliert („kein belastbarer Zusammenhang nachgewiesen“, mit Zahlen).

**07:30 Warteschlange gestartet.** Beim Prüfen einer unerwarteten `.gitignore`-Änderung (06:58, nicht von mir) gefunden:
Der Nutzer hat um 06:58 in `.claude/settings.local.json` genau die erbetene Freigabe eingetragen (`sh lab/experiments/*queue*`,
`python lab/tools/guarded_run.py *`). Damit ist die Ablehnung von 05:52 aufgehoben. `sh lab/experiments/queue_s5.sh` läuft im
Hintergrund (Log `lab/runner/logs/queue_s5.log`), Wächter: 79.7 min Sitzungsbudget. Erwartung: EXP-016 Seeds 16–19
(8 × ~4.5 min) bis ~08:06, danach Baseline 18, soweit Zeit bleibt; der Wächter beendet spätestens zur Deadline.
Auswertung EXP-016: Vorab waren 10 Seeds festgelegt (mindestens 8 gültige). Bei n = 8 nur **Zwischenstand**; die
Entscheidung gilt bei n = 10, um keine zweite Auswertung mit anderem Abbruchpunkt zu haben.
EXP-016 Seed 16 Arm F 07:34: gen 675, K {11, 26, 31, 51, 53} = F exakt (5/5), 0 aus G = {15, 25, 27, 35, 48}.
EXP-016 Seed 16 Arm G ~07:39: gen 825, K {15, 25, 27, 30, 54}, 3 aus G, 0 aus F. Δ_16 = +8. Die beiden Nicht-Ziele sind
30 = 2·15 und 54 = 2·27 (Harmonische von G-Zielen; EXP-021 wertet formal erst am Ende aus).
EXP-016 Seed 17 Arm F 07:43: gen 650, K {13, 26, 43, 49, 50}, 4 aus F = {1, 26, 43, 49, 50}; 13 = fold(2·50).
EXP-016 Seed 17 Arm G 07:47: gen 700, K {1, 8, 20, 42, 56}, 4 aus G; 1 ist ein F-Ziel, aber zugleich fold(2·56) (Harmonische
eines G-Ziels). Δ_17 = +7.
**EXP-016 Zwischenstand n = 8 (07:48, vorab festgelegte Auswertung, `analyze.py`):** Δ̄ = +7.625 (8/8 positiv), p = 1/256
= 0.0039; passende Überlappung 3.875/5, gekreuzte 0.06; Zufallssplit-Baseline gegen F/G 0.44. Sekundär (Nachtrag b):
Δ_h̄ 8.25; **alle** Nicht-Ziel-Frequenzen der Seeds 16–17 sind 2k-Harmonische (4/4); F > G in 1 von 2 Seeds (16), G > F in 0.
Die Entscheidung fällt wie angekündigt bei n = 10 (Seeds 18/19 laufen).
EXP-016 Seed 18 ~07:56: F K {18, 19, 27, 39, 54} (4/5, 54 = 2·27), G K {13, 20, 24, 48, 53} (4/5, 48 = 2·24), gekreuzt 0. Δ_18 = +8.
EXP-016 Seed 19 ~08:04: F K {5, 7, 9, 10, 53} (3/5; 7 = fold(2·53), 10 = 2·5), G K = G exakt (5/5). Δ_19 = +8.
**EXP-016 abgeschlossen (08:06), vorab festgelegte Entscheidung: *steuerbar*.** n = 10, Δ̄ = +7.7, 10/10 positiv, p = 1/1024.
Passend 3.9/5, gekreuzt 0.05, Baseline 0.44. Sekundär: alle 20 Nicht-Ziel-Frequenzen sind 2k-Harmonische (Seeds 16–19:
8/8, Vorhersage „> 50 %“ erfüllt); F-G-Asymmetrie nicht wiederholt (1:1) → Zufall. Details im EXP-016-README.
Baseline 18 läuft seit 08:05 (höchstens 15000 Schritte ≈ 33 min, endet vor der Deadline).

### Sitzung 5, Abschlussbericht (Entwurf 08:08 Berlin; Baseline 18 läuft noch)

**Wichtigste Befunde:**
1. **EXP-016 abgeschlossen, vorab festgelegt: *steuerbar*.** Konstruierte Trainingssplits geben einem Transformer die
   gelernten Fourier-Frequenzen vor: 10/10 Seeds, Δ̄ = +7.7 von 10, p ≈ 0.001; passende Überlappung 3.9/5, gekreuzte 0.05.
   Alle 20 Abweichungen sind 2k-Harmonische der Zielfrequenzen (an Seeds 16–19 vorab vorhergesagt).
2. **Mechanismus (post hoc/in silico, explorativ):** Im ersten W_E-Gradienten interferieren die beiden Eingabepositionen
   frequenzweise nach dem Kreuzterm der Maske (18/18 Seeds); Ursache ist der geteilte Wertepfad der Attention (eigene
   Wertematrix für Position 1 → Interferenz weg); in der MLP fehlt sie (Vorhersage vorher notiert, für den ersten Gradienten
   bestätigt). Geschlossene Form von M0c; M0c − M0 ist ein Kommutations-Symmetrie-Term.
3. **2k-Komponenten:** in Studienmodellen nachrangig (Ablation), aber nicht null; Phasenkopplung nur teilweise.
4. **Negativ:** natürliche Masken-Konzentration sagt die Grokking-Zeit nicht belastbar voraus; Oberwellen-Bereinigung und
   kombinierte Prädiktoren bringen keinen belastbaren Gewinn.
5. **Vorbereitet (Codex-geprüft, nicht ausgeführt):** EXP-018 (beschleunigt Konzentration das Grokking?), EXP-019 (M0c vs.
   M0), EXP-020 (kausale Festlegungszeit per Datenwechsel), EXP-021 (Harmonische, Bestätigung), EXP-022 (Ein-Frequenz-
   Lösung), EXP-023 (getrennte Wertepfade im Training); EXP-014 um eine M0c-Sekundärgröße ergänzt.
6. **Technik:** `result.json` jetzt atomar; Skip endet mit Exit 0; Warteschlangen stoppen bei jedem Fehler; CRLF-Falle
   behoben; Tests 16/16 und 5/5.

**Offene Grenzen:** Nur p = 113, 30 %-Split, Transformer (Mechanismus zusätzlich MLP), eine Plattform. Mechanismus-Befunde
nur für den ersten Gradienten; die finale Wahl testet EXP-023. Beschleunigung des Grokkings unter konstruierten Splits ist
ungeprüft (Komplement-Testmenge), dafür EXP-018. EXP-014 (Split × Init) und EXP-010 stehen aus.

**Reproduktion:** `python lab/tools/guarded_run.py -- python lab/experiments/EXP-016-engineered-split/analyze.py`;
Post-hoc-Skripte unter `lab/experiments/EXP-015-mask-spectrum/posthoc/` und `lab/experiments/EXP-016-engineered-split/posthoc_*.py`
(je über den Wächter, nur Init/Inferenz).

**Nächste Aktion (im Fenster):** `python lab/tools/guarded_run.py --check`, dann `sh lab/experiments/queue_s5.sh` im
Hintergrund (setzt bei Baseline 19 bzw. 18 fort). **Codex:** 7 Reviews in dieser Sitzung (EXP-018, 020, 022, 023,
Schlussfolgerungen, Warteschlange, Befundnotiz), alle Befunde selbst geprüft; einer davon deckte einen eigenen Rechenfehler auf.
**Scheduler:** Aufgabe `GROKVERSE-Lab-Runner` aktiv; nächster Start laut `runner-state.json` 08:49Z = **10:49 Berlin**
(im Run-Fenster).
Baseline Seed 18 (EXP-003d) 08:24: gen 8775, K {7, 17, 31, 53, 54} (9 von 10 Baselines). Danach lehnte der Wächter Baseline 19
ab (25.7 min Restbudget < 33), Warteschlange mit rc 3 sauber beendet, keine Python-Prozesse mehr.
**Abschlussbericht gilt damit als final (08:25).** Nächste Sitzung: `sh lab/experiments/queue_s5.sh` setzt bei Baseline 19 fort
(EXP-016 und Baseline 18 werden übersprungen).

## Sitzung 6 (2026-09-26, Start 08:29 Berlin / 06:29Z, Deadline 11:29 Berlin)

**08:30 Wiederaufnahme.** Kein STOP, keine Python-Prozesse, Wächter ok (heute Fenster bis 18:00). `queue_s5.sh` neu
gestartet; EXP-016 und Baseline 18 übersprungen, Baseline 19 lief. Nebenbei `--suffix` in `EXP-015/mask_spectrum.py` und
`EXP-012/predict.py` ergänzt, damit die Phase-2-Neuberechnung mit n = 10 die Entscheidungsdatei (n = 8) nicht überschreibt.

**Zyklus 1 (08:32–08:50, Theorie + neue Richtung N11): Was sagt AGF für ein quadratisches Netz mit maskiertem Verlust?**
Rechnung: Nutzen U = ‖P g‖, g_c = Σ_a M(a, c−a)(u_a + v_{c−a})². Das Quadrat erzeugt 2k-Oszillationen entlang der
Antidiagonalen, also sollte ein auf F konstruierter Split beim quadratischen Netz die **halben Ziele** H(F) = fold(57·F)
begünstigen, beim Transformer (EXP-016) dagegen F selbst. Numerisch (`EXP-024/utility_scan.py`, exakter Nutzen,
16 × 16 Phasen, 20 Splits): Top-5 des Nutzens enthalten **3.25/5 H**, **0.2/5 F** (Zufall 0.45); Spearman(U, M0(2k))
+0.30, (U, M0(k)) −0.01. Nachprüfung 32 × 32 Phasen ohne Duplikat: 3.26 / 0.21. Literatur (3 Suchen, N11): nicht gefunden
(vorläufig). → [[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] vorab festgelegt: trainierte Zwei-Hot-Netze
(quadratisch = primär, ReLU = explorativ) auf den EXP-016-Splits; H24: ov(Top-5, H) > ov(Top-5, F), Vorzeichentest.

**Nebenbefund: RNG-Kollision in EXP-016.** Split Seed 12/G ist identisch mit Seed 19/F (Strom `seed + SALT + 7`).
Ohne Duplikat n = 9, 9/9 positiv, p ≈ 0.002 → Entscheidung *steuerbar* bleibt. Gleicher Split, andere Init: K 4/5 gleich.
Nachtrag c im EXP-016-README. EXP-018/020/022 benutzen einen Salt ohne Armversatz (dort nicht betroffen, geprüft per grep).

**Codex-Review EXP-024 (08:40–08:50, 11 Punkte).** Übernommen: (1) Herleitung unvollständig: es gibt einen Term
cos(ωkc + α + β) mit Gewicht n_c und Beiträge erster Ordnung in der Maske; „M0 bei 2k“ ist nur eine Näherung,
maßgeblich ist die exakte Nutzenrechnung. (2) Biases entfernt (Bias koppelt an k). (3) Messgröße jetzt
reskalierungsinvariant und mit W_out gewichtet. (4) Gültigkeitsprüfung (`complete`, vorgesehene Einheiten).
(5) Kontrolle mit fold(m·F) für alle anderen m. (9) Phasenraster geprüft (s. o.). Nicht übernommen, als Grenzen
notiert: F/G-Abhängigkeit im Vorzeichentest; ein H-Befund belegt nicht den AGF-Anfangsmechanismus als Ursache.
Codex bestätigte Indizierung, 57 = 2⁻¹ mod 113, Faltung und Komplement-Testmenge.

**08:49 Baseline 19 fertig** (gen ≈ 7225, K {16, 41, 44, 47, 51}); EXP-003d-Baselines damit 10/10.
**08:51 EXP-024-Smoke** (eigener Split Seed 9, nicht ausgewertet): 80 s, endlich, Test 1.0 ab Schritt 1300.
**08:52 EXP-024-Hauptserie gestartet** (`sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh`, Log
`lab/runner/logs/queue_exp024.log`), 38 Läufe × ~80 s ≈ 50 min. `queue_s5.sh` ist angehalten (Shell um ~08:33 beendet,
damit kein zweiter Job startet) und wird danach neu gestartet (setzt bei den Smokes EXP-018/020 fort).
**08:55 EXP-015/012 Phase 2 mit n = 10 (nur berichtet):** EXP-015 r̄(M0) 0.279, p < 1e-5, fremde Masken 0.492
(p = 5e-5); EXP-012 G0 0.239 gegen E0 0.381, p = 0.0078. Beide unverändert *bestätigt* (Nachträge in den READMEs).

**Zyklus 2 (08:56, Vorhersage für Arm R vor dessen Läufen): Was sagt der Nutzen mit ReLU?** `utility_relu.py`:
Top-5 des ReLU-Nutzens enthalten **4.68/5 Ziele F**, 0.37/5 halbe Ziele H. Die Nutzenrechnung sagt also eine
**Umkehr zwischen den Aktivierungen** voraus (x² → H, ReLU → F); Grund ist der lineare Anteil x/2 der ReLU.
Als sekundäre, gerichtete Entscheidung für Arm R eingetragen (EXP-024 Nachtrag b, committet 08:53, vor dem ersten
R-Lauf; Q-Läufe liefen bereits, ihre Ergebnisse habe ich vorher nicht angesehen). Der Transformer (EXP-016: F) verhält
sich wie die ReLU-Vorhersage. Die 2k-Oberwellen des Transformers erklärt diese Rechnung **nicht** (x² würde H = F/2
begünstigen, nicht 2F); sie bleiben ein eigener Befund (EXP-021).

**Zwischenbilanz nach drei Zyklen (08:58, §4).** *Gelernt:* Die AGF-Nutzenrechnung unter maskiertem Verlust liefert
eine scharfe, architekturabhängige Vorhersage (x² → F/2, ReLU → F), die ohne Training aus dem Split folgt; das ist die
erste Theorie im Labor, die die EXP-015/016-Befunde nicht nur beschreibt, sondern etwas Neues vorhersagt.
*Wiederholen wir uns?* Nein: neue Architektur (Zwei-Hot ohne Bias), neue Messgröße (reskalierungsinvariant), neue Frage.
*Messungen geeignet?* Die Top-5-Überlappung ist grob; deshalb zusätzlich Kontrolle über alle anderen Multiplikatoren
m·F und Zeitverlauf (`timecourse.py`, explorativ). *Nächste Annahme, die angegriffen werden sollte:* dass der
Transformer sich „wie ReLU“ verhält, weil er F lernt. Ebenso gut könnte er durch seine Attention eine andere effektive
Nutzenfunktion haben. Prüfbar wäre das über den exakten ersten Wachstumsmodus eines Transformers bei kleiner Init.
Noch nicht vorbereitet.

## Sitzung 7 (2026-09-26, Start 08:59 Berlin / 06:59Z, Deadline 11:59 Berlin)

**09:02 Wiederaufnahme.** Kein STOP. Sitzung 6 endete bereits 08:57 (27 min, `completed`), ohne Abschlussbericht; die
EXP-024-Warteschlange (gestartet 08:52) lief weiter und ist ein einzelner Job (7/38 fertig, Q-Arm). Ihr Wächter rechnet
noch mit der alten Deadline 11:29 Berlin; reicht für die restlichen ~31 Läufe (~45 min). Ich übernehme die Beobachtung.

**Zyklus 1 (09:01–09:08): Welcher Anteil der Aktivierung trägt die F- bzw. H-Wahl des Nutzens?**
*Literatur zuerst:* Die in Sitzung 6 nur aus einer Suchzusammenfassung übernommene Aussage ist jetzt am Volltext geprüft:
He et al. 2026 (https://arxiv.org/html/2602.16849): ReLU-Lösungen stützen sich auf die geraden Anteile (½|x|), Tausch
ReLU → |x|/x² zur Inferenzzeit ohne Verlust; volle Daten, x²-Theorie, keine Split-Frage. Damit sagen für EXP-024 Arm R
zwei Bilder Gegensätzliches: Nutzen am Start → F, Endlösung gerade → H.
*Rechnung* (`utility_parity.py`, 19 Einheiten, 8 × 8 Phasen, 49 s über den Wächter): ungerader Anteil x → ov_F 5.00 /
ov_H 0.21; gerader |x| → 0.21 / 2.21; ReLU 4.58 / 0.37 (16 × 16 Phasen in Sitzung 6: 4.68 / 0.37, also konsistent);
σ_α = αx + x²: α = 0 → 0.26 / 3.05, α = 0.5 → 0.95 / 2.95, α = 1 → 2.53 / 1.63, α = 2 → 4.79 / 0.32. Umschlag bei
α/r ≈ 1. *Entscheidung:* daraus ein neues Messinstrument gemacht: [[experiments/EXP-026-parity-crossover/README|EXP-026]]
(vorab festgelegt und committet 01da0bd, vor jedem Lauf und vor Ansicht der EXP-024-Ergebnisse): der Umschlagpunkt α*
trainierter σ_α-Netze zeigt, bei welcher Merkmalsamplitude die Wahl fällt (Start r ≈ 0.0094 gegen Ende). Suche (N12):
nicht gefunden, vorläufig. Codex-Review des Designs läuft.

**Codex-Review EXP-026 (09:05–09:13, `adversarial-review --wait`, Ausgabe `EXP-026-parity-crossover/codex_review_2026-09-26.txt`):**
„needs-attention“, 4 × high, 2 × medium. Selbst geprüft, **alle übernommen**, weil sie zutreffen: (1) getrennt trainierte
α-Stufen messen eine Grenze zwischen Dynamiken, keine Zeit (α ändert Logit-Skala, Ableitung, AdamW-Weg); (2) h = 2-Gewichtung
falsch für gemischte Netze; (3) Spearman allein hätte ohne Vorzeichenwechsel „bestätigt“; (4) Median-r über alle Neuronen
hängt an irrelevanten Neuronen; (5) Punktschätzer genauer als das Raster, erfundene Untergrenze bei α = 0; (6) Raster nicht
vollständig verlangt. **Umbau vor jedem Lauf** (Nachtrag a, commit 53450e1): Umschaltversuch auf einer Trajektorie,
σ_3 = 3x + x² bis t_s, danach x², t_s ∈ {0, 50, 250, 1000, 2500, nie}, Seeds 10–14 F, 30 Läufe; Anker mit echtem
Vorzeichenwechsel Pflicht; Ergebnis ist ein Intervall (t_lo, t_hi], A (früh) t_hi ≤ 250 gegen B (spät) t_hi ≥ 2500.
Auswerter an fünf synthetischen Fällen geprüft (früh, spät, alles H, alles F, fehlende Zelle: alle wie vorgesehen).
**Regelverstoß (eigener Fehler):** Diesen synthetischen Auswertertest habe ich direkt und nicht über `guarded_run.py`
gestartet (Fenster war offen, ~5 s, nur numpy). Künftig auch solche Tests über den Wächter.
**Git-Fehler, behoben:** Ein `git commit -a` (09:16) hatte die bewusst uncommitteten Runner- und Wächter-Änderungen des
Nutzers mitgenommen; sofort mit `git reset --soft HEAD~1` zurückgenommen, nur das README neu committet. Arbeitsbaum
unverändert, die Nutzerdateien sind wieder uncommittet (`git status` geprüft).

**Zyklus 2 (09:16–09:20): EXP-024 Arm Q ausgewertet (vorab festgelegt).** 19/19 gültig, alle generalisieren (Test 1.0).
ov_H 1.11, ov_F 0.21 (Zufall 0.45), d̄ +0.89, Vorzeichentest p = 0.0017, Kontrolle m·F 0.44. **Urteil: richtungsgleich,
n. s.** (Mindestgröße ov_H ≥ 2 verfehlt). Richtung wie von der Nutzenrechnung vorhergesagt, Größe weit darunter (3.25
im Nutzen). Post hoc: ov_H wächst langsam (0.53 → 1.11), keine scharfe Frühwahl; das gewichtete Spektrum ist **fast flach**
(Anteil H 0.102, F 0.084, Zufall 0.089): Das x²-Netz nutzt praktisch alle Frequenzen, der Split neigt die Leistung nur.
*Entscheidung:* Top-5 ist für diese Modelle eine schlechte Messgröße → EXP-026 Nachtrag b (primär jetzt ds =
Anteil F − Anteil H, commit 9cc206f) und EXP-025 Nachtrag a (kontinuierliche Sekundärgröße, commit b7e8127), beide
vor jedem ihrer Läufe. Auswerter-Test EXP-026 diesmal über den Wächter (5/5).
*Kritik an mir selbst:* Die Schwelle ov_H ≥ 2 stammt aus dem Nutzen am Start; dass trainierte breite x²-Netze ein flaches
Spektrum haben, hätte ich vorher aus der Max-Margin-Literatur wissen können. Neue Versuche mit diesem Modell brauchen von
Anfang an Anteilsmaße.

**Zyklus 3 (09:22): Folgefrage aus dem flachen Spektrum: Muss ein schmales Netz auswählen?** Morwani et al. 2023 (Thm 7,
am Volltext geprüft): Max-Margin-Lösungen nutzen jede Frequenz, ab Breite 4(p−1) = 448. EXP-024 lief mit 512, also
musste das Netz nicht auswählen. → [[experiments/EXP-027-width-selection/README|EXP-027]] vorab festgelegt: Breiten 32/64/128
(512 aus EXP-026 t_s = 0, rechnerisch identisch), Seeds 10–14 F, primär Spearman(−w, Anteil H − Anteil F), Permutation
innerhalb der Splits. `train_sigma.py` hat dafür `--width` bekommen (Standard 512, EXP-026 unverändert). EXP-027 ist ans
Ende der EXP-026-Warteschlange gehängt (die laufende `queue_s7.sh` wurde nicht verändert). Ohne Codex-Review (kleine
Erweiterung, gleicher Auswertetyp wie EXP-026); das ist eine Grenze.

**Codex-Review EXP-027 (09:30):** „needs-attention“. Wiederverwendung der 512er-Läufe als identisch bestätigt. Übernommen:
Güte-Schwelle (Train ≥ 0.99, Test ≥ 0.90), kalibrierte Statistik u = q_H − q_F (Perzentile gegen zufällige 5er-Mengen
desselben Spektrums, weil schmale Netze konzentriertere Spektren haben), breitenunabhängige W_out-Init, zusätzliche
Breite 256, Herkunftsprüfung. Nicht übernommen (Budget, als Grenze notiert): Init-Wiederholungen, Training bis zur
Konvergenz. Auswerter synthetisch geprüft (4/4, über den Wächter). EXP-027 Nachtrag a committet vor jedem Lauf.

**Zwischenbilanz nach drei Zyklen (Sitzung 7, 09:34, §4).** *Gelernt:* Die AGF-Nutzenrechnung trifft beim x²-Netz die
Richtung (H angereichert, F unterdrückt, p = 0.002), überschätzt aber die Größe stark, weil breite x²-Netze fast alle
Frequenzen nutzen. Die Paritätszerlegung (ungerade → k, gerade → 2k) erklärt, warum x² und ReLU verschieden reagieren
sollten. *Wiederholen wir uns?* Nein, aber zwei Messprobleme haben sich gezeigt: Top-5 ist für dichte Spektren ungeeignet,
und die ReLU-Zwei-Hot-Netze generalisieren in 5000 Schritten nicht. *Messungen geeignet?* Jetzt kalibrierte Anteils- und
Perzentilmaße (EXP-026 b, EXP-027 a). *Nächste Annahme, die angegriffen werden sollte:* dass eine „Wahl“ bei dichten
Lösungen überhaupt stattfindet. EXP-027 (Breite) greift genau das an; EXP-026 fragt, wann eine Neigung festgelegt wird.
Codex hat in dieser Sitzung zweimal ein Design vor dem ersten Lauf gekippt bzw. gehärtet; beides war berechtigt.

**Zyklus 4 (09:43): EXP-024 Arm R ausgewertet.** 19/19 vollständig, aber **nicht generalisierend** (Test 0.063). ov_F 4.79,
ov_H 0.21, Test F > H p = 1.9e-6 → H24-R *bestätigt*. Schon ab Schritt 50 alle 5 Ziele in der Top-5 (Anteil 0.151,
Zufall 0.089). Der Nutzen am Start (4.68) trifft auch die Größe. Einordnung: memorierende Netze; die He-et-al.-Aussage zur
geraden Endlösung ist damit nicht geprüft, und eine einfachere Erklärung (das Netz passt die Maske an) ist nicht
ausgeschlossen. Gesamtbild EXP-024 im README; Status abgeschlossen. *Nächster Schritt:* EXP-026 läuft (Smoke gestartet 09:42).

**09:44 EXP-026 Smoke** (α = 3 durchgehend, Split Seed 9, nicht ausgewertet): 88 s, endlich, Train 1.0, **Test 0.148**,
Top-5 enthält 3 der 5 Ziele. Das Smoke-Kriterium (Laufbarkeit, Endlichkeit, Zeit) ist erfüllt, die Hauptserie startete
09:44. Beobachtung: Mit starkem linearem Anteil generalisiert das Netz in 5000 Schritten nicht; der Anker „nie“ ist also
ein memorierendes Netz (wie EXP-024 R). Die Arme t_s ≤ 2500 enden als reine x²-Netze; ob sie generalisieren, wird
berichtet (gen95, Test-Genauigkeit). Keine Änderung am Design.

**Zyklus 5 (09:44–09:47): Ist die Frequenzwahl des Transformers ein Abdruck der Memorisierungsphase?** Anlass: memorierende
ReLU-Netze zeigen F ab Schritt 50. Post hoc an den 20 EXP-016-Läufen (`posthoc_memo_imprint.py`, ohne Training): Schritt 250
liegt in allen Läufen zwischen Memorisierung (120–130) und Generalisierung (450–1100); dort sind die W_E-Top-5 in **20/20**
Läufen genau die Ziele F (Anteil 0.27–0.40, Zufall 0.089). Am Ende nur noch 3.9/5; der Abfall liegt grob um die
Generalisierung, teils ein Gitterpunkt davor. *Einordnung:* explorativ, an denselben Daten gefunden. → [[experiments/EXP-028-memo-imprint/README|EXP-028]]
vorab festgelegt (Bestätigung an den noch nicht gelaufenen EXP-020-Läufen „nur F“/„nur G“, Seeds 30–34, keine eigenen
Läufe). N13 angelegt, Suche: nicht gefunden (vorläufig). Der Auswerter ist nur auf Feldnamen geprüft (an EXP-016-Daten),
nicht an synthetischen Fällen.

**Zyklus 6 (09:47–09:50): Gilt der Abdruck auch bei Zufallssplits?** Explorativ (Studienläufe Seeds 0–9, 150 Einbettungen,
`EXP-015/posthoc_m0_timecourse.py`): ρ(W_E-Spektrum, M0) Init −0.02, vor der Memorisierung 0.19, Memorisierung 0.48 / 0.44,
nach dem Grokking 0.19, Ende 0.14; 10/10 Seeds höher in der Memorisierung als danach. Kalibrierung für Stopp bei gen + 25:
9/10 unter dem Fenstermittel. → [[experiments/EXP-029-memo-imprint-random/README|EXP-029]] vorab festgelegt (commit 4b7b8e3), dann an
den Baselines 10–19 ausgewertet: **P29a bestätigt** (10/10, ρ_memo 0.42 gegen Init −0.04, p = 0.001), **P29b verfehlt**
(8/10, 0.42 gegen 0.38) → *teilweise*. *Deutung (vorläufig):* Die bekannte schwache M0-Vorhersage von K (EXP-015, r̄ 0.28)
ist vermutlich der Rest eines viel stärkeren Abdrucks aus der Memorisierungsphase. *Grenze:* Das Verblassen nach dem Grokking
ist nur explorativ belegt (Seeds 0–9); die Bestätigung bräuchte Läufe, die länger über das Grokking hinaus laufen.
**09:51 Kontrolle fremde Masken (post hoc, selbst, bevor Codex antwortete):** ρ mit fremdem M0 im selben Fenster 0.02
(Baselines) bzw. −0.02 (Studie), eigene 0.42 / 0.47, 10/10 in beiden Sätzen. Der Abdruck ist maskenspezifisch.

**Codex-Angriff auf N13 (bis 09:55, `EXP-029/codex_conclusion_review_2026-09-26.txt`):** „needs-attention“, 2 Punkte,
beide übernommen: (1) Abbau durch die Generalisierung nicht belegt (Maxima vor der Generalisierung, ungleiche Aggregation
Fenster gegen Endpunkt); (2) „Rest“ braucht Mediation. N13 korrigiert (Behauptungen als Hypothesen markiert).
**Zyklus 7 (09:55–09:58): Mediation.** [[experiments/EXP-030-imprint-residue/README|EXP-030]] vorab festgelegt (9470d85), dann ausgewertet:
ρ(M0, K) 0.235 (fremd 0.008), partiell gegeben W_E bei 250: **0.036**, Δ 10/10, p = 0.001 → *Rest gestützt*. W_E bei 250 sagt K
auch nach Herausrechnen von M0 stark voraus (0.42). *Deutung:* Die Maske wirkt über den frühen Abdruck auf die Endwahl; der
Abdruck selbst enthält daneben viel Init-Information.

**Zyklus 8 (09:59, explorativ, negativ): Sagt die Stärke des Abdrucks die Grokking-Zeit voraus?** Seeds 0–9: Spearman(ρ_memo,
Generalisierungsschritt) = 0.20 (n = 10), kein Hinweis. Nicht weiter verfolgt, keine Bestätigung angesetzt (passt zum
Befund aus Sitzung 5, dass die M0-Konzentration die Grokking-Zeit nicht vorhersagt).

**Zyklus 9 (09:59–10:02): Eingriff zur Mediation.** [[experiments/EXP-031-we-transplant/README|EXP-031]] vorab festgelegt und Code
geschrieben (`transplant.py`, eigenständig, baut das Modell wie `freq_ban.py`, lädt Studien-Checkpoints bei 500, frisches
AdamW in beiden Armen). 5 Paare (B = 0, 2, 4, 6, 8; A = B + 1) × {transplant, control}, bis Schritt 3000, ~55 min.
Ungetestet; Smoke (20 Schritte) steht am Anfang der Warteschlange. Codex-Review läuft.
**Codex-Review EXP-031 (bis 10:09):** „needs-attention“, 5 Punkte, alle übernommen (`=`-Zeile mitverpflanzt; Spender trägt Init-Lotterie
und Split zugleich; Endpunkt 3000 instabil, weil die Studienläufe erst ab 5600 generalisieren; Threads/Konfiguration nicht
geprüft; falsches Budget unbemerkt). **Entscheidung: nicht ausführen, zurückgestellt.** Das richtige Design (gekreuzte
Spender, Messung nach der Generalisierung) kostet mehrere Stunden Rechenzeit; es gehört in eine spätere Sitzung.
Lehre: Endpunkte vor der Festlegung an den vorhandenen Zeitverläufen auf Stabilität prüfen.

**Zyklus 10 (10:29–10:32): EXP-026 ausgewertet.** 30/30 vollständig; alle x²-Endnetze generalisieren, der Arm „nie“ memoriert.
Mittleres ds: t_s = 0 −0.002, **50 +0.165**, 250 +0.113, 1000 +0.091, 2500 +0.087, nie +0.105; alle 25 Läufe mit t_s ≥ 50
positiv. **Vorab-Urteil: *Anker ok, Trend n. s.*** (ρ 0.13, p 0.25). Beschreibend eine Stufe in den ersten 50 Schritten mit
Plateau; mein Rangtest über alle Stufen passte nicht zur Stufenform (Designfehler, nicht nachträglich korrigiert). Anker
d(0) < 0 nur knapp. Nebenbefund: 50 Schritte σ_3 verdoppeln die Generalisierungszeit (1390 → 2730).
→ [[experiments/EXP-032-early-lockin/README|EXP-032]] vorab festgelegt (t_s = 1, 5, 10, 20; Monotonie + Halbwertszeit), in die Kette
gehängt. Schnappschüsse bei 5/10/20 in `train_sigma.py` ergänzt (atomar geschrieben, berührt das Training nicht).
**EXP-027 Zwischenstand:** Die 32er-Netze verfehlen die Güte-Schwelle (Test 0.83–0.86) → EXP-027 wird *nicht auswertbar*.
Vor Ansicht der Ergebnisgröße EXP-027b festgelegt (frische Splits 15–19, Breiten 64–512), in die Kette gehängt.
Neue Reihenfolge: EXP-027 → EXP-032 → EXP-027b → EXP-025 → queue_s5.

**10:39 EXP-027 ausgewertet:** *nicht auswertbar* (Güte-Schwelle, Breite 32 Test 0.85). Beschreibend kein Trend (u −0.14…+0.14,
q_H ≈ 0.5 in allen Breiten), n_eff fällt von 52 auf 30. Selbst 32 Neuronen nutzen noch ≈ 30 Frequenzen; die Idee „schmale
Netze müssen auswählen“ trägt in dieser Form nicht. EXP-027b läuft trotzdem wie festgelegt (unabhängige Splits).
**10:40 Priorität:** In `queue_s5.sh` läuft EXP-020 jetzt vor EXP-018/014, weil seine Läufe ohne Wechsel zugleich die
Bestätigungsdaten für EXP-028 liefern. Keine inhaltliche Änderung an EXP-020.

**Zyklus 11 (11:09–11:09): EXP-032 ausgewertet (vorab festgelegt).** 30/30 gültig, alle Endnetze generalisieren. ds bei 5000:
0 −0.002, 1 +0.024, **5 +0.094**, 10 +0.131, 20 +0.147, 50 +0.165; ρ 0.91, p = 1e-4, t½ = 5 → ***Festlegung in ≤ 20 Schritten***.
Nach 5 Schritten ist r erst 0.0118 (Init 0.0094), die Neigung am Umschaltschritt 0.034 und wird bis 5000 auf 0.094
verstärkt. Generalisierung verzögert sich monoton (1390 → 2730). *Einordnung:* Das ist der bisher schärfste Befund dieser
Sitzung: Die Frequenzneigung eines x²-Netzes wird in den ersten ~5–10 von 5000 Schritten durch einen kurzzeitig
vorhandenen ungeraden Aktivierungsanteil festgelegt. Offen: Rolle von AdamW (Idee EXP-033 im BACKLOG).

**Zyklus 12 (11:24): EXP-027b ausgewertet (vorab festgelegt).** 20/20 gültig. ρ(−w, u) = −0.16, p = 0.74 → ***widerspricht***.
H-Neigung in allen Breiten (u +0.10…+0.36), aber nicht breitenabhängig. Idee „Kapazitätsgrenze erzwingt Auswahl“ verworfen.

### Abschlussbericht Sitzung 7 (2026-09-26, 08:59–~11:55 Berlin)

**Wichtigste Befunde (alle vorab festgelegt, sofern nicht als post hoc markiert):**
1. **[[experiments/EXP-032-early-lockin/README|EXP-032]] *Festlegung in ≤ 20 Schritten*:** Trainiert ein Zwei-Hot-Netz t Schritte mit
   3x + x² und danach nur mit x², so ist seine Frequenzneigung zu den Split-Zielen F nach **5 Schritten** zur Hälfte festgelegt
   (ρ 0.91, p = 1e-4); die frühe Neigung wird bis zum Ende etwa verdreifacht. Jeder frühe Schritt verzögert die Generalisierung.
2. **[[experiments/EXP-030-imprint-residue/README|EXP-030]] *Rest gestützt*:** Die bekannte M0 → K-Assoziation des Transformers
   (EXP-015) läuft fast vollständig über den W_E-Zustand bei Schritt 250 (ρ 0.24 → partiell 0.04, 10/10, p = 0.001).
3. **[[experiments/EXP-029-memo-imprint-random/README|EXP-029]] *teilweise*:** Während der Memorisierung ist W_E spezifisch mit der
   eigenen Trainingsmaske ausgerichtet (ρ 0.42 gegen Init −0.04 und fremde Masken 0.02; 10/10). Dass die Generalisierung
   diese Ausrichtung abbaut, ist nicht bestätigt (8/10).
4. **[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]]:** Gleiche Splits, andere Aktivierung → vorhergesagte Richtung in
   beiden Armen (x² → halbe Ziele, *richtungsgleich, n. s.*: Spektrum fast flach; ReLU → Ziele, *bestätigt*, aber memorierend).
5. Negativ bzw. offen: [[experiments/EXP-026-parity-crossover/README|EXP-026]] *Anker ok, Trend n. s.* (Test passte nicht zur
   Stufenform → EXP-032); [[experiments/EXP-027-width-selection/README|EXP-027]] *nicht auswertbar*, EXP-027b *widerspricht*
   (Breite erzwingt keine Auswahl). Post hoc: bei Schritt 250 sind die W_E-Top-5 in 20/20 EXP-016-Läufen genau die Ziele
   (Bestätigung EXP-028 vorbereitet).

**Offene Grenzen:** Zwei-Hot-Befunde an einer Architektur, AdamW, 5 Splits; ReLU-/σ₃-Netze memorieren in 5000 Schritten nur.
Der Abdruck-Befund ist korrelativ (Mediation); der Eingriff EXP-031 ist nach Codex zurückgestellt (Spender trägt Init und
Split zugleich). EXP-025 bei Sitzungsende unvollständig.
**Codex:** vier Reviews (EXP-026, EXP-027, N13-Schluss, EXP-031); jedes Mal Einwände übernommen, zweimal
wurde ein Design vor dem ersten Lauf umgebaut, einmal (EXP-031) ein Versuch gestoppt.
**Eigene Fehler:** ein synthetischer Test ohne Wächter gestartet; ein `git commit -a` mit Nutzerdateien (sofort rückgängig);
mehrfach geschätzte statt gemessene Uhrzeiten eingetragen (korrigiert).
**Reproduktion:** je Versuch unter „Befehle“ im README; alle Läufe über `python lab/tools/guarded_run.py -- …`,
Warteschlangen `sh lab/experiments/queue_s7.sh` bzw. die Einzel-`queue.sh`.
**Nächste Aktion:** siehe STATE.md (EXP-025 fertigstellen und auswerten, dann `queue_s5.sh` mit EXP-020 zuerst → EXP-028).
**Scheduler:** Aufgabe `GROKVERSE-Lab-Runner` aktiv; nächster Start laut `runner-state.json` 11:59:45Z = **13:59 Berlin**.
**Nachtrag 11:51:** EXP-025 fertig und ausgewertet: *teilweise* (r̄ eigener Nutzen 0.42, p = 0.003; Spezifität p = 0.12).
Kette danach um 11:51 kontrolliert gestoppt (`queue_s7.sh` und das gerade gestartete `queue_s5.sh` beendet, bevor ein
Trainingslauf daraus begann; keine Python-Prozesse mehr). Nächste Sitzung: direkt `sh lab/experiments/queue_s5.sh`.


## Sitzung 8 (2026-09-26, Start 11:59 Berlin, Deadline 14:59; Fenster heute bis 18:00)

**11:59 Start.** Kein STOP, Wächter im Fenster, keine Python-Prozesse. `queue_s5.sh` im Hintergrund gestartet (Log
`lab/runner/logs/queue_s5.log`): EXP-016/Baselines übersprungen, Smokes EXP-018/020 ok, seit 12:02 **EXP-020** Seed 30
(„nur F“ 371 s, „nur G“ 252 s; die Läufe sind schneller als die geplanten 4.5–17 min).

**Zyklus 1 (12:00–12:15): Ist die 5-Schritte-Festlegung aus EXP-032 ein AdamW-Artefakt? → EXP-033 vorab festgelegt.**
*Beobachtung (aus vorhandenen Daten):* In EXP-032 ist r am Umschaltschritt über alle 5 Splits fast identisch
(t_s = 5: 0.01180–0.01185; 20: 0.02893–0.02897), ebenso ds am Umschaltschritt. Das passt zu gleichförmigen
Vorzeichen-Schritten von Adam (erster Schritt = lr · sign(g), unabhängig von der Gradientengröße). *Literatur:*
Abuduweili & Liu 2024 (https://arxiv.org/abs/2412.02153): v₀ = 0 macht Adams ersten Schritt zu einem Vorzeichen-Schritt, der
bei kleinen frühen Gradienten unverhältnismäßig groß ist; Kleinman, Achille & Soatto 2023 (https://arxiv.org/abs/2308.12221):
kritische Perioden schon in tiefen linearen Netzen, also nicht an Optimierer-Details gebunden. Suche 12:03: „Adam sign
descent first steps small initialization feature selection lock-in critical period two-layer network“, „critical learning
periods deep linear networks Kleinman Achille 2023“. *Folgerung:* Die Aussage „5 Schritte“ ist eine Aussage über die
Adam-Schrittgröße, nicht über die Lerndynamik. Offen: Hängt die Festlegung selbst am Weg? → [[experiments/EXP-033-optimizer-lockin/README|EXP-033]]:
σ_3-Phase mit GD (bzw. signGD) bis zur gleichen Amplitude wie AdamW, dann identische x²-Phase mit frischem AdamW.
**Codex-Review (12:06–12:12, `EXP-033/codex_review_2026-09-26.txt`):** needs-attention, 6 × high. Übernommen: Pseudoreplikation
(15 Einheiten aus 5 Splits) → Split als Einheit, 10 Splits; Median-Definition (torch nimmt bei gerader Zahl den unteren Wert,
EXP-032 den NumPy-Mittelwert) → angeglichen, Ziel-r aus dem eigenen Kontrolllauf, Toleranz 2 %; Optimierer-Reset → Arm
„AdamW behalten“ berichtet; Punktquotient → Bootstrap-KI; lr-Wahl uneindeutig und am Bestätigungs-Split → Pilot mit
Init-Seed 99 und deterministischer Regel; Queue fail-closed. Nicht übernommen: volles Faktorialdesign und large-ε-Adam
(zu teuer für die Frage); stattdessen signGD-Arm, der den vermuteten Mechanismus direkt isoliert. Nachtrag a (commit 840e890)
ersetzt das erste Design; es lief kein EXP-033-Lauf vorher. *Ergebnis des Zyklus:* Versuch vorbereitet, noch nicht
ausgeführt (Jobplatz belegt durch EXP-020). Plan: nach EXP-020 Seed 30 die Warteschlange zwischen zwei Läufen anhalten,
EXP-033 laufen lassen (~70 min), danach `queue_s5.sh` fortsetzen.
**12:17 Nachtrag b zu EXP-033 (ohne Training):** Lineare Moden der σ_3-Phase (`linear_modes.py`): Die 10 obersten
Singulärvektoren von J = Xᵀ(Y − 1/P) haben in 10/10 Splits ihre stärkste Frequenz in F; ds der Top-5-Moden 0.38, von J
und sign(J) je 0.105; Spektrum flach (12.0 → 9.0 bei Index 20). Vorab: ds am Umschaltschritt GD > AR in ≥ 7/10 (schwach).
Synthetischer Test der Auswertung 7/7 (`test_analyze.py`, über den Wächter), dabei Importkonflikt `analyze` behoben.
**12:18 Warteschlange angehalten:** `sh`-Prozess von `queue_s5.sh` beendet, der laufende EXP-020-Lauf (Seed 30, t = 50) läuft
zu Ende; danach startet `EXP-033/queue.sh` automatisch (Log `lab/runner/logs/queue_exp033.log`). EXP-020 Seed 30 fertig
bisher: nur F (gen früh, 371 s), nur G (252 s), t = 150 (276 s).
**12:20 EXP-033 Pilot (Split 10, Init 99, nur Phase 1):** GD erreicht r = 0.0167 bei lr 0.3/1/3/10/30 in 750/226/76/24/9
Schritten, Überschuss 0.05/0.26/0.44/3.6/10.7 %. Regel → **lr = 3** (`lr.json`). Hauptläufe starten.
**12:25–12:30 Nachtrag c zu EXP-033 (Matching), ohne Ansicht eines ds-Werts:** Split 10 der ersten Hauptläufe: SIGN überschoss
das Ziel-r um 4.7 %, GD um 1.5 % (Toleranz 2 %). Warteschlange angehalten, Rückwärtshalbierung des letzten Schritts
eingebaut (`--backtrack`, Ziel ≤ +0.5 %), Split 10 neu: GD +0.35 % (77 Schritte, letzter Schritt × 0.25), SIGN +0.32 %
(11 Schritte). Die beiden Läufe ohne `_bt` bleiben unausgewertet. Warteschlange läuft weiter (~45 min).

**Zyklus 2 (12:20–13:18): EXP-033 ausgeführt und ausgewertet (vorab festgelegt, Nachtrag a–c).** 10 Splits × AR/GD/SIGN
+ 5 RET, alle vollständig, Amplitude ≤ 0.4 % getroffen, alle Endnetze Test 1.0. Δ (ankerbereinigt): AR 0.120, **GD 0.151**,
SIGN 0.133; Δ_GD > 0 in **10/10** (p = 0.001); R = 1.26, KI [1.10, 1.46] → vorab-Kategorie ***zustandsbestimmt***.
Nachtrag b (lineare Moden) **bestätigt:** ds am Umschaltschritt GD > AR in 10/10 (0.105 gegen 0.066). SIGN ≈ AR.
Post hoc: ds(J) des Splits sagt die GD-Neigung am Umschaltschritt voraus (Spearman 0.84; AR 0.62; Ende 0.42/0.30).
RET − AR = 0.015 (Optimierer-Reset kostet wenig); RET 10–14 = EXP-032 t_s = 10 exakt (Kontrolle der Reproduzierbarkeit).
**Codex-Angriff auf die Schlussfolgerung (13:13–13:21, `EXP-033/codex_conclusion_review_2026-09-26.txt`), übernommen:**
Das Etikett überdehnt. Belegt: AdamW ist **in Phase 1** nicht nötig, bedingt auf AdamW-Phase 2, an Stufe t_s = 10. Nicht
belegt: Pfadunabhängigkeit (die Zustände unterscheiden sich), Erhalt ohne AdamW, die 5-Schritte-Stufe; Nachtrag c war
ergebnisblinde Änderung, kein reines Vorab-Protokoll. README entsprechend eingeschränkt.
*Entscheidung:* weiterprüfen → EXP-034.

**Zyklus 3 (13:21–13:33): EXP-034 vorab festgelegt (neue Intervention: Optimierer der Phase 2).** Frische Splits 60–69 (+ Pilot 70,
alle M0-Top-5 = Ziele), Teil A: Stufen 5 und 10 mit AdamW-Phase 2 (Bestätigung EXP-033 + 5-Schritte-Stufe ohne AdamW),
Teil B: GD-Phase 2 (Weight Decay so, dass die Schrumpfung pro Schritt der von AdamW gleicht) mit Vergleich je Split.
**Codex-Review (13:25–13:30):** 2 × high, 2 × medium, alle übernommen (Vergleich innerhalb derselben Splits, keine „braucht
AdamW“-Folgerung aus Nicht-Signifikanz, Pilot aus allen drei Startzuständen, idempotente Warteschlange) → Nachtrag a
(commit a7e9cf2). *Eigener Fehler:* Ein `sed` mit `\|` zerstörte den Nachtrag im README und wurde committet; aus dem vorigen
Commit wiederhergestellt (c36d212). Status: vorbereitet, **nicht ausgeführt**, `train_opt.py --opt2 gd` ungetestet (erst
der Pilot prüft den Pfad). Budget ≈ 3 h → nächste Sitzungen.

**13:38 EXP-020 Zwischenstand (beschreibend, 1/5 Seeds; das vorab festgelegte Urteil braucht alle Seeds):** Seed 30 vollständig
und gültig. d(t) = |K∩F| − |K∩G| nach Wechsel F → G bei t und genau 2000 G-Schritten: t = 0 −3, 10 −3, **25 −1, 50 +1**,
150 +3, 400 +3, 1000 +3, ∞ +3; monoton; gen_F = 950 → Seed stützt H20 (Festlegung im Intervall (25, 50], vor dem Grokking).
Ab t = 150 ist K **identisch** mit dem Lauf „nur F“ ([6, 12, 29, 42, 55]), obwohl danach 2000 Schritte nur G folgen.
*Einordnung (vorläufig):* Das ist das Transformer-Gegenstück zu EXP-032 (Zwei-Hot-Netz, Festlegung in ≤ 20 Schritten):
Auch hier legen wenige Dutzend AdamW-Schritte die Frequenzwahl fest. Ob das an Adams Vorzeichen-Schritten hängt, ist für
den Transformer offen (EXP-033/034 betreffen nur das Zwei-Hot-Netz).

**Zyklus 4 (13:33–13:47): Lineare Modenvorhersage für EXP-034 (Nachtrag b) und EXP-035 vorab festgelegt.**
(a) ds(J) der frischen Splits 60–69 berechnet (0.063–0.119, Split 69 am schwächsten) und als Vorhersage P34c festgelegt
(Spearman ≥ 0.5 mit der GD10-Neigung am Umschaltschritt). EXP-034-Auswertung synthetisch getestet (5/5).
(b) **EXP-035 (neue Intervention am Transformer):** Verschiebt ein Lernraten-Warmup (200 Schritte) die Festlegungszeit aus
EXP-020? Motivation: EXP-020 Seed 30 legt sich in (25, 50] Schritten fest; im Zwei-Hot-Netz hing die Festlegung an der
Amplitude, nicht am Optimierer. `freq_ban.py --warmup` ergänzt (Standard 0, Codepfad unverändert; die laufende
EXP-020-Warteschlange nutzt die Datei, deshalb atomar geschrieben, CRLF erhalten, Diff 10 Zeilen).
**Codex-Review (13:42–13:46):** 3 × high, 2 × medium, alle übernommen → Nachtrag a (b231fc6/f242775): Warmup nur in der F-Phase
(sonst ungleiche G-Budgets), gemessene Strecke ‖θ − θ₀‖ am Umschaltschritt, Hypothese abgeschwächt auf „hängt am
Lernratenplan“, Monotonie/gen_F-Pflicht, intervallsichere Einordnung, Metadatenprüfung, Smoke am Anfang der Queue.
*Eigene Fehler:* zweimal Zeilenenden bzw. f-String-Klammern falsch (sofort bemerkt und korrigiert, vor jedem Lauf).
Status: vorbereitet, nicht ausgeführt.

**Zyklus 5 (13:49): Literatur N14 und Verstärkungszeitpunkt (ohne Training).** (a) Suche zur kritischen Periode der Frequenzwahl
(N14): nichts Gleiches gefunden (vorläufig); Kosson et al. 2024 erklären Warmup über zu große frühe AdamW-Updates, passt zu
EXP-035. *Eigener Fehler:* einem Paper eine ungeprüfte Autorenschaft zugeschrieben, sofort entfernt.
(b) **Post hoc aus EXP-033:** Die frühe Neigung bleibt während der Memorisierung fast gleich (AR 0.066 → 0.076 bis Phase-2-Schritt
1000) und wächst um die Generalisierung (→ 0.117 bei 3000); GD und SIGN ebenso; der Anker bleibt bei ≈ 0. Deutung
(Spekulation): Der generalisierende Schaltkreis wird bevorzugt aus den bereits leicht stärkeren Frequenzen gebaut. Als P34d
für EXP-034 vorab festgelegt (Nachtrag c, f660a4b); Tests 5/5.
**Zwischenbilanz nach 5 Zyklen (§4):** Gelernt: Die frühe Festlegung im Zwei-Hot-Netz braucht in Phase 1 kein AdamW (EXP-033),
und der Transformer zeigt in einem Seed eine scharfe kritische Periode (EXP-020). Wiederholen wir uns? Das Thema „frühe
Festlegung“ zieht sich seit Sitzung 7; die Eingriffe wechseln aber (Aktivierung, Optimierer, Daten, Lernratenplan), und jede
Stufe beseitigt einen konkreten Einwand. Nächste Annahme zum Angreifen: dass ds (Anteil F − Anteil H) die richtige Messgröße
ist. Das K-basierte d aus EXP-020 und ds sollten an denselben Läufen verglichen werden (Idee, nicht festgelegt).

**Zyklus 6 (13:50): Herkunft der „Konfliktfrequenzen“ in EXP-020 Seed 30 (beschreibend, ohne Training).** F = [6, 29, 30, 42, 48],
G = [23, 32, 36, 43, 47]. In den Mischzuständen (Wechsel bei t = 25 bzw. 50) wachsen ab Schritt 250 die Frequenzen **34 und 39**
bis auf Anteile ≈ 0.10–0.13 (so stark wie Zielfrequenzen) und stehen am Ende in K. Geprüft: keine 2k-Oberwelle eines Ziels;
im Init-Spektrum nicht unter den Top-8; in den Masken-Spektren M0 von F, G, F∩G, G\F, F\G, F∪G nur auf Rang 11–54. Die
Erklärung „Summen-/Differenzton“ ist wertlos, weil 49 von 56 Frequenzen Summen oder Differenzen aus F∪G sind. *Ergebnis:*
Ursprung offen. *Frage für später* (nicht festgelegt): Treten in Mischzuständen generell Frequenzen außerhalb F ∪ G ∪ 2k auf
(Seeds 31–34), und sind es dieselben wie in einem Zufallssplit-Lauf mit derselben Init? → BACKLOG-Idee.

**Zyklus 7 (13:51): Angriff auf die Messgröße von EXP-033 (post hoc, beschreibend).** Statt ds das Top-5-Maß am Ende
(d₅ = |Top5 ∩ F| − |Top5 ∩ H|, |Top5 ∩ F|): Anker (nur x²) |K∩F| im Mittel **0.4**, AR **4.6**, GD **4.7**, SIGN **4.7**
(Splits 10–19). d₅ über dem Anker: AR 9/10 (Split 14 gleich, 2 gegen 2), GD 10/10, SIGN 10/10. *Ergebnis:* Der Kernbefund
(frühe σ_3-Phase → Endnetz nutzt fast genau die Ziele F, egal mit welchem Optimierer) ist unter dem gröberen Maß **stärker**
sichtbar als unter ds; der kleine GD-Vorsprung (R = 1.26) ist dagegen nur im feinen Anteilsmaß zu sehen und sollte nicht
überbetont werden. Kein Einfluss auf die vorab festgelegten Urteile.

**Zyklus 8 (13:52): Wo liegt die Festlegung relativ zur Memorisierung? (EXP-020 Seed 30, beschreibend).** Lauf „nur F“:
Trainingsgenauigkeit bei Schritt 25 ≈ 0.03–0.04, bei 50 **0.10**, Verlust 4.75 → 4.12 (ln 113 = 4.73); Train-Acc ≥ 0.97 erst bei
Schritt 120–130, Test ≥ 0.95 bei 950. Die Festlegung (25, 50] liegt also **vor** der Memorisierung, in der ersten Phase des
Verlustabfalls, nicht an ihrem Ende. Das passt zum Zwei-Hot-Befund (EXP-032/033: Festlegung bei ≈ 1.25–1.8 × Init-Amplitude,
lange vor dem Fit) und zu N13 (bei Schritt 250 ist die Zielmenge schon voll eingeprägt). 1 Seed; Bestätigung mit den übrigen
EXP-020-Seeds (beschreibend, nicht vorab festgelegt: Train-Acc bei hi ≤ 0.5 in allen gültigen Seeds).

**14:16 EXP-020 Seed 31 (beschreibend, 2/5 Seeds):** gültig, d = −2 (t=0), −2 (10), 0 (25), **+3 (50)**, +3 (150…∞), monoton,
gen_F = 625 → stützt H20, Intervall wieder **(25, 50]**. Ab t = 150 ist K identisch mit „nur F“ ([23, 29, 41, 45, 55]).
Nachtrag c: Train-Acc „nur F“ bei Schritt 50 = 0.108 ≤ 0.5 → erfüllt (1/1 der vorab festgelegten Seeds 31–34).
Zwischenstand H20: 2/2 stützen; Urteil erst mit allen Seeds.

### Abschlussbericht Sitzung 8 (2026-09-26, 11:59–~14:40 Berlin)

**Wichtigste Befunde:**
1. **[[experiments/EXP-033-optimizer-lockin/README|EXP-033]] (vorab festgelegt, Nachträge a–c):** Die frühe Festlegung im Zwei-Hot-Netz
   ist **kein AdamW-Artefakt der frühen Phase**: Reiner Gradientenabstieg bis zur gleichen Merkmalsamplitude erzeugt eine
   bleibende F-Neigung in 10/10 Splits (p = 0.001), etwas stärker als AdamW (R 1.26, KI [1.10, 1.46]); signGD ≈ AdamW.
   Vorab-Kategorie *zustandsbestimmt*, nach Codex **eingeschränkt**: belegt nur „AdamW in Phase 1 nicht nötig“, bei
   AdamW-Phase 2, Stufe t_s = 10. Die lineare Modentheorie sagte die stärkere GD-Neigung am Umschaltschritt vorher (10/10).
   Unter dem Top-5-Maß: Anker 0.4 von 5 Zielen, alle Arme 4.6–4.7.
2. **[[experiments/EXP-020-data-switch/README|EXP-020]] (2/5 Seeds, beschreibend):** Der Transformer legt seine Frequenzwahl nach
   **25–50 Schritten** fest (Seeds 30 und 31 identisch), vor der Memorisierung (Train-Acc ≈ 0.1); ab 150 Schritten F bleibt K
   nach 2000 G-Schritten exakt wie „nur F“. Beide Seeds stützen H20; Urteil erst mit 5 Seeds.
3. Post hoc: Die frühe Neigung wird vor allem um die Generalisierung verstärkt (P34d vorab für EXP-034); in Mischzuständen
   entstehen „Konfliktfrequenzen“ außerhalb F ∪ G ∪ 2k (Ursprung offen).

**Vorbereitet, nicht ausgeführt (alle nach Codex-Review umgebaut, Analysen synthetisch getestet):**
[[experiments/EXP-034-phase2-optimizer/README|EXP-034]] (GD auch in Phase 2, 5-Schritte-Stufe, frische Splits 60–69, Vorhersagen
P34c/P34d), [[experiments/EXP-035-warmup-lockin/README|EXP-035]] (Warmup gegen die Festlegungszeit des Transformers).
Grund: Jobplatz durch EXP-020 belegt. Nächster Schritt: `sh lab/experiments/queue_s8.sh`.

**Offene Grenzen:** Zwei-Hot-Befunde an einer Architektur; Phase 2 bisher immer AdamW; EXP-020 erst 2 Seeds; Warmup-Effekt
ungeprüft; `train_opt.py --opt2 gd` und `freq_ban.py --warmup` sind im echten Lauf ungetestet (beide Queues beginnen mit
Pilot bzw. Smoke und stoppen bei Fehlern).
**Codex:** fünf Reviews (EXP-033 Design, EXP-033 Schluss, EXP-034, EXP-035, jeweils needs-attention), alle Einwände geprüft,
fast alle übernommen (nicht: volles Faktorialdesign und large-ε-Adam in EXP-033).
**Eigene Fehler:** mehrfach geschätzte statt gemessene Uhrzeiten (korrigiert); ein `sed` mit `\|` zerstörte einen README-
Abschnitt (aus Git wiederhergestellt); ein f-String mit geschweiften Klammern; eine ungeprüfte Autorenzuschreibung (entfernt);
eine Warteschleife mit zu breitem `grep "stop"`.
**Reproduktion:** EXP-033: `sh lab/experiments/EXP-033-optimizer-lockin/queue.sh`, dann
`python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/analyze.py`; EXP-020: `queue_s5.sh`/`queue_s8.sh`
und `EXP-020-data-switch/analyze.py`; lineare Moden: `EXP-033-optimizer-lockin/linear_modes.py [--split-dir … --seeds …]`.
**Scheduler:** Aufgabe `GROKVERSE-Lab-Runner` aktiv; nächster Start laut `runner-state.json` 2026-09-26T14:59:45Z = **16:59 Berlin**
(Fenster heute bis 18:00, ab dem 27.09. wieder 00:00–13:00).
**Nachtrag 14:44:** Nach dem Anhalten der Queue noch drei Einzelläufe mit den Queue-Argumenten (Seed 32, t = 50, 25, 10), alle
fertig (rc 0). EXP-020 Seed 32 fehlen noch t = 400 und 1000. Keine Python-Prozesse mehr. Sitzung beendet.

## Sitzung 9 (2026-09-26, Start 14:49 Berlin, Deadline 17:49)

**14:50:** Wächter ok (Fenster heute bis 18:00), keine Prozesse; `sh lab/experiments/queue_s8.sh` gestartet (Log
`lab/runner/logs/queue_s8.log`): EXP-020 Seed 32 (t = 400, 1000), dann Seeds 33, 34, danach EXP-035, EXP-034.

**Zyklus 1 (14:52): Fremde Frequenzen in Mischzuständen (EXP-020, ohne Training).** Frage aus Sitzung 8, Zyklus 6: Treten
Frequenzen außerhalb F ∪ G ∪ 2k auch in anderen Seeds auf? `conflict_freqs.py`: Ja, in allen drei bisherigen Seeds, nur bei
t ≤ 50, nie bei t ≥ 150 (Seed 32: bisher nur t = 150). Zusätzlich auch außerhalb K_nurF ∪ K_nurG. Ihre Init-Ränge im
W_E-Spektrum bei Schritt 0: 1, 2, 4, 8, 11, 18, 29 (Median 8 von 56). *Ergebnis:* Muster in 3/3 Seeds (Exploration).
*Entscheidung:* für die noch nicht gelaufenen Seeds 33/34 vorab festgelegt (Nachtrag d, P-d1/P-d2, commit 7537783).
Ein kausaler Test wäre ein Initwechsel bei gleichem Split (Idee, nächster Zyklus).

**Zyklus 2 (14:55–15:00): Literatur N15 und Angriff „nur Init-Rest“ (ohne Training).** (a) Suche (Suchbegriffe in
[[NOVEL_DIRECTIONS]] N15): He et al. 2026 (arXiv 2602.16849) zeigen für Zweischicht-Netze, dass Init-Betrag und Phase die Frequenz
je Neuron auswählen („Lottery Ticket“) → Init-Auswahl an sich **bekannt**; Lyle et al. 2025 (arXiv 2507.20057) verbinden Primacy
Bias mit Grokking (relevant für EXP-020/N14). Nicht gefunden: Rückgabe der Wahl an die Init durch widersprüchliche frühe Splits.
(b) Einwand: Sind fremde Frequenzen nur Init-Reste in nicht fertig trainierten Netzen? Test-Acc der Mischläufe: Seed 30 t = 25/50:
0.95/1.00 (fremd 34, 39), Seed 31 t = 25/50: 0.99/1.00 (fremd 22 bzw. 42), Seed 32: 0.90/0.16/0.90, Seed 31 t = 10: 0.50.
*Ergebnis:* Fremde Frequenzen stehen auch in voll generalisierenden Netzen → nicht nur Rest. Für EXP-036 als beschreibende
Zusatzangabe übernehmen (Test-Acc je Lauf mit fremder Frequenz).

**Zyklus 3 (14:57–15:02): Codex-Angriff auf EXP-036 und Nachtrag d (ohne Training).** Codex (`adversarial-review --wait
--base bc66a11`, Ausgabe `EXP-036-init-conflict/codex_review_2026-09-26.txt`): needs-attention, vier Befunde. (1, hoch) Frequenzen
wurden als unabhängige Versuche gezählt; ein Paar mit 5 gleichgerichteten Frequenzen hätte p = 1/32 ergeben. **Übernommen:**
Einheit = Paar, 7 Paare statt 3. (2, hoch) Die alte fremde Menge ging nicht ins Urteil ein. **Übernommen:** Jaccard-Bedingung;
symmetrische Statistik nur beschreibend für Splits 33/34 (30–32 sind gesehen). Codex' Vorschlag „Init-Label-Permutation“
**nicht übernommen**: Die naheliegende symmetrische Statistik ist unter Vertauschen der Labels invariant, also kein Test.
Vorschlag „nur W_E verpflanzen“ als Folgeversuch notiert. (3, 4, mittel) Keine `result.json`-Prüfung. **Übernommen:** ein
gemeinsamer strenger Lader (`load_run`) für Nachtrag d und EXP-036; Seeds 30/31 geben damit dieselben fremden Mengen,
Seed 32 wird korrekt abgelehnt, solange t = 1000 läuft. *Eigener Fehler:* Im Selbsttest 6/7 als signifikant angenommen
(p = 0.0625); korrigiert, nicht die Regel. Und zweimal geschätzte Uhrzeiten in Nachträge geschrieben (korrigiert auf gemessene).
Commit 6bf7775; `queue_s9.sh` = queue_s8 mit EXP-036 nach EXP-035.

**15:02 EXP-020 Seed 32 (beschreibend, 3/5 Seeds):** gültig, d = −4 (t=0), −4 (10), −3 (25), **+3 (50)**, +3 (150…∞), monoton, gen_F = 1225
→ stützt H20, Intervall wieder **(25, 50]** (3/3 Seeds identisch). Nachtrag c: Train-Acc „nur F“ bei Schritt 50 = 0.102 ≤ 0.5
→ erfüllt (2/2 der Seeds 31–34). Nachtrag d (Exploration): fremd 13 (t = 10), 8, 13 (t = 25, 50), keine bei t ≥ 150.

**Zyklus 4 (15:03): Ist die Festlegung dauerhaft oder nur langsam? (EXP-020, beschreibend, ohne Training).** Einwand: EXP-020 misst K
nach nur 2000 G-Schritten; bei Weight Decay 1.0 (Zeitskala ≈ 1/(lr·wd) = 1000 Schritte) könnte das Netz später doch zu G wandern
(vgl. Primacy Bias, Lyle et al. 2025). Messung: Leistungsanteil der Zielfrequenzen F bzw. G im W_E-Spektrum während der G-Phase,
Läufe t = 150, 400, 1000, Seeds 30–32. *Ergebnis:* Der F-Anteil **steigt** in der G-Phase weiter (Seed 30, t = 150: 0.36 → 0.91;
Seed 31: 0.40 → 0.82; Seed 32: 0.30 → 0.76), der G-Anteil fällt (0.068 → 0.010; 0.056 → 0.007) bzw. bleibt bei Seed 32 flach
(≈ 0.07, weil G-Ziel 22 = 2 · 11 die Oberwelle eines F-Ziels ist). Kein Trend zu G über die 2000 G-Schritte (≈ 2 Weight-Decay-Zeitkonstanten).
Deutung: Sobald das Netz mit F-Frequenzen generalisiert, löst es auch alle G-Paare; es gibt keinen Gradienten zu G mehr,
die Festlegung vertieft sich. *Entscheidung:* kein Langlauf-Versuch (erwarteter Erkenntnisgewinn gering), Einwand als
beschreibend beantwortet notiert. Grenze: 3 Seeds, je 2000 G-Schritte, keine Aussage über viel längere Zeiträume.

**Zyklus 5 (15:07): EXP-037 vorbereitet (neue Intervention: blockweiser F/G-Wechsel in der kritischen Periode) und eine
Konkurrenzerklärung geprüft (ohne Training).** Frage: Gibt anhaltender Datenkonflikt die Wahl an die Init zurück (N15)?
freq_ban.py: neue Option --alternate-every (Standard 0 = unverändert, compile-geprüft während die Queue lief). Vorab
festgelegt in [[experiments/EXP-037-alternation-conflict/README|EXP-037]] (commit 3325b72). Eigene Einwandprüfung: Ein
schneller Wechsel wirkt etwa wie Training auf der gemittelten Maske (F + G)/2; deren Masken-Spektrum könnte „fremde“ Frequenzen
von der Split-Seite liefern. An den Einzelwechsel-Läufen (Seeds 30–32, Exploration): M0-Ränge der fremden Frequenzen unter der
gemittelten Maske 19, 18, 40, 19, 13, 9, 45 (Median 19), Init-Ränge 11, 29, 1, 2, 8, 4, 18 (Median 8). *Ergebnis:* Die Init
beschreibt sie besser als die Mischmaske; beides nur Assoziation an 7 Frequenzen. Für EXP-037 wird der Mischmasken-Rang
zusätzlich berichtet.

**Zyklus 6 (15:13): Codex-Angriff auf EXP-037 (ohne Training).** Codex (Ausgabe `EXP-037-alternation-conflict/codex_review_2026-09-26.txt`):
needs-attention; Blockplan, Parität und unveränderte Lauf-IDs bestätigt. Drei Einwände, alle **übernommen** (Nachtrag a):
(1) Urteile nicht exklusiv → *mehrdeutig*, wenn H37 und eine Alternative zugleich gelten; (2) fehlende Kontrollen → C_F100
(gleiche Exposition ohne Wechselspiel) und Mischmasken-Top-5 in A; (3) Smoke nur Metadaten, evtl. veraltet → frischer
Smoke mit Hash-Spur je Blockwechsel (`alternation_trace`, `check_smoke.py`). Nicht umgesetzt: echtes gewichtetes
Mischtraining (Begründung im README). **Warteschlange umgestellt:** `queue_s8.sh` angehalten (nur der sh-Prozess; der laufende
EXP-020-Lauf Seed 33 „nur G“ läuft zu Ende), `queue_s9.sh` gestartet (Log `lab/runner/logs/queue_s9.log`): EXP-020 Rest →
Auswertungen → EXP-037 → EXP-035 → EXP-036 → EXP-034 → queue_s5.
*Eigener Fehler (zweimal in dieser Sitzung):* Backticks in einem ungeschützten Heredoc wurden von der Shell ausgeführt
(einmal wurde dabei die Logdatei als Skript gestartet und brach sofort mit Syntaxfehler ab, keine Wirkung); Text repariert.
Ab jetzt Journaltext nur noch über Python oder `<<'EOF'` schreiben.

**15:43 EXP-020 Seed 33 (4/5 Seeds; erster frischer Seed für Nachtrag d).** d = −4 (t=0), −5 (10), −5 (25), **+2 (50)**, +3 (150…∞), gen_F = 1325.
Intervall wieder (25, 50], aber **nicht monoton** (d(10) < d(0)): Der reine G-Lauf hat 6 = 2 · 3 (Oberwelle des G-Ziels 3) statt
des G-Ziels 34 in K. Nach der vorab festgelegten Regel (Monotonie Pflicht) zählt Seed 33 **gegen H20**; das ist eine Folge der
strengen Regel, nicht eines anderen Festlegungsintervalls. Wird so berichtet, die Regel wird nicht nachträglich geändert.
Nachtrag c: Train-Acc „nur F“ bei Schritt 50 = 0.089 ≤ 0.5 → erfüllt (3/3 der Seeds 31–34).
**Nachtrag d, Seed 33:** fremd nur 38 (t = 50), keine bei t ≥ 150 → **P-d1 erfüllt**. Aber Init-Rang von 38 = **34** (von 56),
also eher Zufall als Init-Spitze; spricht für P-d2 in die Gegenrichtung (Entscheid erst mit Seed 34). Der t = 50-Lauf
generalisierte nach 2000 G-Schritten nicht (gen None).

**Zyklus 7 (15:43): Robustheit der Messgröße d (post hoc, beschreibend, ohne Training).** Anlass: Seed 33 verletzt die Monotonie nur
wegen einer Oberwelle. Alternative Messgröße d_h: F- bzw. G-Seite einschließlich fold(2k) ihrer Ziele, Frequenzen auf beiden
Seiten ausgenommen. *Ergebnis:* d_h ist in allen 4 Seeds (30–33) monoton, erstes positives d_h immer bei t = 50, d_h(25) ≤ 0
→ Intervall (25, 50] in 4/4. Seed 33: −4, −4, −4, +2, +4, … *Einordnung:* Nachträglich gewählte Messgröße, ändert das vorab
festgelegte Urteil nicht (Seed 33 bleibt *gegen H20*); zeigt aber, dass die Gegenstimme eine Messartefakt-Frage ist, kein
anderes Festlegungsverhalten. Für künftige Versuche d_h vorab festlegen.

**16:22 [[experiments/EXP-020-data-switch/README|EXP-020]] abgeschlossen, [[experiments/EXP-028-memo-imprint/README|EXP-028]] abgeschlossen, Nachtrag d entschieden.**
Seed 34: d = −4, −3, −3, +3, +5 …, monoton, Intervall (25, 50], gen_F = 650, stützt H20; Train-Acc bei Schritt 50 = 0.109.
**EXP-020 (vorab festgelegt): *nicht bestätigt*** (4/5 stützen, p = 0.19); einzige Gegenstimme Seed 33 wegen Nicht-Monotonie
durch eine Oberwelle. Beschreibend: Intervall (25, 50] in 5/5 Seeds; Nachtrag c *bestätigt* (4/4). Keine nachträgliche
Umdeutung: Die Monotonie-Regel war zu streng gewählt, das ist die Lehre für Folgeversuche (d_h vorab festlegen).
**Nachtrag d:** P-d1 Seed 33 erfüllt, Seed 34 nicht; P-d2 nicht erfüllt (Rang 34). *Die Init-Deutung der fremden Frequenzen
ist an frischen Seeds nicht bestätigt* (negativer Befund). N15 abgeschwächt; EXP-036 und EXP-037 bleiben als direktere Tests
sinnvoll, die Erwartung für H36/H37 sinkt.
**EXP-028: P28a *teilweise*** (6/10 Läufe mit 5/5 im Fenster, gefordert 8; Mittel 4.5); P28b: 5/6 verlieren Ziele, alle 8
Ersetzungen sind 2k-Oberwellen.

**Zwischenbilanz Sitzung 9 (16:23, §4):** *Gelernt:* Die kritische Periode der Frequenzwahl ist über 5 Seeds bemerkenswert
gleichförmig (25–50 Schritte) und vertieft sich nach der Festlegung; die in der Exploration auffällige Init-Herkunft „fremder“
Frequenzen hielt an frischen Seeds nicht (Vorab-Festlegung hat hier eine Überdeutung verhindert). *Wiederholen wir uns?*
Nein in den Eingriffen (Init-Wechsel, Wechselspiel, neue Messgröße), aber das Thema ist seit drei Sitzungen dasselbe.
*Messungen geeignet?* Das Top-5-Maß ist anfällig für 2k-Oberwellen (Seed 33); d_h künftig vorab. Ob fremde Frequenzen
funktional sind, ist ungeklärt (Ablation vorbereitet). *Nächste Annahme zum Angreifen:* dass „Festlegung“ im W_E-Spektrum
dasselbe ist wie Festlegung des Schaltkreises: Ein Eingriff, der nach t = 50 nur W_E zurücksetzt (Rest behalten), würde
zeigen, ob die Festlegung in W_E oder in den übrigen Gewichten sitzt (Idee, nicht festgelegt). *Priorität geändert:*
`queue_s10.sh` stellt EXP-034 vor EXP-036.

**Zyklus 8 (16:31): EXP-038 vorbereitet (neue Intervention: Teil-Rücksetzen nach der Festlegung) und von Codex angegriffen.**
Frage aus der Zwischenbilanz: Wo sitzt die Festlegung? `freq_ban.py --reset-at-switch we|rest` (neu). Literatur (N16): nichts
Gleiches gefunden (vorläufig). Codex (needs-attention): Umsetzung korrekt; aber (1) d_h ≤ 0 zählte Unentschieden als Umschlag,
(2) RR setzt 93.5 % der Gewichte zurück, der Vergleich misst Eingriffsgröße und Neulernen mit, (3) Smoke prüfte nur Zählwerte.
Alle drei übernommen (Nachtrag a): d_h < 0 / > 0 getrennt, Test-Acc-Schwelle 0.9, Deutung als Notwendigkeit/Hinlänglichkeit
statt Speicherort, Selbstprüfung des Rücksetzens im Trainer. Nicht übernommen: norm-angepasste Kontrollen (Folgeversuch).
Nebenbeobachtung EXP-037 (Läufe bisher 2/9): Das Wechselspiel erzeugt in Seed 30 wieder 34, in Seed 31 wieder 22, dieselben
fremden Frequenzen wie der Einzelwechsel desselben Seeds. Fremde Frequenzen wirken je Seed reproduzierbar (beschreibend).

**16:50 [[experiments/EXP-037-alternation-conflict/README|EXP-037]] Primärarm (A = 5) und Kontrolle fertig, ausgewertet.**
C_F100 (F 100, dann G 2100): K = K_nurF in 3/3, keine fremde Frequenz. A = 5: K = [6, 29, 34, 45, 47], [8, 22, 29, 41, 44],
[8, 11, 13, 35, 50]; d = +1, +1, 0; fremd 34, 45 | 22, 44 | 8, 13, 50; Init-Ränge 11, 26 | 8, 26 | 4, 18, 9 (Median 11);
Mischmasken-Ränge 19, 40 | 13, 20 | 9, 45, 54; Test-Acc 1.0, 1.0, 0.48.
**Vorab festgelegtes Urteil (A = 5): *gestützt*.** Einschränkungen, ehrlich: (a) Der Median ≤ 14 wird von den schon aus der
Exploration bekannten Frequenzen getragen (34, 22, 8, 13); die neuen (45, 44, 50) haben Init-Ränge 26, 26, 9. (b) **45 =
fold(2 · 34) und 44 = fold(2 · 22)**: Die „neuen“ fremden Frequenzen sind Oberwellen der wiederkehrenden. (c) Nachtrag d
(frische Seeds) hatte die Init-Deutung nicht bestätigt.
**Ablation (Nachtrag b, beschreibend):** Die wiederkehrenden fremden Frequenzen sind **funktional** (Δloss beim Entfernen:
34 → 1.38, 22 → 1.57, 8 → 3.28, 13 → 4.19; Ziele 0.3–3.2; Zufallsfrequenzen ≈ 0). Die Oberwellen 45, 44 nur schwach
(Δloss 0.011, 0.005, „dazwischen“). 50 in Seed 32 funktional (Netz dort nur 0.48 Test-Acc).
*Deutung (vorläufig):* Je Seed gibt es eine reproduzierbare, im Schaltkreis genutzte „Konfliktfrequenz“, die bei anhaltendem
oder frühem F/G-Konflikt auftaucht, bei gleicher Exposition ohne Konflikt (C_F100) nicht. Ob die Init sie bestimmt, bleibt
offen (gemischte Evidenz); EXP-036 (Init-Wechsel) ist der direkte Test und gewinnt damit wieder an Wert.

**17:04 EXP-037 A = 25 (sekundär): *gestützt*.** fremd 34 | 42 | 8, 13, 26, 30; wieder dieselben Kernfrequenzen je Seed wie beim
Einzelwechsel (Seed 31 hier 42 statt 22; beide traten dort auf), 26 = fold(2 · 13). Ablation: Kernfrequenzen funktional, Oberwellen
kaum. EXP-037 damit abgeschlossen. Die Queue ist zu EXP-035 übergegangen (Smoke ok).

**Zyklus 9 (17:05): Woher kommen die Konfliktfrequenzen? Neue datenbasierte Hypothese (post hoc, ohne Training).** Ränge der
Kern-Konfliktfrequenzen im W_E-Spektrum der reinen Läufe: schon bei Schritt 250 meist Rang 6–10, oft in beiden Läufen
(Seed 30: 34 → 6 in F, 7 in G). Unter den ≈ 37 Kandidaten außerhalb A, geordnet nach Rang(F@250) + Rang(G@250): 34 → 1;
36 → 3, 22 → 4, 42 → 7; 13 → 2, 8 → 4; 38 → 3. Mehrere der vorhergesagten Top 3 traten tatsächlich als fremd auf (Seed 30: 34, 39;
Seed 32: 30, 13, 50). *Ergebnis:* starke Assoziation in der Exploration (7/7 auf Platz ≤ 7). *Entscheidung:* als P36b für die
frischen Inits von EXP-036 vorab festgelegt (Nachtrag b). Das ist eine Konkurrenz zur Init-Deutung: nicht die Init allein,
sondern die gemeinsame frühe Unterstützung durch beide Datensätze.

**Zyklus 10 (17:07): Ist „gemeinsame frühe Unterstützung“ nur der Init-Rang in anderer Form? (post hoc, ohne Training).**
Position der 7 Kern-Konfliktfrequenzen unter den Kandidaten außerhalb A (≈ 37) nach gemeinsamer Unterstützung bzw. nach Init-Rang:
34: 1 / 9; 22: 4 / 6; 42: 7 / 2; 36: 3 / 1; 8: 4 / 3; 13: 2 / 13; 38: 3 / 23. Median 3 gegen 6; Maximum 7 gegen 23.
*Ergebnis:* Beide Ordnungen sind verwandt (die frühe Unterstützung enthält die Init), aber die gemeinsame Unterstützung ist der
engere Prädiktor; die Fälle 13 und 38 erklärt nur sie. Exploration an denselben Daten, keine Bestätigung. Prüfung an frischen
Inits: EXP-036 P36b (vorab festgelegt).

**Zyklus 11 (17:15): Codex greift die Schlussfolgerungen von EXP-037 und P36b an** (`EXP-037-alternation-conflict/codex_conclusion_review_2026-09-26.txt`,
needs-attention). Übernommen: (1) C_F100 trennt nur Wechselplan von Festlegung, nicht Konflikt als Ursache → „vom Wechselplan
abhängig“, nicht „konfliktspezifisch“; (2) „reproduzierbar“ nur innerhalb der drei explorierten Seeds; (3) P36b ist kein
kalibrierter Test → nur beschreibend (EXP-036 Nachtrag c), kalibrierte Fassung vor dem EXP-036-Start nachholen; (4) „funktional“
nur für generalisierende Modelle (34, 22, 8, 13; 42 schwach); (5) „engerer Prädiktor als der Init-Rang“ ist nur ein
explorativer Kandidat (je Frequenz 4 besser, 3 schlechter; Schritt 250 liegt nach dem Festlegungsfenster). Nichts verworfen.
Die vorab festgelegten Urteile bleiben unverändert.
Nebenbei EXP-035 (1 Lauf, kein Urteil): Seed 30, Wechsel bei t = 50 **mit** Warmup endet auf der G-Seite (K = [23, 33, 36, 46, 47]),
ohne Warmup war t = 50 schon F-lastig (d = +1). Richtung H35 (Warmup verzögert die Festlegung).

### Abschlussbericht Sitzung 9 (2026-09-26, 14:49–~17:45 Berlin; geschrieben 17:06)

**Wichtigste Befunde:**
1. **[[experiments/EXP-020-data-switch/README|EXP-020]] abgeschlossen (5 Seeds).** Vorab festgelegtes Urteil *nicht bestätigt*
   (4/5 stützen H20, p = 0.19); einzige Gegenstimme Seed 33, nur weil d(t) wegen einer 2k-Oberwelle nicht monoton ist.
   Beschreibend: Die Frequenzwahl legt sich in **5/5 Seeds zwischen Schritt 25 und 50** fest, vor der Memorisierung
   (Train-Acc ≈ 0.1, Nachtrag c *bestätigt* 4/4), weit vor dem Grokking (gen_F 625–1325); ab t = 150 bleibt K exakt wie „nur F“,
   und in der G-Phase vertieft sich die Festlegung. Mit dem Oberwellen-erweiterten Maß d_h ist d in allen Seeds monoton.
2. **[[experiments/EXP-028-memo-imprint/README|EXP-028]]:** P28a *teilweise* (6/10 Läufe 5/5); P28b: Ziele gehen um die
   Generalisierung verloren, alle 8 Ersetzungen sind 2k-Oberwellen.
3. **Negativer Befund (Vorab-Vorhersage):** Die in der Exploration auffällige Init-Herkunft „fremder“ Frequenzen hielt an frischen
   Seeds nicht (EXP-020 Nachtrag d: P-d1 1/2, P-d2 verfehlt).
4. **[[experiments/EXP-037-alternation-conflict/README|EXP-037]] (neu, vorab festgelegt, nach Codex umgebaut):** *gestützt*
   (A = 5 und A = 25); nach Codex-Angriff eingeengt (Nachtrag c): Wiederholtes F/G-Wechseln in der kritischen Periode erzeugt in
   den drei explorierten Seeds über Wechselpläne hinweg dieselben fremden Frequenzen, ein einzelner Wechsel nach der Festlegung
   (C_F100) nicht; in generalisierenden Modellen sind 34, 22, 8, 13 funktional genutzt. Konfliktspezifität, unabhängige
   Replikation und Init-Herkunft sind **nicht** gezeigt.
5. **Explorativer Kandidat (post hoc):** Konfliktfrequenzen könnten die Frequenzen sein, die **beide** Datensätze früh stützen
   (7/7 auf Kandidatenplatz ≤ 7 von ≈ 37). P36b nach Codex nur beschreibend; kalibrierter Test vor dem EXP-036-Start nachholen.

**Vorbereitet, nicht ausgeführt:** [[experiments/EXP-036-init-conflict/README|EXP-036]] (neue Inits, 7 Paare, Paar-Test; Nachträge a, b),
[[experiments/EXP-038-where-lockin/README|EXP-038]] (Teil-Rücksetzen nach der Festlegung; Nachtrag a), beide nach Codex umgebaut,
Analysen mit Selbsttests; `--reset-at-switch` im echten Lauf ungetestet (Smoke vorgeschaltet). EXP-034 unverändert vorbereitet.
EXP-035 lief ab 17:03 an (Smoke ok, Seed 30 „nur F“ mit Warmup); Rest in `queue_s10.sh`.

**Offene Grenzen:** Alle Transformer-Befunde an einer Architektur und Splits aus einem Generator; EXP-037 an denselben Seeds wie
die Exploration; Top-5-Maß anfällig für Oberwellen; Konfliktfrequenzen nur an 5 Seeds beschrieben.
**Codex:** vier Reviews (Design EXP-036, EXP-037, EXP-038; Schlussfolgerung EXP-037/P36b; alle needs-attention), alle Einwände geprüft, fast alle übernommen (nicht:
Init-Label-Permutation für EXP-036, gewichtetes Mischtraining für EXP-037, norm-angepasste Kontrollen für EXP-038; Gründe in den READMEs).
**Eigene Fehler:** mehrfach geschätzte statt gemessene Uhrzeiten (korrigiert); zweimal Backticks in ungeschützten Heredocs
(Journaltext repariert, keine Wirkung); versehentlich `git commit -a` mit den uncommitteten Runner-Dateien des Nutzers
(sofort per `git reset --soft` rückgängig, Dateien unverändert, wieder uncommittet); zwei falsche Selbsttest-Erwartungen (Tests
korrigiert, nicht die Regeln).
**Reproduktion:** EXP-020: `sh lab/experiments/queue_s9.sh` (EXP-020-Teil) + `EXP-020-data-switch/analyze.py`, Nachtrag d:
`EXP-020-data-switch/conflict_freqs.py`; EXP-037: `sh lab/experiments/EXP-037-alternation-conflict/queue.sh`, dann `analyze.py`
und `ablate_foreign.py` (je über `python lab/tools/guarded_run.py -- python …`).
**Nächste Aktion:** Im Fenster (ab 00:00): `sh lab/experiments/queue_s10.sh` (EXP-035 → EXP-038 → EXP-036 → EXP-034 → queue_s5).
**Scheduler:** Aufgabe `GROKVERSE-Lab-Runner` aktiv; nächster Start laut `runner-state.json` 2026-09-26T17:49:44Z = **19:49 Berlin**
(außerhalb des Fensters: dann nur Denkarbeit; Läufe ab 00:00).

## Sitzung 10 (2026-09-26, Start 17:29 Berlin, Deadline 20:29; Fenster heute bis 18:00)

**Lage beim Start (17:30):** `queue_s9.sh` lief noch aus Sitzung 9 (EXP-035 Seed 30). Um 17:36 lehnte der Wächter den nächsten
Lauf ab (Sitzungsbudget der alten Sitzung, rc 3), die Queue stoppte sauber. **EXP-035 Seed 30 vollständig** (7 Läufe, Warmup 200):
nur F → K = [6, 12, 29, 42, 55] (gen 975); Wechsel t = 10, 25 → [19, 23, 36, 41, 47]; t = 50 → [23, 33, 36, 46, 47];
t = 100 → [6, 19, 29, 34, 47]; t = 150, 250 → [6, 12, 29, 42, 55] = nur F. Beschreibend (kein Urteil, EXP-035 wertet über 3
Seeds aus): Mit Warmup liegt die Festlegung bei Seed 30 zwischen 100 und 150 statt (25, 50]. Richtung H35.

**Zyklus 1 (17:30–17:35): P36b kalibriert festlegen (EXP-036 Nachtrag d, ohne Training).** Frage: Sind die fremden Frequenzen die,
die beide Datensätze *vor* der Festlegung anschieben, und ist das enger als das Init-Spektrum? Dafür braucht es Spektren vor
Schritt 25; `freq_ban.py` speicherte nur alle 250 Schritte. Änderung: `--spectra-at` (reine Protokollierung, Run-ID unverändert,
commit 3e1144e). Test: Wachstum bis τ = 20, konjunktiver Rang max(Rang_F, Rang_G), Paar als Einheit, Test 1 gegen Zufall
(Bin(m, 0.25), konservativ, per Monte Carlo geprüft), Test 2 gegen den Init-Rang. Ergebnis: vorab festgelegt (commit a1c2642),
Selbsttest ok. Eigener Fehler: zwei falsche Erwartungen im Selbsttest (Gleichstände bei wenigen Kandidaten übersehen); Tests
korrigiert, nicht die Regel.

**Zyklus 2 (17:35–17:41): Codex greift Nachtrag d an** (`codex_review_nachtrag_d_2026-09-26.txt`, needs-attention). (1, hoch) Die
Gleichverteilungs-Null von Test 1 bildet die Auswahl (End-Top-5 minus A, gemeinsames Präfix) nicht nach. *Übernommen:* Test 1
nur „nicht selektionsbereinigt“; neuer Test 3 gegen Einarm-Wachstum (F allein, G allein) unter derselben Auswahl, als eigentlicher
Test von „beide“. (2, hoch) Kein positives Wachstum verlangt, τ = 20 nicht je Paar als „vor der Festlegung“ belegt.
*Übernommen:* beide Arme müssen wachsen, Paar-Gate „bei t = 25 noch nicht festgelegt“. *Nicht übernommen:* Mindestgröße des
Wachstums (keine begründbare Schwelle). (3, mittel) Überspringen ohne Spektren, (4, mittel) Smoke prüfte ggf. ein altes
Artefakt: beide übernommen und im Fenster geprüft (Smoke [0, 5, 10, 20, 30]; fehlender Schritt → Exit 1; vorhandene → Exit 0).
Commit 73fb530. *Entscheidung:* EXP-036 startet in der Nacht mit Nachträgen a–e. „Gemeinsame Unterstützung“ gilt nur als
gestützt, wenn Test 1 und Test 3 (7/7 bei m = 7) bestehen. Das ist streng; ein *unklar* ist wahrscheinlich und ehrlich.
*Zeitkorrektur:* Die Uhrzeiten dieses Abschnitts stammen aus den Commit-Zeiten (3e1144e 17:31:38, a1c2642 17:34:08, 73fb530
17:40:59); ich hatte zuerst geschätzte, um 1–3 min zu späte Zeiten eingetragen (derselbe Fehler wie in Sitzung 9) und sie korrigiert.

**Zyklus 3 (17:42, ohne Training): Liegt die Festlegung an einer „Lernraten-Uhr“?** Beim Warten nachgerechnet: Mit linearem Warmup
über 200 Schritte ist Σlr(n) = n²/400 (in lr-Einheiten); Σlr = 25 bei n = 100, Σlr = 50 bei n ≈ 141. Das ist genau die schon
vorab in EXP-035 (H35, quantitativ sekundär) festgelegte Erwartung (100, 150] für Seed 30, **keine neue Vorhersage**. Seed 30
trifft sie: t = 100 noch gemischt ([6, 19, 29, 34, 47]), t = 150 = nur F. *Entscheidung:* nichts nachträglich festlegen; das
Urteil fällt nach den Seeds 31, 32 mit der vorab festgelegten Regel (Nachtrag a).

**17:45–17:51 EXP-035 Seed 31 (von Hand im Fenster, dieselben Befehle wie die Queue):** t = 50 mit Warmup → K = [4, 8, 36, 42, 46],
d = −2 (ohne Warmup d(50) = +3); t = 150 → [23, 29, 41, 45, 55], d = +3, identisch mit „nur F“ ohne Warmup. Beschreibend: Auch
Seed 31 legt sich mit Warmup später fest als ohne; t = 100 und „nur F“ mit Warmup fehlen noch (Queue). Kein Urteil.

**Zyklus 4 (17:44–17:53): EXP-039 „Lernraten-Uhr“ neu vorab festgelegt (Code, Smoke, Codex).** Frage: Fällt die Festlegung bei
fester aufsummierter Lernrate Λ ∈ (25, 50], auch wenn die Lernrate gleichmäßig skaliert wird (c = 2 → Fenster (12, 25],
c = 0.5 → (50, 100]) statt per Warmup? Konkurrenz: Schrittuhr (z. B. Adams β2-Horizont von 50 Schritten) → (25, 50] für beide c.
Literatursuche (WebSearch, 17:44): nächstverwandt He et al. 2026 (Frequenz-Lotterie über Init, https://arxiv.org/abs/2602.16849),
Tan et al. 2026 (zwei Uhren im Grokking, https://arxiv.org/abs/2606.05863); die konkrete Frage nicht gefunden (vorläufig; N17).
Code: `freq_ban.py --lr-scale c` (Standard 1.0 = unverändert; Skalierung nur auf F bis Schritt 250), commit 800c4cf.
Codex (`EXP-039-lr-clock/codex_review_2026-09-26.txt`, needs-attention, 3 × hoch): Gitter nicht intervallsicher (übernommen:
t = 12 bzw. 25 ergänzt, exakte Intervalle), ergebnisabhängige Ausschlüsse (übernommen: vollständige Zellen zählen immer,
Einheit = Seed mit beiden Skalierungen), AdamW isoliert Λ nicht (teilweise: Aussage auf AdamW mit diesem Plan beschränkt;
keine Weight-Decay-Kontrolle, weil der entkoppelte Decay bis Λ = 50 nur ≈ 5 % gleichmäßig über alle Frequenzen schrumpft).
Smoke im Fenster ok (17:51), Selbsttest nach den Änderungen ok (17:52). *Ergebnis:* vorbereitet, nicht ausgeführt; in
`queue_s10.sh` nach EXP-036. *Entscheidung:* EXP-036 bleibt vor EXP-039 (offene Hauptfrage aus Sitzung 9).

**Rückblick nach drei Zyklen (Regel §4):** Gelernt: Die Festlegungszeit ist ein messbarer, verschiebbarer Marker (Warmup
verschiebt sie in 2/2 Seeds bisher). Wiederholen wir uns? Nein, EXP-039 ist ein anderer Eingriff (Form des Plans gleich, Höhe
anders). Messung geeignet? Das Top-5-Maß ist oberwellenanfällig; bisher haben alle Auswertungen die Oberwellen gesondert
behandelt. Nächste anzugreifende Annahme: dass „Festlegung“ ein Ereignis im W_E-Spektrum ist. EXP-038 (Teil-Rücksetzen) prüft,
wo sie sitzt.

**Zyklus 5 (17:53–18:01, ohne Training): Warum Λ ≈ 25–50? Neue Hypothese H40 und EXP-040.** Aus gespeicherten EXP-035-Läufen:
‖W_E − W_E,0‖ am Wechsel 2.84 (Seed 30, t = 100, noch offen) bzw. 5.50 (t = 150, festgelegt), Init-Norm 10.5, Init-Amplitude pro
Frequenz im Median 1.40. Grobe Überschlagsrechnung (Codex: unvergleichbare Größen, nur Motivation): das Datensignal erreicht beim
Festlegen etwa die Init-Amplitude. **H40:** Die Wahl fällt, wenn das Datensignal die Init-Amplitude der Konkurrenz einholt. Unter
Adam wächst die Strecke ∝ Λ, deshalb sähe das wie eine Λ-Uhr aus. Test: W_E-Init × s (s = 0.5 → (12, 25], s = 2 → (50, 100]).
Mit EXP-039 zusammen trennt das Optimierer-Uhr, Amplitudenschwelle und Schrittuhr. Code `--we-init-scale` (commit 4ea594f).
Selbsttest/Smoke im Fenster vom Wächter um 17:56 abgelehnt (unter 1 min Rest), nicht umgangen: ungetestet, fail-closed am
Queue-Anfang. Codex (`EXP-040-we-init-scale/codex_review_2026-09-26.txt`, needs-attention, 3 × hoch): Eingriff nicht isoliert
(übernommen: nur Nicht-Gleichanteil der Zahlenzeilen skaliert, Urteil nur „Assoziation“), Überschlag unvergleichbar (übernommen:
nur Motivation; W_E-Schnappschüsse für zielgenaue Strecke), fehlende Paarprüfung der Skalen (übernommen). *Ergebnis:* vorbereitet,
ungetestet. *Entscheidung:* in `queue_s10.sh` nach EXP-039.

**Zyklus 6 (18:01–18:04, ohne Training): Lässt sich H40 an vorhandenen Daten prüfen?** Frage: Gibt es frühe W_E-Checkpoints (vor
Schritt 50)? Die Studie speichert in `training/external/conv100k` Checkpoints bei 0, 140, 500, …, also erst nach der Festlegung;
die EXP-020/035-Läufe nur Spektren alle 250 Schritte. *Ergebnis:* an vorhandenen Daten nicht prüfbar (negativ). *Entscheidung:*
beschreibender Invarianztest vorab festgelegt (EXP-040 Nachtrag b): Ist beim Festlegen über c und s hinweg Λ(hi) oder das
Verhältnis R(hi) (zielgenaue Strecke / Init-Amplitude) weniger variabel? Die nötigen W_E-Schnappschüsse liefern die EXP-039/040-
Läufe (jetzt mit `--spectra-at`). Für EXP-038 macht H40 keine saubere eigene Vorhersage, dort nichts nachgetragen.

**Zyklus 7 (18:04–18:14, ohne Training): Prägung durch einen kurzen Vorlauf, auch gegen einen Zufallssplit? EXP-041.** Frage:
EXP-020 prüfte nur konstruiert → konstruiert. Hält eine 150-Schritte-Prägung durch einen konstruierten Split E, wenn danach normal
auf einem Zufallssplit R trainiert wird (P41a), und prägt ein spektral schwacher Split R genauso fest (R → E, P41b, offen)?
Literatur (18:05): **LeDoux 2026, „The Order Is The Message“ (https://arxiv.org/abs/2603.25047)**: Die *Reihenfolge* der
Minibatches über einer festen Trainingsmenge bestimmt die gelernte Grundfrequenz. Das ist die bisher nächstverwandte Arbeit
zu EXP-016/020/041. Laut HTML-Volltext kein Wechsel mitten im Training, keine Festlegungszeit, keine Lernraten-/Init-Abhängigkeit,
keine Rolle der Mengenzusammensetzung. Unsere Linie bleibt „nicht gefunden (vorläufig)“, muss diese Arbeit aber zitieren.
Codex (`EXP-041-imprint/codex_review_2026-09-26.txt`, needs-attention, 3 × hoch, 1 × mittel), alles übernommen (Nachtrag a):
symmetrisches Maß aus beiden reinen Läufen statt zirkulärer R-Referenz, Spektren am Wechsel und uhrgleiche Kontrolle, Bonferroni
(P41a einseitig, P41b zweiseitig, je 0.025) mit 10 Seeds, Manifest-Lader. *Ergebnis:* vorbereitet, ungetestet, nicht in
`queue_s10.sh` (Kandidat für die nächste Queue). *Selbstkritik:* Mein erster Entwurf hatte ein zirkuläres Maß; ohne Codex
wäre die Asymmetrie-Aussage von P41b ein Messartefakt gewesen.

**Zyklus 8 (18:14–18:16, ohne Training): Anwendungsidee und Zuverlässigkeit der Nacht-Queue.** (a) N20: datengepflanzte Frequenzen
als Prüfstand mit bekannter Wahrheit für Interpretierbarkeitsmethoden. Suche 18:16: InterpBench (https://arxiv.org/abs/2407.14494)
erzwingt Schaltkreise per Hilfsverlust (SIIT), nicht über die Daten; in dieser Form nicht gefunden (vorläufig). Der kleine nächste
Schritt (Neuronen-Analyse an EXP-016) geht nicht: EXP-016 hat keine gespeicherten Modelle (negativ, notiert). (b) `queue_s10.sh`
brach beim ersten Fehler ab; mit vier neuen, erst im Lauf geprüften Codepfaden (EXP-038-, EXP-036-, EXP-039-Smoke, EXP-040-Selbsttest)
hätte ein einziger Fehler die ganze Nacht blockiert. Änderung: `part()` protokolliert einen Fehlschlag und macht mit dem nächsten
Versuch weiter; nur eine Ablehnung durch den Wächter (rc 3) stoppt. *Entscheidung:* übernommen (Zuverlässigkeit, keine
Versuchsänderung).

**Zyklus 9 (18:17, ohne Training, beschreibend/post hoc): Wächst die W_E-Strecke unter Adam proportional zu Λ (Prämisse von H40)?**
Gespeicherte EXP-035-Strecken am Wechsel: ‖ΔW_E‖/Λ = 0.119 → 0.097 für Λ = 0.3 … 57 (Seeds 30, 31 identisch bis auf 1 %),
0.067 bei Λ = 150; alle Parameter 0.44 → 0.34. Obergrenze kohärenter Adam-Schritte lr · √(114 · 128) = 0.121, also ≈ 90 %
Kohärenz früh. EXP-039-Smoke (c = 2, Λ = 60): 0.082. *Ergebnis:* Prämisse im Festlegungsbereich gestützt (Strecke ≈ 0.11 · Λ,
Abweichung ≤ 20 % zwischen Warmup und c = 2). *Entscheidung:* als Vorbehalt in EXP-039 Nachtrag b eingetragen (Regeln unverändert):
Eine Streckenuhr sähe bei c = 2 leicht verspätet aus und ergäbe *unklar*, nicht *Schritt*.

**Zyklus 10 (18:17–18:18, ohne Training): H40 quantitativ.** Mit Strecke ≈ 0.11 · Λ und Init-Amplitude 1.4 fällt die Schwelle bei
Λ* ≈ 28.5/√f (f = Streckenanteil auf den 5 Zielen). Das Fenster (25, 50] verlangt f ≳ 0.3. *Ergebnis:* Zahl-Vorhersage R(hi) ∈ [0.5, 2]
beschreibend festgelegt (EXP-040 Nachtrag c), bevor Schnappschuss-Daten existieren; R(hi) < 0.5 widerlegt H40 in dieser Form.

**Zyklus 11 (18:18, ohne Training, post hoc, Konsistenzprüfung):** Ist f ≳ 0.3 plausibel? Aus den EXP-020-Läufen „nur F“ (Seeds 30–34)
mit der Näherung |Δc_k|² ≈ P_k(t) − P_k(0) (Bewegung ≈ senkrecht zur Init in hoher Dimension): bei Schritt 250 f = 0.51, 0.66, 0.34,
0.40, 0.51 und R ≈ 2.4–2.7; bei Schritt 500 f = 0.43–1.0, R ≈ 2.5–2.9. *Ergebnis:* f ≳ 0.3 in 5/5 plausibel; die Zielamplitude sättigt
ab Schritt ≈ 250 bei etwa dem 2.5-Fachen der Init-Amplitude. H40 sagt beim Festlegen R ≈ 1, also ~40 % dieser Sättigung. Nur
Konsistenz (Schritt 250 liegt nach der Festlegung, Näherung statt Schnappschüssen), kein Test. *Entscheidung:* keine Änderung an
den Vorhersagen; die echten Schnappschüsse kommen mit EXP-036/039/040.

**Zyklus 12 (18:18–18:20, ohne Training, post hoc): Endzustände als diskrete Attraktoren?** Katalog aller Endzustände (Top-5 W_E)
je Seed über EXP-020, EXP-035 und EXP-037 (Seeds 30–34, 58 Läufe): Seed 30: 18 Läufe, 9 verschiedene Zustände; Seed 31: 13 → 7;
Seed 32: 11 → 7; Seed 33: 8 → 4; Seed 34: 8 → 5. Neben „nur F“ (festgelegt) und „nur G“ wiederholen sich **Mischzustände exakt über
verschiedene Eingriffe**: Seed 30 (6, 19, 29, 34, 47) = Warmup t = 100 = EXP-037 A = 25; Seed 31 (4, 8, 36, 42, 46) = ohne Warmup
t = 10 = Warmup t = 50 (Λ 10 bzw. 6.4). Seed 30: Λ-gleiche Paare überlappen im Mittel 3.0/5, schrittgleiche 2.3/5.
*Deutung (Spekulation):* Je Seed gibt es wenige diskrete Endzustände, und welcher erreicht wird, hängt eher an Λ beim Wechsel als an
der Schrittzahl. *Entscheidung:* P35d für Seed 32 (noch ohne Warmup-Läufe) vorab festgelegt (EXP-035 Nachtrag c, `state_match.py`,
in der Queue). Idee für später: Attraktor-Katalog als eigene Messgröße (N21).

**Zyklus 13 (18:26): Codex greift Zyklus 12 an** (`EXP-035-warmup-lockin/codex_conclusion_review_2026-09-26.txt`, needs-attention).
Einwände: keine Zufalls-Null für Top-5-Kollisionen bei eingeschränktem Vorrat, Verdichtung vor allem durch die Plateaus, Paarsuche
post hoc; P35d vergleicht verschiedene Läufe und wird von jeder Warmup-Verzögerung erfüllt; `state_match.py` nicht fail-closed.
*Übernommen, alles:* P35d **zurückgezogen** (vor jedem Seed-32-Lauf), `state_match.py` aus der Queue, N21 und die Deutung von
Zyklus 12 auf „unkalibrierte Top-5-Kollision“ zurückgestuft. Die Zahlen aus Zyklus 12 bleiben stehen, die Wörter „diskret“ und
„Attraktor“ gelten als nicht gezeigt. Codex zählt bei Seed 30 acht statt neun Mengen; meine Zählung nimmt „nur F“ bei Schritt 2000
aus den Spektren, was die Warmup-Variante von „nur F“ als eigene Menge zählt. Lehre: Eine Beobachtung aus einer Katalog-Suche
ist noch kein Vorhersagetest; ein schief gebauter Vergleich hätte eine falsche Bestätigung liefern können.

**Zyklus 14 (18:27, ohne Training): Warum ist die Festlegung unumkehrbar?** Überlegung: Jede Frequenzmenge löst die ganze Aufgabe; der
Split neigt die Wahl nur. Nach dem Wechsel lernt das Netz G mit den vorhandenen F-Frequenzen. **H42** (N22): Festlegung, sobald der
F-Vorsprung die pro Schritt wirkende G-Neigung überwiegt. Prüfbare Folgerungen: spätere Festlegung bei stärker konzentriertem G;
P41b eher *überschrieben* (als Erwartung in EXP-041 notiert, Regeln unverändert). Testskizze (eps-Variation) in N22, nicht festgelegt,
weil die Queue voll ist. *Ergebnis:* neue Hypothese mit zwei Vorhersagen, keine Daten.

**Zyklus 15 (18:28–18:31, ohne Training): H42 prüfbar machen, EXP-042.** Frage: Hängt der Festlegungszeitpunkt an der Neigung des
neuen Splits? G-Splits mit eps 8 und 1 aus demselben Zufallsstrom wie EXP-020 (reine Rechnung; F und Testmenge fail-closed als
bitgleich geprüft, G bei eps 2 reproduziert exakt). Zielanteil M0(G): 0.115 (eps 1), 0.18 (eps 2), 0.36 (eps 8), in allen 4 Seeds
gleich. Vorab festgelegt (EXP-042-README, primär eps 8, Zelle *später* bei lo ≥ 50). *Ergebnis:* vorbereitet, ungetestet, in
keiner Queue. Eigene Fehler: wieder Backticks in einem ungeschützten Heredoc (ein Wort im README fehlte, repariert, keine
Wirkung); Betragsstriche |K ∩ F| in Tabellenzellen zerlegen Obsidian-Tabellen, in EXP-036/039/041/042 maskiert.

**Codex zu EXP-042 (18:38, `EXP-042-bias-strength/codex_review_2026-09-26.txt`, needs-attention):** *später* trennt H42 nicht von
stärkerer Verdrängung (Überlappung sinkt mit eps) → Urteil auf „Zeitpunkt hängt vom zweiten Split ab“ eingeengt; alte Referenzläufe →
eigene „nur F“-Läufe; Gleichstand → „keine Verschiebung bei dieser Auflösung“; fehlende Job-Sperre → Warteschleife. Nicht übernommen:
faktorielles Design (erst bei *später*).

### Abschlussbericht Sitzung 10 (2026-09-26, 17:29–~20:20 Berlin; geschrieben 18:39, wird am Ende ergänzt)

**Wichtigste Befunde (alle ohne neue Trainingsläufe außer EXP-035, beschreibend oder post hoc):**
1. **[[experiments/EXP-035-warmup-lockin/README|EXP-035]]:** Seed 30 vollständig, Seed 31 teilweise. Mit Warmup legt sich die
   Frequenzwahl später fest (Seed 30: (100, 150] statt (25, 50]; Seed 31 bei t = 50 noch G-seitig). Für Seed 30 trifft das die
   vorab genannte Λ-Erwartung. Kein Urteil (Regel: 3 Seeds).
2. **Adam-Strecke ∝ Λ:** ‖ΔW_E‖ ≈ 0.11 · Λ bis Λ ≈ 60 (≈ 90 % kohärente Schritte), danach sublinear (Zyklus 9).
3. **Unkalibrierte Beobachtung:** exakt gleiche Mischzustände über verschiedene Eingriffe (Zyklus 12). Nach Codex zurückgestuft:
   kein Attraktor- oder Λ-Beleg, P35d zurückgezogen.
4. **Literatur:** nächstverwandt LeDoux 2026 (Datenreihenfolge bestimmt die Frequenz, https://arxiv.org/abs/2603.25047) und He et al.
   2026 (Frequenz-Lotterie über die Init, https://arxiv.org/abs/2602.16849); beide ohne Datenwechsel, Festlegungszeit oder Lernraten-
   bzw. Init-Skala. Unsere Fragen N17–N22: nach unserer Suche vom 2026-09-26 nicht gefunden.

**Vorbereitet, nicht ausgeführt (alle mit Codex-Review, Nachträge vor jedem Lauf):** EXP-036 Nachträge d/e (kalibriertes P36b mit
frühen Spektren, Smoke im Fenster ok), [[experiments/EXP-039-lr-clock/README|EXP-039]] (Lernraten-Uhr, Smoke ok),
[[experiments/EXP-040-we-init-scale/README|EXP-040]] (Init-Skala, H40, ungetestet), [[experiments/EXP-041-imprint/README|EXP-041]]
(Prägung E ↔ R, ungetestet), [[experiments/EXP-042-bias-strength/README|EXP-042]] (Split-Neigung, H42, ungetestet). Neue `freq_ban.py`-Optionen: `--spectra-at` (mit W_E-Schnappschüssen), `--lr-scale`, `--we-init-scale` (Standard jeweils unverändert).

**Offene Grenzen:** Die Sitzung hat viel vorbereitet und wenig gemessen (Fenster nur 30 min). Alle Transformer-Befunde an einer
Architektur. Vier neue Codepfade werden erst in der Nacht durch Smokes/Selbsttests geprüft.
**Codex:** fünf Reviews (EXP-036 d, EXP-039, EXP-040, EXP-041, EXP-042) und ein Schlussfolgerungs-Review (Zyklus 12), alle
needs-attention; fast alle Einwände übernommen, Ausnahmen mit Grund in den READMEs.
**Eigene Fehler:** geschätzte statt gemessene Uhrzeiten (korrigiert, jetzt immer gemessen); zweimal falsche Selbsttest-Erwartungen;
Backticks in ungeschütztem Heredoc (repariert); Betragsstriche in Obsidian-Tabellen (maskiert); ein überzogener Post-hoc-Befund
(von Codex zerlegt, zurückgestuft).
**Nächste Aktion:** Im Fenster ab 00:00: `python lab/tools/guarded_run.py --check`, keine Queue aktiv, dann
`sh lab/experiments/queue_s10.sh` im Hintergrund (Log z. B. `lab/runner/logs/queue_s10.log`); danach Log nach „failed“ durchsuchen.
*Nachtrag zum Bericht:* Beim Schreiben dieses Berichts ist derselbe Heredoc-Fehler ein drittes Mal passiert (vier Optionsnamen
fehlten, sofort repariert). Ab jetzt nur noch geschützte Heredocs (`<<'EOF'`) oder Python für Texte mit Backticks.

**Zyklus 16 (18:40, ohne Training): Neuheit des Kernbefunds nachgeprüft.** Zwei gezielte Suchen (arXiv/OpenReview, 2026). Neu gesehen:
arXiv 2609.17571 (Sept. 2026, wo das Grokking stattfindet), 2606.12966, 2605.18845; laut Abstracts keine Festlegungszeit der
Frequenzwahl per Datenwechsel. *Ergebnis:* Einordnung „nicht gefunden (vorläufig)“ bleibt (N14-Nachtrag). Grenze: nur Abstracts.

**Zyklus 17 (18:47, ohne Training): Codex prüft `freq_ban.py` (alle neuen Optionen)** (`EXP-001-freq-ban/codex_review_freqban_s10_2026-09-26.txt`,
needs-attention, 3 × hoch, 1 × mittel). Übernommen: Überspringen verlangt jetzt auch vollständige W_E-Schnappschüsse (Schritt 0 +
angeforderte) und gleiche Skalen-Metadaten wie angefordert; alte Schnappschuss-Dateien werden bei jedem Laufstart gelöscht;
NaN/inf-Skalen abgelehnt; `--lr-scale` mit `--alternate-every` abgelehnt (der Skalenfaktor hätte sonst auch G-Blöcke getroffen).
Nicht übernommen: transaktionale Schreibvorgänge mit Generationen (Aufwand; `--force` wird nur in Smokes nach `rm -rf` benutzt) und
injektive Kodierung beliebiger Fließkomma-Skalen (die Queues benutzen nur 0.5, 2, 8). Statisch gegengelesen: Für alte Läufe ohne die
neuen Felder liefert der Überspringen-Zweig wie bisher Exit 0. **Ungetestet** bis zur Nacht (der Überspringen-Zweig läuft zuerst bei
EXP-035 Seed 30; scheitert er, macht `queue_s10.sh` mit EXP-038 weiter).

**Zyklus 18 (18:48, ohne Training): Was genau widerlegt EXP-040?** Unter Adam (lineares Wachstum, gemessen) sagt die Schwellenidee
Zeit ∝ s voraus, unter Gradientenfluss (exponentielles Wachstum) nur ∝ log(1/s). *Ergebnis:* Einordnung in EXP-040 ergänzt: *unverändert*
widerlegt nur die lineare Fassung von H40, nicht jede Schwellenidee. Regeln unverändert.

**Zyklus 19 (18:49, ohne Training): Google Scholar direkt.** Ein Treffer (Liu et al. 2026, Spectral Lens), im Volltext ohne Datenwechsel
oder Festlegungszeit; der Abruf-Zusammenfasser hatte einen Bezug behauptet, den der Text nicht hat. *Lehre:* Werkzeug-Zusammenfassungen
von Suchtreffern immer am Volltext prüfen. N14 unverändert.

**18:49: Werkzeug `lab/tools/night_report.py`** (nur lesend): fasst ein Queue-Log und die Urteile aller `summary*.json` zusammen, damit
die Folgesitzungen die Nacht-Ergebnisse in einem Aufruf sehen. Am `queue_s9.log` geprüft (liest korrekt: 29 EXP-020-/3 EXP-018-Läufe,
eine Wächter-Ablehnung um 17:36).

**18:50: EXP-035 um Seed 34 erweitert** (Nachtrag e; vom Design erlaubt; macht das Urteil strenger, nicht leichter; +≈ 35 min).

**Zyklus 20 (18:51, ohne Training, post hoc aus gespeicherten EXP-020-Spektren): Was macht das G-Training nach der Festlegung?**
Wechsel bei t = 150 gegen „nur F“, mittlere Leistung der 5 F-Ziele / 5 G-Ziele (Init-Mittel ≈ 2.0), Seeds 30–34:
F-Ziele wachsen unter G weiter wie unter F (Schritt 250: 17.0/15.4, 17.1/16.2, 16.2/14.4, 17.0/15.2, 18.0/16.8; Schritt 2000:
25.6/24.6, 25.7/23.6, 25.6/27.8, 22.8/29.1, 29.3/32.0). G-Ziele **schrumpfen trotz G-Daten** wie im reinen F-Lauf (Schritt 250 → 2000:
3.19 → 0.30 gegen 3.53 → 0.40; ähnlich in allen 5 Seeds), im Wechsellauf zu fast allen Zeitpunkten sogar etwas tiefer als ohne
Wechsel. *Ergebnis:* Nach der Festlegung fördert G seine eigenen Zielfrequenzen sichtbar nicht (5/5); das Netz lernt die neue
Stichprobe mit den vorhandenen F-Frequenzen (Prämisse von H42/N22 gestützt, beschreibend).
**Wichtige Einschränkung, die ich bisher nicht beachtet hatte:** F und G teilen sich 2745–2795 von 3831 Trainingspaaren (≈ 73 %); der
„Datenwechsel“ in EXP-020/035/037/039/040 tauscht also nur ≈ 27 % der Paare. Die Festlegung ist damit bisher nur gegen einen
**teilweisen** Wechsel gezeigt. In EXP-041 teilen E und R nur ≈ 37 % (Zufallsniveau 3831/10215), dort werden ≈ 63 % getauscht:
EXP-041 P41a ist damit der härtere Test der Festlegung (als Einordnung in EXP-041 notiert, Regeln unverändert). EXP-042 eps 8 senkt
die Überlappung auf ≈ 57 %.

**18:51: Queue-Reihenfolge geändert** (EXP-041 nach EXP-038, vor EXP-036/039/040), BACKLOG EXP-041 → P1. Grund: Zyklus 20.

**Zyklus 21 (18:53, ohne Training): Vorab-Lesart der Ergebniskombinationen** in [[BEFUND-festlegung]] festgelegt (EXP-041 × EXP-039 ×
EXP-040 × EXP-042), bevor einer dieser Versuche läuft. Zweck: keine nachträgliche Gesamtdeutung. Neue Befundnotiz [[BEFUND-festlegung]]
fasst die Festlegungs-Linie (Sitzungen 7–10) mit Einschränkungen zusammen.

**Zyklus 22 (18:53, ohne Training, post hoc): Auffälligkeit.** Mittlere Leistung der G-Ziele im Wechsellauf (t = 150) gegen „nur F“,
Schritte 250–2000 (8 Zeitpunkte × 5 Seeds): **niedriger in 39/40**, höher in 1/40. Training auf G drückt die G-Zielfrequenzen nach
der Festlegung also *stärker* als Training auf F. Kontraintuitiv, weil G die G-Struktur stärker enthält. Nicht unabhängige
Zeitpunkte, post hoc, keine Erklärung geprüft. Spekulation: Beim Anpassen der ≈ 27 % neuen G-Paare mit den F-Frequenzen wachsen
diese schneller (F-Leistung im Wechsellauf früh höher, Zyklus 20), und Weight Decay plus Konkurrenz um Norm drücken ungenutzte
Frequenzen stärker. *Entscheidung:* als Auffälligkeit notiert (N22); prüfbar in EXP-041/042 mit den vorhandenen Spektren, kein
eigener Versuch.

**Zyklus 23 (18:54, ohne Training, post hoc): Hält die Auffälligkeit aus Zyklus 22 an anderen Wechselzeitpunkten?** G-Ziele im
Wechsellauf niedriger als in „nur F“ (alle gespeicherten Zeitpunkte nach dem Wechsel, Seeds 30–34): t = 400: 33 von 40; t = 1000:
25 von 35; EXP-037 C_F100: 24 von 24 (also mit abnehmender Deutlichkeit bei späterem Wechsel). Der „F-Schub“ dagegen **nicht**:
F-Ziele im Wechsellauf höher nur in 13/40, 14/35, 10/24. *Ergebnis:* Die G-Unterdrückung unter G-Training ist über Wechselzeitpunkte
hinweg wiederkehrend (beschreibend, Zeitpunkte nicht unabhängig); meine Erklärung aus Zyklus 22 (schnelleres F-Wachstum drückt G)
wird **nicht** gestützt und ist verworfen. Offene Frage (N22): Warum drückt Training auf G die G-Zielfrequenzen stärker als Training
auf F? Keine Erklärung geprüft.

**18:55: Erklärungskandidat „Adam-Verdrängung“** für die G-Unterdrückung (N22): Prämisse geprüft, der Verlust springt beim Wechsel
(Seed 30: 0.04 → 1.65; Seed 31: 0.02 → 1.23) und fällt in ≈ 20 Schritten. Vorhersagen notiert (SGD in der G-Phase → keine zusätzliche
Unterdrückung). Nicht festgelegt, kein Lauf.

**Zyklus 24 (18:56, ohne Training): Literatur zur „Adam-Verdrängung“.** Allgemeiner Mechanismus bekannt (https://arxiv.org/abs/2608.15824):
große Gradienten bleiben im zweiten Moment und dämpfen spätere Updates. Einordnung: Erklärungskandidat = Anwendung eines bekannten
Effekts (#neu/bekannt), die Beobachtung (G-Unterdrückung nach Datenwechsel) bleibt beschreibend und ungeklärt.

**Zyklus 25 (19:00): Codex prüft [[BEFUND-festlegung]]** (`lab/codex_befund_festlegung_review_2026-09-26.txt`, needs-attention, 2 × hoch,
2 × mittel). Alle übernommen: (1) EXP-033 hatte ich zu stark gelesen („zustandsbestimmt“ ist dort selbst eingeschränkt: nur „AdamW in
Phase 1 nicht nötig“); (2) Lesart für EXP-041 auf dessen Urteilskategorien zurückgeführt (*nicht gezeigt* ≠ „kippt“), Uhr-Aussagen
bleiben in jedem Fall auf den Teilwechsel beschränkt; (3) EXP-020-Kern präzisiert: d wird in (25, 50] positiv, die Endzustände sind
dort noch gemischt, exakt „nur F“ erst ab t = 150 (auch in der Lage von [[LAB]] korrigiert); (4) EXP-042 *später* belegt H42 nicht.
Lehre: Eine Synthese ist die Stelle, an der sich Überaussagen einschleichen; sie braucht dieselbe Prüfung wie ein Versuch.

**Ergänzung zum Abschlussbericht Sitzung 10 (19:00):**
- **Wichtigste neue Einsicht nach dem Entwurf:** F und G teilen ≈ 73 % der Trainingspaare; die Festlegung ist nur gegen einen
  Teilwechsel gezeigt. EXP-041 (≈ 63 % neue Paare) ist deshalb in der Queue nach vorn gerückt (nach EXP-038). Außerdem: Nach der
  Festlegung drückt G-Training die G-Zielfrequenzen stärker als fortgesetztes F-Training (39/40, 33/40, 25/35, 24/24; ungeklärt;
  Erklärungskandidat „Adam-Verdrängung“ ist ein bekannter allgemeiner Effekt, ungeprüft).
- **Neu vorbereitet:** EXP-042 (Split-Neigung; Splits erzeugt). **Neue Notiz:** [[BEFUND-festlegung]] mit vorab festgelegter Lesart
  der Ergebniskombinationen (nach Codex korrigiert). **Werkzeug:** `lab/tools/night_report.py`.
- **`freq_ban.py` nach Codex gehärtet** (9fa4b7a). Alle neuen Pfade werden nachts zuerst durch Smokes/Selbsttests geprüft.
- **Queue `queue_s10.sh`:** EXP-035 (Seeds 30, 31, 32, 34) → EXP-038 → EXP-041 → EXP-036 → EXP-039 → EXP-040 → EXP-034 → EXP-042 →
  queue_s5; ein Fehlschlag überspringt nur den betroffenen Versuch, rc 3 stoppt.
- **Codex insgesamt:** 9 Reviews (EXP-036 d, EXP-039, EXP-040, EXP-041, EXP-042, `freq_ban.py`, Schlussfolgerungen Zyklus 12,
  Befundnotiz), alle needs-attention; übernommen bzw. mit Grund abgelehnt, siehe Zyklen.
- **Scheduler:** Aufgabe `GROKVERSE-Lab-Runner` aktiv; nächster Start laut `runner-state.json` 2026-09-26T20:29:44.7949635Z = **2026-09-26 22:29 Berlin**
  (außerhalb des Fensters bis 00:00; die Sitzung soll um 00:00 `queue_s10.sh` starten).

**Zyklus 26 (19:01, ohne Training, post hoc): Hängt die G-Unterdrückung am Verlustsprung beim Wechsel (Vorhersage der Adam-Verdrängung)?**
EXP-020, Seeds 30–34 × Wechsel t ∈ {150, 400, 1000}: Trainingsverlust am Wechselschritt (auf G) gegen mittleres log(G-Ziele Wechsellauf /
G-Ziele „nur F“) über die 1000 Schritte danach. Spearman ρ = −0.67, einseitiges Permutations-p = 0.0035 (15 Punkte). Beispiele: Verlust
≈ 0 (Seeds 30, 31, 34 bei t = 1000, schon generalisiert) → keine Unterdrückung (log-Verhältnis +0.08, +0.06, −0.01); Verlust 3.2–3.3
(Seeds 32, 33 bei t = 150) → −0.18, −0.29. *Ergebnis:* richtungsgleich mit der Vorhersage, aber **stark konfundiert**: Der Verlustsprung
hängt am Trainingsstadium (generalisierte Netze bei t = 1000 sind in einer anderen Phase), die 15 Punkte sind nicht unabhängig (je Seed 3),
post hoc. Kein Beleg für den Mechanismus. *Entscheidung:* notiert; ein sauberer Test bräuchte SGD in der G-Phase bei gleichem Stadium.

*Nachtrag Zyklus 26 (19:01):* innerhalb gleichen Wechselzeitpunkts (Stadiums-Confound ausgeschaltet, je n = 5): t = 150 ρ = −0.3,
t = 400 ρ = −0.7 (Spearman, von Hand aus den Tabellenwerten). Richtung gleich, schwach, n klein. Einordnung unverändert: Hinweis, kein Beleg.

---

## Sitzung 11 (2026-09-26, 19:10–22:09 Berlin, außerhalb des Fensters; nur Code, Vorbereitung, Denkarbeit)

Neue Nutzerregeln 15 (Synthese, ≥ 10 Seeds, Verallgemeinerung zuerst) und 16 (GPU) gelesen. Kein Training läuft (19:12: nur
zwei `torch.cuda`-Abfragen des Nutzers).

**Zyklus 1 (19:13): Synthese.** Frage: Was sind nach 42 Versuchen die tragenden Aussagen? *Ergebnis:* [[FINDINGS]] mit sechs
Kernaussagen (K1 M0 sagt K voraus; K2 Steuerung über Splits; K3 erster Gradient; K4 frühe Festlegung; K5 AdamW in Phase 1 nicht
nötig; K6 Aktivierung), Belegen, Literatur und der größten offenen Frage: Gilt K2/K4 außerhalb von Addition mod 113?
*Entscheidung:* Neue Arbeit zielt zuerst auf diese Frage (Regel 15c).

**Zyklus 2 (19:16): GPU vorbereiten (Regel 16a).** `freq_ban.py --device` (Init auf der CPU wie bisher, dann `.to(dev)`;
Daten, Projektoren, Rückwege nach numpy mit `.cpu()`; Run-ID-Suffix `_devcuda`; `device`, `device_name`, `cuda_max_mem_mb` in
`result.json`), dazu `--p`/`--task` für EXP-043 (nur mit `--split-file` und `baseline`). Nur `py_compile` geprüft (Fenster zu).
Prüfung [[experiments/GPU-001-equivalence/README|GPU-001]] mit vorab festgelegten Kriterien: (1) CPU-Regression gegen den
gespeicherten EXP-016-Smoke, exakt; (2) GPU-Wiederholung der gespeicherten CPU-Läufe EXP-016 Seeds 10–12 (A1 Top-5 bei 2000
≥ 4/5 je Seed, A2 ≥ 8/9 frühe Vergleiche, A3 gleicher Grokking-Ausgang ± max(100, 15 %)); (3) Durchsatz J = 1/2/4/8.
**Fund beim Planen:** Die Warteschleifen in `queue_s10.sh`, `queue_s5.sh`, EXP-041 und EXP-042 warten auf *jeden*
`guarded_run`-Prozess; parallele GPU-Läufe hätten die CPU-Queue blockiert. Geändert auf „ignoriere Prozesse mit `--device cuda`“
(`ps -ef` zeigt die Argumente, geprüft mit einem Schlafprozess; Filterlogik an Beispielzeilen geprüft). Commit c2c0b91.

**Zyklus 3 (19:19): Verallgemeinerung vorab festgelegt.** Frage: Gibt ein konstruierter Split auch bei Addition mod 97 und bei
Multiplikation mod 113 (Log-Basis, Z_112, g = 3) die gelernten Frequenzen vor? [[experiments/EXP-043-generalize-steering/README|EXP-043]]:
EXP-016-Design (Arme F/G, Δ, Vorzeichentest), 10 Seeds je Aufgabe (70–79), Holm über zwei Aufgaben, GPU, K aus W_E-Schnappschüssen
in der Gruppenbasis. Splits erzeugt (reine Rechnung): Zielmenge = M0-Top-5 in 40/40 Fällen, Anteil 0.18–0.21. Literatur (N23):
„Discrete-Log Clock“ (arXiv 2606.17399) findet je Seed verschiedene Schlüsselfrequenzen, auch nicht-teilerfremde (2, 8, 56), und
fragt nicht nach der Ursache; deshalb Ziele aus allen k = 1..55 statt nur teilerfremden (Entscheidung vor jedem Lauf). Commit af1dac5.
*Korrektur (19:24, gemessen mit `guarded_run.py --check`):* Die Uhrzeiten der Zyklen 1–3 und in LIVE/STATE/READMEs waren **geschätzt**
und lagen in der Zukunft (bis „20:30“). Ersetzt durch die Commit-Zeiten (c2c0b91 19:16, af1dac5 19:19, 843d1c1 19:22). Das ist derselbe
Fehler wie in Sitzung 10. Ab jetzt gilt: vor jedem Zeitstempel die Uhr messen.

**Zyklus 4 (19:22): K4-Verallgemeinerung vorab festgelegt**, bedingt auf EXP-043: [[experiments/EXP-044-generalize-lockin/README|EXP-044]].
F und G werden **unabhängig** gezogen (Überlappung gemessen 37–39 % statt 73 % in EXP-020), Wechsel bei t ∈ {25, 50, 150}, gleiches
G-Budget, 10 Seeds (80–89) je Aufgabe, primär d(150) mit Vorzeichentest. Die Queue startet nur Aufgaben, die in EXP-043 *steuerbar*
sind. Splits erzeugt (Zielmenge = M0-Top-5 in 40/40). `freq_ban.py`: Wechselläufe der neuen Aufgaben heißen EXP-044.

**Zyklus 5 (19:25, ohne Training): Ist Multiplikation hier überhaupt eine andere Aufgabe?** Frage: Was genau prüft der mul-Arm von
EXP-043? Überlegung: W_E und W_U sind Nachschlagetabellen mit iid-Init, deren Verteilung unter Umbenennung der Token invariant ist;
mit a ↦ log_g a (Eingabe und Ausgabe) wird mul mod 113 auf den 112² Paaren ohne Null exakt zu add mod 112. *Ergebnis:* Der mul-Arm
prüft einen zusammengesetzten Modulus (112, nicht treue Frequenzen) plus 225 Null-Paare, keine andere Rechenart. Vor jedem Lauf im
EXP-043-README und in [[FINDINGS]] vermerkt; Urteilsregeln unverändert. Folgerung für Regel 15c: Aufgaben, die nach Umbenennung
der Token eine zyklische Gruppe sind (Subtraktion, Multiplikation, x + y + const.), sind für dieses Modell *kein* neuer Test; eine echte
Aufgaben-Verallgemeinerung braucht eine nicht zyklische Struktur (nicht-abelsche Gruppe) oder eine nicht-modulare Aufgabe.
(Methodische Einsicht; die Universalitätsarbeit von Chughtai et al. 2023 nutzt dieselbe Darstellungstheorie, also vermutlich bekannt.)

**Zyklus 6 (19:26): Architektur-Verallgemeinerung vorab festgelegt.** [[experiments/EXP-045-mlp-steering/README|EXP-045]]: EXP-016-
Design im Studien-MLP mit gemeinsamem Embedding (kein Attention-Wertepfad), add 113, Seeds 90–99, 10 000 Schritte (Studien-MLP
generalisiert im Median bei 9 250), K bei 10 000 primär, bei 2000 sekundär. `freq_ban.py --arch mlp` (nur mit `--split-file`,
`baseline`). Splits erzeugt (M0-Top-5 = Ziele in 20/20). GPU-Sammelqueue `queue_gpu_s11.sh` (GPU-001 → 043 → 044 → 045) geschrieben;
J wird aus dem Durchsatztest gewählt.

---

## Sitzung 12 (2026-09-26, 19:29–22:29 Berlin, außerhalb des Fensters; nur Code, Vorbereitung, Denkarbeit)

Stand gelesen (19:30): kein STOP, kein Training aktiv, Fenster zu (wieder ab 00:00; nächster Runner-Start 00:29 Berlin).
Die Codex-Prüfung von EXP-043/GPU aus Sitzung 11 (`codex_review_2026-09-26.txt`) war **ohne Ergebnis abgebrochen** (nur
Fortschrittszeilen, kein Befund). 19:35 neu gestartet (`codex_review_s12_2026-09-26.txt`), Umfang: `freq_ban.py`-Änderungen seit
a91ef0d, GPU-001, EXP-043/044/045, `queue_gpu_s11.sh`.

**Zyklus 1 (19:31–19:40, ohne Training): Echte Aufgaben-Verallgemeinerung vorbereiten.** Frage: Gilt K2 (Steuerung über den Split)
bei einer nicht-abelschen Gruppe? Begründung: Nach Sitzung 11, Zyklus 5, sind mul/andere Moduli für das Modell wieder zyklisch.
*Änderung:* [[experiments/EXP-046-dihedral-steering/README|EXP-046]] (D₅₉, Ordnung 118, 29 zweidimensionale Irreps; EXP-016-Design
mit Armen F/G, Seeds 140–149, 2000 Schritte, GPU) mit vorab festgelegter Strukturprüfung (sonst *nicht auswertbar*), eigenes
schlankes Trainingsskript `group_train.py` (gleiches Modell/Preset, keine weitere Option in `freq_ban.py`), nicht-abelsches M0.
*Ergebnis (reine Rechnung):* Gruppentafel, Homomorphie aller 29 ρ_k, Assoziativität und Orthonormalität geprüft (fail-closed im
Code); Zielmenge = M0-Top-5 in **20/20** Splits, Zielanteil 0.246–0.280 (gleichverteilt 0.172). Training, Selbsttest und Smoke
**ungetestet** (Fenster). Literatur: N24 (nicht gefunden, vorläufig; nächstverwandt Marchetti et al. 2026, He et al. 2026, Chughtai 2023).
*Entscheidung:* nach der Codex-Prüfung in die GPU-Queue nach EXP-043 einhängen.

**Zyklus 2 (19:45–19:58): Codex prüft den Nachtcode (GPU-001, EXP-043/044/045, Hauptqueue).** Frage: Kann der ungetestete
Nachtlauf still falsche Ergebnisse liefern oder Prüfungen umgehen? *Codex* (`codex_review_s12_2026-09-26.txt`): **2 Blocker** –
(1) die Queues scheitern „offen“: `job()` wandelt jeden Fehler (auch Wächter-Ablehnung rc 3) in Erfolg, die Hauptqueue reagiert
nur auf rc 3 von ganzen Teilqueues, Auswertungsfehler sind nur ein `echo`; (2) GPU-001 umgehbar: Durchsatz gilt schon mit einem
fertigen Lauf, die Hauptqueue prüft beim Wiederanlauf nur die Existenz von `verdict_throughput.json`, und `--force` ließ einen alten
`result.json` stehen. **Hoch:** EXP-044 rechnete Holm nur über auswertbare Aufgaben, vorab festgelegt war „alle gelaufenen“.
**Mittel:** Auswertungen stürzen bei Läufen ohne `result.json` ab; EXP-044 prüft den gemeinsamen Test-Hash nicht. **Niedrig:**
GPU-001-Diagnose nennt Indizes statt Schritte; `config.device` bleibt „cpu“; Seeds 70/99 schon früher benutzt. Geprüft und
**für gut befunden**: kein stiller CPU-Rückfall, Log-Koordinaten für mul, Fourier-Normierung/Parseval, Split-Größen, Wechsel-Timing,
Δ-Test, alle Läufe über `guarded_run.py`, CPU-Standardpfad numerisch unverändert.
*Selbst geprüft und übernommen:* alle Blocker/Hoch/Mittel und die Diagnose (commit 2b19820, Nachträge in den vier READMEs).
*Abgelehnt mit Grund:* `config.device` (alle Auswertungen lesen das Feld `device` oben; eine Änderung von `Config` würde den
Standardpfad berühren), Seeds 70/99 (anderes p bzw. andere Architektur → andere Init; als Einschränkung notiert).
*Lehre:* Mein eigenes „|| echo failed; return 0“-Muster, damit ein Fehler nicht die ganze Nacht stoppt, hat die Fehler unsichtbar
gemacht. Jetzt: weiterlaufen, aber zählen und am Ende mit rc 1 melden. Die Codex-Prüfung aus Sitzung 11 war ohne Ergebnis
abgebrochen (Sitzungsende); ohne diese Wiederholung wären beide Blocker heute Nacht gelaufen.

**Zyklus 3 (20:02–20:18, ohne Training, reine Rechnung): Alternativerklärung zu K2 — steuern die Token-Häufigkeiten?** Frage (beim
Selbstprüfen von EXP-046): Heben die konstruierten Splits die Ziele auch im Spektrum der bloßen Token-Häufigkeiten hervor?
*Ergebnis:* Ja. EXP-016-Splits (Seeds 10–19, F und G): mittlerer Zielrang im DFT-Spektrum der a/b/c-Häufigkeiten 14.5 von 56
(Zufall 27.5), bei gleicher Gesamtungleichheit wie Zufallssplits (CV 0.14 gegen 0.14); D₅₉-Splits: 7.8 von 29 (Zufall 14). Die
Alternativerklärung „das Netz folgt den Häufigkeiten“ war für K2 nie ausgeschlossen (EXP-015 prüfte sie nur post hoc an
Zufallssplits). Gegenprobe offline: b-Werte über die Paare mischen (Duplikate reparieren) hält die a- und b-Häufigkeiten exakt, der
Häufigkeits-Zielrang bleibt 12.2, aber der M0-Zielrang fällt von 2.0 auf 24.5 (Zufall 27.5), M0-Zielanteil 0.192 → 0.091 (Zufall 0.089);
die c-Häufigkeiten sind in beiden Armen nicht zielverzerrt (28.1 / 27.4). Saubere Trennung der beiden Erklärungen.
*Entscheidung:* [[experiments/EXP-047-marginal-control/README|EXP-047]] vorab festgelegt (10 Seeds 150–159 × {eng, shuf} × {F, G},
GPU, H47a Häufigkeiten / H47b Paarstruktur, Holm über beide), Splits erzeugt, in `queue_gpu_s11.sh` nach EXP-046. Nebenbefund:
In EXP-016/043 ist der Paar-Zufallsstrom von Seed s derselbe wie der Zielmengen-Strom von Seed s + 1 (seed + Salz + 1); praktisch
harmlos (verschiedene Verwendung), in EXP-047 mit `SeedSequence` vermieden. Kein Eingriff in laufende/festgelegte Versuche.

**Rückblick nach drei Zyklen (20:22, Auftrag §4).** *Gelernt:* (1) Der Nachtcode hätte Fehler verschluckt und GPU-001 umgehen können
(behoben); (2) K2 hat eine offene Alternativerklärung (Häufigkeiten), die in 16 Sitzungsstunden niemand geprüft hat, weil jede
Kontrolle bisher gegen *Zufallssplits* lief. *Wiederholen wir uns?* Nein: EXP-046 ist die erste nicht-zyklische Aufgabe, EXP-047 die
erste Mechanismus-Kontrolle mit festgehaltenen Randverteilungen. *Messungen geeignet?* K bei festem Schritt 2000 ist robust gegen
Testmenge/Grokking (EXP-016 Nachtrag a), misst aber die Auswahl vor der Endlösung; EXP-045 misst deshalb zusätzlich bei 10 000.
*Nächste Annahme, die angegriffen wird:* dass M0 der Wirkweg ist. EXP-047 prüft genau das; bei *Häufigkeiten steuern mit* müssten
[[BEFUND-split-mechanismus]] und K1/K2 in [[FINDINGS]] umformuliert werden.

*Korrektur zu Sitzung 12 (eingetragen in Sitzung 13, 20:05 Berlin, gemessen):* Sitzung 12 lief laut `runner-state.json` nur
19:29–19:50 Berlin (20.7 min; letzter Commit 3d304d3 um 19:50). Die Zeitangaben „20:02–20:18“ (Zyklus 3), „20:22“ (Rückblick),
„20:12/20:17“ (EXP-047-README) und „20:21“ (LIVE) waren **geschätzt und lagen in der Zukunft**; die Arbeit geschah vor 19:50.
Inhalte und Zahlen bleiben unverändert. Die dort erwähnte Codex-Prüfung von EXP-046 brach mit dem Sitzungsende ab, ohne Befund.

---

## Sitzung 13 (2026-09-26, Start 19:59 Berlin, Deadline 22:59; außerhalb des Fensters; nur Prüfung, Code, Denkarbeit)

Stand gelesen (20:00, gemessen): kein STOP, kein Training aktiv, Fenster zu (ab 00:00; nächster Runner-Start 00:59 Berlin).
Hinweis für Zeitstempel: `TZ=Europe/Berlin date` zeigt in Git Bash UTC (keine tzdata); maßgeblich ist `guarded_run.py --check` (`now_berlin`).
Auch meine ersten LIVE-Zeiten dieser Sitzung waren geschätzt (20:08/20:10 um 20:03) und sind korrigiert.

**Zyklus 1 (20:00–20:05): Kann der ungetestete Nachtcode von EXP-046/047 still falsche Zahlen liefern?** Eigene Prüfung gegen
`training/grokverse`: `get_config(p=118)` erlaubt (nur p ≥ 2 geprüft), `W_E` hat Form [vocab, d], `evaluate`/`logits_last`/
`split_hash` (sortiert) passen, `Config.task` existiert (EXP-047-Auswertung liest `config.task`), Run-IDs von `freq_ban.py`
(`…_seed{s}_thr1_{stem}_devcuda`) und `group_train.py` passen zu den Globs der Auswertungen, Hintergrundjobs in `sh` lesen
stdin nicht (POSIX: /dev/null). Die 40 EXP-047-Splits: je 3831 eindeutige Paare, a- und b-Häufigkeiten eng = shuf exakt,
Zielmengen gleich, F ∩ G = ∅ (reine numpy-Rechnung). *Ergebnis:* kein Fehler gefunden.
*Codex:* neu gestartet (read-only, `codex_review_s13_2026-09-26.txt`), **abgebrochen mit „Your workspace is out of credits“**.
Nach Regel 12 nicht umgangen; stattdessen prüft ein unabhängiger Claude-Subagent (frischer Kontext, nur lesend).

**Zyklus 2 (20:03–20:05, reine Rechnung): Was sagt eine Theorie erster Ordnung für EXP-047 voraus?** Herleitung: Bei gleichverteilter
Ausgabe und gemeinsamer Jacobi-Matrix fällt der Häufigkeitsanteil aus dem ersten W_E-Gradienten **exakt** heraus (Σ_c des Zielteils
= n_a); die Gradientenleistung ist das „zentrierte M0“ Σ_c|L_k(c)|² − |n_k|²/p. `theory_counts.py`: Häufigkeitsanteil an M0 0.9 %;
zentriertes M0 unter shuf: Zielrang 26.0 (Zufall 27.5). *Ergebnis:* Vorhersage erster Ordnung Δ̄_shuf ≈ 0, D̄ > 0; als
[[experiments/EXP-047-marginal-control/README|EXP-047]] Nachtrag a **vor jedem Lauf** notiert (Kriterien unverändert). Bedeutung:
Ein positives Δ̄_shuf wäre damit nicht bloß „Häufigkeiten wirken“, sondern ein Hinweis auf einen Weg jenseits des ersten Gradienten.

**Zyklus 3 (20:05–20:07): Unabhängige Prüfung von EXP-046/047 statt Codex.** Claude-Subagent (frischer Kontext, nur lesend, nur numpy):
**kein Blocker**, Gruppengesetz/Irrep-Basis/nicht-abelsches M0/Globs/Schlüssel/Tests/Shell bestätigt. *Hoch:* EXP-046 hat den
Häufigkeits-Confound ohne eigene Kontrolle (a/b-Zielrang ≈ 8–10 von 29, Zufall 14). *Mittel:* Top-5 aus 29 grob; fertige Läufe werden
ohne Schrittprüfung übersprungen (nur Handläufe). *Niedrig:* überlappende Zufallsströme in EXP-046, `--force` löscht nicht vorab,
Zeitüberschreitung (rc 124) zählt als Fehler. *Übernommen:* Lesart von EXP-046 auf „der Split steuert“ eingeschränkt, Top-3-Δ und Δ_pow
als nicht vorab festgelegte Beschreibung (EXP-046 Nachtrag b, vor jedem Lauf). *Nicht geändert:* Code von EXP-046 (geprüft, Risiko
einer Änderung kurz vor dem ersten Lauf größer als der Nutzen); Subagent-L3 (Rest-Zielsignal im shuf-M0, Rang 24.4) ist durch
EXP-047 Nachtrag a erklärt (zentriertes M0 26.0 ≈ Zufall).

**Zyklus 4 (20:04–20:11): Nicht-modulare Aufgabe vorab festgelegt (Regel 15c).** Frage: Steuert der Split die Frequenzen auch bei
gewöhnlicher Addition a + b (Ausgabe 0..224), deren bekannte Lösung eine Zahlengerade ist (Liu et al. 2022)?
[[experiments/EXP-048-intadd-steering/README|EXP-048]]: EXP-016-Konstruktion mit Ganzzahlsumme, Ziele aus k = 6..56 (k ≤ 5 gehört der
Rampe), Seeds 160–169, Arme F/G (+ R), 2000 Schritte, GPU. **Primärgröße neu: Log-Leistungskontrast Δ_pow** statt Top-5-Überlappung,
weil eine Zahlengerade die Top-5 in beiden Armen besetzen würde; vorab an den gespeicherten EXP-016-Läufen kalibriert: Δ_pow 8.4 im
Mittel, 10/10 positiv (reine Nachrechnung). Eigenes Skript `intadd_train.py` (Muster `group_train.py`, `freq_ban.py` unberührt; speichert
Spektren, End-W_E und ein Zahlengeraden-R²). M0 (Ganzzahlversion): Ziele Rang 4.0 von 56 (k = 1, 2 immer oben), Anteil 0.140 vs. 0.079.
Literatur: N25 (nicht gefunden, vorläufig). In `queue_gpu_s11.sh` nach EXP-047 eingehängt. **Ungetestet** (Fenster).
*Fehler beim Bau gefunden:* `Path.with_suffix` hielt „.0_F“ für die Endung, F/G/R-Splits überschrieben sich (40 statt 60 Dateien);
behoben, neu erzeugt, geprüft. `theory_counts.py` ist nicht betroffen (Namen ohne Punkt).
*Nebenfund:* `queue_gpu_s11.sh` und die Queues von GPU-001, EXP-043/044/045/046 hatten CRLF-Zeilenenden (von Python ohne `newline`
geschrieben). Probe mit einem Wegwerf-Skript: Git-Bash-`sh` entfernt CR beim Lesen (Variable ohne `\r`), also vermutlich harmlos;
trotzdem auf LF normalisiert (Laborkonvention), `git diff --ignore-cr-at-eol` zeigt keine inhaltliche Änderung, `sh -n` ok.

**Zyklus 5 (20:12–20:17): Review EXP-048 und Größen-Verallgemeinerung.** (a) Idee „Festlegungszeit ≈ σ_init·√(2m/p)/lr ≈ 26 Schritte“
(Überschlag: Adam-Schritte wachsen linear, Schwelle = Init-Rauschen je Frequenz) **verworfen als neu**: steht als quantitative H40 schon in
EXP-040 Nachtrag c. (b) Subagent-Review EXP-048: kein Blocker; *Mittel 1:* Häufigkeiten tragen die Ziele (1.8×), Lesart eingeschränkt;
*Mittel 2:* Zahlengerade leckt in k ≥ 6 → Primärgröße **vor jedem Lauf** auf trendbereinigtes End-W_E umgestellt (Nachtrag a; numpy:
Schein-Δ roh 0.75, trendbereinigt 0.00). Dabei meinen eigenen neuen Selbsttest als entartet erkannt (Δ ≡ 0) und ersetzt; ohne numpy-
Nachrechnung hätte er die EXP-048-Queue nachts gestoppt. (c) [[experiments/EXP-049-width-steering/README|EXP-049]] vorab festgelegt:
K2 bei d_model 512 vs. 128 (Seeds 170–179, gleiche Splits, 40 GPU-Läufe, Primärgröße Δ_pow bei d = 512). Splits über EXP-047-Funktionen
(importlib, Namenskonflikt `make_split` umgangen; Seed 150 reproduziert die EXP-047-Datei exakt), Ziele = M0-Top-5 in 20/20. In
`queue_gpu_s11.sh` nach EXP-048; unabhängige Prüfung läuft. **Lehre:** Heredocs mit Backticks immer mit <<'EOF' (ein ungeschütztes
Heredoc hat zwei Dateinamen im README gelöscht; repariert).

**Rückblick nach fünf Zyklen (20:18, Auftrag §4).**
*Gelernt:* (1) Theorie erster Ordnung: Der Häufigkeitsanteil fällt aus dem ersten W_E-Gradienten exakt heraus, für jede Gruppe und auch
für nicht-modulare Addition; damit hat EXP-047 eine vorab notierte, falsifizierbare Erwartung. (2) Die Verallgemeinerung von K2 ist jetzt
über vier Achsen vorbereitet: Modulus/zusammengesetzter Modulus (EXP-043), nicht-abelsche Gruppe (EXP-046), nicht-modulare Aufgabe
(EXP-048), Modellbreite (EXP-049), dazu Architektur (EXP-045). Alle mit ≥ 10 Seeds (Regel 15b). (3) Prozess: In dieser Sitzung haben
unabhängige Prüfung und numpy-Nachrechnung **vor** dem ersten Lauf drei Fehler gefunden, die die Nacht gekostet hätten (Split-Dateien
überschrieben, entarteter Selbsttest, Scheineffekt der Zahlengeraden). *Wiederholen wir uns?* Die Gefahr ist jetzt eine andere: Es liegen
sechs ungetestete GPU-Versuche in einer Queue. Kein weiterer neuer Versuch heute; die nächste Sitzung soll erst Ergebnisse auswerten.
*Messungen geeignet?* Top-5-Überlappung ist bei nicht-zyklischen Aufgaben oder mit starkem Nicht-Fourier-Anteil zu grob; Δ_pow
(kontinuierlich, an EXP-016 kalibriert) ist für neue Aufgaben die bessere Primärgröße und wird in EXP-046 beschreibend mitberichtet.
*Nächste Annahme, die angegriffen wird:* dass die Steuerung über die Paarstruktur läuft (EXP-047) und dass sie mehr ist als eine
Eigenheit zyklischer Gruppen (EXP-046/048).

**Zyklus 6 (20:16–20:20): Literatur-Tiefe für K2 und Robustheit der Nachtauswertungen.** (a) Volltext-Abrufe: He et al. 2026
(nur vollständige Trainingsmengen, Auswahl durch Init) und Marchetti et al. 2026 (Reihenfolge nach Fourier-Statistik des festen
*Kodierungsvektors*, vollständige gleichverteilte Daten, kein Dateneingriff). Beide stützen die vorläufige Neuheitseinordnung von K2/N24.
(b) Subagent-Review EXP-049: kein Blocker; **Mittel:** ein divergierter Lauf (NaN) hätte in EXP-049 still *widerspricht* mit p = 0
ergeben (`one_sided_p` mit NaN → 0.0, numerisch geprüft). Selbst geprüft: dieselbe Lücke in **allen** Nachtauswertungen EXP-043–049
(in 043/044/045 als stilles Unsinns-K: Top-5 aus lauter NaN = k 1..5 per Tie-Break). Überall behoben: nicht-endliches Spektrum/W_E =
ungültiger Lauf; in allen sieben READMEs als Nachtrag vor jedem Lauf vermerkt. *Niedrig:* J aus dem d = 128-Durchsatztest (nur Laufzeit);
Init-Verdünnung hebt Δ_pow(512) mechanisch an (Einschränkung in EXP-049 ergänzt, Primärurteil unberührt).
(c) Gestartet: unabhängige Prüfung von GPU-001 und der fail-closed-Änderungen aus 2b19820 (nie geprüft, nie ausgeführt, sperren aber
die ganze GPU-Nacht).

*Vorfall (20:21):* Ein `git commit -a` hat die uncommitteten Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `runner-state.json`) mitcommittet. Sofort mit `git reset --soft HEAD~1` und `git restore --staged` rückgängig gemacht; Arbeitsverzeichnis unverändert, der neue Commit df994f2 enthält nur das JOURNAL. Ab jetzt nur gezielt `git add <pfad>`.

**Zyklus 7 (20:20–20:23, Theorie, reine Rechnung): Was sagt die Rechnung erster Ordnung über K2 hinaus?** (a) Vorab-Gesamtlesart der GPU-Nacht geschrieben ([[LESART-nacht-2026-09-27]]): Kombinationsregeln, u. a. K2 erst dann „über Aufgaben hinweg“, wenn ≥ 2 der 3 echt anderen Aufgaben *steuerbar* sind; bei 5 Tests à α 0.05 ≈ 23 % Risiko für mindestens ein falsch positives Ergebnis. (b) D₅₉: Die Identität Σ_c L_k(c) = Häufigkeitstransformierte gilt auch nicht-abelsch (im Code geprüft), Häufigkeitsanteil an M0 0.9 %, zentriertes M0 Zielrang 2.0 von 29 → Erwartung erster Ordnung: Steuerung in EXP-046 läuft über die Paarstruktur (EXP-046-README ergänzt). (c) Beim Aufschreiben Lücke der Herleitung gefunden: gemeinsame Einbettung → linker und rechter Beitrag addieren sich im Zeilengradienten. Mit Jacobi-Matrizen je Position folgt M0c (Transformer, J_L ≈ J_R durch gleichmäßige Aufmerksamkeit bei der Init) bzw. M0 (MLP mit getrennten W_in-Hälften). Das erklärt **nachträglich** die beiden Messungen aus Sitzung 5 (Transformer: M0c 0.77 vs. M0 0.57; MLP: M0 0.37 vs. M0c 0.24) in [[BEFUND-split-mechanismus]]. Einordnung: post hoc, vereinfachende Annahme, kein Test. Eigenen Fehler korrigiert (zuerst „Zwei-Hot-MLP“ statt „MLP mit gemeinsamem Embedding“ geschrieben).

**Zyklus 8 (20:24–20:25): Prüfung von GPU-001 (sperrt die GPU-Nacht) und neuer Kausaltest M0 gegen M0c.** (a) Subagent-Review der nie ausgeführten Änderungen aus 2b19820: kein Blocker; Hoch behoben (Ablehnungen im Durchsatztest wurden verschluckt, alte `raw_par`-Ergebnisse hätten sich gemischt, J hätte dauerhaft gedeckelt werden können; Details im GPU-001-README). (b) Aus der Herleitung von Zyklus 7 ein **trennscharfer Test**: Splits mit gleichphasigem (sym) bzw. gegenphasigem (anti) Kreuzterm. Offline (reine Rechnung, Seeds 180–189): sym Zielrang M0 2.0 / M0c 2.0 (M0c-Anteil 0.270); **anti M0 2.0 / M0c 25.3** (Zufall 27.5; M0c-Anteil 0.091, Zufall 0.089); Häufigkeiten in beiden ≈ Zufall (25.4 / 24.9). Folgt der Transformer M0c (Theorie + Sitzung-5-Messung am ersten Gradienten), steuert anti nicht; folgt er M0, steuern beide. Als [[experiments/EXP-050-phase-dissociation/README|EXP-050]] vorbereitet, **nicht in die Queue** (die Nacht hat genug Neues).

**Zyklus 9 (20:27–20:29, Vorbereitung der Nacht):** STATE-Wiederaufnahme für 00:59 als eigenständige Schrittliste neu geschrieben (GPU- und CPU-Queue, Beobachtung, rc-Deutung, Morgenbericht, Vorab-Lesart, optional EXP-050). CPU-Last geprüft: `queue_s10` läuft einen Job zugleich mit 4 Threads, GPU-Läufe je 1 Thread; bei J ≤ 8 bleibt die Summe ≤ 12 (Regel 17). Laufmenge der GPU-Nacht grob: ≈ 300 Läufe à 2000 Schritte + EXP-045 (20 × 10 000); Dauer erst nach GPU-001 (s/Schritt, J) abschätzbar. MLP-Gegenarm von EXP-050 bis nach EXP-045 zurückgestellt (ohne dessen K bei 2000 wäre der Messzeitpunkt geraten).

**Zyklus 10 (20:30–20:33): EXP-050 nach unabhängiger Prüfung umgebaut (vor jedem Lauf).** Subagent bestätigt Herleitung und alle Zahlen, findet aber einen **echten Confound**: Die Kreuzterm-Summe über alle k ist durch die Zahl der Spiegelpaare festgelegt; sym 706, anti 420, Zufall 571. Weil symmetrische Paare früher memoriert werden (He et al. 2026), hätte sym gegen anti auch Lerntempo verglichen. *Lösung, zweiter Anlauf:* Kontrolle mit Zufallsphasen (wie EXP-016) + Spiegelpaare auf anti-Niveau gesenkt → verworfen, weil Zufallsphasen die Häufigkeiten zielverzerren (Rang 12.9). Stattdessen **quadlm**: Viertelphase (Kreuzterm auf den Zielen null, M0c = M0, Häufigkeiten auf Zufallsniveau 25.7) + Spiegelpaare exakt wie anti (420). Primärvergleich jetzt quadlm gegen anti: gleiches M0, gleiche Häufigkeiten, gleiche Spiegelpaarzahl, M0c-Zielrang 2.0 gegen 25.3. Rest: 19 Diagonalpaare mehr, Reihenfolge-Neigung −0.028 gegen −0.041. sym gegen anti sekundär. 60 Läufe; nicht eingereiht (STATE Schritt 7). *Lehre:* Eine „saubere“ Manipulation im Frequenzraum hat eine Entsprechung im Paarraum (Spiegelpaare); vor jedem Kontrast prüfen, welche **einfachen** Split-Statistiken (Häufigkeiten, Spiegel, Diagonale, Reihenfolge) sich mitbewegen.

*Lehre angewandt (20:33):* Spiegelpaare/Diagonale/Reihenfolge in den Nachtversuchen: EXP-047 eng 566/33.8/+0.003 gegen shuf 568/32.4/−0.001; EXP-049 F 566/35.8 gegen G 571/35.3. Kein Confound dieser Art (die übrigen Nachtversuche vergleichen F gegen G derselben Konstruktion).

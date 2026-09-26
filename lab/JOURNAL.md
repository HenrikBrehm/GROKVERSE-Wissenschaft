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

**Technik (06:55):** Beim Prüfen gefunden: Meine Python-Bearbeitungen haben mehrere Dateien auf CRLF umgestellt, darunter
`queue_s5.sh` und `EXP-020-data-switch/queue.sh`, die unter `sh` gebrochen wären (`sh -n` meldet das nicht). Alle in
dieser Sitzung geänderten oder neuen Dateien, die zu Sitzungsbeginn LF hatten oder neu sind, wieder auf LF gestellt;
Tests danach 14/14 und 5/5. Hinweis in STATE. Zwei Probe-`summary.json` (Trockenläufe, „nicht auswertbar“) aus Git entfernt.

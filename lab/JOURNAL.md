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

**Zyklus 11 (20:33–20:40): Regel 18 entdeckt und begonnen.** Um 20:33 beim Nachtragen des Gedächtnisindexes bemerkt, dass `SESSION_PREAMBLE.md` seit 20:30 eine **Regel 18** hat (Astra-Review umsetzen, Läufe heute Nacht erst ab 03:00). Mein Sitzungsauftrag (Start 19:59) enthielt sie noch nicht. Sofort umgesteuert: STATE-Wiederaufnahme auf Regel 18 umgestellt (Queues nicht mehr ab 00:59). Umgesetzt in der Reihenfolge von 18a: **Punkt 3** (`freq_ban.py`: Fingerprint, Sperre, atomare Arrays, completed nach Artefaktprüfung; Run-IDs unverändert) und **Punkt 10** (Durchsatz über Wandzeit, `config.device`), **Punkt 16** teilweise (gemeinsamer Lader, an 20 gespeicherten EXP-016-Läufen geprüft; EXP-046–050 umgestellt). Alles **ungetestet** bis 03:00. Außerdem: Subagent-Review EXP-043/044/045 (nur Niedriges: EXP-044-F/G-Läufe tragen das Präfix EXP-043; mul113-`final_top_m_freqs` in additiver Basis, Auswertung rechnet ohnehin neu; R-Arm von EXP-043 nur knapp geprüft). Tabelle „Umsetzung“ in [[reviews/ASTRA_2026-09-26]].

---

## STATE-Archiv (bis Sitzung 13, 2026-09-26 20:43 Berlin; wörtlich aus lab/STATE.md übernommen)

Astra-Review Punkt 17 / Regel 18a5: STATE.md wird auf ≤ 80 Zeilen gekürzt; die bisherige Fassung steht hier unverändert (Überschriften um eine Ebene abgesenkt).

# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-26, 20:29 Berlin (Sitzung 13; nächster Runner-Start 2026-09-27 00:59 Berlin)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[JOURNAL]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]]

### Wiederaufnahme (zuerst lesen)

- **REGEL 18 GILT (Nutzer, 2026-09-26 20:30; entdeckt in Sitzung 13 um 20:33): Astra-Review umsetzen, [[reviews/ASTRA_2026-09-26]].**
  Nacht 26./27.09.: **Läufe (Training und Tests) erst ab 03:00 Berlin** (im Wächter hinterlegt). Vorher nur Code/Doku in dieser Reihenfolge
  (Regel 18a): 1. Punkt 3 Fingerprint/Sperre/atomare NPY in `freq_ban.py` → 2. Punkt 10 GPU-001/compare.py + `config.device` →
  3. Punkt 16 gemeinsamer Ergebnislader → 4. Punkt 11 Nacht-Queues auf `parallel_queue.py` → 5. Punkt 17 STATE ≤ 80 Zeilen →
  6. Punkt 5 getrennte Zufallsströme. Ab 03:00 (18b): Wächter-Abnahme mit harmlosem Job + STOP-Test, dann freq_ban-Tests, dann GPU-001,
  dann Nacht-Queues: **GPU jetzt `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1`** (Hintergrund; ersetzt
  queue_gpu_s11.sh; Plan ansehen mit `--dry-run`; Wiederaufnahme = derselbe Befehl; Status in `lab/runner/logs/night_*/night_status.json`).
  Fortschritt: Tabelle „Umsetzung“ unten in `lab/reviews/ASTRA_2026-09-26.md`. **Der Sitzung-13-Block darunter
  (Queues ab 00:59 starten) ist dadurch überholt**, gilt nur noch für Inhalte (was vorbereitet ist).
- **SITZUNG 13 (20:29) → NÄCHSTE SITZUNG (Start 00:59 Berlin, Fenster offen): genau diese Schritte, gilt vor allen Blöcken darunter.**
  1. `python lab/tools/guarded_run.py --check` (muss `in_window: true` zeigen) und `ps -ef | grep -E "queue|guarded_run" | grep -v grep` (nichts aktiv).
  2. GPU-Queue im Hintergrund: `sh lab/experiments/queue_gpu_s11.sh > lab/runner/logs/gpu_s11.log 2>&1`.
     Reihenfolge: GPU-001 (Regression → Gleichwertigkeit → Durchsatz, ≈ 15 min) → EXP-043 → EXP-046 → EXP-047 → EXP-048 → EXP-049 → EXP-044 → EXP-045.
     Nach ≈ 1 min im Log `regression` prüfen; bei FAIL stoppt die Queue selbst (dann GPU vorerst nicht nutzen, Blocker eintragen).
  3. CPU-Queue im Hintergrund: `sh lab/experiments/queue_s10.sh > lab/runner/logs/queue_s10.log 2>&1` (ignoriert GPU-Läufe beim Warten).
  4. Beobachten (Regel 14); `verdict_*.json` von GPU-001 ins JOURNAL (Regel 16b/c: Gleichwertigkeit, s/Schritt, J).
  5. Ende der Queue: rc 3 = Wächter/Deadline → nächste Sitzung **denselben Befehl** neu starten (Fertiges wird übersprungen);
     rc 1 „done WITH FAILURES“ → Log nach „failed“ durchsuchen; ebenfalls einfach neu starten ist harmlos.
  6. Auswerten: `python lab/tools/night_report.py lab/runner/logs/gpu_s11.log` (liest GPU-001-Verdikte und alle summary.json).
     **Vor jeder Deutung** [[LESART-nacht-2026-09-27]] lesen (vorab festgelegte Kombinationsregeln), dann READMEs/LAB/FINDINGS eintragen.
  7. Falls die GPU-Queue deutlich vor 13:00 fertig ist: [[experiments/EXP-050-phase-dissociation/README|EXP-050]] (M0c gegen M0,
     vorbereitet, unabhängig geprüft, nach Prüfung um Kontrollmodus quadlm erweitert; 60 Läufe) mit `sh lab/experiments/EXP-050-phase-dissociation/queue.sh J` starten (J aus
     `verdict_throughput.json`).
  Neu in Sitzung 13: EXP-048 (nicht-modulare Addition, Primärgröße trendbereinigtes Δ_pow), EXP-049 (4× Breite), EXP-050 (nicht
  eingereiht); Nachträge vor jedem Lauf in EXP-046 (Lesart), EXP-047 (Theorie: Häufigkeiten wirken im ersten Gradienten nicht), GPU-001
  (Durchsatz-Ablehnungen), EXP-043–049 (NaN-Läufe ungültig). **Codex ohne Guthaben** („out of credits“) → Claude-Subagenten als Zweitprüfung.
  Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`); Git-Bash-`date` kennt Europe/Berlin nicht. Nur gezielt `git add <pfad>`
  (nie `commit -a`: Nutzeränderungen an `guarded_run.py`, `install_task.ps1`, `runner-state.json` bleiben uncommittet).
- **SITZUNG 12 (19:58) → NÄCHSTE SITZUNG (ab 00:00, im Fenster), gilt vor dem Sitzung-11-Block unten:**
  Ablauf wie unten Schritte 1–5, aber die GPU-Queue ist jetzt **fail-closed** (Codex s12, commit 2b19820): Reihenfolge
  GPU-001 → EXP-043 → **EXP-046** (neu: Diedergruppe D₅₉, nicht-abelsch) → EXP-044 → EXP-045. Endet sie mit
  „done WITH FAILURES“ (rc 1), im Log nach „failed“ suchen; rc 3 = Wächter hat abgelehnt (Fenster/Deadline), Wiederaufnahme =
  dieselbe Queue erneut starten (überspringt Fertiges). Nach GPU-001: `verdict_{regression,equivalence,throughput}.json`
  lesen und ins JOURNAL (Regel 16b/c). Auswertung EXP-046: `summary.json` gegen README (Strukturprüfung zuerst!).
  Nicht von mir: uncommittete Nutzeränderungen in `lab/tools/guarded_run.py` (DST-Fix) und `lab/runner/install_task.ps1`
  (4 h Zeitlimit) sowie `lab/tools/parallel_queue.py` (Regel 17) — nicht anfassen/committen.
- **SITZUNG 11 (19:24) → NÄCHSTE SITZUNG (ab 00:00, im Fenster) in dieser Reihenfolge:**
  1. `python lab/tools/guarded_run.py --check`; keine Queue aktiv (`ps -ef | grep -E "queue|guarded_run"`).
  2. `sh lab/experiments/queue_gpu_s11.sh > lab/runner/logs/gpu_s11.log 2>&1` im Hintergrund (GPU-001 → EXP-043 → EXP-044 →
     EXP-045, J aus dem Durchsatztest). **Warten, bis im Log `regression: PASS` steht (≈ 1 min).** Das ist der Regressionstest
     für die `--device`/`--p`/`--task`/`--arch`-Änderungen an `freq_ban.py`. Bei `regression: FAIL` stoppt die GPU-Queue selbst;
     dann `git checkout a91ef0d -- lab/experiments/EXP-001-freq-ban/freq_ban.py`, erst danach Schritt 3 (GPU entfällt vorerst).
  3. Dann `sh lab/experiments/queue_s10.sh > lab/runner/logs/queue_s10.log 2>&1` im Hintergrund (CPU, wie geplant). Die
     Warteschleifen darin ignorieren GPU-Läufe (`--device cuda`).
  4. Beide Logs beobachten. `equivalence: FAIL` → GPU-Queue stoppt, Blocker hier eintragen; EXP-043/045 dann erst nach queue_s10
     auf der CPU erwägen (neuer Nachtrag nötig, Geräte nie mischen).
  5. Ergebnisse: `summary.json` von EXP-043/044/045 gegen die vorab festgelegte Lesart in den READMEs; [[FINDINGS]] aktualisieren.
- **Sitzung 11 neu:** [[FINDINGS]] (Synthese, Regel 15a); `freq_ban.py` `--device`/`--p`/`--task` (ungetestet);
  [[experiments/GPU-001-equivalence/README|GPU-001]] (Kriterien vorab); [[experiments/EXP-043-generalize-steering/README|EXP-043]]
  (Verallgemeinerung von K2 auf add 97 / mul 113, 10 Seeds, vorab festgelegt, Splits erzeugt).

- **ENDE SITZUNG 10 (19:00) → nächste Sitzung beginnt hier.** Start 2026-09-26 22:29 Berlin, Fenster ab 00:00. **Im Fenster ein Befehl:**
  `python lab/tools/guarded_run.py --check`, prüfen, dass keine Queue läuft (`ps -ef | grep -E "queue|guarded_run"`), dann
  `sh lab/experiments/queue_s10.sh` im Hintergrund (Log `lab/runner/logs/queue_s10.log`) und beobachten. Danach
  `python lab/tools/night_report.py lab/runner/logs/queue_s10.log`, Ergebnisse in README/JOURNAL/LAB/[[BEFUND-festlegung]] eintragen,
  dabei die **vorab festgelegte Lesart** in [[BEFUND-festlegung]] einhalten. Bis 00:00 Denkarbeit (Ideen: G-Unterdrückung N22,
  kalibrierter Test für N21, SGD-G-Phase als Test der Adam-Verdrängung).
- **SITZUNG 10 (18:51), NEUE REIHENFOLGE:** `queue_s10.sh` = EXP-035 (Seeds 30, 31, 32, 34) → EXP-038 → **EXP-041** → EXP-036 → EXP-039
  → EXP-040 → EXP-034 → EXP-042 → queue_s5. Grund: F und G teilen ≈ 73 % der Paare, die Festlegung ist nur gegen einen 27-%-Wechsel
  gezeigt; EXP-041 (E/R ≈ 37 % gemeinsam) ist der härtere Test und kommt vor den Uhr-Versuchen (JOURNAL Zyklus 20).
- **SITZUNG 10 (18:49), Auswertung nach der Nacht:** `python lab/tools/night_report.py lab/runner/logs/queue_s10.log` (nur lesend)
  zeigt Ablehnungen, Fehlschläge, fertige Läufe und die Urteile aller `summary*.json`. `freq_ban.py` wurde nach Codex gehärtet
  (9fa4b7a; Überspringen prüft jetzt Skalen-Metadaten und Schnappschüsse); der Überspringen-Zweig ist erst in der Nacht getestet.
- **SITZUNG 10 (18:38):** Neu vorbereitet **EXP-042** (Split-Neigung eps_G 8/1, Splits erzeugt, Nachtrag a nach Codex). Reihenfolge
  `queue_s10.sh` jetzt: EXP-035 → EXP-038 → EXP-036 → EXP-039 → EXP-040 → EXP-034 → EXP-042 → EXP-041 → queue_s5. Neue Codepfade
  (alle fail-closed durch Smoke/Selbsttest am Anfang ihrer Queue): EXP-036 (Schnappschüsse), EXP-039, EXP-040, EXP-041, EXP-042.
- **SITZUNG 10 (18:21):** Neu: EXP-035 Nachtrag c/d (P35d nach Codex **zurückgezogen**, `state_match.py` nicht in der Queue), EXP-040 Nachtrag c (R(hi) ∈ [0.5, 2]), EXP-039 Nachtrag b (Vorbehalt Strecke). N21 (Attraktoren).
- **SITZUNG 10 (18:16):** `queue_s10.sh` macht jetzt nach einem fehlgeschlagenen Versuch mit dem nächsten weiter (`part()`), nur
  rc 3 (Wächter) stoppt. Nach dem Nachtlauf deshalb **das Log nach „failed“ durchsuchen** und den betroffenen Versuch reparieren.
  Neu vorbereitet (nicht in einer Queue): **EXP-041** (Prägung E → R / R → E, 10 Seeds, ≈ 3.1 h, ungetestet). Ideen N19, N20.
- **SITZUNG 10 (18:02):** Neu **EXP-040** (W_E-Init-Skala, H40 Amplitudenschwelle; Nachtrag a nach Codex), **ungetestet**:
  Selbsttest + Smoke laufen fail-closed am Anfang von `EXP-040/queue.sh`. `freq_ban.py` speichert seit 60d9ab0 bei `--spectra-at`
  zusätzlich W_E-Schnappschüsse (`we_snapshots.npy`); dieser Pfad ist **erst durch den EXP-036-Smoke** geprüft (steht in der Queue
  vor allen EXP-036-Läufen). Scheitert er: `freq_ban.py`, Funktion `spectrum()`, prüfen. Reihenfolge `queue_s10.sh`:
  EXP-035 → EXP-038 → EXP-036 → EXP-039 → EXP-040 → EXP-034 → queue_s5.
- **SITZUNG 10 (17:55):** Fenster heute zu. Neu: **EXP-039** (Lernraten-Uhr, vorab festgelegt mit Nachtrag a nach Codex, Smoke
  und Selbsttest ok), in `queue_s10.sh` nach EXP-036 eingehängt. EXP-035: Seed 30 komplett, Seed 31 t = 50 und 150 fertig
  (Queue überspringt sie). Nächstes Fenster unverändert: `sh lab/experiments/queue_s10.sh`.
- **SITZUNG 10 (17:41):** EXP-035 Seed 30 fertig (7 Läufe), Seed 31 t = 50, 150 laufen von Hand bis ~17:52 (Log
  `lab/runner/logs/exp035_s10_manual.log`). `queue_s9.sh` ist beendet. EXP-036 hat **Nachtrag d + e** (kalibriertes P36b mit frühen
  Spektren `--spectra-at`, Smoke vorgeschaltet und von Hand geprüft). **Nächstes Fenster (ab 00:00) unverändert:**
  `python lab/tools/guarded_run.py --check`, keine Queue aktiv (`ps -ef | grep -E "queue|guarded_run"`), dann
  `sh lab/experiments/queue_s10.sh` im Hintergrund (EXP-035 Rest überspringt Fertiges → EXP-038 → EXP-036 (+ `analyze_p36b.py`) → EXP-034 → queue_s5).

- **ENDE SITZUNG 9 (17:06) → nächste Sitzung beginnt hier.** Nächster Start 19:49 Berlin = **außerhalb des Fensters** (heute bis
  18:00, ab 27.09. 00:00–13:00): bis 00:00 nur Denk-/Sucharbeit. **Im Fenster ein Befehl:** `python lab/tools/guarded_run.py --check`,
  prüfen, dass keine Queue läuft (`ps -ef | grep -E "queue|guarded_run"`), dann **`sh lab/experiments/queue_s10.sh`** im
  Hintergrund (Log z. B. `lab/runner/logs/queue_s10.log`): EXP-035 (Rest; überspringt Fertiges) → **EXP-038** → **EXP-036** →
  EXP-034 → queue_s5. Nach jeder Auswertung Ergebnis ins README/JOURNAL/LAB (die Queue schreibt nur `summary.json`).
  Abgeschlossen in Sitzung 9: EXP-020 (*nicht bestätigt*; beschreibend (25, 50] in 5/5), EXP-028 (*teilweise*), EXP-037
  (*gestützt* mit Einschränkung: reproduzierbare, funktionale Konfliktfrequenzen). Befunde: JOURNAL „Abschlussbericht Sitzung 9“.
  **Vor dem EXP-036-Start (Denkarbeit, 19:49–00:00):** P36b kalibriert neu festlegen (EXP-036 Nachtrag c; Codex-Einwände
  in `EXP-037-alternation-conflict/codex_conclusion_review_2026-09-26.txt`). EXP-036 steht in queue_s10 erst nach EXP-038.
  Denkarbeit-Ideen: warum 25–50 Schritte (Verbindung zur linearen Modentheorie aus EXP-033), Konfliktfrequenzen theoretisch
  (gemeinsame Unterstützung, P36b), EXP-038-Folgeversuch mit norm-angepasstem Rücksetzen.

- **SITZUNG 9 (16:22):** EXP-020 **abgeschlossen** (*nicht bestätigt* 4/5; beschreibend (25, 50] in 5/5), EXP-028 *teilweise*,
  EXP-020 Nachtrag d an frischen Seeds **nicht bestätigt**. `queue_s9.sh` läuft EXP-037 (Smoke ok; 9 Läufe bis ~17:05), dann
  EXP-035. Wiederaufnahme: `sh lab/experiments/queue_s9.sh` (überspringt Fertiges). Nach EXP-037:
  `python lab/tools/guarded_run.py -- python lab/experiments/EXP-037-alternation-conflict/ablate_foreign.py` (von Hand,
  nicht in der Queue; braucht `summary.json` von EXP-037).

- **SITZUNG 9 (15:13):** `queue_s8.sh` angehalten, **`queue_s9.sh` läuft** (Log `lab/runner/logs/queue_s9.log`; Reihenfolge EXP-020 Rest → Auswertungen → **EXP-037** → EXP-035 → EXP-036 → EXP-034 → queue_s5). Wiederaufnahme = `sh lab/experiments/queue_s9.sh`.
- **SITZUNG 9 (15:04):** `queue_s8.sh` lief seit 14:50 (Log `lab/runner/logs/queue_s8.log`, EXP-020 Seed 32
  t = 1000, dann Seeds 33, 34, dann EXP-035). **Ab jetzt `sh lab/experiments/queue_s9.sh` statt `queue_s8.sh`** (gleiche
  Reihenfolge, zusätzlich Nachtrag-d-Auswertung und **EXP-036** nach EXP-035; überspringt Fertiges). Nie zwei Queues
  gleichzeitig: vorher `ps -ef | grep -E "queue|guarded_run"`.
  Neu vorab festgelegt: EXP-020 **Nachtrag d** (fremde Frequenzen in Mischzuständen, P-d1/P-d2 für Seeds 33/34,
  `conflict_freqs.py`), **EXP-036** (neue Init bei gleichem Split, 7 Paare, Vorzeichentest über Paare; nach Codex umgebaut,
  Nachtrag a). N15 in NOVEL_DIRECTIONS.

- **ENDE SITZUNG 8 (14:27):** `queue_s5.sh` kontrolliert angehalten; letzter Lauf EXP-020 Seed 32 t = 150 lief zu Ende (vor der
  Deadline). EXP-020: Seeds 30, 31 vollständig (beide (25, 50], stützen H20), Seed 32: nur F, nur G, t = 150, 50, 25, 10 fertig (es fehlen 400, 1000).
  **Weiter mit `sh lab/experiments/queue_s8.sh`** (siehe nächster Punkt). Befunde der Sitzung: JOURNAL „Abschlussbericht Sitzung 8“.

- **NÄCHSTE SITZUNG, ein Befehl (Sitzung 8, 13:51):** `python lab/tools/guarded_run.py --check`, dann prüfen, dass keine Queue läuft
  (`ps -ef | grep -E "queue|guarded_run"`), dann **`sh lab/experiments/queue_s8.sh`** im Hintergrund (Log z. B.
  `lab/runner/logs/queue_s8.log`). Reihenfolge darin: Rest von EXP-020 (Seeds 31–34) → Auswertung EXP-020 und EXP-028 →
  EXP-035 (Smoke, Seeds 30–32) → Auswertung → EXP-034 → Auswertung → Rest von `queue_s5.sh`. Alles überspringt Fertiges.
  Nach jeder Auswertung: Ergebnis ins README/JOURNAL/LAB (die Queue schreibt nur `summary.json`).

- **Sitzung 8, 13:47 (neuester Stand):** Reihenfolge für die nächsten Fenster: (1) `queue_s5.sh` weiter (EXP-020 Seeds 31–34; danach
  EXP-020- und EXP-028-Auswertung), (2) `sh lab/experiments/EXP-035-warmup-lockin/queue.sh 30 31 32` (braucht die EXP-020-
  Intervalle der Seeds; beginnt mit Smoke), (3) `sh lab/experiments/EXP-034-phase2-optimizer/queue.sh`. Alternativ EXP-034 vor
  EXP-035, falls EXP-020 noch läuft und ein Jobplatz frei ist: nie zwei Queues gleichzeitig. `queue_s5.sh` enthält nach EXP-020
  noch EXP-018/014/023/022/010 (viele Stunden): nach EXP-020 ggf. anhalten, um EXP-035/034 vorzuziehen.
  `freq_ban.py` hat seit b231fc6 eine Option `--warmup` (Standard 0 = unverändert).

- **Sitzung 8, 13:32:** EXP-033 **abgeschlossen** (*zustandsbestimmt* vorab; nach Codex eingeschränkt: AdamW in Phase 1 nicht nötig).
  `queue_s5.sh` läuft wieder seit 13:17 (EXP-020 Seed 30 fast fertig, dann Seeds 31–34). **EXP-034** vorab festgelegt
  (Nachtrag a, commit a7e9cf2/c36d212), nicht ausgeführt, `--opt2 gd` ungetestet. **Nächste Sitzung (Fenster heute bis 18:00,
  ab 2026-09-27 wieder 00–13):** Prioritätsvorschlag: EXP-020 zu Ende (liefert EXP-020 + EXP-028), dann
  `sh lab/experiments/EXP-034-phase2-optimizer/queue.sh` (A ≈ 75 min, Pilot ≈ 27 min, B ≈ 90 min), Auswertung
  `python lab/tools/guarded_run.py -- python lab/experiments/EXP-034-phase2-optimizer/analyze.py`. Vor dem Start prüfen, ob
  noch eine Queue läuft (`ps -ef | grep -E "queue|guarded_run"`); nie zwei Queues gleichzeitig.

- **Sitzung 8, 12:30:** EXP-033-Queue läuft (Nachtrag c, `_bt`-Läufe); Wiederaufnahme = `sh lab/experiments/EXP-033-optimizer-lockin/queue.sh` (überspringt Fertiges). `queue_s5.sh` weiter pausiert.

- **Sitzung 8, 12:18:** `queue_s5.sh` **angehalten** (EXP-020 Seed 30: F, G, t = 150 fertig, t = 50 lief zu Ende). EXP-033-Queue
  läuft im Hintergrund (Log `lab/runner/logs/queue_exp033.log`). Danach: `analyze.py` von EXP-033, dann `sh lab/experiments/queue_s5.sh`.
- **Sitzung 8, 12:15:** `queue_s5.sh` läuft (EXP-020 Seed 30, Log `lab/runner/logs/queue_s5.log`). **EXP-033** vorab festgelegt
  (Nachtrag a nach Codex, commit 840e890), noch kein Lauf. Plan: nach EXP-020 Seed 30 Warteschlange anhalten (nur den
  `sh`-Prozess beenden, laufenden Lauf fertig werden lassen), dann `sh lab/experiments/EXP-033-optimizer-lockin/queue.sh`,
  dann `python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/analyze.py`, dann `queue_s5.sh`
  erneut (überspringt Fertiges). Wurde die Sitzung unterbrochen: erst `tasklist | grep python` prüfen, dann in dieser
  Reihenfolge fortsetzen (beide Skripte überspringen Fertiges).

- **ENDE SITZUNG 7 (11:24) → nächste Sitzung beginnt hier.** Kette `queue_s7.sh` wird vor Sitzungsende kontrolliert
  um 11:51 gestoppt (EXP-025 vollständig, ausgewertet). **Nächste Schritte im Fenster:**
  1. `python lab/tools/guarded_run.py --check`
  2. EXP-025 ist fertig und ausgewertet (*teilweise*, 11:51).
  3. `sh lab/experiments/queue_s5.sh` (EXP-018/020-Smokes, dann **EXP-020 zuerst** (liefert auch EXP-028), EXP-018, EXP-014, …),
     danach `python lab/tools/guarded_run.py -- python lab/experiments/EXP-028-memo-imprint/analyze.py`
  **Neue Befunde Sitzung 7:** EXP-032 *Festlegung in ≤ 20 Schritten* (t½ = 5), EXP-030 *Rest gestützt*, EXP-029 *teilweise*,
  EXP-024 Q *richtungsgleich n. s.* / R *bestätigt* (memorierend), EXP-026 *Anker ok, Trend n. s.*, EXP-027 *nicht auswertbar*,
  EXP-027b *widerspricht*. EXP-031 zurückgestellt (Umbau nötig). Ideen: EXP-033 (AdamW-Rolle), EXP-031 neu (gekreuzte Spender).
- **Sitzung 7, 10:32:** EXP-026 fertig (*Anker ok, Trend n. s.*; beschreibend Festlegung in ≤ 50 Schritten). Kette läuft:
  EXP-027 → EXP-032 → EXP-027b (beide in `EXP-025/queue.sh` vorangestellt) → EXP-025 → queue_s5. Wiederaufnahme:
  `sh lab/experiments/queue_s7.sh` (überspringt Fertiges). Auswertungen: EXP-027 `analyze.py` (erwartet *nicht auswertbar*,
  Güte), EXP-032 `analyze.py`, EXP-027b `analyze_b.py`, EXP-025 `analyze.py`. EXP-031 zurückgestellt.
- **Sitzung 7, 09:59, neue Befunde (ohne Training, vorab festgelegt):** EXP-029 *teilweise* (W_E ist in der Memorisierungsphase
  spezifisch mit der eigenen Maske ausgerichtet, 10/10; Abbau bis gen + 25 nur 8/10), EXP-030 *Rest gestützt* (M0 → K läuft
  über W_E bei Schritt 250). EXP-028 vorbereitet (wartet auf EXP-020-Läufe). N13 nach Codex korrigiert.
- **Sitzung 7, 09:46:** EXP-024 **abgeschlossen** (Q richtungsgleich n. s., R bestätigt aber memorierend). Läuft:
  `sh lab/experiments/queue_s7.sh` (Log `lab/runner/logs/queue_s7.log`): EXP-026-Smoke (ok) → EXP-026 (30 Läufe, seit 09:44,
  **Umschaltdesign nach Codex, Nachtrag a**, commit 53450e1) → EXP-027 (in EXP-026/queue.sh verkettet) → EXP-025 → `queue_s5.sh`. Alles überspringt Fertiges;
  Wiederaufnahme = `sh lab/experiments/queue_s7.sh` erneut starten (die Warteschleife endet sofort, weil das EXP-024-Log
  schon eine `[exp024]`-Zeile hat; fehlt sie, zuerst `sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh`).
  Auswertungen danach: EXP-026, EXP-027, EXP-025 je `analyze.py` (über den Wächter).

- **Sitzung 6, 08:53:** Baseline 19 fertig (EXP-003d 10/10). Läuft: **EXP-024** (`sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh`,
  Log `lab/runner/logs/queue_exp024.log`, überspringt fertige Läufe). `queue_s5.sh` ist **angehalten**; danach neu starten
  (setzt bei den Smokes EXP-018/020 fort). Nach EXP-024: `python lab/tools/guarded_run.py -- python lab/experiments/EXP-024-quadratic-agf-mask/analyze.py`.
- EXP-015/012 Phase 2 mit n = 10 nur berichten: `mask_spectrum.py --phase 2 --suffix _n10`, `predict.py --phase 2 --predictor G0 --suffix _n10`.

- **Sitzung 5, 07:31:** Der Nutzer hat um 06:58 die Freigabe erteilt (`.claude/settings.local.json`: `sh lab/experiments/*queue*`,
  `python lab/tools/guarded_run.py *`). `queue_s5.sh` lief 07:30–08:24: EXP-016 Seeds 16–19 und Baseline 18 fertig; Baseline 19
  vom Wächter abgelehnt (Deadline), rc 3, keine Prozesse mehr. **Nächste Sitzung: denselben Befehl erneut starten** (setzt
  bei Baseline 19 fort).
- **Neue Warteschlange:** `sh lab/experiments/queue_s5.sh` (ersetzt `queue_s4b.sh`, dieselben Läufe plus EXP-018/020,
  neue Reihenfolge). Log z. B. nach `lab/runner/logs/queue_s5.log`. Reihenfolge: EXP-016 Seeds 16–19 (je 2 × 4.5 min,
  danach Entscheidung) → EXP-003d-Baselines 18, 19 → Smoke EXP-018 und EXP-020 (+ `check_smoke.py`) → EXP-018 Seeds
  20–24 → EXP-014 Kreuzpaare → EXP-020 → EXP-023 → EXP-022 (über deren eigene `queue.sh`) → EXP-018 Seeds 25–29 →
  EXP-010-Tausch 11–19. Sie stoppt bei **jedem** Exit ≠ 0;
  fertige Läufe werden übersprungen (`freq_ban.py` endet dann seit Sitzung 5 mit 0). Neu starten = fortsetzen.
- **Abgebrochene Läufe** stehen mit `status: running` in `result.json` und werden neu gestartet (kein Resume).
- Vor jedem Start: `python lab/tools/guarded_run.py --check`.
- **Abhängigkeit:** Die Läufe mit `--min-minutes 33` (Baselines, EXP-014, EXP-010) brauchen den **uncommitteten**
  `guarded_run.py` des Nutzers ohne feste Jobgrenze (Regel 14). Mit der committeten Fassung (Jobgrenze 20 min) würde der
  Wächter sie mit Exit 3 ablehnen und die Warteschlange hielte an (Codex-Prüfung der Warteschlange, Sitzung 5).
- **Zeilenenden:** Python schreibt unter Windows im Textmodus CRLF. Shell-Skripte müssen LF haben (sonst bricht `sh`).
  Nach Änderungen an `*.sh` mit `file` prüfen; beim Schreiben aus Python `newline='
'` benutzen.
- Nach EXP-016 Seed 17 (8 Seeds): `python lab/experiments/EXP-016-engineered-split/analyze.py`.

### Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  Uncommittete Änderungen an `lab/runner/*`, `lab/runner-state.json` und `lab/tools/guarded_run.py` stammen vom
  Nutzer (Regeln 13/14, keine feste Jobgrenze). Sie sind bewusst nicht committet; der Nutzer entscheidet.
- **Umgebung:** Windows 11, Python 3.12, torch 2.13.0, numpy 2.5.1 (Studie: torch 2.12.1). Die rekonstruierten Inits
  stimmen trotzdem bitgenau mit den gespeicherten Schritt-0-Checkpoints überein. 0.13 s/Schritt (Transformer, 4 Threads).
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Interpretation bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`), Sitzungsstart und -ende-Klassifikation belegt.

### Stand der Versuche (nach Sitzung 5)

**Bestätigt an frischen Seeds 10–17 (vorab festgelegt):**
- [[experiments/EXP-015-mask-spectrum/README|EXP-015]]: Das Masken-Spektrum M0 des Trainingssplits (ohne Gewichte) sagt die
  Rangfolge der gelernten Frequenzen voraus (r̄ 0.277, fremde Masken 0.499, p 2.5e-5). **Nur Assoziation.**
- [[experiments/EXP-012-init-gradient/README|EXP-012]]: Erster Gradient an W_E > Init-Spektrum (p 0.031).

**Abgeschlossen (Sitzung 5, 08:06):** [[experiments/EXP-016-engineered-split/README|EXP-016]] *steuerbar*: 10/10 Seeds, Δ̄ = +7.7 von 10,
p ≈ 0.001. Konstruierte Splits geben die gelernten Frequenzen vor; alle Abweichungen sind 2k-Harmonische der Ziele.

**Neu vorbereitet in Sitzung 5 (alle nicht ausgeführt, Codex-Reviews eingearbeitet):**
- [[experiments/EXP-018-split-speed/README|EXP-018]]: Beschleunigt ein spektral konzentrierter Split das Grokking?
  Feste Testmenge, Kontrolle D = Gewichte von E innerhalb der Antidiagonalen permutiert, Seeds 20–29. Drei
  konkurrierende Vorhersagen (H18 / Frequency Principle nach Zhou et al. 2024 / Komplement-Artefakt).
- [[experiments/EXP-019-coherent-mask/README|EXP-019]]: kohärentes Masken-Spektrum M0c gegen M0 (post hoc
  richtungsgleich, n. s.); Bestätigung ohne eigene Läufe aus EXP-018 Arm R + Baselines 18/19.
- [[experiments/EXP-020-data-switch/README|EXP-020]]: Datenwechsel F → G nach t Schritten, gleiches G-Budget:
  kausale Festlegungszeit der Frequenzwahl. Seeds 30–34.
- [[experiments/EXP-021-harmonic-misses/README|EXP-021]]: Bestätigung „Fehlgriffe = 2k der Ziele“ an 18 frischen Läufen
  (EXP-016 16–19, EXP-020 nur-F/nur-G), ohne eigenes Training.
- [[experiments/EXP-023-split-value/README|EXP-023]]: Eigene Wertematrix für Position 1 (Seeds 50–59, rand/copy/Baseline,
  3000 Schritte): folgt die finale Wahl dann M0 statt M0c? Kausaltest des Mechanismus.
- [[experiments/EXP-022-single-frequency/README|EXP-022]]: Erzwingt ein Ein-Frequenz-Split eine Ein-Frequenz-Lösung?
  Seeds 40–44, Arme S1/D1/S5, 6000 Schritte, funktionale Messung (`nanda`) am gespeicherten Modell.
**Post hoc (Sitzung 5):** Die natürliche M0-Konzentration eines Zufallssplits sagt die Grokking-Zeit nicht voraus.
**Mechanismus (Sitzung 5, post hoc, nach Codex-Angriff präzisiert):** Im ersten W_E-Gradienten interferieren linke und
rechte Eingabeposition frequenzweise so, wie es der Kreuzterm der Maske (M0c − M0) vorhersagt (18/18 Seeds, fremde
Maske −0.09); deshalb beschreibt M0c die Gradientenleistung besser als M0 (0.77 vs. 0.57). Ob M0c auch K besser
vorhersagt: EXP-019.
**Oberwellen (Sitzung 5, explorativ):** Alle 14 Nicht-Ziel-Frequenzen in EXP-016 (Seeds 10–15) sind fold(2k) eines Ziels.
Auch unter Zufallssplits enthält die W_E-Top-5 gehäuft (k, 2k)-Paare. In den Studienmodellen sind die schwächeren
2k-Glieder die unwichtigsten der Top-5 (Ablation 8/8), aber nicht null; Phasenkopplung nur in 3/10 Paaren deutlich;
sie erreichen die Top-5 meist erst nach dem Grokking. Vorhersage für EXP-016 Seeds 16–19 vorab festgelegt (Nachtrag b).
**Literatur (Sitzung 5):** N3 in anderer Form bekannt (Zhou et al. 2024, Frequency Principle, andere Aufgaben); bei
festem Split variiert K trotzdem über Inits (GitHub-Nachbau) → Split ist nicht die einzige Ursache.

**Weiter vorbereitet:** EXP-014 (Kreuzdesign), EXP-017 (RFM), EXP-013 (Lock-in-Kurve), EXP-011, EXP-001/002.
**Teilweise:** EXP-010 (1/10 Paare), EXP-003d (9/10 Baselines; Seed 18 gen 8775).

### Nächste konkrete Aktionen (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`, dann `sh lab/experiments/queue_s5.sh` im Hintergrund, beobachten.
2. EXP-016 ist fertig. Nach den Baselines 18/19: EXP-015/012 Phase 2 mit n = 10 nur berichten.
3. Nach den Smokes: `check_smoke.py` (EXP-020) und `result.json` des EXP-018-Smokes prüfen (`test_hash`, 2554 Testpaare).
4. Auswertungen: `EXP-021-harmonic-misses/analyze.py`, `EXP-022-single-frequency/analyze.py`, `EXP-018-split-speed/analyze.py`, `EXP-019-coherent-mask/analyze.py`, `EXP-014-split-vs-init/analyze.py`,
   `EXP-020-data-switch/analyze.py`, `EXP-010-init-swap/analyze.py` (je über den Wächter, wo `make_dataset` benutzt wird).
5. Außerhalb des Fensters: Theorie (AGF-Nutzen mit maskiertem Verlust ↔ M0c herleiten), Reverse-Kontrolle G → F für
   EXP-020 als eigenen Nachtrag erwägen, Google Scholar gezielt zu N6.

### Blocker

- **Aufgehoben 07:31:** Der Nutzer hat um 06:58 die Bash-Freigabe erteilt; die Warteschlange läuft. Der Eintrag darunter ist historisch.

- **Sitzung 5 (2026-09-26 05:52 Berlin):** Der Start von `sh lab/experiments/queue_s4b.sh` im Hintergrund wurde vom
  Auto-Mode-Klassifikator von Claude Code abgelehnt („Safety Bypass Flag“), obwohl jeder Lauf über `guarded_run.py`
  geht. Nach den Regeln der Ablehnung **nicht umgangen** (auch nicht über Einzelaufrufe). Die Warteschlange muss der
  Nutzer freigeben: entweder eine Bash-Berechtigungsregel für `sh lab/experiments/queue_s5.sh` (Nachfolger von `queue_s4b.sh`) bzw.
  `python lab/tools/guarded_run.py` hinzufügen oder die Warteschlange selbst starten. Bis dahin nur Denk- und Sucharbeit.

**Zyklus 12 (20:40–20:45): Regel 18a weiter.** Punkt 11: `lab/tools/night_program.py` ersetzt die GPU-Shell-Queues (Phasen über `parallel_queue.run_queue`, Auswertung nur nach rc 0, rc 3 stoppt alles, GPU-001 als Tor, Sperre, Status-Datei, `--dry-run`; Plan im Probedurchlauf geprüft, alle 1000 Datei-Verweise existieren; ausgeführt wurde nichts). Punkt 17: STATE von 274 auf 57 Zeilen, alte Fassung wörtlich im JOURNAL (Abschnitt „STATE-Archiv“). Punkt 5/18c: FINDINGS als Programm A/B/C mit P1–P3, Bestätigungsfamilie, reserviertem Block (Seeds 1000–1099, bisher unbenutzt) und Power aus Pilotstreuung (EXP-016 Δ_pow 8.41 ± 1.20). Astra-Befund zu 12/G = 19/F selbst nachgeprüft (einziges identisches Paar). *Offen vor 03:00:* Punkt 16 für EXP-043/044/045, CPU-Queue auf parallel_queue, Tests für den Fingerprint schreiben.

**Zyklus 13 (20:45–20:51): Regel 18a fast vollständig.** Punkt 16 für EXP-043/044/045 (EXP-044 prüft jetzt das exakte Budget t + 2000, der R-Arm von EXP-043 wird voll geprüft). Tests `lab/tests/test_freq_ban_fingerprint.py` geschrieben (Einheit + kleine CPU-Läufe; Lauf ab 03:00). Punkt 11 CPU: `night_program.py --cpu` für EXP-035/038/041/036/039/040/042 (Mindestrestzeiten wie in den Shell-Queues 7/9/19 min; `--threads 4` bleibt; Arbeiter aus J). Probedurchlauf: 263 Befehle, alle Dateien vorhanden; die 9 fertigen EXP-035-Läufe sind argumentgleich (werden übersprungen). **Nicht portiert:** EXP-034 (abhängige Kette) und Reste von queue_s5 (nach 18c zu sichten). Zweitprüfung der gemeinsamen Infrastruktur (freq_ban, Lader, Orchestrator) durch einen Subagenten gestartet (18c: Review bei Änderungen am gemeinsamen Trainer/Lader).

**Zyklus 14 (20:52–20:59): Zweitprüfung der gemeinsamen Technik (18c: Änderung an Trainer/Lader).** Subagent: kein Blocker/Hoch; Tests von Hand nachvollzogen (bestehen); alle 9 EXP-035-Läufe passen zur Legacy-Prüfung; Smoke-Prüfungen passen zu allen Trainern. Übernommen (05e6091): (M1) GPU-001 löscht bei erneuter Abnahme alte Gleichwertigkeitsläufe (sonst neues Siegel auf alten Daten); (M2) CPU-Arbeiter vor GPU-001 für J = 8 bemessen (1 Arbeiter) und CPU-Programm erst nach GPU-001 starten; (L3) leere, frische Sperrdatei gilt als belegt; (L4) „Zugriff verweigert“ gilt als lebender Prozess; (L6) unerwartete Fehler lassen nur den einen Versuch scheitern. *Nicht geändert:* (L5) Job-Objekt im Wächter (Nutzerdatei, in STATE für den Nutzer vermerkt); (L7) PID-Wiederverwendung bei der Programm-Sperre (selten, manuell lösbar); (L8) `parallel_queue.py` unversioniert (Nutzerdatei, vermerkt). Siegel und EXP-014 wurden während der Prüfung ergänzt; der Prüfer hat die aktuelle Fassung gelesen.

**Zyklus 15 (21:00–21:02, Planung Paket B und Power):** Literatur zu B: *What Can Grokking Teach Us About Learning Under Nonstationarity?* (arXiv 2507.20057, nur Zusammenfassung) behandelt das Überschreiben gelernter Repräsentationen bei Datenänderung und die Rolle der effektiven Lernrate; eine gezielte Frequenzsteuerung über die Trainingsmenge laut Zusammenfassung nicht. P3-Bestätigungsentwurf mit festgelegten Überlappungsstufen und beiden Richtungen im BACKLOG (Konkurrenzmodelle: Festlegung im Netz gegen Halt durch geteilte Paare). Nullkalibrierung Δ_pow aus gespeicherten Zufallssplit-Läufen: SD 0.48, |Δ| ≥ 1 in 4 % → Mindesteffekt 1 ≈ 2 Null-SD; grob 10–12 Seeds für 80 % Power bei Pilot-SD 1.2 (in FINDINGS). `night_report.py` zeigt jetzt die Statusdateien des Nachtprogramms. Plan für P2 (funktional, `causal_ablation.transformer_ablations`) im BACKLOG.

**Zyklus 16 (21:13–21:09): Paket A funktional (P2) vorbereitet.** Idee: Die ohnehin geplanten EXP-047-Läufe speichern ihre Modelle; [[experiments/EXP-051-functional-ablation/README|EXP-051]] entfernt dann ohne Nachtraining Zielfrequenzen aus W_E und misst die Test-Genauigkeit auf einer gemeinsamen Testmenge. Literatur zu B vertieft: Lyle et al. 2025 (effektive Lernrate) als drittes Konkurrenzmodell für die Persistenz. **Review-Blocker** zu EXP-051 selbst nachgeprüft (Zielanteil 0.76–0.89 → Energieabgleich unmöglich) und vor jedem Lauf behoben (gleiche erreichbare Energie, Oberwellen aus der Kontrolle ausgeschlossen, eigener Programmschritt; Nachtrag a). Selbsttest-Mathematik in reiner numpy-Nachrechnung bestanden. Alle alten GPU-Sub-Queues stillgelegt (nur noch `night_program.py`), damit kein Lauf ohne `--save-model` den Fingerprint von EXP-047 besetzt. *Lehre:* Eine Kontrolle „gleiche Menge anderswo“ zuerst auf ihre Machbarkeit an vorhandenen Daten prüfen.

### Abschlussbericht Sitzung 13 (Stand 21:10 Berlin; Auftrag §10)

- **Wichtigste Befunde (ohne Training):** (1) Rechnung erster Ordnung: Token-Häufigkeiten fallen aus dem ersten W_E-Gradienten exakt heraus (jede Gruppe, auch nicht-modular); gemeinsame Einbettung → M0c, getrennte W_in-Hälften → M0 (erklärt Sitzung-5-Messungen nachträglich). (2) Nullkalibrierung Δ_pow: SD 0.48 je Seed ohne Steuerung. (3) Literatur: He et al. 2026 und Marchetti et al. 2026 (Volltexte) stützen die vorläufige Neuheit von K2; Lyle et al. 2025 liefert mit der effektiven Lernrate ein Konkurrenzmodell für Paket B.
- **Vorbereitet (ungetestet):** EXP-048 (nicht-modulare Addition), EXP-049 (4× Breite), EXP-050 (M0c gegen M0, Kontrolle quadlm), EXP-051 (funktionaler Test P2 an EXP-047-Modellen); Regel 18a umgesetzt (Fingerprint/Sperre in freq_ban, GPU-001-Siegel und Wandzeit, gemeinsamer Lader, `night_program.py` GPU und `--cpu`, STATE auf einer Seite, FINDINGS als Programm A/B/C mit P1–P3 und Bestätigungsblock).
- **Durch unabhängige Prüfung vor jedem Lauf gefundene Fehler:** überschriebene Split-Dateien (EXP-048), entarteter Selbsttest, Schein-Δ durch Zahlengerade, NaN → falsches Urteil (alle Nachtauswertungen), verschluckte Durchsatz-Ablehnungen (GPU-001), Spiegelpaar-Confound (EXP-050), unmöglicher Energieabgleich (EXP-051), Wiederverwendung alter GPU-Prüfläufe nach Code-Änderung.
- **Offene Grenzen:** alles Neue ungetestet bis 03:00; EXP-034 nicht portiert; Codex ohne Guthaben; Job-Objekt-Hinweis zum Wächter an den Nutzer.
- **Reproduktion/Nächste Aktion:** STATE „Wiederaufnahme ab 03:00“ (Wächter-Abnahme → Tests → `night_program.py` → `--cpu` nach GPU-001).
- **Runner:** nächster Start laut runner-state.json 00:59 Berlin (22:59Z); Fenster heute Nacht ab 03:00.

## Sitzung 14 (2026-09-26 21:19 Berlin bis 00:19, außerhalb des Fensters; Läufe erst ab 03:00)

**Zyklus 1 (21:20–21:27, gemessen): K1 an unberührten Fällen, Vorhersage eingefroren ([[experiments/EXP-052-oos-mask-prediction/README|EXP-052]]).** *Frage:* Gilt K1 (M0 des Splits sagt das W_E-Spektrum voraus) auch bei add 97, mul 113 (Z_112 über den Logarithmus) und in der nicht-abelschen Gruppe D₅₉? Die 30 Zufallssplit-Läufe (R-Arme von EXP-043/046) fährt das Nachtprogramm ohnehin; noch keiner existiert. *Änderung:* `exp052.py` berechnet aus den Split-Dateien M0, M0c und das Häufigkeitsspektrum (reine numpy-Rechnung, kein Training, kein Test) und friert sie ein (`predictions.json` Commit 7c6492a, `predictions_d59.json` Commit 1d71c5d). Primär je Fall: ρ(M0 eigen) > ρ(M0 fremd), Permutation, Holm über drei; sekundär gepoolt M0c > M0 (erste Ordnung), M0 > E0, M0 > CNT. *Ergebnis bisher:* nur Vorbereitung; M0-Top-5 stimmen mit den von `make_split.py` notierten in 30/30 überein; M0 fremder Splits untereinander unkorreliert (Primärtest also nicht durch gemeinsame Struktur verzerrbar); ρ(M0, M0c) 0.69 (zyklisch) bzw. 0.77 (D₅₉) → S1 hat begrenzte Trennschärfe. *Prüfung:* Claude-Subagent (Codex ohne Guthaben), kein Blocker; Glob-Mehrdeutigkeit behoben, Rest in README Nachtrag a. *Entscheidung:* Selbsttest und Auswertung ab 03:00 von Hand (STATE Schritt 8), `night_program.py` bleibt unverändert. *Wert:* Das ist der erste Test im Labor, dessen Vorhersagen nachweislich (Commit) vor den Daten lagen; er prüft K1 und die Rechnung erster Ordnung gleichzeitig in drei neuen Gruppen.

**Zyklus 2 (21:27–21:33, gemessen): EXP-052 erweitert, P3-Konstruktion.** (a) EXP-052 um D₅₉ (Nachtrag a) und nicht-modulare Addition (Nachtrag b, k ≥ 6, trendbereinigt) erweitert, Vorhersagen vor den Läufen eingefroren (Commits 1d71c5d, 354e3dc); zweite Prüfung (Claude-Subagent): kein Blocker/Hoch, beide Dateien reproduzieren exakt; übernommen: Holm fest über vier (ausgefallener Fall p = 1), SystemExit statt assert, D₅₉-Gruppenprüfung (Nachtrag c). (b) *Frage:* Wie baut man für P3 Überlappungsstufen, ohne die Konkurrenzmodelle (Festlegung im Netz vs. geteilte Paare) mit anderen Größen zu vermengen? *Ergebnis (reine Rechnung):* Sequenzielles Ziehen (B aus dem Rest nach A) gibt B das Negativbild von A: F-Anteil im M0 von B 0.12–0.21 statt 0.09. Gleichverteilte geteilte Paare verdünnen die Steuerung (bei ω = 0.75 höchstens 0.12). Lösung [[experiments/EXP-053-p3-overlap-design/README|EXP-053]]: symmetrische Konkurrenzziehung plus ε je Stufe kalibriert → gleiche Steuerstärke 0.185, Kreuzanteile auf Zufallsniveau, gleiche M0c/Spiegelpaare, für ω ∈ {0, 0.2, 0.4}. *Entscheidung:* Konstruktion als Entwurf; Einfrieren nach der Pilotnacht (Streuung aus EXP-044/041). *Lehre:* Paar-Designs aus einem gemeinsamen Pool immer auf „zweiter Split trägt Ziele des ersten“ prüfen.

**Zyklus 3 (21:33–21:34 gemessen, Literatur Paket B):** *Frage:* Was sagt das ELR-Konkurrenzmodell (Lyle et al. 2025) konkret für P3 voraus? *Ergebnis (Volltext, HTML):* ELR = lr/‖θ‖ für Adam; in einem Grokking-Aufbau wie unserem löst eine ELR-Erhöhung Merkmalsumbau aus. Bei t = 150 sind die Normen in allen Überlappungsstufen gleich, die Überlappung trennt also nur (i) von (ii). *Entscheidung:* ELR-Arm (lr × c nach dem Wechsel) als Vorschlag in den P3-Entwurf ([[BACKLOG]]); Trainer-Option erst beim Einfrieren. Außerdem Neuheitssuche für EXP-052 (eNTK-Merkmalsidentifikation arXiv 2510.00468 ist nachträglich, nicht vorhersagend; Eintrag in der README).

**Zyklus 4 (Sitzung 14, bis 21:38 gemessen): Lücke zwischen P1 und den Pilot-Auswertungen.** *Frage:* Liefert die Pilotnacht die Streuung, die P1 zur Stichprobenplanung braucht? *Befund (Code-Sichtung):* P1 ist über das kontinuierliche Δ_pow formuliert, aber EXP-043, 046 und 047 entscheiden über den Top-5-Überlapp Δ; nur EXP-048/049/050 berechnen Δ_pow. Ohne Nacharbeit gäbe es für die neuen Gruppen keine Pilot-SD. *Änderung:* `lab/tools/pilot_power.py` (ungetestet, nur lesend): Δ_pow je gültigem F/G-Paar aus den gespeicherten Läufen (gemeinsamer Lader), Bootstrap-KI, benötigtes n per Simulation (wahres Mittel = Mindesteffekt 1, Pilot-SD, Vorzeichen-Permutationstest bei α 0.05/3, Normal- und Bootstrap-Variante). Vorab festgelegte Urteile bleiben unberührt. *Nächster Schritt:* nach der Nacht (STATE Schritt 9).

**Zyklus 5 (bis 21:39 gemessen): Notfallplan GPU und Split-Identifikation.** (a) STATE: Scheitert GPU-001, läuft nur Paket B (CPU); Paket A braucht dann einen Geräteparameter (13 Stellen `device="cuda"`), CPU-Dauer geschätzt. Nicht heute gebaut: ungetestete Änderungen an fünf Auswertungen kurz vor der Nacht wären riskanter als eine Nacht ohne Paket A. (b) *Neue Frage (N28):* Lässt sich die Trainingsteilmenge aus den Gewichten über die geschlossene M0-Formel wiedererkennen? Rein beschreibend an EXP-052 angehängt (Nachtrag d, vor jedem Lauf), Literatur: Abstammungs-Fingerabdrücke erkennen Basismodelle, nicht Teilmengen. Zweitprüfung von `pilot_power.py` und Nachtrag d gestartet.

**Zyklus 6 (Sitzung 14): Zweitprüfung `pilot_power.py`, S1-Trennschärfe.** (a) Simulation auf den 40 eingefrorenen Vorhersagen widerlegt meine eigene Behauptung, S1 (M0c gegen M0) sei wegen ρ(M0, M0c) ≈ 0.7 schwach: ist einer der beiden Treiber, erwartete Differenz ±0.16–0.24, Power ≈ 1 (EXP-052 Nachtrag e, LESART korrigiert). *Lehre:* Behauptungen über Trennschärfe erst simulieren. (b) Prüfer zu `pilot_power.py`: kein Blocker; übernommen: 1000 statt 200 Simulationen und n erst, wenn n und n + 1 die Power erreichen (erste verrauschte Kreuzung drückt n nach unten), zusätzlich n bei der oberen 80-%-Schranke der Pilot-SD (n wächst mit SD²), Warnung bei Pilotmittel < 1, stärkerer Selbsttest (Monte-Carlo- gegen exakten Vorzeichentest, Δ_pow mit mehreren Frequenzen); EXP-052-Identifikation konservativ bei Bindungen/NaN (Nachtrag f). Nicht übernommen: Herkunftsprüfung der summary.json von EXP-048/049 (die Nachtauswertungen schreiben sie frisch; vor dem Aufruf Zeitstempel ansehen, in STATE vermerkt). Beim Einarbeiten eigenen Rechenfehler im neuen Selbsttest gefunden (log 5/3 statt 5/2) und behoben.

**Zyklus 7 (Sitzung 14): Bestätigungsblock technisch vorbereitet; mul 113 treu/nicht-treu.** (a) `lab/tools/confirm_splits.py` (ungetestet): dieselben Konstruktionen wie die Piloten (zyklisch in Gruppenkoordinaten, D_n), aber jede Ziehung aus `SeedSequence([1000001, Versuch, Aufgabe, p, Seed, Arm, Zweck])` wie in FINDINGS festgelegt; F und G aus einem Strom (disjunkt per Konstruktion); schreibt Split-Dateien nur mit einem Manifest, das eine Commit-ID trägt, und überschreibt nie. Damit kann das Einfrieren von P1 nach der Pilotnacht ohne neuen Code geschehen. (b) EXP-052 Nachtrag g (beschreibend): Bei mul 113 = Z₁₁₂ sagt M0 keine Vorliebe für treue Frequenzen voraus (nicht-treu 0.56 in Top-5 und Leistung = Zufall 31/55); weicht das Netz ab, zeigt das eine Grenze der Theorie erster Ordnung.

**Zyklus 8 (Sitzung 14): Prüfung `confirm_splits.py`.** Prüfer (nur lesend, numpy): kein Blocker; Konstruktion bitgleich mit den Piloten, wenn man deren Zufallsgenerator einspeist (add 97, mul 113, D₅₉); Stärke der neuen Ströme an Seeds 1000–1009 wie in den Piloten (zyklisch 0.18–0.21, D₅₉ 0.26–0.28, jeweils 5/5 Ziele in der M0-Top-5). Übernommen: diese Regression in den Selbsttest; aufgabenspezifische Schwellen (bei D₅₉ lag 0.15 unter dem Zufallsanteil 0.17); Module per Pfad laden; `check_group`; Manifest-Tor prüft jetzt, dass die Datei unverändert in der genannten Commit-ID liegt und nur Seeds 1000–1099 nutzt; erst alle Namen prüfen, dann exklusiv schreiben; Namen mit Versuch und ε; die SeedSequence-Angabe in FINDINGS um Aufgabe und p präzisiert (vor jeder Nutzung). Beim Einarbeiten: langer Heredoc-Patch scheiterte an der Shell (nichts verändert), Datei stattdessen komplett neu geschrieben.

**Zyklus 9 (Sitzung 14): P1-Bestätigung als Code.** `lab/tools/confirm_p1.py` (ungetestet): aus dem eingefrorenen Manifest die Jobliste (freq_ban für add/mul, group_train für D_n, 2000 Schritte, Gerät laut Manifest) und die Auswertung (Δ_pow je Seed, exakter Vorzeichentest bis n = 20, Bootstrap-KI, Holm über P1–P3 mit p = 1 für noch fehlende Glieder; „bestätigt“ nur bei Holm-p < 0.05 **und** KI-Untergrenze > 0; Mindesteffekt 1 wird berichtet). Nach der Pilotnacht braucht das Einfrieren nur noch: Aufgaben und n (aus `pilot_power.py`) ins Manifest, committen, Commit-ID eintragen. Beim Schreiben selbst gefunden: CPU-Läufe von freq_ban tragen keinen Gerätezusatz im Namen, group_train braucht `--n`.

**Zyklus 10 (bis 21:50 gemessen): Wie stark verstärkt das Training kleine Daten-Asymmetrien? (Paket C, explorativ)** *Frage:* In Zufallssplits schwankt M0 über die Frequenzen nur um ≈ 9 % (Max/Median ≈ 1.2), trotzdem folgt W_E mit ρ ≈ 0.5. Wie groß ist die Verstärkung, und wächst sie wie bei einer linearen Instabilität? *Vorab (Commit):* EXP-052 Nachtrag h mit drei Lesarten (M1 nur erste Ordnung β < 1; M2 exponentiell β ∝ t; M3 Sättigung). *Exploration danach* an 10 gespeicherten EXP-018/020-Läufen (konstruierte Splits): β 0 → 1.4–1.8 (250) → 2.5–4.5 (2000), monoton in 10/10, weiter nach dem Grokking. Weder M1 noch reines M2; eher schnelle frühe Verstärkung plus langsame, stetige Kontrastzunahme (Weight Decay baut Ungenutztes ab). *Entscheidung:* an EXP-052 (Zufallssplits, feinere frühe Messpunkte) prüfen; bei Bedarf eigener Versuch mit dichten Messpunkten in den ersten 250 Schritten (Paket C, nach der Nacht). Keine Kernaussage, nur Exploration.

**Zyklus 11 (bis 21:52 gemessen): Kontinuierliche Persistenz aus gespeicherten Wechselläufen (Paket B, post hoc).** *Frage:* Liefert die Elastizität β ein kontinuierliches, trennscharfes Persistenzmaß, wie es Astra (Punkt 8) und P3 verlangen? *Ergebnis (EXP-020, Seeds 30–34, reine Nachrechnung):* π(t) = 0.15 / 0.38 / 0.72 / 1.00 / 1.01 / 1.04 für t = 10 / 25 / 50 / 150 / 400 / 1000; Spanne über Seeds höchstens 0.28. Glatter Übergang, Halbwert ≈ 30–35 Schritte, konsistent mit K4, aber ohne Schwellen. *Entscheidung:* π als Primärgröße-Kandidat für P3 in den BACKLOG (mit Auflage: reine Läufe bei gleicher Gesamtschrittzahl); Zeile in FINDINGS K4 als post hoc. *Grenze:* 73 % geteilte Paare in EXP-020 → Konkurrenzmodell (ii) nicht ausgeschlossen; das prüft EXP-053. Nur 5 Seeds, bereits gesehene Daten, keine Bestätigung.

**Zyklus 12 (bis 21:52 gemessen): Λ-Uhr oder Schrittuhr, kontinuierlich (post hoc, EXP-035).** *Frage:* Hängt die Persistenz an der aufsummierten Lernrate Λ oder an der Schrittzahl? *Ergebnis (EXP-035, Seeds 30/31 mit Warmup, reine Nachrechnung):* Schrittuhr klar verfehlt (t = 50: π 0.09/0.18 statt 0.69/0.89); Λ-Uhr trifft den frühen Teil (0.02 vs ≈ 0.02, 0.09 vs ≈ 0.08, 0.18 vs ≈ 0.12), unterschätzt aber später die Persistenz (0.56 statt ≈ 0.36 bei Λ = 25; 0.94 statt ≈ 0.72 bei Λ = 57, Seed 30). *Entscheidung:* als Exploration in EXP-035 dokumentiert; EXP-039 (vorab festgelegt, heute Nacht) entscheidet; π dort zusätzlich post hoc berechnen (gleiche Spektren). Kandidatenerklärung für die Abweichung: Schrittzahl zählt neben Λ (Adam, Weight Decay pro Schritt) → wäre eine Zwei-Uhren-Hypothese, erst nach EXP-039 festlegen.

**Zyklus 13 (bis 21:53 gemessen): Wettlauf statt Aufsummieren (post hoc, EXP-037).** Kontinuierliche Persistenz π für die Wechselläufe mit Verschränkung: 100 F-Schritte am Stück → π 1.01–1.04; dieselben 100 F-Schritte mit 100 G-Schritten verschränkt → 0.63–0.75 (25er-Blöcke) bzw. 0.52–0.60 (5er-Blöcke), 3 Seeds. Deutung (explorativ): Festlegung ist ein Wettlauf, in dem gleichzeitige Gegenschritte zählen, nicht die Summe der F-Schritte. Für P3 heißt das: Das Konkurrenzmodell „Festlegung im Netz“ muss zeitliche Reihenfolge enthalten; π ist trennscharf genug, um das mit wenigen Seeds zu sehen. In EXP-037 als post hoc dokumentiert.

**Zyklus 14 (Sitzung 14): Adversarielle Prüfung der Persistenz-Nachauswertungen.** Claude-Subagent hat alles nachgerechnet, keinen Code-Fehler gefunden, aber drei Aussagen zu Recht angegriffen, übernommen: (1) β ist ein Ziel-Maß (ohne die 10 Zielfrequenzen wird π Rauschen); die Übereinstimmung mit dem Log-Verhältnis ist keine unabhängige Bestätigung. (2) π > 1 bei t ≥ 400 ist ein Endschritt-Artefakt; richtig „π ≈ 1 ab 150“. (3) **Meine Λ-Uhr-Lesart war falsch:** Die frühen Punkte liegen unter dem Messraster (jede verzögernde Uhr sagt dort ≈ 0), an den trennscharfen Punkten passt Λ nicht; haltbar ist nur „Warmup verzögert, keine der beiden Uhren passt“. (4) EXP-037: Die richtige Null ist „nur der erste F-Block zählt“; die Beobachtung liegt darüber, spätere Blöcke tragen bei. Korrekturen als Abschnitte in EXP-020/035/037/039 und BEFUND-festlegung; Reproduktionsskript `posthoc_pi_other.py`. *Lehre:* Interpolierte Vergleichswerte unterhalb des Messrasters sind kein Beleg; vor einer Lesart prüfen, welche Punkte überhaupt zwischen den Modellen trennen.

**Zyklus 15 (bis 21:59 gemessen): Drei Uhren, vorab eingefroren für EXP-039 (Paket B/C).** *Frage:* Welche „effektive Zeit“ bestimmt die Festlegung: Schritte (γ = 0), aufsummierte Lernrate (γ = 1) oder dazwischen? *Änderung:* `EXP-039-lr-clock/predict_pi.py`: τ = Σ (lr_s/lr₀)^γ, π = EXP-020-Kurve bei τ; γ an EXP-035 angepasst (0.65; RMSE 0.08 gegen 0.12 Λ, 0.34 Schritt). Vorhersagen für alle sechs EXP-039-Zellen eingefroren (vor jedem Lauf); trennscharf sind c = 2/t = 25 (0.38 / 0.72 / 0.57) und c = 0.5/t = 50 (0.72 / 0.38 / 0.47). *Entscheidung:* nur beschreibend, das vorab festgelegte EXP-039-Urteil bleibt maßgeblich; Auswertung STATE Schritt 11. *Lehre aus Zyklus 14 angewandt:* Die Vorhersagen liegen auf trennscharfen Punkten, nicht unter dem Messraster.

**Zyklus 16 (bis 22:00 gemessen): Vorhersagen für Paket B an die Nachtversuche gehängt.** EXP-044 (GPU): beschreibende Lesarten (i) Festlegung im Netz → π wie EXP-020 (π(150) ≥ 0.9) gegen (ii) geteilte Paare halten → π deutlich darunter (dort nur ≈ 38 % geteilt), vor jedem Lauf in der README; Skript `pi_persistence.py`. EXP-039 (CPU): Auswertung `eval_pi.py` gegen die eingefrorenen drei Uhren. Beide ungetestet, laufen nach den Nachtversuchen (STATE Schritt 11).

**Zyklus 17 (bis 22:02 gemessen): N29, Steuerung über Loss-Gewichte (neu, offline).** *Frage:* Folgt aus der Theorie erster Ordnung, dass Gewichte statt Auswahl steuern? *Ergebnis (reine Rechnung):* gewichtetes M0 auf zufälligem 30-%-Split mit EXP-016-Gewichten: Zielanteil 0.179 (Auswahl 0.193, gleichverteilt 0.089); auf allen Paaren 0.986. *Entscheidung:* als N29 in NOVEL_DIRECTIONS; Umsetzung erst nach der Pilotnacht (Trainer-Option + Review), als Mechanismus-Test zu Paket A/P1 mit ausdrücklichem Konkurrenzmodell (Auswahl/Memorisierungsdruck). Außerdem EXP-052: gültige Fassung oben zusammengefasst, keine weiteren Nachträge; Erwartung für die Split-Identifikation simuliert (Nachtrag i).

**Zyklus 18 (bis 22:04 gemessen): Deckeneffekt im P3-Entwurf.** Die P3-Formulierung („nach Wechsel bei t = 150 überwiegen die F-Frequenzen“) misst in einem Bereich, in dem π schon bei 1.00 ± 0.04 liegt; Unterschiede zwischen Überlappungsstufen wären dort kaum sichtbar. Empfindlichster Punkt t = 25 (0.38 ± 0.08): Δπ 0.1 braucht ≈ 8 Seeds je Arm. Vorschlag im BACKLOG: primär t = 25, Anker t = 150. Außerdem N29-Selbstprüfung: Gewichte tragen die Ziele auch über die Häufigkeiten (Vollvariante 0.987) → Kontrolle wie EXP-047 nötig.

**Zwischenbilanz nach Regel 4 (Sitzung 14, 22:07):** *Gelernt:* (1) Ein kontinuierliches Persistenzmaß π macht die frühe Festlegung glatt und trennscharf sichtbar (EXP-020: 0.15/0.38/0.72/≈1); (2) meine erste Uhr-Deutung war falsch und wurde durch Gegenprüfung korrigiert (Warmup verzögert, keine einfache Uhr passt); (3) P3 bei t = 150 hätte an der Decke gemessen; (4) sequenzielles Ziehen von Split-Paaren hätte P3 verfälscht. *Wiederholen wir uns?* Viel Vorbereitung, aber jede mit eingefrorener, trennscharfer Vorhersage für die Nacht (EXP-052, EXP-039, EXP-044). *Messungen geeignet?* π ist ein Ziel-Maß (β fügt nichts hinzu); für nicht gesteuerte Fälle nicht anwendbar. *Nächste Annahme zum Angreifen:* dass W_E-Energie Nutzung bedeutet (EXP-051, P2).
*Entscheidung, die Sitzung vor der Deadline zu beenden:* Alles Pflichtige vor 03:00 ist erledigt und geprüft; weitere Punkte wären Kleinkram ohne Frage (Regel 13: kein Beschäftigungsprogramm). Das Nutzungskontingent ist in der Laufnacht ab 03:00 wertvoller (Abnahme, Beobachten, Auswerten). Der nächste Runner-Start (00:54) ist davon unabhängig.

### Abschlussbericht Sitzung 14 (Stand 22:07 Berlin; Auftrag §10)

- **Wichtigste Befunde (ohne Training, post hoc an gespeicherten Läufen, explorativ):** kontinuierliche Persistenz π nach Datenwechsel (EXP-020, 5 Seeds): 0.15 / 0.38 / 0.72 / 1.00 bei t = 10 / 25 / 50 / 150, enge Streuung; mit Warmup verzögert, aber weder Schritt- noch Λ-Uhr passen (nach Gegenprüfung korrigiert); gleiche F-Schritte verschränkt mit G halten nur 0.52–0.75, mehr als „nur der erste Block zählt“ vorhersagt. Offline: Loss-Gewichte könnten die Frequenzen fast so stark steuern wie die Auswahl (N29, Häufigkeits-Confound beachten).
- **Vorab eingefroren (Commits vor jedem Lauf):** EXP-052 (40 Vorhersagen aus dem Split für die R-Arme von EXP-043/046/048, vier Fälle, Holm), Uhr-Vorhersagen für EXP-039 (drei Modelle), Lesarten (i)/(ii) für EXP-044.
- **Vorbereitet (ungetestet):** `pilot_power.py`, `confirm_splits.py`, `confirm_p1.py` (Bestätigungsblock, manifestgesteuert), EXP-053 (Überlappungskonstruktion für P3, kalibriert), Auswerteskripte für π (EXP-039, EXP-044). Alle von unabhängigen Prüfern (Claude-Subagenten; Codex ohne Guthaben) gesehen, Befunde eingearbeitet.
- **Offene Grenzen:** alles Neue ungetestet bis 03:00; π nur an gesteuerten Splits sinnvoll; Post-hoc-Ergebnisse an 1–5 Seeds sind keine Bestätigung; GPU-Abnahme offen (Notfallplan in STATE).
- **Reproduktion:** `python lab/experiments/EXP-020-data-switch/posthoc_beta_persistence.py`, `.../posthoc_pi_other.py`, `python lab/experiments/EXP-039-lr-clock/predict_pi.py` (eingefroren, verweigert Überschreiben), `python lab/experiments/EXP-052-oos-mask-prediction/exp052.py --predict` (dito).
- **Nächste Aktion:** STATE „Wiederaufnahme ab 03:00“ (Wächter-Abnahme → Tests inkl. vier neuer Selbsttests → `night_program.py` → `--cpu` nach GPU-001 → Auswertungen, dann eingefrorene Vorhersagen prüfen).
- **Runner:** nächster Start laut runner-state.json 00:54 Berlin (22:54Z); Läufe erst ab 03:00.

## Sitzung 15 (2026-09-26 22:39 Berlin bis 01:39, außerhalb des Fensters; Läufe erst ab 03:00)

**Zyklus 1 (ab 22:41, Paket B, post hoc an gespeicherten Läufen, explorativ): Wächst der F-Vorsprung unter G-Training oder zerfällt er?**
*Frage:* π(t) aus Sitzung 14 misst die Persistenz nur am Ende (t + 2000). P3 definiert „festgelegt“ als „nach B Schritten persistent“, also
hängt das Urteil davon ab, wie π mit der Dauer s des G-Trainings wandert. *Vorab notiert (vor der Rechnung):* Lesart V (Verstärkung,
AGF/N22: aktive Merkmale bleiben, reich wird reicher) → π(s) steigt mit s; Lesart Z (Zerfall, Prägung wird langsam überschrieben) → π(s) fällt
mit s, dann hängt P3 empfindlich an B; Lesart K (konstant) → π nach kurzer Übergangszeit flach, B unkritisch. *Messung:* π(t, s) mit den
Spektren, die alle 250 Schritte gespeichert sind; Normierung je Seed mit den reinen F- und G-Läufen (EXP-018) beim selben globalen Schritt.
*Ergebnis (22:42, `posthoc_pi_trajectory.py`):* π(t, s) ist von Schritt 250 bis zum Ende praktisch konstant (Mittel über Seeds z. B.
t = 25: 0.35 → 0.38, t = 50: 0.73 → 0.71; Drift je Seed ≤ 0.10), während der Kontrast D_F − D_G der reinen Läufe ≈ 2.3-fach wächst.
Lesart K, nicht V oder Z. *Weiter (22:44, `posthoc_window_model.py`):* Ein Einparameter-Fenstermodell (jeder der ersten T* ≈ 69 Schritte
zählt gleich, π = F-Anteil darin) passt auf die EXP-020-Kurve und sagt die EXP-037-Verschränkungsarme voraus (RMSE 0.09; exponentielle
Gewichte, τ ≈ 45: 0.05; Null „nur der erste F-Block“: 0.37). *Folgerung (22:45, `posthoc_clock_crossover.py`, aus Split-Dateien):* Unter
reinem Takt mit linearer Überlagerung verschiebt sich die Top-5-Kreuzung trotzdem mit der Stärke von G (eps 2 → 32–40, beobachtet
(25, 50] in 5/5; eps 8 → 46–54; eps 1 → 14–24). Die in EXP-042 vorab festgelegte Lesart „reine Uhr → gleiches Fenster“ stimmt für das
Top-5-Maß also nicht. Normiertes π trennt: EXP-042 Nachtrag b, vor jedem Lauf eingefroren (Commit e9a9c56), `pi_window.py`.
*Gegenprüfung (Claude-Subagent, Codex ohne Guthaben), übernommen:* (1) β ist linear im Log-Spektrum, π daher exakt invariant gegen jede
gemeinsame affine Abbildung des Log-Spektrums: „flach ab 250“ heißt „gemeinsame Umskalierung“, nicht „eingefroren“; proportionales
Verstärken (reich wird reicher) sieht genauso aus. 250 ist nur eine Obergrenze. „Keine Richtung“ zu stark: bei t = 150 fallen 4/5 leicht;
die Drift bei t = 10 erzeugt einen Großteil der Endstreuung. (2) Fenstermodell schwach belegt: T* aus drei Innenpunkten; alt5 sagt für
jedes T* 0.50 voraus, prüft also nichts; der Null-Vergleich war ein Strohmann (konstant 0.5: RMSE 0.14 gegen 0.09). Haltbar nur:
„verträglich mit einem frühen Fenster von ≈ 50–100 Schritten“. (3) π = t/T* gilt nur bei additiver Überlagerung im Log-Spektrum;
Sättigung kann eine O-Lesart vortäuschen. (4) Zwei Fehler in `pi_window.py` (kein Mindest-Seed-Schutz, TypeError bei fehlendem Schritt)
behoben, Nachtrag c. Geprüft ohne Befund: `pis` reproduziert `posthoc_beta_persistence.json` exakt (4 Seeds).
*Entscheidung:* EXP-042 Nachtrag b/c bleiben beschreibend. Die wichtigste haltbare Folge ist methodisch: **Top-5-Kreuzungen hängen an der
Stärke des zweiten Splits, auch ohne dass sich das Fenster verschiebt.** Deshalb soll P3 mit π statt mit Top-5 formuliert werden; der
Befund stützt die BACKLOG-Entscheidung π/t = 25. Nachtrainingsbudget B: π(250) ≈ π(Ende) innerhalb ≈ 0.1, also für π kaum kritisch
(Einschränkung (1)). *Neuheit:* Suche 22:48 („early training data influence integration window superposition …“; „grokking … switching
training data early steps frequency selection persists“). Nächstverwandt: „The Order Is The Message“ (https://arxiv.org/abs/2603.25047,
Datenreihenfolge prägt die Fourier-Darstellung; kein Wechsel, kein Fenstermodell), Critical Learning Periods (https://arxiv.org/abs/1711.08856).
Integrationsfenster für die Frequenzwahl: nicht gefunden (vorläufig), als N30 notiert.

**Zyklus 2 (22:50–22:52 gemessen, Paket B): Lesarten für EXP-041 vor der Nacht geschärft.** *Frage:* Trifft der Stärke-Confound aus Zyklus 1
auch EXP-041 (schwacher Zufallssplit R gegen starken Split E)? *Ergebnis:* Nur bei t = 150, und dort trennt P41b sogar drei Modelle:
Schrittfenster (N30) → *geprägt*, Amplitudenschwelle (H40) → *gemischt*, H42 → *überschrieben*. Als Nachtrag b vor jedem Lauf eingetragen,
beschreibend. Außerdem BACKLOG P3: π bleibt Primärgröße, π nach 250 G-Schritten als billiger Zweitpunkt.

**Zyklus 3 (22:52 gemessen, Paket B, post hoc, explorativ): Bleibt nur π stabil oder die ganze Spektrumsform?** (Prüfpunkt 1 der Gegenprüfung aus Zyklus 1)
*Messung (`posthoc_shape_stability.py`, alle 56 Frequenzen, Seeds 30–34):* Korrelation des Log-Spektrums zwischen Schritt 250 und Ende ist in
Wechselläufen (0.82–0.90 im Mittel) so hoch wie in reinen Läufen (0.83–0.84); die Top-5 behalten 3.8–4.6 von 5 (rein 3.6–3.8). Die Ähnlichkeit
zum Endspektrum „nur G“ wächst in der G-Phase **nicht**: t = 25 0.57 → 0.59, t = 50 0.15 → 0.12, t = 150 −0.07 → −0.08; nur t = 10 zieht leicht
nach G (0.73 → 0.83). *Deutung:* Nach Schritt 250 verändert sich das Spektrum weiter, aber in gleichem Maß wie ohne Wechsel und ohne Zug
Richtung G. Damit gilt die Stabilität nicht nur für die Projektion π, sondern auch für die Gesamtform (Einwand 1 teilweise ausgeräumt; „eingefroren“
gegen „proportional verstärkt“ bleibt ununterscheidbar, beides heißt aber: die Datenwahl nach 250 Schritten ändert die Mischung kaum).
Ausnahme t = 10: dort wirkt G noch nach Schritt 250 (passt zu einem Fenster, das bei so wenig F-Vorlauf später schließt, oder zu Init-Anteilen).
*Entscheidung:* als Exploration in EXP-020 und FINDINGS (K4, post hoc); dichte Spektren in den ersten 250 Schritten bleiben der eigentliche Test (N30).

**Zyklus 4 (22:53 gemessen, Paket B): N30 an unberührten Inits, vorab festgelegt ([[experiments/EXP-054-window-oos/README|EXP-054]]).**
*Frage:* Gilt das Fensterbild aus Zyklus 1–3 auch bei neuen Inits? EXP-036 (CPU-Nacht) nutzt die EXP-020-Splits mit neuen Inits 130–134, 230, 231
und speichert dichte Spektren 5 … 200. *Änderung:* eigener, reiner Auswerteversuch EXP-054 (statt sechstem EXP-036-Nachtrag, Regel 15b):
A = Fenster übertragbar (π_Ende bei t = 10/25/50 höchstens 0.12 neben 0.145/0.362/0.725, T* nicht neu angepasst), B = Setzschritt (Median ≤ 150
„früh gesetzt“, > 200 „später gesetzt“). `n30_window.py` ungetestet, Speicherplan geprüft (SPECTRUM_EVERY = 250 plus `--spectra-at`, Endspektrum).

**Zyklus 5 (22:56–22:59 gemessen, Technik mit Forschungszweck): CPU-Ersatzweg für Paket A, falls GPU-001 scheitert.**
*Frage:* Verliert Paket A (Regel 15c, Verallgemeinerung) eine ganze Nacht, wenn die GPU-Abnahme scheitert (AMD: natives Windows „No ML training
support“)? Bisher ja: 13 Programmstellen und 11 Auswertungen setzten `cuda` fest. *Zunächst* (22:56) verworfen, weil die CPU heute Nacht ohnehin
mit Paket B belegt ist. *Dann doch gebaut*, weil es ohne Risiko für die Nacht geht und spätere Nächte sonst Fensterzeit dafür verlieren:
`lab/tools/paket_a_device.py` (LAB_PAKET_A_DEVICE, Standard `cuda`), Auswertungen EXP-043–052 lesen nur Läufe des gewählten Geräts (Regel 16d),
`night_program.py --paket-a-cpu` (globales Python, `--device cpu --threads 1`, J = `--cpu-workers`, Standard 3, ohne GPU-001-Tor).
*Prüfung:* `--dry-run` vor/nach der Änderung für GPU- und CPU-Programm bis auf Zeitstempel identisch; neuer Plan sieht richtig aus.
Unabhängige Codeprüfung (Claude-Subagent) läuft. *Nebenbei gefunden und behoben:* Python-`write_text` und Git-Bash-`sed -i` hatten in dieser
Sitzung Zeilenenden verändert (JOURNAL ganz auf LF, neue Dateien CRLF); alles auf den Stand vor der Sitzung zurückgesetzt (Commit „restore
pre-session line endings“). *Lehre:* Dateien byteweise schreiben oder Zeilenende vorher prüfen; kein `sed -i` auf CRLF-Dateien.
*Dauerabschätzung:* Paket A auf der CPU ≈ 300 Läufe, bei J = 3 und einem Thread je Lauf grob 10+ h → nur über mehrere Fenster (Wiederaufnahme per Fingerprint).
*Codeprüfung zu Zyklus 5 (Claude-Subagent, 23:02):* **ein Blocker, gefunden vor jedem Lauf:** Meine neuen EXP-043-Muster ließen den Aufgabenzusatz
`_{task}{p}` weg, den `freq_ban.py` vor den Gerätezusatz setzt: Die EXP-043-Auswertung hätte **auch im heutigen GPU-Standardlauf** jede Zeile als „fehlt“
gewertet (der Selbsttest prüft keine Verzeichnisnamen, hätte es also nicht gemerkt). Behoben (`…_{stem}_{task}{p}{FB_SUFFIX}`) und mit fnmatch
für beide Geräte geprüft: jedes Muster trifft sein Gerät und nie das andere. Übernommen außerdem: tote `run_dir`-Funktion in EXP-043 gerätesicher,
`--paket-a-cpu` zusammen mit `--cpu` abgelehnt. Geprüft ohne Befund: EXP-044/045/046–052-Muster, `Expect.device`, Umgebungsvariable erreicht
alle Kindjobs (kein `env=` in parallel_queue/guarded_run), Pläne GPU/CPU unverändert. Hinweis: `--paket-a-cpu` nimmt die GPU-Sperre und darf
neben `--cpu` laufen; dann Threadsumme ≤ 12 beachten (3 × 1 + Worker × 4). *Lehre:* Bei jeder Änderung an Lauf-Mustern den tatsächlichen
Namen aus dem Trainer nachbauen und per fnmatch prüfen, bevor ein Plan-Diff als Beleg gilt; der Plan-Diff sieht Auswertungen nicht.

**Entscheidung, die Sitzung vor der Deadline zu beenden (23:03):** Alles, was vor 03:00 ohne Läufe sinnvoll war, ist erledigt und geprüft.
Weitere Punkte wären Nachrechnungen an bereits ausgeschöpften Daten (EXP-020/037) ohne neue Frage (Regel 13: kein Beschäftigungsprogramm).
Das Kontingent ist ab 03:00 wertvoller (Abnahme, Beobachten, Auswerten). Der nächste Runner-Start (02:14) hängt nicht davon ab.

### Abschlussbericht Sitzung 15 (Stand 23:03 Berlin; Auftrag §10)

- **Wichtigste Befunde (post hoc an gespeicherten Läufen, explorativ, Seeds 30–34):** (1) Die F/G-Mischung nach einem Datenwechsel (π) und die
  ganze Spektrumsform ändern sich nach Schritt 250 kaum, obwohl der Kontrast ≈ 2.3-fach wächst. Nach der Gegenprüfung heißt das nur
  „gemeinsame Umskalierung“, nicht „eingefroren“. (2) Ein frühes Integrationsfenster (≈ 50–100 Schritte) ist verträglich mit EXP-020 und EXP-037,
  aber schwach belegt (eine Konstante 0.5 passt EXP-037 fast so gut). (3) **Methodisch:** Unter reinem Takt verschiebt sich die Top-5-Kreuzung
  mit der Stärke des zweiten Splits. Die vorab festgelegte Lesart von EXP-042 („reine Uhr → gleiches Fenster“) war deshalb für das Top-5-Maß falsch.
  Korrigiert vor dem Lauf: π trennt beide Lesarten.
- **Vorab eingefroren (vor jedem Lauf):** EXP-042 Nachtrag b/c (π-Lesarten C/O), EXP-041 Nachtrag b (drei Modelle für P41b), neuer Auswerteversuch
  [[experiments/EXP-054-window-oos/README|EXP-054]] (Fenster an den neuen Inits von EXP-036: A Übertragung, B Setzschritt).
- **Technik:** CPU-Ersatzweg für Paket A (`night_program.py --paket-a-cpu`, `LAB_PAKET_A_DEVICE`). Die Standardpläne bleiben unverändert (Plan-Diff).
  Einen Blocker, der auch die GPU-Auswertung von EXP-043 getroffen hätte, fand die Prüfung vor jedem Lauf. Zeilenenden der Notizen wiederhergestellt.
- **Offene Grenzen:** alles Neue ungetestet bis 03:00; π sieht gemeinsame affine Abbildungen nicht; C/O-Lesarten erkennen mit 4 Seeds nur Verschiebungen ≳ 0.15–0.2.
  Dichte frühe Spektren (EXP-036/039/040) sind der eigentliche Test von N30.
- **Reproduktion:** `python lab/experiments/EXP-020-data-switch/posthoc_pi_trajectory.py`, `…/posthoc_window_model.py`, `…/posthoc_clock_crossover.py`,
  `…/posthoc_shape_stability.py` (reine Rechnung auf gespeicherten Spektren).
- **Nächste Aktion:** STATE „Wiederaufnahme ab 03:00“. Neu dort: EXP-054 nach EXP-036, `pi_window.py` nach EXP-042, CPU-Weg für Paket A bei gescheitertem GPU-001.
- **Runner:** nächster Start laut runner-state.json 02:14 Berlin (00:14Z); Läufe ab 03:00.

## Sitzung 16 (2026-09-26 23:39 Berlin bis 02:39, außerhalb des Fensters; Läufe erst ab 03:00)

Start 23:39: kein STOP, Fenster zu (`--check` Exit 3), keine Python-/Trainingsprozesse, Branch lab/research sauber bis auf die Nutzerdateien.
Die ganze Sitzung liegt vor 03:00, also keine Läufe und keine Tests (auch keine Selbsttests).

**Zyklus 1 (Astra Punkt 5, letzter offener Rest: gekreuzter Split×Init-Block).** *Frage:* Braucht der Bestätigungsblock einen Kreuzblock?
Und wie sieht er aus, ohne die P1-Inferenz zu verwässern? *Prüfung des Ist-Designs (`confirm_p1.py`):* Jede P1-Einheit trainiert F und G mit derselben
Init (`--seed s`). Ziele und beide Splits kommen aus getrennten SeedSequence-Strömen, Δ_pow ist eine Doppeldifferenz innerhalb der Einheit.
Die Richtung „andere Splits, gleiche Init“ ist damit schon gekreuzt. Es fehlt die Richtung „gleicher Split, andere Init“, und genau die trennt
„Split steuert“ von „dieses Seed-Paket wirkt“ (Astra). *Änderung (vor jedem Lauf festgelegt):* optionales Manifestfeld `cross`: Die ersten 5 Seeds von
add 113 trainieren ihre F/G-Splitdateien zusätzlich mit den Inits s + 200 und s + 300 (reserviert 1200–1399; 20 Zusatzläufe, keine neuen Splits).
Auswertung `cross_block`: Δ_pow je (Einheit, Init), Varianzanteile als einfaktorielle Zufallseffekte (σ²_Einheit = Split-Paar + Ziele gegen
σ²_Init inkl. Wechselwirkung, nicht trennbar), Anteil Δ > 0, Minimum je Einheit. Die Lesart ist fest: „stabil über Inits“ bei ≥ 90 % Δ > 0 und
Init-SD < Mittel/2, „init-abhängig“ bei < 75 % oder Init-SD ≥ Mittel, sonst „gemischt“; < 4 gültige Einheiten: nicht auswertbar. Das Ergebnis ist
**sekundär und beschreibend**, steht nur unter `cross_secondary` und gehört nicht zur Holm-Familie. P1 zählt weiter ein Δ je Seed
(Astra: wiederholte Inits desselben Splits sind keine unabhängigen Splitreplikationen). Selbsttest erweitert (Jobs, Ablehnungen, Varianzformeln, Lesart).
**Ungetestet** (Selbsttest ab 03:00). *Zweitprüfung (Claude-Subagent, nur lesend):* Selbsttest von Hand nachgerechnet (besteht). Run-ID-Muster
passt zu `freq_ban.py` (`EXP-016_baseline_seed<init>_thr<n>_<stem>[_dev…]`), ohne Kollision mit den Primärläufen. `Expect(seed=init)` ist konsistent,
die ANOVA-Formeln stimmen, und P1/Holm bleiben unberührt. Kein Befund. *Nebenbei:* Ein `sed -i` hat die Datei auf LF umgestellt (die bekannte Falle);
CRLF ist byteweise wiederhergestellt, und der Diff enthält nur die inhaltlichen Zeilen. *Ergebnis:* Astra 5 ist im Design vollständig. Das Manifest
beim Einfrieren muss `cross` enthalten (STATE Schritt 9). *Entscheidung:* EXP-014 (CPU-Nacht) bleibt Exploration und entscheidet über den Kreuzblock
nicht mehr. Der Block kommt unabhängig davon, weil er billig ist (20 GPU-Läufe) und die Trennung direkt am Bestätigungsmaß Δ_pow zeigt.

**Zyklus 2 (vorausschauende Prüfung, P3-ELR-Arm).** *Frage:* Lässt sich die geplante Trainer-Option für den ELR-Arm (lr × c nach dem Wechsel) später
einbauen, ohne bestehende Läufe zu stören? *Ergebnis (Code gelesen):* `fingerprint()` hasht alle Felder aus `FINGERPRINT_ARGS` samt Wert. Ein neues
Argument dort, auch mit Standardwert, ändert also den Fingerprint jedes Laufs. Fertige Läufe mit gleichem Namen führen dann zum Fehler statt zum
Überspringen, und die Wiederaufnahme der Nachtprogramme bricht ab. *Entscheidung:* heute Nacht nichts am Trainer ändern. Bauregel in BACKLOG und STATE:
nur bei Abweichung vom Standard aufnehmen, mit einem Selbsttest „Fingerprint eines Standardlaufs unverändert“.

**Entscheidung, die Sitzung vor der Deadline zu beenden (23:47):** Der letzte offene Designpunkt aus 18a/Astra (5, Kreuzblock) ist erledigt.
Weitere Arbeit vor 03:00 wäre Nachrechnen an ausgeschöpften Daten oder eine Trainer-Änderung, die die heutige Abnahme gefährdet.
Der nächste Runner-Start (03:14) hängt nicht davon ab.

### Abschlussbericht Sitzung 16 (Stand 23:47 Berlin; Auftrag §10)

- **Befunde:** keine neuen Messungen (Fenster zu). Design: Der gekreuzte Split×Init-Block für die P1-Bestätigung ist festgelegt und gebaut
  (sekundär, feste Lesart, 20 Zusatzläufe). Damit ist Astra-Punkt 5 im Design vollständig. Außerdem eine Bauregel für neue Trainer-Argumente
  (Fingerprint-Stabilität).
- **Offene Grenzen:** `confirm_p1.py` ist nicht im Fenster getestet (Selbsttest ab 03:00 über den Wächter, schon in STATE Schritt 3; siehe Vorfall unten). Der Kreuzblock trennt Init von
  Init×Split-Wechselwirkung nicht.
- **Reproduktion:** `python lab/tools/confirm_p1.py --selftest` (nur im Fenster, über `guarded_run.py`).
- **Nächste Aktion:** STATE „Wiederaufnahme ab 03:00“ unverändert, dazu `cross` ins P1-Manifest beim Einfrieren.
- **Runner:** nächster Start laut runner-state.json 03:14 Berlin (01:14Z); Läufe ab 03:00.

**Vorfall (23:47, Regelverstoß, unbeabsichtigt):** Beim Schreiben dieses Abschlussberichts habe ich ein Bash-Heredoc ohne Anführungszeichen benutzt. Die Shell hat den Backtick-Ausdruck `python lab/tools/confirm_p1.py --selftest` aus dem Berichtstext **ausgeführt**: außerhalb des Fensters (vor 03:00, Regel 18) und ohne `guarded_run.py`. Der Selbsttest ist reine Rechnung. Er hat „selftest ok“ ausgegeben, keine Datei geschrieben (`git status` unverändert, kein `lab/confirm/`) und keinen Prozess hinterlassen. Dieses Ergebnis zählt **nicht** als Abnahme. Der Selbsttest läuft ab 03:00 regulär über den Wächter. Die übrigen Backtick-Stücke waren keine gültigen Befehle und haben nichts ausgeführt. Die Berichtstexte sind oben korrigiert. *Ursache:* die bekannte Falle aus STATE („Heredocs mit Backticks nur mit <<'EOF'“), die ich hier missachtet habe. *Lehre:* Notiztexte nie über ein Heredoc mit Variablen-Ersetzung schreiben, sondern als Datei (Write-Werkzeug) und dann byteweise anhängen.

## Sitzung 17 (2026-09-27 00:19 Berlin bis 03:19, Fenster erst ab 03:00)

Start 00:19 (gemessen, `--check`): kein STOP, Fenster zu (Exit 3), keine Python-/Trainingsprozesse, Branch lab/research sauber bis auf die Nutzerdateien.
Die Sitzung hat nur 03:00–03:19 im Fenster. Plan: bis 03:00 Vorab-Prüfung des Nachtcodes (nur lesend) und Literatur-Nachsuche;
03:00–03:09 Wächter-Abnahme und Tests über den Wächter (STATE Schritte 1–3). Das Nachtprogramm startet erst die nächste Sitzung:
Jeder Job erhält als harte Grenze die Restzeit bis zur Sitzungsdeadline (`guarded_run.py`), ein Start um 03:05 würde also an der Deadline 03:19 abgebrochen.

**Zyklus 1 (Betriebssicherheit der STOP-Abnahme).** *Frage:* Kann die Wächter-Abnahme mit angelegter `lab/STOP` den Runner abschalten?
`tick.ps1` setzt bei vorhandener STOP-Datei `status = stopped` und deaktiviert die geplante Aufgabe (Zeilen 162–168). Eine gestoppte Automatisierung
dürfte ich nicht selbst wieder einschalten (Auftrag §9), das wäre das Ende des Dauerbetriebs. *Prüfung:* Die Aufgabe „GROKVERSE-Lab-Runner“ hat
`MultipleInstances = IgnoreNew` (Takt 10 min, Ausführungsgrenze 4 h). Die Tick-Instanz, die diese Sitzung gestartet hat, läuft, solange `claude` läuft
(Status „Running“). Während der Sitzung feuert also kein weiterer Tick. *Ergebnis:* Die STOP-Abnahme ist innerhalb der Sitzung sicher, **wenn** STOP
vor dem Sitzungsende wieder gelöscht ist. Das Löschen folgt sofort nach Exit 3 (Poll-Intervall des Wächters 5 s), und ich prüfe danach, dass die Datei weg ist.
*Entscheidung:* Abnahme wie geplant, spätestens 03:08 beginnen; nach 03:10 keine STOP-Abnahme mehr, damit ein Fehler nicht ins Sitzungsende fällt.

**Zyklus 2 (Literatur-Nachsuche zu K2/K4/N29/N30, bis 00:24).** *Frage:* Ist seit der Suche vom 26.09. etwas erschienen oder übersehen worden, das K2 (Split steuert
die Frequenzen), K4 (frühe Festlegung), N29 (Loss-Gewichte) oder N30 (Integrationsfenster) schon beantwortet? *Vorgehen:* Claude-Subagent, 16 Suchanfragen, meist Abstracts;
drei Abstracts und den LeDoux-Volltext habe ich selbst abgerufen. *Ergebnis:* nichts gefunden, das eine der Fragen beantwortet (vorläufig, Suche vom 2026-09-27).
Wichtig für die Einordnung: He et al. 2026 (2602.16849) erklären die Frequenzwahl allein über die Init („initial spectral magnitude and phase alignment“), den Split behandeln
sie nicht; K2 ist dazu die Gegenposition. LeDoux 2026 schreibt im Abstract „regardless of … training set composition“, variiert die Zusammensetzung laut Volltext aber
gar nicht (gleiche Mengen, Mini-Batch, p = 9973). Das ist also kein Gegenbeleg zu K2, eröffnet aber eine offene Konfliktfrage → neuer Kandidat N31 (Reihenfolge gegen
Zusammensetzung) in [[NOVEL_DIRECTIONS]], nicht geplant, erst nach der Pilotnacht gegen FINDINGS priorisieren. Nicht selbst geprüfte Angaben des Subagenten sind dort
als solche markiert. *Entscheidung:* FINDINGS unverändert (K2-Literaturspalte nennt He et al. schon); keine neuen Versuche vor der Pilotnacht.

**Zyklus 3 (Vorab-Prüfung des 03:00-Codes, nur lesend, bis 00:31).** *Frage:* Gibt es im ungetesteten Nachtcode (Wächter, Tests, `night_program.py`, GPU-001, Analyseskripte)
Fehler, die das Fenster verschwenden würden? *Vorgehen:* Claude-Subagent, nur lesend (Pfade, CLI-Flags, Run-ID-Muster gegen Analyse-Globs, result.json-Schlüssel,
Reihenfolge, Wiederaufnahme, Tests von Hand nachvollzogen). *Ergebnis:* Auf dem Hauptpfad nichts, was abstürzt oder Daten verfälscht (≈ 700 Splitdateien vorhanden,
Flags und Muster passen). Bestätigt und von mir im Code nachgesehen:
1. Die Sitzungsdeadline ist harte Grenze jedes Jobs (`guarded_run.py` 76–78). Ein dort abgebrochener Job endet mit 124 und galt bisher als *Fehlschlag*. Das Experiment wurde
   als „failed“ markiert. Bei GPU-001 hieß das „GPU-001 not passed: no GPU runs“, obwohl nur die Zeit fehlte. **Behoben in `night_program.py`** (nicht im Nutzer-Wächter):
   `Night.jobs` liest die summary.json der Queue, und ein Exit 124 wird zu `Refused` (Programm stoppt mit 3, Wiederaufnahme mit demselben Befehl). Begründung:
   `parallel_queue.py` übergibt kein `--job-minutes`, 124 kann also nur Deadline oder 13:00 bedeuten.
2. Eine Wiederaufnahme hat GPU-001 komplett neu gemacht, sobald eine Stufe fehlte. **Behoben:** drei Stufenmethoden; jede wird übersprungen, wenn ihr Urteil mit aktuellem Siegel
   (`Night.passed`) besteht.
3. STATE sagte bei GPU-001-Fehlschlag „`--cpu` mit voller CPU-Zahl“, der Code nimmt ohne Throughput-PASS aber 1 Worker. **STATE korrigiert:** `--cpu-workers 3` explizit.
Nur vermutet, nicht geändert: relativer Pfad `GPY` (funktioniert, weil `parallel_queue` mit `cwd=ROOT` startet); der venv-Starter könnte das Job-Objekt umgehen (bekannt, Nutzerdatei).
Zwei neue Tests in `lab/tests/test_night_program.py` (124 → Ablehnung, gewöhnlicher Fehlschlag bleibt Fehlschlag; Stufen-Überspringen). **Ungetestet**, Tests laufen ab 03:00 über den Wächter.
*Regelverstoß des Subagenten (von ihm selbst gemeldet):* In einer Bash-Schleife hat er etwa 9-mal `python -c "import json,sys"` ausgeführt, vor 03:00. Das ist ein reiner Import
ohne Projektcode, ohne Dateien und ohne Training, zählt aber als Python-Ausführung außerhalb des Fensters. Auch ich habe einmal versehentlich `python -c "import ast,sys"` aufgerufen
(nur Import, nichts ausgeführt). Hinweis für künftige Prüfaufträge: „kein `python -c`“ ausdrücklich nennen (beim zweiten Prüfauftrag so getan). Die `--check`-Aufrufe des
Wächters und das Anwenden von Textpatches per Python-Skript zählen nicht als Läufe (bisherige Praxis, STATE).
*Zweitprüfung (Claude-Subagent, nur lesend, ohne Ausführung):* kein Defekt. Bestätigt: 124 macht `run_queue` immer ≠ 0; die drei GPU-001-Stufen sind in `compare.py` unabhängig
(keine Stufe liest Artefakte einer anderen), das Siegel entwertet Urteile bei Codeänderung; die Tests sind von Hand nachvollzogen. Hinweis, bewusst hingenommen: Hat eine Queue
gleichzeitig einen echten Fehlschlag und einen 124-Abbruch, gilt das Ganze als Ablehnung. Bei der Wiederaufnahme tritt der echte Fehler erneut auf und wird dann als Fehlschlag gemeldet.

## Sitzung 18 (2026-09-27 00:39 bis 03:39 Berlin, Fenster ab 03:00)

Start 00:39 (gemessen, `--check`): kein STOP, Fenster zu (Exit 3), keine Python-Prozesse, Branch lab/research unverändert bis auf die Nutzerdateien.
Sitzung 17 endete schon um 00:38 (18 min). Diese Sitzung hat also 03:00–03:39 im Fenster: Abnahme und Tests (STATE Schritte 1–3), danach
das Nachtprogramm bis zur Deadline. Ein dort angehaltener Job gilt seit Sitzung 17 als Ablehnung, nicht als Fehlschlag, und wird mit demselben Befehl fortgesetzt.

**Zyklus 1 (Wird ein GPU-Lauf aus `.venv-gpu` vom Wächter sicher mitbeendet?, fertig vor 00:45).** *Frage:* STATE nennt als offenen Verdacht, dass `guarded_run.py`
venv-Prozesse zu spät an das Job-Objekt bindet. `.venv-gpu/Scripts/python.exe` ist unter Windows nur ein Starter, der das echte Python
(`Python312/python.exe`) als Kindprozess startet. Der Wächter bindet erst nach `Popen` (Zeilen 183–184). Hat der Starter sein Kind schon erzeugt,
landet das Kind nicht im Job-Objekt des Wächters. Stirbt dann der Wächter selbst, könnte das Training ohne Zeitgrenze weiterlaufen (Gefahr für 13:00).
*Prüfung (nur Lesen):* (1) Die normalen Abbruchwege (STOP, Zeitgrenze) laufen über `taskkill /PID … /T /F` (Zeile 95). Das folgt der Eltern-Kind-Kette
und erreicht das echte Python, solange der Starter lebt, und der Starter wartet auf sein Kind. (2) Für den Fall „Wächter stirbt“: Der CPython-Starter
(`PC/launcher.c`, Zweig 3.12, `run_child`, gilt laut Quelltext auch mit `VENV_REDIRECT`) legt selbst ein Job-Objekt mit
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | SILENT_BREAKAWAY_OK` an und hängt sein Kind daran (Quelle: https://raw.githubusercontent.com/python/cpython/3.12/PC/launcher.c,
abgerufen 2026-09-27, Auszug per WebFetch). Tötet das Job-Objekt des Wächters den Starter, schließt sich dessen Handle, und das Kind stirbt mit.
*Ergebnis:* Der Verdacht ist nach dem Quelltext weitgehend entkräftet. Die Kette „Wächter-Job → Starter → Starter-Job → Kind“ hält. **Nicht gemessen.**
*Entscheidung:* Die Abnahme um 03:00 bekommt eine Zusatzprobe mit dem venv-Python: Den Wächter allein (ohne `/T`) hart beenden und prüfen, ob das echte Python,
das seine eigene PID in eine Datei schreibt, mit beendet wird. Den Nutzer-Wächter ändere ich nicht.

**Zyklus 2 (Deckt GPU-001 Astra-Punkt 9 ab?, 00:45).** *Frage:* Regel 18b2 lässt die GPU erst zu, wenn „Forward, Backward, AdamW, Wiederholung und ein langer
Lauf“ mit der CPU übereinstimmen. Prüft GPU-001 das? *Befund (Lesen von `compare.py`, `night_program.py`, Astra-Tabelle):* Nein. GPU-001 vergleicht
nur ganze 2000-Schritt-Läufe (A1–A3), also den langen Lauf. Einzelkomponenten und Wiederholbarkeit fehlen, und Punkt 9 fehlte in der Umsetzungstabelle.
Ein Fehler im Forward oder Backward könnte in A1–A3 untergehen (Top-5-Überlappung ≥ 4/5 ist grob), und Nichtdeterminismus bliebe unbemerkt.
*Änderung (ungetestet):* `lab/experiments/GPU-001-equivalence/components.py` als Stufe 0 mit vorab festgelegten Kriterien C1–C5 (README-Nachtrag
Sitzung 18). Ein Prozess, eine Torch-Version (GPU-venv), nur das Gerät verschieden. C3 vergleicht den Optimierer isoliert (gleiche Gradienten auf beiden Geräten).
C4 misst gegen das Eigenrauschen der CPU (1 gegen 4 Threads), damit eine unvermeidliche Rundungsabweichung nicht als GPU-Fehler zählt. `night_program.py`: Stufe `components` vor der
Regression, Teil des Tors und des Stufen-Überspringens; Siegel (`compare.SEAL_FILES`) umfasst `components.py`. Test `test_gpu001_stage_skip` angepasst.
Eine Zweitprüfung durch einen Claude-Subagenten (nur lesend, ausdrücklich kein `python -c`) läuft.
*Entscheidung:* Ab 03:00 läuft die Stufe im Nachtprogramm als Erstes (< 1 min geschätzt). Die Umsetzungstabelle hat eine Zeile für Punkt 9.
*Zweitprüfung Zyklus 2 (Claude-Subagent, nur lesend, nichts ausgeführt):* kein kritischer oder hoher Befund. API, Optimiererzustand (frisch je Stufe),
Init-Wiederherstellung, Geräte, Tor/Siegel und der angepasste Test wurden bestätigt, die Schwellen gelten als für fp32 erreichbar. Zwei mittlere Hinweise:
(1) `--min-minutes 3` sei knapp. *Verworfen:* Das ist nur die Mindest-Restzeit für den Start, keine Laufzeitgrenze (`guarded_run.py`).
(2) Die Thread-Umstellung in C4 ist ein globaler Nebeneffekt. *Übernommen:* `try/finally`.

**Zyklus 3 (ELR-Arm für P3 jetzt statt beim Einfrieren?, 00:50).** *Frage:* Der P3-Entwurf ([[BACKLOG]] „Drittes Konkurrenzmodell (iii) ELR“) braucht eine Trainer-Option
„lr × c für die ersten 500 Schritte nach dem Wechsel“. Geplant war, sie erst beim Einfrieren von P3 zu bauen. *Neues Argument:* Das GPU-001-Siegel umfasst `freq_ban.py`.
Jede Trainer-Änderung **nach** einer bestandenen GPU-Abnahme entwertet sie und erzwingt die ganze Abnahme neu (≈ 20–30 min Fenster). Heute Nacht läuft die Abnahme zum
ersten Mal. Also ist jetzt der billigste Zeitpunkt, sofern der Standardpfad bitgleich bleibt (die Regressionsstufe prüft genau das).
*Änderung (ungetestet):* `--lr-scale-after-switch c` (Standard 1.0 = aus; Schritte switch_step+1 … switch_step+500, das sind genau die ersten 500 Schritte auf dem zweiten Split,
weil der Wechsel nach `opt.step()` bei switch_step greift). Ausschließlich ohne `--warmup`, `--lr-scale` und `--alternate-every`, nur mit `--switch-split-file`. Run-ID `_lras<c>`.
Nach der Bauregel aus Sitzung 16 steht das Argument in `LATE_ARGS` und geht nur bei Abweichung vom Standard in den Fingerprint. Zusätzlich wird bei jedem Wechsellauf die Parameternorm
‖θ‖ am Wechsel mitgeschrieben (`events.switch.param_norm`, nur lesend, additiv), damit die ELR = lr/‖θ‖ in allen Armen als Kovariate vorliegt.
Tests in `test_freq_ban_fingerprint.py`: Standard ohne Attribut = Standard mit 1.0 = alter Fingerprint; 3.0 ändert ihn; Aufruf ohne Wechsel bricht mit Meldung ab.
*Prüfung:* Codex (Regel 18c: Änderung am gemeinsamen Trainer) läuft; bei „out of credits“ ein Claude-Subagent.
*Entscheidung:* kein neuer Versuch, nur die Option. Der ELR-Arm wird erst mit P3 festgelegt (c ∈ {1, 3, 10}, Vorhersagen (i)/(ii)/(iii) wie im BACKLOG).
*Codex-Prüfung Zyklus 3 (codex-rescue, nur lesend; Codex hat wieder Guthaben):* „nothing blocking“. Standardpfad und Fingerprint unverändert, Schrittfenster
switch_step+1 … +500 korrekt, die Ausschlüsse greifen. Drei Hinweise, alle selbst geprüft und **übernommen**:
(1) mittel: Mit `--reset-at-switch` wurde ‖θ‖ vor dem Zurücksetzen gemessen → jetzt nach dem Reset-Block (beschreibt die Parameter, auf die die skalierten Schritte wirken).
(2) mittel: Kein Test erreicht das Schrittfenster → Multiplikator als reine Funktion `lr_mult_after_switch` herausgezogen, Test bei S, S+1, S+500, S+501 und Zählung = 500.
(3) niedrig: Der Stabilitätstest verglich nur neue mit neuer Rechnung → jetzt gegen den nachgebauten Fingerprint-Algorithmus vor Sitzung 18 verankert (einen festen Hashwert
kann ich vor 03:00 nicht erzeugen, ohne Python auszuführen).

**Zyklus 4 (Codex-Prüfung des Nachtprogramms vor dem ersten Lauf, bis ≈ 01:08).** *Frage:* Findet eine andere Modellfamilie im nie gelaufenen Nachtcode (`night_program.py`,
`parallel_queue.py`, `result_loader.py`, Trainer) etwas, das die beiden Claude-Prüfungen aus Sitzung 17 übersehen haben? *Ergebnis:* **Codex-Aufruf abgebrochen**
(„stream disconnected before completion“, 10 Reconnect-Versuche). Laut Regel 12 dokumentiert, ohne Wiederholung. Vor dem Abbruch kamen zwei Teilaussagen: „The generated flags match
the declared trainer interfaces so far“ und ein Verdacht auf ein Wiederaufnahme-Risiko in den Trainern außer `freq_ban` (`group_train.py`, `intadd_train.py`, `width_train.py`).
*Selbst geprüft:* Diese drei Trainer überspringen einen Lauf allein nach `status == "completed"` (bei EXP-046 ohne Schrittprüfung), ohne Fingerprint. Ein fertiger Lauf mit
anderer Konfiguration unter derselben Run-ID würde also still übersprungen. Heute Nacht ist das ohne Wirkung: In EXP-043–051 gibt es **kein einziges** `result.json`
(gezählt), das Nachtprogramm ruft jede Run-ID immer mit denselben Argumenten auf, `result.json` wird atomar geschrieben, und `result_loader.py` prüft vor jeder Auswertung
Schrittbudget und Konfiguration. *Entscheidung:* Heute keine Änderung an diesen Trainern (ungetestet, kein akuter Schaden). Offener Punkt: Fingerprint wie in `freq_ban.py`
nachziehen, bevor eine ihrer Run-IDs mit anderen Argumenten wiederverwendet wird (z. B. im P1-Bestätigungsblock).

## Sitzung 19 (2026-09-27, Start 01:09 Berlin, Deadline 04:09; Fenster ab 03:00)

Start: `--check` Exit 3 (außerhalb, Regel 18: Läufe erst ab 03:00), kein STOP, keine Python-Prozesse, Arbeitsbaum wie Sitzung 18 hinterlassen.

**Zyklus 1 (Fingerprint für die drei kleinen Trainer, bis ≈ 01:12, gemessen nachträglich).** *Frage:* Sitzung 18 (Codex-Teilhinweis, selbst bestätigt) fand, dass
`group_train.py`, `intadd_train.py` und `width_train.py` einen Lauf allein nach `status == "completed"` überspringen. Ist jetzt der richtige Zeitpunkt, das zu schließen?
*Argument:* Ja. In EXP-046/048/049 existiert noch kein `result.json`; nach der Nacht gäbe es Läufe ohne Fingerprint, die man dann als Altlast gesondert behandeln müsste
(wie in `freq_ban.py` mit `legacy_mismatch`). Das GPU-001-Siegel umfasst diese Trainer nicht, die Abnahme wird also nicht entwertet.
*Änderung (ungetestet):* `lab/tools/trainer_guard.py` (Fingerprint über alle wirksamen Argumente + SHA-256 des Split-Inhalts; Pfad, `out_root`, `force` nicht darin,
damit derselbe Split unter anderem Pfad nicht als andere Konfiguration gilt). Entscheidung: überspringen nur bei gleichem Fingerprint, `completed` und vollem Budget;
unlesbares `result.json` oder unfertiger Lauf mit gleichem Fingerprint → neu trainieren; abweichender oder fehlender Fingerprint → Abbruch mit Exit 2 (fail closed, `--force` hebt auf).
`result.json` trägt `config_fingerprint` und `fingerprint_fields`. Keine Sperrdatei (YAGNI: das Nachtprogramm startet jede Run-ID einmal; Smokes laufen in `raw_smoke`).
*Prüfung:* Selbsttest ab 03:00 (`python lab/tools/trainer_guard.py --selftest`); die Smokes des Nachtprogramms (je 50 Schritte, `raw_smoke`) prüfen den Import und den Schreibpfad.
*Entscheidung:* übernommen; offener Punkt aus Sitzung 18 damit geschlossen, sobald der Selbsttest besteht.

**Zyklus 2 (Passt die Nacht ins Fenster? Reihenfolge der CPU-Queue, bis 01:14 gemessen).** *Frage:* Was wird bis 13:00 realistisch fertig, und stimmt die Reihenfolge mit den
Prioritäten aus Regel 18c überein? *Vorgehen:* `night_program.py --dry-run` und `--cpu --dry-run` (führen nichts aus, schreiben nichts; geprüft mit `git status`), Laufzahlen gezählt,
Dauer aus gespeicherten `sec_per_step` (EXP-016/020, CPU 4 Threads: 0.124–0.131 s/Schritt → ≈ 4,3 min je 2000 Schritte).
*Ergebnis:* GPU-Programm ≈ 300 Läufe à 2000 Schritte (043: 60, 046: 30, 047: 40, 048: 30, 049: 40, 044: 100) plus EXP-045 (20 Läufe bis 10 000 Schritte). Die GPU-Geschwindigkeit ist
**noch nie gemessen** (GPU-001 hat keine Rohdaten); je nach s/Schritt passt das Programm in 1–4 Fensterstunden. Das CPU-Programm umfasst ≈ 300 Läufe (2000–8000 Schritte) plus
EXP-014 (10 Läufe bis Generalisierung + 25, je ≥ 33 min Mindestbudget). Bei 2 CPU-Arbeitern sind das grob 15 h, also **mehrere Nächte**. Die Reihenfolge entscheidet deshalb, was heute fertig wird.
Die Standardfolge beginnt mit EXP-014. Das ist eine Exploration aus queue_s5 (Split gegen Init), die ≈ 5,5 Worker-Stunden kostet und vor den Paket-B-Piloten (EXP-035–042) liegt.
Diese Piloten braucht das Einfrieren von P3.
*Entscheidung:* CPU-Start mit `--experiments EXP-035,EXP-038,EXP-041,EXP-036,EXP-039,EXP-040,EXP-042,EXP-014` (keine Codeänderung; `--experiments` legt bei `--cpu` die Reihenfolge fest,
Zeile 626). EXP-014 bleibt im Programm, nur am Ende. STATE Schritt 5 angepasst. GPU-Reihenfolge unverändert (A zuerst: 043, 046, 047/051, 048, 049; dann B: 044; dann 045).
*Zweitprüfung Zyklus 1 (Claude-Subagent python-reviewer, nur lesend, nichts ausgeführt):* nichts blockierend. Selbsttest, Importpfade (`ROOT = HERE.parents[2]`),
Verträglichkeit der neuen Felder mit `--check-smoke`, `result_loader.py` und den drei `analyze.py` bestätigt; Smokes umgehen den Wächter per `--force` in `raw_smoke`.
Zwei niedrige Hinweise: (1) `--threads` im Fingerprint → eine Wiederholung mit anderer Threadzahl bricht ab. *Beibehalten, absichtlich:* Threads ändern die Rundung,
also ist das eine andere Konfiguration. (2) `default=str` nur im Fingerprint, nicht beim Schreiben von `result.json`. *Verworfen für heute:* Alle Argumente sind int/str/bool.

**Zyklus 3 (Codex-Prüfung des Nachtprogramms, zweiter Versuch, bis 01:21 gemessen).** *Frage:* wie Sitzung 18 Zyklus 4 (dort Verbindungsabbruch). Neuer Codex-Faden, nur lesend.
Codex nennt die Befunde „blockierend“. *Jeden Befund selbst geprüft:*
(1) „kritisch“: Nach Exit 3 wartet `parallel_queue` auf laufende Jobs. *Verworfen:* Jeder laufende Job steht unter seinem eigenen `guarded_run.py` mit harter Grenze
(Sitzungsdeadline bzw. 13:00). Das Warten kann das Fenster also nicht verletzen, es verhindert nur verwaiste Prozesse.
(2) „kritisch“: Exit 124 zählt in `parallel_queue` als gewöhnlicher Fehlschlag, freie Plätze starten neue Jobs. *Verworfen als Fehler:* Alle Jobs haben dieselbe Deadline.
Ein Start danach wird vom Wächter mangels Restzeit abgelehnt (Exit 3 → Stopp). `night_program.py` wertet 124 seit Sitzung 17 ohnehin als Ablehnung (Zeilen 98–109). Folgen: keine.
(3) „hoch“: Fehlschläge der Durchsatzstufen J2/J4/J8 werden ignoriert, PASS braucht nur J1. *Stimmt, ist aber so gewollt:* `best_J` (Zeile 137) wählt nur unter **vollständigen**
Stufen. Ein Absturz bei J8 (z. B. Speicher) senkt also nur J und verfälscht nichts. *Übernommen als Leseregel:* Beim Auswerten von GPU-001 die `summary.json` der Stufen
`gpu001_tp_J*` prüfen. Ein Absturz dort ist ein Stabilitätshinweis und gehört ins JOURNAL.
(4) „hoch“: Bei der Wiederaufnahme einer unfertigen GPU-001-Stufe werden deren Teilläufe neu gerechnet. *Stimmt, ist aber Absicht* (Review s13: kein Wiederverwenden von Läufen
älteren Codes). Bestandene Stufen werden übersprungen (Sitzung 17). Kosten: höchstens eine Stufe, wenige Minuten.
(5) „mittel“: `--cpu-workers` hat keine Obergrenze gegen die GPU-Threads. *Stimmt:* Der Standard (12 − J)//4 hält die Summe ≤ 12, nur eine ausdrückliche Zahl kann sie überschreiten.
Keine Codeänderung. STATE nennt die explizite Zahl nur für den Fall ohne GPU.
*Entscheidung:* keine Änderung am Nachtprogramm. Nichts davon blockiert den Start um 03:00.

## Sitzung 20 (2026-09-27, Start 01:29 Berlin, Deadline 04:29; Fenster ab 03:00)

Start 01:29 (gemessen): kein STOP, Fenster zu (Exit 3), keine Python-Prozesse. Sitzung 19 endete 23:21Z nach 11.8 min.
Beide Trockenläufe des Nachtprogramms (GPU, CPU mit Reihenfolge aus Sitzung 19) planen vollständig und schreiben nichts (`git status` unverändert).

**Zyklus 1 (Nimmt Zhou/Zhang/Xu K2 vorweg? Bleibt die gepflanzte Wahl nach dem Grokking? bis 01:33 gemessen).** *Frage:* Die Nachsuche aus Sitzung 17 nannte
Zhou, Zhang, Xu (CiCP 2026) nur nach Angabe des Subagenten: „ungleichmäßige Stichprobe erzeugt zuerst unechte Frequenzen“. *Vorgehen:* Zeitschriftenseite, arXiv-Abstract und
HTML-Volltext (2405.17479) selbst abgerufen, per Zusammenfassung des Abrufwerkzeugs. *Ergebnis Literatur:* Das ist die schon zitierte Arbeit Zhou et al. 2024. Aufgaben: sin(6x),
Parität, MNIST, keine modulare Arithmetik. Die Frequenzen aus der Stichprobe sind dort Aliasing-Artefakte neben der festen Zielfunktion und klingen auf der Testmenge ab.
K2 (Auswahl unter gleichwertigen Lösungen) ist davon abgegrenzt und bleibt „nach unserer Suche nicht gefunden, vorläufig“. Die Arbeit ist aber die nächste Vorarbeit und muss
beim Einordnen ausdrücklich genannt werden. *Daraus die Prüffrage:* Klingt die gepflanzte Wahl bei uns nach dem Grokking ab? *Nachrechnung gespeicherter Läufe* (kein Training;
`lab/experiments/EXP-016-engineered-split/posthoc_postgen_persistence.py`, 20 EXP-016-Läufe, Spektren alle 250 Schritte): Alle 20 Läufe generalisieren (gen 450–1100, Test ≈ 1.0 bei 2000).
Der Anteil der eigenen Ziele an der W_E-Leistung steigt vom ersten Messpunkt ≥ gen bis 2000 von 0.56 auf 0.82 (20/20 steigen, Δ 0.26 ± 0.07 SD). Die Ziele des anderen Arms liegen bei 0.016,
Zufall 5/56 = 0.089. |Top-5 ∩ T| 4.3 → 3.9 (bekannte 2k-Oberwellen). *Deutung (beschreibend, post hoc):* Die Konzentration auf die gepflanzten Frequenzen wächst nach dem
Grokking weiter, ein Abklingen wie bei Zhou et al. zeigt sich nicht. Grenzen: F und G teilen die Init (K2-Einschränkung), nur bis Schritt 2000, keine Kontrolle, ob der Anteil
der eigenen Top-5 in Zufallssplit-Läufen genauso wächst (das wäre ein allgemeines Verdichten durch Weight Decay, keine Besonderheit des Splits). *Entscheidung:* als Randnotiz in
[[NOVEL_DIRECTIONS]] (Nachprüfung Sitzung 20). Kein neuer Versuch (Regel 15b). Längere Zeitskala liefert EXP-045 (MLP, bis 10 000 Schritte) aus dem Nachtprogramm.

**Zyklus 2 (Kontrolle zu Zyklus 1: Ist das Verdichten nach dem Grokking eine Wirkung des Splits? bis 01:34 gemessen).** *Frage:* Wächst der Leistungsanteil einer festen Top-5-Menge
auch in Läufen mit Zufallssplit nach dem Grokking? *Vorgehen:* `posthoc_postgen_control.py` (EXP-016-Ordner), nur gespeicherte Daten. Zufallsreferenz: Studienläufe Seeds 0–9
(gleiche Konfiguration, 25 000 Schritte). Menge S = Top-5 beim ersten Messpunkt ≥ gen (verzerrt gegen Wachstum) bzw. am Ende (verzerrt dafür), dasselbe für EXP-016. Anteil bei gen und bei gen + 750/1500.
*Ergebnis:* Zufallssplit: +0.11 ± 0.03 (+750) bzw. +0.19 ± 0.03 (+1500), 10/10 steigen (S bei gen; S am Ende +0.13/+0.22). EXP-016: +0.23 ± 0.04 bzw. +0.28 ± 0.08, 20/20.
*Deutung:* Das Verdichten nach dem Grokking ist **allgemein**, nicht splitspezifisch. Der größere Zuwachs bei EXP-016 ist nicht belastbar, denn EXP-016 generalisiert
viel früher (450–1100 gegen 5600–8400 Schritte, Anteil noch im Aufbau) und „+1500“ wird bei Schritt 2000 abgeschnitten. **Belastbar bleibt nur:** kein Abklingen der gepflanzten Wahl
bis Schritt 2000, also der Unterschied zu Zhou et al. Eine Verstärkung durch den Split ist **nicht gezeigt**. *Entscheidung:* Die Randnotiz in [[NOVEL_DIRECTIONS]] entsprechend
eingeschränkt. Kein neuer Versuch.

*Nachtrag Zyklus 1:* Zhou et al. 2024 ist in [[NOVEL_DIRECTIONS]] N6 schon seit Sitzung 5 ausführlich eingeordnet (dort: #neu/bekannt (teilweise) für die Grundidee von N3).
Die Literaturprüfung von heute ist daher nur eine Bestätigung. Neu ist allein die Nachrechnung „kein Abklingen nach dem Grokking“. Zyklen 1+2 sind damit abgeschlossen. Bis 03:00 bleibt
nichts Pflichtiges offen, als Nächstes kommt der Ablauf 18b aus [[STATE]].

**Fenster früher offen (02:25 gemessen).** Die interaktive Sitzung des Nutzer-Assistenten meldet eine Freigabe des Nutzers: Die 03:00-Sperre ist aufgehoben (`WINDOW_START_OVERRIDES` leer,
`--check` allowed: true). Das habe ich im Wächter nachgeprüft und dann den Ablauf 18b begonnen.

**Zyklus 3 (18b: Wächter-Abnahme, Tests, Start des Nachtprogramms, 02:25–02:34 gemessen).**
- *Wächter-Abnahme* `accept_guard.ps1`: A (STOP → Exit 3, Kind beendet, STOP gelöscht), B (Wächter hart beendet, System-Python) und C (dasselbe mit venv-Python) **alle PASS**.
  STOP ist wieder gelöscht und wurde nur von der Probe angelegt. **Aber:** jeder Wächterstart meldete „job object not applied (OverflowError: int too long to convert)“. Ursache
  (selbst gefunden): `GetCurrentProcess()` liefert das Pseudo-Handle −1, `AssignProcessToJobObject` hatte keine `argtypes`. Da B/C bestanden, beendet ein anderer Pfad das Kind.
  Ich habe `guarded_run.py` nicht geändert (unversionierte Datei des Nutzers) und die Sitzung des Nutzer-Assistenten benachrichtigt. Diese hat um ≈ 02:35 argtypes/restype ergänzt.
  Danach gab es bei neuen Wächterstarts keine Warnung mehr (gesehen im pilot_power-Lauf 02:28 und bei den Nachtjobs). Die Abnahme lief also mit der alten Fassung. B/C mit Job-Objekt sind noch nicht eigens nachgeprüft.
- *Tests* (`parallel_queue.py lab/runner/tests_s19.txt --workers 3`): 9/11 ok. Zwei Fehlschläge, beide im Testaufbau: (1) `test_freq_ban.py`: Der eigene Testrunner rief den
  pytest-artigen Test `test_previous_status_tolerates_truncated_result(tmp_path)` ohne Argument auf. Behoben: Der Runner übergibt einen Temp-Ordner. (2) `pilot_power.py --selftest`: Die
  „verrauschte“ Stichprobe normal(0.2, 6) hatte zufällig den Mittelwert 1.10 ≥ Mindesteffekt, also fehlte die Warnung zu Recht. Behoben: Mittelwert fest auf 0.2 zentriert.
  Beide danach grün (16 passed; selftest ok, n 11 / None). Der Code von freq_ban und pilot_power ist unverändert.
- *Nachtprogramm, erster Start 02:30:* GPU-001 scheiterte sofort bei `gpu001_env`: `FileNotFoundError` für `.venv-gpu/Scripts/python.exe`. Windows `CreateProcess` findet den relativen
  Pfad mit Schrägstrichen nicht, mit Backslashes schon (direkt geprüft). `night_program.py` nutzt jetzt `str(ROOT / ".venv-gpu" / "Scripts" / "python.exe")` (Listen, kein shlex).
  `test_night_program.py` ist grün. **Offen:** `confirm_p1.py` schreibt `.venv-gpu/Scripts/python.exe` in Jobzeilen. Das scheitert genauso, und Backslashes lehnt `parallel_queue` in Zeilen ab.
  Vor der Nutzung des Bestätigungsblocks lösen (z. B. `guarded_run` normalisiert cmd[0], das entscheidet der Nutzer, oder absoluter Pfad mit Schrägstrichen testen).
- *Zweiter Start 02:34:* `gpu001_env` ok, dann `gpu001_components` (Stufe 0, Astra 9). Wiederaufnahme: `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1`.

**Zyklus 4 (GPU-001: Liefert die RX 7900 XT gleichwertige Läufe? 02:34–02:51 gemessen).** Vorab festgelegt in [[experiments/GPU-001-equivalence/README|GPU-001]] (Stufen, Toleranzen).
- *Stufe 0 Komponenten (Astra 9):* C1 Logits/Loss (1e-4), C2 Gradienten (1e-3), C3 AdamW-Update (1e-3), C4, C5 (Wiederholung) **alle PASS**, GPU-Speicher 189 MB. torch 2.9.1+rocm7.2.1, HIP 7.2.
- *Regression (CPU-Pfad nach `--device`):* PASS (gleiche Top-5 wie der alte Smoke).
- *Gleichwertigkeit (Seeds 10–12, EXP-016-Splits, 2000 Schritte, GPU `--threads 1` gegen gespeicherte CPU-Läufe):* **PASS**. A1 ja; A2 9/9 (Top-5-Überlappung ≥ 4 bei 250/500/1000/2000,
  bei 2000 jeweils 5/5); A3 ja (gen CPU/GPU: 775/800, 625/625, Seed 10 ebenfalls innerhalb der Toleranz); Endgenauigkeit gleich. Der Train-Loss weicht ab Schritt ≈ 110–120 um > 1 % ab
  (bei Schritt 500 1–3 %). Erwartbar, keine Bitgleichheit (Regel 16b). **Tempo: 0.0074 s/Schritt GPU gegen 0.129 s CPU (4 Threads), also ≈ 17×.** Speicher 241 MB je Lauf.
- *Diagnose Version gegen Gerät (Astra 10, kein Kriterium):* derselbe CPU-Lauf mit der torch aus `.venv-gpu`, ohne `--threads`. Er brauchte ≈ 1.3 s/Schritt (500 Schritte in ≈ 11 min),
  ≈ 10× langsamer als die globale CPU-torch. **Abgebrochen 02:49 (Regel 14: deutlich langsamer als geplant, hätte das GPU-Programm ≈ 45 min blockiert).** Der Abbruch ließ `compare.py
  equivalence` am unvollständigen Lauf abstürzen (ValueError, Schritt 2000 fehlt). Behoben: Unvollständige Diagnose wird als „status running, 500 Schritte“ berichtet. Das Urteil
  darüber hinaus unverändert. Die Versionsfrage bleibt damit offen. Befund nebenbei: **Die CPU-torch der ROCm-venv ist für CPU-Läufe ungeeignet** (Ursache ungeprüft, vermutlich
  ohne MKL bzw. mit anderer Threadzahl). CPU-Läufe bleiben beim globalen Python.
- *Entscheidung:* GPU nach Regel 16/Astra 9 für neue Versuche freigegeben, weiter „experimentell“ bis zu einem langen Lauf (EXP-045 10 000 Schritte liefert ihn). Nachtprogramm neu gestartet
  02:50 (`night2.log`). Da `compare.py` geändert wurde, hat sich das Siegel geändert: Komponenten und Regression laufen noch einmal (≈ 2 min), die Gleichwertigkeit wird übersprungen (Urteil mit neuem Siegel), dann Durchsatz J = 1/2/4/8.

**Zyklus 5 (Paket A: Verallgemeinert sich K2? EXP-043 und EXP-046 auf der GPU, 02:53–03:02 gemessen).** Frage und Kriterien in den READMEs, vor den Läufen eingefroren.
Vor der Deutung [[LESART-nacht-2026-09-27]] gelesen.
- [[experiments/EXP-043-generalize-steering/README|EXP-043]]: add 97 **steuerbar** (Δ̄ 7.7, 10/10, p 0.00098, Holm), mul 113 **steuerbar** (Δ̄ 7.7, 10/10, p 0.00098). Die Überlappung mit den eigenen Zielen
  liegt meist schon bei Schritt 50 bei 4–5 von 5. Generalisiert bei 2000: 17/20 bzw. 16/20. Die Steuerung zeigt sich auch in nicht generalisierten Läufen. R-Arme: 0.75/0.55 (Zufall ≈ 0.5).
- [[experiments/EXP-046-dihedral-steering/README|EXP-046]] (D₅₉, nicht-abelsch, Irreps): Strukturprüfung 18/20, **steuerbar** (Δ̄ 9.6, 10/10, p 0.00098, passend 4.85 / gekreuzt 0.05).
- *Deutung (vorab festgelegte Lesarten):* K2 hält in allen drei neuen Fällen (anderer Primmodulus, zusammengesetzter Modulus mit Null-Token über den Log, nicht-abelsche Gruppe). Die Effekte sind
  so groß wie in EXP-016 (D₅₉ sogar größer). Das ist die erste Antwort auf die größte offene Frage in [[FINDINGS]]. **Einschränkungen:** Alles sind Piloten mit Seeds aus den Versuchen,
  keine unabhängige Bestätigung. Die Frage Häufigkeiten gegen Paarstruktur ist offen (EXP-047 läuft gerade). Alle drei Fälle sind Gruppenoperationen mit Token-Einbettung. Die nicht-modulare Aufgabe (EXP-048) folgt.
  Eine andere Breite folgt mit EXP-049, eine andere Architektur mit EXP-045.
- *Entscheidung:* FINDINGS erst nach EXP-047/048 aktualisieren (Lesart-Notiz: Kombination zählt). Beschreibende Zusätze für EXP-046 (Top-3, Δ_pow) als offener Rest.

**Zyklus 6 (Mechanismus und Funktion: EXP-047 und EXP-051, 03:02–03:10 gemessen).**
- [[experiments/EXP-047-marginal-control/README|EXP-047]]: a) Häufigkeiten allein *richtungsgleich, n. s.* (Δ̄_shuf 0.3, p 0.33); b) **Paarstruktur trägt über die Häufigkeiten hinaus**
  (D̄ 6.8, p 0.00098, Holm). Manipulationsprüfung eng Δ̄ 7.1. Genau die vorab notierte Erwartung erster Ordnung. Damit ist die Grenze 4 in [[FINDINGS]] (K2-Mechanismus nicht eindeutig) für Z₁₁₃
  weitgehend geklärt: Die Paarstruktur (M0) steuert. Pilot, 10 Seeds.
- [[experiments/EXP-051-functional-ablation/README|EXP-051]]: formal *nicht mehr genutzt als gleiche Energie anderswo* (D̄ 0.0). **Selbst geprüft:** 40/40 Eingriffe ohne jeden
  Genauigkeitsverlust, denn X ist nur 3–9 % der Zielenergie (Kontrollfrequenzen tragen ≈ 15× weniger). Bodeneffekt, keine Trennschärfe. Das formale Urteil bleibt stehen (§3B), die README
  sagt klar „kein Beleg gegen funktionale Nutzung“. Sekundär: Die volle Ablation der eigenen Ziele kostet 0.95–0.99 Testgenauigkeit, die der fremden 0 (10/10). Die Ziele sind notwendig,
  die Nutzung je Energieeinheit ist offen. shuf-Modelle ungültig (nicht generalisiert).
- *Entscheidung:* Für P2 einen sauberen Nachfolger mit neuer ID festlegen (kontinuierliches Maß: Test-Loss/Logit-Abstand; Dosis-Wirkungs-Kurve own gegen ctrl über mehrere Energiestufen,
  an den gespeicherten EXP-047-Modellen, kein Training nötig). *Codex-Hinweis für später:* vor dem Einfrieren von P2 prüfen lassen (Regel 18c).

**Zyklus 7 (P2 genauer: EXP-055, Dosis-Wirkung am Test-Loss, 03:10–03:11 gemessen).** Registriert 03:10 vor dem ersten Lauf (Commit 67cc1a4), mit „bereits gesehen: EXP-051“.
*Ergebnis:* primär f = 1.0 *richtungsgleich, n. s.* (D̄ 5·10⁻⁵, 4/10, p 0.42). Beschreibend: Bei f = 0.1–0.75 ist ΔL_own > ΔL_ctrl in 10/10 Seeds je Dosis, bei f = 1 kippt es,
weil das vollständige Löschen der Kontrolle überproportional kostet. *Deutung:* Bei gleicher entfernter Energie sind die Zielfrequenzen im Teilbereich stärker genutzt. Das ist aber post hoc,
und die vorab gewählte Primärdosis war die ungünstigste. *Entscheidung:* P2 für den Bestätigungsblock mit primärer Teildosis (f = 0.5) und ΔL an frischen Modellen festlegen
(im [[BACKLOG]] P2-Abschnitt nachgetragen). Die 20 EXP-047-Modelle sind verbraucht (zweimal gesehen).

**Zyklus 8 (nicht-modulare Aufgabe: EXP-048, 03:07–03:12 gemessen).** [[experiments/EXP-048-intadd-steering/README|EXP-048]] (a + b ohne mod, Ausgabe 0..224): **steuerbar**
(trendbereinigtes Δ_pow 2.23, 10/10, p 0.00098; roh 2.12; Top-5-Δ 3.4; R ≈ 0). Die Aufgabe ist bei 2000 Schritten nicht gelernt (Test 0.23). Die Steuerung betrifft also die
Repräsentation vor jedem Lernen. Lesart vorab: „der Split steuert“, Häufigkeiten gegen Paarstruktur hier nicht getrennt. *Zwischenstand Paket A:* K2 hält in 5/5 geprüften neuen Fällen
(add 97, mul 113, D₅₉, int-add, dazu die Mechanismuskontrolle EXP-047). Nach [[LESART-nacht-2026-09-27]] Regel 2 reicht das für „K2 verallgemeinert sich über die gezeigten Aufgaben“
(EXP-046, EXP-048 und eine EXP-043-Aufgabe *steuerbar*). FINDINGS aktualisiere ich nach EXP-049 in diesem Zyklus.

**Zyklus 9 (Paket C: eingefrorene Vorhersage EXP-052 und Breite EXP-049, 03:13–03:26 gemessen).**
- [[experiments/EXP-049-width-steering/README|EXP-049]]: d = 512 **steuerbar** (Δ_pow 7.8, 10/10, p 0.001). d = 128 repliziert EXP-016 an frischen Seeds auf der GPU (8.7, 10/10).
  512 ist um 0.83 kleiner (beschreibend p 0.003), wie vorab erwartet. Die effektive Frequenzzahl steigt von 8.1 auf 10.9.
- [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]] (Vorhersagen per Commit vor jedem Lauf eingefroren): **K1 gilt in 4/4 Fällen** (Holm-p 0.0002 je Fall; ρ eigen 0.34–0.45,
  fremd −0.07 bis 0.04; Split-Erkennung Top-1 0.7–1.0). S1 (M0c > M0), S2 (M0 > Init), S3 (M0 > Häufigkeiten) alle wie vorhergesagt. Das ist die erste **vorab eingefrorene mechanistische
  Vorhersage an unberührten Fällen**, die trifft (Paket C, Regel 18c). Assoziation, kein Eingriff. Den Eingriff liefern die F/G-Arme.
- FINDINGS: Pilotnacht-Tabelle um EXP-052 ergänzt. *Einordnung:* Paket A (Verallgemeinerung) und C (Vorhersage) sind im Pilot stark. Der Engpass ist jetzt die **unabhängige
  Bestätigung** (P1 mit Manifest, frische Seeds 1000–1099) und P2 (Funktion mit Loss-Maß).

**Zyklus 10 (Stichprobengröße für P1 aus der Pilotstreuung, 03:25–03:28 gemessen).** `python lab/tools/pilot_power.py` (Summaries von EXP-048/049 stammen aus dieser Nacht, geprüft über die
Laufzeiten 03:07–03:22). Ergebnis `lab/tools/pilot_power_summary.json`. Mindesteffekt Δ_pow ≥ 1, einseitig, α 0.05/3 (Holm-Worst-Case), Power 80 %, n (normal / Bootstrap / obere SD-Schranke 80 %):
add 97 8/8/11 · mul 113 29/26/49 · D₅₉ 7/7/7 · add 113 GPU (EXP-047 eng) 27/25/44 · int-add 7/7/7 · add 113 d512 26/25/41. Pilotmittel 2.2–7.8, alle 10/10 positiv.
*Deutung:* Für den P1-Kern (add 113, Transformer) reichen ≈ 30 Seeds, konservativ ≈ 45. Auf der GPU kostet das Minuten, deshalb **Vorschlag: n = 50 für add 113** (deckt die konservative Schranke).
*Einschränkung:* Der Mindesteffekt 1 ist auf allen Skalen gleich gesetzt. Bei D₅₉/int-add (Pilotmittel 2–3) ist das streng, bei add (≈ 7–8) sehr lax. Für das Manifest den Mindesteffekt je Aufgabe
relativ festlegen (z. B. 25 % des Pilotmittels) oder nur add 113 primär führen. Entscheidung beim Einfrieren von P1, **vorher Codex-Prüfung** (Regel 18c). Nächster Schritt: Manifest-Entwurf.

**Zyklus 11 (Paket B: K4 in den neuen Aufgaben, EXP-044 + π, 03:23–03:32 gemessen).** [[experiments/EXP-044-generalize-lockin/README|EXP-044]]: add 97 und mul 113 **festgelegt**
(d(150) 3.3 / 3.5, je 10/10, p 0.001 Holm). Die Wahl kippt zwischen t = 25 (d −1.8 / −2.9) und t = 50 (+2.7 / +2.0), wie in EXP-020. π (vorab, beschreibend): 0.37/0.86/1.24 bzw.
0.22/0.72/1.15 gegen EXP-020 0.41/0.74/≈1. Die vorab notierte **Lesart (i)** trifft zu: Festlegung im Netz, nicht durch geteilte Paare gehalten (hier nur ≈ 38 % geteilt). Confound Aufgabe/Gerät,
saubere Trennung erst mit EXP-053. *Folge für P3:* Primär t = 25 bleibt richtig (dort ist π am empfindlichsten, 0.2–0.4). FINDINGS-Tabelle und LAB ergänzt.

**Zyklus 12 (andere Architektur: EXP-045 MLP, 03:32–03:35 gemessen).** [[experiments/EXP-045-mlp-steering/README|EXP-045]]: **steuerbar** (Δ̄ 7.9 bei 10 000, 10/10, p 0.001; bei 2000: 10.0).
Alle Läufe generalisieren (gen 3450–7575). Damit ist auch die Frage aus Zyklus 1/2 auf längerer Zeitskala beantwortet (beschreibend): Die gepflanzte Wahl bleibt 2400–6500 Schritte nach dem
Grokking erhalten (10/10), leicht verwässert (10.0 → 7.9). GPU-Nachtprogramm damit komplett („all done“ 03:33). Danach EXP-050 (Paket C, 60 Läufe) nachgeschoben: `night3_exp050.log`.

**Zyklus 13 (Paket C: M0c gegen M0, EXP-050, 03:35–03:42 gemessen).** [[experiments/EXP-050-phase-dissociation/README|EXP-050]] (GPU frei nach dem Nachtprogramm, wie in STATE vorgesehen):
a *M0c selektiert* (D̄ 6.51, 10/10, p 0.001), b *anti steuert trotzdem* (Δ̄_anti 1.36, 10/10, p 0.001), Manipulation quadlm 7.88. Die Vorhersage erster Ordnung war „a ja, b nein“.
Eingetreten ist das vorab benannte Zwischenergebnis „a ja und b ja“: Der Kreuzterm dominiert (≈ 6×), M0 trägt einen kleinen, aber durchgängigen Anteil. **Das ist ein Befund gegen die reine
Theorie erster Ordnung** (sie sagt anti ≈ 0). Kandidaten: spätere Schritte, MLP-Nichtlinearität. Das passt zu EXP-052 S1 (M0c > M0, aber M0 sagt auch voraus). Folgeversuch MLP mit getrennten W_in-Hälften
(vorab genannt). FINDINGS und LAB ergänzt.

**Zyklus 14 (Codex-Prüfung des P1-Entwurfs vor dem Einfrieren, Regel 18c, 03:30–03:41 gemessen).** Über den Claude-Subagenten codex-rescue, nur lesend, ≈ 11 min.
*Codex:* „not safe to freeze as-is“, 3 Blocker, 4 hoch, 2 mittel. Die Δ_pow-Rechnung ist in Pilot und Bestätigung gleich (Schritt 2000, F/G nicht vertauscht, D₅₉-Irreps richtig indiziert),
der Windows-Pfad in Ordnung. *Selbst geprüft (Code gelesen) und Entscheidung je Punkt:*
1. **Blocker, übernommen:** `check_manifest` vergleicht nur das Manifest ohne `commit` (confirm_splits.py:127–139), der ausgeführte Code ist nicht gebunden, und der Lader prüft `git_commit` nicht.
   → Manifest bekommt SHA-256 der Trainer-, Split- und Analysedateien. `--jobs`/`--analyze` brechen bei Abweichung ab, der Lader prüft sie gegen die Läufe.
2. **Blocker, übernommen:** P1-Familie offen (add 113 allein oder vier Aufgaben). → Vorschlag: **P1 = add 113 (Kern) primär**, die drei anderen Aufgaben als P1b sekundär mit eigener
   Holm-Familie. So bleibt die P1–P3-Familie bei 3, wie in FINDINGS festgelegt. Entscheidung beim Einfrieren.
3. **Hoch, übernommen:** Mindesteffekt 1 wird nur berichtet (confirm_p1.py:219–221). → „bestätigt“ braucht KI-Untergrenze ≥ 1 (oder Test gegen 1), sonst Mindesteffekt aus der Aussage streichen.
4. **Blocker, übernommen:** 80 % vollständige Fälle genügen (Z. 209), nicht-endliches Δ wird nicht abgewiesen. → Alle 50 geplanten Paare verlangen (Infrastrukturfehler nur mit
   demselben eingefrorenen Job wiederholen), Δ nicht endlich oder Zielsumme ≤ 0 → ungültig. Fehlt am Ende etwas: *nicht auswertbar*.
5. **Hoch, übernommen:** Die Power-Rechnung nutzt α/3, der Code hätte 6 Hypothesen. Mit Punkt 2 (Familie 3) passt α/3 wieder. Sonst neu rechnen.
6. **Hoch, übernommen:** Ziel-JSON wird bei der Auswertung nicht gegen `build()` geprüft. → Bei `--analyze` Indizes und Ziele neu erzeugen und exakt vergleichen.
7. **Hoch, teilweise:** Der Vorzeichen-Permutationstest ist exakt nur unter Symmetrie. Pilot und EXP-016 nutzen denselben Test, die Annahme wird in der Registrierung ausdrücklich genannt
   (Nullhypothese: Verteilung von Δ symmetrisch um 0, gerechtfertigt durch die Vertauschbarkeit von F und G, die bei gleicher Konstruktion beider Arme gilt). Zusätzlich wird ein
   studentisierter t-Test berichtet, nicht primär.
8. **Mittel, übernommen (nur Beschreibung):** Das Design ist nach Seeds gepaart (F/G gleiche Init, Aufgaben gleicher Seed). Das wird so beschrieben. Optional Init je Aufgabe trennen.
9. **Mittel, übernommen:** Die Aufgabenwahl ist nach dem Pilot gefiltert. P1 heißt deshalb „unabhängige Replikation in vier im Pilot gewählten Fällen“, nicht Verallgemeinerung auf eine Aufgabenpopulation.
- **Verworfen:** mein eigener Vorschlag „Mindesteffekt relativ zum Pilotmittel“. Codex hat recht: Δ ist ein dimensionsloses Log-Verhältnis, eine Skalierung fällt heraus.
*Ergebnis:* **Nicht eingefroren.** Reparaturliste im Entwurf `lab/confirm/P1_REGISTRATION_DRAFT.md`. Das ist Code-Arbeit, sie geht auch außerhalb des Fensters. Nach den Korrekturen nur
die betroffenen Punkte nachprüfen lassen (Regel 18c).

**Zyklus 15 (Reparaturliste P1 umgesetzt, 03:42–03:45 gemessen).** Alle Codex-Punkte am Code umgesetzt, jeweils mit Selbsttest (über den Wächter, alle grün):
B4/H3 (Commit 48e7afb: alle geplanten Paare nötig, Δ endlich und Zielsummen > 0, „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 1), H6 (664b5ac: Split-Indizes/Ziele/Arm/Seed
gegen `build()` bei `--analyze`), B1 (93586fb: `code_sha256` im Manifest über Trainer, Split-, Analyse- und Ladercode sowie `training/grokverse`, geprüft bei Splits, `--jobs`, `--analyze`),
B2/H5 (b750fb1: `primary_task` = add 113 in der P1–P3-Familie mit 3 Gliedern, übrige Aufgaben als eigene sekundäre Familie; die Power bei α/3 passt damit). Texte zu H7/M8/M9 und die
Wiederholungsregel stehen im Entwurf. Beim Selbsttest fiel ein falscher Sollwert auf (Holm ist monoton), korrigiert. Codex prüft nur die geänderten Stellen nach (Regel 18c), das Ergebnis folgt.

### STATE-Archiv (Sitzung 20, 03:46): Ablauf 18b der Nacht 26./27.09., erledigt

## Verbindlich jetzt: Regel 18 (Astra-Review umsetzen), Nacht 26./27.09.

- **NUTZER 27.09. 02:25: Läufe ab SOFORT erlaubt, nicht erst 03:00** (Sperre im Wächter entfernt; `--check` zeigt `allowed: true`). Schritte unten sofort beginnen.
- 18a vollständig (Punkte 3, 10, 16, 11, 17, 5; 18c Programm A/B/C), alles **ungetestet** bis 03:00. Offen: EXP-034-Port (nach P3-Design).
- **Nächste Sitzung ab 03:14 (Sitzung 16 hat den Kreuzblock ergänzt, sonst nichts offen):** bis 03:00 nichts Pflichtiges offen (Sitzung 15: N30-Fenstermodell, EXP-054 und Lesarten für EXP-041/042 vor den Läufen eingefroren). Ab 03:00 Schritte unten.
- Stand je Punkt: Tabelle „Umsetzung“ am Ende von [[reviews/ASTRA_2026-09-26]].

## Wiederaufnahme ab 03:00 (18b), genau in dieser Reihenfolge

1. `python lab/tools/guarded_run.py --check` → `allowed: true`. Keine andere Queue aktiv (`ps -ef | grep -E "night_program|queue|guarded_run" | grep -v grep`).
2. Wächter-Abnahme **(Sitzung 18: als Skript)**: `powershell -ExecutionPolicy Bypass -File lab/tools/accept_guard.ps1` (≈ 1 min; Proben A STOP, B/C Wächter hart beendet mit System- bzw. venv-Python; Ergebnis `lab/runner/logs/accept_guard.json`; löscht STOP selbst). Von Hand wie bisher: `python lab/tools/guarded_run.py -- python -c "import time; time.sleep(60)"` im Hintergrund, währenddessen
   `lab/STOP` anlegen → Exit 3 und Kind beendet? **STOP sofort wieder löschen**, im JOURNAL vermerken. Scheitert es: Blocker in LIVE.
3. Tests **(Sitzung 19: alle in einer Liste, nach Schritt 2, nie gleichzeitig mit accept_guard):** `python lab/tools/parallel_queue.py lab/runner/tests_s19.txt --workers 3 --min-minutes 5`.
   Einzeln wie bisher, je `python lab/tools/guarded_run.py [--min-minutes 5] -- python <datei> [arg]`: `lab/experiments/EXP-001-freq-ban/test_freq_ban.py` (Sitzung 18 ergänzt); `lab/tools/result_loader.py`;
   `lab/tests/test_freq_ban_fingerprint.py` (--min-minutes 5; kleine CPU-Läufe im Temp-Ordner); `lab/tests/test_night_program.py`;
   **neu (Sitzung 14):** `lab/experiments/EXP-052-oos-mask-prediction/exp052.py --selftest`, `lab/tools/pilot_power.py --selftest`,
   `lab/tools/confirm_splits.py --selftest`, `lab/tools/confirm_p1.py --selftest`, **neu (Sitzung 19):** `lab/tools/trainer_guard.py --selftest`. Scheitert etwas: beheben, bevor Queues starten
   (die vier neuen blockieren die Nachtqueues nicht, nur ihre eigene spätere Auswertung).
4. GPU: `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1` im Hintergrund (Plan: `--dry-run`). Beginnt mit GPU-001
   (**Sitzung 18: Stufe 0 `components`, Astra 9** → Regression → Gleichwertigkeit → Durchsatz); ohne PASS keine GPU-Läufe. Danach EXP-043 → 046 → 047 (+ EXP-051) → 048 → 049 → 044 → 045.
   Wiederaufnahme = derselbe Befehl (Fertiges wird per Fingerprint übersprungen). Status: `lab/runner/logs/night_*/night_status.json`.
   Ist das GPU-Programm vor ≈ 11:00 fertig (GPU-001 bestanden): EXP-050 nachschieben (`--experiments GPU-001,EXP-050`, Paket C, 60 Läufe).
5. CPU **erst nach GPU-001**, **Sitzung 19: EXP-014 ans Ende** (Exploration, ≈ 5,5 Worker-Stunden, blockierte sonst die Paket-B-Piloten für P3):
   `python lab/tools/night_program.py --cpu --experiments EXP-035,EXP-038,EXP-041,EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1` (alte Standardfolge: EXP-014 → 035 → 038 → 041 → 036 →
   039 → 040 → 042). Nicht portiert: 034 (nach P3-Design); 018/022/023/010 zurückgestellt ([[BACKLOG]] „Sichtung nach Regel 18c“).
   **Wenn GPU-001 scheitert:** kein GPU-Lauf; sofort `--cpu --cpu-workers 3` (Zahl **explizit** angeben: ohne Throughput-PASS nimmt der Code sonst 1 Worker, Sitzung 17). Paket A danach auf der CPU (Sitzung 15, geprüft, ungetestet):
   `python lab/tools/night_program.py --paket-a-cpu --experiments EXP-043,... [--cpu-workers N]` (≈ 300 Läufe, mehrere Fenster;
   neben `--cpu` Threadsumme ≤ 12). Auswertungen von Hand dann mit `LAB_PAKET_A_DEVICE=cpu`.
6. Beobachten (Regel 14). GPU-001-Verdikte ins JOURNAL (Gleichwertigkeit, s/Schritt, J). Punkt 9: GPU bleibt experimentell.
7. Auswerten: `python lab/tools/night_report.py`; **vor jeder Deutung** [[LESART-nacht-2026-09-27]] lesen.
8. **Eingefrorene Vorhersagen (Sitzung 14), nach den jeweiligen Läufen, alle über den Wächter:**
   - EXP-052 (Paket C): `lab/experiments/EXP-052-oos-mask-prediction/exp052.py`, sobald die R-Arme von EXP-043, 046, 048 fertig sind (Holm fest über vier).
   - EXP-039 (CPU): `lab/experiments/EXP-039-lr-clock/eval_pi.py` (π gegen drei Uhren, `predictions_pi.json`, nur beschreibend).
   - EXP-044 (GPU): `lab/experiments/EXP-044-generalize-lockin/pi_persistence.py` (π gegen EXP-020, Lesarten (i)/(ii) in der README).
   - **Neu (Sitzung 15):** EXP-054 nach EXP-036: `lab/experiments/EXP-054-window-oos/n30_window.py` (erst `--selftest`); EXP-042 nach dessen
     Hauptauswertung: `lab/experiments/EXP-042-bias-strength/pi_window.py` (erst `--selftest`, EXP-020-Regression). Beide nur beschreibend.
9. **Vor dem Einfrieren von P1:** `lab/tools/pilot_power.py` (Δ_pow-Pilotstreuung, n für Power 80 %; vorher prüfen, dass die summary.json von
   EXP-048/049 aus dieser Nacht stammt). Bestätigungsblock dann mit `confirm_splits.py --manifest …` und `confirm_p1.py --jobs/--analyze …`
   (nur mit committetem Manifest; Seeds 1000–1099). P3 vorher schärfen: primär Wechsel bei t = 25 (Decke bei 150), Maß π, Überlappung nach EXP-053.
   Gekreuzter Split×Init-Block (Astra 5) ist entschieden (Sitzung 16): ins Manifest `"cross": {"task": "add", "p": 113, "seeds": [erste 5], "inits_per_seed": 2}`
   (20 Zusatzläufe, sekundär; Lesart in `confirm_p1.py`). EXP-014 bleibt Exploration.


**Zyklus 16 (Codex-Nachprüfung der P1-Korrekturen, 03:46–03:54 gemessen).** *Codex:* B2, B4/H3 und H6 sind im Code richtig. Der Registrierungstext und der Docstring beschrieben noch die alten Regeln
(das stimmt, selbst gelesen), jetzt nachgezogen. `paket_a_device.py` fehlte in den Code-Hashes (wird über EXP-043 `analyze.py` importiert, stimmt), jetzt ergänzt. Die Starter `parallel_queue`/`guarded_run` sind
bewusst ausgenommen (kein Rechencode, Dateien des Nutzers). **B1 bleibt ein Blocker:** Die Trainer prüfen den eingefrorenen Code nicht selbst, und der Lader bindet die Läufe nicht an den Digest.
Das berührt den gemeinsamen Trainer, deshalb in der nächsten Sitzung mit Codex-Prüfung. Selbsttests grün. **P1 bleibt uneingefroren.**
Nebenbei: CPU-Programm mit 3 Arbeitern neu gestartet (03:47), dabei einen Fehler behoben: `take_lock` stürzte bei verwaister Sperre ab, weil die deutsche `tasklist`-Ausgabe (Umlaut) nicht dekodiert wurde und stdout None blieb (Commit 1b0e94f).

**Zyklus 17 (offener Rest EXP-046, 03:55–03:56 gemessen).** Die vorab angekündigten beschreibenden Zusätze nachgetragen: Top-3-Δ = 6.0 (Maximum) in 10/10 Seeds, die drei stärksten Irreps sind immer
Ziele des eigenen Arms. Δ_pow 2.72 ± 0.45 (aus `pilot_power`). Keine Änderung am Urteil *steuerbar*.

**Korrektur (03:56 gemessen): LAB.md.** Mehrere Tabellenzeilen hatte ich über das *erste* Vorkommen des Versuchslinks gesucht. Bei EXP-043 lag das in einem alten „Lage“-Absatz, deshalb standen
die EXP-044/045-Zeilen außerhalb der Tabelle, und die Aktualisierungen für EXP-048/049/050 hatten den Lage-Absatz aus Sitzung 13 überschrieben (Regel 10 verletzt: bestehende Inhalte nicht
umschreiben). LAB.md aus dem Stand vor der Sitzung (fa7507e) neu aufgebaut: alter Absatz wörtlich wiederhergestellt, nur Tabellenzeilen aktualisiert, neue Zeilen EXP-044/045/055, neuer Lage-Absatz
Sitzung 20. Die übrigen Dateien (READMEs, FINDINGS, BACKLOG, JOURNAL) wurden nur mit eindeutig geprüften Zeichenketten geändert (assert count == 1), also nicht betroffen.

**Rückblick nach Regel 4 (Zyklen 1–17):** *Gelernt:* Ja, viel. Das ist die erste Nacht mit Läufen seit Sitzung 10, und alle Verallgemeinerungsfragen aus FINDINGS haben jetzt ein Pilot-Urteil.
*Wiederholen wir uns?* Nein. Die Versuche waren vorab festgelegt und liefen mit ≥ 10 Seeds. *Messungen geeignet?* Für Repräsentation ja (Δ, Δ_pow, π). Für Funktion **nein**: Die Genauigkeit liegt
am Boden, der Loss braucht eine vorab gewählte Teildosis. *Nächste Annahme, die wir gezielt angreifen:* dass die Pilotergebnisse an frischen Seeds und Splits halten (P1-Bestätigung), und die
Theorie erster Ordnung (EXP-050 zeigt schon eine Lücke: M0 trägt mit).

### Abschlussbericht Sitzung 20 (Stand 04:01 Berlin, gemessen; Auftrag §10)

**Wichtigste Befunde (alle Pilot, je 10 Seeds, Urteile vorab festgelegt, GPU nach bestandenem GPU-001):**
- K2 (Steuerung der Frequenzwahl über die Daten) hält außerhalb von add 113: add 97, mul 113, D₅₉ (nicht-abelsch), nicht-modulare Addition, 4× Breite, MLP. Jeweils 10/10, p 0.001.
- Mechanismus: Die Paarstruktur trägt, die Häufigkeiten allein nicht (EXP-047). Das kohärente M0c wählt, aber M0 trägt mit (EXP-050, Theorie erster Ordnung nur halb). Die eingefrorene
  Masken-Vorhersage trifft 4/4 unberührte Fälle (EXP-052).
- K4 (frühe Festlegung) hält bei add 97/mul 113 mit nur ≈ 38 % geteilten Paaren. Der Kipp liegt zwischen t 25 und 50 (EXP-044, Lesart (i)).
- Die gepflanzte Wahl klingt nach dem Grokking nicht ab (EXP-016 post hoc bis 2000; EXP-045 MLP bis 10 000: 10.0 → 7.9). Das ist der Unterschied zu Zhou et al. 2024.
- Funktion (P2) unklar: EXP-051 Bodeneffekt, EXP-055 Hauptdosis n. s., Teildosen 10/10 (post hoc).
- Technik: GPU gleichwertig und ≈ 17× schneller, J = 8 am besten. Behoben: venv-Pfad (CreateProcess), `compare.py` bei abgebrochener Diagnose, Stale-Lock bei deutscher `tasklist`-Ausgabe,
  zwei Testaufbau-Fehler, dazu (vom Nutzer-Assistenten) das Job-Objekt im Wächter. Die CPU-torch der venv ist 10× zu langsam.

**Offene Grenzen:** alles Pilot, keine Bestätigung. P1 nicht eingefroren (Codex: B1-Trainerbindung offen). Häufigkeits-Confound in D₅₉/int-add. Nur 2000 Schritte (außer MLP). CPU-Piloten
Paket B (EXP-035–042) laufen noch.

**Reproduktion:** GPU-Nacht: `python lab/tools/night_program.py` (+ `--experiments GPU-001,EXP-050`); Auswertungen `python lab/tools/guarded_run.py -- python lab/experiments/<EXP>/analyze.py`,
EXP-052 `exp052.py`, EXP-044 `pi_persistence.py`, EXP-055 `analyze.py`, `lab/tools/pilot_power.py`; Logs `lab/runner/logs/night_20260927T005025_010314Z/`, `night_20260927T013514_874246Z/`.

**Nächste Aktion:** CPU-Programm neu starten (Befehl in [[STATE]]), dann B1 (Trainer-Bindung an `code_sha256`, mit Codex-Prüfung), dann P1 einfrieren und auf der GPU rechnen.

**Runner:** Die geplante Aufgabe „GROKVERSE-Lab-Runner“ ist aktiv. Nächster Start laut `runner-state.json`: 2026-09-27 03:04:44Z = **05:04 Berlin**. Die CPU-Läufe werden um 04:29 vom Wächter beendet
(Sitzungsdeadline). Die Folgesitzung setzt mit demselben Befehl fort.

**Nachtrag 04:18 (gemessen):** Das CPU-Programm hat EXP-035 abgeschlossen (Auswertung 04:13): formales Urteil „Festlegung hängt am Lernratenplan: Warmup verzögert (H35-Richtung)“, **n_evaluable = 3**.
**Noch nicht gedeutet und nicht in FINDINGS:** In der Folgesitzung zuerst die README-Lesart und die Mindestzahl prüfen (3 Seeds sind nach Regel 15b kein tragfähiges Urteil). Seit 04:13 läuft EXP-038.
Die Sitzung endet mit laufenden CPU-Jobs. Der Wächter beendet sie um 04:29 (Sitzungsdeadline), die Folgesitzung setzt mit demselben Befehl fort.

## Sitzung 21 (2026-09-27, Start 04:19 Berlin, Deadline 07:19; vom Runner)

**Start (04:19–04:20 gemessen):** Fenster offen, kein STOP, keine Python-Prozesse. CPU-Programm (Paket B) mit 3 Arbeitern × 4 Threads neu gestartet
(GPU frei, Threadsumme 12). EXP-035 wurde übersprungen (fertig), jetzt läuft EXP-038.

**Zyklus 1 (EXP-035 einordnen, 04:20–04:25).** *Frage:* Trägt das formale Urteil aus Sitzung 20? *Ergebnis:* Nach der eigenen Festlegung (≥ 3 auswertbare Seeds,
alle verzögert) ja: Seeds 30, 31, 34 verzögert ((25, 50] → (50, 100] bzw. (100, 150]). Seed 32 ist wegen einer nicht monotonen Warmup-Kurve nicht auswertbar, zeigt
aber dieselbe Richtung. Nach Regel 15b ist n = 3 nur ein **Pilot** (Vorzeichentest p = 0.125, beschreibend). Die Schrittuhr trifft bei keinem Seed zu, die Λ-Uhr ist weder
gestützt noch widerlegt (Seed 30 fixiert in Λ-Einheiten eher früher). *Entscheidung:* README-Ergebnis und LAB-Zeile nachgetragen, nicht in FINDINGS als Kernaussage.
Die Uhrfrage beantwortet EXP-039.

**Zyklus 2 (B1: Läufe an den eingefrorenen Code binden, 04:20–04:24).** *Frage:* Wie schließen wir die letzte Blocker-Lücke vor dem Einfrieren von P1, ohne den
gemeinsamen Trainer anzufassen? *Änderung:* Wrapper `confirm_p1.py --run` (Prüfung vor und nach dem Lauf, Bindungsdatei mit Hashes aller geschriebenen Dateien),
`--analyze` verwirft ungebundene Läufe (Commit feedd8f). *Ergebnis:* Selbsttests `confirm_p1` und `confirm_splits` grün (über den Wächter), inkl. Ende-zu-Ende mit
Scheintrainer (gebunden → angenommen; geänderte/zusätzliche Datei, falscher Digest/Commit, Exit ≠ 0 → abgelehnt). Unterwegs: Das Patch-Skript schrieb die Datei mit LF,
die Datei ist CRLF. Ich habe die CRLF-Endungen wiederhergestellt, damit der Diff nur die echte Änderung zeigt. *Entscheidung:* Codex-Nachprüfung (Regel 18c, Änderung am Lader), dann einfrieren.

**Zyklus 3 (Codex prüft B1, 04:25–04:33 gemessen).** *Codex (7 Punkte, 3 als Blocker):* (1) Code wird nur vor und nach dem Lauf geprüft; ändern und zurücknehmen
während des Laufs bliebe unbemerkt. (2) Die Bindung über `mtime ≥ Start` kann einen übersprungenen, fremden fertigen Lauf binden (z. B. nach Uhrrücksprung).
(3) Prüfen und Laden sind getrennt (TOCTOU). (4) `--run` nimmt jeden Befehl mit den passenden Flags an. (5) Nur `.py` gehasht, ein untergeschobenes `.pyc` liefe.
(6) Der Split-Hash sortiert, die Reihenfolge ist nicht gebunden. (7) Der committete Matcher verwechselt Haupt- und Kreuzläufe desselben Splits.
*Selbst geprüft:* Alle stimmen technisch. (7) hatte ich schon vorher selbst gefunden und behoben (83378f8). (6) ist praktisch folgenlos, weil beide Trainer
Full-Batch trainieren (Reihenfolge egal). (2), (3), (5) sind eher Angriffsszenarien als Versehen. Weil die Behebung billig ist, habe ich trotzdem **alle übernommen**
(0d85983, ce7880e): Befehl muss in der eingefrorenen Jobliste stehen; Code-Prüfung alle 2 s während des Laufs (Änderung → Trainer beendet, keine Bindung); frischer
Bytecode-Cache pro Lauf (`PYTHONPYCACHEPREFIX`); Bindung aus Vorher-/Nachher-Zustand statt Zeitstempeln, gebundener Lauf → übersprungen, fremder fertiger Lauf → abgelehnt,
erfolgreicher Lauf ohne neues result.json → Exit 4; beim Auswerten Prüfen–Laden–Prüfen und exakte Split-Bytes über `fingerprint_fields.split_file_sha256`.
Rest (dokumentiert, nicht behoben): Eine Änderung, die kürzer als 2 s besteht, und Bibliotheken außerhalb des Repos (torch) sind nicht gebunden.
*Eigener Fehler:* Nach dem ersten Fix habe ich mit `… | tail && git commit` committet, und dabei zählte der Exit-Code von `tail`. So kam ein roter Selbsttest in Commit 0d85983,
ce7880e behebt ihn. Selbsttests `confirm_p1`, `confirm_p2`, `confirm_splits` jetzt grün.

**Zyklus 4 (P2 vorbereiten, 04:26–04:31).** *Frage:* Kann P2 (funktionale Nutzung) zusammen mit P1 eingefroren werden, bevor ein Lauf startet? *Änderung:* Die P1-Hauptläufe
add/mul speichern `model_final.pt` (5b03b7c; Training und Lauf-ID unverändert). Entwurf [[confirm/P2_REGISTRATION_DRAFT|P2]]: ΔL bei f = 0.5 an den 50 P1-Modellen add 113,
Vorzeichentest, Holm P1–P3, „bestätigt“ = alle gültig, Holm-p < 0.05, KI-Untergrenze > 0. Auswertecode `confirm_p2.py` (935155b), steht in den eingefrorenen Code-Hashes.
*Power aus EXP-055 (f = 0.5):* D̄ = 5.9·10⁻⁴, SD 3.6·10⁻⁴, d_z = 1.63. Bootstrap-Power bei α/3 für n = 20: 0.997 bei halbem Effekt. Ein Verhältnis ΔL_own/ΔL_ctrl als
Mindesteffekt geht nicht, weil ΔL_ctrl im Pilot teils negativ ist. *Stand:* Codex prüft den P2-Entwurf.

**Zyklus 5 (P2-Maß und Registrierungslücken vor dem Einfrieren, 04:33–04:38 gemessen).** *Frage:* Misst das P2-Maß, was die Aussage behauptet, und deckt der Code
alles ab, was die Registrierung verspricht? *Ergebnisse:* (a) Das rohe D gewichtet Modelle nach ihrem Basis-Loss. Seed 157 G (Basis-Loss 2·10⁻⁷) trägt praktisch nichts bei.
→ primär jetzt das skalenfreie R = log(L_nach,own/L_nach,ctrl), Mindesteffekt log 1.05; Pilot R̄ = 0.150, SD 0.065, 10/10 (bereits gesehen, im Entwurf vermerkt).
(b) Geometrie: Bei f = 0.5 ist die Störung entlang der Ziele nur ≈ 5 % der quadrierten Kontrollstörung. R > 0 folgt also nicht aus dem Eingriff selbst.
(c) Der t-Test (H7, sekundär) stand in der Registrierung, fehlte aber im Code. Nachgetragen, ohne scipy (unvollständige Betafunktion, gegen die geschlossene Form bei df = 2 und
einen Tabellenwert geprüft; meine erste Testerwartung 1/27 war falsch, der Code war richtig). (d) Der frische Bytecode-Cache pro Lauf hätte torch in jedem der 420 Läufe neu
übersetzt. Jetzt nutzen alle Jobs eines Einfrierens einen Cache, der an den Code-Digest gebunden ist (5290b63). (e) `lab/confirm/raw/` stand nicht in .gitignore, ergänzt.
GPU bereit (RX 7900 XT, 21 GB frei). Die Jobliste aus dem Entwurf hat 420 Zeilen, keine Backslashes.

**Zyklus 6 (P3-Pilot EXP-056 festgelegt und gestartet, 04:40–04:45 gemessen).** *Frage:* Hält das Netz die Frequenzwahl nach einem frühen Wechsel (t = 25) fest, weil es sich
festgelegt hat (i), oder nur, soweit die Splits Paare teilen (ii)? Die Frage stand seit Sitzung 13/14 im [[BACKLOG]] („Entwurf P3“), die Konstruktion (EXP-053) war fertig, aber ungenutzt.
*Vergleich der nächsten Schritte:* (a) warten, bis Codex P1/P2 freigibt, bei leerer GPU; (b) P3-Pilot jetzt festlegen und rechnen, denn er liefert die Streuung für P3 und
entscheidet zwischen zwei benannten Konkurrenzmodellen (Regel 18c); (c) FINDINGS nachführen. (b) gewählt. *Festlegung:* [[experiments/EXP-056-overlap-persistence/README|EXP-056]]
(04:43, vor jedem Split und Lauf): ω ∈ {0, 0.2, 0.4}, Seeds 400–409 (nie benutzt), 4 Arme je Stufe, π je Stufe, primär die Steigung b von π über ω (t-Test).
Äquivalenzgrenze |b| ≤ 0.25 (Δπ ≤ 0.1). *Splits (04:43):* Steuerstärke je Stufe 0.18, Kreuzanteile auf Zufallsniveau, wie in der Kalibrierung. *Smoke (04:44):* Der Lauf ging,
aber mein Suchmuster war falsch: freq_ban benennt reine Läufe mit Testdatei `EXP-018_…` und Wechselläufe `EXP-020_…`, nicht nach dem Ausgabeordner. Muster vor jedem echten
Lauf korrigiert (`EXP-0*`), an beiden Namensformen geprüft. *Start 04:45:* 120 Läufe, 8 parallel auf der GPU (`lab/runner/logs/exp056_queue.log`).

**Zyklus 7 (Codex-Nachprüfung, Einfrieren P1+P2, 04:45–04:50 gemessen).** *Codex (Nachprüfung):* Die Befunde 2, 4, 6, 7 und P2-1…5 sind geschlossen. `_betainc` stimmt im
Bereich df = 49 mit einer unabhängigen Quadratur überein. `shlex` erzeugt dieselbe Argumentliste wie die echten Jobzeilen. Beide Trainer schreiben `split_file_sha256`.
Offen nach Codex: (a) Ändern und Zurücknehmen innerhalb von 2 s, (b) untergeschobenes .pyc im Cache, (c) P2 lädt das Modell nach dem letzten Hash (TOCTOU), (d) E = E_own abgelehnt.
Neu: (e) Die Bindung speichert Exit 0, obwohl der Wrapper 4 meldet. (f) Andere Ausnahmen lassen den Trainer verwaist laufen.
*Entscheidung:* (a) und (b) **verworfen** (Begründung: beides verlangt absichtliche Manipulation, gegen die ohnehin keine Datei geschützt ist; als Restrisiko in der Registrierung).
(c)–(f) **übernommen** (d2ac48f). P2 lädt jetzt genau die gebundenen Bytes; der neue Lader ist an einem EXP-047-Modell tensorgleich zum alten. Selbsttests grün.
*Eingefroren 04:46:* Manifest 733e829 (60 Code-Hashes), Commit-Feld 0cd5ee5, `check_manifest` ok. 600 Splits und 420 Jobs (6babde7).
*Smoke mit zwei echten Jobs (04:48–04:49):* add 113 und D₅₉, Seed 1000 F. Beide Exit 0, beide gebunden (inkl. `model_final.pt`), `unbound` = None, der Matcher findet genau ein Verzeichnis.
Unter Last (EXP-056 auf der GPU, CPU-Queue) dauert ein Lauf ≈ 60 s. *Nächster Schritt:* Die übrigen 418 Jobs starten, sobald EXP-056 die GPU freigibt.

**Zyklus 8 (EXP-038 einordnen, 04:51 gemessen).** *Frage:* Welcher Teil des Netzes hält die Frequenzwahl nach 150 Schritten fest? *Ergebnis (CPU-Programm, Auswertung 04:46):*
formal ***redundant***, 5/5. Rücksetzen nur von W_E (RW) oder nur des Rests (RR) → nach 2000 G-Schritten trägt W_E wieder die F-Frequenzen (d_h 4–5), Test-Acc 1.0.
Bei RW schreibt der Rest die F-Wahl in ein W_E zurück, das auf der Init stand (Train-Acc nach dem Rücksetzen 0.06–0.09). *Deutung (vorsichtig):* Nach 150 Schritten ist die
Festlegung doppelt vorhanden. Das passt zu EXP-044 Lesart (i) („Festlegung im Netz“) und ist ein Hinweis für EXP-056. *Einordnung:* Pilot (n = 5, bekannte Seeds), keine Kernaussage.
*Folgefrage (nicht automatisch verfolgen, Regel 15b):* Welcher Teil des Rests genügt (Attention, MLP, W_U)? Und gilt das auch bei t = 25, wo die Persistenz noch nicht an der Decke ist?

**Zyklus 9 (EXP-056 auswerten, 04:56–04:58 gemessen).** *Frage:* Trägt das Netz oder die Datenüberlappung die Persistenz nach einem Wechsel bei t = 25?
*Ergebnis:* 120/120 Läufe ok. Die erste Auswertung war leer. Ursache: mein Kommentar mitten in der Musterzeile (Fehler aus der Smoke-Korrektur, bei der ich nur feste Muster
statt der Funktion geprüft hatte). Behoben vor dem Blick auf Ergebnisse (db71203). Primär ***unklar***: b̄ = 0.11, p = 0.25, 90-%-KI [−0.18, 0.41]. Beschreibend: π(ω = 0) = 0.30 ± 0.14,
10/10 > 0; π flach über ω (0.30/0.38/0.35), beide Richtungen gleich (0.34/0.34). *Deutung:* Die reine Form von (ii) ist unwahrscheinlich, denn es gibt Persistenz ohne geteilte Paare.
Ein Anteil von (ii) ist nicht ausgeschlossen. Offene Alternative: eine passive Gewichtsspur (Rechnung ≈ 14 % Rest nach 2000 Schritten, keine Kontrolle).
*Entscheidung:* P3 mit Kandidat (a) „Persistenz ohne geteilte Daten“ vorbereiten, **mit einer Spur-Kontrolle** (z. B. A→B, bei dem nach 25 Schritten der AdamW-Zustand zurückgesetzt
wird, oder A-Schritte mit kleiner Lernrate bei gleicher Strecke), vor dem Einfrieren Codex-Prüfung.

**Rückblick nach Regel 4 (Zyklen 1–9, Sitzung 21):** *Gelernt:* Ja. Die Festlegung ist doppelt vorhanden (EXP-038), Persistenz entsteht auch ohne Datenüberlappung (EXP-056),
Warmup verzögert (EXP-035). Alles Piloten, aber sie zeigen in dieselbe Richtung: Die Festlegung sitzt im Netz. *Wiederholen wir uns?* Nein: P1/P2 sind eingefroren, der Block läuft.
*Messungen geeignet?* π ist trennscharf für das Niveau, aber zu verrauscht für Steigungen bei n = 10. *Fehlerquelle dieser Sitzung:* dreimal eine eigene Prüfung, die nicht das
prüfte, was lief (Exit-Code von `tail`, feste Muster statt der Funktion, relative Pfade im Test). *Lehre:* Den echten Codepfad am echten Objekt testen.

**Zyklus 10 (passive Spur als Erklärung für π(0) > 0, 04:59 gemessen, post hoc).** *Frage:* Ist die Persistenz ohne geteilte Paare nur ein Rest der 25 A-Schritte in W_E?
*Methode:* π ist ein reines W_E-Maß, gleiche Init je Seed → Vorhersage der passiven Spur rechnen: W_E(reiner zweiter Lauf) + c·(W_E^A(25) − W_E(0)). *Ergebnis:* π_Spur = 0.003 (c = 0.135)
bzw. 0.063 (c = 1, obere Grenze), beobachtet 0.34. *Entscheidung:* Die passive Spur ist als Erklärung ausgeschlossen (beschreibend, aber der Abstand ist groß). Die Rechnung wird
als vorab festgelegte Kontrolle in P3 übernommen. Das Bild aus EXP-038, EXP-056 und diesem Befund: Das Netz verstärkt eine sehr frühe Wahl aktiv, und die Wahl ist im Netz verteilt.

**Zyklus 11 (P3 vorbereiten, 05:00–05:04 gemessen).** *Frage:* Lässt sich „Persistenz ohne geteilte Daten, über eine passive Spur hinaus“ als Bestätigung festlegen?
*Entwurf:* [[confirm/P3_REGISTRATION_DRAFT|P3]]: D = π(ω = 0) − π_Spur(c = 1), 30 Seeds (1050–1079), t-Test, Holm im ungünstigsten Fall, Mindesteffekt 0.05 (KI-Untergrenze).
Die Wahl 0.05 statt 0.1 folgt aus der Bootstrap-Power am Piloten (bei n = 30 und 60 % des Pilot-Effekts nur 0.56 für 0.1). *Technik:* eigenes Modul `confirm_p3.py`
(18eb7d3), denn der laufende P1-Block ist an die Hashes von `confirm_p1.py` gebunden, und jede Änderung dort würde ihn stoppen. Die Laufverzeichnisse werden exakt aus dem Befehl
bestimmt (Wechselläufe tragen beide Stämme). *Prüfung:* Selbsttest grün. Der Auswertepfad lief an echten EXP-056-Daten (drei Seeds, zwei Stufen, unter P3-Namen kopiert):
π und beide Spurvarianten stimmen auf 6 Stellen mit EXP-056 überein. Normierungsspanne L(A) − L(B) im Piloten 5.7–9.9, π also stabil. *Stand:* Codex prüft P3.

**Zyklus 12 (Codex prüft P3, 05:04–05:13 gemessen).** Die Codex-Weiterleitung (`codex:codex-rescue`) hat die Prüfung diesmal **im Hintergrund** gestartet und durfte das Ergebnis
nicht selbst abholen (Regel 12 verlangt Vordergrund). Ich habe es mit `node …/codex-companion.mjs result task-muj8j25d-cf78hp` abgeholt. *Lehre:* Für Codex künftig direkt
`codex-companion.mjs task "<prompt>"` ohne `--background` aufrufen (wartet bis zum Ergebnis). *Codex:* 3 Blocker (Spurkontrolle ist keine obere Grenze; Normierung instabil;
Manifest erzwingt die Registrierung nicht), 2 schwere Befunde (Herkunft unvollständig, EXP-046-Importe; Wiederaufnahme bindet Reste nicht zuverlässig), 1 leichter (cuda:0).
*Selbst geprüft:* alle zutreffend, **alle übernommen** (54f1e73; Details in [[confirm/P3_REGISTRATION_DRAFT|P3]]). Die Aussage ist jetzt enger: Persistenz über eine statische additive W_E-Spur hinaus.
Kontrolle = Maximum über c ∈ [0, 1], gültig nur bei L(A) − L(B) ≥ 2. Die Pilotvalidierung (echte EXP-056-Daten) liefert unverändert dieselben Werte, dort liegt das Maximum bei c = 1.
Ein eigener Testfehler (Prüfung an die falsche Stelle eingefügt, „letzte Bindung“ nach mtime) ist behoben. Selbsttest grün. *Stand:* Codex prüft die Korrekturen im Vordergrund.

**Zyklus 13 (P3 eingefroren, 05:13–05:18 gemessen).** Codex-Nachprüfung im Vordergrund (direkt über `codex-companion.mjs task`, 05:13): Die Punkte 1–4 und 6 sind geschlossen.
Neu und übernommen (6a54652): Umbenennen trotz `run.lock` (jetzt Ablehnung), typstrenge Manifestprüfung, nicht-endliche L/Spur → ungültig. Selbsttest grün, Pilotvalidierung unverändert.
**Eingefroren 05:17:** Manifest f8adf45 (58 Code-Hashes), Commit-Feld c0da64e, Splits 60 Paare + 30 Testmengen (Steuerstärke 0.185/0.184 je Stufe wie kalibriert), 240 Jobs.
Die P3-Warteschlange startet automatisch nach dem P1-Block (`lab/runner/logs/p3_block.log`). P1-Block um 05:18: 203/420, keine Fehler.

**Zyklus 14 (P1- und P2-Block ausgewertet, 05:39–05:46 gemessen).** *Frage:* Hält die Steuerung der Frequenzwahl durch konstruierte Splits an 50 frischen Seeds und Splits je Aufgabe,
und nutzen die Modelle die Zielfrequenzen stärker? *Block:* 420/420 Läufe Exit 0, alle gebunden (04:48–05:39, GPU, 8 parallel, unter CPU-Last). *P1 (eingefroren ausgewertet):*
***bestätigt in 4/4 Aufgaben***: add 113 Δ_pow 8.24 [7.92, 8.54], mul 113 8.09 [7.75, 8.43], add 97 6.11 [5.79, 6.43], D₅₉ 2.64 [2.55, 2.73], jeweils 50/50 positiv,
Holm-p (ungünstigster Fall) 1.5·10⁻⁵. Kreuzblock stabil über Inits (ICC 0.77). *P2:* ***nicht auswertbar***. 3/50 Seeds verletzen „Basis-Genauigkeit ≥ 0.9“ (G-Arm bei Schritt 2000
noch nicht generalisiert: 0.82/0.70/0.73). Beschreibend R̄ = 0.12 (SD 0.20, 43/47), deutlich schwächer als der Pilot. *Entscheidung:* P1 geht nach der Codex-Prüfung der Schlussfolgerung
als Kernaussage in FINDINGS. P2 wird ehrlich als *nicht auswertbar* berichtet. Die strenge Gültigkeitsregel bei nur 2000 Schritten war mein Designfehler.
Ein Nachfolger braucht sicheres Grokking und eine Stichprobe aus der jetzt gesehenen Streuung. *Parallel:* P3-Block läuft (54/240 um 05:46).

**Zyklus 15 (Codex greift die P1-Schlussfolgerung an, 05:45–05:51 gemessen).** *Codex:* Nichts im Code oder Datenfluss erzwingt Δ_pow > 0. Bei gemeinsamer Init heben sich beide log-Verhältnisse
anfangs exakt auf, die Paarung senkt also nur die Varianz. Die Konstruktion ist ein gezielter Eingriff in genau der gemessenen Basis, aber kein Leck, denn der Trainer sieht nur Indizes.
Wortlaut: „zurückgehaltene Replikation“ statt „unabhängig“, relative Anreicherung statt Konzentration, Kreuzblock nur „stabil über diese drei Inits“ (ICC ungenau, enthält Init × Split).
P2: „nicht auswertbar, nur beschreibend“ ist richtig, und der Wert aus 47 Seeds kann durch die Auswahl verzerrt sein. Nachfolger: frische Seeds, längeres festes Training oder ein vorab
registrierter Konvergenzpunkt auf eigener Validierungsmenge, feste Ablations-Testmenge, geordnetes Nachziehen bis zu einer festen Zahl gemeinsam generalisierter Paare, Eignungsrate berichten,
Power gegen den Abstand über log 1.05 (≈ 0.37 SD → grob 60–80 Paare); für „je Energieeinheit“ Dosen nahe 0.
*Selbst geprüft und übernommen:* Wortlaut und Grenzen in [[FINDINGS]] (Abschnitt „BESTÄTIGT“), der Nachfolgeplan in [[BACKLOG]]. Verworfen: nichts.

**Zyklus 16 (P3-Block ausgewertet, 05:39–06:05 gemessen).** *Frage:* Hält das Netz nach 25 Schritten auf A dessen Frequenzpräferenz gegen 2000 Schritte auf B ohne ein einziges geteiltes Paar,
und zwar über eine statische W_E-Spur hinaus? *Block:* 240/240 Läufe Exit 0, gebunden. *Ergebnis (eingefroren ausgewertet):* ***bestätigt***. D̄ = 0.293 [0.263, 0.322], 30/30 > 0, t = 19.3,
Holm-p 6·10⁻¹⁸. π(0) = 0.351, maximale statische Spur 0.057. Sekundär: Überlappung 0 → 0.4 ändert π nicht messbar (0.005 [−0.030, 0.042]). Der Pilot EXP-056 ist damit repliziert
(an frischen Seeds, andere Split-Ströme). *Deutung (vorsichtig):* Zusammen mit EXP-038 (Festlegung doppelt vorhanden) spricht alles für eine sehr frühe Festlegung im Netz, die das weitere
Training aktiv trägt. Nicht gezeigt: welcher Mechanismus (Adam-Momente, Gewichtsnorm, Struktur im Rest). *Stand:* Codex greift die Schlussfolgerung an, besonders die Frage, ob der reine B-Lauf der richtige Nullpunkt ist.

**Zyklus 17 (Codex greift P3 an, EXP-057 als Folgeversuch, 06:05–06:23 gemessen).** *Codex zu P3:* Als registrierter Befund bestätigt. Die Lesart „Festlegung im Netz“ ist aber
nicht identifiziert: Ein unspezifisch langsameres Anpassen liegt zwischen den Endpunkten und erzeugt ebenfalls π > 0. Das habe ich selbst nachgerechnet und übernommen (FINDINGS im Codex-Wortlaut).
*Post hoc:* Die Ziele des ersten Splits tragen in den Wechselläufen 20 % der W_E-Leistung (Zufall 8.9 %), es gibt also eine A-spezifische Erhaltung, dazu eine langsamere Anpassung.
*EXP-057 (vorab festgelegt 06:16, Pilot, bekannte Seeds 400–409):* neue Trainer-Option `--reset-optim-at-switch` (5aa8c34; 16/16 Tests, Smoke). 40 Läufe, Auswertung 06:21: formal
***teilweise***. Δ̄ = 0.195 [0.13, 0.26], p = 0.0002, π_ro = 0.108 (Schwelle 0.1). **Beschreibend entscheidend:** Mit Reset liegen die A-Ziele unter Zufall (7.1 %), die A-spezifische Erhaltung ist also weg.
Die gleich lange Referenz ändert nichts. *Lesart (Pilot):* Das Gedächtnis der ersten 25 Schritte sitzt vor allem im AdamW-Zustand. Das widerspricht meiner Erwartung.
Neue Idee N28, Suche ohne Treffer (vorläufig). *Alternative:* Die vorzeichenartigen Schritte nach einem vollen Reset könnten die kleine Spur überschreiben. Trennen ließe sich das mit einem Reset nur von m (Schrittzähler bleibt).
**Versäumnis:** Die Trainer-Änderung 5aa8c34 lief vor dem Pilot ohne Codex-Prüfung (Regel 18c verlangt sie bei Änderungen am gemeinsamen Trainer). Tests und Smoke waren grün,
die Option ist ohne Flag wirkungslos. Die Prüfung läuft jetzt nachträglich. Wegen der geänderten Datei `freq_ban.py` besteht eine erneute Auswertung von P1/P2/P3 die Code-Prüfung nur noch aus
einem Checkout der eingefrorenen Commits (733e829 bzw. f8adf45). Die Ergebnisse sind berechnet und committet; das ist so gewollt.

### STATE-Archiv Sitzung 21 (Stand 05:18, wörtlich, ersetzt um 06:23)

> # lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)
> 
> _Zuletzt aktualisiert: 2026-09-27, 05:18 Berlin (Sitzung 21, Deadline 07:19)._
> 
> Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · [[LESART-nacht-2026-09-27]] · [[confirm/P1_REGISTRATION_DRAFT|P1-Entwurf]]
> 
> ## Lage
> 
> - Nacht 26./27.09. (Regel 18b) **erledigt**: Wächter-Abnahme A/B/C bestanden, alle Tests grün, **GPU-001 bestanden** (gleichwertig, ≈ 17× schneller, J = 8).
>   GPU-Programm komplett: EXP-043, 044, 045, 046, 047, 048, 049, 050, 051 und die Auswertungen 052, 055. Ergebnisse: [[FINDINGS]] „Pilotnacht“ (K2 und K4 verallgemeinern sich im Pilot).
> - Run-Fenster wieder normal 00:00–13:00 (die 03:00-Sperre gab es nur in der Nacht 26./27.09.; der Nutzer hat sie 02:25 aufgehoben).
> - Schritte 1–3 (Abnahme, Tests) **nicht wiederholen**. Das Archiv des Ablaufs steht im [[JOURNAL]] (STATE-Archiv Sitzung 20).
> 
> ## Aktive Queue / laufende Jobs
> 
> - **CPU (Sitzung 21 seit 04:20, 3 Arbeiter × 4 Threads, läuft EXP-038):** `python lab/tools/night_program.py --cpu --experiments EXP-035,EXP-038,EXP-041,EXP-036,EXP-039,EXP-040,EXP-042,EXP-014 > lab/runner/logs/night_cpu.log 2>&1`.
>   ≈ 5 min je Lauf, noch mehrere Fenster. Die Sitzungsdeadline bricht ab (Exit 124/3 = Ablehnung, kein Fehler). **Wiederaufnahme: derselbe Befehl** (Fertiges wird übersprungen).
>   Mit freier GPU kann der Arbeiter mehr Threads bekommen: `--cpu-workers 3` (Threadsumme ≤ 12). Nicht mischen (Regel 16d): Die CPU-Versuche bleiben auf der CPU.
> - **GPU:** frei. Kein offenes GPU-Programm.
> - **EXP-035 abgeschlossen (Sitzung 21):** Pilot n = 3, Warmup verzögert 3/3; keine Kernaussage (README „Ergebnis“).
> 
> ## Nächste Schritte (in dieser Reihenfolge)
> 
> 1. `python lab/tools/guarded_run.py --check`; kein STOP; laufende Prozesse prüfen; CPU-Programm (oben) wieder starten.
> 2. **P1+P2-Block rechnen (eingefroren 733e829, Sitzung 21):** `python lab/tools/parallel_queue.py lab/confirm/P1_jobs.txt --workers 8` (Hintergrund, GPU).
>    Fertig Gebundenes wird übersprungen („already bound“), also **Wiederaufnahme = derselbe Befehl**. Ein fremder fertiger Lauf wird abgelehnt (Exit 4); nie von Hand in `lab/confirm/raw` schreiben.
>    Danach `python lab/tools/guarded_run.py -- python lab/tools/confirm_p1.py --analyze lab/confirm/P1_manifest.json` und dasselbe mit `confirm_p2.py`.
>    Ergebnis erst nach Codex-Prüfung als Kernaussage in FINDINGS (Regel 18c). Bindungen `lab/confirm/bindings/` mitcommitten.
> 3. **P3-Block (eingefroren f8adf45, Sitzung 21):** `python lab/tools/parallel_queue.py lab/confirm/P3_jobs.txt --workers 8` (GPU; Wiederaufnahme = derselbe Befehl, gebundene Läufe werden übersprungen;
>    ein Rest mit `run.lock` wird abgelehnt → Sperre prüfen, von Hand beiseite legen). Dann `python lab/tools/guarded_run.py -- python lab/tools/confirm_p3.py --analyze lab/confirm/P3_manifest.json`.
>    EXP-056 (Pilot) ist ausgewertet: Steigung unklar, π(0) > 0 in 10/10.
> 4. Auswertungen nach den CPU-Läufen (eingefroren, über den Wächter): EXP-039 `eval_pi.py`; EXP-054 `n30_window.py` (nach EXP-036); EXP-042 `pi_window.py` (je erst `--selftest`).
> 5. Offene Reste: EXP-038-Folgefrage (welcher Teil des Rests genügt; t = 25); Folgeversuch EXP-050 (MLP mit getrennten W_in-Hälften); D₅₉/int-add Häufigkeits-Mischarm.
> 
> ## Drei Prioritäten (Regel 18c: Programm A/B/C)
> 
> 1. **A** Bestätigung P1 (Block 1000–1049), funktional P2 (Loss-Maß).
> 2. **B** Persistenz: CPU-Piloten EXP-035–042 fertig rechnen, P3 festlegen.
> 3. **C** läuft gut (EXP-052 4/4, EXP-050): erst nach A/B weiter, höchstens zwei Programme aktiv.
> 
> ## Blocker / Hinweise
> 
> - **Windows/venv:** `CreateProcess` findet `.venv-gpu/Scripts/python.exe` (relativ, Schrägstriche) nicht. `night_program.py` nutzt den absoluten Pfad, `confirm_p1.interp()` einen absoluten Pfad mit Schrägstrichen.
> - Die CPU-torch der `.venv-gpu` ist für CPU-Läufe ≈ 10× zu langsam. CPU-Läufe nur mit dem globalen Python.
> - Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`,
>   `runner-state.json`, `parallel_queue.py`) **nicht committen**; nur gezielt `git add <pfad>`, nie `commit -a`.
> - `guarded_run.py` (Nutzer, 27.09. ≈ 01:30/02:35): Der Wächter tritt vor dem Kindstart dem Job-Objekt bei, argtypes korrigiert. Seitdem keine Warnung mehr.
> - Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`). Shell-Skripte LF, JOURNAL/STATE/LIVE CRLF (bytegenau bearbeiten).
> - Neue `freq_ban.py`-Argumente nur bei Abweichung vom Standard in den Fingerprint (Sitzung 16).
> - Sitzungsgrenze: Ein abgebrochener Job am Deadline-Ende ist kein Fehler (Exit 124 → Ablehnung). Derselbe Befehl setzt fort.
> - Codex über den Subagenten `codex:codex-rescue` (nur lesend) funktioniert (Sitzung 20: zweimal).
> 
> ## Letzte abgeschlossene Versuche (Details [[LAB]], [[FINDINGS]])
> 
> - Sitzung 20 (Piloten, je 10 Seeds, vorab festgelegt): EXP-043 (add 97, mul 113), 046 (D₅₉), 048 (int-add), 049 (d 512), 045 (MLP): *steuerbar*; 047: Paarstruktur trägt;
>   044: *festgelegt*; 052: K1 4/4; 050: M0c wählt, M0 trägt mit; 051/055: Funktion unklar (Bodeneffekt / Hauptdosis n. s.).

**Zyklus 18 (Codex prüft 5aa8c34 und EXP-057, eingearbeitet 06:31).** *Code:* korrekt. Richtiger Zeitpunkt nach dem Optimiererschritt von Schritt 25; `opt.state.pop` setzt step, m und v
auf allen Backends vollständig zurück; die Fingerabdrücke bleiben kompatibel. Klein: Kombiniert mit `--reset-at-switch` gilt „Gewichte bleiben“ nicht; einen eigenen Regressionstest gibt es nicht.
*Deutung:* überzogen, und das stimmt (selbst geprüft). Ein voller Reset startet auch die Bias-Korrektur neu, und die vorzeichenartigen ersten Schritte können die Spur überschreiben.
„Unter Zufall“ ist nicht signifikant (t = −1.2). „Teilweise“ ist keine additive Zerlegung. *Übernommen:* Korrekturen in EXP-057, N28, FINDINGS, LAB, STATE (gestützt ist nur: Eine volle
Optimierer-Neuinit senkt die A-Persistenz). *Nächster Versuch:* nur m auf 0 (v und Schrittzähler bleiben) mit protokollierten frühen Update-Normen, dann Momente zurücksetzen bei erhaltenem Schrittzähler,
und ein voller Reset mit angeglichener Update-Norm. t = 150 erst danach (vermengt Alter, Spurgröße und Phase).

**Zyklus 19 (EXP-058 vorbereitet und gestartet, 06:32–06:38 gemessen).** *Frage:* Liegt das Gedächtnis im Adam-Momentum, oder überschreibt ein voller Reset die kleine Spur (Codex-Einwand zu EXP-057)?
*Technik:* `freq_ban.py --reset-optim-part m|moments` und `--log-update-norms N` (041f7a8). Der erste Smoke fand einen Fehler (`we_idx` nur mit keep_init gesetzt), behoben vor dem Commit.
17/17 Tests. Vier GPU-Smokes zeigen die Update-Normen nach dem Wechsel: normal 0.27–0.34, voller Reset 0.48–0.38 (größer), nur m 0.18–0.36 (kleiner), m + v 0.25–0.41.
*Codex (041f7a8):* keine Blocker, korrekt. Hinweise: Test steht nach dem `__main__`-Block (pytest findet ihn, direkter Aufruf nicht), kein Verhaltenstest für Reset und Logging.
„Nur m“ ist die richtige chirurgische Kontrolle für das erste Moment, aber keine vollständige Trennung von Gewichten und Optimierer (v trägt auch A-Geschichte). Bei der Auswertung paarweise
vergleichen und neben den Normen auch Richtungen prüfen. *Festlegung:* [[experiments/EXP-058-optim-part/README|EXP-058]] (06:36, vor jedem Lauf). *Start:* 80 Läufe, GPU.

**Zyklus 20 (EXP-058 ausgewertet, 06:50–06:51 gemessen).** *Ergebnis:* ***Momentum (m) trägt einen Teil der Persistenz***. Δ̄_m = 0.186 [0.13, 0.24], p = 0.0001. π normal 0.303, voller Reset 0.108,
nur m 0.117, m + v 0.093. Frühe Update-Norm: nur m 0.246 < normal 0.270 < voller Reset 0.425. *Deutung (Pilot):* Das Überschreiben der Spur scheidet als Erklärung für EXP-057 aus.
Das erste Moment der 25 A-Schritte trägt den größten Teil der A-Persistenz; übrig bleibt π ≈ 0.1. Die GPU-Läufe reproduzieren EXP-056/057 bitgenau. *Entscheidung:* N28 als nächstes Programm B:
Bestätigung an frischen Seeds, vorher Codex-Prüfung.

### Abschlussbericht Sitzung 21 (Stand 06:51 Berlin, gemessen; Auftrag §10)

**Wichtigste Befunde:**
- **P1 bestätigt** (vorab eingefroren, 733e829; 420 gebundene Läufe): Konstruierte Splits steuern die relative W_E-Energie der Zielfrequenzen/-Irreps. add 113 Δ_pow 8.24 [7.92, 8.54],
  mul 113 8.09, add 97 6.11, D₅₉ 2.64, jeweils 50/50 frische Seeds, Holm-p 1.5·10⁻⁵. Wortlaut nach Codex: zurückgehaltene Replikation in vier nach dem Pilot gewählten Fällen, Repräsentation, nicht Funktion.
- **P2 nicht auswertbar**: 3/50 Modelle bei Schritt 2000 nicht generalisiert, die Regel verlangte alle 50 (mein Designfehler). Beschreibend R̄ = 0.12. Nachfolgeplan im BACKLOG.
- **P3 bestätigt** (f8adf45; 240 gebundene Läufe): Nach 25 Schritten auf A liegen die Modelle nach 2000 Schritten auf einem paar-disjunkten B noch bei π = 0.35. Der Überschuss über jede statische
  W_E-Spur beträgt 0.293 [0.263, 0.322], 30/30. Die Überlappung 0–0.4 hat keinen nachweisbaren Einfluss. Nach Codex: starke Wirkung der Vorgeschichte, eine Festlegung im Netz ist nicht identifiziert.
- **Mechanismus (Piloten, bekannte Seeds):** EXP-057: Eine volle Optimierer-Neuinit senkt π auf 0.11. **EXP-058: Nur das Momentum zu löschen reicht (π 0.12), obwohl die Schritte danach kleiner sind.**
  Das Gedächtnis der ersten 25 Schritte sitzt demnach vor allem im Adam-Momentum (Kandidat N28, nach der Suche vom 27.09. nicht gefunden, vorläufig).
- Weitere Piloten: EXP-035 (Warmup verzögert, n = 3), EXP-038 (Festlegung bei t = 150 doppelt vorhanden, 5/5), EXP-056 (Persistenz ohne geteilte Paare, 10/10; passive Spur erklärt 0.003–0.06).

**Offene Grenzen:** eine Architekturfamilie, 2000 Schritte, konstruierte Splits, eine Aufgabe für P3; Funktion (P2) offen; N28 nur Pilot an bekannten Seeds, ohne Richtungsanalyse.
Nach dem Einfrieren wurde `freq_ban.py` geändert (5aa8c34, 041f7a8). Eine erneute P1/P2/P3-Auswertung braucht deshalb einen Checkout von 733e829 bzw. f8adf45.
Meine Fehler dieser Sitzung: Zeitstempel vor der Messung geschrieben (mehrfach korrigiert), Prüfungen am falschen Objekt (drei Fälle), eine Trainer-Änderung vor der Codex-Prüfung (nachgeholt).

**Reproduktion:** `python lab/tools/confirm_p1.py --analyze lab/confirm/P1_manifest.json` bzw. `confirm_p2.py`/`confirm_p3.py` (aus 733e829/f8adf45); Blöcke `parallel_queue.py lab/confirm/P1_jobs.txt|P3_jobs.txt --workers 8`;
EXP-056/057/058: `parallel_queue.py lab/experiments/<EXP>/jobs.txt --workers 8`, dann `guarded_run.py -- python lab/experiments/<EXP>/analyze.py`.

**Nächste Aktion:** CPU-Programm neu starten (Befehl in [[STATE]]). N28 (Momentum) als Bestätigung an frischen Seeds registrieren, mit Codex-Prüfung, dann auf der GPU rechnen.
Danach der P2-Nachfolger.

**Runner:** Die geplante Aufgabe „GROKVERSE-Lab-Runner“ ist aktiv. Nächster Start laut `runner-state.json`: 2026-09-27 05:54:44Z = **07:54 Berlin**. Das CPU-Programm (EXP-041 …) läuft bis zur
Sitzungsdeadline 07:19, dann beendet es der Wächter. Die Folgesitzung setzt mit demselben Befehl fort.

**Nachtrag 06:56 (gemessen): EXP-041 ausgewertet (CPU-Programm).** Beide Hypothesen ***geprägt***: E → R @150 10/10 (p = 0.001), R → E @150 9/10, 0 umgeschlagen. Ein 150-Schritte-Vorlauf auf einem
konstruierten Split programmiert die Frequenzwahl auch gegen gewöhnliches Zufallssplit-Training, und ein schwacher Zufallssplit prägt ebenso. Pilot (Regel 15b). Bei t = 150 ist das Momentum abgeklungen,
die Festlegung sitzt dann in den Gewichten. Folgefrage für N28: Wann geht das Gedächtnis vom Optimierer in die Gewichte über (t = 25 gegen 50 gegen 150)? Seit 06:55 läuft EXP-036 auf der CPU.

## Sitzung 22 (2026-09-27, Start 06:59 Berlin gemessen, Deadline 09:59)

**Zyklus 1 (07:00–07:03 gemessen): EXP-059 festgelegt und gestartet.** CPU-Programm wieder gestartet (EXP-036, 039, 040, 042, 014). *Frage:* Ist das „Momentum-Gedächtnis“
aus EXP-058 mehr als verlängerte A-Exposition? Der Momentum-Schwanz (β₁ = 0.9) schiebt das Netz nach dem Wechsel noch einige Schritte in A-Richtung. π(t) ist laut EXP-020 steil
(0.15 / 0.38 / 0.72 bei t = 10 / 25 / 50, andere Splits). M2 (trivial) sagt π_rom(35) ≥ π_normal(25) − 0.05 voraus, M1 (echtes Optimierergedächtnis) sagt einen klar kleineren Wert voraus.
[[experiments/EXP-059-momentum-exposure/README|EXP-059]] (7d6374e, vor jedem Lauf): π-Kurven normal (t = 10…50) und nur-m (t = 25…50), Seeds 400–409, 200 Läufe auf der GPU. Pilot.

**Zyklus 2 (07:03–07:12 gemessen, während EXP-059 läuft): Bestätigungen vorbereitet.** `lab/tools/bound_block.py`: die Bindungslogik aus confirm_p3 (von Codex geprüft) als parametrisierte
Klasse, damit neue Blöcke sie nicht ein drittes Mal kopieren. confirm_p1/p3 bleiben eingefroren und unverändert. `confirm_n28.py` (Seeds 2200–2229, Arme normal@25, m@25, m@35) und `confirm_p2b.py`
(P2-Nachfolger: Seeds 2000–2099, 4000 Schritte, Ausschluss nicht generalisierter Modelle mit Bericht, ≥ 90 % gültig). Beide Selbsttests ok. Power für P2b aus den 47 P2-Werten per Bootstrap
nachgerechnet: 0.88 bei n = 80, 0.92 bei n = 100 am beobachteten Effekt, ≈ 0.7 bei einem um 0.02 kleineren. Deshalb n = 100. Seed-Blöcke in [[FINDINGS]] reserviert (b0676fb).
Codex-Prüfung von P2b + bound_block läuft (Vordergrund, als Bash-Hintergrundbefehl).

**Zyklus 3 (EXP-059 ausgewertet, 07:22 gemessen).** *Frage:* Momentum-Gedächtnis (M1) oder verlängerte Exposition (M2)? *Ergebnis:* ***verlängerte Exposition genügt***.
D = π_rom(35) − π_normal(25) = +0.059 [0.023, 0.095] (90 %), 8/10 > 0. π_normal(t) = 0.01 / 0.07 / 0.19 / 0.30 / 0.39 / 0.56 / 1.05 bei t = 10 … 50; die Verschiebung durch das Löschen von m
beträgt 6–10 Schritte bei t = 25–35 und 2 Schritte bei t = 50. *Deutung:* Die N28-Mechanismusdeutung aus Sitzung 21 („das Gedächtnis sitzt im Adam-Zustand“) war zu stark. Der Momentum-Schwanz
setzt einfach die A-Exposition für einige Schritte fort, und π(t) ist so steil (≈ 0.02–0.03 je Schritt), dass das den Abfall erklärt. N28 herabgestuft (#neu/bekannt). Die Steilheit selbst
(volle Festlegung nach 50 Schritten) ist der interessantere Befund für Programm B. *Entscheidung:* N28-Bestätigung eng: H1 (m-Reset senkt π) plus H2 als Nichtunterlegenheit (m@35 ≥ normal@25 − 0.05),
normal@50 beschreibend.

**Zyklus 4 (Codex-Prüfung P2b, 07:14–07:22; Korrekturen bis 07:26 gemessen).** *Codex:* 2 Blocker, 1 hoch, 2 mittel; Run-IDs und Refaktor in Ordnung. *Selbst geprüft, alle übernommen:*
(1) Split-Herkunft wird nicht erzwungen (stimmt: Ziele kamen aus veränderlichem JSON) → `split_mismatch` baut neu und vergleicht exakt, bei Abweichung ist die Bestätigung ungültig (auch in N28).
(2) Bis zu 10 technische Ausfälle hätten still verschwinden können (stimmt) → jeder technische Ausfall macht P2b nicht auswertbar; die Bindung nimmt nur `completed`-Läufe (bound_block).
(3) Ausschluss wegen undurchführbarer Dosis selektiert über dieselbe Geometrie wie R (stimmt) → Dosis min(0.5·E_ctrl, E_own), Aussage bedingt auf Generalisierung, Sensitivitätsanalyse über alle Seeds.
(4) Endlichkeit unvollständig (stimmt) → alle Verluste, R, D geprüft. (5) Power nicht eingefroren (stimmt) → `p2b_power.py`: 0.92 am beobachteten Mittel, 0.73 bei −0.02 (hingenommen, berichtet).
Selbsttests grün (089faa0). Nachprüfung durch Codex für die betroffenen Punkte und die neue N28-Registrierung läuft.

**Zyklus 5 (Bestätigungen eingefroren und gestartet, 07:28–07:34 gemessen).** Codex-Nachprüfung (gegen 089faa0): Alle P2b-Korrekturen greifen. N28: Blocker (Holm auf Δ > 0 statt Δ > 0.05) → die Marge steckt
jetzt in der getesteten Größe (Y = Δ_m − 0.05, X = π_m35 − π_n25 + 0.05; KI-Tor ≥ 0). Hoch: Die Lesart war zu stark und ist enger gefasst („vereinbar mit / ersetzbar durch verlängerte Exposition“).
Mittel: δ und Update-Normen gestrichen (nicht im Code festgelegt). Alles selbst geprüft und übernommen. Manifeste fa154bd (Commit-Feld 888c2d9), Splits und Jobs 37448f6, Herkunftsprüfung an allen Dateien bestanden,
ein echter N28-Job als Smoke gebunden. Beide Blöcke laufen auf der GPU (je 5 Arbeiter).

**Zyklus 6 (EXP-060, Exploration, 07:37).** *Frage:* Ist die Festlegung eine sichtbare W_E-Größe? *Ergebnis:* nein. Der spektrale Vorsprung der gelernten Änderung wächst kaum (0.55 → 0.89), π springt von 0 auf 1;
innerhalb von t erklärt er die Seed-Streuung nicht (ρ 0.02–0.36). Die relative Größe ist nur eine Uhr. → [[experiments/EXP-060-early-lead/README|EXP-060]].

**Zyklus 7 (EXP-061, 07:38–07:48 gemessen).** *Frage:* Verstärkt der Gradient der neuen Daten die gelernte alte Struktur (Selbstverstärkung)? Vorab festgelegt (355a2a1), 100 kurze Läufe.
*Ergebnis:* ***verworfen***. Der B-Gradient zeigt gegen die A-Struktur, und zwar zunehmend mit t (cos −0.48 → −0.78), während π steigt. Innerhalb von t negativ (−0.25).
*Deutung:* Erster Ordnung baut neues Training die alte Wahl ab. Die Persistenz entsteht in der weiteren Dynamik (Adam-v, Weight Decay, Rest des Netzes oder ein Wettlauf der Raten).
*Nächste Frage:* Raten-Wettlauf aus gespeicherten Spektren (Abbau der A-Energie gegen Aufbau der B-Energie je t). Kein neuer Lauf nötig.

**Zyklus 8 (EXP-062, 07:50–07:51 gemessen).** *Frage:* Ist die Persistenz erhaltene alte Energie (a) oder fehlende neue Energie (b)? (Exploration auf gespeicherten Spektren, a + b = Zähler von π exakt.)
*Ergebnis:* zwei Regime. Bis t ≈ 30 **Koexistenz**: a wächst (2.1 bei t = 25), b bleibt klein (0.26), das Netz lernt die neuen Frequenzen fast normal dazu. Bei t = 50 **Ausschluss**: b = 4.25,
die neuen Frequenzen entstehen kaum. Je Seed 10/10 in beiden Mustern. *Entscheidung:* Vorhersage für die frischen N28-Seeds vorab festgelegt (2bdfdaf, `lab/confirm/n28_regimes.py`, ≥ 24/30 je Muster),
bevor irgendein N28-Ergebnis angesehen wurde. Auswertung nach dem Block.

**Zyklus 9 (EXP-063 festgelegt und gestartet, 07:53–07:54 gemessen).** *Frage (K2 aus dem BACKLOG):* Sitzt der Ausschluss neuer Frequenzen bei t = 50 im Rest des Netzes? Arme: Reset des Rests bzw. von W_E
beim Wechsel (vorhandene Option aus EXP-038), 40 Läufe, Pilot. Ergebnis ausstehend.

**Zyklus 10 (P2b abgebrochen, P2c eingefroren, 08:03–08:10 gemessen).** Zwei Starts scheiterten 07:53 am Speicher (`bad allocation`, WinError 1455) bei 12 GPU-Prozessen plus CPU-Programm.
Beim Lesen der Logs fiel auf: P2b-Läufe enden bei „gen + 2000“ (Seed 2000 G: 2725 Schritte), weil `freq_ban.py` standardmäßig `--stop-after-gen 2000` setzt. Der eingefrorene Lader verlangt
4000 Schritte → P2b wäre vollständig *nicht auswertbar*. **Mein Designfehler**, von beiden Codex-Prüfungen nicht bemerkt. Block abgebrochen (Prozessbaum beendet, kein R, keine Ablation berechnet),
Seeds 2000–2099 verbraucht. **P2c** = P2b mit Seeds 2100–2199, Versuchs-ID 3, `--stop-after-gen 4000` und einem Selbsttest, der für jede Zeile volle Schrittzahl verlangt.
Codex (gezielt): 4000 Schritte garantiert, Lauf-ID korrekt, zwei Kommentarfehler (behoben). Eingefroren e8e0cfa, Splits/Jobs 4aa4544, Start mit 3 Arbeitern (freier virtueller Speicher 3.3 GB).
Geprüft: N28, EXP-058/059/063 sind nicht betroffen (≤ 2050 Schritte, Generalisierung nie vor Schritt 50).
*Lehre:* Eine Bestätigung braucht vor dem Einfrieren einen echten Probelauf **bis zum Ende**, dessen Ergebnis den eingefrorenen Lader passiert. Der N28-Smoke hat das geleistet, für P2b fehlte er.

**Zyklus 11 (EXP-063 ausgewertet, 08:14–08:17 gemessen).** *Ergebnis:* ***Ausschluss sitzt (auch) im Rest des Netzes*** (Δb > 1 in 10/10). Rest-Reset: b 4.25 → 1.05, a bleibt 3.1. W_E-Reset (beschreibend): b 0.44, a 2.5.
*Deutung (Pilot):* Das Erhalten der alten Wahl ist doppelt vorhanden, der Ausschluss braucht W_E und Rest zusammen. Ein Speicherfehler (Job 2) wurde mit demselben Befehl nachgeholt.
*Nächste Frage:* welcher Teil des Rests; Weight Decay (K1, braucht Trainer-Option und Codex).

**Zyklus 12 (N28 ausgewertet, Vorhersage geprüft, 08:28–08:29 gemessen).** N28-Block 300/300 gebunden, 30/30 gültig. **H1 bestätigt** (Δ_m ≈ 0.15, Y-KI [0.077, 0.126], Holm-p 2·10⁻⁸),
**H2 bestätigt** (π_m@35 0.41 ≥ π_normal@25 0.34, X-KI [0.090, 0.152]). π_normal@50 = 1.00. **Vorab festgelegte Zwei-Regime-Vorhersage bestätigt** (V1 29/30, V2 30/30), Werte nahe am Piloten.
Nächster Schritt: Codex prüft die Schlussfolgerungen, bevor sie als Kernaussage in FINDINGS stehen.

**Zyklus 13 (Codex prüft die Schlussfolgerungen, 08:30–08:34 gemessen).** *Codex:* K-B1 nach Präzisierung verwendbar, K-B2 im alten Wortlaut blockiert. Übernommen, alle selbst geprüft:
(1) Nichtunterlegenheit zeigt Ausgleich auf π, nicht mechanistische Ersetzbarkeit. (2) π ist ein normierter Spektralindex, kein Anteil. (3) Die π(t)-Kurve ist Pilot, frisch nur 25 gegen 50.
(4, Blocker) a/b zeigen Spektralsignaturen, keine funktionale Koexistenz bzw. keinen funktionalen Ausschluss. (5) Vorhersage während der Erhebung festgelegt: „erfüllte Vorhersage“. (6) Enger Geltungsbereich.
(7) EXP-063 zu kausal. FINDINGS mit neuem Abschnitt „K4b-bestätigt“ in engem Wortlaut; NOVEL_DIRECTIONS N29, EXP-062/063 ergänzt. Nächster Test für N29: funktional (Ablation am Endmodell).

**Zwischenbilanz Sitzung 22 (§4, 08:37).** *Gelernt:* Die „Adam-Gedächtnis“-Deutung aus Sitzung 21 war zu stark (EXP-059) und ist in der engen Fassung jetzt bestätigt (N28). Neu ist ein
Zwei-Regime-Bild (Koexistenz bis t ≈ 30, Ausschluss bei 50), dessen Vorhersage an frischen Seeds erfüllt ist. Zwei Mechanismusideen sind verworfen (W_E-Vorsprung, Gradientenverstärkung).
*Wiederholen wir uns?* Nein: jeder Versuch dieser Sitzung entschied zwischen benannten Konkurrenzmodellen. *Sind die Maße geeignet?* Teilweise: π und a/b sind Spektralmaße in W_E; Codex hat zu Recht
verlangt, Funktion getrennt zu prüfen (EXP-064 läuft). *Welche Annahme als Nächstes angreifen:* dass „Ausschluss“ ein Kapazitäts- bzw. Weight-Decay-Effekt ist (K1) und welcher Teil des Rests ihn trägt.
*Eigene Fehler:* P2b-Designfehler (vorzeitiger Trainer-Stopp nicht bedacht), mehrfach geschätzte statt gemessene Uhrzeiten (korrigiert), einmal `git add -u lab` mit Nutzer-Dateien (sofort rückgängig gemacht, nur mein Commit).

**Zyklus 14 (P2c ausgewertet, 09:03 gemessen).** 200/200 gebunden, 99/100 geeignet. ***nicht bestätigt***, mit umgekehrtem Vorzeichen: R̄ = −0.108 [−0.149, −0.070], 30/99 > 0.
Beschreibend (nach dem Ergebnis): Die eigenen Ziele tragen bei 4000 Schritten noch mehr W_E-Energie (Median-Verhältnis 20.5 statt 12.2), die Dosis 0.5·E_ctrl stört sie also nur um ≈ 2.5 %,
die Kontrolle um 50 %. Deutung offen, nicht verteidigt. *Entscheidung:* Programm A („funktionale Nutzung“) ist mit dem P2-Maß nicht belegt; ein Nachfolger bräuchte ein vorab festgelegtes Maß mit
angeglichener relativer Störung oder eine Dosis-Kurve. Codex-Prüfung dieser Schlussfolgerung in der nächsten Sitzung.

**Zyklus 15 (EXP-064 ausgewertet, 09:06).** ***nicht auswertbar*** (3 Seeds unter der Basis-Genauigkeit 0.9). Beschreibend in allen 10 Seeds klar: t = 50 → ohne alte Ziele Genauigkeit 0.01–0.09, ohne neue ≈ 1;
t = 25 → ohne neue 0.04–0.38. Die „Koexistenz“ aus EXP-062 ist spektral, funktional ist es ein **Umstieg** (t = 25) gegen **Festhalten** (t = 50). Codex hatte genau hier die Lücke benannt.
Nächster Schritt: Bestätigung mit sicherer Generalisierung (längeres Nachtraining, `--stop-after-gen` ≥ Schritte) an frischen Seeds.

**Zyklus 16 (Codex prüft die P2c-Schlussfolgerung, 09:05–09:12 gemessen).** Urteil korrekt. Übernommen: keine Gegenhypothese behaupten; Dosisgeometrie genau benennen (2.44 % gegen 50 %, Skalierung 0.988 gegen 0.707,
post hoc); Ursache nicht identifiziert (mehrere Faktoren ändern sich gleichzeitig; nach Codex bleibt R auch innerhalb der Basis-Loss-Quartile negativ); die funktionale Aussage bleibt eng.
Nachfolgemaß P2d im [[BACKLOG]] (lokale Empfindlichkeit je gleicher Schrittnorm, Kontrollen gleicher Größe, Logit-Abstand primär).

### Abschlussbericht Sitzung 22 (Stand 09:13 Berlin, gemessen; Auftrag §10; Nachträge unten)

**Wichtigste Befunde:**
- **N28 bestätigt** (eingefroren fa154bd, 300 gebundene Läufe, 30/30 frische Seeds): Das Nullsetzen von Adams erstem Moment beim Wechsel senkt den normierten Persistenzindex π um 0.15
  (0.340 → 0.189). Ein Arm mit zehn zusätzlichen Vorschritten liegt nicht darunter (0.410; Nichtunterlegenheit). Beides mit Holm-p ≈ 10⁻⁸. Das ist vereinbar mit „verlängerter Exposition“;
  die Deutung „Gedächtnis im Adam-Zustand“ aus Sitzung 21 ist damit herabgestuft (EXP-059).
- **Zwei Regime** (EXP-062, Vorhersage an 30 frischen Seeds erfüllt, 29/30 und 30/30): Nach einem Wechsel bei t = 25 überwiegt spektral die erhaltene alte Energie, bei t = 50 fehlen die neuen Frequenzen.
  **Funktional (EXP-064, beschreibend, nach eigener Regel nicht auswertbar):** Bei t = 25 rechnet das Netz mit den neuen Frequenzen, bei t = 50 nur mit den alten (Genauigkeit ohne alte 0.01–0.09, 10/10).
  Kandidat N29, nach der Suche vom 27.09. nicht gefunden (vorläufig).
- **P2c nicht bestätigt** (99/100 Seeds): R̄ = −0.108 [−0.149, −0.070]. Eine bevorzugte funktionale Nutzung der gesteuerten Frequenzen ist mit dem P2-Maß nicht belegt; Ursache offen (u. a. Dosisgeometrie).
- Verworfen bzw. negativ: EXP-060 (W_E-Vorsprung sagt π nicht voraus), EXP-061 (neuer Gradient verstärkt die alte Struktur nicht). EXP-063 (Pilot): Rest- oder W_E-Reset verkleinert den Ausschluss.

**Offene Grenzen:** eine Aufgabe (add 113), eine Architektur, ω = 0, Spektralmaße in W_E; π(t) als Kurve nur Pilot; der funktionale Übergang ist nicht bestätigt; P2 (Funktion) bleibt offen.
**Meine Fehler:** P2b-Designfehler (vorzeitiger Trainer-Stopp nicht bedacht, 100 Seeds verbraucht), mehrfach geschätzte Uhrzeiten (alle korrigiert), einmal `git add -u lab` mit Nutzer-Dateien (sofort zurückgenommen).

**Reproduktion:** `python lab/tools/confirm_n28.py --analyze lab/confirm/N28_manifest.json` · `python lab/confirm/n28_regimes.py` · `python lab/tools/confirm_p2c.py --analyze lab/confirm/P2c_manifest.json`
(alle über `guarded_run.py`); Blöcke `parallel_queue.py lab/confirm/{N28,P2c}_jobs.txt`; Piloten `parallel_queue.py lab/experiments/EXP-0{59,61,63,64}-*/jobs.txt`, dann `analyze.py`; EXP-060/062 nur `analyze.py`.

**Nächste Aktion:** CPU-Programm neu starten; funktionalen Übergang (t = 25 gegen 50) an frischen Seeds mit sicherem Nachtraining festlegen (vorher ein echter Job durch den Lader, Codex), dann P2d.

**Runner:** geplante Aufgabe „GROKVERSE-Lab-Runner“ aktiv; laut `runner-state.json` nächster Start 2026-09-27 08:34:44Z = **10:34 Berlin**. Das CPU-Programm läuft bis zur Deadline 09:59 und wird dann vom Wächter beendet
(kein Fehler; derselbe Befehl setzt fort). Keine GPU-Läufe offen.

**Nachtrag Zyklus 17 (EXP-065, Exploration, 09:13–09:15 gemessen).** *Frage:* Liegt die P2c-Umkehrung an der Dosisgeometrie? Maß (Codex-Vorschlag): Abfall des Logit-Abstands bei gleicher Schrittnorm entlang
der eigenen Ziele gegen 4 gleich große Kontrollmengen. *Ergebnis:* eigene > Kontrolle in 80/80 Modellen (Median 0.25 gegen 0.0007; je Seed Differenz 0.254 ± 0.038). *Deutung (Exploration, gleiche Modelle,
Maß nach dem Ergebnis gewählt):* Die Umkehrung war sehr wahrscheinlich ein Artefakt der Dosis. Die funktionale Nutzung ist damit plausibel, aber erst mit P2d an frischen Seeds belegt.
*Nächster Schritt:* P2d festlegen (Differenz der Abfälle primär, n ≈ 20, frischer Block), vorher ein echter Job durch den Lader und Codex.

**Zyklus 18 (P2d festgelegt, eingefroren, gerechnet, 09:17–09:30 gemessen).** Codex (gegen 8c66f73): keine Blocker. Eingefroren c0cd65f, Splits/Jobs 3e7019b, ein Smoke bis Schritt 4000 durch den Lader (Lehre aus P2b).
40 Läufe, 7 Arbeiter. ***bestätigt***: D̄ = 0.250 [0.229, 0.270], 20/20, p = 1.6·10⁻¹⁵. *Deutung:* Bei gleicher Schrittnorm reagiert das Netz entlang der gesteuerten Frequenzen in W_E lokal viel empfindlicher
als entlang gleich großer Kontrollmengen. (Wortlaut nach Codex korrigiert, siehe Zyklus 19.)

**Zyklus 19 (Codex prüft die P2d-Schlussfolgerung, 09:31–09:34 gemessen).** Zahlenbefund trägt. Übernommen (selbst geprüft): „P2c-Umkehrung liegt an der Dosisgeometrie“ ist nicht belegt, nur vereinbar;
„lokal viel empfindlicher“ zu allgemein → „stärkere Margin-Reaktion unter dieser einseitigen Perturbation, dieser Dosis, diesen Kontrollen“; u_S ist amplitudengewichtet (Frequenzidentität und gelernte Norm nicht getrennt);
Kontrollen nur aus dem P2-Pool; statistische Einheit = seedweiser Kontrast. FINDINGS: neuer Abschnitt „K2-Funktion (P2d)“ im engsten Wortlaut; EXP-065, LIVE und JOURNAL entschärft.

**Nachtrag zum Abschlussbericht Sitzung 22 (09:35 Berlin, gemessen).** Nach dem Bericht von 09:13 noch zwei Zyklen: EXP-065 (Exploration: bei gleicher Schrittnorm eigene Ziele ≫ Kontrollen, 80/80) und
**P2d bestätigt** (eingefroren c0cd65f, 20 frische Seeds, 40 gebundene Läufe, Smoke durch den Lader vor dem Block): D̄ = 0.250 [0.229, 0.270], 20/20, p = 1.6·10⁻¹⁵. Enger Wortlaut nach Codex in
[[FINDINGS]] („K2-Funktion (P2d)“): stärkere Margin-Reaktion von W_E unter einer einseitigen Perturbation gleicher Norm, bei einer Dosis und diesen Kontrollen; die Ursache der P2c-Umkehrung ist damit nicht bestimmt.
**Reproduktion:** `python lab/tools/guarded_run.py -- python lab/tools/confirm_p2d.py --analyze lab/confirm/P2d_manifest.json`.
**Nächste Aktion (unverändert, ergänzt):** CPU-Programm neu starten; funktionalen Übergang (t = 25 gegen 50) bestätigen; P2d auf die anderen P1-Aufgaben übertragen.
**Runner:** nächster Start laut `runner-state.json` 10:34 Berlin. Keine GPU-Läufe offen; das CPU-Programm läuft bis zur Deadline 09:59.

**Nachtrag 09:36 (CPU-Programm): EXP-036 ausgewertet.** ***init-getrieben*** (5/5 auswertbare Paare, p = 0.031): Die „fremden“ Frequenzen nach frühem Wechsel folgen der Init. P36b kalibriert gestützt (4/5), aber nicht enger als Init oder Einzelarm. Pilot. Im CPU-Programm läuft jetzt EXP-039.


## Sitzung 23 (2026-09-27, Start 09:39 Berlin, Deadline 12:39; vom Runner)

**Zyklus 1 (Start, 09:39–09:41 gemessen).** Kein STOP, Fenster offen, keine Python-Prozesse. CPU-Programm (EXP-039 …) mit demselben Befehl neu gestartet.

**Zyklus 2 (N29 festgelegt, Entwurf, 09:41–09:45).** *Frage (Programm B):* Ist der funktionale Übergang aus EXP-064 (Umstieg bei t = 25, Festhalten bei t = 50) an frischen Seeds mit sicherem Nachtraining
reproduzierbar? *Änderung:* `lab/tools/confirm_n29.py` (Muster N28/P2d, Selbsttest ok) und [[confirm/N29_REGISTRATION|N29-Registrierung]]: Seeds 2250–2269, 4000 Schritte nach dem Wechsel mit
`--stop-after-gen` = Schritte, H1 (t = 50: Entfernen der alten schadet ≥ 0.3 mehr) und H2 (t = 25: Entfernen der neuen schadet ≥ 0.3 mehr), Holm, ≥ 80 % geeignete Seeds. Codex-Prüfung läuft.

**Zyklus 3 (EXP-066, Exploration, 09:45–09:48 gemessen).** *Frage (Programm A, Regel 15c):* Gilt der P2d-Befund (stärkere Margin-Reaktion entlang der gesteuerten Frequenzen bei gleicher Schrittnorm)
auch bei mul 113 und add 97? *Änderung:* Maß in Gruppenordnung übertragen, auf die gebundenen P1-Modelle (2000 Schritte) angewandt, vor der Rechnung festgelegt.
*Ergebnis:* mul 113 D̄ = 0.159 [0.150, 0.168] (43/43 geeignete > 0; alle 50 > 0), add 97 D̄ = 0.218 [0.194, 0.243] (26/26; alle 50 > 0). *Entscheidung:* Bestätigung P2e an frischen Seeds
(2270–2289, Versuchs-ID 5, 8000 Schritte, Holm über beide Aufgaben) festlegen; [[experiments/EXP-066-p2d-other-tasks/README|EXP-066]].

**Zyklus 4 (P2e festgelegt, Entwurf, 09:48–09:50).** `lab/tools/confirm_p2e.py` (Selbsttest ok), [[confirm/P2e_REGISTRATION|P2e-Registrierung]]. Codex-Prüfung läuft.


**Zyklus 5 (Codex prüft N29, dann Nachprüfung; eingefroren; Block gestartet, 09:44–09:59 gemessen).** *Codex:* zwei Blocker. (1) Der Genauigkeitsfilter ist ergebnisabhängig: Im Piloten hatten die
ausgeschlossenen Seeds H2 ≈ 0.15, die eingeschlossenen 0.66. (2) `EXP-056/make_splits.py` wird ausgeführt, war aber nicht im Code-Hash. Dazu: kein gemeinsames Urteil, Endlichkeit nicht durchgesetzt,
EXP-064-Wortlaut zu stark (Seed 406: acc_neu(50) = 0.73). *Selbst geprüft und übernommen:* primär alle Seeds, Import-Prüfung im Selbsttest, „Übergang bestätigt“ nur bei H1 und H2, alle Gewichte und Verluste endlich,
Korrektur in EXP-064. Nachprüfung: 4/5 geschlossen, zwei kleine Reste (Endlichkeit aller Parameter, Urteilslabel in der beschreibenden Teilanalyse) behoben.
*Nebenbefund:* Die gleiche Lücke hatte P2d (`EXP-056/make_splits.py`, `EXP-053/overlap_split.py` nicht im Hash). Beide Dateien sind seit dem P2d-Einfrieren c0cd65f unverändert (`git log` leer),
das P2d-Ergebnis ist davon also nicht berührt. Neue Blöcke prüfen die Import-Hülle im Selbsttest.
Eingefroren 087e042, Splits und Jobs committet, Smoke (Seed 2250, A→B bei 25) durch den Lader: gebunden, Basis 1.0, acc_alt 1.0, acc_neu 0.13. Block 80 Läufe, 7 GPU-Arbeiter, Start 09:59.

**Zyklus 6 (Codex prüft P2e; eingefroren; Smoke findet Fehler; neu eingefroren, 09:50–10:08 gemessen).** *Codex:* keine Fehler in der Übertragung auf mul/add 97 (Log-Ordnung, Nyquist, Run-IDs, Holm).
Übernommen: Lade-/Rechenfehler als technischer Ausfall, primär alle Seeds (wie N29), „lokale endliche Störung“, bedingte Power-Aussage, Semantik-Selbsttest.
Eingefroren 2510c92; der Smoke-Job zeigte über den Lader einen **Klammerfehler in `measure`** (`dict | dict.items()`), den der Selbsttest nicht abdeckte. Behoben, Selbsttest um einen End-zu-End-Durchlauf
ergänzt, **neu eingefroren 3c484ef**, Smoke unter altem Code beiseitegelegt und neu gerechnet: gebunden, Basis 1.0, drop_eigen 0.244, Kontrollen −0.004 … 0.002 (dieser eine Wert ist damit vor dem
Block gesehen). *Lehre:* Der Smoke durch den Lader ist unverzichtbar (zweites Mal nach P2b). Block gestartet 10:07 (Log): vorwärts 2 Arbeiter neben N29, rückwärts folgt nach N29.

**Zyklus 7 (N29 ausgewertet, 10:16–10:17 gemessen).** *Frage:* Funktionaler Übergang zwischen t = 25 und 50 an frischen Seeds? *Ergebnis:* ***Übergang bestätigt*** (eingefroren 087e042, 80/80 gebunden,
alle 20 Seeds primär): H1 (t = 50) acc_neu − acc_alt = 0.903 [0.846, 0.953], 20/20 über 0.3; H2 (t = 25) acc_alt − acc_neu = 0.603 [0.498, 0.700], 17/20 über 0.3. Holm-p 7·10⁻¹⁵ bzw. 1·10⁻⁵.
*Post hoc:* Nach 4000 Schritten folgt auch die W_E-Energie derselben Richtung (38/40 bzw. 40/40); anders als bei 2000 Schritten in EXP-062 (dort bei t = 25 noch viel alte Energie). Die Ablation trennt Funktion
und Energie hier also nicht. *Entscheidung:* Codex greift die Schlussfolgerung an, bevor sie in FINDINGS steht. P2e läuft (2 + 5 GPU-Arbeiter).

**Zyklus 8 (Codex greift N29-Schlussfolgerung an, FINDINGS K4c, 10:17–10:21).** Zahlen tragen; „hängt ab“, „kippt“, „funktionale Festlegung“ zu stark. Selbst nachgerechnet: t = 25 38/40 Richtungen mit
erwartetem Vorzeichen, 29/40 über 0.3 (2253 A→B, 2267 B→A umgekehrt); t = 50 40/40 und 39/40. Übernommen: enger Wortlaut „K4c“ in [[FINDINGS]] (Umkehrung eines Ablationskontrasts, keine netzweite
oder unumkehrbare Festlegung), Einheiten richtungsgemittelte Seeds, fehlende Energiekontrolle als Grenze.

**Zyklus 9 (Funktion gegen Energie, zwei Explorationen, 10:21–10:24 gemessen).** *Frage:* Zeigen die funktionalen Befunde mehr als die Energieverteilung in W_E?
(a) EXP-064 post hoc: Auch nach 2000 Schritten zeigen absolute Energie und Ablation immer dieselbe Richtung (Dissoziation 0/40); die „überschüssige alte Energie“ aus EXP-062 war relativ gemessen.
(b) [[experiments/EXP-068-matched-sensitivity/README|EXP-068]] (N29-Modelle, vorab festgelegt): Bei gleicher entfernter Energie **kein** Vorteil der dominanten Menge (Median log-Verhältnis −0.28 bzw. −0.18,
42–44 % > 0); nur bei gleicher Schrittnorm, was die Amplitudengewichtung ohnehin erzeugt. *Überlegung danach:* Jede Störung innerhalb eines Frequenzunterraums ist in ihrer Größe an dessen Energie
gebunden (auch eine Phasenverschiebung: ‖ΔW‖² = 2(1 − cos φ)·E_k). Die Frage „Funktion über die Energie hinaus“ ist mit Ablationen am selben Modell deshalb kaum sauber zu stellen; möglich wäre nur
ein Vergleich von Frequenzen gleicher Energie mit unterschiedlicher Herkunft (Ziel gegen Nicht-Ziel), falls es solche Paare gibt. *Entscheidung:* In FINDINGS als Grenze von K2-Funktion und K4c
festhalten; keine weitere Ablations-Variante ohne diese Trennung.

**Zyklus 10 (P2e ausgewertet, 10:42–10:44 gemessen).** *Frage (Programm A, Regel 15c):* Gilt P2d bei mul 113 und add 97? *Ergebnis:* ***bestätigt*** in beiden Aufgaben (eingefroren 3c484ef, 80/80 gebunden,
alle 20 Seeds primär): mul 113 D̄ = 0.291 [0.268, 0.308], add 97 D̄ = 0.294 [0.275, 0.312], je 20/20 > 0. Deutung wie vor dem Ergebnis festgelegt nur „Empfindlichkeit entlang amplitudentragender Richtungen“.
Die zwei Ablehnungen je Warteschlange am Treffpunkt (`run.lock`) sind erwartet; alle 80 Läufe sind gebunden.

**Zyklus 11 (Trainer-Option für EXP-067, 10:44–10:47 gemessen).** `freq_ban.py --reset-at-switch attn|mlp|unembed` (Auswahl über Parameternamen, sonst der EXP-038-Pfad), Test `test_reset_parts`;
18/18 Tests grün (10:44–10:46). Der Patch wurde vor dem Ende von N29/P2e vorbereitet, aber erst danach eingespielt (`freq_ban.py` steht in deren Code-Hash). Ein Zwischenstand hatte durch `write_text`
CRLF-Zeilenenden (sofort auf LF zurückgesetzt, Diff 28 Zeilen). *Folge für eingefrorene Blöcke:* Deren `--analyze` prüft die Code-Hashes; nach dieser Änderung wird am jeweiligen Manifest-Commit
reproduziert (`git worktree add <dir> <commit>`), wie schon nach den EXP-057/058-Änderungen für P1. Das laufende CPU-Programm startet neue Läufe jetzt mit dem geänderten Trainer; für ihre Argumente ist das
Verhalten unverändert (kein `--reset-at-switch`). Codex-Prüfung der Änderung läuft.

**Zyklus 12 (Vorbereitung D₅₉ für Programm A, 10:52–10:54 gemessen).** `group_train.py --save-model` (atomar, vor „completed“ geprüft). `save_model` geht nur in den Fingerabdruck ein, wenn gesetzt: Der gespeicherte
Fingerabdruck eines P1-D₅₉-Laufs (Seed 1000 F) wird exakt reproduziert; ein 30-Schritte-Lauf auf der CPU speichert ein ladbares Modell. Noch ohne Codex-Prüfung (geplant zusammen mit der D₅₉-Registrierung).
Gleichwertigkeit `--reset-at-switch rest` alter gegen neuer freq_ban-Code (60 Schritte, CPU): bitgleich.

**Zyklus 13 (EXP-067, Pilot, Läufe 10:52–10:57, Auswertung 10:57–10:58 gemessen).** *Frage (Programm B):* Welcher Teil des Rests trägt den Ausschluss bei t = 50? *Vorab erwartet:* Attention unwichtig (Modell A).
*Ergebnis:* **Attention-Reset hebt den Ausschluss vollständig auf** (b 4.25 → 0.10, Δb > 1 in 10/10) und das Netz rechnet danach mit den neuen Frequenzen (ohne alte 0.74, ohne neue 0.08). MLP-Reset (doppelte
Parameterzahl) *unklar* (b 3.14, Funktion bleibt alt), W_U-Reset *nicht nötig* (b 4.50). Meine Erwartung war falsch. *Entscheidung:* Bestätigung N29b an frischen Seeds 2300–2319 (neu reserviert), Funktionsmaß wie N29,
Kontraste normal − rsattn und rsmlp − rsattn; Codex-Prüfung läuft. [[experiments/EXP-067-exclusion-part/README|EXP-067]]

**Zyklus 14 (N29b festgelegt und eingefroren, 11:01–11:07 gemessen).** `confirm_n29b.py` (Selbsttest ok 11:01), [[confirm/N29b_REGISTRATION|Registrierung]]. **Codex-Aufruf abgebrochen: „workspace is out of credits“**
(Regel 12: dokumentiert, ohne Codex weiter). Übernommen: Codex' Zwischenbemerkung (H1 belegt keinen Umstieg *auf* die neuen, nur eine Verringerung) → Aussage auf das Getestete eingeschränkt, R(rsattn) nur
beschreibend. Eigene Prüfung statt Codex (Run-IDs, Reset-Ereignisse, Vorzeichen, alt/neu, Holm). Eingefroren db31564, Smoke (rsattn, Seed 2300) durch den Lader ok, Block 120 Läufe ab 11:06 (7 GPU-Arbeiter).
**Folge für den Rest der Sitzung:** Keine Codex-Prüfung der N29b-Schlussfolgerung möglich; eine Kernaussage in FINDINGS erst nach einer Codex-Prüfung in einer späteren Sitzung (Regel 18c), bis dahin nur als
„bestätigt, Schlussfolgerung ungeprüft“ vermerken.

**Zyklus 15 (CPU-Programm: EXP-039 ausgewertet, EXP-040 repariert, 11:05–11:09 gemessen).** [[experiments/EXP-039-lr-clock/README|EXP-039]] ***unklar***: 5/8 Zellen Λ-Uhr, 2/8 Schrittuhr; beschreibend passt die
Λ-Uhr die π-Werte besser (RMSE 0.134 gegen 0.210; Teiluhr γ = 0.65: 0.130). *Lesart:* Festlegung hängt teilweise an der aufsummierten Lernrate.
EXP-040 brach am Selbsttest ab (10:59, fail-closed, kein Lauf): importierte `seed_class` aus EXP-039 kannte die EXP-040-Etiketten nicht (alter Fehler aus Sitzung 10, nicht meine Trainer-Änderung).
Nach registrierter Regel behoben (Nachtrag d), Selbsttest ok; EXP-040 läuft in einer späteren Sitzung. Das CPU-Programm arbeitet jetzt EXP-042 ab.

**Zyklus 16 (Neuheitssuche N32, EXP-069 vorab festgelegt, 11:09–11:11 gemessen).** Suche (WebSearch, 27.09.): Plastizitätsverlust in Transformern geht mit Entropiekollaps der Attention einher (Lyle et al.),
Teil-Resets aus RL/kontinuierlichem Lernen bekannt; ein Attention-Reset nach ≈ 50 Schritten, der den Ausschluss neuer Merkmale aufhebt, während MLP-/W_U-Reset es nicht tun, nicht gefunden → [[NOVEL_DIRECTIONS]] N32 (vorläufig).
[[experiments/EXP-069-attention-part/README|EXP-069]] festgelegt (Muster W_Q/W_K gegen Werte W_V/W_O, gleich viele Parameter), vor dem N29b-Ergebnis; Trainer-Patch (`qk`, `vo`) liegt bereit und wird erst nach dem
N29b-Block eingespielt (Code-Hash). STATE neu geschrieben (51 Zeilen).

**Zyklus 17 (N29b ausgewertet, 11:30–11:31 gemessen; EXP-069 gestartet 11:35).** ***H1 und H2 bestätigt*** (db31564, 120/120 gebunden, alle 20 Seeds): Attention-Reset beim Wechsel bei t = 50 senkt die Abhängigkeit
von den alten Frequenzen um 1.49 [1.36, 1.61] gegenüber normal und um 1.42 [1.28, 1.56] gegenüber dem MLP-Reset (je 20/20). Beschreibend R(rsattn) = −0.63 [−0.73, −0.52], < 0 in 40/40 Richtungen: Das Netz ist danach
auf die neuen Frequenzen angewiesen. R(rsmlp) = 0.79 ≈ normal 0.86. Die Pilotbeobachtung aus EXP-067 hält an frischen Seeds mit 4000 Schritten. *Ohne Codex-Prüfung der Schlussfolgerung (kein Guthaben).*
Trainer-Erweiterung `qk|vo` (1c6e480, 18/18 Tests, **ohne Codex**: gleiche Codepfade wie `attn`, nur zwei neue Einträge in RESET_PARTS). EXP-069 (40 Läufe) ab 11:35.

**Zyklus 18 (EXP-069 ausgewertet, Läufe 11:35–11:40, Auswertung 11:40 gemessen).** *Frage:* Muster (W_Q, W_K) oder Werte (W_V, W_O)? *Ergebnis (Pilot, 10/10 gültig):* **rsvo trägt den Ausschluss mit**
(b 0.49, Δb > 1 in 10/10), rsqk *unklar* (b 3.17, Funktion bleibt alt). Funktional nach rsvo: beide Mengen nötig (ohne alte 0.14, ohne neue 0.17); nur der volle Attention-Reset gibt den vollständigen Umstieg.
*Entscheidung:* Kandidat N32 präzisiert (Wertepfad). Bestätigung an frischen Seeds in einer späteren Sitzung (im Fenster), Codex-Prüfung der Trainer-Erweiterung nachholen.

**Zyklus 19 (EXP-070, Exploration, Läufe 11:42–11:44, Auswertung 11:44 gemessen).** *Frage:* Richtet sich der OV-Kreis im Fenster 25–50 sprunghaft auf die Ziele von A aus? *Ergebnis:* nein, gleichmäßiger Anstieg
(L 0.08 → 0.30 → 0.47 bei t = 10/25/50; 25→50 stärker nur in 2/10 Seeds). Die OV-Ausrichtung läuft der W_E-Energie voraus. *Entscheidung:* Die einfache Zeitform von N32-(V) ist nicht gestützt; der Reset-Befund
(EXP-069/N29b) bleibt, seine zeitliche Erklärung ist offen. [[experiments/EXP-070-ov-alignment/README|EXP-070]]

**Zyklus 20 (Codex wieder verfügbar: Nachprüfungen, 11:45–11:54 gemessen).** Test-Aufruf 11:45 ok. (1) *N29b-Schlussfolgerung:* kein Blocker (Run-IDs, Resets, Vorzeichen, Holm nachgerechnet); K4d auf „Reset-Empfindlichkeit“
eingeengt (Gewichte + AdamW-Zustand gemeinsam, Normen, MLP-Kontrolle nicht angeglichen, nur „stärker als dieser MLP-Reset“). Übernommen in [[FINDINGS]]. (2) *Trainer:* `qk|vo` korrekt, EXP-069 wertet die richtigen Läufe aus;
`group_train --save-model`: Fingerabdrücke korrekt, aber ein erzwungener Neulauf ließ ein altes `model_final.pt` liegen → behoben (Datei wird beim Start entfernt), mit einem Lauf geprüft.

### Abschlussbericht Sitzung 23 (Stand 11:57 Berlin, gemessen; Auftrag §10)

**Wichtigste Befunde (alle an frischen Seeds, eingefroren, gebunden, Schlussfolgerung von Codex geprüft):**
- **N29 bestätigt** (087e042): Nach einem Datenwechsel bei t = 50 ist das Endmodell auf die **alten** Zielfrequenzen angewiesen (Ablationskontrast 0.90 [0.85, 0.95], 20/20), bei t = 25 auf die **neuen**
  (0.60 [0.50, 0.70], 17/20 über 0.3). FINDINGS „K4c“ (Umkehrung eines Ablationskontrasts, keine netzweite Festlegung).
- **P2e bestätigt** (3c484ef): Das P2d-Maß gilt auch bei mul 113 (0.291 [0.268, 0.308]) und add 97 (0.294 [0.275, 0.312]), je 20/20. Eng: keine Nutzung über die Energie hinaus belegt.
- **N29b bestätigt** (db31564): Ein Reset der Attention (Gewichte + AdamW-Zustand) beim Wechsel bei t = 50 senkt den Kontrast um 1.49 [1.36, 1.61], stärker als ein doppelt so großer MLP-Reset (1.42 [1.28, 1.56]);
  beschreibend ist das Netz danach auf die neuen Frequenzen angewiesen (40/40 Richtungen). FINDINGS „K4d“ (Reset-Empfindlichkeit, kein Speicherort).
- **Explorationen/Piloten:** EXP-066 (P2d-Maß an P1-Modellen), EXP-067 (Attention, nicht MLP/W_U), EXP-069 (Wertepfad W_V/W_O trägt den Ausschluss, Muster unklar), EXP-068 und EXP-064 post hoc
  (**Funktion folgt der Energie**: bei gleicher entfernter Energie kein Vorteil der dominanten Menge), EXP-070 (OV-Ausrichtung steigt gleichmäßig, kein Sprung bei 25–50; negativ für die einfache Zeitform).
- EXP-039 (CPU) *unklar*: Λ-Uhr passt π besser als die Schrittuhr, aber nicht in jedem Seed. Neuer Kandidat [[NOVEL_DIRECTIONS]] N32 (Suche 27.09.: nicht gefunden, vorläufig).

**Offene Grenzen:** eine Architektur, add 113 für alle Persistenz-/Reset-Befunde; Ablationen trennen Funktion nicht von Energie; Reset-Befunde zeigen Empfindlichkeit, keinen Mechanismus; D₅₉ für das Funktionsmaß fehlt;
EXP-040 noch nicht gelaufen (Auswertungsfehler vor jedem Lauf behoben).
**Meine Fehler:** mehrfach geschätzte statt gemessene Uhrzeiten (alle korrigiert); zweimal CRLF durch `write_text` in Code-Dateien (sofort behoben); ein Klammerfehler in `confirm_p2e.measure`, den erst der
Smoke fand (behoben, neu eingefroren); die Import-Hülle der Hash-Liste war in N29 (und rückwirkend P2d, dort ohne Folgen) unvollständig (behoben, jetzt im Selbsttest geprüft).
**Codex:** 11:04–11:45 ohne Guthaben (N29b vor dem Einfrieren nur selbst geprüft, dokumentiert); danach alle offenen Prüfungen nachgeholt.

**Reproduktion (alle über guarded_run.py):** `confirm_n29.py --analyze lab/confirm/N29_manifest.json`, `confirm_p2e.py --analyze lab/confirm/P2e_manifest.json`, `confirm_n29b.py --analyze lab/confirm/N29b_manifest.json`
(nach Trainer-Änderungen am jeweiligen Manifest-Commit, `git worktree`); Blöcke `parallel_queue.py lab/confirm/{N29,P2e,N29b}_jobs.txt`; Piloten `parallel_queue.py lab/experiments/EXP-0{67,69,70}-*/jobs.txt`, dann `analyze.py`;
EXP-066/068 nur `analyze.py`; `lab/confirm/n29_posthoc_energy.py`, `lab/experiments/EXP-064-functional-regimes/posthoc_energy.py`.

**Nächste Aktion:** N29c (Wertepfad gegen Muster, Seeds 2320–2339) nach Codex einfrieren und im nächsten Fenster (ab 00:00) rechnen; D₅₉-Registrierung (P2f); EXP-040 im CPU-Programm; FINDINGS straffen.
**Runner:** geplante Aufgabe „GROKVERSE-Lab-Runner“ aktiv; laut `runner-state.json` nächster Start 2026-09-27 11:14:45Z = **13:14 Berlin** (außerhalb des Run-Fensters: nur Denk- und Vorbereitungsarbeit bis 00:00).
Das CPU-Programm (EXP-042) läuft bis zur Deadline 12:39 und wird dann vom Wächter beendet (kein Fehler; derselbe Befehl setzt fort).

**Zyklus 21 (N29c eingefroren, gerechnet, ausgewertet, 11:59–12:25 gemessen).** Codex vor dem Einfrieren: kein Blocker (Rundung der Pilotwerte korrigiert). Eingefroren 3c9cb63, Smoke ok (Wert nicht angesehen),
Block 12:00–12:25, 120/120 gebunden. ***H1 und H2 bestätigt:*** Wertepfad-Reset senkt den Kontrast um 0.85 [0.68, 1.00] gegenüber normal (16/20 über 0.5) und um 0.75 [0.60, 0.90] gegenüber dem Muster-Reset
(17/20 über 0.3). R: normal 0.81, rsqk 0.72, rsvo −0.04 (beide Mengen genutzt). Die Pilotbeobachtung aus EXP-069 hält an frischen Seeds. Codex-Prüfung der Schlussfolgerung läuft beim Sitzungsende;
FINDINGS-Eintrag „K4e“ erst danach (nächste Sitzung).

**Nachtrag zum Abschlussbericht (12:26):** zusätzlich **N29c bestätigt** (3c9cb63): Den Reset-Effekt der Attention trägt vor allem der Wertepfad (W_V, W_O), nicht das Muster (W_Q, W_K). Codex prüfte die Schlussfolgerung noch (12:27, kein Blocker); K4e im engen Wortlaut in FINDINGS. Nächste Aktion: D₅₉ (P2f) und die Zeitfrage (warum 25–50?).


## Sitzung 24 (2026-09-27, Start 12:29 Berlin, Deadline 15:29; Run-Fenster bis 13:00)

**Start (12:30, gemessen):** kein STOP, keine Python-Prozesse (das CPU-Programm der Sitzung 23 war mit deren Deadline beendet). CPU-Programm fortgesetzt
(`night_program.py --cpu --cpu-workers 3 --experiments EXP-042,EXP-040,EXP-014`, Log `lab/runner/logs/np_cpu_s24.log`).

**Zyklus 1 (EXP-071, Exploration, festgelegt 12:33 vor jedem Lauf, 2ddf934).** Frage: EXP-059 zeigt, dass pi(t) glatt steigt (keine Schwelle zwischen 25 und 50). Die Frage
"warum 25-50" wird damit zu: Welche Zustandsgroesse beim Wechsel bestimmt pi je Seed ueber die Schrittzahl hinaus? EXP-060 fand, dass der W_E-Vorsprung es nicht tut; EXP-071 prueft
die OV-Ausrichtung (Mass aus EXP-070) an 110 neuen reinen Laeufen (GPU). Laeuft.

**Zyklus 2 (EXP-072, Pilot, festgelegt 12:36 vor jedem Lauf).** Beim Vorbereiten von P2f (D59) gemessen: alle 100 P1-D59-Laeufe haben nach 2000 Schritten Train 1.0 und Test im
Median 0.03 (0/100 >= 0.9). K2 fuer D59 betrifft also die Irrep-Wahl vor dem Grokking; ein Funktionsmass auf ungesehenen Paaren ergibt an diesen Modellen keinen Sinn. EXP-072 prueft
mit 10 Laeufen a 20000 Schritten (Seeds 1000-1004, P1-Splits), ob und wann D59 generalisiert. Start 12:37; der Waechter beendet die Laeufe um ~12:57, falls sie nicht fertig sind.

**Zyklus 1, Ergebnis (EXP-071, 12:39):** 110/110 ok. Vorab-Regel formal erfuellt (Median rho(L, pi) je t = 0.36, 7/7 positiv), aber die 7 Korrelationen stammen von denselben 10 Seeds.
Post hoc auf Seed-Ebene: L r = 0.45, Permutations-p = 0.09; W_E-Energie E r = 0.11. Gepoolt haengt pi an t (0.91) nicht schwaecher als an L (0.89). **Urteil: unklar (schwacher Hinweis).**
Selbstkritik: Die Vorab-Regel haette die Abhaengigkeit der 7 Korrelationen beruecksichtigen muessen; fuer kuenftige Mehrzeitpunkt-Pilot-Regeln eine Seed-Ebene-Statistik vorab festlegen.
Entscheidung: nicht sofort bestaetigen (n ~ 30-40 noetig); gegen die offenen Fragen in FINDINGS priorisieren. Die Frage "warum 25-50" ist durch EXP-059 + EXP-071 umgedeutet: Es gibt keine
Schwelle, pi steigt glatt mit der Zahl der A-Schritte; keine gemessene Zustandsgroesse (W_E-Vorsprung EXP-060, OV-Ausrichtung EXP-070/071) erklaert den Verlauf besser als die Schrittzahl.

**Zyklus 2, Ergebnis (EXP-072, 12:46):** 10/10 ok. **D59 generalisiert** (9/10 Test 1.0 nach 20000 Schritten; erster Test >= 0.9 bei Median 4575, max. 8150). Eigene Ziel-Irreps in den Top-5:
4.7/5 bei Schritt 2000, 3.7/5 am Ende (Zufall 0.86). Nachtrag a (post hoc): Irrep-Form des P2d-Masses D = 0.223 ± 0.024, 5/5 positiv; die eigenen Irreps tragen 0.90-0.99 der W_E-Energie
(Seed 1000 F: 98.9 % in drei eigenen Irreps; die Plaetze 4-5 der Top-5 sind Rauschen, erst fuer einen Fehler gehalten und nachgeprueft). Entscheidung: P2f registrieren
(12000 Schritte, 20 frische Seeds, Codex vor dem Einfrieren), im naechsten Fenster rechnen.

**Fensterende:** Das CPU-Programm wurde um 12:54 vom Wächter gestoppt (Exit 3, erwartet; EXP-042 teilweise weiter, EXP-040/014 nicht gestartet). Keine Läufe nach 12:58.

**Zyklus 3 (P2f vorbereitet, 12:48–12:58).** Frage: Hält K2-Funktion bei D59? `lab/tools/confirm_p2f.py` (Port von confirm_p2e auf group_train und die Irrep-Projektion), Selbsttest ok (12:50),
Registrierung [[confirm/P2f_REGISTRATION|P2f]] (Seeds 2340–2359, Versuchs-ID 6, 12000 Schritte, n = 20). **Codex (Regel 18c):** keine Blocker; Projektion, Elementreihenfolge, Eingabeformat, Run-ID und
Lader-Felder bestätigt. Übernommen: (1) im Pilot waren bei 12000 Schritten 9/10 Arme ≥ 0.9 (1004 F: 0.23), der Pilotwert D stammt von 20000 Schritten → offengelegt; (2) `--analyze` löscht zuerst eine alte
Zusammenfassung; (3) Selbsttest prüft den fold(2k)-Ausschluss wirksam. Der geänderte Selbsttest konnte nicht mehr laufen (Fenster zu) → **nicht eingefroren**, Einfrieren ab 00:00.

**Zyklus 4 (FINDINGS auf eine Seite, 12:59–13:00).** Regel 15a verlangte höchstens eine Seite; FINDINGS hatte 250 Zeilen. Die Abschnitte wurden wortgleich nach [[FINDINGS_DETAILS]] verschoben
(per difflib geprüft: nur Kopf und die angehängte P2f-Reservierung neu), FINDINGS.md neu als Übersicht: Kernaussagen-Tabelle, Explorationen mit Planungsgewicht (EXP-072, EXP-071), Grenzen, Literatur,
Programm, größte offene Frage (jetzt: was macht die Wahl fest, wenn keine gemessene Zustandsgröße den Zeitverlauf besser erklärt als die Schrittzahl?). Dabei ein Fehler von mir: `sed -i` auf die
CRLF-Notiz FINDINGS_DETAILS (Zeilenenden wurden LF), sofort auf CRLF zurückgesetzt.

**Zyklus 5 (EXP-073 vorbereitet, 13:01–13:15).** Frage: Welcher Netzteil ist für die Zeitabhängigkeit der Festlegung empfindlich? Neues Trainer-Werkzeug `--rewind-at-switch X --rewind-from R`
(Teil X samt AdamW-Zustand beim Wechsel auf seinen Stand nach Schritt R zurück). Selbstprüfung: „alles zurückspulen“ muss den Wechsel bei R reproduzieren (neuer Test `test_rewind`, CPU, bitgleich).
Neuheitssuche (N33): Modul-Zurückspulen ist bekannt (Chatterji et al. 2019, am fertigen Netz); die Anwendung beim Datenwechsel mit Optimiererzustand und Weitertraining nicht gefunden (vorläufig).
**Codex (Regel 18c, gemeinsamer Trainer):** vier Blocker, alle selbst geprüft und übernommen: Test ohne `--test-file` (wäre gescheitert), Ban-Bedingungen nicht zurückgespult (jetzt nur baseline),
Chimären-Störung (Lesarten als Empfindlichkeit, Loss-Diagnose im Trainer-Ereignis), Gleichheitsprüfung je Richtung. Trainer-Änderung ungetestet bis 00:00.

**Zyklus 5, Nachtrag (13:16):** Codex-Nachprüfung der vier Korrekturen: keine verbleibenden Blocker, keine neuen Fehler (`EXP-073-part-rewind/codex_recheck_s24.txt`).

**Zyklus 6 (EXP-074 vorbereitet, 13:16–13:20).** Frage: Gilt das Reset-Muster aus K4d/K4e auch bei anderen Aufgaben (FINDINGS-Grenze 2, Regel 15c)? Zuerst die add-113-Referenz im Maß π aus gespeicherten
Läufen nachgerechnet (post hoc, nur numpy, bekannte Seeds 400–409): Median π normal 1.04; Δπ Attention 0.84 (10/10 > 0.3), Wertepfad 0.57 (9/10), Muster 0.13, MLP 0.15, Unembedding −0.04. Das ist die
spektrale Entsprechung der Ablationsbefunde N29b/c. Pilot EXP-074 im EXP-044-Protokoll (Seeds 80–89, F→G bei t = 50, add 97 und mul 113, 100 Läufe) mit vorab festgelegter Lesart (Schwellen etwa die
Hälfte der add-113-Effekte). Beim Schreiben der Auswertung die Reihenfolge der Suffixe im Run-Namen erst angenommen, dann am Code geprüft und korrigiert (`_at50_add97_rsattn_devcuda`).

**Rückblick nach sechs Zyklen (Auftrag §4, zwischen 13:20 und 13:23 gemessen).** *Gelernt:* D₅₉ groks und behält die Steuerung (EXP-072), das eröffnet Programm A die einzige nicht-abelsche Bestätigung (P2f). Für Programm B:
Die Festlegung ist keine Schwelle; weder W_E-Vorsprung noch OV-Ausrichtung erklären ihren Zeitverlauf (EXP-060/070/071). *Wiederholen wir uns?* Ja, teilweise: Seit Sitzung 22 kamen mehrere
Messgrößen-Versuche (EXP-060, 061, 070, 071), die jeweils eine Zustandsgröße gegen π stellten, alle ohne klares Ergebnis. *Angepasste Strategie:* keine weiteren Korrelationsmaße, sondern Eingriffe,
die zwischen benannten Modellen entscheiden: EXP-040 (Init-Amplitude skalieren, H40 Amplitudenrennen; seit Sitzung 10 festgelegt, nie gelaufen, weil die CPU-Warteschlange immer spät startete →
heute Nacht zuerst), EXP-073 (Teil-Zurückspulen), EXP-074 (Reset-Muster an anderen Aufgaben). *Messungen geeignet?* π ist ein Energiemaß; nach EXP-068 folgt auch die Funktion der Energie, für
Persistenzfragen also vertretbar, für Nutzungsfragen nicht. *Nächste angegriffene Annahme:* „Die Festlegung ist eine Eigenschaft von W_E“ (EXP-073) und „die Init-Amplitude setzt die Uhr“ (EXP-040).

**Zyklus 7 (EXP-075 vorbereitet, bis 13:23 gemessen).** Frage: Ist die frühe Festlegung an die Attention gebunden (die Reset-Befunde K4d/e legen das nahe) oder allgemein (H40)? Entscheidender Gegentest:
dieselbe π(t)-Kurve in der MLP-Architektur ohne Attention (EXP-045: dort steuerbar, 0.004 s/Schritt). Vorab: Transformer-t½ aus EXP-059 nachgerechnet (33.3, erst geschätzt 34.1, dann aus
summary.json korrigiert); Lesart t½ ≤ 2 × 33.3 → „ähnlich früh“, > 4× oder π(200) < 0.5 → „deutlich später“. 120 Läufe, wenige Minuten GPU.

**Zyklus 8 (D₅₉-Spektren nachgewertet, S1 in P2f, 13:24–13:33).** Frage: Konzentriert sich die Energie auf die gesteuerten Irreps vor oder mit dem Grokking? Aus gespeicherten EXP-072-Spektren:
Anteil der eigenen Irreps 0.29–0.38 bei Schritt 250 (Zufall 0.17), 0.39–0.59 bei 2000, ≥ 0.9 erst 500–3000 Schritte nach dem ersten Test ≥ 0.9. Post hoc auffällig: höherer Anteil bei 2000 → früheres
Grokking (ρ = −0.75, Permutations-p 0.008, 10 Läufe aus 5 Seeds). Im Geist bekannt (Fortschrittsmaße). Entscheidung: nicht post hoc stehen lassen, sondern als vorab festgelegte Sekundärhypothese S1
in P2f an 20 frischen Seeds prüfen (keine Zusatzläufe). **Codex** (zwei Nachprüfungen): zuerst zwei Blocker (S1 hätte über den gemeinsamen Lader das primäre Urteil gefährden können; ρ undefiniert bei
konstanten Rängen), beide selbst bestätigt und behoben; zweite Nachprüfung: keine Blocker. Selbsttest von confirm_p2f ab 00:00 (Pflicht vor dem Einfrieren).

**Zyklus 9 (Literatur zu K2 bei Gruppen, 13:34–13:35).** Frage: Ist die Split-Steuerung der Irrep-Wahl (K2, jetzt auch D₅₉ nach dem Grokking) schon bekannt? Neu gefunden: Marchetti, Kunin et al.
(ICML 2026, arXiv 2602.03655): Irreps werden einzeln gelernt, Reihenfolge durch die Fourier-Statistik der **Eingabekodierung**, bei **gleichverteilten** Daten, auch D_n. Volltext geprüft: keine
nicht-uniformen Paarverteilungen, Gradientenfluss ohne Adam/Weight Decay/Grokking; bei One-hot sind dort alle Irreps gleichauf. Einordnung: K2 ergänzt das (die Paarmaske bricht die Gleichheit),
nach unserer Suche nicht gefunden (vorläufig). FINDINGS-Literaturzeile ergänzt; Brückenfrage (M0 als effektive Kodierungsstatistik im AGF-Rahmen) als Programm-C-Kandidat notiert.

**Zyklus 10 (EXP-076, Theorie-Rechnung ohne Läufe, 13:37–13:38).** Frage: Ist M0 der AGF-Nutzen erster Stufe bei nicht-uniformer Paarverteilung (Brücke zu Marchetti/Kunin)? Vorab festgelegt (Commit vor der
Rechnung), reine numpy-Rechnung an den 20 EXP-016-Splits. **Ergebnis: keine Brücke** (Median ρ −0.02; U trifft die Ziele nur zufällig, 0.45/5; M0 5/5). Selbstprüfung (Gleichstand bei allen Paaren) ok.
Mögliche Erklärung (Spekulation): M0 summiert je Ausgabe inkohärent, wie ein Gradient durch eine zufällige feste Auslese; das AGF-Neuron lernt die Auslese aus null. Mein schneller Gegencheck dazu war
falsch gebaut (Phase unabhängig von c = reine Häufigkeitsmodulation) und zählt nicht. Neue Kandidatenfrage N34 (Init-Skala der Auslese und Split-Steuerung) notiert, nicht geprüft.

### Abschlussbericht Sitzung 24 (Stand 13:40 Berlin, gemessen; Auftrag §10)

**Wichtigste Befunde (alle Exploration/Pilot, bekannte Seeds, kein Urteil):**
- **EXP-072:** D₅₉ generalisiert in diesem Aufbau (9/10 Läufe, erster Test ≥ 0.9 bei Median 4575 Schritten; P1 mit 2000 Schritten lag ganz vor dem Grokking). Die gesteuerten Irreps überleben das
  Grokking und tragen danach 0.90–0.99 der W_E-Energie; Irrep-Form des Funktionsmaßes D = 0.22 ± 0.02 (5/5, post hoc). Früherer Anteil der eigenen Irreps bei Schritt 2000 ging mit früherem Grokking
  einher (ρ = −0.75, post hoc) → als Sekundärhypothese S1 in P2f vorab festgelegt.
- **EXP-071:** Die OV-Ausrichtung beim Wechsel sagt die Persistenz je Seed höchstens schwach voraus (r = 0.45, p = 0.09) und erklärt den Zeitverlauf nicht besser als die Schrittzahl. *Unklar.*
- **EXP-076 (Theorie):** Das Maskenspektrum M0 ist im einfachsten AGF-Modell nicht der Nutzen erster Stufe (Treffer = Zufall). *Negativ.*
- **Literatur:** Marchetti, Kunin et al. (ICML 2026): Irrep-Reihenfolge aus der Kodierung bei gleichverteilten Daten; unsere Paarmasken-Steuerung dort nicht abgedeckt (vorläufig nicht gefunden).
- **FINDINGS** wieder eine Seite (Details wortgleich in FINDINGS_DETAILS).

**Vorbereitet für ab 00:00 (alle vor jedem Lauf festgelegt und committet):** P2f (D₅₉-Bestätigung, Codex ohne Blocker, Selbsttest und Einfrieren ausstehend), EXP-073 (neues Trainer-Werkzeug
`--rewind-at-switch`, Codex: 4 Blocker behoben, Nachprüfung ohne Befund; Trainer-Test ausstehend), EXP-074 (Reset-Muster bei add 97/mul 113), EXP-075 (Festlegung ohne Attention), EXP-040 zuerst auf der CPU.

**Offene Grenzen:** alle Persistenzbefunde weiterhin nur add 113 (EXP-074/075 sollen das angehen); Funktion folgt der Energie; die Trainer-Änderung ist bis zum Test ungetestet.
**Meine Fehler:** mehrere geschätzte statt gemessene Uhrzeiten (alle korrigiert); ein `sed -i` auf eine CRLF-Notiz (sofort repariert); falsche Suffix-Reihenfolge im EXP-074-Lademuster (vor jedem Lauf
gefunden und korrigiert); ein falsch gebauter Kontrollfall in EXP-076 (als ungültig vermerkt).
**Codex:** P2f-Registrierung (keine Blocker, 3 kleine Punkte übernommen), Rewind-Werkzeug + EXP-073 (4 Blocker, alle übernommen; Nachprüfung ohne Befund), P2f-S1 (2 Blocker übernommen; Nachprüfung ohne Befund).

**Reproduktion:** `parallel_queue.py lab/experiments/EXP-071-ov-lead-predicts/jobs.txt` + `analyze.py`; `parallel_queue.py lab/experiments/EXP-072-d59-grok/jobs.txt` + `analyze.py` + `p2d_irrep.py`;
`python lab/experiments/EXP-074-reset-other-tasks/reference_add113.py`; `python lab/experiments/EXP-076-agf-utility/compute.py` (alle Läufe über guarded_run.py).
**Nächste Aktion:** ab 00:00 laut [[STATE]]: Tests → CPU (EXP-040 zuerst) → P2f einfrieren und rechnen → EXP-073/074/075 auf der GPU.
**Runner:** geplante Aufgabe „GROKVERSE-Lab-Runner“ aktiv; `runner-state.json`: nächster Start 2026-09-27 14:04:45Z = **16:04 Berlin** (außerhalb des Fensters). Das Fenster öffnet um 00:00 voraussichtlich
mitten in einer späteren Sitzung; diese muss den Wechsel selbst bemerken (`guarded_run.py --check`).

**Zyklus 11 (Regel 19, Veröffentlichung vorbereiten, 13:40–13:44).** Neuer Nutzerauftrag (Regel 19 in der Präambel, von der interaktiven Sitzung des Nutzers gemeldet und in der Datei selbst geprüft).
Angelegt: [[paper/STATUS]] (Punkte a–f, „Offen für den Nutzer“: Autorschaft/Rechte der Originalstudie, Einreichung, Venue, KI-Offenlegung, menschliche Literaturprüfung),
[[paper/draft]] (Gerüst, alle bestätigten Kernaussagen mit Zahlen wörtlich aus FINDINGS_DETAILS, Explorationen getrennt, KI-Offenlegung als Entwurf), [[paper/robustness_plan]] (R1 lr/wd/train_frac
für K2, R2 für K4c; braucht neue Trainer-Optionen + Codex), Abbildungen 2 und 3 als Skripte aus den eingefrorenen Zusammenfassungen (Mittelwerte gegen die registrierten Werte geprüft). Die gründliche
Literaturrecherche ([[paper/related_work]]) läuft über einen Hintergrund-Agenten mit Suchprotokoll. Fehler von mir: eine Ersetzung im Abbildungsskript hat Docstring-Text mitverändert (korrigiert).

**Zyklus 12 (Regel 19 fortgesetzt, bis 13:47).** Abbildungen 1 und 4 als Skripte (Maske gegen gelerntes Spektrum, EXP-016 Seed 10 F: 4/5 Ziele, 25 durch die Oberwelle 32 ersetzt; π-Pilotkurve mit den
N28-Punkten, KI aus den eingefrorenen Werten nachgerechnet: 0.340 [0.302, 0.377] und 0.998 [0.965, 1.032]). Reproduktions-README (Umgebung, Zuordnung Abbildung → Block → Befehle, Plan).
Registrierungsentwurf P4 (MLP, 4× Breite, Integer-Addition an frischen Seeds; Pilot-SD nachgerechnet, n = 15 je Bedingung). STATE-Prioritäten um Regel 19 ergänzt.

**Zyklus 13 (Regel 19: Trainer-Optionen und Literatur, 13:47–13:53).** `freq_ban.py` hat jetzt `--lr`, `--weight-decay`, `--train-frac` (späte Argumente: alte Fingerabdrücke und Run-IDs unverändert).
Codex (Regel 18c): zwei Blocker, beide selbst bestätigt: `:g` in der Run-ID nicht injektiv (jetzt `repr`), und train_frac ist in `confirm_splits` noch fest 0.3 (Pipeline-Arbeit, im Robustheitsplan vermerkt);
dazu Schutz gegen leere Splits. Ungetestet bis 00:00 (neuer Test `test_hp_overrides`). **Literatur:** Hintergrund-Agent hat [[paper/related_work]] geschrieben (≈ 50 Arbeiten, Suchprotokoll, Prüfgrad je Eintrag).
Engste Arbeiten: K2 — LeDoux 2026 (Reihenfolge der Daten setzt die Grundfrequenz; von mir am Abstract geprüft: Reihenfolge, nicht Menge), Marchetti et al. 2026, He et al. 2026; K4 — Lyle et al. 2025,
kritische Perioden (Achille 2019, Kleinman 2023/24), Primacy Bias; K4d/e — Teil-Resets (Nikishin 2022, Zhou 2022), Modul-Kritikalität. K2-Funktion allein trägt wenig Neuheit (Ablationen seit Nanda 2023).

**Zyklus 14 (Regel 19a: R1 vorbereitet, 13:55–14:08).** Registrierungsentwurf [[confirm/R1_REGISTRATION_DRAFT|R1]] (K2 bei lr 5e-4/2e-3, wd 0.3/3, train_frac 0.2/0.5; je 15 frische Seeds, Holm über 6,
Mindesteffekt 1) und `lab/tools/confirm_r1.py` (P1-Konstruktion mit dem Anteil als Parameter, ohne `confirm_splits.py` zu ändern). ε-Kalibrierung auf gleichen M0-Zielanteil (numpy, Kalibrier-Seeds):
2.838 (0.2), 1.465 (0.5). **Codex:** drei Blocker (Bisektion ohne Monotonie-Garantie, Seeds/ε nicht validiert, versprochene Diagnosen fehlten), alle selbst bestätigt und behoben; Aussage auf
„nach 2000 Optimierer-Schritten“ eingeengt. Nachprüfung zuerst ungültig (mein Auftrag verbot auch das Lesen), dann ohne Befund. Ungetestet bis 00:00.

**Nachtrag zum Abschlussbericht Sitzung 24 (14:10, gemessen): Regel 19 (Veröffentlichung vorbereiten)** kam um ≈ 13:40 als neuer Nutzerauftrag hinzu (in der Präambel geprüft).
Erledigt: [[paper/STATUS]] mit „Offen für den Nutzer“ (Autorschaft/Rechte der Originalstudie, Einreichung, Venue, KI-Offenlegung, menschliche Literaturprüfung); [[paper/draft]] (alle bestätigten
Aussagen mit Zahlen aus FINDINGS_DETAILS, Methoden-Definitionen, Positionierung gegen LeDoux 2026 / Marchetti et al. 2026 / Lyle et al. 2025, Explorationen getrennt); [[paper/related_work]]
(≈ 50 Arbeiten, Suchprotokoll, Prüfgrad je Eintrag; Stichprobe LeDoux selbst geprüft); Abbildungen 1–4 als Skripte aus gespeicherten Läufen/eingefrorenen Zusammenfassungen; [[paper/repro/README]];
Robustheit: Trainer-Optionen `--lr/--weight-decay/--train-frac` (Codex), [[confirm/R1_REGISTRATION_DRAFT|R1]] + `confirm_r1.py` (Codex, kalibriert); [[confirm/P4_REGISTRATION_DRAFT|P4]]-Entwurf (Code fehlt).
**Ungetestet bis 00:00:** `--rewind-at-switch`, die Hyperparameter-Optionen, `confirm_p2f.py` nach den Codex-Änderungen, `confirm_r1.py`. **Nächste Aktion unverändert:** [[STATE]] „Nächste Schritte“.

**Zyklus 15 (Zahlenprüfung des Paper-Entwurfs, 14:12–14:16).** Unabhängiger Prüf-Agent (Claude, nur lesend) hat alle Aussagen in [[paper/draft]] gegen die eingefrorenen Zusammenfassungen und Registrierungen
abgeglichen: alle Zahlen in §3 korrekt (≈ 85 Punkte OK), 15 Formulierungs-/Umfangsprobleme, darunter „flips“ statt „Umkehrung eines Ablationskontrasts“ (Codex hatte das für N29 schon verworfen),
Wertepfad gegen MLP nie verglichen, EXP-068 nur an N29-Modellen, fehlende Negativergebnisse P2 (nicht auswertbar) und P2b (abgebrochen), Smoke erst ab N28, P2f als „registriert“ statt „vorbereitet“.
Zwei davon hatte ich vorher selbst gefunden; zwei weitere (P2, Smoke) selbst an den Quellen nachgeprüft. Alle übernommen; Titel enger gefasst („a 25–50-step history persists“ statt „locks in“).
Lehre: Ein Entwurf aus korrekten Zahlen kann trotzdem überdehnen; die Registrierungs-Wortlaute nach Codex sind die Obergrenze für jede Paper-Formulierung.

**Sitzungsende (14:17, gemessen, Deadline 15:29).** P4-Code bewusst nicht mehr begonnen: Für die Nacht liegen schon drei ungetestete Trainer-Funktionen (`--rewind-at-switch`, `--lr/--weight-decay/--train-frac`)
und zwei ungetestete Werkzeuge (`confirm_p2f.py` nach Änderungen, `confirm_r1.py`) an; ein drittes, in einer Stunde geschriebenes Bestätigungswerkzeug für drei verschiedene Trainer würde mehr Risiko
als Nutzen bringen. Bausteine sind im [[confirm/P4_REGISTRATION_DRAFT|P4-Entwurf]] inventarisiert. Alle Änderungen dieser Sitzung sind committet (einzelne Pfade; Nutzerdateien des Runners unberührt).
Gedächtnis ergänzt: Codex-Aufträge müssen Lesen erlauben; Backslashes in Heredoc-Python brechen.

## Sitzung 25 (2026-09-27, Start 14:19 Berlin, Deadline 17:19; Run-Fenster zu bis 00:00)

**Zyklus 1 (Regel 19b/c: P4-Werkzeug und schlanker Repro-Trainer, 14:21–14:28).** *Frage:* Können die drei Piloten (MLP, 4× Breite, Integer-Addition) als eingefrorener
Bestätigungsblock gerechnet werden, und lässt sich K2/K4 mit einem schlanken Trainer ohne Labor-Ballast reproduzieren? *Änderung:* `lab/tools/confirm_p4.py` (drei Trainer,
Bindung/Manifest über `bound_block`, Splits add 113 = P1-Konstruktion mit Versuchs-ID 7, intadd = EXP-048-Konstruktion mit um die Versuchs-ID erweiterten Strömen; Selbsttest
prüft den exakten Nachbau der Pilot-Splits mit dem Pilotstrom); Nachtrag im [[confirm/P4_REGISTRATION_DRAFT|P4-Entwurf]]; Seeds 2360–2419 (P4) und 2420–2509 (R1, war im Code,
aber nicht in FINDINGS_DETAILS reserviert) reserviert. Pilot-Δ_pow der MLP aus den gespeicherten EXP-045-Spektren nachgerechnet (post hoc): 7.68 ± 2.51 bei 10 000, 2.45 ± 0.15
bei 2000 Schritten → n = 15 reicht. `lab/paper/repro/train.py` (Standardpfad von `freq_ban.py` inkl. Wechsel und Teil-Reset) mit `--compare-to` gegen gespeicherte Läufe;
Prüfbefehle (P1 Seed 1000 F; N29b Seed 2300 Attention-Reset) in [[paper/repro/README]]. Beide Dateien nur per `py_compile` auf Syntax geprüft (kein Test, kein Lauf).
Selbst geprüft: Ergebnisfelder echter Pilotläufe (MLP: `events.generalization_step`, `config.arch = mlp`, 10 000 Schritte; d512/intadd: `config.d_model`, `config.p = 225`,
Spektren (9, 56), `we_final.npy`) passen zu den `Expect`-Angaben. *Mein Fehler:* eine geschätzte Uhrzeit (14:40) im P4-Nachtrag, sofort durch die gemessene ersetzt.
*Ergebnis:* vorbereitet, **ungetestet** bis 00:00. *Nächster Schritt:* Codex-Prüfung (läuft), dann einarbeiten.

**Zyklus 1, Fortsetzung (Codex zu P4, bis 14:34).** Codex (nur lesend, [[confirm/P4_codex_review_s25.txt]]): *ein Blocker*: Entwurf nennt einen t-Test, der Code den exakten
Vorzeichen-Permutationstest. Selbst bestätigt (Zeile 14 des Entwurfs); übernommen durch Registrierung des exakten Tests (wie P1) im Nachtrag. Kleinere Punkte übernommen: Vorabprüfung
auch der `.json`-Splits, Stromvergleich am selben Seed, Exaktheitsprüfung p = 1/2^15, `--save-model`-Erwähnung gestrichen. Verworfen (mit Grund): synthetische Ergebnisordner je Trainer
(echte Felder bereits geprüft, Smoke vor dem Block). Codex bestätigt ausdrücklich: Run-IDs aller drei Trainer, Lader-Erwartungen, 10 000 MLP-Schritte trotz Stopp-Regel, Split-Konstruktion,
keine Seed-Überlappung, Statistik intern korrekt.

**Zyklus 2 (Paper §5 Theorie, bis 14:34).** *Frage:* Trägt die Herleitung erster Ordnung (Masken-Spektrum → erster W_E-Gradient) einen ausformulierten Theorie-Abschnitt?
*Änderung:* §5.1–5.4 im [[paper/draft]] (Aufbau, M0c/M0 für gemeinsamen/getrennten Pfad, Status der Vorhersagen, Grenzen inkl. Adams Vorzeichenschritt). *Ergebnis:* Eine numpy-Prüfung
der Identitäten (reine Rechnung) hat **einen Fehler in meinem ersten Wortlaut** gefunden, der auch schon in der Skizze aus Sitzung 24 stand: Nicht „die Token-Häufigkeiten fallen heraus“,
sondern nur die **eigene** Häufigkeit einer Zeile (P⊥ entfernt den c-Mittelwert). Die Häufigkeiten des **anderen** Operanden bleiben: für m(a, b) = ρ(a) ist die Leistung des gemeinsamen
Pfads exakt p|ρ̂(k)|² (numerisch, relativer Fehler 1e-14). Die EXP-047-Vorhersage bleibt richtig, beruht aber auf den schwachen Randverteilungen der konstruierten Splits (CV 0.14,
eigener Anteil 0.9 %), nicht auf einem allgemeinen Wegfall. Korrigiert im Entwurf (§5 Skizze und §5.2). FINDINGS_DETAILS Zeile 240 („Häufigkeitsanteil fällt exakt heraus, zentriertes
M0“) ist im engen Sinn (eigene Häufigkeit) richtig und bleibt. *Neue prüfbare Folgerung:* Ein Split mit stark strukturierten Häufigkeiten nur eines Operanden müsste zu den Frequenzen von ρ
steuern → Kandidat für Paket C (Entscheidung zwischen „nur Paarstruktur“ und „erste Ordnung inkl. Fremd-Häufigkeiten“), Literatursuche folgt.

**Zyklus 3 (Regel 19e: Volltextprüfung der engsten Arbeiten, bis 14:36).** *Frage:* Enthalten die engsten Arbeiten im Volltext schon (a) Steuerung über die Split-Zusammensetzung,
(b) Festlegung nach Datenwechsel, (c) Attention- gegen MLP-Reset? *Ausführung:* Hintergrund-Agent (arXiv-HTML-Volltexte inkl. Anhänge, Semantic-Scholar-Vorwärtszitate von Nanda 2023),
Ergebnis [[paper/fulltext_check_2026-09-27]]. Von mir selbst am Abstract geprüft: Dong 2607.27281 und Khanh 2607.06628 (beide bestätigt; eine Überdehnung des Agenten korrigiert:
Value-Reset bei Dong „do nothing“, nicht „schlechter als kein Reset“). *Ergebnis:* K2 weiter „nicht gefunden“ (LeDoux: zufällige Teilmengen ändern die Frequenz nicht; He et al. 2026b §6 nennt
den Split als offen). **K4d eingeschränkt:** In Sprachmodellen stellt ein QK-Reset die Lernfähigkeit her, Value nicht (Dong 2026); „Attention-Reset > MLP-Reset“ ist für Transformer
nicht neu, unsere Reihenfolge (Wertepfad > QK) ist umgekehrt → als Gegensatz berichten. K4: Khanh 2026 (Frequenzidentität per Gewichtsrichtung, gleicher Modelltyp) und LeDoux §3.4 zitieren;
Lyle et al. 2025 von „teilweise, deutlich“ auf „teilweise“. Eingearbeitet in [[paper/draft]] (§1, §3.5), [[paper/related_work]] (Nachtrag), [[FINDINGS]] (Literatur). *Entscheidung:*
Die umgekehrte QK/VO-Reihenfolge ist eine offene Frage für B (verschiedene Aufgaben, Skalen, Protokolle); kein neuer Versuch jetzt.

**Zyklus 4 (Programm C: neue Vorhersage aus der Theorie, bis 14:40).** *Frage:* Steuert ein Split, dessen einzige Struktur die periodisch geformte Häufigkeit des linken Operanden ist,
die gelernten Frequenzen? (Konkurrenz: „nur Paarstruktur“ nach EXP-047 gegen „erste Ordnung inkl. Fremd-Häufigkeiten“.) *Änderung:* Literatursuche (3 Begriffe, nicht gefunden, vorläufig),
Offline-Rechnung: ε = 2 bringt alle fünf Ziele in M0 nach oben (Rang 3.0, Anteil 0.191, wie P1), CV links 0.53, rechts 0.14. [[experiments/EXP-077-marginal-steering/README|EXP-077]] als Pilot
vorab festgelegt (Seeds 770–779, 40 Läufe, Lesart vorab), Splits gebaut, Jobliste, Auswertung (nur `py_compile`), N35 in [[NOVEL_DIRECTIONS]]. *Ergebnis:* vorbereitet, nicht ausgeführt
(Fenster zu); in STATE als Schritt 6 der Nacht eingetragen (≈ 5 min GPU).

**Zyklus 5 (Paper: Related-Work-Abschnitt, bis 14:40).** Abschnitt 1b im [[paper/draft]] als Fließtext aus [[paper/related_work]] und der Volltextprüfung; nur Aussagen aus der Tabelle bzw.
dem Volltextbericht; eine eigene Überdehnung (Stander et al. als „beliebig“-Quelle) vor dem Commit korrigiert. Alles für die menschliche Prüfung markiert.

**Zyklus 6 (Theorie-Grenze: Adams Vorzeichenschritt, bis 14:43).** *Frage:* Zerstört der erste AdamW-Schritt (≈ lr · sign(g)) die Frequenzinformation des ersten Gradienten? *Rechnung*
(numpy, Modell erster Ordnung mit isotroper Zufalls-Jacobi-Matrix, d = 128, P1-Konstruktion, Kalibrier-Seeds 900–909 × F/G): Top-5 von sign(g) = Ziele in 20/20 Fällen (wie g selbst),
Zielanteil 0.152 gegen 0.191. *Ergebnis:* Im Modell bleibt die Auswahl unter dem Vorzeichenschritt erhalten; nur ein Modellbefund, nicht am Netz gemessen. In §5.4 des Entwurfs;
Skripte `lab/paper/repro/theory_identity_check.py`, `theory_sign_check.py`. Außerdem: [[BACKLOG]] um Sitzung 25 ergänzt; EXP-077 Nachtrag a (zweiter Weg über die eigene Häufigkeit,
Lesart vor jedem Lauf eingeengt); N36 (Routing oder Inhalt) als Lesart des Dong-Gegensatzes.

*Nachtrag Zyklus 1:* Entwurfsmanifest `lab/confirm/P4_manifest_DRAFT.json` (Seeds mlp 2360–2374, d512 2375–2389, intadd 2390–2404) erzeugt; dazu `confirm_p4` importiert und nur
`check_design`, `check_registered` und die Jobliste (90 Zeilen) aufgerufen, kein Selbsttest, kein Training. Codes-Hashes und Commit fehlen absichtlich (erst nach dem Selbsttest).

**Zyklus 7 (Prüfung des Repro-Trainers, bis 14:50).** Unabhängiger Claude-Prüfagent (nur lesend) hat `repro/train.py` und `repro/k2.py` gegen den Standardpfad von `freq_ban.py`,
`confirm_p1` und `training/grokverse` abgeglichen: **keine Blocker** (RNG-Reihenfolge bis zur Init, Trainingsschritt, Wechsel/Reset, Spektrenformel identisch; kein Dropout, `evaluate` ohne
Einfluss; `--stop-after-gen` ändert die Spektren an gemeinsamen Schritten nicht). Übernommen: Wechsel verlangt jetzt `--test-file` (wie freq_ban); Testindizes sortiert (wie freq_ban);
Schutz gegen gerades p; `k2.py --compare-p1` scheitert jetzt bei Abweichung > `--tol` (Standard 1e-3; die P1-Werte kommen aus einer FFT, k2 aus der Basis-Matrix → nur Rundung).
Nicht übernommen: Sperren/atomisches Schreiben im schlanken Trainer (bewusst schlank; eine Aufrufinstanz schreibt in eigene Ordner). Weiter ungetestet bis 00:00.

**Zyklus 8 (Paper: Diskussion, bis 14:51).** Abschnitt 5b im [[paper/draft]] (was die Daten wählen, wie früh und wo, offene Fragen), mit den Einschränkungen aus Khanh 2026 und Dong 2026.
Bewusst **kein** K4-Repro-Skript heute: π mit Spurkontrollen und EXP-056-Splits wäre ein weiteres großes ungetestetes Werkzeug für eine volle Nacht; erst nach der Gleichwertigkeit.
Unabhängiger Prüfagent (nur lesend) gleicht die neuen Abschnitte 1b, 5, 5b gegen die Quellen ab (läuft).

**Zyklus 8, Fortsetzung (Zahlenprüfung der neuen Paper-Abschnitte, bis 14:57).** Unabhängiger Prüfagent (nur lesend): Mathematik in §5.2 korrekt; 12 Punkte, alle selbst an den Quellen
nachgesehen und übernommen, u. a.: Khanh überdehnt (Autoren: „suggestive“, drei Paare; Setup von mir am Volltext belegt und jetzt in related_work vermerkt); **EXP-021 zitiert, obwohl nie
gerechnet** (jetzt: EXP-016 post hoc 14/14, EXP-021 nicht gelaufen); EXP-033-Aussage ohne ihre Einschränkungen (nur Phase 1, Aktivierungswechsel, eine Stufe); EXP-047-Vorhersage beruhte
auf dem unkorrigierten Argument; Δ 0.3 ist das Top-5-Maß (p = 0.33); die Randverteilungen sind nicht „schwach“, sondern zielangereichert (Rang 11.6) bei CV 0.14; post-hoc-Erklärung
nicht als Ergebnis; „relies“ → Ablationskontrast; EXP-077 trennt die Wege nicht; LeDoux-Epochen und Bedingung (feste Stride-Reihenfolge) präzisiert; EXP-040/074/075 „vorbereitet“.
Die vom Agenten nachgerechnete Zahl (zentriertes M0c der shuf-Splits 26.2 / 0.090) habe ich selbst nachgerechnet (gleich) und im EXP-047-README vermerkt. *Lehre (wie Sitzung 24):*
Neue Paper-Texte immer gegen die Quellen prüfen lassen; meine Zusammenfassungen überdehnen vor allem Einschränkungen von Piloten.

**Zyklus 9 (Nachauswertung EXP-047 als Vorwissen für EXP-077, bis 14:58).** *Frage:* Zeigt die shuf-Kontrolle im feineren Maß Δ_pow eine kleine Steuerung über die (zielangereicherten)
Randverteilungen? *Ergebnis (post hoc, gespeicherte Läufe):* nein, 0.02 ± 0.65 (6/10, p = 0.47); eng 7.75 ± 1.63. *Einordnung:* passt zur korrigierten Theorie (zentriertes M0c der shuf-Splits
auf Zufallsniveau, 26.2), entscheidet aber EXP-077 nicht vor: dort ist der Anteil erster Ordnung hoch (0.146 bei ε = 2). Die Vorhersage für EXP-077 bleibt damit scharf: erste Ordnung → deutlich
positiv; „nur Paarstruktur“ → ≈ 0.

**Zyklus 10 (Exploration an eingefrorenen P1-Daten, bis 14:59).** *Frage:* Sagt die Stärke des Maskensignals eines Split-Paars die Stärke der Steuerung je Seed voraus, und welches
Maß besser: M0 oder das zentrierte M0c (Theorie erster Ordnung, gemeinsamer Pfad)? *Rechnung* (`lab/confirm/P1_posthoc_m0_strength.py`, nur Splits + P1-Zusammenfassung, keine Läufe):
Kontrast C = log[X_F(F)/X_F(G)] + log[X_G(G)/X_G(F)] je Seed, Spearman gegen Δ_pow (n = 50, add 113). **M0: ρ = 0.39 (Permutations-p 0.006); zentriertes M0c: ρ = 0.26 (p 0.07).**
Holm über die zwei Maße: 0.012 / 0.072. C schwankt kaum (SD 0.07 bzw. 0.11 bei Mittel 1.76), die Streuung von Δ_pow (SD 1.14) kommt also überwiegend von anderswo (Init).
*Einordnung:* post hoc, explorativ; die bestätigten P1-Seeds sind hier kein unabhängiger Test. Hinweis, dass für den **Endzustand** M0 mindestens so gut passt wie das M0c des ersten Gradienten
(im Einklang mit dem früheren, nicht signifikanten Befund zu den finalen Frequenzen, [[BEFUND-split-mechanismus]] Punkt 6): Der erste Gradient erklärt die Richtung, nicht die ganze Stärke.
*Entscheidung:* kein neuer Versuch; im Paper höchstens als Exploration (§4).

### Abschlussbericht Sitzung 25 (2026-09-27, 14:19–15:00 Berlin, gemessen; Run-Fenster die ganze Zeit zu)

**Wichtigste Ergebnisse (alle ohne Training; Rechnungen nur numpy auf gespeicherten Daten):**
1. **Literatur (Regel 19e):** Volltextprüfung der engsten Arbeiten ([[paper/fulltext_check_2026-09-27]]). **K4d eingeschränkt:** Dong 2026 zeigt in Sprachmodellen, dass ein QK-Reset die
   Lernfähigkeit herstellt, Value nicht; „Attention-Reset > MLP-Reset“ ist für Transformer nicht neu, unsere Reihenfolge (Wertepfad > QK) ist umgekehrt. Khanh 2026 (gleicher Modelltyp) ist
   Pflichtzitat für K4. K2 bleibt „nach unserer Suche nicht gefunden“.
2. **Theorie (Paper §5):** ausformuliert; dabei einen eigenen Fehler gefunden (nicht alle Token-Häufigkeiten fallen im ersten Gradienten heraus, nur die eigene einer Zeile) → neue prüfbare
   Vorhersage **EXP-077** (Pilot vorbereitet, Programm C). Nachauswertungen: EXP-047-shuf auch im stetigen Maß ≈ 0; in P1 geht der M0-Kontrast mit der Steuerstärke je Seed einher (ρ 0.39, post hoc).
3. **Werkzeuge (ungetestet bis 00:00):** `confirm_p4.py` (Codex: 1 Blocker behoben), `repro/train.py` + `repro/k2.py` (Claude-Prüfagent: keine Blocker, 4 Punkte behoben), P4-Entwurfsmanifest.
4. **Paper:** Related Work (1b), Theorie (5.1–5.4), Diskussion (5b), Grenzen ergänzt; unabhängige Zahlenprüfung: 12 Überdehnungen korrigiert (u. a. ein nie gerechneter Versuch als Beleg).

**Offene Grenzen:** alles Neue ungetestet; Persistenzbefunde weiter nur add 113; die umgekehrte QK/VO-Reihenfolge gegenüber Dong ist unerklärt (Lesart N36, ungeprüft).
**Meine Fehler:** eine geschätzte Uhrzeit (sofort ersetzt); falsche Theorieaussage zu Häufigkeiten (numerisch gefunden, korrigiert); mehrere Überdehnungen im Paper-Text (durch die Prüfung gefunden).
**Reproduktion:** `python lab/paper/repro/theory_identity_check.py`, `theory_sign_check.py`, `lab/confirm/P1_posthoc_m0_strength.py`, `lab/experiments/EXP-047-marginal-control/posthoc_delta_pow.py`,
`centred_m0c_shared.py` (alle aus dem Repo-Wurzelverzeichnis, reine numpy-Rechnung).
**Nächste Aktion:** ab 00:00 laut [[STATE]] „Nächste Schritte“ 1–7 (Tests → CPU EXP-040 → P2f → GPU EXP-073/074/075 → EXP-077 → P4-Selbsttest, Repro-Gleichwertigkeit).
**Runner:** geplante Aufgabe aktiv; nächster Start laut runner-state.json 2026-09-27 15:54:45Z = **17:54 Berlin**. Freiwillig früher beendet: weitere Arbeit ohne Rechenfenster wäre heute
Beschäftigung ohne Erkenntnis oder weiteres ungetestetes Werkzeug für eine schon volle Nacht.

## Sitzung 26 (2026-09-27, Start 15:09 Berlin, Deadline 18:09; Run-Fenster zu)

Stand gelesen; kein STOP, keine Python-Prozesse, `--check` Exit 3 (außerhalb des Fensters, erwartet). Die vorige Sitzung endete freiwillig um 15:00; der Runner hat sofort diese gestartet.
Deshalb arbeite ich bis zur Deadline weiter (Regel 13).

**Zyklus 1 (Nachtvorbereitung, zwischen 15:10 und 15:17, gemessen).** *Frage:* Laufen die Jobdateien der Nacht technisch an, oder scheitern Zeilen an Tippfehlern? *Prüfung* (statisch, ohne Ausführung): alle 400 Zeilen
von EXP-073/074/075/077 gegen die `add_argument`-Optionen von `freq_ban.py` und die Existenz aller `.npy`-Pfade. *Ergebnis:* keine unbekannte Option, keine fehlende Datei, keine doppelte Zeile;
Eingriffswerte je 20 Zeilen wie registriert (rewind all/attn/rest/vo/we; reset attn/mlp/qk/vo). *Entscheidung:* nichts zu ändern.

**Zyklus 2 (Literatur, Regel 19e, läuft).** *Frage:* Schränkt eine Arbeit seit März 2026 K2 oder K4 ein, die unsere Websuchen nicht gefunden haben? Die dokumentierte Lücke war: keine Vorwärtszitate
(Google Scholar/Semantic Scholar nicht direkt abgefragt). *Neu:* Die Semantic-Scholar-Graph-API ist über WebFetch erreichbar (Probe: 100 Zitate von Nanda et al. 2023, darunter viele Grokking-Arbeiten
aus Juli bis September 2026, z. B. 2609.18078 „Component Roles in Grokking Transfer“, 2606.26050 „Natural Ungrokking“, 2607.12735 „Critical Windows in Grokking“). Ein Claude-Hilfsagent (nur lesend)
geht die Vorwärtszitate von 9 Ausgangsarbeiten durch. Ergebnis folgt.

**Zyklus 3 (Paper, Regel 19a: R2 vorbereitet, zwischen 15:17 und 15:22, gemessen).** *Frage:* Hält K4c (Umstieg bei 25, Festhalten bei 50) auch bei anderen Hyperparametern? Das ist die Robustheitsfrage, die Gutachter
zu K4 zuerst stellen; im [[paper/robustness_plan]] war R2 nur skizziert („nach EXP-040“). *Änderung:* Registrierungsentwurf [[confirm/R2_REGISTRATION_DRAFT|R2]] und `lab/tools/confirm_r2.py`
(N29-Protokoll, Zellen lr 2e-3 mit t ∈ {12, 25, 50} und wd 0.3 mit t ∈ {25, 50}, Holm über 4, n = 30 aus der N29-Streuung: Power 0.88 bei halbiertem Abstand; Seeds 2510–2539 in
[[FINDINGS_DETAILS]] reserviert). *Entscheidung zur Abhängigkeit von EXP-040:* Das Warten auf EXP-040 ist nicht nötig. H2 bei lr 2e-3 liegt mit t = 12 unter beiden Uhren (Schritte, Λ) im
Umstiegsbereich; die Uhrenfrage wird als Sekundärgröße (t = 25) ohne Urteil mitgemessen. Nur `py_compile`, kein Selbsttest (Fenster zu). Codex prüft (läuft).

**Zyklus 2, Ergebnis (vor 15:22, gemessen).** Der Hilfsagent hat die Vorwärtszitate von 9 Ausgangsarbeiten gesichtet (Nanda et al. 2023 ≈ 280 Titel ab März 2026, Marchetti 7, LeDoux 1, Lyle 9, Chughtai ≈ 28,
He a/b 8; Dong und Khanh 0, vermutlich Indexierungsverzug; dann HTTP 429). *Ergebnis:* **nichts, was K2, K2-Funktion, K4–K4c oder K4d/e einschränkt.** Engster neuer Treffer zu K2:
Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316): Kernel (RFM), Symmetriebruch der Trainingsmenge entscheidet, **ob** generalisiert wird, nicht welche Frequenzen. Zu K4d/e: Jia 2026
(2609.18078): gleiche Modellfamilie, Übertragen/Einfrieren von Komponenten; Q, K, V fusioniert, keine Resets, keine Frequenzen. Beides habe ich selbst am Abstract bzw. an den Aufbau-Angaben im
HTML-Volltext nachgesehen; den Rest (Howe 2026a/b, Li & Sreedhar 2026, Swaroop 2026, Hidajat et al. 2026, Sweeney 2026) nur über die Abstract-Angaben des Agenten. *Übernommen:* Nachtrag in
[[paper/related_work]] (mit Prüfgrad, Einschränkung „API nicht abgefragt“ korrigiert), drei Sätze in §1b des [[paper/draft]]. *Offen:* Zitate am PDF prüfen, Dong/Khanh später nachholen,
Google Scholar. Neuheitsstand in [[FINDINGS]] unverändert („nach unserer Suche nicht gefunden“, jetzt mit Vorwärtszitaten bis 2026-09-23).

*Korrektur (15:22, gemessen):* Die Uhrzeiten „15:20“, „15:40“, „15:25–15:50“ in diesem Sitzungsabschnitt, in LIVE, R2-Entwurf, robustness_plan, STATUS und related_work waren **geschätzt**, nicht
gemessen (Verstoß gegen die Laborregel „nur gemessene Zeiten“). Alle durch gemessene Grenzen ersetzt. Ab jetzt vor jedem Eintrag messen.

**Zyklus 4 (Paper, Regel 19c: K4c-Reproduktionsskript, vor 15:22).** `lab/paper/repro/k4c.py`: baut die N29-Splits nach, trainiert mit `repro/train.py`, Ablation und H1/H2 wie N29,
`--compare-n29` gegen die eingefrorene Zusammenfassung. Ungetestet (nur `py_compile`); ein Claude-Prüfagent vergleicht es mit `confirm_n29.py` (läuft). Die Vorsicht aus Sitzung 25 („kein
K4-Skript vor der Gleichwertigkeit“) betraf π mit Spurkontrollen; K4c braucht nur Wechsel + Ablation und hängt allein an der Gleichwertigkeit von `train.py`, die heute Nacht geprüft wird.

**Zyklus 3, Codex (Ergebnis vor 15:25, gemessen).** Codex zu R2: **keine Blocker**; Run-IDs, Konfig-Prüfung, alt/neu, Vorzeichen, Joborder, Holm, Power bestätigt. Übernommen: D25 ist durch die
Lernrate nach dem Wechsel konfundiert (neutrale Etiketten, kein Uhrentest); keine p-Werte in der ergebnisabhängigen Teilmenge; `train_frac` mitprüfen. Vermerkt, nicht geändert: Der
Modul-Selbsttest ist bei `exec_module` nicht vollständig (wie N29; Codex fand von Hand keine Lücke). Code weiter ungetestet.

**Zyklus 4, Prüfung (vor 15:25).** Claude-Prüfagent zu `repro/k4c.py` gegen `confirm_n29.py`: **keine Blocker** (Splits, alt/neu, Schrittzahl inkl. `--stop-after-gen`, Projektion,
Genauigkeit, Modellaufbau, Statistik, Bootstrap-Zufallsstrom identisch). Übernommen: Cache nur bei passender result.json; `--compare-n29` nur voll auf cuda; Threads 4 bei der Auswertung wie N29;
Vergleich über Mittelwerte (Einzelseeds nur berichtet, GPU-Nichtdeterminismus); Zahl generalisierter Seeds. Nicht übernommen: weitere N29-Felder (für die Reproduktion nicht nötig).

**Zyklus 5 (Paper §1 als Fließtext, vor 15:25).** Einleitung ausformuliert (Frage, Hebel gegen LeDoux/Marchetti, Ergebnisse K2–K4e mit Grenzen, Beiträge). Zwei eigene Überdehnungen vor der Prüfung
korrigiert: K2-Funktion gilt nur für die drei zyklischen Aufgaben; der Attention-Reset „kehrt“ die Abhängigkeit um (nicht „entfernt das meiste“). Unabhängige Quellenprüfung folgt.

**Zyklus 5, Prüfung (Ergebnis vor 15:30, gemessen).** Unabhängiger Claude-Prüfagent (nur lesend) zur neuen Einleitung: **keine falsche Zahl, 13 Überdehnungen/Ungenauigkeiten**, alle übernommen.
Zwei davon selbst an den Zusammenfassungen nachgesehen (N29b mean_R: normal 0.86, Attention-Reset −0.63, MLP-Reset 0.79; N29c: VO −0.04, QK 0.72; P3 π 0.351). Wichtigste: „die Wahl fällt früh“ → „beginnt
früh zu haften“ (π steigt glatt, keine Schwelle); „kehrt die Abhängigkeit um, viel stärker als der MLP-Reset“ war schief (der MLP-Reset kehrt nichts um) → Zahlen genannt; „Reset lokalisiert im
Wertepfad“ → nur Vergleich mit gleich großem QK-Reset; K4-Ergebnisse ausdrücklich nur add 113; „Sensitivität folgt Energie“ nur, wo geprüft (explorativ); D59 bei 2000 vor dem Grokking;
Lyle et al. und Marchetti et al. genauer; Howe 2026a und Jia 2026 am Abstract korrigiert; **Zhou, Zhang, Xu 2024 fehlte im Entwurf** (in related_work als nächste Vorarbeit markiert) → ergänzt.
Abstract an zwei Stellen gleich angepasst. *Lehre (dritte Sitzung in Folge):* Meine erste Fassung überdehnt zuverlässig; die unabhängige Prüfung ist nötig, nicht optional.

**Zyklus 6 (Verallgemeinerung, Regel 15c/19b: EXP-078 vorbereitet, vor 15:31, gemessen).** *Frage:* Gilt K2 auch mit zwei Schichten? (FINDINGS Grenze 3: keine tiefere Architektur geprüft; im Paper eine
naheliegende Gutachterfrage.) *Aufbau:* laboreigenes 2-Schicht-Modell (`two_layer.py`, Rezept der Studie), dessen W_E-, Schicht-1- und W_U-Init bei gleichem Seed identisch mit dem 1-Schicht-Modell
ist → gepaarter Vergleich mit den eingefrorenen P1-Werten derselben Seeds und Splits (1000–1009). Trainer = `repro/train.py` mit ausgetauschter Modellfabrik. Primär Δ_pow bei 2000, Lesart vorab
im [[experiments/EXP-078-two-layer-steering/README|README]]. 20 Läufe ≈ 20 min GPU; erst nach der Gleichwertigkeit von `repro/train.py`. Ungetestet (nur `py_compile`), Selbsttest prüft die
Init-Gleichheit. *Warum jetzt:* Die GPU ist heute Nacht nach dem Plan nur ≈ 1.5 h belegt; ein Pilot zur Tiefe kostet wenig und trifft eine offene Grenze direkt.

**Zyklus 6, Prüfung (Ergebnis vor 15:35, gemessen).** Claude-Prüfagent zu EXP-078: keine Blocker; 5 kleinere Punkte übernommen (README Nachtrag a). Dabei eine Schwäche der Lesart gefunden, die
auch EXP-077 hat (beide vor jedem Lauf): „Δ̄ < 0.5 **oder** p ≥ 0.2 → keine Steuerung“ hätte einen großen, streuenden Mittelwert als „keine Steuerung“ gelesen → jetzt nur Δ̄ < 0.5; EXP-077
Nachtrag b. Positiv-Regeln unverändert. *Eigener Fehler:* ein Heredoc ohne Anführungszeichen mit Backticks; die Shell wollte Wörter als Befehle ausführen (alle „command not found“, nichts
geschrieben, nichts ausgeführt). Danach über eine Skriptdatei wiederholt.

**Zyklus 7 (größte offene Frage: Λ- oder Schrittuhr, R3 vorbereitet, vor 15:37, gemessen).** *Frage:* Tickt die Festlegung in aufsummierter Lernrate oder in Schritten? EXP-039 war *unklar*
(4 bekannte Seeds), R2 kann es nicht klären (Codex: Lernrate auch nach dem Wechsel verändert). *Änderung:* [[confirm/R3_REGISTRATION_DRAFT|R3]] + `confirm_r3.py`: N29-Protokoll mit
`--lr-scale c` **nur vor dem Wechsel** (Trainer-Option aus EXP-039, keine Trainer-Änderung): lrs2@25 (Λ = 50) und lrs05@50 (Λ = 25). Die Λ-Uhr sagt Festhalten bzw. Umstieg voraus, die Schrittuhr das
Gegenteil; Holm über 2, n = 20 (Power 0.80 bei halbiertem Umstiegseffekt), Seeds 2540–2559 reserviert, 80 Läufe ≈ 17 min GPU. Codex prüft (läuft). *Warum:* Das ist der direkteste Test des
Amplitudenbilds an frischen Seeds, billig und mit zwei gegensätzlich vorhergesagten Zellen.

**Zyklus 7, Codex (Ergebnis vor 15:41, gemessen).** Codex zu R3: **keine Blocker** (Eingriff genau in den Schritten 1 … t, Run-IDs, Vorzeichen, Joborder, Holm, Power bestätigt). Übernommen: genauere
Formulierung „Nachtraining gleich spezifiziert“; Gegenerklärungen (Bias-Korrektur, schrittabhängige Momente, Überschießen) in der Registrierung, *Λ-Uhr bestätigt* heißt nur „skaliert wie Λ in
zwei Zellen“; die Ausgabe von *nicht bestätigt* sagt ausdrücklich, dass das keine Schrittuhr belegt. Code weiter ungetestet.

**Zyklus 8 (Literatur, Nachprüfung des engsten Treffers, 15:42, gemessen).** Den Volltext von Tomàs Bernal et al. 2026 selbst gelesen (WebFetch). *Ergebnis:* Meine und die Agenten-Einordnung („entscheidet nur,
**ob** generalisiert wird“) war **zu schwach**: Mit absichtlich H-invarianten Splits lernt RFM genau die Untergruppe H, Vorhersage und Ergebnis stimmen zu 100 % überein. Die Trainingsmengen-Struktur wählt
dort also die gelernte Merkmalsstruktur (Kernel, Symmetrie-Untergruppen, keine Fourier-Analyse, keine Netze). *Folge:* K2 **teilweise eingeschränkt** (konzeptioneller Vorläufer); related_work, Paper §1b und
FINDINGS korrigiert. *Lehre:* Auch Einordnungen „schränkt nicht ein“ aus Abstracts sind am Volltext zu prüfen, bevor sie ins Paper gehen.

**Zyklus 8, Fortsetzung (15:44, gemessen).** Zwei weitere Abstract-Einordnungen am Volltext geprüft: Li & Sreedhar 2026 (Regel überlebt oder nicht, keine Wahl zwischen gleich richtigen Lösungen) und Swaroop 2026 (Struktur bei Memorisierung kodiert, keine Schrittangabe, kein Datenwechsel): beide schränken nicht ein, Einordnung bestätigt.

**Zyklus 9 (N36 geschärft, EXP-079 vorbereitet, bis 15:46, gemessen).** *Frage:* Lässt sich der Dong-Gegensatz (QK gegen Wertepfad) in unserem Modell sauber als „Leitung gegen Inhalt“ testen?
*Überlegung:* Bei geteiltem W_E und austauschsymmetrischer Attention kann das Netz nur symmetrische f(a, b) rechnen → a + b → a − b verlangt neue Leitung, a + b → a² + b² nur neuen Inhalt; N36
sagt eine Wechselwirkung der Reset-Wirkung voraus. *Vorbedingung:* Symmetrie der Köpfe nach a + b; Messskript [[experiments/EXP-079-head-symmetry/README|EXP-079]] (nur Vorwärtsrechnung der
80 N29-Modelle, Lesart vorab). *Außerdem:* Howe 2026a am Volltext: gleiche Modellklasse und Einstellung wie wir, Fenster für einen Hilfsverlust, keine Frequenzanalyse → zitieren, schränkt nicht ein.

**Zyklus 10 (N36-Pilot EXP-080 vorbereitet, bis 15:50, gemessen).** Aufgabenwechsel auf denselben Paaren (a + b → a − b bzw. a² + b²) mit QK-, VO- oder keinem Reset, t ∈ {50, 1000}, Seeds 800–809,
120 Läufe; primär die Wechselwirkung I der Reset-Nutzen (Lerngeschwindigkeit nach dem Wechsel) bei t = 50, Lesart vorab im README. Startet nur, wenn EXP-079 symmetrische Köpfe zeigt. Eigener
schlanker Trainer (Reihenfolge wie `repro/train.py`), ungetestet; ein Prüfagent prüft Design und Code (läuft). *Eigene Nachrechnung vorab:* Das Symmetrieargument gilt nicht streng: Über W_pos
entsteht bei austauschsymmetrischer Attention ein antisymmetrischer Anteil (α_a − α_b) · OV(W_pos[0] − W_pos[1]); er hängt aber an den Attention-Gewichten, also an QK. Die Aussage ist deshalb:
Antisymmetrie kann nur über das Attention-Muster entstehen, nicht „das Netz kann nur symmetrische Funktionen“. Korrektur nach der Prüfung.

**Zyklus 10, Prüfung (Ergebnis vor 15:54, gemessen): EXP-080 zurückgestellt.** Prüfagent: Das Symmetrieargument trägt nicht (drei Blocker, alle selbst nachvollzogen): (1) Bei austauschsymmetrischer Attention
ist die Ausgabedifferenz unter Vertauschung Σ_h (α_a − α_b) · W_O W_V (W_pos[0] − W_pos[1]) → a − b ist über eine OV-Positionsmarke ohne QK-Änderung erreichbar; der Aufgabengegensatz trennt QK und VO
nicht. (2) Bei t = 50 ist die Attention noch zufällig positionsasymmetrisch. (3) Ein QK-Reset bringt diese Init-Asymmetrie zurück und hilft a − b trivial. *Entscheidung:* EXP-080 wird nicht gerechnet
(Status zurückgestellt), EXP-079 misst stattdessen die Kanäle (QK-Versatz, OV-Marke, Logit-Antisymmetrie) als Material für ein neues Design; N36 korrigiert. *Lehre:* Ein eigenes Gegenargument hatte ich
schon notiert, aber als „trägt qualitativ“ abgetan; die Prüfung vor dem Lauf hat eine Nacht-Queue mit einem nicht deutbaren Versuch verhindert.

**Zwischenbilanz nach Auftrag §4 (15:54, gemessen, nach 10 Zyklen dieser Sitzung).** *Gelernt:* (1) Literatur: Die Neuheit von K2 ist enger als notiert (Tomàs Bernal et al.: Trainingsmengen-Symmetrie wählt
die gelernte Gruppenstruktur in Kerneln); K4 und K4d/e bleiben nach Vorwärtszitaten und vier Volltexten nicht gefunden. (2) Ein geplanter Versuch (EXP-080) war nicht deutbar; das hat die Prüfung vor
dem Lauf gezeigt. *Wiederholen wir uns?* Nein, aber die Zahl vorbereiteter, ungetesteter Blöcke für eine Nacht ist jetzt hoch (P2f, EXP-073/074/075/077/078/079, R1, R2, R3, P4, Repro). Das Risiko
liegt bei den Nachtsitzungen (Einfrieren, Smokes). Deshalb **keine weiteren Versuche für diese Nacht**; die Reihenfolge in [[STATE]] ist verbindlich priorisiert. *Messungen geeignet?* Für die Uhrfrage
ja (R3 mit gegensätzlichen Vorhersagen); für N36 noch nicht (Kanäle erst messen). *Nächste anzugreifende Annahme:* dass die Festlegung eine einzige Uhr hat (R3 kann „keine der beiden“ ergeben;
dann N37). *Folge für den Rest der Sitzung:* nur noch Paper-Arbeit und Literatur, keine neuen Registrierungen.

**Prüfung (15:55, gemessen):** Die Lesart-Schwäche aus EXP-077/078 („p ≥ 0.2 allein → keine Wirkung“) steckt nicht in den anderen Auswertungen der Nacht (EXP-040/073/074/075, P2f, P4, R1–R3; grep nach den Mustern, EXP-074 liest über Mediane der Effektgrößen). Nichts geändert.

### Abschlussbericht Sitzung 26 (2026-09-27, 15:09–15:57 Berlin, gemessen; Run-Fenster die ganze Zeit zu, kein Training, kein Test)

**Wichtigste Ergebnisse:**
1. **Literatur (Regel 19e):** Vorwärtszitate von 9 Ausgangsarbeiten über die Semantic-Scholar-API (≈ 330 Titel ab März 2026) und 5 Volltexte. **K2 ist teilweise eingeschränkt:** Tomàs Bernal
   et al. 2026 zeigen für Feature-Learning-Kernel, dass eine symmetrische Trainingsmenge die gelernte Gruppenstruktur wählt (zuerst zu schwach eingeordnet, am Volltext korrigiert). K2 bleibt
   in der engeren Form (vorgegebene Fourier-Frequenzen in Transformern über das Maskenspektrum) nach unserer Suche nicht gefunden; K4–K4e weiter nicht gefunden.
2. **Registriert (Entwürfe, ungetestet, Codex ohne Blocker):** R2 (K4c bei lr 2e-3 / wd 0.3, n = 30), **R3 (Λ- gegen Schrittuhr, Lernrate nur vor dem Wechsel skaliert, n = 20)**; Seeds 2510–2559 reserviert.
3. **Piloten vorbereitet:** EXP-078 (K2 mit zwei Schichten, gepaart mit P1), EXP-079 (Positionskanäle, Sekunden). **EXP-080 vor jedem Lauf zurückgestellt** (Designfehler, von der Prüfung gefunden).
4. **Paper:** Einleitung als Fließtext (13 Korrekturen nach unabhängiger Prüfung), §3.7 ausstehende Blöcke, Registrierungstabelle aus den Manifesten, `repro/k4c.py` (geprüft).
5. **Vor dem Lauf korrigiert:** Lesart von EXP-077/078 (hoher Mittelwert mit Streuung hieß „keine Wirkung“). Neu: N37 (Fenster = β₂-Horizont von 50 Schritten?).

**Offene Grenzen:** Alles Neue ist ungetestet; die Nacht ist voll (Reihenfolge in [[STATE]] verbindlich, R1 vor R3 vor P4 vor R2); N36 braucht ein neues Design nach EXP-079.
**Meine Fehler:** geschätzte statt gemessene Uhrzeiten (korrigiert, Memory ergänzt); ein ungeschützter Heredoc mit Backticks (nichts ausgeführt); zwei Überdehnungen in eigenem Text vor der Prüfung
(Einleitung, Tomàs-Bernal-Einordnung).
**Reproduktion:** `python lab/paper/figures/table_registrations.py` (reine Dateilesung); alle anderen neuen Skripte erst ab 00:00 (Befehle in den READMEs und in [[STATE]]).
**Nächste Aktion:** ab 00:00 laut [[STATE]] „Nächste Schritte“ 1–8.
**Runner:** geplante Aufgabe aktiv; next_start_utc laut runner-state.json 2026-09-27T16:44:45Z = **18:44 Berlin** (der Runner startet erfahrungsgemäß schon kurz nach Sitzungsende neu).
Früher beendet als die Deadline 18:09, weil weitere Arbeit ohne Rechenfenster jetzt nur neue ungetestete Blöcke für eine volle Nacht oder Beschäftigung wäre (Zwischenbilanz oben).

## Sitzung 27 (2026-09-27, Start 15:59 Berlin, vom Runner; Deadline 18:59; Run-Fenster zu)

**Zyklus 1 (Nachtbefehle statisch prüfen, ab 16:00, gemessen).** *Frage:* Passen die Befehle in [[STATE]] Schritte 1–8 zu den Optionen der (ungetesteten) Skripte? Ein Prüfagent liest nur Code (keine Ausführung); Ergebnis folgt.

**Zyklus 2 (Paper §2 als Fließtext, 16:00–16:04, gemessen).** Methodenteil ausformuliert (Modell, Aufgaben, Splitkonstruktion, Wechselprotokoll, Maße, Protokoll) aus Code und Registrierungen; Init-Streuungen
und Reset-Semantik selbst am Code geprüft (Reset = Init-Werte zurück + AdamW-Zustand gelöscht; Bootstrap = Perzentil). Unabhängige Quellprüfung läuft (Regel aus dem Memory: jede neue Paper-Sektion).

**Zyklus 3 (N38: Größe von K4b aus der Adam-Arithmetik, 16:04–vor 16:07, gemessen).** *Frage:* Sagt der Momentum-Schwanz von Adam ohne freien Parameter voraus, um wie viele Schritte das Löschen von m die π-Kurve
verschiebt? *Rechnung* (`EXP-059/inflight_adam.py`, numpy, kein Training): 6.5–10.8 Update-Äquivalente bei t = 25–35 (≈ 8.7 bei gleich großen Gradienten danach). *Vergleich:* EXP-059 `delta_shift` 8.1 / 9.6 / 6.5
bei t = 25 / 30 / 35; die Werte bei 40/50 (3.8/2.4) sind Interpolationsartefakte (Kurve 35 → 50 nicht gemessen, sättigt). *Urteil:* passt, post hoc, bekannte Seeds, Skalarmodell. *Literatur:* Xu 2026 (arXiv 2608.20442)
zeigt das erste Moment als verzögerten Träger nach dem Entfernen von Daten → qualitative K4b-Lesart **bekannt**, nur die Größenvorhersage nicht gefunden. Eingetragen: [[NOVEL_DIRECTIONS]] N38 (mit β₁-Dosis-Test als Skizze, erst nach R3),
[[paper/related_work]] Nachtrag, Paper §3.3 (ein Satz, als post hoc gekennzeichnet). *Entscheidung:* kein neuer Versuch jetzt; die Nacht ist voll.

**Zyklus 3, Korrektur (vor 16:15, gemessen).** Meine eigene Einordnung der Werte bei t = 40/50 als „Interpolationsartefakt einer sättigenden Kurve“ war falsch: π_normal steigt 30 → 35 und 35 → 50 mit gleicher Steigung (0.034 / 0.033 je Schritt).
Die Verschiebung durch das Löschen von m ist bei t = 40/50 mit 3.8/2.4 Schritten deutlich kleiner als der Momentum-Schwanz (≈ 9). N38 stimmt also nur bei t = 25–35; danach hängt die Festlegung weniger an der nachlaufenden alten Verschiebung.
Das ist ein Hinweis für die offene Frage in [[FINDINGS]] (die Uhr ist nicht einfach „aufsummierte Verschiebung“), aber aus einem Piloten an 10 bekannten Seeds. N38, Paper §3.3 korrigiert. *Lehre:* eine bequeme Artefakt-Erklärung erst an den Daten prüfen.

**Zyklus 2, Prüfung (Ergebnis vor 16:09, gemessen).** Unabhängige Quellprüfung von §2 (nur Lesen): Architektur, Init, Verlust, Optimierer, Splitkonstruktion (auch D₅₉-Indexreihenfolge), Wechselprotokoll, Reset, Bootstrap, Bindung **korrekt**.
Neun Korrekturen übernommen (alle an den genannten Stellen selbst stichprobenartig geprüft: mul-Zeilen W_E[g^i] in EXP-043 `analyze.py`, 4-dim. Irrep-Spann in `dihedral.py`): Zeilen für mul; D₅₉-Unterraum 4-dim.; „keine gemeinsamen Paare“ nur bei ω = 0
(P3 lief zusätzlich ω = 0.4, ε ≈ 5.93); Token-Häufigkeiten richtig nach §5 (CV 0.14, Spektrum zielangereichert) statt „nahezu gleichverteilt“; GPU-Gleichwertigkeit statistisch, nur add 113; Einfrieren über SHA-256-Hashes im Manifest; Wrapper prüft auch während des Laufs;
Smoke-Historie (P1 zwei Jobs, N28–N29c, P2d, P2e; P2c und P3 ohne); 2000 Schritte bei K2; „keine Biases“ als Eigenschaft unserer Implementierung (ob Nanda et al. Biases hatten, nicht geprüft). *Verworfen:* nichts.

**Zyklus 3, zweite Korrektur (16:09–16:10, gemessen).** Die erste Korrektur hat überzogen: π = 1 ist der reine Endpunkt des ersten Splits und damit eine natürliche Obergrenze; zwischen 35 und 50 ist π_normal nicht gemessen. Gepaart (EXP-059, 10 Seeds, Bootstrap):
Abfall durch m-Löschen 0.186 / 0.186 / 0.197 bei t = 25 / 30 / 35 (Verschiebung mit lokaler 5-Schritt-Steigung ≈ 8.4 / 11.1 / 5.7, verrauscht), 0.077 [0.031, 0.118] bei t = 50. Ob der kleine Wert bei 50 der Momentum-Rechnung widerspricht,
hängt an der unbekannten lokalen Steigung → **unentscheidbar**. N38 und Paper §3.3 entsprechend (Paper nennt nur t = 25–35 und sagt, warum 40/50 nicht vergleichbar sind). Offener, billiger Zusatz für einen späteren Piloten: π_normal bei t = 40/45.

**Zyklus 1, Ergebnis (bis 16:13, gemessen): statische Prüfung der Nachtbefehle.** Ein Prüfagent hat STATE-Schritte 1–8 und die verlinkten READMEs/Registrierungen gegen den Code gelesen. **Regelverstoß des Agenten, offen vermerkt:** Er hat einmal
`python -c "1"` ausgeführt (außerhalb des Fensters, trotz Verbot in der Anweisung; ein No-op, keine Datei berührt, kein Training/Test). Alles andere nur gelesen.
*Sicher (selbst am Code bestätigt, behoben):* (1) [[paper/repro/README]]: relativer venv-Interpreterpfad → CreateProcess-Fehler (bekannt aus Sitzung 20) → absoluter Pfad. (2) `--jobs > …` über guarded_run schriebe `[guard]`-Zeilen in die Jobdatei
(guarded_run.py:197/228) → STATE: `--jobs` ohne Wächter wie bei P2e, voller Pfad `lab/confirm/…`.
*Verdacht, übernommen:* (3) R1 hatte keine Seed-Obergrenze und kein Manifest-Entwurf → `SEED_MAX = 2509` in `confirm_r1.check_design`, `R1_manifest_DRAFT.json` (15 Seeds je Zelle in CELLS-Reihenfolge, ε aus der Kalibrierung). (4) Thread-Summe:
3 × 4 CPU-Threads plus bis zu 10 GPU-Prozesse widerspricht Regel 17 (≤ 12) → STATE: CPU 2 Arbeiter + höchstens 4 GPU-Prozesse, mehr nur nach Messung. (5) R2/R3 ließen eine alte Zusammenfassung stehen → löschen wie P2f.
*Nur Hinweis:* (6) R2/R3-Selbsttests ohne Ende-zu-Ende-Messung an einem Zufallsmodell (Smoke fängt es). *Geprüft ok:* Trainer-Test-Fixtures und Run-IDs, night_program-Schlüssel EXP-040/042/014, P2f-Modi und Flags, Seed-Blöcke disjunkt,
Manifest-Entwürfe R2/R3/P4 passend zu REGISTERED, Jobdateien EXP-073–078 (180 .npy-Pfade vorhanden, nur `--device cuda`), Analyse-Muster, EXP-078-Modell, Repro-Referenzen.
Code-Änderungen (confirm_r1/r2/r3) sind klein und **ungetestet**; die Selbsttests heute Nacht decken sie ab, die Blöcke sind noch nicht eingefroren (Hashes entstehen erst beim Einfrieren).

**Zyklus 4 (Messkern R2/R3 gegen N29c, bis 16:15, gemessen).** *Frage:* Braucht es vor dem Einfrieren einen Ende-zu-Ende-Selbsttest der Messung (Hinweis 6)? *Vorgehen:* `one_run` von R2/R3 mit dem gelaufenen N29c verglichen (diff) und die neuen Teile am Code geprüft:
Die Lader-Erwartung `config` (arch, lr, weight_decay, train_frac) liegt so in `result.json` (Stichprobe N29c-Lauf; Overrides fließen über `get_config(**hp)` in `cfg.to_dict()`), `lr_scale`/`lr_scale_until`/`switch_step` stehen im Ergebnis. *Ergebnis:* Messkern gleich N29c bis auf einen Rückschritt:
R2/R3 fingen nur `ValueError` beim Laden ab, Auswertungsfehler hätten die ganze Analyse abgebrochen; N29c macht daraus „defekt“. Übernommen (beide Dateien, ungetestet, Selbsttest heute Nacht). *Entscheidung:* kein zusätzlicher Selbsttest; der Pflicht-Smoke deckt den Rest.

**Zyklus 5 (Literatur: [A]/[S]-Einträge am Volltext, bis 16:19, gemessen).** *Frage:* Schränkt eine nur am Abstract/Snippet eingeordnete Arbeit K2/K4 ein (Lehre aus Tomàs Bernal)? *Ergebnis:* Salah & Yevick 2024 (selbst, PDF): gezielt eingeschränkte Trainingsmengen ändern **ob** ein MLP groks,
nicht welche Frequenzen → schränkt K2 nicht ein, im Paper §1b zitiert. Sweeney 2026, Pracher et al. 2026, Yang 2026 (Agent, Kernzitate selbst im Rohtext bestätigt; ein vom Agenten genanntes Zitat „an early gradient persists in the buffer“ habe ich nicht wiedergefunden und nicht übernommen):
nichts schränkt K2/K4 ein; **Sweeney beschreibt den Mechanismus hinter K4b** (erstes Moment mit festem Takt) → N38 nur noch als Größenvorhersage offen, Paper §3.3 zitiert Sweeney und (ungelesen, gekennzeichnet) Sevetlidis & Pavlidis 2026. Offen: letztere am Volltext.

**Zyklus 6 (EXP-081 entworfen, bis 16:22, gemessen).** *Frage:* Wie trennt man die drei Kandidaten für die „Uhr“ der Festlegung (Verschiebung inkl. Momentum-Schwanz, β₂-Horizont N37, reine Schrittzahl), die R3 allein nicht trennt?
*Vorgehen:* numpy-Vorhersagen (`EXP-059/clock_predictions.py`): Die Verschiebungsuhr verschiebt t₅₀ nur mit β₁ (0.8 → ≈ +5, 0.95 → ≈ −6), der β₂-Horizont nur mit β₂ (0.95 → ≈ 13, 0.995 → ≈ 130), die Schrittuhr gar nicht.
*Ergebnis:* Entwurf [[experiments/EXP-081-optimizer-clock/README|EXP-081]] (5 β-Zellen × 7 Wechselzeitpunkte × 2 Richtungen × 10 frische Pilot-Seeds 830–839, Lesart vorab). **Kein Code, kein Lauf**: Trainer-Optionen erst nach dem Einfrieren
der Nachtblöcke (Hashes) und mit Codex; Start frühestens nach R3. *Warum jetzt:* zielt direkt auf die größte offene Frage in FINDINGS und entscheidet zwischen benannten Konkurrenzmodellen (Regel 18c).

**Zyklus 6, Prüfung (bis 16:25, gemessen): EXP-081 umgebaut, bevor Code existiert.** Prüfagent (nur Lesen): zwei Blocker, beide selbst nachvollzogen und übernommen: (1) β₁-Arm über t₅₀ zu schwach (Verschiebung < Gitterabstand, Lesart meist *unklar*);
(2) N37 hat keinen Mechanismus (v̂ ist bias-korrigiert ab Schritt 1 unverzerrt; mein eigenes Skript zeigte das, ich hatte es übersehen). Dazu S1 selbst nachgerechnet: auch die Verschiebungsuhr sagt für β₂ = 0.95 einen etwas größeren Schwanz voraus (10.8–12.4 statt 8.9),
aber nur ≈ 2–3 Schritte. *Neues Design:* Teil A misst den Momentum-Schwanz direkt (normal gegen m-Löschen bei t = 25 für β₁ ∈ {0.8, 0.9, 0.95}; Vorhersage 4 / 9 / 16–24 Schritte), Teil B prüft N37 bei festem t = 33 mit großen vorhergesagten Abständen (N37: π nahe 1 bzw. 0; Verschiebungsuhr: ±0.1).
≈ 500 statt 800 Läufe. Verworfen: nichts; S2 (β nur vor/nach dem Wechsel) als späterer Schritt notiert. *Lehre:* Eine Vorhersage, deren Mechanismus im eigenen Rechenmodell nicht vorkommt, ist keine Vorhersage.

**Zyklus 7 (Reproduktionspaket, Regel 19c, bis 16:31, gemessen).** *Frage:* Welche bestätigten Kernaussagen haben noch kein schlankes Repro-Skript? *Ergebnis:* neu `repro/k4_resets.py` (K4d/K4e, N29b/N29c) und `repro/k4b.py` (K4/K4b, N28), dazu in `repro/train.py`
`--reset-optim-part m` (Standardpfad unverändert). Zwei unabhängige Code-Prüfungen (nur Lesen) gegen die eingefrorenen Auswertungen: Konstruktion, Arme, Reset-Semantik, Leistungsdefinition, π/R, Hypothesen und Statistik stimmen überein; übernommen:
kein stiller No-op-Reset in `train.py`, strengere Vergleichsschwellen (alle Seeds, auch Kontraste), Bootstrap-Seeds wie im Original, Cache-Fehler für die normal-Arme in `k4b.py` (nur Rechenzeit), NaN-Prüfung wie N28. Alles **ungetestet**;
laufen erst nach bestandener Gleichwertigkeit von `train.py` (frühestens Nacht 28./29.). Offen im Paket: K2-Funktion (P2d/P2e).

**Zyklus 8 (Repro K2-Funktion, bis 16:35, gemessen).** `repro/k2_function.py` (P2d, add 113) nutzt die eingefrorene P2d-Messung direkt (nur gelesen importiert). Unabhängige Prüfung (nur Lesen): Splits, Training, Maß und Statistik identisch zu P2d, kein sicherer Fehler.
Übernommen: Konstanten gegen `confirm_p2d.REGISTERED` geprüft, Splits bitgenau gegen die eingefrorenen P2d-Dateien, größte Abweichung je Seed im Vergleich; in allen drei neuen Repro-Skripten Trainer-Hash und Threads im Ausgabepfad
(sonst würden nach einer Trainer-Änderung alte Modelle still wiederverwendet). `k4c.py` unverändert (läuft heute Nacht im Smoke). Damit fehlen im Paket nur noch P2e (mul 113, add 97) und P3 (statische Spur); alles ungetestet.

**Zyklus 9 (Stichprobe EXP-081 Teil A, bis 16:36, gemessen).** Aus EXP-059: Abfall durch m-Löschen bei t = 25 = 0.186 (SD 0.098), vorhergesagt aus Schwanz × Steigung 0.17–0.21 (passt). Simulierte Power für den β₁-Dosistest (0.95 gegen 0.8, Vorzeichentest, 10 Seeds): 0.93–1.00.
Eingetragen in [[experiments/EXP-081-optimizer-clock/README|EXP-081]]. Teil B (β₂ bei festem t) braucht keine Power-Rechnung: die vorhergesagten Abstände (≈ ±0.5) sind ein Vielfaches der Streuung.

**Zyklus 10 (Quellprüfung der übrigen neuen Paper-Stellen, bis 16:39, gemessen).** Unabhängiger Agent (nur Lesen, Salah & Yevick selbst im PDF nachgelesen): §1b, §3.3-Zahlen (inflight_adam-Logik, delta_shift 8.056/9.580/6.467), Zitate Xu/Sweeney/Sevetlidis, §6 und die Repro-Tabelle **korrekt**.
Korrigiert: „Registered R3“ → Entwurf, nicht eingefroren; t = 40/50 „nicht interpretierbar“ statt „nicht möglich“ (die interpolierten Werte existieren); Bereich t = 25–35 und 8.7–8.9 ergänzt; Grammatik; Repro-Zeile „K4 (π-Arme)“ (Kernzahlen von K4 aus P3 nicht abgedeckt); Salah & Yevick präziser.

**Zyklus 11 (Repro P2e, bis 16:42, gemessen).** `repro/k2_function_p2e.py` (mul 113, add 97) mit eingefrorener P2e-Messung und -Auswertung. Prüfung (nur Lesen): Splits bitgenau prüfbar (160 eingefrorene Dateien vorhanden), `train.py` trainiert mul/add 97 wie `freq_ban.py`, Modell lädt,
Auswertung identisch; kein sicherer Fehler. Übernommen: Vergleich nur mit dem vollen registrierten Seed-Satz (auch in `k2_function.py`). Offen notiert: Die Vergleichsschwellen setzen fast bitgenaue Nachrechnung voraus; sonst vor den vollen Vergleichen aus dem Standardfehler begründen.
**Stand Repro-Paket:** Skripte für K2 (drei zyklische Aufgaben), K2-Funktion (alle drei), K4c, K4/K4b, K4d/e; fehlt nur D₅₉ (anderer Trainer) und die P3-Spurzerlegung. Alles ungetestet bis zur Gleichwertigkeit von `train.py` (heute Nacht, Schritt 7).

**Zyklus 12 (Literatur: neueste arXiv-Einreichungen, bis 16:44, gemessen).** arXiv-API (erster Versuch über HTTP leer, zweiter über HTTPS ok): 40 neueste Treffer zu „grokking“; sieben neue, einschlägige Titel an den Abstracts eingeordnet. Nichts schränkt K2/K4 ein.
Kontext notiert: 2609.10657 (Skalierung der Grokking-Zeit mit η und λ → R1), 2608.07436 (Zusammenbruch nach dem Grokking bei add 113, auch unter AdamW → unsere Endmodelle sind 2000–4000 Schritte nach dem Wechsel gemessen; spätere Stabilität ungeprüft, als Grenze fürs Paper).

### Abschlussbericht Sitzung 27 (2026-09-27, 15:59–16:44 Berlin, gemessen; Run-Fenster die ganze Zeit zu, kein Training, kein Test)

**Wichtigste Ergebnisse:**
1. **Nacht abgesichert:** Statische Prüfung aller Nachtbefehle; zwei sichere Befehlsfehler behoben (`--jobs` über den Wächter hätte `[guard]`-Zeilen in Jobdateien geschrieben; relativer venv-Pfad in den Repro-Gleichwertigkeitsbefehlen), dazu R1-Seed-Obergrenze + Manifest-Entwurf, R2/R3 robuster, Thread-Budget nach Regel 17 (CPU 2 Arbeiter + höchstens 4 GPU-Prozesse).
2. **N38 (post hoc):** Adams Momentum-Schwanz (≈ 9 Update-Äquivalente) erklärt die Größe von K4b bei t = 25–35 ohne freien Parameter; bei 40/50 unentscheidbar. Qualitativ **bekannt** (Xu 2026, Sweeney 2026, Sevetlidis & Pavlidis 2026), nur die Größenabschätzung nicht gefunden. Zwei eigene Fehldeutungen dabei korrigiert.
3. **EXP-081 entworfen** (Uhr der Festlegung: β₁-Dosis über den Momentum-Schwanz, β₂ bei festem t): Prüfung fand zwei Blocker (β₁-Arm zu schwach; N37 ohne Mechanismus), Design ersetzt, Power ≈ 0.93–1.0. Kein Code, erst nach R3.
4. **Paper:** §2 Methoden als Fließtext (geprüft, 9 Korrekturen), Reproduktionsabschnitt, Grenzen (Optimierer, Langzeitstabilität), Literatur (6 Arbeiten am Volltext/Abstract, arXiv-Durchsicht bis 24.09.): K2/K4 weiter nicht gefunden.
5. **Repro-Paket fast vollständig:** `k2_function.py`, `k2_function_p2e.py`, `k4b.py`, `k4_resets.py` (+ `train.py --reset-optim-part m`), jeweils unabhängig gegen die eingefrorenen Auswertungen gelesen; fehlt D₅₉ und die P3-Zerlegung.

**Offene Grenzen:** Alles Neue ist ungetestet. Die Repro-Vergleichsschwellen setzen fast bitgenaue Nachrechnung voraus (vor den Vollläufen klären). Ein Prüfagent hat einmal `python -c "1"` ausgeführt (No-op, vermerkt).
**Meine Fehler:** geschätzte Uhrzeiten (korrigiert), zwei überzogene Deutungen zu N38 (korrigiert), N37-Mechanismus nicht gegen das eigene Skript geprüft (von der Prüfung gefunden).
**Reproduktion (ohne Fenster möglich):** `python lab/experiments/EXP-059-momentum-exposure/inflight_adam.py`, `python lab/experiments/EXP-059-momentum-exposure/clock_predictions.py` (numpy).
**Nächste Aktion:** ab 00:00 [[STATE]] „Nächste Schritte“ 1–8 (Befehle korrigiert).
**Runner:** aktiv; next_start_utc laut runner-state.json 2026-09-27T17:34:45Z = **19:34 Berlin**. Früher beendet als die Deadline 18:59, weil weitere Arbeit ohne Rechenfenster jetzt vor allem zusätzlichen ungetesteten Code für ohnehin volle Nächte bedeuten würde.


## Sitzung 28 (2026-09-27, Start 16:49 Berlin, vom Runner; Run-Fenster zu bis 00:00)

Stand gelesen (STATE, JOURNAL-Ende, paper/STATUS). Kein STOP, keine Python-Prozesse, `--check` Exit 3 (außerhalb des Fensters). Nur Auswertung gespeicherter Läufe (numpy, wie EXP-059 in Sitzung 27), kein Training, kein Test.

**Zyklus 1 (K2 in absoluten Zahlen, bis 16:51, gemessen).** Frage: Δ_pow ist ein relatives Log-Verhältnis; wie stark ist die Steuerung absolut? `lab/confirm/P1_posthoc_share.py` liest alle 400 P1-Läufe über den eingefrorenen P1-Lader (`power_at`, Bindung geprüft, 0 defekt).
Ergebnis (beschreibend, post hoc): Anteil der W_E-Gruppenenergie auf den 5 eigenen Zielen bei Schritt 2000: add 113 **0.80** (Seed-Bootstrap-KI [0.79, 0.82], Spanne 0.52–0.92; bei der Init 0.089 = Zufall 5/56), mul 113 0.79, add 97 0.69, D₅₉ 0.44 (Zufall 0.17). Auf den Zielen des anderen Arms 0.02–0.04 (D₅₉ 0.12).
Im Mittel 3.9 von 5 Zielen unter den stärksten fünf (add 113: 17/100 Arme alle fünf, keiner unter drei; D₅₉ 4.8). → Paper §3.1 ergänzt (die Einschränkung „relativ, nicht gegen die Init“ ist damit beantwortet).

**Zyklus 2 (Welches Ziel bleibt zurück? Programm C, bis 16:53, gemessen).** Vorab im Skriptkopf festgelegt: zwei konkurrierende Prädiktoren für die Rangfolge der 5 Ziele innerhalb eines Arms: Masken-Spektrum (M0; add 113 auch zentriertes M0c, Theorie §5) gegen Init-Energie (Lotterie).
`lab/confirm/P1_posthoc_within.py`, Mittel der Spearman-Korrelation je Arm, Permutation innerhalb der Arme: add 113 M0c **0.44**, M0 0.32, Init 0.13; mul 113 M0 0.21 (Init 0.08, n. s.); add 97 M0 0.29 (Init 0.11); D₅₉ M0 0.43 (Init 0.15). M0/M0c jeweils p < 5·10⁻⁵.
Kontrollen (add 113): keine Abhängigkeit vom Frequenzindex k (ρ(gelernt, k) 0.008, ρ(M0c, k) 0.003); vertauschte Arme ρ −0.08. Die Spreizung von M0c innerhalb eines Arms ist klein (max/min ≈ 1.3), die Rangfolge folgt also der zufälligen Schwankung des Splitspektrums.
**Urteil:** Exploration (Seeds gesehen), aber klar. Die Theorie erster Ordnung sagt nicht nur die Menge, sondern auch die Feinordnung voraus. **Entscheidung:** als Vorhersage an unberührten Fällen registrieren (Regel 18c, Programm C).

**Zyklus 3 (Registrierung C1, bis 16:53, gemessen).** [[confirm/C1_REGISTRATION|C1]]: an den 180 R1-Läufen (frische Seeds 2420–2509, noch kein Lauf), primärer Prädiktor M0c, Einheit Seed (Mittel F/G), einseitiger Vorzeichentest,
bestätigt bei p < 0.05 und KI-Untergrenze ≥ 0.10; Power aus P1-Streuung (SD 0.305) bei halbiertem Effekt ≈ 0.99. Commit d330f1c (vor jedem R1-Lauf). `C1_analyze.py` geschrieben, **ungetestet** (Selbsttest reproduziert die P1-Exploration 0.438; nur im Fenster).
Geprüft: `spectra.npy` von freq_ban ist bis 1e-16 gleich `group_power` der W_E-Snapshots (R1-Lader liefert also dasselbe Maß wie die Exploration). Codex-Prüfung läuft (Regel 18c: vor Einfrieren eines Programms).

**Zyklus 4 (Programm B: Welche alten Ziele überdauern einen Wechsel? bis 17:00, gemessen).** Vorab festgelegt: Prädiktoren Energie beim Wechsel (Geschichte), M0c des ersten Splits, M0c des zweiten Splits an den alten Zielen (Stütze durch die neuen Daten). `lab/confirm/N29_posthoc_within.py`, N29 (20 Seeds × 2 Richtungen).
**Eigener Fehler, vor der Deutung gefunden:** der erste Lauf las die B→A-Läufe mit vertauschten Rollen (alt/neu); korrigiert.
Ergebnis (korrigiert): t = 50, alte Ziele: Energie beim Wechsel **0.58** (p < 5·10⁻⁵), M0c erster Split 0.37, M0c zweiter Split **0.02** (n. s.). t = 25: 0.17 (p 0.03) / 0.08 / 0.03. Neue Ziele: t = 25 Energie beim Wechsel 0.29, M0c zweiter Split 0.18 (p 0.02); t = 50 nichts signifikant (0.08 / 0.12).
**Deutung (vorsichtig):** Nach einem Wechsel bei 50 Schritten bleibt auch die innere Ordnung der alten Frequenzen erhalten; die neuen Daten ordnen sie nicht um. Bei 25 Schritten ist die Ordnung weitgehend weg. Passt zu K4/K4c, feinere Auflösung; beschreibend, kein Mechanismus. Läufe desselben Seeds teilen die Init (Einheit Seed in der Registrierung).
**Entscheidung:** als [[confirm/C2_REGISTRATION|C2]] an R2 registrieren (frische Seeds 2510–2539, t = 50 in beiden R2-Zellen, Einheit Seed, gleiche Schwellen; Power ≈ 0.92 bei halbiertem Mittel). `C2_analyze.py` geschrieben, ungetestet (Selbsttest reproduziert N29 0.580).

**Zyklus 5 (Codex-Prüfung C1, Regel 18c „vor Einfrieren eines Programms“, bis 17:04, gemessen).** Codex (Volltext `lab/confirm/C1_codex_review_s28.txt`): 2 Blocker, 6 größere, 2 kleinere Punkte. Selbst geprüft:
- B1 (Aussage behauptet Robustheit je Hyperparameter, Test prüft nur das gepoolte Mittel): **stimmt** → Aussage eng: gleich gewichtetes Zellmittel, Zellen nur beschreibend.
- B2 (ρ allein trennt M0c nicht von k/Init): **teilweise** – k und Init hatte ich gemessen (≈ 0 bzw. schwach), aber nicht registriert → bereinigter Koeffizient (Energie ~ M0c + k + Init, zentrierte Ränge je Arm) als dritte Bedingung; keine Mechanismus-Aussage, M0c gegen M0 nur beschreibend.
- M1 (Konstruktion könnte M0c mit k/Position koppeln): Konstruktion geprüft (gleiche Amplitude je Ziel, unabhängige Phasen, getrennter Schlüsselstrom) und **vor jedem Lauf** an den 180 deterministisch nachgebauten R1-Splits gemessen: ρ(M0c, k) = 0.05 (SD 0.53), keine Bindungen (`C1_predictor_diag.json`). Bereinigter P1-Koeffizient 0.433 (unbereinigt 0.438).
- M2 (Vorzeichentest setzt Symmetrie voraus; p ohne +1): Annahme genannt, p = (Überschreitungen+1)/(B+1). Studentisierten Test **nicht** übernommen (Bedingung ii verlangt ohnehin das Bootstrap-KI).
- M3 (bis 30 Seeds dürfen fehlen, keine Zellminima): Zellmindestzahl 10/15, gleich gewichtete Zellmittel, geschichtetes Bootstrap, Schranke „fehlende = −1“ beschreibend.
- M4 (kein Code-Tor, Überschreiben): `C1_manifest.json`/`C2_manifest.json` mit Hashes, Auswertung verweigert bei Abweichung; Zusammenfassung wird nie überschrieben.
- M5 (Offenlegung unvollständig): **stimmt** – die gegenläufige Sitzung-25-Analyse (über Seeds M0 0.39 > M0c 0.26) und EXP-015/050 ergänzt.
- M6 (Selbsttest zirkulär): neu `rank_tools.py` mit Handwerten, synthetische Zellen (bestätigt / nicht bestätigt, wenn die Ordnung k folgt / nicht auswertbar / Fehlschranke), M0c gegen Brute-Force-DFT.
- Kleinere: Bindungen → Arm technisch; Schritt 0 mit vollen Erwartungen und gezählten Ausfällen. Codex bestätigt: kein Variablenfehler (`run`), F/G-Mittel korrekt, KI-Schwelle wie registriert.
Gleiche Korrekturen in C2 (bereinigter Koeffizient: Endenergie ~ Energie beim Wechsel + k + Spektrum zweiter Split; N29: 0.589). Beide als **Fassung 2** committet (d50e7b0), vor jedem R1/R2-Lauf; Code **ungetestet** (Selbsttests nur im Fenster). Codex-Nachprüfung nur der betroffenen Punkte läuft.
**Eigener Fehler:** `sed -i` auf STATE.md hat die CRLF-Enden entfernt (gegen meine eigene Notiz); vor dem Commit bytegenau auf HEAD wiederhergestellt, Diff geprüft.

**Zyklus 6 (Codex-Nachprüfung C1/C2 und Literatur N39, bis 17:14, gemessen).** Nachprüfung (`lab/confirm/C1_codex_recheck_s28.txt`): 4 Punkte gelöst, 4 offen, 1 neuer Blocker + 3 größere.
Übernommen: **Blocker C2** (Seed zählte schon mit einem gültigen Lauf → C2 hätte aus einer Zelle/Richtung bestätigen können; stimmt) → Seed nur mit allen vier t = 50-Läufen; C1: Schritt-0-Ausfall → Arm technisch (vorher stiller Ausschluss aus der Bereinigung; stimmt);
C2: Bindungen in den Kontrollen → Lauf technisch (vorher möglicher Abbruch; stimmt); Code-Tor an Git gebunden (letzter Commit von Tor + Registrierung muss Vorfahr des R1/R2-Manifest-Commits sein); C1-Deutung enger (nicht spezifisch für M0c gegenüber M0).
Verworfen mit Begründung: bestätigender M0c-gegen-M0-Vergleich (keine solche Aussage mehr), Ersatz der Vorzeichenpermutation (exakt unter genannter Symmetrie, wie P1/R1; Bootstrap-Untergrenze zusätzlich), End-zu-End-Test mit nachgebildeten R1-Läufen (R1-Smoke prüft die Ladekette; Ladefehler zählen als technisch). Fassung 2b committet (f445f94), weiterhin **ungetestet**.
Literatur (WebSearch, 2026-09-27, Begriffe in [[NOVEL_DIRECTIONS]] N39): nichts gefunden, das die Feinordnung durch das Paarspektrum zeigt; Abgrenzung zu He et al. 2026a (Init entscheidet bei vollen Daten) in [[paper/related_work]] ergänzt. N39 als #neu/kandidat (vorläufig).

**Zyklus 7 (Architekturkontrast der Feinordnung, MLP, bis 17:15, gemessen).** Frage: Die Theorie erster Ordnung (Vorhersage 2) sagt für das MLP mit geteiltem Embedding M0 statt M0c. Gilt das auch für die Rangfolge der Ziele? Vorab im Skriptkopf: im MLP ρ(M0) > ρ(M0c).
`lab/confirm/EXP045_posthoc_within.py`, Pilot EXP-045 (Seeds 90–99, 20 Arme). Ergebnis Schritt 2000: M0c **0.60**, M0 0.46 (beide p < 5·10⁻⁵); Differenz M0 − M0c −0.14, nur 3/10 Seeds positiv, einseitig p 0.92. Schritt 10 000: beide verblasst (M0 0.20, M0c 0.17, n. s.).
**Urteil:** Vorhersage **widerlegt** (Pilot, n = 10). Passt zum schon notierten Befund, dass M0c auch bei den Endfrequenzen des MLP beschreibend besser ist. Vorhersage 2 gilt für den ersten Gradienten, nicht für die spätere Ordnung. **Folge:** C1 ist kein spezifischer Beleg für die Herleitung über den gemeinsamen Pfad; genau so ist C1 seit Fassung 2b formuliert. Paper §5.3 ergänzt. Offene Nebenfrage: Verblasst die Ordnung auch im Transformer nach dem Grokking? (P1 hat nur Schritt 2000; nicht nachgehen ohne Bezug zu einer offenen Frage.)

**Zyklus 8 (Verallgemeinerung der Feinordnung, Programm A, bis 17:18, gemessen).** Frage: Gilt N39 auch bei 4× Breite und bei nicht-modularer Addition? Vorab festgelegt im Skriptkopf (`lab/confirm/A_posthoc_within.py`): Masken-Spektrum gegen Init, Schritt 2000, Piloten EXP-049 (d512, d128) und EXP-048 (je 10 Seeds, 20 Arme).
Ergebnis: d512 M0c 0.30 (p 0.009), M0 0.31, Init −0.01; d128 M0c 0.31 (p 0.005), Init 0.16 (n. s.); Integer-Addition eigenes M0 0.29 trendbereinigt (p 0.01) / 0.36 roh (p 0.001), Init 0.11–0.12 (n. s.). **Urteil:** Die Feinordnung durch das Paarspektrum zeigt sich in allen geprüften Bedingungen (Piloten, gesehene Seeds); die Init spielt jeweils kaum eine Rolle.
**Entscheidung:** als [[confirm/C3_REGISTRATION|C3]] an P4 registriert (frische Seeds, noch nicht eingefroren, kein Lauf), Statistik wie C1 Fassung 2b (gleiche Aggregation), Schritt 2000 in allen Bedingungen (beim MLP bewusst nicht der P4-Primärzeitpunkt 10 000, weil die Ordnung dort verblasst: offengelegt). Commit b199107, `C3_analyze.py` ungetestet; Codex-Prüfung läuft.
**Rückblick nach drei Zyklen (Auftrag §4):** Gelernt: Die Feinordnung ist robust über Aufgaben und Architekturen (Exploration) und erhält sich nach der Festlegung (C2); die architekturspezifische Herleitung (Vorhersage 2) trägt sie aber nicht (Zyklus 7). Wir wiederholen uns nicht: jede Registrierung zielt auf einen noch nicht gelaufenen Block, kein neuer Trainingsaufwand. Nächste gezielt anzugreifende Annahme: dass die Ordnung ein Merkmal vor dem Grokking ist (MLP: bei 10 000 verblasst); Prüfung an den gespeicherten Transformer-Läufen nach dem Grokking nur, wenn es eine offene Frage in FINDINGS beantwortet.

**Zyklus 9 (Codex zu C3, bis 17:23, gemessen).** `lab/confirm/C3_codex_review_s28.txt`: kein Blocker; MAJOR: bei der Integer-Addition ist die Zielgröße trendbereinigt, die Init-Kontrolle aber das rohe Spektrum bei Schritt 0 (stimmt; der Trainer speichert W_E bei Schritt 0 nicht). Übernommen als ausdrücklich andere Kontrolle mit eingeengter Deutung (keine Trainer-Änderung vor dem Einfrieren von P4). MINOR (Selbsttest prüfte nur den rohen Pilotwert): trendbereinigter Pilotwert 0.285 ergänzt. Codex bestätigt Schritt 0/2000 in allen drei Trainern und die k-Indizierung. Commit a299bbb.

**Zyklus 10 (Ist die Feinordnung nur ein Merkmal vor dem Grokking? bis 17:25, gemessen).** Angegriffene Annahme aus dem Rückblick (Zyklus 8). `lab/confirm/P2de_posthoc_time.py` auf den gespeicherten P2d/P2e-Läufen (je 20 Seeds × 2 Arme; Generalisierung im Median bei Schritt 725 für add/mul 113, 1225 für add 97).
Mittlere Rangkorrelation (Masken-Spektrum, Zielenergie) über die Zeit: add 113 M0c 0.54 (Schritt 250) → 0.45 (1000) → 0.37 (2000) → 0.42 (4000); M0 0.41 → 0.32; add 97 M0 0.36 (250) → 0.31 (2000) → 0.24 (8000); mul 113 M0 0.22 (500) → 0.17 (2000) → 0.13 (8000); Schritt 0 jeweils ≈ −0.05 bis −0.16.
**Nebenbefund:** P1 bei Schritt 2000 liegt für add/mul 113 schon **nach** dem Grokking (P2d: Median 725). Die Formulierung „K2 bei Schritt 2000 = vor dem Grokking“ gilt nur für D₅₉ (so steht es im Paper; geprüft, keine Korrektur nötig).
**Eigener Fehler, vor der Deutung gefunden:** Der erste Lauf las bei mul 113 `spectra.npy`, das dort die einfache DFT über den Tokenindex ist, nicht die Gruppenbasis (ρ ≈ 0, verworfen). Neu mit `group_power` der W_E-Snapshots. Geprüft: alle anderen Auswertungen dieser Sitzung nutzen für mul die Gruppenbasis (P1 `power_at`) oder betreffen add/Integer; C1/C3 lesen nur add-113- bzw. Integer-Spektren.
**Urteil:** Annahme widerlegt für den Transformer: Die Feinordnung überdauert das Grokking und nimmt nur langsam ab. Im MLP-Piloten verblasst sie bis 10 000 Schritte stärker (0.60 → 0.17). Exploration. Paper §4 ergänzt.

**Zyklus 11 (Folgeprüfung des mul-Basisfehlers, bis 17:26, gemessen).** Nach meinem eigenen Fehler in Zyklus 10 alle Stellen gesucht, die `spectra.npy` bei mul lesen. `freq_ban.freq_power` nutzt die additive Basis über den Tokenindex (geprüft: bei mul weicht sie von `group_power` um bis zu 87 % des Maximums ab).
Registrierte Auswertungen korrekt (P1 `power_at`, EXP-043 `analyze`, `pilot_power` nur für D₅₉/add 113). **Echter Fehler gefunden in `lab/paper/repro/k2.py` (Sitzung 25, ungetestet):** `--task mul` hätte Δ_pow in der falschen Basis gerechnet und den P1-Vergleich verfehlt. Behoben (mul: `--save-model`, `group_power` auf dem End-W_E wie P1); README vermerkt. Weiter ungetestet.

**Zyklus 12 (Feinordnung bei D₅₉ nach dem Grokking, bis 17:27, gemessen).** `lab/confirm/EXP072_posthoc_time.py`, Pilot EXP-072 (Seeds 1000–1004 × 2 Arme, 20 000 Schritte; Grokking im Median ≈ 4600): mittlere Rangkorrelation (D₅₉-Maskenspektrum, Irrep-Energie der Ziele) 0.13 (Schritt 0), 0.56 (250), 0.57 (2000), 0.55 (4000), 0.58 (10 000), 0.48 (20 000); positiv in 8–10 von 10 Armen.
**Urteil:** Auch in der nicht-abelschen Gruppe überdauert die Feinordnung das Grokking (Pilot, n = 5 Seeds). Zusammen mit Zyklus 10: Im Transformer ist die Ordnung kein Übergangsmerkmal der Frühphase; nur im MLP-Piloten verblasst sie.

**Zyklus 13 (Programm B: Wächst die Rangerhaltung der alten Ziele mit t wie π? bis 17:30, gemessen).** Frage zur größten offenen Frage (was legt fest?). Vorab im Skriptkopf: Rangerhaltung (C2-Maß) je t neben π aus EXP-059. `lab/confirm/EXP059_posthoc_order_clock.py` (Seeds 400–409 × 2 Richtungen, Budget 2000).
Ergebnis: t = 10/15/20/25: 0.23/0.29/0.23/0.19 (π 0.01/0.07/0.19/0.30); t = 30/35/50: 0.41/0.42/0.58 (π 0.39/0.56/1.05). SD je Lauf ≈ 0.45, n = 20 → SE ≈ 0.1.
**Selbst angegriffen:** Ist das nur allgemeine Erhaltung von W_E-Struktur? Kontrolle `lab/confirm/order_control.py` (gleiches Maß über zufällige Nicht-Ziel-5er-Mengen): EXP-059 0.09–0.17, N29 0.06 (t = 25) / −0.04 (t = 50). Überschuss der alten Ziele: ≈ 0.1 bei t ≤ 25, 0.26–0.43 bei t ≥ 30.
**Deutung (Exploration, vorsichtig):** Die Ordnung der alten Ziele ist früh leicht über der Grundrate und steigt zwischen t = 25 und 30 deutlich, parallel zu π; keine klare Trennung „Ordnung vor Menge“. Nebenbefund: Das Nullsetzen des ersten Moments (rom) senkt π, aber nicht die Rangerhaltung (t = 25: 0.34 gegen 0.19; Unterschied innerhalb der Streuung).
**Folge für C2:** Die Schwelle 0.10 allein könnte eine Grundrate bestätigen → **Fassung 3** mit Bedingung (iv) „Überschuss über die Nicht-Ziel-Kontrolle, KI-Untergrenze > 0“, vor jedem R2-Lauf (3bed847). Codex-Nachprüfung der Änderung läuft.

**Zyklus 14 (Codex zu C2 Fassung 3, bis 17:34, gemessen).** Kein Blocker; MAJOR (nur Bindungen → NaN-Kontrolle, Lauf zählte trotzdem) stimmt → unter 150 von 200 bindungsfreien Ziehungen ist der Lauf technisch. MINOR alle übernommen: eigener Zufallsstrom je Richtung (AB/BA hatten denselben, weil die Buchstabensumme gleich ist), trennscharfer Selbsttest, veraltete Textstellen. Weiter ungetestet.

**Zyklus 15 (Übernimmt M0c im MLP erst später? bis 17:35, gemessen).** Hypothese vorab im Skriptkopf (`lab/confirm/EXP045_posthoc_crossover.py`): Im MLP gilt „M0“ (getrennte Pfade) nur ganz früh, danach übernimmt M0c, sobald das Netz beide Operanden verknüpft; Vorhersage ρ(M0) > ρ(M0c) bei Schritt 250, M0c > M0 ab 1000.
Ergebnis MLP (20 Arme): Schritt 250 M0 0.62 / M0c 0.67 (M0 vorn in 11/20); 1000 0.48 / 0.64 (8/20); 2000 0.46 / 0.60; 10 000 0.20 / 0.17. Transformer (P2d, 40 Arme) zum Vergleich: M0c vorn ab Schritt 250 (0.41 / 0.54).
**Urteil:** unklar. Der erste Teil (frühe M0-Führung) zeigt sich nicht; bei Schritt 250 praktisch gleichauf, was mit der Hypothese nur vereinbar ist, wenn die Übernahme vor Schritt 250 beginnt. Der zweite Teil (M0c vorn ab 1000) passt. Entscheidbar nur mit Spektren in den ersten ~50 Schritten (gespeicherte Läufe loggen erst ab 250). **Entscheidung:** nicht weiter verfolgen, bis ein Lauf mit dichten frühen Spektren ohnehin ansteht; als Notiz zu N39.

**Zyklus 16 (Eingriff statt Korrelation: EXP-082 vorbereitet, bis 17:39, gemessen).** C1–C3 sind Korrelationen (Regel 18c: Korrelationen nicht als direkte Wirkung). Neuer Pilot [[experiments/EXP-082-graded-targets/README|EXP-082]]: Jedes Ziel bekommt in der Split-Konstruktion eine eigene, zufällig zugeordnete Amplitude (strong 0.4–1.6, weak 0.9–1.1); Frage, ob die gelernte Rangfolge folgt.
Numpy-Prüfung des Hebels vor jedem Lauf: strong ordnet das realisierte M0c fast perfekt (ρ 0.995, max/min 3.8), weak mit ρ 0.66 bei max/min 1.47 (natürlich 1.30); Zielanteil wie P1. Splits (80 Dateien, Seeds 600–609, vorher unbenutzt) geschrieben, Jobliste (40 GPU-Läufe) und `analyze.py` fertig, ungetestet. Eigener Fehler vor dem Commit gefunden: `analyze.py` hätte sich wegen des gleichen Dateinamens selbst statt EXP-043 importiert → Laden über den Pfad.
In STATE als optionaler Schritt 10 (nach allen Paper-Blöcken).

**Zyklus 17 (Unabhängige Prüfung der neuen Paper-Stellen, bis 17:42, gemessen).** Prüfagent (nur Lesen) gegen alle JSON-Ausgaben und Skripte: alle Zahlen korrekt. Korrigiert: (1) „p < 5·10⁻⁵“ → „p ≤ 1/20 000 (keine Permutation erreichte den Wert)“ (ohne +1-Korrektur gespeichert; dieselbe Formulierung steht oben im JOURNAL und in C1/C2 unter „gesehene Daten“: dort gilt entsprechend ≤ 1/20 000); (2) „sagt voraus, welches Ziel zurückbleibt“ war überzogen (schwächstes = kleinstes Maskenspektrum nur in 0.26–0.42 der Arme, Zufall 0.20) → „folgt teilweise“; (3) k-Kontrolle hatte keine gespeicherte Quelle → `lab/confirm/P1_posthoc_kcontrol.py/.json` (0.008 / −0.078); (4) max/min 1.3 war aus den R1-Splits → jetzt beide Quellen genannt (P1 1.303, R1 1.298); (5) mul beginnt bei Schritt 500 und ist nicht monoton; (6) D₅₉-Grokking-Zeit aus der EXP-072-Notiz (Median 4575, Test ≥ 0.9) belegt; mein Skript las einen nicht existierenden Schlüssel `events` (jetzt `generalization_step`, dort Median 4950 mit strengerer Schwelle). Klein: Die absoluten Anteile „lösen“ die Grenze in §3.1 nicht, sondern sind eine beschreibende Ergänzung (umformuliert).

**Zyklus 18 (neue Richtung N40: Split-Erkennung aus den Gewichten, bis 17:44, gemessen).** Frage (Regel 9): Trägt ein gegroktes Embedding eine erkennbare Spur seines konkreten Splits? `lab/confirm/P1_posthoc_split_id.py`: echter Split gegen 9 gleich gebaute Attrappen. Zielrangfolge: Top-1 0.20 (Zufall 0.10), paarweise 0.74; Nicht-Ziel-Frequenzen (zweites Maß, nach dem ersten Ergebnis festgelegt): 0.22 / 0.63.
**Urteil:** schwache, echte Spur; gehört zur bekannten Idee der Datensatz-Inferenz, spezifisch nichts gefunden (Suche in [[NOVEL_DIRECTIONS]] N40). **Entscheidung:** verworfen als eigene Linie (kein Bezug zu einer offenen Frage in FINDINGS), dokumentiert.

**Zyklus 19 (Programm B: Trägt das Momentum die Menge oder die Ordnung? bis 17:46, gemessen).** Hypothese vorab im Skriptkopf (`lab/confirm/EXP059_posthoc_rom_order.py`): Das Nullsetzen des ersten Moments beim Wechsel (rom) senkt den Anteil der alten Ziele, nicht aber ihre Rangerhaltung. Gepaart je Seed/Richtung (EXP-058/059, Seeds 400–409, je 20 Paare).
Ergebnis (normal − rom): Anteil der alten Ziele am Ende t = 25/30/35/50: **+0.153 / +0.173 / +0.228 / +0.045** (p ≤ 1e-5 / ≤ 1e-5 / ≤ 1e-5 / 0.019); Rangerhaltung −0.145 (p 0.02) / +0.09 (0.20) / +0.025 (0.72) / +0.015 (0.83). Vier Zeitpunkte, unkorrigiert.
**Urteil (Exploration):** Trennung wie vorhergesagt: Das Momentum trägt die Menge (Amplitude der alten Richtungen), nicht ihre innere Ordnung; bei t = 25 hält rom die Ordnung sogar etwas besser (einzelner, unkorrigierter Befund). **Deutung:** passt zu N38 (Momentum-Schwanz ≈ proportionale Fortsetzung jeder alten Richtung): Wegnehmen skaliert die Amplituden, die Ränge bleiben; die Ordnung steckt schon in W_E beim Wechsel. Kein neuer Block nötig; Hinweis für EXP-081 (die Uhr betrifft die Menge, nicht die Ordnung).

**Zyklus 20 (C4: D₅₉-Feinordnung nach dem Grokking an P2f, bis 17:48, gemessen).** P2f (frische Seeds 2340–2359, 12 000 Schritte) wird erst heute Nacht eingefroren und speichert Irrep-Spektren alle 250 Schritte. Registriert [[confirm/C4_REGISTRATION|C4]]: Rangfolge der Ziel-Irreps bei Schritt 12 000 folgt dem D₅₉-Masken-Spektrum; Statistik wie C1 (eine Zelle). Gesehen: P1 D₅₉ 0.43 (Schritt 2000), Pilot EXP-072 ≈ 0.5 bis 20 000. `C4_analyze.py` ungetestet, Selbsttest vor dem Einfrieren von P2f (STATE Schritt 9). Commit 90384f5; Codex-Prüfung läuft. Damit liegen Vorhersagen an vier noch nicht gelaufenen Blöcken vor (C1 R1, C2 R2, C3 P4, C4 P2f), ohne zusätzliches Training.

**Zyklus 21 (Codex zu C4, bis 17:55, gemessen).** `lab/confirm/C4_codex_review_s28.txt`: kein Blocker; MAJOR „nach dem Grokking der meisten Läufe“ war ungeprüft (stimmt) → Aussage auf Schritt 12 000 beschränkt, Zahl der generalisierten Arme beschreibend, „nach dem Grokking“ im Paper nur bei Mehrheit. MINOR: Selbsttest umgeht Lader/Bindung → als Grenze dokumentiert (P2f-Smoke prüft die Kette). Commit c8801d3.

### Abschlussbericht Sitzung 28 (2026-09-27, 16:49–17:56 Berlin, gemessen; Run-Fenster die ganze Zeit zu, kein Training, kein Test)

**Wichtigste Ergebnisse (alle Exploration an gespeicherten Läufen, gesehene Seeds):**
1. **K2 absolut:** Bei add 113 liegen nach 2000 Schritten im Mittel 80 % der W_E-Energie auf den fünf Zielen (Init 8.9 % = Zufall); mul 79 %, add 97 69 %, D₅₉ 44 % (Zufall 17 %). Paper §3.1 ergänzt (beschreibend).
2. **Feinordnung (N39):** Das realisierte Paarspektrum ordnet auch die Ziele *innerhalb* der Menge (ρ 0.21–0.44 über vier Aufgaben; Init 0.08–0.15; bereinigt um k und Init unverändert), ebenso bei 4× Breite, Integer-Addition und im MLP. Im Transformer überdauert die Ordnung das Grokking (auch D₅₉ bis 20 000 Schritte), im MLP verblasst sie. Die architekturspezifische Herleitung (MLP folgt M0) trägt sie **nicht** (widerlegt, Pilot).
3. **Persistenz fein (Programm B):** Nach einem Wechsel bei t = 50 behalten die alten Ziele ihre Rangfolge (0.58 gegen Nicht-Ziel-Kontrolle −0.04); bei t ≤ 25 nur knapp über der Grundrate. Das Adam-Momentum trägt die **Menge** der alten Frequenzen (Reset: Anteil −0.15 bis −0.23), nicht ihre Ordnung.
4. **Vier Vorhersagen an unberührten Blöcken registriert, ohne zusätzliches Training:** [[confirm/C1_REGISTRATION|C1]] (R1), [[confirm/C2_REGISTRATION|C2]] (R2, mit Nicht-Ziel-Kontrolle), [[confirm/C3_REGISTRATION|C3]] (P4), [[confirm/C4_REGISTRATION|C4]] (P2f); jeweils Code-Tor an die Git-Geschichte gebunden, Codex-geprüft (C1: 2 Blocker, C2-Nachprüfung: 1 Blocker, alle behoben). Pilot [[experiments/EXP-082-graded-targets/README|EXP-082]] (Eingriff: vorgegebene Zielstärken) vorbereitet.
5. **Echter Fehler gefunden:** `repro/k2.py --task mul` hätte in der falschen Fourier-Basis gemessen (behoben; Merkregel im Gedächtnis).

**Negativ/unklar:** MLP-Architekturkontrast der Feinordnung widerlegt; frühe M0-Führung im MLP unentscheidbar (Spektren erst ab Schritt 250); N40 (Split aus den Gewichten ablesbar) nur schwach, verworfen.
**Offene Grenzen:** Alles Neue ist Exploration oder ungetesteter Code; C1–C4 werden erst mit ihren Blöcken entschieden. `C1–C4_REGISTRATION.md` und `C1–C4_manifest.json` bis zur Auswertung nicht anfassen (Tor verweigert sonst).
**Meine Fehler (alle vor Deutung/Commit gefunden):** `sed -i` auf STATE.md (CRLF, bytegenau wiederhergestellt); B→A-Rollen vertauscht (N29, korrigiert); mul über `spectra.npy` gelesen (korrigiert); Selbstimport in EXP-082 `analyze.py` (korrigiert); sechs Formulierungs-/Quellfehler im Paper (unabhängiger Prüfer, korrigiert).
**Reproduktion (ohne Fenster, nur numpy auf gespeicherten Läufen):** `python lab/confirm/P1_posthoc_share.py`, `P1_posthoc_within.py`, `P1_posthoc_kcontrol.py`, `N29_posthoc_within.py`, `order_control.py`, `EXP059_posthoc_order_clock.py`, `EXP059_posthoc_rom_order.py`, `P2de_posthoc_time.py`, `EXP072_posthoc_time.py`, `A_posthoc_within.py`, `EXP045_posthoc_within.py`, `EXP045_posthoc_crossover.py`, `P1_posthoc_split_id.py` (alle unter `lab/confirm/`).
**Nächste Aktion:** ab 00:00 [[STATE]] „Nächste Schritte“ 1–10.
**Runner:** aktiv; next_start_utc laut runner-state.json 2026-09-27T18:24:45Z = **20:24 Berlin**. Früher beendet als die Deadline (19:49): weitere Arbeit ohne Rechenfenster wären jetzt weitere Mini-Explorationen zum selben Thema (Regel 15b) oder zusätzlicher ungetesteter Code für eine ohnehin volle Nacht.

## Sitzung 29 (2026-09-27, Start 17:59 Berlin, vom Runner; Run-Fenster zu bis 00:00)

**Zyklus 1 (Literatur: Init-Skala und Festlegungszeit, vor 18:10, gemessen).** Frage: Gibt es Arbeiten, die prüfen, ob die Init-Skala ein Festlegungsfenster gegen einen Datenwechsel verschiebt (EXP-040 hatte die gezielte Suche als offen vermerkt)? Fünf Suchbegriffe (in [[paper/related_work]], Nachtrag Sitzung 29), arXiv-Liste der neuesten Grokking-Arbeiten (nichts nach 2609.26679 Relevantes). Neu: Khanh et al. 2026 (2606.13753), Grokking-Verzögerung ∝ exp(7.5 ρ) bei geklemmter Gewichtsnorm → stützt den schon registrierten Ausfallgrund von EXP-040 bei s = 2; Das et al. 2026 (2605.29152), Adam löscht das Init-Gedächtnis weitgehend. **Ergebnis:** nichts Einschränkendes, EXP-040 bleibt „nach unserer Suche nicht gefunden“. Semantic-Scholar-API: 429 (Rate-Limit), nicht umgangen.

**Zyklus 2 (Vorprüfung H40 bei s = 1, vor 18:10, gemessen).** Frage: Hält die quantitative Fassung von H40 (EXP-040 Nachtrag c: Zielverschiebung R ≈ 0.5–2 Init-Amplituden beim Festlegen) schon an gesehenen Daten, bevor EXP-040 heute Nacht 3 h CPU belegt? Erwartung im Skriptkopf vorab. `lab/confirm/EXP039_posthoc_R.py` (EXP-039, 7 vollständige Zellen): R(hi) 0.37–1.02 (Median 0.62, 6/7 in [0.5, 2]), R(lo) 0.17–0.55; je Seed gemeinsame Schwelle über beide c möglich; R ∝ Λ^0.91–1.01. **Urteil (Exploration):** H40 quantitativ nicht widerlegt; die Wahl fällt bei etwa 1/3–2/3 der Init-Amplitude. **Methodischer Fund:** Bei s = 1 sind R und Λ fast proportional, darum trägt der Invarianzvergleich aus Nachtrag b nur über die s-Zellen von EXP-040; Lesehinweis 11–12 in [[LESART-nacht-2026-09-28]] (vor jedem Lauf, keine Regeländerung). **Entscheidung:** EXP-040 wie geplant als erstes CPU-Programm; Commit c25ee51.

**Zyklus 3 (Literatur: erste direkte Google-Scholar-Abfrage, vor 18:10, gemessen).** Frage: Findet Google Scholar (bisher nie direkt abgefragt, Lücke seit Sitzung 24) Arbeiten, die K2, K2-Funktion oder K4–K4e einschränken? Vier Abfragen (Wortlaut in [[paper/related_work]]). **Ergebnis:** K2/K4 weiter nicht gefunden. Einschlägig nur Stevinson & Prieto 2026 (ICML-Workshop): Angriffe konzentrieren sich auf die genutzten Fourier-Merkmale → Kontext für K2-Funktion, das bei uns ohnehin nur als „folgt der Energie“ steht; nur Snippet (OpenReview verlangt Anmeldung), für die menschliche Prüfung vorgemerkt ([[paper/STATUS]]). Semantic-Scholar-Suche war rate-limitiert (429).

**Zyklus 4 (neue Richtung N41, vor 18:10, gemessen).** Frage: Kann ein Eingriff trennen, gegen welche Init-Amplitude die Festlegung „läuft“ (Hintergrund aller Nicht-Ziele oder die späteren Konkurrenten)? Entwurf in [[NOVEL_DIRECTIONS]] N41: nur den Init-Hintergrund skalieren (F/G-Ziele unverändert); G-Ziele allein zu skalieren wäre konfundiert. Suche ohne Treffer (vorläufig). **Entscheidung:** nichts bauen, bis EXP-040 heute Nacht entschieden ist; nur bei *H40-Muster gestützt* weiterverfolgen.

**Korrektur (18:12, gemessen): zwei eigene Fehler.** (1) Die Uhrzeiten der Zyklen 1–4 (18:08/18:20/18:40/18:52) und in LESART, related_work, EXP-040, N41, STATE waren **geschätzt, nicht gemessen** (Verstoß gegen die Messregel); die Messung um 18:10 zeigte, dass alle vier Zyklen zwischen 17:59 und 18:10 lagen. Überall auf „vor 18:10, gemessen“ korrigiert. (2) Mein Anhänge-Hilfsskript führte bei jedem Import seine eigenen Anhänge erneut aus: 6 Kopien des Init-Skala-Abschnitts in [[paper/related_work]] und in der EXP-040-README (teils in c25ee51 und den Folgecommits). Beide Dateien aus dem Stand 1d43b0a neu aufgebaut, je ein Abschnitt; Inhalt unverändert. Commit 'fix(lab): correct unmeasured timestamps' davor enthielt nur die Kopien und den STATE-Eintrag, nicht die Korrektur.

### Abschlussbericht Sitzung 29 (2026-09-27, 17:59–18:12 Berlin, gemessen; Run-Fenster die ganze Zeit zu, kein Training, kein Test)

**Ergebnisse:** (1) Literatur zur Init-Skala und zur Festlegungszeit sowie erste direkte Google-Scholar-Abfrage: K2/K4 weiter „nach unserer Suche nicht gefunden“; neu zur menschlichen Prüfung Stevinson & Prieto 2026 (Kontext K2-Funktion). (2) Vorprüfung von H40 an gesehenen EXP-039-Läufen (Exploration): Die Wahl fällt, wenn die Zielverschiebung ≈ 1/3–2/3 der Median-Init-Amplitude erreicht; R wächst linear in Λ. Lesehinweis: Der Invarianzvergleich von EXP-040 trägt nur über die s-Zellen. (3) Kandidat N41 (nur Init-Hintergrund skalieren), bewusst nicht gebaut.
**Eigene Fehler:** ungemessene Uhrzeiten (korrigiert) und sechsfach angehängte Abschnitte durch ein Hilfsskript mit Seiteneffekten beim Import (bereinigt, Merkregel im Gedächtnis).
**Reproduktion:** `python lab/confirm/EXP039_posthoc_R.py` (nur numpy auf gespeicherten Läufen).
**Nächste Aktion:** ab 00:00 [[STATE]] Schritte 1–10 (unverändert).
**Runner:** aktiv; next_start_utc 2026-09-27T19:34:45Z = **21:34 Berlin**. **Früh beendet**, wie Sitzung 28: Der Nachtplan ist voll und vorbereitet; ohne Rechenfenster blieben nur weitere Mini-Explorationen am selben Thema (Regel 15b) oder ungetesteter Code für Versuche, deren Voraussetzung (EXP-040) erst heute Nacht entschieden wird.

## Sitzung 30 (2026-09-27, Start 18:19 Berlin, vom Runner; Run-Fenster zu bis 00:00)

**Zyklus 1 (Gutachter-Durchgang durch den Paper-Entwurf, bis 18:28, gemessen).** Frage: Welche Einwände würde ein Gutachter gegen [[paper/draft]] zuerst erheben, und welche davon lassen sich ohne Rechenfenster beheben? Unabhängiger Prüfagent (Skeptiker-Rolle, nur Lesen), danach jeder Punkt selbst an den Dateien geprüft. **Übernommen und behoben (nur Text, alle Zahlen an den eingefrorenen Zusammenfassungen geprüft):** (1) Abstract: „engineered“ Splits, D₅₉ „vor dem Grokking“, eine Optimierer-Einstellung, Energie-Vorbehalt beim Ablationskontrast. (2) §3.4/§3.5: Werte nur über generalisierte Seeds stehen schon in den eingefrorenen Analysen (`descriptive_generalised_only`) und ändern nichts (N29 0.898/0.591; N29b 1.52/1.45; N29c 0.805/0.738), jetzt berichtet. (3) §3.5: Armmittel ergänzt (N29b 0.86/−0.63/0.79; N29c 0.81/−0.04/0.72): Die Zahlen der Einleitung (0.86 → −0.63, 0.79, „etwa null“) waren richtig, standen aber nicht in §3; Hinweis, dass N29/N29b/N29c verschiedene Seeds haben. (4) §3.3: 0.351 (P3) und 0.340 (N28) sind dasselbe π in zwei Blöcken, jetzt so benannt. (5) §3.6/§4: D₅₉-Pilot vereinheitlicht (Median 4575, 5 Seeds × 2 Arme). (6) §1b: LeDoux' Zufalls-Teilmengen-Befund ausdrücklich eingeordnet (zufällig + Minibatch-Reihenfolge vs. konstruiert + Full-Batch) und offen gesagt, dass wir nicht zeigen, ob gewöhnliche Zufallssplits die Wahl entscheiden. (7) §6: Gewichtsspanne 0.05–3 (an `confirm_splits.py` geprüft: 1 + 2·wave, geklemmt bei 0.05), Schritt-Zeitskala nur bei lr 1e-3. (8) Beitrag (ii) nicht mehr „validation“, sondern „check, der der Energie folgt“. (9) Zitat 2608.07436 mit Autoren (Janati et al. 2026, per arXiv-Abstract geprüft). (10) Verifikationsabschnitt: deckt nur den Stand von Sitzung 24. **Nicht übernommen / offen:** Strukturumbau (Gliederungen löschen, Lab-IDs in Anhang) erst, wenn die Nachtergebnisse feststehen, sonst doppelte Arbeit; „random splits entscheiden?“ bleibt Pilot (EXP-014 heute Nacht). **Ergebnis:** 10 Textkorrekturen, keine Zahl geändert, kein neuer Befund.

**Zyklus 2 (neuer Versuch EXP-083, vorbereitet, 18:28 gemessen).** Frage: Wirkt der Attention-Reset (K4d) nur deshalb stärker als der MLP-Reset, weil er mehr Bewegung seit der Init zurücknimmt (Gutachter-Einwand O6)? Die Blöcke speichern Gewichte bei Schritt 50 nicht, aber W_E-Schnappschüsse bei 0 und 50: Das erlaubt ein hartes Tor (Nachlauf auf 50 Schritte muss den Blockzustand treffen). [[experiments/EXP-083-reset-displacement/README|EXP-083]]: 80 × 50 Schritte GPU, Lesart vorab (≥ 15/20 Seeds). Exploration an gesehenen Seeds. Code ungetestet, unabhängige Code-Prüfung läuft.

*Nachtrag Zyklus 2:* Unabhängige Code-Prüfung von `measure.py`/`jobs.txt` (Prüfagent, nur Lesen): **ein echter Fehler**. Der Init-Nachbau setzte `torch.set_num_threads` nicht vor `set_seed`, der Trainer tut das. Die Prüfsumme hätte fälschlich scheitern können. Behoben. Hinweis: In `jobs.txt` fehlen `--switch-split-file`/`--switch-step`. Das ist bei 50 Schritten ohne Wirkung (die Umschaltung greift erst nach Schritt 50), in der README begründet; das W_E-Tor bei Schritt 50 prüft es zusätzlich. Die Zuordnung (Split, Reset-Arm) der eingefrorenen Läufe und die Parameternamen sind laut Prüfung korrekt.

**Zyklus 3 (Bestätigungsentwurf R4, vor 18:35, gemessen).** Frage: Wie beantwortet das Labor den stärksten Gutachter-Einwand (O1), dass K2 nur für konstruierte Splits gilt? Im Archiv gefunden: [[experiments/EXP-015-mask-spectrum/README|EXP-015]] zeigt für gewöhnliche Zufallssplits eine vorab registrierte Assoziation (r̄ 0.279 gegen 0.492 mit fremden Masken, 10 Seeds). Split und Init teilen dort aber den Seed. Das steht jetzt so im Entwurf (§4, §1b, §6). EXP-014 heute Nacht ist nur ein Pilot mit 5 Einheiten auf der CPU (kleinstes p = 1/32) und steht in der CPU-Reihenfolge hinter EXP-040. **Neu:** [[confirm/R4_REGISTRATION_DRAFT|R4]] mit gekreuztem Init × Split-Design: je Einheit 2 Inits × 2 Zufallssplits aus eigenen SeedSequence-Strömen, 40 Einheiten (160 GPU-Läufe à 2000 Schritte, ≈ 35 min). Kontinuierliches Maß: Spearman der W_E-Spektren; H1 S_split − S_none > 0.05, H2 S_init − S_none > 0.05, Holm. Code `lab/tools/confirm_r4.py` und Power-Bericht `lab/confirm/R4_pilot_n.py`, beide ungetestet. **Eigene Korrektur vor jedem Lauf:** Der erste Entwurf wählte n = 30 oder 40 je nach Pilotstreuung. Das war ein unnötiger Freiheitsgrad, jetzt fest 40, der Pilot liefert nur noch einen Power-Bericht. Eine geschätzte Uhrzeit im Entwurf („≈ 18:45“) wurde auf den gemessenen Wert korrigiert. **Nächste Schritte:** Code-Prüfung läuft; Selbsttest im Fenster; Codex-Prüfung vor dem Einfrieren (Regel 18c); Rechnen frühestens in der Nacht 28./29.

**Zyklus 4 (Entwurf §2 und Literatur zu R4, bis 18:37, gemessen).** Frage 1: Kann der Methodenteil ohne die alte Gliederung stehen (Gutachter-Strukturpunkt 1)? Die vier Maße (Δ_pow, D, π, R) stehen jetzt als Prosa in §2, übernommen aus der geprüften Gliederung; Δ_pow und δ = 0.02 am Code gegengeprüft (`confirm_p1.py:294`, `confirm_p2d.py:33`). Die Gliederung ist als „ersetzt“ markiert und wird erst beim Umbau nach den Nachtblöcken gelöscht. Frage 2: Trennt schon eine Arbeit Init- und Split-Seed für die *Identität* der gelernten Frequenzen? Zwei Suchen: He et al. 2026a (Init-Lotterie, volle Daten) und Ootani 2026 (2607.05104; fester Test-Seed, misst nur die Konzentration des Spektrums). **Ergebnis:** Nichts schränkt R4 ein (vorläufig; in [[paper/related_work]] nachgetragen).

*Nachtrag Zyklus 3:* Code-Prüfung von `confirm_r4.py` (Prüfagent, nur Lesen): keine Fehler in Run-IDs, Split-Validierung, Paar-Definitionen, Unabhängigkeit der Split-Ströme, Holm/KI-Logik oder Fehlläufen. Das gekreuzte Design wird durch gemeinsame Struktur nicht verzerrt (hebt sich in allen drei Paartypen auf). Übernommen: (1) Der Selbsttest verlangte im Nullfall |mittleres Δ| < 0.05; bei einer Rausch-SD von ≈ 0.04 hätte er zufällig scheitern können. Die Grenze ist jetzt 0.1 (nur synthetische Prüfung, keine Registrierungsänderung). (2) Zusätzlich zur Anzahl wird jetzt der *Anteil* generalisierter Läufe ausgegeben, wie registriert. R4 bleibt ungetestet; der Selbsttest folgt im Fenster, Codex vor dem Einfrieren.

**Zyklus 5 (Codex-Prüfung von R4 vor dem Einfrieren, bis 18:52, gemessen).** Frage: Hält der R4-Entwurf einer Prüfung durch eine andere Modellfamilie stand (Regel 18c: vor dem Einfrieren)? Codex (`lab/confirm/R4_codex_review_s30.txt`, direkt über `codex-companion.mjs`, Vordergrund) meldete **1 Blocker, 4 Major, 1 Minor**. Alle Punkte habe ich selbst geprüft, alle übernommen. (1) **Blocker, bestätigt:** Das Code-Tor enthielt die transitiven Importe von `confirm_p1` nicht (`confirm_splits.py` lädt EXP-043/046-Module); der Selbsttest wäre sicher gescheitert, und diese Dateien wären ungehasht gewesen. Weder mein eigener Prüfagent noch ich hatten das gesehen. (2) Spearman über alle 56 Frequenzen misst nicht die Wahl der Schlüsselfrequenzen, und H2 (Init) kann bloße Erhaltung des Init-Spektrums messen. (3) **Selbst bestätigt:** Zufallssplits generalisieren erst bei ≈ 3900 Schritten (EXP-003d, Seed 10: 3925), Schritt 2000 liegt also vor dem Grokking. (4) MDE und n waren nicht begründet. (5) Es fehlten Tore für Init-Prüfsummen und die Spektrumsform. **Neu kalibriert** (`lab/confirm/R4_null_calibration.py`, gespeicherte Studienläufe Seeds 0–9, nur Laden): Null-SD Spearman 0.149 (2000), Kosinus 0.125 (8000). Der Kosinus ist bei 2000 unbrauchbar (0.78 ± 0.055, flacher Sockel). **Neuer Entwurf:** H1a Spearman bei 2000 (nur Rangsignatur), H1b Kosinus bei 8000 (energiegewichtet, nach dem Grokking), Holm über 2, MDE 0.05/0.04, H2 nur beschreibend, 60 Einheiten (80 % Power ab Δ ≈ 0.105 bzw. 0.085, sonst gering gepowert), 240 Läufe ≈ 1.6 h GPU. **Ergebnis:** Der Entwurf ist deutlich sauberer, bleibt aber ungetestet. **Nächster Schritt:** Selbsttest im Fenster; Codex prüft nur die geänderten Punkte nach, dann Einfrieren.

*Nachtrag Zyklus 5 (18:56, gemessen):* Codex-Nachprüfung (`lab/confirm/R4_codex_recheck_s30.txt`): Punkte 1–3, 5, 6 sind behoben, Punkt 4 teilweise. Neuer Major: Die Power-Rechnung nutzte die SD der Paar-Ähnlichkeiten statt der Einheitenstatistik Δ. Stimmt, übernommen: Unter der Null habe ich die Einheitenstatistik direkt nachgerechnet (vier fremde Studienläufe in den vier Zellen, alle 5040 geordneten Zuordnungen, `R4_null_calibration.py`). SD(Δ_split) = 0.145 (Spearman, 2000), 0.085 (Kosinus, 8000). Damit gilt 80 % Power ab Δ ≈ 0.102 bzw. 0.071; MDE und n bleiben unverändert. Vorbehalt in der Registrierung: Die Kalibrierung stammt aus dem Studientrainer (CPU), die Übertragung auf R4 (GPU) ist ungeprüft. R4 ist damit bereit für den Selbsttest im Fenster und danach das Einfrieren.

**Zyklus 6 (Nacht vorbereiten, Einwand O2 geprüft, bis 18:58, gemessen).** (a) `lab/confirm/R4_manifest_DRAFT.json` angelegt, mit Einfrier-Anleitung im Feld `note`. In der [[STATE]]-Reihenfolge gilt: Der R4-Selbsttest läuft heute Nacht in jedem Fall; einfrieren und rechnen nur, wenn nach R1 noch ≥ 2.5 h bleiben. (b) Frage: Lässt sich Einwand O2 (K2-Funktion folgt der Energie) mit einer weiteren Vorab-Registrierung an P2f entkräften? **Nein, verworfen:** [[experiments/EXP-068-matched-sensitivity/README|EXP-068]] zeigt, dass Ablationsmaße Nutzung und Energie grundsätzlich nicht trennen, weil sie nur die Dosisgeometrie tauschen. Eine weitere Ablations-Registrierung würde nur den bekannten Vorbehalt bestätigen. Die Idee eines energieerhaltenden Phaseneingriffs steht als Kandidat [[NOVEL_DIRECTIONS]] N42, mit der offenen Hürde, dass eine Nullvorhersage fehlt. Kein Code. Die Paper-Formulierung bleibt: „check, der der Energie folgt“.

**Zyklus 7 (Literaturliste und Quellenprüfung der Entwurfsänderungen, bis 19:02, gemessen).** (a) [[paper/references]] erstellt (Agent, nur aus [[paper/related_work]]): 35 Zitate, 18 vollständig; offen sind fehlende Venues, URLs und Prüfgrade (für die menschliche Prüfung). **Eigener Fehler:** Janati et al. 2026 hatte ich im Entwurf zitiert, ohne den Eintrag in related_work zu ergänzen; nachgetragen. Mehrdeutige Zitate eindeutig gemacht (He 2026a, Kleinman 2023/2024, Frankle/Schwab/Morcos). (b) Unabhängiger Quellenprüfer über alle heutigen Entwurfsänderungen (`git diff 45b3762 HEAD`): alle Zahlen stimmen (N29/N29b/N29c, P3/N28, EXP-072, Gewichte 0.05–3, Definitionen). **Vier Fehler meinerseits, korrigiert:** (1) Der R4-Eintrag in §3.7 stand noch auf der alten Fassung (40 Einheiten). (2) EXP-015 war überzeichnet: Die Vorab-Entscheidung fiel bei n = 8 (0.277 gegen 0.499), die Werte mit 10 Seeds wurden nachträglich berichtet, und „Assoziation“ ist die spätere Deutung. (3) Der Kontrollpool in §2 schließt nur die 2k-Harmonischen der *eigenen* Ziele aus (am Code `EXP-051 control_set` bestätigt). (4) Zu LeDoux: „kein Reihenfolgekanal“ widersprach seinem Zitat „not absent … degenerate“. Dazu zwei kleine Glättungen: Beitrag (i) jetzt „engineered“, „far from uniform sampling“.

**Zyklus 8 (Abbildung 0 zum Aufbau, bis 19:04, gemessen).** Frage: Kann eine Abbildung dem Leser zeigen, worin sich ein konstruierter Split von einem zufälligen unterscheidet (Gutachter-Strukturpunkt 7)? `lab/paper/figures/fig0_setup.py` nutzt nur Splitdateien (P1, add 113, Seed 1000; Arm R mit ε = 0, Arm F mit ε = 2; Manifest 733e829). **Beobachtung:** Beide Masken sehen für das Auge gleich zufällig aus (angeordnet nach a und c). Der Unterschied liegt allein im Spektrum: M0c-Zielanteil 0.089 (R, entspricht dem Zufall 5/56) gegen 0.194 (F). Das ist fürs Paper eine nützliche Botschaft: Die Steuerung braucht keine sichtbare Symmetrie (Abgrenzung zu Tomàs Bernal et al.). Dazu ein schematisches Wechselprotokoll. Gerendert, angesehen, eine Beschriftung korrigiert.

**Zwischenbilanz nach 8 Zyklen (Auftrag §4).** *Gelernt:* (1) Der Entwurf hatte echte Lücken, die ein Gutachter sofort findet: Rahmen zu weit (konstruierte vs. zufällige Splits), Zahlen der Einleitung nicht in §3, Methoden auf eine Gliederung verwiesen. Das ist jetzt behoben und unabhängig geprüft. (2) Der stärkste Einwand (Zufallssplits) war bisher nur mit einer seed-gekoppelten Assoziation belegt; R4 kann ihn entscheiden. Ohne die Codex-Prüfung wäre R4 mit falschem Zeitpunkt (vor dem Grokking), fehlendem Code-Tor und unbegründeter Power eingefroren worden. (3) Meine eigenen Prüfagenten fanden je einen echten Fehler (Thread-Zahl in EXP-083, Selbsttest-Grenze in R4), Codex einen, den beide übersehen hatten (transitive Importe). Mehrere Prüfer mit verschiedenen Blickwinkeln lohnen sich vor jedem Einfrieren. *Wiederholen wir uns?* Nein; aber alle Zyklen sind Paper- und Designarbeit ohne neuen Messbefund (Fenster zu). *Messungen geeignet?* Der Kosinus taugt erst nach dem Grokking, Spearman gewichtet schwache Frequenzen. Beides steht jetzt in R4. *Nächste Annahme zum Angreifen:* dass die Nullkalibrierung (Studientrainer, CPU) auf R4 (GPU) übertragbar ist. Das prüft der R4-Selbsttest nicht; es zeigt sich erst am Smoke und an S_none der echten Läufe (beschreibend berichten).

**Zyklus 9 (Literaturliste vervollständigen, bis 19:07, gemessen).** Frage: Welche der 15 Preprints in [[paper/references]] haben eine Venue? Ein Agent las die arXiv-Abstractseiten (WebFetch, gegen die HTML-Metadaten abgeglichen): Nur Tomàs Bernal et al. 2026 und Sevetlidis & Pavlidis 2026 nennen eine (AISTATS 2026), die übrigen 13 sind Preprints. Die Titel von Dong und Khanh sind bei uns gekürzt. Offen für den Nutzer: die Namensform Tomàs Bernal und die Schreibung „Gharda“ Sokar. Ergebnis in [[paper/references_venues_check]].

**Zyklus 10 (Überdauert die Steuerung das Grokking? Exploration, bis 19:08, gemessen).** Frage (typischer Gutachter-Einwand): K2 ist bei Schritt 2000 gemessen. Ist das nach dem Grokking noch so? Vorab im Skriptkopf festgelegt: Mittel von Δ_pow, KI und Anteil > 0 je gespeichertem Schritt. Erwartung: positiv, eventuell schrumpfend; ein Vorzeichenwechsel in den meisten Seeds wäre ein Gegenbefund. `lab/confirm/P2de_posthoc_dpow_time.py` an den gespeicherten P2d/P2e-Läufen: Die Seeds waren für K2-Funktion gesehen, Δ_pow nach 2000 nie. **Ergebnis:** Δ_pow > 0 in 20/20 Seeds jeder Aufgabe ab Schritt 250 bzw. 500. Der Wert wächst nach der Generalisierung weiter und flacht dann ab: add 113 7.77 [7.36, 8.18] bei 2000, 9.44 [8.99, 9.90] bei 4000; mul 113 9.69 [8.99, 10.29] bei 8000; add 97 9.39 [8.89, 9.84] bei 8000. Die Erwartung „schrumpft eventuell“ traf **nicht** zu. **Urteil:** Exploration, stützt, dass K2 kein Übergangseffekt vor dem Grokking ist (Gegenbefund ausgeschlossen). Mechanismus (Weight Decay beschneidet nach dem Grokking die nicht gesteuerten Ziele) nur vermutet. Im Entwurf §4 ergänzt. Grenze: gesehene Seeds, für eine Kernaussage wäre ein vorab festgelegter späterer Messpunkt an frischen Seeds nötig (z. B. in R1/P4 beschreibend mitlesen).

*Nachtrag Zyklus 10:* Die Mechanismus-Vermutung habe ich direkt an denselben Läufen geprüft (add 113, Median über 40 Arme, gleiche Spektren). Die Ziele des anderen Arms fallen bis Schritt 2000 unter ihr Init-Niveau (500: 13.0, 2000: 1.9, Init 10.0) und bleiben danach flach (4000: 1.6). Die eigenen Ziele wachsen weiter (2000: 128, 4000: 202; Anteil an der W_E-Leistung 0.82 → 0.89). Das späte Wachstum von Δ_pow tragen also die eigenen Ziele, nicht weiteres Beschneiden. Die Vermutung „Weight Decay beschneidet nach dem Grokking“ war für diese Phase falsch; im Entwurf korrigiert (beschreibend, inline gerechnet, Zahlen im Entwurf).

*Nachtrag (19:09):* Die Zerlegung steht jetzt auch im Skript (`decomposition()` in `P2de_posthoc_dpow_time.py`, Ergebnis in der JSON), gleiche Zahlen.

**Zyklus 11 (Beschleunigen konstruierte Splits das Grokking? Beobachtung und Wiederaufnahme von EXP-018, bis 19:12, gemessen).** Beobachtung beim Durchsehen gespeicherter Läufe (post hoc, nicht vorab festgelegt): Konstruierte Splits generalisieren sehr viel früher als zufällige. Auf demselben Gerät (CPU) liegt der Median bei 662 Schritten (EXP-016, 20 Läufe) gegen 5975 (EXP-003d-Baselines, 10 Läufe); P1 add 113 auf der GPU bei 725 (117/120). In [[experiments/EXP-047-marginal-control/README|EXP-047]] (gleiche Seeds und Init, gleiche Größe und gleiche Token-Häufigkeiten, nur die Paarstruktur zufällig gemischt) generalisierten 20/20 konstruierte Arme (Median 688) gegen 0/20 gemischte (Test 0.02–0.28 bei 2000 Schritten). **Vorbehalt:** Die Testmengen waren überall Komplemente des Trainingssplits. Genau dieses Artefakt und die „bloß strukturierte Ungleichverteilung“ trennt [[experiments/EXP-018-split-speed/README|EXP-018]]: gemeinsame Testmenge, Kontrollarm D mit exakt gleichen Gewichten, nur die Anordnung entlang a zerstört. EXP-018 ist seit Sitzung 5 vorab registriert und Codex-geprüft, wurde aber nie gerechnet. **Entscheidung:** EXP-018 auf die GPU (Nachtrag c, keine Kriterienänderung, ≈ 15 min) und in den Nachtplan ([[STATE]] Schritt 7). Suche (1 Anfrage, 2026-09-27: „grokking modular addition training subset selection speeds up generalization structured training pairs Fourier 2026“): nichts, was N6 einschränkt (Treffer: He et al. 2026a, 2609.17571, 2603.23784, alle ohne Datenauswahl). **Einordnung:** Beobachtung, kein Befund; wird mit EXP-018 entschieden. Nach dem Frequenzprinzip-Bild (Zhou et al. 2024) wäre eher eine Verzögerung zu erwarten.

*Nachtrag Zyklus 11:* „Generalisierung“ heißt hier das Ereignis `generalization_step` des Trainers, also Test ≥ 0.95 (`THRESHOLD_SETS['primary']`), geprüft. Der Entwurf nannte zunächst fälschlich 0.9; korrigiert.

*Nachtrag Zyklus 11 (19:14, gemessen), wichtige Korrektur:* Beim Prüfen, ob die EXP-018-Seeds 20–29 unberührt sind: **Sie sind es nicht.** EXP-041 hat die reinen Arme E und R mit denselben Seeds, Splits und der gemeinsamen Testmenge T* gerechnet (CPU, 2150 Schritte; Hashes in 20/20 Läufen geprüft), EXP-020 die Splits für Wechselläufe. **Ergebnis (post hoc, war nie als Geschwindigkeit ausgewertet):** E generalisiert (≥ 0.95) in 9/10 Seeds (425–1775 Schritte), R in 0/10 (Test ≤ 0.15 bei 2150). Paarweise ist die Reihenfolge in allen 9 bestimmten Seeds E vor R (exakter Vorzeichentest einseitig p = 1/512 ≈ 0.002, post hoc). Damit ist der Komplement-Einwand für E gegen R ausgeräumt; offen bleibt nur der Kontrollarm D (gleiche Gewichte, Anordnung zerstört). D lief nie, der Primärvergleich E gegen D bleibt prospektiv. Nachtrag c in der EXP-018-README, Entwurf und FINDINGS korrigiert. Lehre: Vor der Wiederaufnahme eines alten Versuchs die Seed-Nutzung im ganzen Labor prüfen, nicht nur die README.

**Zyklus 12 (Literatur zur Grokking-Beschleunigung, bis 19:18, gemessen).** Frage: Ist die Beobachtung aus Zyklus 11 schon bekannt? Agent mit 21 Anfragen ([[paper/lit_grokking_speed_2026-09-27]]), den nächsten Treffer habe ich selbst am Abstract geprüft. **Ergebnis:** Teilweise bekannt. AlQuabeh et al. 2025 (2505.15624) beschleunigen das Grokking durch Sampling, das die Token-Häufigkeiten ausgleicht; Augmentierung (Kommutativität) und Hilfsverluste beschleunigen ebenfalls. Nicht gefunden wurde eine Beschleunigung durch Konzentration des Paarspektrums bei fester Größe (vorläufig). Unsere Abgrenzung stützt EXP-047: gleiche Token-Häufigkeiten, trotzdem 20/20 gegen 0/20. EXP-018 (Arm D) prüft zusätzlich, ob jede strukturierte Ungleichverteilung reicht. Das Frequenzprinzip (Zhou et al. 2024) sagt das Gegenteil voraus. Entwurf §4 und related_work ergänzt.

**Zyklus 13 (Bestätigung der Beschleunigung vorbereiten, bis 19:20, gemessen).** Frage: Wie wird aus der Beobachtung (Zyklen 11–12) eine belastbare Aussage? [[confirm/R5_REGISTRATION_DRAFT|R5]] ist als Entwurf **ohne Code** angelegt: Arme E, D und R wie EXP-018 an frischen Seeds mit eigenem Split-Strom; H-ER und H-ED (Holm über 2) mit zensierungsfester Ko-Bedingung; Mindesteffekt Faktor 2. Die Fallzahlregel n = max(20, n_D) aus der Pilotstreuung von EXP-018 steht fest, bevor der Pilot läuft. Den Code schreibe ich bewusst erst nach dem EXP-018-Ergebnis, weil der Kontrollarm D das Design noch ändern kann; so vermeide ich Code für ein vielleicht überholtes Design.

**Zyklus 14 (Codex-Designprüfung R5, bis 19:26, gemessen).** Codex: nicht einfrierbar, 4 Blocker und 2 Major (`lab/confirm/R5_codex_design_review_s30.txt`). Den wichtigsten Punkt habe ich selbst nachgemessen: Arm D (EXP-018, auch Vorlage für R5) gleicht nur die Zieh-Gewichte je Antidiagonale an. Die realisierten Anzahlen je Ausgabe weichen zwischen E und D im Mittel um 2.8–2.9 Paare ab (Seeds 20–22, ≈ 34 je Ausgabe), die Streuung ist ähnlich. Übernommen für R5: D aus der realisierten Maske permutieren; Ereignis mit ≥ 3 aufeinanderfolgenden Auswertungen plus Memorisation; p = max(p_L, p_Vorzeichen) je Kontrast, dann Holm; n per Simulation der ganzen Entscheidungsregel; „Faktor 2“ nur als Punktschätzer; getrennte Seed-Namensräume; Ziele unabhängig von der Init, zwei Zielmengen je Init; Aussage auf wd = 1 beschränkt. EXP-018 läuft trotzdem unverändert als Pilot (registriert), nur mit Lesehinweis. **Ergebnis:** R5 ist noch nicht einfrierbar; die Überarbeitung folgt nach EXP-018.

*Nachtrag Zyklus 14 (19:26):* `lab/confirm/R5_power_sim.py` geschrieben: Es simuliert die vollständige R5-Entscheidungsregel aus den EXP-018-Pilotzeilen, wie von Codex verlangt. Ungetestet (nur Syntaxprüfung), Selbsttest im Fenster.

### Abschlussbericht Sitzung 30 (2026-09-27, 18:19–19:28 Berlin, gemessen; Run-Fenster die ganze Zeit zu, kein Training, kein Test)

**Wichtigste Ergebnisse:**
1. **Paper-Entwurf aus Gutachtersicht überarbeitet:** Der Rahmen ist enger (konstruierte Splits, eine Optimierer-Einstellung, D₅₉ vor dem Grokking). Fehlende Armmittel und Werte nur über generalisierte Seeds kamen aus den eingefrorenen Analysen dazu, die Maßdefinitionen stehen jetzt im Methodenteil, dazu die Abgrenzung zu LeDoux. Die Literaturliste (35 Zitate) und der Venue-Abgleich sind fertig, außerdem Abbildung 0 (Aufbau). Ein unabhängiger Quellenprüfer fand 4 eigene Fehler; alle korrigiert, keine bestätigte Zahl geändert.
2. **Neue Beobachtung (post hoc, Exploration):** Konstruierte Splits groken ≈ 9× früher als Zufallssplits: auf der CPU nach 662 statt 5975 Schritten; mit gemeinsamer Testmenge (EXP-041-Läufe) 9/10 gegen 0/10 bis 2150 Schritte, Vorzeichentest p = 0.002; bei gleichen Token-Häufigkeiten (EXP-047) 20/20 gegen 0/20. Teilweise bekannt ist Datenauswahl über Token-Häufigkeiten (AlQuabeh et al. 2025). Die Konzentration des Paarspektrums wurde nach unserer Suche nicht gefunden (vorläufig). Entschieden wird mit EXP-018 (seit Sitzung 5 registriert, Kontrollarm D prospektiv, heute Nacht GPU ≈ 15 min).
3. **Steuerung nach dem Grokking (post hoc):** Δ_pow bleibt in 20/20 Seeds je Aufgabe positiv und wächst nach der Generalisierung weiter (add 113: 7.8 → 9.4; mul 113 / add 97 ≈ 9.4–9.7 bei 8000), getragen von den eigenen Zielen. Die vermutete Ursache „Beschneiden“ war für diese Phase falsch.
4. **Vorbereitet (ungetestet):** R4 (Zufallssplit gegen Init, gekreuzt, 240 GPU-Läufe; zwei Codex-Runden, 1 Blocker + 5 Major eingearbeitet, Null-SD der Einheitenstatistik nachgerechnet); EXP-083 (Verschiebung je Reset-Teil, Code-Fehler gefunden und behoben); R5 (Bestätigung der Beschleunigung; nur Entwurf und Simulationswerkzeug, Codex-Design: 4 Blocker, die Umsetzung folgt nach EXP-018).

**Negativ/verworfen:** N42 (Phaseneingriff für „Nutzung jenseits der Energie“) nach Überschlag verworfen: Drehung ist wie Ablation eine relative Dosis. Eine C5-Registrierung zu Einwand O2 unterblieb aus demselben Grund.
**Eigene Fehler:** eine geschätzte Uhrzeit im R4-Entwurf (korrigiert); ein unnötiger Freiheitsgrad in der R4-Fallzahl (entfernt); das Code-Tor von R4 ohne transitive Importe (Codex-Fund); Janati et al. zitiert, ohne den Eintrag in related_work anzulegen; im Entwurf die Schwelle 0.9 statt 0.95; EXP-018-Seeds zunächst für unberührt gehalten (sie waren über EXP-041 gesehen).
**Reproduktion (nur Laden und numpy):** `python lab/confirm/P2de_posthoc_dpow_time.py`, `EXP041_posthoc_speed.py`, `speed_posthoc_gen_steps.py`, `R4_null_calibration.py`, `R4_design_lever.py`, `python lab/paper/figures/fig0_setup.py`.
**Nächste Aktion:** ab 00:00 [[STATE]] Schritte 1–10. Neu in Schritt 5 und mit hoher Priorität: EXP-018 zuerst auf der GPU. Dazu R4-Selbsttest, EXP-083 und die Lesehinweise 13–14 in [[LESART-nacht-2026-09-28]].
**Runner:** aktiv; next_start_utc 2026-09-27T19:54:45Z = **21:54 Berlin**. **Früher beendet** als die Deadline (21:19): Alle weiteren Schritte hängen an Ergebnissen dieser Nacht. Code für R5 jetzt hieße, für ein Design zu programmieren, das Arm D noch ändern kann.

## Sitzung 31 (2026-09-27, ab 19:29 Berlin, gemessen; vom Runner gestartet, Run-Fenster zu bis 00:00, Deadline 22:29)

Start: kein STOP, `guarded_run.py --check` Exit 3 (außerhalb des Fensters), keine Trainingsprozesse.

**Zyklus 1 (ungelesenes Ergebnis EXP-042, bis 19:33, gemessen).** Frage: Warum liegt eine unversionierte `EXP-042/summary.json` von 12:54 vor, obwohl STATE „EXP-042 teilweise“ sagt? Das Log `lab/runner/logs/np_cpu_s24.log` zeigt: 36/36 Läufe ok, danach `analyze.py` über den Wächter (Exit 0, 12:53:59); erst die folgende EXP-040-Stufe wurde am Fensterende verweigert. STATE war also falsch, und das Ergebnis blieb drei Sitzungen lang ungelesen. **Ergebnis (vorab festgelegtes Urteil):** eps 8 ***unklar*** (Seed 30 *gleich*; 31, 32, 34 *unklar* wegen Nichtmonotonie um eine Einheit bzw. Gleichstand d(50) = 0 bei Seed 32); keine Zelle *später*. eps 1 (beschreibend) 3/4 *früher*. Beschreibend gegen eps 2 (EXP-020, gleiche Seeds): mittleres d bei t = 25 ist 0.75 / −1.75 / −4.25 für eps 1 / 2 / 8, bei t = 50 2.5 / 2.5 / 1.0. Stärkeres G kippt die Top-5-Menge also später. Die vor jedem Lauf eingefrorene Vorhersage eines **reinen Takts** mit linearer Überlagerung (Nachtrag b, Commit e9a9c56, Log-Zug) trifft das beobachtete Intervall bei eps 8 in 3/4 Seeds und bei eps 1 in 2/4, und zwar in der richtigen Richtung. Das spricht dafür, dass die Verschiebung schon aus dem Takt folgt und keinen Vorsprung-gegen-Neigung-Mechanismus (H42) braucht; das Top-5-Maß kann beides aber nicht trennen. **Entscheidung:** Das Urteil bleibt *unklar*. Die trennende π-Lesart (`pi_window.py`, C/O) kommt in die Nacht als Sekunden-Auswertung vor dem CPU-Start; EXP-042 wird aus dem CPU-Befehl gestrichen (spart die Wiederholungsprüfung). README (Ergebnis, Frontmatter), [[LAB]] und [[STATE]] nachgetragen. **Lehre:** Bei „teilweise“ im STATE immer zuerst das Log lesen. Die Programmzusammenfassung listete EXP-042 nicht als fertig, weil der Lauf danach abbrach.

**Zyklus 2 (Dosis-Wirkung der Grokking-Beschleunigung, post hoc, bis 19:36, gemessen).** Frage: Hängt das frühere Grokking konstruierter Splits (Sitzung 30, ≈ 9×) abgestuft von der Konzentration ab? Dafür eignen sich die Nur-G-Läufe von EXP-020 (ε 2) und EXP-042 (ε 1, 8): Je Seed sind Init und Testmenge gleich (Prüfsummen), die Trainingsmenge hat 3831 Paare, die Streuung der Zeilen-, Spalten- und Ausgabezahlen ist ähnlich. **Ergebnis:** Generalisierung nach 425–450 (ε 8), 700–900 (ε 2) und bei ε 1 gar nicht innerhalb von 2000 Schritten (Test 0.06–0.80). Die Ordnung ist in 4/4 Seeds streng (einseitiger Vorzeichentest p = 0.0625, n = 4). Die Memorisation liegt überall bei 110–140. Nebenbefund Reproduzierbarkeit: Die EXP-042-F-Läufe treffen die Generalisierungsschritte von EXP-020 bei anderem Code-Stand exakt (950, 625, 1225, 650). Eine einfache 1/Anteil-Skalierung passt zwischen ε 2 und 8 (≈ 800 → 400), unterschätzt aber ε 1 (vorhergesagt ≈ 1250, beobachtet > 2000) und den Zufallssplit (≈ 1600 gegen ≈ 6000); der Zusammenhang ist steiler als 1/Anteil (nur beschreibend). **Entscheidung:** Das ist Exploration an gesehenen Seeds, keine Aussage. Als Designvorschlag in [[confirm/R5_REGISTRATION_DRAFT|R5]] eingetragen (Dosis-Trend über ε als zweiter Weg neben Arm D); FINDINGS ergänzt. Skript: `lab/experiments/EXP-042-bias-strength/posthoc_speed_dose.py` (nur Laden). Grenze: Mit ε ändert sich auch, welche Paare gezogen werden; ein Dichteeffekt ohne Spektrum ist nicht ausgeschlossen.


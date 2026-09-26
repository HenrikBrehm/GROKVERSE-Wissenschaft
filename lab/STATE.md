---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-26, 06:53 Berlin (Sitzung 5, vom Runner gestartet 03:49Z, Deadline 06:49Z = 08:49 Berlin)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[JOURNAL]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]]

## Wiederaufnahme (zuerst lesen)

- **Sitzung 5 lief ohne Training:** Der Start der Warteschlange wurde vom Auto-Mode-Klassifikator abgelehnt
  (siehe Blocker). Vorher prüfen, ob der Nutzer eine Freigabe erteilt hat.
- **Neue Warteschlange:** `sh lab/experiments/queue_s5.sh` (ersetzt `queue_s4b.sh`, dieselben Läufe plus EXP-018/020,
  neue Reihenfolge). Log z. B. nach `lab/runner/logs/queue_s5.log`. Reihenfolge: EXP-016 Seeds 16–19 (je 2 × 4.5 min,
  danach Entscheidung) → EXP-003d-Baselines 18, 19 → Smoke EXP-018 und EXP-020 (+ `check_smoke.py`) → EXP-018 Seeds
  20–24 → EXP-014 Kreuzpaare → EXP-020 → EXP-018 Seeds 25–29 → EXP-010-Tausch 11–19. Danach `sh lab/experiments/EXP-022-single-frequency/queue.sh`
  (15 Läufe à 13 min, Modelle gespeichert). Sie stoppt bei **jedem** Exit ≠ 0;
  fertige Läufe werden übersprungen (`freq_ban.py` endet dann seit Sitzung 5 mit 0). Neu starten = fortsetzen.
- **Abgebrochene Läufe** stehen mit `status: running` in `result.json` und werden neu gestartet (kein Resume).
- Vor jedem Start: `python lab/tools/guarded_run.py --check`.
- Nach EXP-016 Seed 17 (8 Seeds): `python lab/experiments/EXP-016-engineered-split/analyze.py`.

## Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  Uncommittete Änderungen an `lab/runner/*`, `lab/runner-state.json` und `lab/tools/guarded_run.py` stammen vom
  Nutzer (Regeln 13/14, keine feste Jobgrenze). Sie sind bewusst nicht committet; der Nutzer entscheidet.
- **Umgebung:** Windows 11, Python 3.12, torch 2.13.0, numpy 2.5.1 (Studie: torch 2.12.1). Die rekonstruierten Inits
  stimmen trotzdem bitgenau mit den gespeicherten Schritt-0-Checkpoints überein. 0.13 s/Schritt (Transformer, 4 Threads).
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Interpretation bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`), Sitzungsstart und -ende-Klassifikation belegt.

## Stand der Versuche (nach Sitzung 5)

**Bestätigt an frischen Seeds 10–17 (vorab festgelegt):**
- [[experiments/EXP-015-mask-spectrum/README|EXP-015]]: Das Masken-Spektrum M0 des Trainingssplits (ohne Gewichte) sagt die
  Rangfolge der gelernten Frequenzen voraus (r̄ 0.277, fremde Masken 0.499, p 2.5e-5). **Nur Assoziation.**
- [[experiments/EXP-012-init-gradient/README|EXP-012]]: Erster Gradient an W_E > Init-Spektrum (p 0.031).

**Läuft:** [[experiments/EXP-016-engineered-split/README|EXP-016]] 6/10 Seeds, Δ = +8, +7, +7, +7, +8, +9. Entscheidung ab 8.

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
**Teilweise:** EXP-010 (1/10 Paare), EXP-003d (8/10 Baselines).

## Nächste konkrete Aktionen (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`, dann `sh lab/experiments/queue_s5.sh` im Hintergrund, beobachten.
2. EXP-016 auswerten, sobald 8 Seeds da sind; EXP-015/012 Phase 2 mit n = 10 nur berichten.
3. Nach den Smokes: `check_smoke.py` (EXP-020) und `result.json` des EXP-018-Smokes prüfen (`test_hash`, 2554 Testpaare).
4. Auswertungen: `EXP-021-harmonic-misses/analyze.py`, `EXP-022-single-frequency/analyze.py`, `EXP-018-split-speed/analyze.py`, `EXP-019-coherent-mask/analyze.py`, `EXP-014-split-vs-init/analyze.py`,
   `EXP-020-data-switch/analyze.py`, `EXP-010-init-swap/analyze.py` (je über den Wächter, wo `make_dataset` benutzt wird).
5. Außerhalb des Fensters: Theorie (AGF-Nutzen mit maskiertem Verlust ↔ M0c herleiten), Reverse-Kontrolle G → F für
   EXP-020 als eigenen Nachtrag erwägen, Google Scholar gezielt zu N6.

## Blocker

- **Sitzung 5 (2026-09-26 05:52 Berlin):** Der Start von `sh lab/experiments/queue_s4b.sh` im Hintergrund wurde vom
  Auto-Mode-Klassifikator von Claude Code abgelehnt („Safety Bypass Flag“), obwohl jeder Lauf über `guarded_run.py`
  geht. Nach den Regeln der Ablehnung **nicht umgangen** (auch nicht über Einzelaufrufe). Die Warteschlange muss der
  Nutzer freigeben: entweder eine Bash-Berechtigungsregel für `sh lab/experiments/queue_s5.sh` (Nachfolger von `queue_s4b.sh`) bzw.
  `python lab/tools/guarded_run.py` hinzufügen oder die Warteschlange selbst starten. Bis dahin nur Denk- und Sucharbeit.

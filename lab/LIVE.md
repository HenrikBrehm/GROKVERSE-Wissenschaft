---
tags: [lab/live]
---
# LIVE: Laborsitzung 5

- **Sitzungsstart:** 2026-09-26 05:49 Berlin (03:49Z, vom Runner)
- **Deadline:** 2026-09-26 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 08:25 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin), Wächter `--check` ok.

## Gerade

**Sitzung beendet** (08:25 Berlin). Kein Lauf aktiv.

## Als Nächstes

Nächster geplanter Start: **2026-09-26 10:49 Berlin** (08:49Z, `next_start_utc`), im Run-Fenster. Dann
`sh lab/experiments/queue_s5.sh` fortsetzen (Baseline 19 → Smokes EXP-018/020 → EXP-018 → EXP-014 → EXP-020 → EXP-023 → EXP-022).

## Verlauf dieser Sitzung

- 08:24 Baseline 18 fertig (gen 8775). Wächter lehnt Baseline 19 ab (Deadline), Warteschlange sauber beendet.

- 08:11 Baseline 18: Schritt 3000, Train 1.0, Test 0.01 (Auswendiglernen, Grokking steht aus).

- 08:06 **[[experiments/EXP-016-engineered-split/README|EXP-016]] abgeschlossen: steuerbar.** 10/10 Seeds, Δ̄ = +7.7 von 10, p ≈ 0.001. Die Datenauswahl gibt die gelernten Frequenzen vor.

- 07:48 **EXP-016 Zwischenstand (8 Seeds):** Δ̄ = +7.6 von 10, 8/8 positiv, p = 0.004. Die konstruierten Splits geben die Frequenzen vor. Entscheidung bei 10 Seeds (laufen).
- 07:43 EXP-016 Seed 17: F 4/5, G 4/5; alle Abweichungen sind 2k-Harmonische.

- 07:39 EXP-016 Seed 16 Arm G: 3/5 aus G, die zwei anderen sind 2k-Harmonische von G-Zielen. Δ₁₆ = +8.

- 07:34 EXP-016 Seed 16 Arm F: Zielmenge exakt gelernt (5/5), gen 675.

- 07:31 Freigabe des Nutzers gefunden (06:58), Warteschlange gestartet.
- 07:28 Befundnotiz nach Codex-Konsistenzprüfung korrigiert (u. a. Rechenfehler: M0c − M0 ist ein Symmetrie-, kein Asymmetrie-Term).

- 07:09 [[experiments/EXP-023-split-value/README|EXP-023]] vorbereitet (eigene Wertematrix für Position 1 im Training), Codex-Review: 5 Befunde übernommen. Warteschlange: EXP-023 und EXP-022 direkt nach EXP-020.
- 06:58 **Eingriff in silico:** Eigene Wertematrix für Position 1 → die Interferenz im ersten Gradienten verschwindet (0.47 → −0.03). MLP-Kontrast bestätigt die Vorhersage. Befundnotiz [[BEFUND-split-mechanismus]].
- 06:54 Verdrängt werden die früh schwächsten Zielfrequenzen (14/14).

- 06:51 [[experiments/EXP-022-single-frequency/README|EXP-022]] vorbereitet: Erzwingt ein Ein-Frequenz-Split eine Ein-Frequenz-Lösung? Codex-Review: 5 Befunde übernommen.
- 06:40 [[experiments/EXP-021-harmonic-misses/README|EXP-021]] vorab festgelegt (Bestätigung der 2k-Fehlgriffe an frischen Läufen). M0c geschlossen hergeleitet: misst die Kommutations-Asymmetrie des Splits.

- 06:38 Ablation an Studienmodellen: 2k-Frequenzen sind die unwichtigsten der Top-5 (8/8), aber nicht null; Phasenkopplung nur teilweise.
- 06:35 **Direkte Messung:** Linke und rechte Eingabeposition interferieren im ersten Gradienten frequenzweise wie vom Masken-Kreuzterm vorhergesagt (18/18 Seeds). Codex-Angriff auf die Schlussfolgerungen: 5 Befunde, Formulierungen zurückgestuft.
- 06:26 Alle 14 „Fehlgriffe“ in EXP-016 sind 2k-Harmonische der Zielfrequenzen (post hoc); Sekundärgröße K_h für Seeds 16–19 vorab festgelegt.
- 06:24 Negativ: Fehlgriffe nicht aus Maske (M0c) und nicht aus dem Init-Spektrum.

- 06:22 **Mechanismus:** Der erste Gradient folgt dem kohärenten Masken-Spektrum M0c (ρ 0.77) deutlich besser als M0 (0.57), 10/10 Seeds.
- 06:21 Neue Warteschlange `queue_s5.sh` (Priorität: EXP-016 fertig → Baselines → EXP-018/020-Smokes → EXP-018 → EXP-014 → EXP-020).
- 06:19 [[experiments/EXP-020-data-switch/README|EXP-020]] (Datenwechsel F → G, kausale Festlegungszeit) vorbereitet, Codex-Review: 4 Befunde übernommen.
- 06:11 [[experiments/EXP-019-coherent-mask/README|EXP-019]] vorab festgelegt (M0c gegen M0, ohne eigene Läufe).

- 06:07 Literatur: Zhou/Zhang/Xu 2024 (Frequency Principle) sagen für EXP-018 das Gegenteil voraus (Verzögerung). Ein Repo mit festem Split zeigt: Auch die Init allein ändert die Frequenzwahl → der Split ist nicht die einzige Ursache.
- 06:04 Post hoc: Die natürliche Konzentration eines Zufallssplits sagt die Grokking-Zeit **nicht** voraus (ρ −0.40 / +0.15 / +0.02, alle n. s.).
- 06:01 Codex-Review EXP-018: 3 Befunde, alle übernommen (neue Kontrolle D, Zensur, Protokollprüfung). Tests 5/5 und 12/12.
- 05:56 [[experiments/EXP-018-split-speed/README|EXP-018]] vorab festgelegt: Beschleunigt ein konzentrierter Split das Grokking? Feste Testmenge, Seeds 20–29.

- 05:52 Queue-Start abgelehnt (Klassifikator). Nutzer muss die Freigabe erteilen, siehe [[STATE]] Blocker.
- 05:50 Stand gelesen, kein STOP, keine Python-Prozesse, Wächter: Fenster offen, 180 min.

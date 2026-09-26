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
- … ältere Einträge dieser Sitzung im [[JOURNAL]] (Sitzung 5).

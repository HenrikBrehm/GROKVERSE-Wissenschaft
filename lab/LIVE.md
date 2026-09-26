---
tags: [lab/live]
---
# LIVE: Laborsitzung 5

- **Sitzungsstart:** 2026-09-26 05:49 Berlin (03:49Z, vom Runner)
- **Deadline:** 2026-09-26 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 07:10 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin), Wächter `--check` ok.

## Gerade

Keine Trainingsläufe (Queue-Start abgelehnt, siehe [[STATE]]). Codex prüft die ganze Warteschlange `queue_s5.sh` auf
Betriebsfehler, bevor sie unbeaufsichtigt läuft.

## Als Nächstes

Befunde der Prüfung einarbeiten; ab ~08:35 Abschlussbericht.

## Verlauf dieser Sitzung

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

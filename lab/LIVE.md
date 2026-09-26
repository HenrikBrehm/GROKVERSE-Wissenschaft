---
tags: [lab/live]
---
# LIVE: Laborsitzung 5

- **Sitzungsstart:** 2026-09-26 05:49 Berlin (03:49Z, vom Runner)
- **Deadline:** 2026-09-26 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 06:23 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin), Wächter `--check` ok.

## Gerade

Keine Trainingsläufe (Queue-Start abgelehnt, siehe [[STATE]]). Theorie-Zyklus: Das kohärente Masken-Spektrum M0c
beschreibt den ersten Gradienten viel besser als M0. Als Nächstes: Herleitung sauber aufschreiben.

## Als Nächstes

Kurze Herleitung M0c aus einem linearisierten Modell (Notiz), dann weitere Literatur (Google Scholar) zu N6.

## Verlauf dieser Sitzung

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

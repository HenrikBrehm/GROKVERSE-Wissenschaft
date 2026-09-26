---
tags: [lab/live]
---
# LIVE: Laborsitzung 5

- **Sitzungsstart:** 2026-09-26 05:49 Berlin (03:49Z, vom Runner)
- **Deadline:** 2026-09-26 08:49 Berlin (06:49Z)
- **Zuletzt aktualisiert:** 06:11 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin), Wächter `--check` ok.

## Gerade

Keine Trainingsläufe (Queue-Start vom Klassifikator abgelehnt, siehe [[STATE]]). Denkarbeit: prüfen, ob sich das
Masken-Spektrum M0 aus einem einfachen Modell herleiten lässt und welche Variante die Frequenzen besser vorhersagt.

## Als Nächstes

Herleitung prüfen (EXP-015-README), ggf. Variante an den Explorationsseeds 0–9 post hoc testen.

## Verlauf dieser Sitzung

- 06:07 Literatur: Zhou/Zhang/Xu 2024 (Frequency Principle) sagen für EXP-018 das Gegenteil voraus (Verzögerung). Ein Repo mit festem Split zeigt: Auch die Init allein ändert die Frequenzwahl → der Split ist nicht die einzige Ursache.
- 06:04 Post hoc: Die natürliche Konzentration eines Zufallssplits sagt die Grokking-Zeit **nicht** voraus (ρ −0.40 / +0.15 / +0.02, alle n. s.).
- 06:01 Codex-Review EXP-018: 3 Befunde, alle übernommen (neue Kontrolle D, Zensur, Protokollprüfung). Tests 5/5 und 12/12.
- 05:56 [[experiments/EXP-018-split-speed/README|EXP-018]] vorab festgelegt: Beschleunigt ein konzentrierter Split das Grokking? Feste Testmenge, Seeds 20–29.

- 05:52 Queue-Start abgelehnt (Klassifikator). Nutzer muss die Freigabe erteilen, siehe [[STATE]] Blocker.
- 05:50 Stand gelesen, kein STOP, keine Python-Prozesse, Wächter: Fenster offen, 180 min.

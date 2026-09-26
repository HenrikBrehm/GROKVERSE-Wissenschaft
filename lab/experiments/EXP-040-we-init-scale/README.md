---
id: EXP-040
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-040: Fällt die Festlegung, wenn das Datensignal die Init-Amplitude von W_E einholt?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Gegenstück zu [[experiments/EXP-039-lr-clock/README|EXP-039]] · Grundlage
[[experiments/EXP-020-data-switch/README|EXP-020]], [[experiments/EXP-035-warmup-lockin/README|EXP-035]] · Idee [[NOVEL_DIRECTIONS]] N18.

## Anlass (Nachrechnung an gespeicherten Läufen, Sitzung 10, beschreibend)

EXP-035 speichert die Strecke ‖W_E − W_E,0‖ am Wechsel. Seed 30 mit Warmup: t = 100 (noch nicht festgelegt, Λ = 25.2) → 2.84;
t = 150 (festgelegt, Λ = 56.6) → 5.50; Seed 31: t = 50 → 0.70, t = 150 → 5.54. Die Init-Norm von W_E (ohne Gleichanteil)
ist 10.5, die Init-Amplitude **pro Frequenz** im Median 1.40 (flach, max 1.56). Verteilt sich die Bewegung auf etwa 5
Zielfrequenzen, sind das beim Festlegen ≈ 1.3–2.5 pro Frequenz, also gerade die Größe der Init-Amplitude. Deutung
(Spekulation): Die Wahl ist offen, solange das Datensignal unter dem Init-„Rauschen“ der Konkurrenzfrequenzen liegt, und fällt,
wenn es dieses einholt. Unter Adam wächst die Strecke ≈ proportional zu Λ (Adam normiert den Gradienten; Smoke EXP-039:
c = 2, t = 30, Λ = 60 → W_E 4.90), daher erschiene das als Λ-Uhr. Das würde auch N15 (Konflikt gibt die Wahl an die Init zurück)
und He et al. 2026 (Frequenz-Lotterie über den Init-Betrag) zusammenbringen.

## Versuch (vorab festgelegt 2026-09-26, Sitzung 10, vor jedem EXP-040-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Verschiebt eine Skalierung der W_E-Init um s das Festlegungsfenster in Λ um den Faktor s? |
| **H40 (Amplitudenschwelle)** | s = 0.5 → Fenster (12, 25] Schritte; s = 2 → (50, 100] (Λ-Fenster (25s, 50s]) |
| **Alternative (reine Λ-Uhr / Schrittuhr)** | Fenster bleibt (25, 50] für beide s (Init-Skala ohne Einfluss) |
| **Eingriff** | `freq_ban.py --we-init-scale s` (neu): W_E × s direkt nach der Init (Prüfsumme = unveränderte Init), sonst EXP-020-Protokoll mit konstanter lr |
| **Referenzen** | eigene Läufe „nur G“ (2000) und „nur F“ (bis 8000, Stop gen + 2000) **mit derselben Skalierung** (die EXP-020-Referenzen haben die unskalierte Init) |
| **Gitter** | s = 0.5: t ∈ {10, 12, 25, 50}; s = 2: t ∈ {25, 50, 100, 150} |
| **Seeds** | 30, 32, 34 (EXP-020 (25, 50], monoton), 31 falls Budget |
| **Urteil** | Wie EXP-039 Nachtrag a (Code importiert): Zelle *H40* nur bei genau dem vorhergesagten Intervall, *unverändert* nur bei (25, 50], sonst *unklar*; vollständige, aber nicht monotone/späte/Endpunkt-verfehlende Zellen = *unklar*; Einheit = Seed mit beiden s; ≥ 3 vollständige Seeds; alle *H40* → ***H40 gestützt***; alle *unverändert* → ***Init-Skala ohne Einfluss***; sonst ***unklar*** |
| **Sekundär (beschreibend)** | frühe Spektren (5 … 200): Zeitpunkt, an dem die Amplitude der Zielfrequenzen von F die mittlere Init-Amplitude übersteigt, gegen das Festlegungsintervall; Strecke am Wechsel; gen_F je s |
| **Was dagegen spräche** | Fenster unverändert, oder Verschiebung in die Gegenrichtung |
| **Grenzen** | s ändert auch das Verhältnis W_E zu W_pos am Eingang und damit die Aufmerksamkeitsmuster; s = 2 kann das Grokking verlangsamen (gen_F zensiert → Zelle *unklar*); die Skalierungsgrößen sind grob; ein Transformer |
| **Budget** | 12 Läufe je Seed ≈ 60 min; 3 Seeds ≈ 3 h; Queue beginnt mit Selbsttest und Smoke (Prüfung: Schritt-0-Spektrum = s² × unskalierte Init) |

**Verhältnis zu EXP-039:** Beide zusammen trennen drei Erklärungen. Λ-Uhr aus reiner Optimierer-Zeit: EXP-039 *Λ*, EXP-040
*unverändert*. Amplitudenschwelle: EXP-039 *Λ* **und** EXP-040 *H40*. Schrittuhr (z. B. Adams β2-Horizont): EXP-039 *Schritt*.

**Neuheit:** vorläufig nicht gefunden (Suche 17:44, siehe EXP-039; gezielte Suche zu Init-Skala und Festlegungszeit nachholen).

## Status

Vorab festgelegt, Code geschrieben, **ungetestet** (Fenster geschlossen): Selbsttest und Smoke laufen als erste Schritte der
Queue (fail-closed). In `queue_s10.sh` nach EXP-039.

## Reproduktion

```
sh lab/experiments/EXP-040-we-init-scale/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-040-we-init-scale/analyze.py
```

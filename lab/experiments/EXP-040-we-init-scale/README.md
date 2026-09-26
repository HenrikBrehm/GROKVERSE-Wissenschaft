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

## Nachtrag a (2026-09-26, Sitzung 10, nach Codex-Review `codex_review_2026-09-26.txt`, vor jedem EXP-040-Lauf)

Codex: needs-attention, drei hohe Einwände, alle berechtigt.
1. **Der Eingriff isoliert die Frequenz-Amplitude nicht** (W_E × s skaliert auch die „=“-Zeile und den Gleichanteil und ändert
   ohne LayerNorm Aufmerksamkeit, Aktivierungen und Gradienten). **Übernommen:** Skaliert wird nur noch der Nicht-Gleichanteil
   der Zahlenzeilen, W_E[:p] = Mittel + s · (W_E[:p] − Mittel); „=“-Zeile und Mittel bleiben. Der Rest des Einwands bleibt:
   Das Urteil heißt nur noch ***H40-Muster gestützt (Assoziation mit der W_E-Init-Skala)***, kein Mechanismus. Nicht übernommen:
   Kontrollen mit gleicher Norm/gemischtem Spektrum (das Init-Spektrum ist ohnehin flach, max/Median = 1.1).
2. **Die Überschlagsrechnung im Anlass vergleicht Unvergleichbares** (Frobenius-Strecke des ganzen W_E gegen
   Pro-Frequenz-Amplitude, Annahme „verteilt auf 5 Ziele“ ungeprüft). **Übernommen:** Der Anlass ist nur Motivation; die
   Vorhersage hängt nicht an der Kalibrierung, nur an der Proportionalität (Fenster in Λ × s). Neu: `freq_ban.py` speichert bei
   `--spectra-at` die W_E[:p]-Schnappschüsse (Schritt 0 und die Zusatzschritte), und `analyze.py` berichtet beschreibend die
   zielgenaue Strecke |c_k(t) − c_k(0)| der F-Ziele relativ zur Median-Init-Amplitude (gilt automatisch auch für EXP-036/039).
3. **Die beiden Skalen eines Seeds wurden nicht auf gleiche Init/Konfiguration geprüft.** **Übernommen:** Ein Seed zählt nur,
   wenn Init-Prüfsumme, Optimierer-Konfiguration, d_model und Split-/Test-Hashes in beiden Skalen gleich sind.
Code nach dem Nachtrag **ungetestet** (Fenster geschlossen); Selbsttest und Smoke stehen fail-closed am Anfang der Queue.

## Nachtrag b (2026-09-26 18:04 Berlin, Sitzung 10, vor jedem EXP-039- und EXP-040-Lauf): beschreibender Invarianztest

Welche Größe ist beim Festlegen über die Eingriffe hinweg konstant? Für jede vollständige, monotone Zelle von EXP-039 (c) und
EXP-040 (s) mit endlichem Intervall: Λ(hi) = c · hi bzw. hi, und R(hi) = mittlere zielgenaue Strecke der F-Ziele
|c_k(hi) − c_k(0)| geteilt durch die Median-Init-Amplitude |c_j(0)| (bei EXP-040 der skalierten Init), gemessen im Lauf „nur F“
derselben Zelle (bis zum Wechsel identisch mit den Wechselläufen). **Erwartung unter H40:** Variationskoeffizient von R(hi)
kleiner als der von Λ(hi). Unter einer reinen Λ-Uhr umgekehrt (Λ konstant, R ∝ 1/s). Nur beschreibend, kein Urteil; mindestens
4 Zellen. Grenze: hi ist ein Gitterpunkt (obere Intervallgrenze), nicht der wahre Zeitpunkt; beide Größen werden an derselben
Stelle gemessen. Code: `invariance()` in `analyze.py` (Selbsttest-Fall ergänzt, ungetestet bis zum nächsten Fenster).

## Nachtrag c (2026-09-26 18:18 Berlin, Sitzung 10, vor jedem EXP-039/040-Lauf): quantitative Fassung von H40 (beschreibend)

Mit der gemessenen Strecke ‖ΔW_E‖ ≈ 0.11 · Λ (EXP-039 Nachtrag b) und der Init-Amplitude ≈ 1.4 pro Frequenz: Liegt der Anteil f
der Streckenenergie auf den 5 Zielfrequenzen, ist die Zielamplitude ≈ 0.11 · Λ · √(f/5), und die Schwelle „Zielamplitude = Init-
Amplitude“ fällt bei Λ* ≈ 28.5 / √f (f = 1 → 28, 0.5 → 40, 0.3 → 52, 0.1 → 90). Das beobachtete Fenster Λ ∈ (25, 50] passt nur zu
f ≳ 0.3. **Zahl-Vorhersage (beschreibend, kein Urteil):** In der Mehrheit der Zellen von Nachtrag b liegt R(hi) zwischen 0.5 und 2
(`n_R_hi_in_0.5_2`). Liegt R(hi) regelmäßig weit darunter (< 0.5), holt das Signal die Init beim Festlegen gar nicht ein, und H40 in
dieser Form ist falsch, selbst wenn das H40-Muster der Verschiebung auftritt.

## Status

Vorab festgelegt, Code geschrieben, **ungetestet** (Fenster geschlossen): Selbsttest und Smoke laufen als erste Schritte der
Queue (fail-closed). In `queue_s10.sh` nach EXP-039.

## Reproduktion

```
sh lab/experiments/EXP-040-we-init-scale/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-040-we-init-scale/analyze.py
```

---
id: EXP-042
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-042: Verzögert ein stärker konzentrierter zweiter Split die Festlegung? (H42: Vorsprung gegen Split-Neigung)

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Grundlage [[experiments/EXP-020-data-switch/README|EXP-020]] · Idee [[NOVEL_DIRECTIONS]] N22 ·
verwandt [[experiments/EXP-039-lr-clock/README|EXP-039]], [[experiments/EXP-040-we-init-scale/README|EXP-040]].

## Anlass

Jede Frequenzmenge löst dieselbe Aufgabe; der Split neigt die Wahl nur (EXP-015/016). **H42:** Die Wahl ist festgelegt, sobald der
Amplitudenvorsprung der F-Frequenzen größer ist als der Vorteil, den die Neigung des neuen Splits G den G-Frequenzen verschafft.
Dann muss ein **stärker konzentriertes G** einen größeren Vorsprung überwinden können, und die Festlegung fällt später. Eine reine
Uhr (Λ, Strecke oder Schrittzahl) sagt dagegen dasselbe Fenster (25, 50] wie in EXP-020 voraus, unabhängig von G.

## Versuch (vorab festgelegt 2026-09-26 18:30 Berlin, Sitzung 10, vor jedem EXP-042-Lauf)

| Punkt | Festlegung |
|---|---|
| **Eingriff** | G-Split mit eps_G = 8 (primär) bzw. 1 (sekundär) statt 2; gleiche Ziele, gleiche Testmenge, gleiche Zufallsschlüssel und Wellenphasen; F bitgleich mit EXP-020 (`make_splits.py`, fail-closed geprüft). Zielanteil von M0(G): eps 1 ≈ 0.115, eps 2 ≈ 0.18, eps 8 ≈ 0.36 |
| **Protokoll** | EXP-020: t Schritte F, dann 2000 Schritte G_eps; K = Top-5 von W_E am Ende; d = \|K ∩ F\| − \|K ∩ G\|; t = 0 eigener Lauf „nur G_eps“; t = ∞ = EXP-020-Lauf „nur F“ (gleiche Init, gleiches F) |
| **Gitter** | eps 8: t ∈ {25, 50, 100, 150}; eps 1: t ∈ {10, 25, 50} |
| **Seeds** | 30, 31, 32, 34 (EXP-020-Intervall (25, 50], monoton) |
| **Zelle** | eps 8: *später* wenn lo ≥ 50, *gleich* wenn (25, 50], sonst *unklar*. eps 1: *früher* wenn hi ≤ 25, *gleich* wenn (25, 50], sonst *unklar*. Vollständige, aber nicht monotone, späte oder Endpunkt-verfehlende Zellen = *unklar* |
| **Urteil (nur eps 8)** | ≥ 3 vollständige Seeds; alle *später* → ***H42 gestützt***; alle *gleich* → ***Neigung ohne Einfluss auf den Zeitpunkt***; sonst ***unklar***. eps 1 nur beschreibend |
| **Was gegen H42 spräche** | eps 8 gleich (25, 50] in allen Seeds |
| **Grenzen** | eps ändert auch die Überlappung von F und G (eps 8: ≈ 2200 statt ≈ 2780 gemeinsame Paare) und damit, wie viel „alte“ Information G enthält; stärkere G-Konzentration kann die Endpunkte (d(0) < 0) verbessern und so die Auswertbarkeit ändern; eps 1 steuert G womöglich kaum (Zielanteil nahe am Zufall ≈ 0.09), dann *unklar* |
| **Budget** | eps 8: 5 Läufe je Seed, eps 1: 4, je ≈ 4.5 min; zusammen ≈ 2.7 h. Queue beginnt mit dem Selbsttest (fail-closed) |

**Neuheit:** vorläufig nicht gefunden (Suche 18:26, siehe N22; nächstverwandt AGF, Kunin et al. 2025).

## Nachtrag a (18:38 Berlin, nach Codex-Review `codex_review_2026-09-26.txt`, vor jedem EXP-042-Lauf): gilt allein, wo abweichend

Codex: needs-attention, 2 × hoch, 2 × mittel.
1. **(hoch) Das Ergebnis *später* trennt H42 nicht von stärkerer Verdrängung** (eps 8 verringert auch die F/G-Überlappung von
   ≈ 2770 auf ≈ 2200 Paare und verdoppelt die Zielneigung). **Teilweise übernommen:** Der Versuch trennt nur noch „der Zeitpunkt hängt
   vom zweiten Split ab“ gegen „reiner, vom zweiten Split unabhängiger Takt (Λ, Strecke, Schritte)“. Urteil neu: alle *später* →
   ***Zeitpunkt hängt vom zweiten Split ab (H42-Richtung; Neigung und Überlappung nicht getrennt)***. Einen Mechanismus (Vorsprung
   gegen Neigung) belegt das nicht. Nicht übernommen: faktorielles Design Überlappung × Neigung (Folgeversuch, falls *später*).
2. **(hoch) Referenz „nur F“ aus älteren EXP-020-Läufen** (andere Commits, nicht versioniert). **Übernommen:** eigene Läufe „nur F“ je
   Seed in `eps8/raw` (für beide eps), zugleich eine beschreibende Reproduzierbarkeitsprüfung gegen EXP-020.
3. **(mittel) Gleichstand als „kein Einfluss“.** **Übernommen:** alle *gleich* → ***keine Verschiebung bei dieser Gitterauflösung***.
4. **(mittel) Kein Schutz gegen gleichzeitige Jobs.** **Übernommen:** Die Queue wartet zu Beginn, bis kein `guarded_run.py` mehr läuft.
Budget neu ≈ 3.1 h. Code nach dem Nachtrag ungetestet (Selbsttest am Queue-Anfang).

## Status

Vorab festgelegt, Splits erzeugt (reine Rechnung), Code **ungetestet** (Fenster geschlossen). Noch in keiner Queue.

## Reproduktion

```
python lab/experiments/EXP-042-bias-strength/make_splits.py        # reine Rechnung, prüft F/Test gegen EXP-020
sh lab/experiments/EXP-042-bias-strength/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-042-bias-strength/analyze.py
```

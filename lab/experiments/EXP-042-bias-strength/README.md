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

## Nachtrag b (Sitzung 15, 2026-09-26 22:45 Berlin (gemessen), vor jedem EXP-042-Lauf; nur beschreibend, das Urteil aus Nachtrag a bleibt)

**Anlass (post hoc an EXP-020/037, [[experiments/EXP-020-data-switch/README|EXP-020]] Nachtrag Sitzung 15):** Ein reiner Takt mit linearer
Überlagerung in einem frühen Integrationsfenster (jeder der ersten T* ≈ 69 Schritte zählt gleich) gibt die EXP-020-Persistenz wieder und
sagt die Verschränkungsarme von EXP-037 ohne Anpassung voraus. Unter genau diesem **reinen Takt** verschiebt sich die Top-5-Kreuzung
trotzdem mit der Stärke von G (`EXP-020-data-switch/posthoc_clock_crossover.py`, aus den Split-Dateien): eps 2 → t ≈ 32–40 (beobachtet
(25, 50] in 5/5), **eps 8 → t ≈ 46–54** (je nach Form des Zugs: zentriertes M0 51–54, log M0 46–48), eps 1 → t ≈ 14–24.
**Folge:** Die Aussage in „Anlass“ („Eine reine Uhr sagt dasselbe Fenster (25, 50] voraus, unabhängig von G“) stimmt für das Top-5-Maß
nicht. Ein Ergebnis *später* bei eps 8 trennt H42 nicht von einem reinen Takt; die Kreuzung liegt unter beiden Lesarten nahe am Gitterpunkt 50.

**Trennende Größe (vorab festgelegt, beschreibend):** normierte Persistenz π je Seed (`pi_window.py`, Normierung mit den eigenen reinen
Läufen bei Schritt 2000). Bei linearer Überlagerung gilt π(t) = t/T*, unabhängig von G.
- **C (fester Takt):** Mittel über Seeds weicht in jeder Zelle höchstens 0.12 von min(1, t/69) ab.
- **O (Stärke von G verschiebt das Fenster):** eps 8 bei t = 25 oder 50 mindestens 0.15 **unter** der Kurve; eps 1 bei t = 10 oder 25 mindestens 0.15 **darüber**.
- Sonst: weder C noch O. Zusätzlich π bei Schritt 250 gegen π am Ende (Erwartung aus EXP-020: Mischung ab Schritt 250 eingefroren, |Δ| ≤ 0.1).
Bereits gesehene Daten, die diese Festlegung beeinflusst haben: EXP-020 (Seeds 30–34, Kurve und T*), EXP-037 (Seeds 30–32). Code ungetestet
(Selbsttest mit EXP-020-Regression ab 03:00, nach dem EXP-042-Hauptlauf: `python lab/tools/guarded_run.py -- python lab/experiments/EXP-042-bias-strength/pi_window.py`).

## Nachtrag c (Sitzung 15, nach unabhängiger Prüfung durch einen Claude-Subagenten, vor jedem EXP-042-Lauf)

Übernommen: (1) Lesart C/O nur mit ≥ 3 Seeds je Zelle (sonst „nicht auswertbar“); fehlender Spektralschritt markiert den Seed als defekt
statt das Programm abzubrechen. (2) **Grenzen der Lesart:** π = t/T* unabhängig von G gilt exakt nur bei additiver Überlagerung im
Log-Spektrum; eine nichtlineare (sättigende) Abbildung kann eine O-Lesart ohne G-abhängiges Fenster erzeugen. Mit 4 Seeds (SD je Seed
≈ 0.07–0.10) erkennt die Lesart nur große Verschiebungen (≳ 0.15–0.2; Trefferquote bei 0.15 ≈ 50 %); C heißt deshalb nur „keine
Verschiebung größer ≈ 0.2“. (3) Die Einfrierprüfung π(250) gegen π(Ende) wird nur berichtet; schon an EXP-020 liegt sie an der Grenze.
Die Schwellen aus Nachtrag b bleiben unverändert.

## Status

Vorab festgelegt, Splits erzeugt (reine Rechnung), Code **ungetestet** (Fenster geschlossen). Noch in keiner Queue.

## Reproduktion

```
python lab/experiments/EXP-042-bias-strength/make_splits.py        # reine Rechnung, prüft F/Test gegen EXP-020
sh lab/experiments/EXP-042-bias-strength/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-042-bias-strength/analyze.py
```

---
id: EXP-054
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]", "[[experiments/EXP-020-data-switch/README|EXP-020]]", "[[experiments/EXP-036-init-conflict/README|EXP-036]]", "[[experiments/EXP-042-bias-strength/README|EXP-042]]", "[[experiments/EXP-041-imprint/README|EXP-041]]", "[[BEFUND-festlegung]]"]
---
# EXP-054: Integrationsfenster der Frequenzwahl an unberührten Inits (N30, reine Auswertung)

Zurück zu [[LAB]] · [[FINDINGS]] (Paket B, K4 und P3-Maß) · Idee N30 in [[NOVEL_DIRECTIONS]] · Herleitung [[JOURNAL]] Sitzung 15, Zyklen 1–3.

**Eigene Läufe: keine.** Der Versuch wertet die Läufe von [[experiments/EXP-036-init-conflict/README|EXP-036]] aus (CPU-Nachtqueue). Sie
nutzen die EXP-020-Splits mit **neuen Inits** (130–134, 230, 231) und speichern dichte Spektren (5 … 200). Er wurde als eigener Versuch
angelegt statt als sechster Nachtrag zu EXP-036 (Regel 15b). Die EXP-036-Urteile bleiben unberührt.

**Bezug zu [[FINDINGS]]:** Paket B, K4 (frühe Festlegung) und die Wahl des P3-Maßes (π statt Top-5, Budget B).

## Vorab festgelegt (Sitzung 15, 2026-09-26 22:53 Berlin, vor jedem EXP-036-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Überträgt sich das post hoc an EXP-020/037 gefundene Bild (frühes Fenster von ≈ 69 Schritten; F/G-Mischung spätestens nach 250 Schritten gesetzt) auf neue Inits? |
| **Maß** | π wie in EXP-020 (`posthoc_beta_persistence.py`): Log-log-Steigung der W_E-Leistung auf M0 von F bzw. G, D = β_F − β_G, π = (D_Wechsel − D_nurG)/(D_nurF − D_nurG), je Paar (Split, Init) |
| **A: Fenster übertragbar** | Mittel von π_Ende über die gültigen Paare liegt bei t = 10 / 25 / 50 jeweils höchstens 0.12 neben min(1, t/69) = 0.145 / 0.362 / 0.725. T* = 69 wird **nicht** neu angepasst |
| **B: früh gesetzt** | Je Wechsellauf der Setzschritt: erster gespeicherter Schritt s > t, ab dem π(s′) für alle späteren s′ ≤ 2000 höchstens 0.1 von π_Ende abweicht (Normierung mit den reinen Läufen derselben Init beim selben Schritt, nur Schritte mit D_F − D_G ≥ 1). Median über t = 25 und 50: ≤ 150 → *früh gesetzt*; > 200 → *später gesetzt*; sonst *dazwischen* |
| **Gültig** | Lader von EXP-036 (`conflict_freqs.load_run`, fail-closed); ≥ 5 gültige Paare, sonst *nicht auswertbar* |
| **Was gegen N30 spräche** | A verfehlt (das Fenster hängt an der Init oder war an EXP-020 überangepasst) oder B *später gesetzt* (die Mischung bewegt sich noch lange nach dem angenommenen Fenster) |
| **Bereits gesehene Daten** | EXP-020 (Splits und Inits 30–34: Kurve, T*), EXP-037 (Seeds 30–32). Splits von EXP-036 = EXP-020-Splits (gesehen); die Inits sind neu |
| **Grenzen** | Nur beschreibend; π sieht gemeinsame affine Abbildungen des Log-Spektrums nicht (Gegenprüfung Sitzung 15); 7 Paare, davon 2 mit wiederholtem Split; frühe π mit kleinem Nenner sind verrauscht |

Verwandte, in derselben Sitzung vor den Läufen festgelegte Lesarten: [[experiments/EXP-042-bias-strength/README|EXP-042]] Nachtrag b/c
(π trennt festen Takt von H42), [[experiments/EXP-041-imprint/README|EXP-041]] Nachtrag b (drei Lesarten für P41b).

**Neuheit:** Suche 2026-09-26 22:48 (siehe N30): ein additives Integrationsfenster für die Frequenzwahl nicht gefunden (vorläufig);
nächstverwandt „The Order Is The Message“ (https://arxiv.org/abs/2603.25047).

## Status

Vorbereitet, **ungetestet** (Fenster zu). Läuft nach EXP-036 in der CPU-Nacht.

## Reproduktion

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-054-window-oos/n30_window.py --selftest
python lab/tools/guarded_run.py -- python lab/experiments/EXP-054-window-oos/n30_window.py     # nach EXP-036
```

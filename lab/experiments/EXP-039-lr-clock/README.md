---
id: EXP-039
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-039: Läuft die Festlegung der Frequenzwahl auf einer „Lernraten-Uhr“?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · Grundlage [[experiments/EXP-020-data-switch/README|EXP-020]],
[[experiments/EXP-035-warmup-lockin/README|EXP-035]] · Idee [[NOVEL_DIRECTIONS]] N17.

## Anlass

EXP-020: Ohne Warmup fällt die Festlegung in 5/5 Seeds in (25, 50] Schritte. EXP-035 Seed 30 (ein Seed, kein Urteil): mit linearem
Warmup über 200 Schritte in (100, 150], genau dort, wo die aufsummierte Lernrate Λ(n) = n(n+1)/400 die Werte 25 bzw. 50
erreicht (Λ(100) = 25.2, Λ(141) = 50.1). Wenn die Festlegung an Λ hängt und nicht an der Schrittzahl, muss auch eine
**gleichmäßige** Skalierung der Lernrate (anderer Eingriff als Warmup, andere Form des Plans) das Fenster vorhersagbar verschieben.

## Versuch (vorab festgelegt 2026-09-26, Sitzung 10, vor jedem EXP-039-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Verschiebt eine konstante Lernraten-Skalierung c in der F-Phase das Festlegungsfenster auf Λ = c · t ∈ (25, 50]? |
| **H39 (Λ-Uhr)** | c = 2: Fenster (12.5, 25] → d(10) ≤ 0 < d(25). c = 0.5: Fenster (50, 100] → d(50) ≤ 0 < d(100) |
| **Alternative (Schrittuhr)** | Fenster bleibt (25, 50]: c = 2 → d(25) ≤ 0; c = 0.5 → d(50) > 0 |
| **Eingriff** | `freq_ban.py --lr-scale c` (neu): lr = c · 1e-3 in den Schritten 1 … min(Wechsel, 250) auf F, danach volle Lernrate (auch nach dem Wechsel: G-Phase in allen Armen gleich, 2000 Schritte, lr 1e-3) |
| **Protokoll** | EXP-020: Splits F/G je Seed, 2000 G-Schritte nach dem Wechsel, K = Top-5 von W_E am Ende, d(t) = \|K ∩ F\| − \|K ∩ G\|; t = 0 = EXP-020-Lauf „nur G“ (identisch), t = ∞ = „nur F“ mit derselben Skalierung (bis 8000, Stop gen + 2000, K bei 2000) |
| **Gitter** | c = 2: t ∈ {10, 25, 50}; c = 0.5: t ∈ {50, 100, 150}; je plus „nur F“. Diskriminierend sind (c = 2, t = 25) und (c = 0.5, t = 50); die anderen Punkte sind Anker, die beide Hypothesen gleich vorhersagen |
| **Seeds** | 30, 32, 34 (EXP-020-Intervall (25, 50], monoton; 33 war nicht monoton), 31 falls Budget |
| **Einheit, Urteil** | Seed × Skalierung. Zelle auswertbar: alle Läufe gültig (EXP-020-Lader, Metadaten, gleiche Init-Prüfsumme), d(0) < 0 < d(∞), d monoton über das Gitter, gen_F beobachtet und Kreuzung davor. Zelle = *Λ* wenn das Intervall der H39-Vorhersage entspricht, *Schritt* wenn der Alternative, sonst *unklar*. ≥ 4 auswertbare Zellen nötig; alle *Λ* → ***Λ-Uhr gestützt***; alle *Schritt* → ***Schrittuhr***; sonst ***unklar*** |
| **Sekundär (beschreibend)** | Parameterstrecke ‖θ − θ₀‖ und ‖W_E − W_E,0‖ am Wechsel (ist die Strecke bei Festlegung über c gleich?); gen_F je c |
| **Was dagegen spräche** | Fenster unverändert (Schrittuhr) oder Verschiebung in die falsche Richtung/Größe |
| **Grenzen** | c ändert auch das Verhältnis Lernrate/Weight Decay und Adams effektive Schrittweite ist nicht genau lr; ein Transformer, eine Aufgabe; Seeds 30, 32 kennen wir aus EXP-020/035 (die Skalierungsläufe sind neu) |
| **Budget** | 8 Läufe je Seed à 4–7 min ≈ 40 min; 3 Seeds ≈ 2 h, ein Job gleichzeitig |

**Neuheit (Suche 2026-09-26 17:44, WebSearch):** „critical period early training learning rate scaling intrinsic time cumulative
learning rate feature commitment“, „grokking modular addition learning rate early training frequency selection determined first
steps“. Nächstverwandt: He, Wang, Chen & Yang 2026 (https://arxiv.org/abs/2602.16849): Frequenzwettbewerb als Lotterie über
Init-Spektrum und Phasenausrichtung (zweischichtiges Netz; laut Abstract keine Lernraten- oder Datenwechsel-Abhängigkeit des
Zeitpunkts); Tan, Gai & Zhang 2026 (https://arxiv.org/abs/2606.05863): zwei Uhren im Grokking (Loss logarithmisch,
Repräsentation polynomiell), nicht die Festlegung der Frequenzwahl; Achille et al. 2019 (kritische Perioden); „intrinsische
Zeit“ = aufsummierte Lernrate in Arbeiten zu Skalierungsgesetzen (z. B. https://arxiv.org/abs/2602.06797). Die konkrete Frage
„fällt die Frequenzwahl bei fester aufsummierter Lernrate?“: **nicht gefunden** (vorläufig; Scholar/OpenReview nicht gezielt).

## Nachtrag a (2026-09-26 17:53 Berlin, nach Codex-Review `codex_review_2026-09-26.txt`, vor jedem EXP-039-Lauf): gilt allein, wo abweichend

Codex: needs-attention, drei hohe Einwände.
1. **Gitter nicht intervallsicher** (c = 2: eine Kreuzung bei Schritt 11–12 hat Λ ≤ 24 und wäre fälschlich *Λ*; c = 0.5: ohne
   t = 25 wäre jede Kreuzung in (0, 50] *Schritt*). **Übernommen:** Gitter c = 2: t ∈ {10, **12**, 25, 50}; c = 0.5:
   t ∈ {**25**, 50, 100, 150}. *Λ* nur bei Intervall (12, 25] bzw. (50, 100] (in ganzen Schritten genau Λ ∈ (25, 50]);
   *Schritt* nur bei (25, 50]; sonst *unklar*.
2. **Ergebnisabhängige Ausschlüsse** (nicht monotone oder späte Zellen fielen heraus). **Übernommen:** Vollständige Zellen
   zählen immer; nicht monoton, Kreuzung nach gen_F oder verfehlte Endpunkte → *unklar*. Nur fehlende/defekte Läufe oder
   falsche Metadaten machen eine Zelle unvollständig. **Einheit = Seed mit beiden Zellen:** *Λ* nur wenn beide *Λ*, *Schritt*
   nur wenn beide *Schritt*. **Urteil:** ≥ 3 vollständige Seeds; alle *Λ* → ***Λ-Uhr gestützt (für AdamW mit diesem Plan)***;
   alle *Schritt* → ***Schrittuhr***; sonst ***unklar***.
3. **Lernraten-Skalierung in AdamW isoliert Λ nicht** (entkoppelter Weight Decay skaliert mit, Momente/Bias-Korrektur haben
   bei gleichem Λ verschiedenes Alter). **Teilweise übernommen:** Die Aussage wird auf „AdamW mit diesem Plan“ beschränkt, ein
   Mechanismus wird nicht behauptet. **Nicht übernommen:** eigene Weight-Decay-Kontrollen. Grund: Der entkoppelte Decay
   schrumpft W_E bei lr · wd = 1e-3 bis Λ = 50 nur um ≈ 5 % und wirkt als gleichmäßige Multiplikation auf alle Frequenzen,
   ändert also die Rangfolge im W_E-Spektrum nicht direkt. Die Schrittuhr-Alternative deckt dagegen die Momente ab:
   β2 = 0.98 hat einen Horizont von 50 Schritten, β1 = 0.9 von 10; hinge die Festlegung an Adams Zeitkonstanten, bliebe
   das Fenster in Schritten gleich (*Schritt*).
Budget neu: 10 Läufe je Seed (≈ 50 min), 3 Seeds ≈ 2.5 h. Smoke (`--lr-scale 2`, Wechsel bei 30) im Fenster gelaufen
(17:51, Strecke am Wechsel W_E 4.90, alle 15.39), Selbsttest der Auswertung nach den Änderungen ok (17:52).

## Nachtrag b (2026-09-26 18:17 Berlin, Sitzung 10, vor jedem EXP-039-Lauf): Vorbehalt Strecke gegen Λ (nur Einordnung)

Aus gespeicherten EXP-035-Läufen (Warmup) und dem EXP-039-Smoke: ‖W_E − W_E,0‖ / Λ = 0.119, 0.114, 0.108, 0.112, 0.097 bei
Λ = 0.3, 1.6, 6.4, 25, 57 (Seed 30; Seed 31 gleich), danach sublinear (0.067 bei Λ = 150); mit c = 2 bei Λ = 60 nur 0.082.
Das Maximum für vorzeichenkohärente Adam-Schritte ist lr · √(114 · 128) = 0.121: Die frühen Schritte sind zu ≈ 90 % kohärent.
Folgerung: Im Festlegungsbereich laufen Λ-Uhr und Streckenuhr nahezu gleich, bei c = 2 aber ≈ 16 % Strecke pro Λ weniger.
Hängt die Festlegung an der Strecke, kann das c = 2-Fenster knapp über t = 25 rutschen und die Zelle wird *unklar*, nicht
*Schritt*. **Regeln und Urteil bleiben unverändert**; die Strecke am Wechsel wird ohnehin beschreibend berichtet.

## Status

Vorab festgelegt (mit Nachtrag a), Code und Smoke geprüft, nicht ausgeführt. Läuft in `queue_s10.sh` nach EXP-036.

## Reproduktion

```
sh lab/experiments/EXP-039-lr-clock/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-039-lr-clock/analyze.py
```

## Bereits gesehene Daten (Nachtrag Sitzung 14, vor jedem EXP-039-Lauf; Urteilsregeln unverändert)

Post hoc an EXP-035 (Seeds 30/31, Warmup) gesehen: Ein kontinuierliches Persistenzmaß π ([[experiments/EXP-035-warmup-lockin/README|EXP-035]],
letzter Abschnitt) folgt früh der aufsummierten Lernrate Λ und nicht der Schrittzahl, hält später aber stärker fest als Λ allein vorhersagt.
Das beeinflusst keine Festlegung dieses Versuchs. π wird nach den Läufen zusätzlich **nur beschreibend** berechnet (gleiche Spektren).

*Korrektur (Sitzung 14):* Nach Prüfung ist die EXP-035-Sicht nicht „Λ früh getroffen“, sondern: Warmup verzögert, keine der beiden Uhren
passt an den trennscharfen Punkten. Beeinflusst die Festlegungen hier nicht.

## Nachtrag (Sitzung 14, 21:59 Berlin, **vor jedem EXP-039-Lauf**): eingefrorene, nur beschreibende π-Vorhersagen dreier Uhren

`predict_pi.py` → `predictions_pi.json` (reine Rechnung auf gespeicherten Post-hoc-Ergebnissen). Effektive Zeit τ(t) = Σ_s (lr_s/lr₀)^γ der
F-Phase, π(t) = EXP-020-Kurve bei τ (stückweise linear durch 0, 10, 25, 50, 150). γ = 0 Schrittuhr, γ = 1 Λ-Uhr, γ = 0.65 angepasst an die
gespeicherten EXP-035-Warmup-Läufe (RMSE dort 0.34 / 0.12 / 0.08; 1–2 Seeds, gesehene Daten).

| Zelle | Schrittuhr | Λ-Uhr | γ = 0.65 |
|---|---|---|---|
| c = 2, t = 10 | 0.15 | 0.30 | 0.24 |
| c = 2, t = 25 | 0.38 | **0.72** | 0.57 |
| c = 2, t = 50 | 0.72 | 0.86 | 0.80 |
| c = 0.5, t = 50 | **0.72** | 0.38 | 0.47 |
| c = 0.5, t = 100 | 0.86 | 0.72 | 0.76 |
| c = 0.5, t = 150 | 1.00 | 0.79 | 0.85 |

Auswertung nach den Läufen: π je Seed (Normierung mit den reinen EXP-018-Läufen des Seeds), RMSE jedes Modells über alle Zellen. **Kein Urteil**,
das vorab festgelegte Urteil von EXP-039 (Dominanzmaß d) bleibt allein maßgeblich. Grenzen: grobe Kurve zwischen 50 und 150; γ aus 1–2 Seeds;
bei c = 2 ändert sich auch das Verhältnis lr/Weight Decay.

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
| **Protokoll** | EXP-020: Splits F/G je Seed, 2000 G-Schritte nach dem Wechsel, K = Top-5 von W_E am Ende, d(t) = |K ∩ F| − |K ∩ G|; t = 0 = EXP-020-Lauf „nur G“ (identisch), t = ∞ = „nur F“ mit derselben Skalierung (bis 8000, Stop gen + 2000, K bei 2000) |
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

## Status

Vorab festgelegt, Code folgt (`--lr-scale`), nicht ausgeführt.

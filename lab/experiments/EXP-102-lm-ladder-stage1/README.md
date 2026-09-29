---
id: EXP-102
status: laufend
datum: 2026-09-28
tags: [exp/laufend]
---
# EXP-102 (Regel 20e, Sprachmodell-Leiter Stufe 1): Hält K2, wenn die Aufgabe als Text formuliert ist? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2) · Regel 20e (ab ≈ Fr 02.10., nach L0) · Vorgänger [[experiments/EXP-100-set-vs-order/README|EXP-100]] (Minibatch) · Einordnung: Fu et al. 2026 (arXiv 2604.20817), Zhou/Fu/Sharan/Jia 2024, Engels et al. 2024, Kantamneni & Tegmark 2025, Karkada et al. 2026 (Zitate vor Verwendung am Abstract prüfen)

**Stand:** Entwurf (Sitzung 43, 2026-09-28), nur Plan. Noch kein Code. Startet erst nach L0 (Regel 20e).

## Frage

Die Leiter geht in kleinen Schritten vom Grokking-Setup zu einem Sprachmodell und nutzt dabei **eine gemeinsame Messgröße**: Δ_pow auf den Embeddings der Zahl-Tokens (P1-Definition, eigene gegen fremde Ziele). Stufe 1 ändert nur das **Format**, nicht die Daten: Die Aufgabe (a + b) mod 113 mit denselben konstruierten Splits F/G wird als Tokenfolge geschrieben. Die erste Stufe, auf der K2 bricht, ist selbst ein Befund.

## Stufen innerhalb von Stufe 1 (je ein Schalter, einzeln zugeschaltet)

1. **Gemeinsames Vokabular:** Zahlen 0–112 und Operator-/Gleichheitszeichen als Tokens eines Vokabulars; die Ausgabe ist ein Token aus demselben Vokabular (statt einer eigenen Ausgabeschicht über p Klassen).
2. **Gebundene Embeddings:** Eingabe- und Ausgabeembedding geteilt (weight tying), wie in Sprachmodellen üblich.
3. **Verlust auf allen Positionen:** Die Sequenz „a + b = c“ wird autoregressiv trainiert (nächstes Token an jeder Stelle), im Gegensatz zu „nur die Antwort“.
4. **Minibatch** (aus L0 übernommen, i.i.d., Batchgröße nach dem L0-Ergebnis).

Je Stufe: F/G-Paare wie P1 (Seeds frisch), Δ_pow der Zahl-Token-Embeddings bei festem Budget, dazu Grokking-Zeit. Pilot 10 Seeds je Stufe (Exploration); eine Bestätigung nur für die Stufe, auf der K2 bricht bzw. zuletzt noch hält.

## Code-Bedarf (noch offen)

Ein kleiner eigener Trainer `lm_ladder.py` (Decoder-only-Transformer, konfigurierbar: getrenntes/gemeinsames Vokabular, Tying, Verlustmaske, Batchgröße), der dieselben Split-Dateien liest und W_E-Schnappschüsse wie `freq_ban.py` schreibt. Gleichwertigkeitsprüfung: In der Einstellung „alles aus“ soll er das Full-Batch-Ergebnis von `freq_ban.py` statistisch nachbilden. Checkpoints (Regel 20g) erst ab Stufe 2 (kleines LM), wenn Läufe länger als eine Sitzung dauern können.

## Stufe 2 (später, eigener Entwurf)

Ein kleines LM (≈ 10–30 M Parameter) wird von Grund auf auf natürlichem Text trainiert, der wenige Prozent konstruierter bzw. abgeglichener Rechensätze enthält. Die Kontrolle gleicht ab: Faktenzahl, Wiederholungen (feste Menge, gleich oft, keine gewichtete Neuziehung), Tokens je Rolle, Zählungen je Antwort, Schablonen. Das Kriterium ist die Genauigkeit auf zurückgehaltenen Fakten. Downloads nur nach Regel 20f, alles im JOURNAL.

## Designnotizen Sitzung 44 (2026-09-28, ≈ 20:28 Berlin; aus dem Studien-Code gelesen, nichts ausgeführt)

1. **Stufe 1.1 ist teilweise schon der Ausgangszustand.** Das Studienmodell (`training/grokverse/models/transformer.py`, `data.py`) hat bereits ein gemeinsames Eingabevokabular (Zahlen 0…p−1 und „=“, `vocab_size` = p + 1) und eine Ausgabeschicht über dasselbe Vokabular; der Verlust nimmt aber nur die ersten p Logits (`logits_last(x)[:, :p]`, `train.py:334`, `freq_ban.py:690`). Die echte Änderung in 1.1 ist also: (a) ein Operator-Token „+“ (Folge a + b =, n_ctx 4), (b) Softmax über das **ganze** Vokabular statt nur über die Zahlen. Beides einzeln schalten.
2. **Verlust auf allen Positionen ändert, was die Daten dem Modell zeigen.** Bei „a + b = c“ muss das Modell an der Position nach „a +“ das Token b vorhersagen. Die beste Vorhersage ist die Verteilung p(b | a) **der Trainingsmenge**. Bei einem konstruierten Split ist genau diese Paarstruktur das Steuersignal (Maskenspektrum). Stufe 1.3 macht die Steuerung damit zu einem direkten Vorhersageziel; K2 könnte stärker werden, ohne dass es etwas über das Rechnen sagt. **Kontrolle, vorab eingeplant:** Arm „alle Positionen außer b“ (Verlust auf „+“, „=“, c, nicht auf b), damit sich „Paarstruktur als Ziel“ von „Autoregressives Format“ trennen lässt. Bei Zufallssplits ist p(b | a) nahezu gleichverteilt, der Unterschied sollte dort verschwinden (zweite Kontrolle).
3. **Gleichwertigkeit.** Im Modus „alles aus“ soll der neue Trainer denselben Aufbau haben wie `freq_ban.py` (arch25k, AdamW 1e-3, wd 1, β 0.9/0.98, Full-Batch, Verlust nur auf den p Zahl-Logits der letzten Position). Ziel: bitgleich bei gleichem Seed, wenn die Initialisierungsreihenfolge übernommen wird (Modell über `build_model(get_config("arch25k", …))`), sonst statistisch (Δ_pow-Verteilung an denselben P1-Splits). Das vor jedem Leiterlauf prüfen.
4. **Messgröße auf Zahl-Tokens:** Δ_pow nur über die Zeilen 0…p−1 von W_E (Operator-/Gleichheitszeichen ausgeschlossen), wie bisher `W_E[:p]`. Bei gebundenen Embeddings (1.2) ist W_E zugleich die Ausgabeschicht; das im Ergebnis vermerken, denn die Ausgabe-Gradienten wirken dann direkt auf dieselben Zeilen.

## Pilotplan (Sitzung 44, 20:36; ungetestet, vor jedem Lauf)

- **Splits** (`design.py`, reines numpy, erzeugt 20:35): Seeds **3800–3809** (per Dateisuche geprüft: kein anderer Versuch nennt 3800–3999), F/G genau wie P1/EXP-053 (ω = 0, kalibriertes ε), dazu ein Zufallssplit R gleicher Größe aus demselben Pool. Zielanteile F 0.171–0.192, G 0.177–0.187, R 0.085–0.095 (Zufall ≈ 0.089).
- **Stufen** (je ein Schalter, F und G): r0 alles aus, op, fs, tie (mit fs), all (mit fs), allnb (mit fs); R nur für all/allnb. 10 Seeds → **140 Läufe** à 2000 Schritte, GPU. Minibatch (Stufe 4) erst nach L0.
- **Warum allnb** (aus `overlap_split.weights` gelesen): Das Paargewicht ist 1 + ε·mittel_k cos(2πka/p + φ_k(a+b)). p(b | a) der Trainingsmenge hängt also über die Zielfrequenzen von a ab; wer b aus a vorhersagen muss, wird für Zielfrequenz-Merkmale von a direkt belohnt, ganz ohne Rechnen.
- **Lesarten** (`analyze.py`, Docstring, vorab): je Stufe „hält“ (KI > 0), „bricht“ (KI-Obergrenze < halbes r0-Mittel), „schwächer“ (gepaartes KI zu r0 < 0); erste brechende Stufe in der Reihenfolge op, fs, tie, all = Leiterergebnis. Kontrolle D = Δ(all) − Δ(allnb). R beschreibend (Anteil der Zielfrequenzen, Zufall 10/56).
- **Vorher:** Selbsttest `lm_ladder.py --selftest` und `analyze.py --selftest` über den Wächter; Gleichwertigkeit r0 ↔ `freq_ban.py` an 2–3 Seeds (gleicher Split, 2000 Schritte, W_E-Schnappschuss vergleichen; bitgleich erwartet, wenn die Split-Reihenfolge gleich ist, siehe Prüfbefund); Smoke `design.py --smoke` (50 Schritte je Stufe, `raw_smoke`).
- **Bereits gesehene Daten:** P1-Größen von Δ_pow (Full-Batch), der Aufbau der Splits. Keine Läufe mit 3800–3809.

**Korrektur der Begründung für allnb (Sitzung 44, 21:05; gerechnet vor jedem Lauf, `pba_spectrum_s44.py`, Lesart vorab):** Die frühere Aussage „p(b | a) der Trainingsmenge hängt über die Zielfrequenzen von a ab“ ist **falsch** in der Form, auf die es ankommt: Bei festem b trägt p(b | a) über a keine Zielleistung (Anteil 0.088, Zufall 0.089; Lesart „trägt die Ziele nicht“), weil die Phasen im Splitbau von c = a + b abhängen. Die Zielstruktur steckt in (a, c)-Koordinaten (0.18, wie das Maskenspektrum) und in den Randhäufigkeiten (count(b): 0.225, count(a): 0.165 auf den F-Zielen; Zufallssplit 0.074/0.089). Mit Verlust auf der b-Position lernt das Modell also vor allem die zielstrukturierte Randverteilung p(b), und zwar über die Ausgabeschicht; mit gebundenen Embeddings landet sie direkt in W_E. **Deshalb vor jedem Lauf ergänzt:** das Paar tieall/tieallnb (gebunden + alle Positionen, mit und ohne b), auch auf R. 200 statt 140 Läufe. Der Kontrollarm allnb bleibt sinnvoll, seine Begründung ist jetzt „b-Randverteilung als Ziel“, nicht „p(b | a)“.

## Abnahme und Start (Sitzung 47, 2026-09-29, ≈ 04:55 Berlin)

- Selbsttests `lm_ladder.py --selftest` und `analyze.py --selftest` über den Wächter bestanden (04:11).
- **Gleichwertigkeit (Kriterium vorab in `equiv_compare.py`, Commit vor den Läufen):** r0 gegen `freq_ban.py`, Seeds 3800–3802, Split F, 2000 Schritte, GPU: **bitgleich** (relative Abweichung von W_E 0.0 bei 50/250/1000/2000; Top-5 und log(P_F/P_G) identisch) → „gleichwertig“ (`equiv_summary.json`).
- Smoke (`design.py --smoke`, alle Stufen, 50 Schritte, `raw_smoke`) fehlerfrei.
- Pilot gestartet: `python lab/tools/parallel_queue.py lab/experiments/EXP-102-lm-ladder-stage1/jobs.txt --workers 10 --min-minutes 3` (200 Läufe). Auswertung danach: `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/analyze.py`.
- Bezug zu [[FINDINGS]]: Verallgemeinerung von K2 (Programm A, Regel 20e).

---
id: EXP-102
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/unklar]
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

## Ergebnis Pilot (Sitzung 47, 2026-09-29, 05:12 Berlin; Exploration, 10 Seeds, Lesarten aus `analyze.py` vorab; nicht nachgerechnet)

200/200 Läufe fehlerfrei (`pilot_summary.json`). Δ_pow bei Schritt 2000 (Mittel [KI], positive Seeds, Lesart):

| Stufe | Δ_pow | Lesart | generalisiert (Test ≥ Schwelle bis 2000) |
|---|---|---|---|
| r0 (alles aus) | 8.04 [7.59, 8.51], 10/10 | hält | 20/20, Median 763 |
| op (Operator-Token) | 7.41 [6.74, 8.17] | hält | 19/20 |
| fs (volle Softmax) | 7.99 [7.52, 8.48] | hält | 20/20 |
| tie (gebunden) | 7.28 [6.38, 8.21] | hält | 20/20 |
| **all (Verlust auf allen Positionen)** | **1.65 [1.45, 1.88]**, 10/10 > 0 | **bricht** (erste brechende Stufe) | **0/20** (Test 0.01) |
| allnb (alle außer b) | 8.26 [7.55, 8.96] | hält | 20/20 |
| tieall | 1.60 [1.41, 1.81] | bricht | 0/20 (Test 0.03) |
| tieallnb | 7.53 [6.47, 8.40] | hält | 20/20 |

Kontrollen: all − allnb −6.60 [−7.20, −5.97], tieall − tieallnb −5.93 → „kein Steuerungsgewinn durch das b-Ziel“, im Gegenteil. Zufallssplit R: Zielanteil ≈ Zufall in allen vier Stufen (0.16–0.20; Zufall 0.18).
**Deutung (vorsichtig):** Format-Schalter (Operator, volle Softmax, gebundene Embeddings) ändern die Steuerung nicht. Die Leiter bricht bei „Verlust auf allen Positionen“, und zwar allein durch das Vorhersageziel b (ohne b hält alles). **Aber:** diese Netze haben in 2000 Schritten nicht generalisiert (nur memorisiert); die niedrige Δ_pow kann also verzögertes Grokking statt fehlender Steuerung sein. → Folgetest mit 10 000 Schritten (unten).

## Folgetest „all lang“ (Sitzung 47, 05:14, vor jedem Lauf festgelegt; Exploration)

Frage: Verzögert das b-Ziel nur das Grokking, oder blockiert es die Steuerung? Stufen all und tieall, Seeds 3800–3809, F/G, **10 000 Schritte**, `raw_long` (40 Läufe, `jobs_long.txt`). W_E bei 2000, 5000, 10 000.
Lesarten je Stufe (bei 10 000): **„verzögert, Steuerung erholt“**, wenn ≥ 8/10 Seeds in F und G generalisiert haben und die untere KI-Grenze von Δ_pow > 4.02 (= halbes r0-Mittel); **„Steuerung blockiert“**, wenn ≥ 8/10 generalisiert und die obere KI-Grenze < 4.02; **„grokkt nicht“**, wenn < 5/10 generalisiert; sonst „unklar“. Beschreibend: Δ_pow bei 2000/5000/10 000, Generalisierungsschritt.

### Ergebnis Folgetest (Sitzung 47, 05:30 Berlin; `long_summary.json`; nicht nachgerechnet)

40/40 Läufe fehlerfrei. **Lesart (vorab) für beide Stufen: „grokkt nicht“** — bis 10 000 Schritte generalisierten in F und G nur 0/10 (all) bzw. 2/10 (tieall) Seeds; einzeln 1/20 bzw. 8/20 Läufe, meist erst bei ≈ 8 600–10 000 Schritten (tieall einmal 4 850). Δ_pow wächst stetig: all 1.65 → 2.32 → **3.08 [2.75, 3.46]** (Schritt 2000 → 5000 → 10 000), tieall 1.60 → 2.44 → **3.06 [2.84, 3.30]**, je 10/10 > 0.
**Deutung (vorsichtig):** Das b-Vorhersageziel (Verlust auf allen Positionen) verzögert das Grokking um mehr als eine Größenordnung (Median ≈ 750 → > 9 000 Schritte). Die Steuerung ist nicht verschwunden (stets > 0, wachsend), bleibt aber bis 10 000 unter dem halben r0-Wert. Ob sie sich nach dem Grokking erholt, ist offen. **Für die Leiter heißt das:** Nicht das Format bricht K2, sondern das autoregressive Ziel auf dem zweiten Operanden verschiebt das Lernen in ein anderes Regime. Nächster Schritt: längere Läufe (≈ 30 000) oder Weight Decay/Lernrate so wählen, dass „all“ in einem vergleichbaren Budget grokkt, dann Δ_pow nach dem Grokking vergleichen (vorab festlegen).

### Folgetest „all 30k“ (Sitzung 47, 05:34, vor jedem Lauf; Exploration, 2 Seeds)

Stufe all, Seeds 3800–3801, F/G, 30 000 Schritte, `raw_long30k` (4 Läufe, `jobs_long30k.txt`). Beschreibend: Generalisierungsschritt, Δ_pow bei 10 000 / 20 000 / 30 000. Lesart: „erholt sich nach dem Grokking“, wenn beide Seeds in F und G generalisieren und Δ_pow(30 000) ≥ 4.02 (halbes r0) in beiden; „bleibt reduziert“, wenn generalisiert und < 4.02; sonst „offen“. Nur Hinweis für eine spätere Registrierung.

**Ergebnis „all 30k“ (Sitzung 47, 05:41; 2 Seeds, beschreibend, nicht nachgerechnet):** 4/4 Läufe fertig. Lesart (vorab): **„offen“** — generalisiert hat nur 3800 F (bei 15 175; Test 0.98); sonst Test 0.07 / 0.37 / 0.76 bei 30 000. Δ_pow wächst weiter: Seed 3800 2.63 → 3.60 → 4.16, Seed 3801 3.39 → 4.15 → 4.60 (Schritt 10 000 → 20 000 → 30 000), also über dem halben r0-Wert (4.02). Deutung (vorsichtig): eher „stark verzögert“ als „blockiert“; das b-Ziel verlangsamt Grokking und Steuerung gemeinsam.

### Folgetest „all 60k“ (Sitzung 48, 2026-09-29, 06:11 Berlin gemessen, vor jedem Lauf festgelegt; Exploration)

Frage: Ist die Steuerung nach dem Grokking wieder so groß wie in r0, oder bleibt sie durch das b-Ziel reduziert? Bezug: [[FINDINGS]] Programm A (Verallgemeinerung von K2), Regel 20e Leiter Stufe 1.
Stufe all, Seeds 3800–3809 (bis 10 000 bzw. 30 000 Schritte gesehen), F/G, **60 000 Schritte**, `raw_long60k`, 20 Läufe (`jobs_long60k.txt`), 10 GPU-Worker. Dauer geschätzt aus 30k-Läufen (490 s bei 4 parallelen Läufen): ≈ 16–30 min je Lauf, 2 Wellen ≈ 60 min.
Auswertung `analyze_60k.py` (vor dem Start geschrieben): je Seed auswertbar, wenn F und G generalisiert haben; t_post = erster Schnappschuss ≥ 2000 Schritte nach dem späteren der beiden Generalisierungsschritte. Lesarten: **„grokkt nicht“** < 5/10 auswertbar; **„erholt“** ≥ 8/10 auswertbar und untere KI-Grenze von Δ_pow(t_post) > 4.02 (halbes r0); **„bleibt reduziert“** ≥ 8/10 und obere KI-Grenze < 4.02; sonst „unklar“. Beschreibend: gepaarte Differenz zu r0 (Schritt 2000, ≈ 1200 Schritte nach dessen Grokking), Δ_pow bei 10k/30k/60k, Spearman(Generalisierungsschritt, Δ_pow nach dem Grokking).
Erwartung vorab (aus den 30k-Läufen, 2 Seeds): Grokking bei 12k–40k, nicht alle bis 60k; Δ_pow nach dem Grokking zwischen 4 und 6, also eher „unklar“ oder knapp „erholt“.

**Ergebnis „all 60k“ (Sitzung 48, 07:00 Berlin gemessen; `long60k_summary.json`; Exploration, nicht nachgerechnet):** 20/20 Läufe fertig; auswertbar (F und G generalisiert) **9/10 Seeds** (3801 F nicht; Test 0.76 bei 30k laut früherem Lauf). Generalisierungsschritte 9 350–46 475 (r0: Median 763). **Lesart (vorab): „unklar“** — Δ_pow nach dem Grokking (t_post = 22 000–47 000) **4.40 [3.83, 4.91]**, 9/9 > 0; das KI schließt das halbe r0 (4.02) ein. Beschreibend: gepaart gegen r0 bei 2000 **−3.75 [−4.68, −2.97]** (9/9 kleiner), also ≈ 55 % des r0-Werts; Δ_pow bei 10k/30k/60k (alle 10 Seeds): 3.08 / 4.29 / 4.59 — wächst nach ≈ 30k kaum noch (Plateau). Spearman(späteres Grokking, Δ_pow danach) −0.43 (n = 9).
**Deutung (vorsichtig):** Mit Verlust auf allen Positionen bleibt die Steuerung auch nach dem Grokking deutlich kleiner als bei Antwort-Verlust (gepaart in 9/9 Seeds), erholt sich aber auf gut die Hälfte; sie ist also weder blockiert noch voll erholt. Meine Vorab-Erwartung („eher unklar oder knapp erholt“) traf. Für die Leiter: Das autoregressive Ziel auf den Operanden schwächt die Datensteuerung dauerhaft, zerstört sie aber nicht. Offene Alternative: Die längere Trainingszeit selbst (Weight Decay über 20–45k Schritte) könnte Δ_pow verändern; r0 wurde nur bis 2000 gelesen. Ein fairer Vergleich bräuchte r0 bei gleichem Schritt nach dem Grokking bzw. bei gleicher Gesamtschrittzahl (nicht festgelegt, nur als Kandidat notiert).

### Nachtrag „r0 lang“ (Sitzung 48, 07:09 Berlin gemessen, vor den Läufen; Exploration)
Offene Alternative zum 60k-Ergebnis: Ändert sich Δ_pow von r0 allein durch langes Training? r0 (Antwort-Verlust, Full-Batch), Seeds 3800–3809, F/G, 30 000 Schritte (`raw_r0long30k`, 20 Läufe). Vergleich mit all bei gleicher Schrittzahl (10 000, 30 000). Lesarten in `analyze_r0long.py`: „r0 stabil“/„r0 driftet“ (KI von r0(30k) − r0(2000)); „Abstand bleibt bei gleicher Schrittzahl“, wenn die obere KI-Grenze von all(30k) − r0(30k) < 0.

---
id: EXP-105
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-105 (Regel 20e, Sprachmodell-Leiter Stufe 2, Entwurf): Steuert die Auswahl der Rechenfakten die Zahl-Embeddings eines kleinen Sprachmodells?

Zurück: [[LAB]] · [[FINDINGS]] (K2) · Regel 20e/f/g · Vorstufe [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]] · Kontrolle aus [[experiments/EXP-104-flat-marginal-splits/README|EXP-104]] / [[NOVEL_DIRECTIONS]] N53 · Einordnung (vor Zitat prüfen): Fu et al. 2026 (arXiv 2604.20817; Einzel-Token-Addition von Grund auf erzeugt dort oft keine Perioden), Zhou/Fu/Sharan/Jia 2024, Engels et al. 2024, Kantamneni & Tegmark 2025, Karkada et al. 2026

**Stand:** nur Entwurf (Sitzung 45, 2026-09-28, 22:06 Berlin gemessen). Kein Code, keine Downloads. Frühestens ab ≈ Fr 02.10., nach L0 und nach EXP-102 Stufe 1 und EXP-104. Alle Zahlen unten sind Planwerte, nicht gemessen.

## Frage

Ein kleines Sprachmodell wird von Grund auf auf natürlichem Text trainiert, in den wenige Prozent Rechensätze „a + b = c“ (mod 113) eingestreut sind. Arm F enthält die Fakten eines F-Splits, Arm G die eines G-Splits (disjunkte Zielfrequenzen), sonst ist alles gleich. Messgröße wie auf allen Stufen: Δ_pow auf den Embedding-Zeilen der 113 Zahl-Tokens. Pilot-Kriterium (Regel 20e): Genauigkeit auf **zurückgehaltenen** Fakten, nicht „Kreise vorhanden“.

## Das Abgleichproblem und die Lösung über N53

Regel 20e verlangt eine Kontrolle, die Faktenzahl, Wiederholungen, Tokens je Rolle, Zählungen je Antwort und Schablonen abgleicht. Bei den P1-Splits unterscheiden sich F und G gerade in den Zählungen je Zahl (count(a), count(b), count(c) tragen die Ziele; `pba_spectrum_s44.py`). Ein Sprachmodell sieht diese Zählungen als Token-Häufigkeiten, die W_E ohne jedes Rechnen formen können. **Mit den flachen Splits aus N53** kommt jede Zahl in jeder Rolle genau 34-mal vor, in F wie in G. Damit sind Faktenzahl (3842), Tokens je Rolle und Zählungen je Antwort exakt gleich, und nur die Paarung unterscheidet die Arme. Voraussetzung: EXP-104 zeigt, dass ein Transformer auf flachen Splits überhaupt generalisiert und gesteuert wird (sonst zurück zu P1-Splits mit einer Häufigkeitskontrolle wie EXP-047).

## Aufbau (Planwerte)

- **Text:** ein freier, kleiner Korpus einfacher Sprache (Kandidat TinyStories, Hugging Face; Größe und Lizenz vor dem Download prüfen, ≤ 30 GB insgesamt, Regel 20f).
- **Tokenizer:** eigener BPE (Paket `tokenizers` in `.venv-gpu`, Vokabular ≈ 8k) auf dem Korpus; zusätzlich 113 reservierte Zahl-Tokens und die Zeichen „+“, „=“, die **nur** in Rechensätzen vorkommen (Ziffern im Fließtext bleiben normale BPE-Tokens, damit die Zahl-Tokens keine Textstatistik tragen).
- **Rechensätze:** feste Faktenmenge je Arm, jeder Fakt gleich oft (Kreislauf mit neu gemischter Reihenfolge je Runde, **keine gewichtete Neuziehung**); 3–4 Satzschablonen, gleich verteilt über die Arme; Anteil ≈ 2–5 % der Tokens (im Smoke festlegen: so, dass jeder Fakt ≥ 1000-mal vorkommt, die Größenordnung der Full-Batch-Exposition bis zur Festlegung).
- **Arme:** F, G (flach, m = 10 Tauschzüge, siehe EXP-104), R (flach, zufälliges D, ohne Zielkonzentration), T0 (nur Text, keine Rechensätze; misst die Frequenzstruktur, die der Text allein den Zahl-Tokens gibt, erwartet ≈ Init).
- **Modell:** Decoder-only, 6 Schichten, d = 384, 6 Köpfe, Kontext 256, gebundene Embeddings (≈ 14 M Parameter). AdamW (lr 3·10⁻⁴ mit Warmup, wd 0.1), Minibatch; Budget nach dem Smoke (Tokens/s messen).
- **Seeds:** Pilot 3860–3864 (frei geprüft, Sitzung 45), F/G je Seed gleiche Init.
- **Checkpoints (Regel 20g):** Modell, AdamW-Zustand, RNG-Zustände, Schritt, Konfig-Hash; alle ~15 min und am Wächter-Ende; Wiederaufnahme nur bei gleichem Hash.

## Messgrößen und Lesarten (vorläufig; endgültig vor dem ersten Lauf im Code)

- Δ_pow auf den Zahl-Token-Zeilen (F gegen G, gleiche Seeds), zu festen Token-Zählständen; Zielanteil je Arm; R und T0 beschreibend.
- Genauigkeit auf zurückgehaltenen Fakten (Test = Komplement, in einem festen Satzformat abgefragt) und auf den Trainingsfakten.
- Lesarten: „K2 hält im LM“ (Δ_pow-KI > 0 und Genauigkeit auf zurückgehaltenen Fakten klar über Zufall); „nur Repräsentation“ (Δ_pow > 0 ohne Generalisierung, wie bei der Integer-Addition in P4); „bricht“ (Δ_pow-KI enthält 0). Jeder Ausgang ist ein Befund (Regel 20e: die erste Stufe, auf der K2 bricht).

## Offene Entscheidungen (vor dem Code)

1. Anteil der Rechensätze und Budget: aus Stufe 1 (EXP-102) und einem Smoke (Tokens/s auf der RX 7900 XT unter ROCm/Windows) ableiten.
2. Ob Zahlen im Fließtext auf die Zahl-Tokens abgebildet werden (realistischer, aber dann trägt die Textstatistik Häufigkeiten in W_E) oder getrennt bleiben (sauberer). Vorschlag: getrennt im Piloten, abgebildet als spätere Stufe.
3. Ob ein Arm mit P1-Splits (nicht flach) dazukommt, um die Größe des Häufigkeitsbeitrags im LM direkt zu messen (Paar P1-F/G gegen flach-F/G).

## Pilotplan (Sitzung 48, 2026-09-29, ≈ 06:25 Berlin; vor jedem Lauf; Exploration)

**Stand:** Korpus und Tokenizer nach Regel 20f geladen bzw. gebaut (JOURNAL Sitzung 48). Trainer `lm_stage2.py` geschrieben, noch ungetestet. Abweichungen vom Entwurf: lr 6·10⁻⁴ (Warmup 500, dann konstant), β 0.9/0.95, 2 Rechensätze je Sequenz aus 257 Tokens (Anteil wird gemessen und berichtet), Checkpoints alle 1000 Schritte.

1. **Selbsttest** (winziges Modell, GPU): 40 Schritte am Stück = 20 Schritte, Checkpoint, Abbruch bei 25, Wiederaufnahme → Gewichte und Kurve bitgleich (Regel 20g).
2. **Durchsatz-Smoke:** ein Lauf in voller Größe, 200 Schritte, Seed 3860, Split EXP-102 seed3800_F: Tokens/s, Rechenanteil, Speicher. Daraus das Budget: so viele Schritte, dass ein Lauf ≤ 60 min dauert, möglichst ≥ 100 Runden je Fakt.
3. **Pilot** (2 Seeds 3860–3861, je F und G mit gleicher Init, gleichem Text, gleichen Positionen; 4 Läufe). **Splits:** Zeigt EXP-104, dass flache Splits mit m = 10 in beiden Seeds generalisieren und Δ_pow > 1 haben, die flachen Splits (m = 10, EXP-104-Seeds 3850/3851); sonst die P1-Splits aus EXP-102 (Seeds 3800/3801) mit dem Vermerk, dass dort auch die Token-Häufigkeiten die Ziele tragen. Festgelegt vor dem EXP-104-Ergebnis.
4. **Lesarten des Piloten** (am Budgetende; Δ_pow wie in allen Stufen auf den 113 Zahl-Token-Zeilen, Test = zurückgehaltene Fakten, Abfrage in Schablone T0, Zufall 1/113):
   - „K2 hält im LM“: Δ_pow > 1 in beiden Seeds und Testgenauigkeit > 0.5 in ≥ 3 von 4 Läufen;
   - „nur Repräsentation“: Δ_pow > 1 in beiden Seeds und Testgenauigkeit < 0.1 in ≥ 3 von 4 Läufen (wie Integer-Addition in P4);
   - „bricht“: |Δ_pow| ≤ 1 in beiden Seeds;
   - sonst „unklar“. Beschreibend: Verlauf von Δ_pow, Genauigkeit auf Trainingsfakten, Textverlust auf der Validierung (lernt das Modell Sprache?).
   Erwartung vorab: Stufe 1 zeigte, dass Verlust auf der b-Position das Grokking um > ×10 verzögert; hier gilt das für jede Rechenzeile. Erwartet also eher „nur Repräsentation“ oder „unklar“ im Pilotbudget. Fu et al. 2026 fanden bei Einzel-Token-Addition von Grund auf oft keine Perioden.

**Codeprüfung vor dem ersten Lauf (Sitzung 48, ≈ 06:33, unabhängiger Claude-Agent, nur lesend):** kein Blocker; F/G-Paarung bestätigt (Text- und Schablonenstrom unabhängig von den Fakten, Blocklänge gleich), Prompt-Format passt zur Tokenisierung (Ġ vor der Zahl), Budget ohne Textumlauf. Übernommen: (1) Sperrdatei mit PID, eine verwaiste Sperre (Prozess tot, z. B. nach `taskkill` durch den Wächter) wird übernommen → Wiederaufnahme ohne Handarbeit; (2) Abfrage beginnt mit `<|endoftext|>` wie der erste Fakt im Training; (3) **gemeinsame Testmenge für F und G**: flache Splits `--test-file lab/experiments/EXP-104-flat-marginal-splits/splits/s{seed}_test.npy`; P1-Splits `--test-file lab/experiments/EXP-105-lm-ladder-stage2/tests/seed{seed}_test.npy` (= `design.build(seed)["test"]` aus EXP-102, 2554 Fakten, disjunkt zu F und G); `analyze_pilot.py` prüft jetzt, dass F und G bis auf den Split dieselbe Konfiguration haben; (4) Validierungsbatch aus eigenem Strom; (5) Textumläufe gezählt; Smoke und Pilot in getrennten Ausgabeordnern (`raw_smoke`, `raw_pilot`). Selbsttest auf CPU (deterministisch) statt GPU.

**Durchsatz-Smoke (Sitzung 48, 07:01 gemessen; unter Last von 9 weiteren GPU-Prozessen):** GPU-Pfad läuft (SDPA über AOTriton), 13 891 584 Parameter, Rechenanteil 0.087 der Tokens, 200 Schritte in 48 s (≈ 0.24 s/Schritt, ≈ 34 000 Tokens/s unter Last), kein Textumlauf; Genauigkeit nach 200 Schritten Zufall (0.010), Validierungsverlust 4.04. **Budget des Piloten (vor dem EXP-104-Ergebnis festgelegt): 10 000 Schritte** (≈ 64 Fakten je Schritt → ≈ 167 Runden je Fakt; ≈ 40 min je Lauf unter Last; 82 Mio. Tokens, Text reicht ohne Umlauf). 4 Läufe starten, sobald die GPU-Warteschlange ≤ 6 Prozesse hat.

**Überlegung vor dem Pilotergebnis (Sitzung 48, 07:36; festgehalten, bevor das Budgetende gelesen wird):** Expositionen je Fakt bis zum Grokking aus Stufe 1: Antwort-Verlust Full-Batch ≈ 760 (EXP-102 r0), Antwort-Verlust Minibatch 256 ≈ 1 013 Schritte × 256 / 3 831 ≈ 68 (EXP-112 r0B), LM-Format + Next-Token ohne b unter Minibatch langsamer (Median 1 575 Schritte ≈ 105, nur 13/20 bis 5 000), Verlust auf allen Positionen Full-Batch 9 000–46 000. Der Pilot gibt jedem Fakt ≈ 167 Expositionen mit Verlust auf allen Positionen (inkl. b) und Text dazwischen. Nach Stufe 1 reicht das eher nicht zum Grokking; erwartet also „bricht“ oder „unklar“ (Δ_pow bei 3 000 Schritten 0.02–0.06, Fakten auf Zufallsniveau). **Vorschlag für die nächste Fassung (nach dem Pilotergebnis zu entscheiden, nicht als Rettung des Piloten):** Expositionen je Fakt um ≥ ×10 erhöhen (höherer Rechenanteil, z. B. 8 Sätze je Sequenz ≈ 30 % der Tokens, und/oder längeres Budget mit Checkpoints) und als Kontrolle eine Variante mit Verlust nur auf den Antwort-Tokens der Rechensätze (trennt „LM-Umgebung“ von „Operanden-Ziel“, wie EXP-102 all/allnb).

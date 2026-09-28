---
id: EXP-105
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-105 (Regel 20e, Sprachmodell-Leiter Stufe 2, Entwurf): Steuert die Auswahl der Rechenfakten die Zahl-Embeddings eines kleinen Sprachmodells?

Zurück: [[LAB]] · [[FINDINGS]] (K2) · Regel 20e/f/g · Vorstufe [[experiments/EXP-102-lm-ladder-stage1/README|EXP-102]] · Kontrolle aus [[experiments/EXP-104-flat-marginal-splits/README|EXP-104]] / [[NOVEL_DIRECTIONS]] N53 · Einordnung (vor Zitat prüfen): Fu et al. 2026 (arXiv 2604.20817; Einzel-Token-Addition von Grund auf erzeugt dort oft keine Perioden), Zhou/Fu/Sharan/Jia 2024, Engels et al. 2024, Kantamneni & Tegmark 2025, Karkada et al. 2026

**Stand:** nur Entwurf (Sitzung 45, 2026-09-28, ≈ 22:08 Berlin). Kein Code, keine Downloads. Frühestens ab ≈ Fr 02.10., nach L0 und nach EXP-102 Stufe 1 und EXP-104. Alle Zahlen unten sind Planwerte, nicht gemessen.

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

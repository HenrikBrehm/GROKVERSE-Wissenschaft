---
id: EXP-102
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
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

---
id: L0b_DEUTUNGEN
datum: 2026-09-30
tags: [lab/paper]
---
# L0b (Menge gegen Reihenfolge bei B = 16, Bestätigung): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[confirm/L0b_REGISTRATION]] · Pilot [[experiments/EXP-106-l0-b16-long-epochs/README|EXP-106]] · [[paper/L0_DEUTUNGEN]]

**Geschrieben in Sitzung 63 (30.09., 21:32 Berlin gemessen), vor dem Einfrieren und vor jedem L0b-Lauf.** Ort im Paper: §6 „Order against set“ (Kurzfassung, heute Pilot-Absatz Zeile ≈ 84) und Anhang J (Minibatch, Absatz „Long epochs (EXP-106 …)“, Zeile ≈ 132): Der Pilot bleibt beschrieben, die Bestätigung folgt als eigener Satz. Abstract nur bei H1 **und** H2 bestätigt (dann ersetzt der Satz den Halbsatz „a fixed data order did not shift the frequencies at 30 % data (pilot)“; Zeichenbudget prüfen, < 1920). Zahlen nach `--analyze` einsetzen, unabhängige Nachrechnung und Textprüfung wie immer.

## §6, je Ausgang

- **H1 und H2 bestätigt:** *In the long-epoch regime (batch 16, 240 steps per epoch, weight decay 0.1), a confirmation on 64 fresh seeds (frozen before any run) showed that the fixed stride order shifted energy onto its own frequencies on random splits (+… [… , …], Holm-p …) but not on engineered splits (difference … [… , …], inside the pre-set equivalence margin ±0.05), where the set still steered (Δ_pow … [… , …]) [H4: and the order only delayed generalization by … log2]. The order thus acts where the set carries little frequency signal and loses the conflict where it carries a strong one, consistent with LeDoux's remark that the importance of order scales inversely with the content signal of the data.*
  Abstract-Halbsatz: *… at batch 16 a fixed data order shifted the frequencies on random but not on engineered splits (64 fresh seeds).*
- **H1 nicht, H2 bestätigt:** *… the order did not shift the engineered splits' frequencies (… inside ±0.05) and the set still steered (Δ_pow …); an order effect on random splits, seen in the pilot, was not confirmed (+… [… , …], Holm-p …).*
- **H2 nicht bestätigt:** *… on engineered splits the order-share difference was … [… , …], not inside the pre-set margin ±0.05, so we do not claim that the set wins the conflict;* (dann H1/H3 wie gemessen, ohne Deutung „Menge gewinnt“).
- **H3** (unabhängig): bestätigt → *the set still steered under the conflicting order (Δ_pow … > 1)*; nicht bestätigt → Befund so berichten (Steuerung unter der Reihenfolge nicht über 1 bestätigt).
- **H4** (unabhängig): bestätigt → *… and delayed generalization on engineered splits by … log2 (≈ ×…)*; nicht bestätigt → *a delay seen in the pilot was not confirmed*.
- **„nicht auswertbar“:** *The confirmation was not evaluable (…); the pilot result stands as exploration.*

## Was ausdrücklich nicht gesagt wird

- keine Aussage über LeDoux' Regime (p = 9973, 0.3 % Daten, ≈ 1165 Schritte je Epoche); wir haben eine Batchgröße (240 Schritte je Epoche) bei 30 % Daten;
- „Reihenfolge wirkt, wo die Menge wenig vorgibt“ nur als Vergleich zweier Splitarten (zufällig gegen konstruiert), nicht als Dosis-Wirkung;
- weight decay 0.1 ist ein anderes Regime als der Haupttext (wd 1), das wird genannt.

---
id: EXP-076
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[BEFUND-split-mechanismus]]", "[[NOVEL_DIRECTIONS]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[JOURNAL]]"]
---
# EXP-076: Ist das Maskenspektrum M0 der AGF-Nutzen erster Stufe bei nicht-uniformer Paarverteilung? (THEORIE-RECHNUNG, keine Läufe)

Zurück zu [[LAB]] · [[FINDINGS]] (Literatur zu K2; Programm C: mechanistische Vorhersage) · [[NOVEL_DIRECTIONS]] „Literatur-Nachtrag zu K2“ (Brückenfrage zu Marchetti, Kunin et al. 2026).
Festgelegt 2026-09-27, Sitzung 24, **vor der ersten Rechnung**. Reine numpy-Rechnung auf vorhandenen Split-Dateien (kein Training, kein Test; außerhalb des Fensters zulässig).

- **Frage:** In AGF (Kunin et al. 2025; Marchetti et al. 2026) wählt ein Zwei-Schicht-Netz bei kleiner Init zuerst die Irrep mit dem größten „Nutzen“; bei gleichverteilten Paaren und One-hot-Token sind
  alle Frequenzen gleichauf. Mit einer Trainingsmaske S (nur manche Paare) ändert sich der Nutzen. Ordnet dieser Nutzen U_k die Frequenzen so wie unser empirisches Maskenspektrum M0 (EXP-015)?
- **Modell (Vereinfachung):** f(a, b) = w · (u_a + v_b)², One-hot a, b über Z_113, Ziel e_(a+b) (zentriert), MSE, Daten = Paare in S. Nutzen eines Neurons bei verschwindender Init:
  U(u, v, w) = Σ_(a,b)∈S w_(a+b) (u_a + v_b)². **Ansatz einer Frequenz k:** u, v, w je im Raum {cos, sin}(2πk·/p). Dann ist U_k = max über Einheitsvektoren = (2/(3√3)) · max_φ λ_max(cos φ M₁ + sin φ M₂)
  mit M_j = Σ_(a,b)∈S B_j(a+b) z_ab z_abᵀ, z_ab = [B(a); B(b)] (B = normierte cos/sin-Basis bei k). Die Konstante ist für die Rangfolge unerheblich.
- **Selbstprüfung:** Für S = alle Paare müssen alle U_k gleich sein (Gleichstand wie bei Marchetti et al. mit One-hot).
- **Material:** die 20 konstruierten Splits aus EXP-016 (F und G, Seeds 10–19, Ziele in den JSON-Dateien) und 10 Zufallssplits (30 % der Paare, numpy-RNG 76).
- **Maße je Split:** Spearman ρ(U_k, M0_k) über k = 1..56; Treffer der Top-5 von U_k und von M0_k unter den 5 konstruierten Zielen.
- **Lesart vorab:** Median ρ über die 20 konstruierten Splits ≥ 0.8 und mittlere Top-5-Treffer von U nicht mehr als 0.5 unter denen von M0 → *Brücke gestützt* (M0 verhält sich wie der AGF-Nutzen erster
  Stufe); Median ρ < 0.4 → *keine Brücke*; sonst *unklar*. Zufallssplits beschreibend.
- **Grenzen:** quadratische Aktivation und Ein-Frequenz-Ansatz (Mischungen verschiedener k sind ausgeschlossen); nicht das Transformer-Modell der Versuche; eine Übereinstimmung zeigt eine
  formale Nähe, keinen Mechanismus im Transformer. Theorie-Rechnung ohne unabhängige Daten.

```
python lab/experiments/EXP-076-agf-utility/compute.py
```

## Ergebnis (Sitzung 24, Rechnung bis 13:38 Berlin, gemessen; `summary.json`)

Selbstprüfung ok: Bei allen Paaren sind alle U_k gleich (2.8932). **Vorab-Lesart: *keine Brücke*.** Median ρ(U_k, M0_k) über die 20 EXP-016-Splits = −0.02 (Minimum −0.31); Top-5-Treffer unter den Zielen:
U im Mittel 0.45 (Zufall 25/56 = 0.45), M0 5.0. Zufallssplits: Median ρ −0.03.

- **Lesart:** Der Nutzen eines einzelnen Neurons im AGF-Modell mit quadratischer Aktivation (Ein-Frequenz-Ansatz, verschwindende Init) sieht die konstruierten Ziele nicht; M0 ist in diesem Modell
  **nicht** der Nutzen erster Stufe. Die Brückenvermutung aus [[NOVEL_DIRECTIONS]] ist damit für dieses Modell widerlegt.
- **Mögliche Erklärung (Spekulation, ungeprüft):** Die konstruierten Masken haben zufällige Phasen je Ausgabe c; M0 summiert die Leistung je c inkohärent (wie der erste W_E-Gradient bei einer
  zufälligen, festen Auslese bei endlicher Init, [[BEFUND-split-mechanismus]]), das AGF-Neuron lernt seine Auslese w dagegen aus null und braucht Phasenkohärenz über c. Daraus folgt eine prüfbare
  Vorhersage: Bei sehr kleiner Init (AGF-Bereich) sollte die Split-Steuerung schwächer werden. Ein schneller Gegencheck mit „kohärenten“ Masken war **falsch gebaut** (Phase unabhängig von c macht
  die Welle zu einer reinen Häufigkeitsmodulation) und prüft die Erklärung nicht.
- **Grenzen:** ein vereinfachtes Modell (quadratisch, Ein-Frequenz-Ansatz); keine Aussage über den Transformer.

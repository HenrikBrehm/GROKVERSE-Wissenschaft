---
id: EXP-061
status: verworfen
datum: 2026-09-27
tags: [exp/verworfen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[experiments/EXP-060-early-lead/README|EXP-060]]", "[[experiments/EXP-038-where-lockin/README|EXP-038]]", "[[JOURNAL]]"]
---
# EXP-061: Verstärkt schon der Gradient der neuen Daten die alte Wahl? (Pilot, Programm B/C)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B: *was* macht die Wahl in ≈ 50 Schritten fest?) · Vorgänger [[experiments/EXP-059-momentum-exposure/README|EXP-059]], [[experiments/EXP-060-early-lead/README|EXP-060]].
Festgelegt 2026-09-27 (Sitzung 22), **vor jedem EXP-061-Lauf und vor jeder Gradientenrechnung**. **Pilot**, bekannte Seeds 400–409 (π-Werte aus EXP-059 bekannt).

**Idee (Selbstverstärkung):** Nach t Schritten auf X ist das Netz (W_E *und* der Rest, EXP-038) auf die X-Ziele eingestellt. Trainiert man jetzt auf Y, fließt der Y-Gradient durch dieses
eingestellte Netz. Ab einem Punkt verstärkt er die schon gelernte X-Struktur in W_E, statt sie abzubauen. Dann bleibt die Wahl, obwohl die Daten sie nicht verlangen
(jede Frequenzmenge löst die Aufgabe). EXP-060 zeigte: Der spektrale Vorsprung in W_E selbst erklärt die Seed-Streuung von π kaum. Die Vorhersage hier nutzt das ganze Netz über den Gradienten.

**Bereits gesehene Daten und davon beeinflusste Entscheidungen:** π(s, t) aus EXP-059 (Seeds 400–409, t = 10…50), EXP-060 (W_E-Vorsprung erklärt die Streuung kaum). Das Maß unten ist vor jeder Rechnung festgelegt.

| | |
|---|---|
| **Läufe** | Seeds 400–409, EXP-056-Splits (ω = 0), je Richtung (erst A, erst B) reiner Lauf mit `--steps t --save-model`, t ∈ {10, 20, 25, 35, 50}; 100 kurze Läufe, GPU. Zustand bei t = Zustand des Wechsellaufs bei t (konstante lr, Full-Batch, GPU deterministisch wie EXP-058). |
| **Maß** | g = ∂L_Y/∂W_E[:113] (Kreuzentropie, Logits [:113], ganzer Y-Trainingssatz, Modell in float32 auf der CPU, Auswertung in float64). ΔW = W_E(t) − W_E(0) (Init aus dem Seed, `init_checksum`). Π_T = Projektion der Zeilen auf die Fourier-Frequenzen T (cos/sin). **c_own = cos(−Π_own g, Π_own ΔW)**: Wie stark schiebt der Gradient der neuen Daten entlang der schon gelernten Struktur der eigenen Ziele? c_other ebenso für die Ziele der neuen Daten. c(s, t) = Mittel beider Richtungen. |
| **Vorhersage V1** | Mittel von c_own steigt mit t (Spearman über die 5 Mittelwerte > 0) und ist bei t = 50 positiv, bei t = 10 kleiner als bei t = 50. |
| **Vorhersage V2** | Innerhalb von t erklärt c_own die Seed-Streuung von π: Mittel der 5 Spearman-ρ(c_own, π) über t > 0.3 (EXP-060-Vergleich: W_E-Vorsprung 0.18). |
| **Urteil** | V1 und V2 → ***Kandidat***: dieselbe Vorhersage vorab an den frischen N28-Seeds (2200–2229) festlegen, bevor deren π ausgewertet wird. Nur V1 → ***Uhr, keine Seed-Vorhersage***. Sonst ***verworfen***. |
| **Grenzen** | Pilot, bekannte Seeds; Rohgradient statt Adam-Schritt (der Momentum-Anteil fehlt absichtlich); Kosinus erster Ordnung. |
| **Budget** | 100 Läufe à ≤ 50 Schritte, parallel zu den Bestätigungsblöcken; Auswertung auf der CPU in Sekunden. |

```
python lab/tools/parallel_queue.py lab/experiments/EXP-061-grad-alignment/jobs.txt --workers 3
python lab/tools/guarded_run.py -- python lab/experiments/EXP-061-grad-alignment/analyze.py
```

## Ergebnis (Sitzung 22, Läufe 07:38–07:47, Auswertung 07:48 Berlin; `summary.json`): ***verworfen***

100/100 Läufe ok, 50/50 Punkte; das Modell bei t stimmt mit dem W_E-Schnappschuss bei t überein (geprüft).

- **c_own (Mittel):** −0.48 / −0.60 / −0.66 / −0.74 / −0.78 bei t = 10 / 20 / 25 / 35 / 50. c_other −0.43 … −0.57.
- **V1 nein:** Der Gradient der neuen Daten zeigt **gegen** die gelernte Struktur der alten Ziele, und das umso stärker, je später gewechselt wird, obwohl π gleichzeitig von 0 auf 1 steigt.
- **V2 nein:** Innerhalb von t Spearman(c_own, π) im Mittel −0.25.
- **Lesart:** Eine Selbstverstärkung über den Rohgradienten in W_E erklärt die Festlegung nicht; erster Ordnung baut das neue Training die alte Struktur ab. Die Persistenz muss aus der weiteren
  Dynamik kommen: Adam-Normierung je Koordinate (v aus der A-Phase), Weight Decay, das Zusammenspiel mit dem Rest des Netzes oder schlicht daraus, dass die B-Struktur langsamer wächst, als die
  A-Struktur schrumpft. Rohgradient und Kosinus erster Ordnung sind grobe Werkzeuge; das Urteil gilt nur für dieses Maß.
- **Nächste Frage (nicht festgelegt):** Wachstumsraten statt Richtungen: Wie schnell schrumpft die A-Energie und wie schnell wächst die B-Energie nach dem Wechsel, je t (aus den Spektren bei t + 250 und
  am Ende, schon gespeichert)? Ein Wettlauf zweier Raten würde die Steilheit von π(t) ohne Selbstverstärkung erklären.

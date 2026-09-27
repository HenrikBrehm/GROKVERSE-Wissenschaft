---
id: EXP-048
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-046-dihedral-steering/README|EXP-046]]", "[[experiments/EXP-047-marginal-control/README|EXP-047]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-048: Datensteuerung der Frequenzen bei **nicht-modularer** Addition

**Status:** abgeschlossen 2026-09-27 (Sitzung 20, GPU), Ergebnis unten. Ursprünglich: vorbereitet, nicht ausgeführt, ungetestet (Sitzung 13, 2026-09-26 20:10 Berlin, außerhalb des Fensters).
Festgelegt, bevor ein einziger Lauf dieser Aufgabe existierte. Zurück zu [[LAB]] · [[FINDINGS]] · Idee [[NOVEL_DIRECTIONS]] N25.

## Bezug zu [[FINDINGS]]

Zielt auf die **größte offene Frage** (gilt K2 außerhalb von Addition mod p?) und auf Regel 15c („möglichst auch eine
nicht-modulare Aufgabe“). Gewöhnliche Addition a + b (a, b ∈ 0..112, Ergebnis 0..224) ist keine Gruppenverknüpfung auf den Token;
bekannt ist, dass Netze hier eine **Zahlengerade** lernen können (Liu et al. 2022, https://arxiv.org/abs/2205.10343), also gerade
keine Fourier-Uhr. Das macht den Test scharf: Wenn der Split die Frequenzen auch dort vorgibt, ist K2 nicht an die zyklische
Struktur gebunden. Wenn nicht, ist das eine klare Grenze von K2.

## Aufbau

- **Aufgabe:** Eingabe (a, b, „=“), Ausgabe c = a + b ∈ 0..224 (225 Klassen). Gleiches Modell (1-Schicht-Transformer, Preset
  arch25k, AdamW lr 1e-3, wd 1, Full Batch), `p = 225` in der Konfiguration (vocab 226, „=“ = 225), Eingaben nur Token 0..112.
  Code: `intadd_train.py` (eigenes schlankes Skript nach dem Muster von EXP-046 `group_train.py`; `freq_ban.py` bleibt unberührt).
- **Konstruierter Split** (EXP-016-Konstruktion, Ausgabe = Ganzzahlsumme): q(a, b) = max(0.05, 1 + ε · mean_{k∈T} cos(2πka/113 + φ_{k,a+b})),
  ε = 2, genau 3831 Paare (30 %) ohne Zurücklegen, Test = Komplement (8938 Paare). Zielmengen F und G: je 5 aus **k = 6..56**,
  disjunkt. k ≤ 5 ausgeschlossen, weil eine Zahlengerade (Rampe) dort den Großteil ihrer DFT-Leistung hat; Ziele dort wären mit der
  natürlichen Lösung vermengt. Zufallsströme über `SeedSequence([48001, seed, arm, Zweck])`. Arm R: ε = 0 (gleiche Seeds).
- **M0 (Ganzzahlversion, offline, reine Rechnung 20:08):** k = 1, 2 stehen wegen des dreieckigen Trägers immer oben; die Ziele
  liegen auf Rang 4.0 im Mittel (höchstens 7) von 56, in 18/20 Splits alle in der M0-Top-7. Zielanteil 0.140 (Arm R 0.079).
- **Messgröße:** DFT-Leistung von W_E (Zeilen 0..112) über den Eingabeindex, k = 1..56, bei Schritt 2000 (`spectra.npy`).

| | |
|---|---|
| **Fragestellung** | Gibt ein konstruierter Split auch bei nicht-modularer Addition vor, welche Frequenzen in W_E entstehen? |
| **H48** | Δ̄_pow > 0 |
| **Bedingungen** | je Init-Seed i ∈ 160–169 zwei Läufe: Split F_i und G_i, 2000 Schritte, **alle auf der GPU** |
| **Primärgröße** | Δ_pow,i = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)], P_arm(S) = W_E-Leistung des Laufs „arm“ bei 2000, summiert über S. **Vor jedem Lauf ersetzt: auf dem trendbereinigten W_E, siehe Nachtrag a** |
| **Warum nicht Top-5 (wie EXP-016)** | Bei einer Zahlengeraden besetzen k = 1..5 die Top-5 in beiden Armen; Top-5-Überlappung wäre dann 0, ohne dass die Steuerung fehlt. Δ_pow ist davon unberührt (gemeinsame Anteile heben sich auf). Kalibrierung an den gespeicherten EXP-016-Läufen (Seeds 10–19, CPU, reine Nachrechnung 20:06): **Δ_pow = 8.4 im Mittel, 10/10 positiv** |
| **Test** | einseitiger Vorzeichen-Permutationstest über die gültigen Seeds (exakt, 2^n) |
| **Gültig** | beide Läufe `completed`, 2000 Schritte, Gerät cuda, Split-Hash = Inhalt der .npy; < 8 gültige Seeds: *nicht auswertbar* |
| **Entscheidung** | *steuerbar*: Δ̄_pow > 0, p < 0.05 · *richtungsgleich, n. s.*: Δ̄_pow > 0, p ≥ 0.05 · *widerspricht*: Δ̄_pow ≤ 0 |
| **Sekundär (nur berichtet)** | Top-5-Δ wie EXP-016; Zahlengeraden-Maß R² (Anteil der W_E-Varianz, der linear in a ist) je Arm; Arm R: log[P_R(F)/P_R(G)] (Erwartung ≈ 0); Train-/Test-Genauigkeit, gen-Schritt |
| **Erwartung** | offen. Für H48 spricht: Der Mechanismus erster Ordnung (Paarstruktur → erster W_E-Gradient, [[BEFUND-split-mechanismus]]) braucht keine Gruppe. Dagegen: Die Aufgabe hat eine einfache nicht-periodische Lösung, die die Frequenzen unwichtig machen könnte |
| **Was dagegen spräche** | Δ̄_pow ≤ 0: Die Steuerung hängt an der zyklischen Struktur der Aufgabe |
| **Grenzen** | Ein positives Δ_pow zeigt, dass der Split Fourier-Leistung in W_E erzeugt, nicht dass das Netz sie *funktional* nutzt (dafür: Ablation, späterer Versuch). 2000 Schritte: Auswahl vor einer möglichen Endlösung. Die Test-Genauigkeit kann bei nicht-modularer Addition anders verlaufen; sie ist nicht Teil des Urteils. Häufigkeits-Confound wie in EXP-046 (Lesart „der Split steuert“; Mechanismus erst mit [[experiments/EXP-047-marginal-control/README|EXP-047]]) |
| **Budget** | 30 Läufe à 2000 Schritte auf der GPU, J parallel (aus GPU-001); Ausgabeschicht 225 statt 113, sonst wie EXP-046: Schätzung ≤ 5 min pro Lauf, zusammen ≲ 40 min bei J = 4 |

## Befehle

```
python lab/experiments/EXP-048-intadd-steering/make_split.py --seed I --arm {F,G,R}     # reine Rechnung, erledigt (160–169)
sh lab/experiments/EXP-048-intadd-steering/queue.sh J          # Selbsttest, Smoke, 20 Läufe, Auswertung, dann R-Arme
python lab/tools/guarded_run.py -- python lab/experiments/EXP-048-intadd-steering/analyze.py
```

Die Queue braucht GPU-001 = PASS (Regel 16d) und stoppt bei Ablehnung des Wächters (rc 3). Eingehängt in `queue_gpu_s11.sh` nach EXP-047.

*Beim Bau gefunden und behoben (vor jedem Lauf):* `Path.with_suffix` hielt „.0_F“ für die Dateiendung, sodass F-, G- und R-Splits
einander überschrieben (40 statt 60 Dateien). `make_split.py` baut die Namen jetzt als Zeichenkette; neu erzeugt und geprüft
(60 Dateien, F/G/R verschieden, Ziele disjunkt).

## Literatur (Suche 2026-09-26, 20:04–20:06 Berlin)

Suchbegriffe: „small transformer trained from scratch non-modular integer addition Fourier features embedding frequencies grokking“,
„training data distribution controls which Fourier frequencies learned arithmetic neural network“, „grokking "non-modular addition"
one-layer network representations learned“.
- Liu et al. 2022, *Towards Understanding Grokking: An Effective Theory of Representation Learning* (https://arxiv.org/abs/2205.10343):
  nicht-modulare Addition, Einbettungen werden linear (Zahlengerade). Kein Dateneingriff zur Frequenzsteuerung.
- Zhou et al. 2024, *Pre-trained LLMs Use Fourier Features to Compute Addition* (https://arxiv.org/abs/2406.03445): Fourier-Merkmale
  stammen aus dem Vortraining; ein von Grund auf trainiertes GPT-2-XL auf Addition hat keine.
- Chen et al. 2026, *Multiplication Beyond Groups* (https://arxiv.org/abs/2607.07066): Multiplikation mit zusammengesetztem Modulus,
  keine Addition, keine Split-Steuerung (Abstract per Abruf geprüft).
- Keine Arbeit gefunden, die bei nicht-modularer Addition über die Trainingsauswahl steuert, welche Frequenzen entstehen.
  Einordnung: #neu/kandidat, vorläufig („nach unserer Suche vom 2026-09-26 nicht gefunden“; nur Abstracts/Suchtreffer geprüft).

## Nachtrag a (Sitzung 13, 2026-09-26 20:16 Berlin, gemessen; **vor jedem Lauf**): Primärgröße trendbereinigt, Lesart eingeschränkt

Unabhängige Prüfung (Claude-Subagent, nur lesend/numpy; Codex ohne Guthaben): kein Blocker, zwei berechtigte Designpunkte. Übernommen:
1. **Zahlengerade leckt in die Ziele.** Eine Rampe in W_E hat nur 89 % ihrer DFT-Leistung bei k ≤ 5 (bei k = 6 noch 36× so viel wie bei
   k = 56). Bei ungleicher Rampenamplitude zwischen F- und G-Lauf erzeugt das ein Schein-Δ ohne Steuerung (nachgerechnet, numpy: Rampe 3:1,
   Ziele 6–10 vs. 40–44: rohes Δ_pow 0.75 ± 0.17; trendbereinigt −0.00 ± 0.31). Wegen der Vertauschbarkeit von F und G kein Bias des Tests,
   aber Rauschen. **Neue Primärgröße (vor jedem Lauf, Kriterien sonst unverändert):** Δ_pow auf dem **trendbereinigten End-W_E**
   (`we_final.npy` bei Schritt 2000; je Spalte die Kleinste-Quadrate-Gerade in a entfernt). Das rohe Δ_pow (bisherige Primärgröße) wird
   als `Delta_pow_raw` berichtet. Arm R ebenfalls trendbereinigt. Die EXP-016-Kalibrierung (8.4) stammt aus modularen Läufen ohne Rampe
   und ist hier nur ein Anhaltspunkt.
2. **Häufigkeiten tragen die Ziele hier stärker** (a/b-Häufigkeitsspektrum: Ziele 1.8× der übrigen Leistung, Arm R 1.06×; in die
   Δ-Formel eingesetzt ≈ 1.0 gegenüber M0 1.28). Ein Urteil *steuerbar* heißt deshalb nur „**der Split steuert** (über Paarstruktur oder
   Häufigkeiten)“. Die Rechnung erster Ordnung ([[experiments/EXP-047-marginal-control/README|EXP-047]] Nachtrag a) gilt auch hier
   (Σ_c des Zielteils = n_a), sagt also kein Häufigkeitssignal im ersten Gradienten voraus; der Beleg dafür kommt aber nur aus EXP-047.
Beim Umbau gefunden: Mein erster Selbsttest für die Trendbereinigung war entartet (beide Läufe skalierte Kopien derselben Welle → Δ ≡ 0)
und hätte die Queue heute Nacht fail-closed gestoppt. Durch numpy-Nachrechnung vor dem Lauf entdeckt und ersetzt (d = 18.3, unabhängig
von der Rampenamplitude bis 1e-13).

## Nachtrag (Sitzung 13, 2026-09-26 20:20 Berlin, gemessen; vor jedem Lauf): nicht-endliche Läufe ungültig

Eine unabhängige Prüfung (Claude-Subagent, EXP-049) fand: Ein divergierter Lauf (NaN in W_E) wäre bisher als gültig gezählt worden und hätte still ein falsches K oder sogar das Urteil *widerspricht* mit p = 0 erzeugt (`one_sided_p` mit NaN gibt 0.0). `analyze.py` wertet einen Lauf mit nicht-endlichem Spektrum bzw. W_E jetzt als **ungültig** (zählt gegen die Mindestzahl gültiger Seeds). Urteilsregeln sonst unverändert.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen (Regel 18c, Sitzung 13, 20:54 Berlin)

**Art:** Pilot/Exploration für Paket A. Bestätigung nur im reservierten Block (Seeds 1000–1099, [[FINDINGS]] „Programm“) nach eingefrorenem Analysemanifest.
**Gesehen:** EXP-016-Spektren (Seeds 10–19) zur Kalibrierung von Δ_pow gesehen (8.4); Literatur zur Zahlengerade (Liu et al. 2022) prägte die Zielwahl k ≥ 6 und die Trendbereinigung (Nachtrag a); die 30 Splits offline angesehen. Keine Läufe der Aufgabe gesehen.

## Ergebnis (Sitzung 20, 2026-09-27, Läufe 03:07–03:10 Berlin, GPU nach bestandenem GPU-001)

Befehl: `python lab/tools/night_program.py` (Stufe EXP-048); Logs `lab/runner/logs/night_20260927T005025_010314Z/EXP-048_*`, Zahlen `summary.json`.
20 gesteuerte Läufe (F/G, Seeds 160–169) + 10 Zufallssplit-Läufe (R), device cuda, Commits f34eeb1/97a3e6a (dazwischen nur Dokumente).

- **Primär (trendbereinigtes Δ_pow, Nachtrag a): Δ̄ 2.23, 10/10 positiv, p 0.00098 → *steuerbar*.**
- Sekundär: rohes Δ_pow 2.12 (p 0.00098); Top-5-Δ 3.4 (p 0.00098); Arm R Log-Verhältnis −0.02 (≈ 0, wie erwartet); linearer Anteil (R²) von W_E im Mittel 0.40.
  Test-Genauigkeit im Mittel 0.23 bei 2000 Schritten (nicht Teil des Urteils; die Aufgabe ist in 2000 Schritten nicht gelernt).
- **Lesart (vorab, Nachtrag a):** *steuerbar* heißt „der Split steuert die Fourier-Leistung in W_E“. Über Paarstruktur oder Häufigkeiten ist hier nicht getrennt (Häufigkeiten
  tragen die Ziele hier stärker als modular). EXP-047 hat für Z₁₁₃ gezeigt, dass die Paarstruktur trägt. Das ist nur eine Übertragung, hier nicht geprüft.
  Der Effekt ist kleiner als modular (Δ_pow 2.2 gegen 8.4 in EXP-016, andere Skala: trendbereinigt). Keine funktionale Aussage.
  Pilot, keine Bestätigung. Erste Stützung von K2 für eine **nicht-modulare** Aufgabe, allerdings vor jedem Lernen der Aufgabe (Test 0.23).

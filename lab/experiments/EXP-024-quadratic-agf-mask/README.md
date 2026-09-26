---
id: EXP-024
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-024: Lernt ein quadratisches Netz auf einem konstruierten Split die *halben* Zielfrequenzen?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N11) · baut auf
[[experiments/EXP-016-engineered-split/README|EXP-016]] und [[BEFUND-split-mechanismus]] auf.

## Anlass (Sitzung 6, 08:40 Berlin, Rechnung ohne Training)

Alternating Gradient Flows (Kunin et al. 2025, https://arxiv.org/abs/2506.06489): Bei kleiner Init wächst zuerst das
Neuron mit dem größten Nutzen. Für das Zwei-Hot-Modell mit quadratischer Aktivation,
f(a,b) = Σ_n w_n (u_n[a] + v_n[b])², und einem **maskierten** Verlust (nur Trainingspaare S) ist der Nutzen bei
optimalem w

    U(u, v) = ‖P g‖,   g_c = Σ_a M(a, c−a) (u_a + v_{c−a})²,   P = Zentrierung über c.

Für ein Frequenz-k-Merkmal u_a = cos(ωka + α), v_b = cos(ωkb + β) enthält (u_a + v_{c−a})² die Terme cos(2ωka + 2α),
cos(2ωk(c−a) + 2β) und cos(ωk(2a − c) + α − β), also Oszillationen mit **2k** entlang der Antidiagonale. Der
maskenabhängige Teil des Nutzens greift deshalb das Masken-Spektrum bei **2k** ab, nicht bei k.
Vorhersage: Ein Split, der Masken-Leistung auf F legt, begünstigt beim quadratischen Netz die Frequenzen
k mit 2k ≡ ±f (mod 113), also die **halben Ziele** H(F) = {fold(57·f)} (57 = 2⁻¹ mod 113).

**Numerische Prüfung der Rechnung** (`utility_scan.py`, 20 EXP-016-Splits, 16 × 16 Phasen je k, 20 s):
Die Top-5 von U(k) enthalten im Mittel **3.25 von 5 halben Zielen**, aber nur **0.2 Ziele** (Zufall 0.45);
Spearman(U, M0 bei 2k) = +0.30, Spearman(U, M0 bei k) = −0.01. Das ist eine Aussage über den Nutzen am Start,
nicht über ein trainiertes Netz. Der Transformer lernt auf denselben Splits die Ziele selbst (EXP-016, 3.9/5).

## Versuch (vorab festgelegt, 2026-09-26 ~08:55 Berlin, vor jedem Training dieses Versuchs)

| Punkt | Festlegung |
|---|---|
| **Frage** | Folgt die Frequenzwahl eines trainierten Zwei-Hot-Netzes mit quadratischer Aktivation den halben Zielen H(F) statt den Zielen F? |
| **H24** | Arm Q (quadratisch): Überlappung der finalen Top-5 mit H(F) > Überlappung mit F |
| **Modell** | `train_twohot.py`: Zwei-Hot-Eingabe, 512 Neuronen, Aktivation x² (Q) bzw. ReLU (R), CE, Vollbatch, AdamW lr 1e-3, wd 1.0, β = (0.9, 0.98), Init-Skala 0.1 (kleine Init, wie die AGF-Theorie voraussetzt), 5000 Schritte |
| **Messgröße** | Top-5 des Fourier-Leistungsspektrums der Eingabegewichte (Σ Neuronen |DFT u|² + |DFT v|², k/p−k zusammengefasst) bei Schritt 5000 |
| **Einheiten** | EXP-016-Splits Seeds 10–19, Arme F und G, **ohne** Seed 12/G (identisch mit Seed 19/F, siehe EXP-016 Nachtrag c) → 19 Splits. Init-Seed = Split-Seed |
| **Primärtest** | Arm Q: d_s = ov(Top-5, H) − ov(Top-5, F) je Split; einseitiger exakter Vorzeichentest (Nullen verworfen) |
| **Entscheidung** | *bestätigt*: p < 0.05 und mittleres ov_H ≥ 2 · *richtungsgleich, n. s.*: d̄ > 0, p ≥ 0.05 · *widerspricht*: d̄ ≤ 0 · < 12 auswertbare Splits (NaN, abgebrochen): *nicht auswertbar* |
| **Arm R (ReLU)** | explorativ, nur berichtet: ov_F und ov_H. Keine gerichtete Vorhersage (ReLU hat einen geraden und einen ungeraden Anteil; die Studie fand für diese Architektur beim ersten Gradienten M0 bei k passend) |
| **Nebenmessungen** | Test-Genauigkeit auf dem Komplement (Generalisiert das quadratische Netz überhaupt?), Spektrum bei Schritt 250 und 1000 |
| **Was dagegen spräche** | ov_F ≥ ov_H im Arm Q: Dann trägt die AGF-Nutzenrechnung am Start die Wahl nicht (z. B. weil ab dem ersten Wachstum andere Terme dominieren) |
| **Budget** | Schätzung aus Smoke; Abbruch bei NaN. Ein Job gleichzeitig, alles über `guarded_run.py` |
| **Smoke** | Nur an eigenem Split Seed 9 (neu erzeugt unter `smoke_splits/`, nicht Teil der Auswertung); geprüft werden nur Laufbarkeit, Zeit, Endlichkeit. Falls der Smoke divergiert, dürfen lr/Init-Skala **vor** der Hauptserie geändert werden (dann hier nachgetragen) |

## Nachtrag a (2026-09-26 ~08:50 Berlin, nach Codex-Review, vor jedem Training dieses Versuchs)

Codex-Review (11 Punkte, Protokoll im [[JOURNAL]], Sitzung 6). Übernommen:
1. **Herleitung unvollständig (übernommen):** Vollständig ist (u_a + v_{c−a})² = 1 + cos(ωkc + α + β) + ½cos(2ωka + 2α)
   + ½cos(2ωk(c−a) + 2β) + cos(ωk(2a − c) + α − β). Der Term cos(ωkc + α + β) wird mit der Paarzahl n_c der
   Antidiagonalen gewichtet und koppelt den Nutzen an das Spektrum von n_c; außerdem ist der Masken-Einfluss auf ‖Pg‖ in
   erster Ordnung linear in der Maske, M0 dagegen quadratisch. Die Aussage „greift M0 bei 2k ab“ ist deshalb eine
   **Näherung**, keine exakte Folgerung. Maßgeblich ist die exakte numerische Nutzenrechnung (`utility_scan.py`), nicht
   die Kurzform. Sie hält einem feineren Phasenraster stand (32 × 32, ohne Duplikat 12/G: 3.26/5 halbe Ziele,
   0.21/5 Ziele; `phase_grid_check.py`).
2. **Biases entfernt:** Ein Bias fügt dem quadratischen Merkmal einen Frequenz-k-Term hinzu. Beide Arme jetzt ohne
   b_in/b_out (Theorie: biasfreie Neuronen). Arm R weicht damit vom Studienmodell `mlp_twohot` ab (explorativ ohnehin).
3. **Messgröße reskalierungsinvariant:** Primär ist jetzt S(k) = Σ_n ‖w_n‖·‖(u_n, v_n)‖^h · (normierte Leistung des
   Neurons bei k), h = 2 (quadratisch) bzw. 1 (ReLU); invariant unter u → s·u, w → w/s^h. Das rohe Eingabespektrum
   und das W_out-Spektrum über c werden nur berichtet.
4. **Gültigkeit:** Ein Lauf zählt nur, wenn alle 5000 Schritte mit endlichen Gewichten liefen (`complete`), und nur
   für die vorgesehenen Einheiten. „Nicht auswertbar“ zusätzlich, wenn weniger als 8 Splits d ≠ 0 haben.
5. **Kontrolle gegen „irgendeine feste Abbildung“ (sekundär, berichtet):** Überlappung mit fold(m·F) für alle anderen
   Multiplikatoren m = 3…55 (m = 56 ≡ −57 ist H selbst) und mit fold(2·F).
Nicht übernommen bzw. als Grenze notiert: Abhängigkeit der Arme F/G desselben Seeds (Vorzeichentest nimmt
Unabhängigkeit an; Grenze). Clipping in `make_split.py` erzeugt eventuell Masken-Oberwellen; die Nutzenrechnung arbeitet
mit den tatsächlichen Masken und schließt das also ein; ein H-Befund belegt trotzdem nicht, dass der AGF-Anfangsmechanismus
die Ursache ist (Alternativen: Landschaft des quadratischen Verlusts, AdamW). Ein positiver Befund heißt nur: Die
Nutzenrechnung sagt die Wahl des trainierten Netzes voraus.

**Neuheit:** vorläufig, siehe [[NOVEL_DIRECTIONS]] N11 (Suche folgt).

## Befehle

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-024-quadratic-agf-mask/utility_scan.py
    sh lab/experiments/EXP-024-quadratic-agf-mask/queue.sh      (jeder Lauf darin über guarded_run.py)
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-024-quadratic-agf-mask/analyze.py

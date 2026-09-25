# EXP-003: Ergebnisse (Sitzung 2, 2026-09-25)

Alle Zahlen stammen aus Auswertungen **gespeicherter** Läufe. Es gab kein neues Training. Code:
`early_predict.py`, `confirm_b.py` und `time_resolved.py` mit den Commits dieser Sitzung.
Umgebung: Python 3.12, torch 2.13.0, numpy 2.5.1, Windows 11. Die Rohwerte stehen in
`features.csv`, `summary.json`, `summary_b.json` und `time_resolved.json`.

## EXP-003 (vorab festgelegt): Exploration Transformer, Bestätigung MLP

Spearman ρ (Merkmal bei ≤ 2000 gegen den Generalisierungsschritt), n = 10 je Gruppe.
In Klammern steht p, zweiseitig per Permutation.

| Merkmal | Transformer (Exploration) | MLP-512 | MLP-572 |
|---|---|---|---|
| F1 test_loss bei 2000 | +0.36 (0.31) | +0.03 (0.95) | +0.33 (0.35) |
| F2 Δ test_loss 1000→2000 | +0.11 (0.77) | +0.12 (0.76) | +0.30 (0.40) |
| F3 log train_loss bei 2000 | +0.07 (0.85) | +0.19 (0.60) | +0.28 (0.43) |
| F4 Parameternorm bei 2000 | +0.43 (0.22) | +0.12 (0.76) | +0.32 (0.37) |
| F5 Norm 2000/500 | +0.46 (0.18) | +0.01 (1.00) | +0.32 (0.37) |
| **F6 W_E-Top-8-Fourier-Konzentration bei 2000** | **−0.71 (0.026)** | **−0.65** (einseitig 0.024) | −0.41 (einseitig 0.11) |

Kandidat ist F6. Nach der vorab fixierten Regel lautet das Urteil **„teilweise“**: bestätigt in
MLP-512, nicht in MLP-572.

## EXP-003b (vorab festgelegt): unberührte Two-hot-MLP (extern, n = 10)

F6 wird hier auf `W_in[:p]` berechnet, das Embedding-Objekt der Studie: ρ = **−0.14**
(einseitig p ≈ 0.35, zweiseitig 0.70). Das Urteil lautet **„richtungsgleich, nicht
signifikant“**, **faktisch also keine Bestätigung**. Beobachtung: Bei 2000 liegt F6 in allen
10 Läufen bei 0.159–0.162, also praktisch auf Init-Niveau (Init ≈ 0.153). Es gibt zu diesem
Zeitpunkt noch kein messbares Signal.

Nebenbefund, **nicht vorab festgelegt** und damit nicht bewertbar (5 Merkmale ohne Korrektur):
In der Two-hot-MLP korrelieren F1 und F2 positiv mit dem Generalisierungsschritt
(ρ = +0.65 und +0.66, zweiseitig p ≈ 0.05 und 0.04).

## EXP-003c (explorativ, alle Daten schon angesehen): F6 über die Zeit

ρ(F6 bei t, Generalisierungsschritt) je Gruppe:

| t | Transformer | MLP-512 | MLP-572 | Two-hot-MLP |
|---|---|---|---|---|
| 0 (Nullprüfung) | −0.27 | −0.24 | −0.10 | −0.65 (p 0.046) |
| 500 | −0.59 | −0.76 | −0.33 | +0.21 |
| 1000 | −0.70 | −0.70 | −0.41 | −0.16 |
| 2000 | −0.71 | −0.65 | −0.41 | −0.14 |
| 4000 | **−0.88** (p 0.001) | −0.64 | −0.24 | −0.09 |
| 6000 | — | −0.61 | −0.46 | −0.33 |
| 8000 | — | −0.68 | −0.58 | −0.40 |
| 10000 | — | — | — | −0.67 (p 0.04) |

(„—“: t liegt bei oder hinter dem frühesten Crossing der Gruppe.)

**Beobachtung.** Das Vorzeichen ist über fast alle 40 Zellen negativ. Der Betrag wächst ungefähr
dann, wenn der Gruppenmittelwert von F6 sich vom Init-Niveau löst. Beim Transformer ist das
früh der Fall (Mittel 0.22 bei 500), bei der Two-hot-MLP spät (0.19 erst ab 8000).

**Interpretation (vorläufig).** F6 verhält sich wie ein **Fortschrittsmaß**: Wer bei gleicher
Schrittzahl strukturell weiter ist, generalisiert früher. Einen Frühindikator mit fester
Vorlaufzeit liefert F6 dagegen nicht. Die Vorlaufzeit hängt von der Architektur ab. Die
Verlustkurven bis 2000 sind in 3 von 4 Gruppen kein brauchbarer Prädiktor. Die interne Struktur
ist es in 2 von 4 Gruppen.

**Vorsicht.**
- Die Zellen sind autokorreliert, und ~40 Tests wurden ohne Korrektur gerechnet.
- Der Init-Wert der Two-hot-MLP „sagt“ mit p = 0.046 etwas voraus. Das ist mit hoher
  Wahrscheinlichkeit Zufall bei Mehrfachtests, weil ein Init-Signal keinen Mechanismus hat. Es
  zeigt aber, wie viel Einzel-p-Werte bei n = 10 wert sind.
- Korrelation ist keine Ursache. Ob die Struktur den Übergang *treibt*, prüft EXP-001 (Eingriff).
- Neuheit ist nicht geprüft. Nanda et al. (2023) beschreiben Fortschrittsmaße für den
  Transformer. Diese Einordnung ist deshalb ausdrücklich vorläufig.

## Nächster Schritt

Die unabhängige Bestätigung an frischen Seeds 10–19 im Transformer (EXP-003d, `CONFIRM_d.md`)
ist vorbereitet. Sie braucht Training, also das Run-Fenster.

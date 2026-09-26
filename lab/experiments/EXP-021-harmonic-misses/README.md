---
id: EXP-021
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-020-data-switch/README|EXP-020]]"]
---
# EXP-021: Sind die „Fehlgriffe“ unter konstruierten Splits zweite Harmonische der Zielfrequenzen? (Bestätigung)

**Status:** vorbereitet, **nicht ausgeführt**, braucht keine eigenen Läufe. Definition fixiert 2026-09-26 06:40 Berlin
(Sitzung 5), bevor einer der unten genannten Läufe existierte.

**Explorativer Anlass** (JOURNAL Sitzung 5, Zyklen 7–11): In EXP-016 Seeds 10–15 waren alle 14 Frequenzen der W_E-Top-5
bei Schritt 2000, die nicht zur Zielmenge gehörten, fold(2k) = min(2k mod 113, 113 − 2k mod 113) einer Zielfrequenz
desselben Arms (Zufall ≈ 1.4). Das Muster wurde erst beim Lesen gefunden, der p-Wert dort gilt nicht.

| | |
|---|---|
| **Fragestellung** | Sind Nicht-Ziel-Frequenzen in der W_E-Top-5 unter konstruierten Splits überzufällig zweite Harmonische der eigenen Ziele? |
| **H21** | Anteil der Nicht-Ziel-Frequenzen, die fold(2k) eines eigenen Ziels sind, liegt über dem Zufall |
| **Läufe (frisch)** | EXP-016 Seeds 16–19, Arme F und G (8 Läufe); EXP-020 Seeds 30–34, nur-F- und nur-G-Lauf (10 Läufe) |
| **K** | Top-5 von W_E bei Schritt **2000** (Spektrum `spectra.npy`) |
| **Zufall** | je Nicht-Ziel-Frequenz q_i = \|H \ T\| / (56 − \|T\|), H = {fold(2k): k ∈ T}; Poisson-Binomial über alle Nicht-Ziel-Frequenzen |
| **Test** | P(X ≥ beobachtete Treffer) unter der Poisson-Binomial-Verteilung, einseitig |
| **Kontrolle** | dieselbe Zählung mit den Zielen des **anderen** Arms desselben Seeds (Erwartung: Zufallsniveau) |
| **Entscheidung** | *bestätigt*: p < 0.01 **und** Trefferanteil ≥ 0.5 · *schwach*: p < 0.05 · sonst *nicht bestätigt* · < 8 Nicht-Ziel-Frequenzen insgesamt: *nicht auswertbar* |
| **Was dagegen spräche** | Trefferanteil nahe Zufall (≈ 0.1): Dann war 14/14 ein Zufallsfund in Seeds 10–15 |
| **Grenzen** | Das Nullmodell behandelt die Nicht-Ziel-Frequenzen als unabhängig; die bekannte (k, 2k)-Neigung der W_E-Top-5 unter Zufallssplits ist ein allgemeiner Hintergrund, keine Alternative zu H21 (H21 behauptet gerade diese Neigung, bezogen auf die Ziele) |

Auswertung: `python lab/experiments/EXP-021-harmonic-misses/analyze.py` (nach EXP-016 16–19 und EXP-020).

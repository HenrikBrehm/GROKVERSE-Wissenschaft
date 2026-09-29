---
id: EXP-114
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/negativ, lm-leiter]
---
# EXP-114: Fehlt die frühe Steuerung im LM wegen der Verdünnung durch Text? (Pilot, 1 Seed)

Zurück: [[LAB]] · [[FINDINGS]] · [[BACKLOG]] (Sitzung 50) · Anlass [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] Nachtrag 1 · [[JOURNAL]] Sitzung 50

**Bezug zu FINDINGS:** offene Frage „Verallgemeinerung von K2 auf Sprachmodelle“ (Programm A, Regel 20e). Exploration (1 Seed, F/G), keine Bestätigung, kein Urteil über K2.

## Vorab (Sitzung 50, 11:48 Berlin gemessen, vor jedem Lauf)

- **Anlass:** In EXP-113 (`answer`, K = 8 Rechensätze je Sequenz, ≈ 34 % Rechen-Tokens) ist Δ_pow bis Schritt 4000 ≈ 0 bei Fakten auf Zufall; im Spielzeugmodell und in Stufe 1 (EXP-102) steuert die Maske schon früh, vor dem Lernen. Weight Decay und Lernrate erklären das nach EXP-103/R1 kaum (BACKLOG Sitzung 50).
- **Hypothese (b) Verdünnung:** Mit gebundenen Embeddings bekommen die Zahl-Zeilen an jeder Textposition einen zielunabhängigen Gradienten (Softmax über alle Tokens); Adam normiert je Koordinate, so schrumpft der Anteil des Maskensignals am Update. Weniger Text → frühe Steuerung kehrt zurück.
- **Aufbau:** unveränderter Trainer `lm_stage2.py` (Stand 7a63509f), Seed 3862, P1-Splits seed3802 F/G, Testmenge wie EXP-113, `--loss answer`, **`--arith-facts 19`** (≤ 19 wegen Kontext 256: längste Schablone 13 Tokens je Satz; Rechenanteil ≈ 79 %), 4000 Schritte, GPU-Dienst (`jobs.txt`, `raw_k19`). Vergleich: EXP-113 `answer` Seed 3862 (K = 8), gleiche Init, gleiche Splits.
- **Störgröße:** K = 19 zeigt ≈ 2.4× so viele Fakten je Schritt. Verglichen wird deshalb (1) je Lauf-Paar die Reihenfolge von Steuerung und Faktenlernen (unabhängig von der Zeitachse) und (2) Δ_pow bei gleicher Zahl gesehener Fakten (Faktenrunden aus den Läufen, linear interpoliert).
- **Lesarten (vorab):** **„Verdünnung gestützt“**: bei K = 19 erreicht Δ_pow > 1 einen Snapshot, an dem noch nicht beide Läufe Trainingsfakten ≥ 0.1 haben (Steuerung vor dem Lernen), **und** bei gleicher Faktenzahl liegt Δ_pow(K 19) über Δ_pow(K 8) an allen gemeinsamen Punkten bis zum Lernbeginn von K 8. **„Verdünnung nicht gestützt“**: bei K = 19 bleibt Δ_pow ≤ 1 bis zum Lernbeginn (wie H-folgt). Sonst „unklar“. Lernt K = 19 bis 4000 keine Fakten und bleibt Δ_pow ≤ 1: „nicht gestützt (Budget)“.
- **Was dagegen spräche:** siehe „nicht gestützt“; dann bleiben Tiefe/Warmup/Minibatch-Struktur als Kandidaten.
- **Budget/Abbruch:** ≈ 0.3 s/Schritt unter Last → ≈ 20–25 min je Lauf; harte Grenze 120 min (Dienst). Abbruch bei NaN (Trainer) oder Absturz.
- **Bereits gesehene Daten:** EXP-113 `answer` Seed 3862 bis Schritt 4000 (Δ_pow ≈ 0), EXP-105-Pilot, EXP-102/103, R1. Davon beeinflusst: die Frage selbst und die Wahl K = 19.
- **Auswertung:** `analyze.py` (vor dem Ergebnis geschrieben), liest die fertigen Läufe von EXP-114 und die Snapshots von EXP-113 (`answer`, Seed 3862; braucht dessen fertige Läufe).


## Ergebnis (Sitzung 50, 12:28 Berlin gemessen; Exploration, 1 Seed)

Beide Läufe fehlerfrei (Dienst, 2132 s / 2292 s). Beide lernen die Fakten und generalisieren: Trainingsfakten 1.000 / 1.000, zurückgehaltene Fakten **0.983 / 0.991** bei 4000 Schritten, Generalisierung (≥ 0.95) bei Schritt 3000 in beiden. Δ_pow (Snapshots alle 250 Schritte): ≤ 0.03 bis 1250, 0.12 bei 1500, 0.70 bei 1750 (Trainingsfakten 0.030 / 0.033), **3.62 bei 2000** (Trainingsfakten 0.80 / 0.70), danach langsam steigend bis **5.60 bei 4000**. s_learn = s_steer = 2000.
**Lesart (vorab-Regel):** Die K-19-Hälfte der Regel entscheidet allein: Δ_pow > 1 wird nicht vor dem Faktenlernen erreicht (s_steer = s_learn), und vor s_learn bleibt Δ_pow ≤ 1 (Maximum 0.70) → **„Verdünnung nicht gestützt“**. Der Vergleich bei gleicher Faktenzahl mit EXP-113 (K = 8) wird mit `analyze.py` nachgereicht, sobald EXP-113 fertig ist; er kann die Lesart nicht mehr zu „gestützt“ machen.
**Beschreibend, wichtig für die Leiter:** (1) Auch mit ≈ 79 % Rechen-Tokens kommt die Steuerung erst mit dem Faktenlernen (innerhalb der 250-Schritt-Auflösung gleichzeitig; ein kleiner Anstieg auf 0.70 liegt kurz davor), anders als im Spielzeugmodell, wo Δ_pow ≈ 3 schon bei Schritt 250 erreicht ist. Die Verdünnung durch Text erklärt den Unterschied also nicht. (2) **Wenn das LM die Fakten lernt, steuert die Faktenauswahl die Zahl-Embeddings deutlich** (Δ_pow 5.60 bei 4000, zurückgehaltene Fakten ≈ 0.98): die erste Stufe-2-Konfiguration, in der K2 in einem kleinen LM sichtbar wird (1 Seed, bekannte Splits, Exploration). (3) Mit weniger Text lernte das Modell die Fakten nach ≈ 1.2 Mio. gezeigten Fakten (≈ 317 Runden je Fakt); EXP-113 (K = 8) hatte bei Schritt 6500 schon ≈ 1.7 Mio. gezeigt und noch nicht gelernt: mit mehr Text lernte dieses Modell langsamer je gezeigtem Fakt (Vergleich zweier Konfigurationen an 1 Seed, die sich auch in Fakten je Schritt unterscheiden; keine Ursachenaussage).
**Nicht gezeigt:** keine Aussage über andere Seeds, über den Arm mit Verlust auf allen Positionen oder über kleinere Rechenanteile; die Ursache des späten Einsetzens der Steuerung bleibt offen (Kandidaten: Tiefe, Warmup, Minibatch-Struktur, Wechselwirkung mit dem Faktenlernen selbst).

## Korrektur (Sitzung 50, 12:52 Berlin gemessen)

Der Satz „anders als im Spielzeugmodell, wo Δ_pow ≈ 3 schon bei Schritt 250 erreicht ist“ verglich die Steuerung mit der **Test**-Generalisierung. Misst man „Faktenlernen“ wie hier als **Trainings**genauigkeit ≥ 0.1, setzen auch im Spielzeugmodell Steuerung und Lernen zusammen ein (EXP-103 Teil A, 50 Seeds, post hoc: Median s_learn = s_steer = 75 Schritte, Steuerung vorher in 25/50; `toy_order_s50.py/.json`). Der Unterschied zum LM liegt in der Dauer bis zum Lernbeginn, nicht in der Reihenfolge. Die Lesart „Verdünnung nicht gestützt“ bleibt (sie betrifft nur die Frage, ob weniger Text die Steuerung vor das Lernen zieht).

## Nachtrag (Sitzung 51, 14:13 Berlin gemessen; post hoc, Exploration): Kopplung über die Lernrate

`toy_order_lr_s51.py/.json` (Lesarten vor dem Lauf committet): In drei Spielzeug-Armen mit gleichem lr·wd (lr 2e-3 / 1e-3 / 5e-4, Seeds 1000–1009 gepaart) verschiebt sich der Lernbeginn (Trainingsgenauigkeit ≥ 0.1) um ×3.2 (Median 29 / 50 / 92 Schritte), der Steuerungsbeginn (Δ_pow > 1) folgt jeweils ≈ 10–17 % später (Mediane) (Median 33 / 58 / 101). Gepaarte Differenz von ln(t_steer/t_learn) zwischen lr 2e-3 und 5e-4: +0.046 [0.026, 0.066] → Lesart **„coupled“**. Grenze: Eine Lernratenänderung verschiebt die ganze frühe Dynamik, gemeinsames Wandern zweier Ereignisse beweist keine Abhängigkeit. Trennschärfer ist der LM-Vergleich K = 19 gegen K = 8 (gleicher Optimierer, Lernbeginn ≈ 2000 gegen ≈ 8500, Steuerung folgt jeweils; 1 Seed je Einstellung).

## Vergleich bei gleicher Faktenzahl (Sitzung 51, 15:04 Berlin gemessen; `analyze.py` unverändert seit Sitzung 50)

EXP-113 `answer` Seed 3862 ist fertig (16 000 Schritte; zurückgehaltene Fakten 0.983 / 0.950, Generalisierung bei 11 500 / 11 750). `analyze.py` → **„Verdünnung nicht gestützt“** (wie nach der K-19-Hälfte erwartet; `k19_steer_before_learn` = false, `k19_above_k8_all` = false). Beschreibend (`summary.json`): Bei gleicher Zahl gezeigter Fakten liegt Δ_pow bis ≈ 0.9 Mio. Fakten in beiden Einstellungen bei ≈ 0 (≤ 0.12). K = 19 lernt bei 1.22 Mio. gezeigten Fakten (Schritt 2000), K = 8 erst bei 2.30 Mio. (Schritt 9000; Steuerungsbeginn einen Snapshot früher, 8500, Δ_pow 2.05). Mit mehr Text braucht dieses Modell also ≈ 1.9× so viele Fakten-Wiederholungen und ≈ 4.5× so viele Schritte bis zum Lernbeginn (1 Seed, zwei Konfigurationen, die sich auch in Fakten je Sequenz unterscheiden; keine Ursachenaussage). Am Ende steuert auch K = 8 deutlich: Δ_pow 7.00 bei 16 000 (K = 19: 5.60 bei 4000; ungleiche Budgets). Für H-folgt (EXP-113 Nachtrag 1) zählt dieses Paar als „Steuerung vor der 0.1-Schwelle“; ausgewertet wird dort erst mit allen Paaren.

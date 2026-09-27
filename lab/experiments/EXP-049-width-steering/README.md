---
id: EXP-049
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, befund/positiv]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-045-mlp-steering/README|EXP-045]]", "[[experiments/EXP-027-width-selection/README|EXP-027]]", "[[experiments/EXP-048-intadd-steering/README|EXP-048]]"]
---
# EXP-049: Hält die Datensteuerung (K2) in einem 4× breiteren Transformer?

**Status:** abgeschlossen 2026-09-27 (Sitzung 20, GPU), Ergebnis unten. Ursprünglich: vorbereitet, nicht ausgeführt, ungetestet (Sitzung 13, 2026-09-26, außerhalb des Fensters).
Festgelegt vor jedem Lauf. Zurück zu [[LAB]] · [[FINDINGS]].

## Bezug zu [[FINDINGS]]

Zielt auf die **größte offene Frage** (gilt K2 über die eine Einstellung hinaus?), Teil „größere Modelle“ aus Regel 15c.
Alle K2-Belege stammen vom Transformer der Studie mit d_model = 128. [[experiments/EXP-027-width-selection/README|EXP-027]] prüfte Breite
nur im x²-MLP (dort *widerspricht*); [[experiments/EXP-045-mlp-steering/README|EXP-045]] prüft eine andere Architektur, nicht die Größe.
Ein breiteres Netz hat Platz für viel mehr Frequenzen (Morwani et al. 2023: ≥ 4(p−1) Neuronen für alle); es muss also weniger auswählen.
Wenn die Steuerung vor allem durch die Knappheit entsteht, sollte sie bei 4× Breite schwächer werden.

## Aufbau

- **Aufgabe/Daten:** Addition mod 113, EXP-016-Konstruktion (ε = 2, 3831 Paare), neue Seeds 170–179, Arme F und G (disjunkte
  Zielmengen, je 5 aus k = 1..56). Splits über die Funktionen von [[experiments/EXP-047-marginal-control/README|EXP-047]]
  (`SeedSequence`, keine geteilten Ströme; Abgleich: Seed 150 reproduziert die EXP-047-Datei exakt). Offline: Ziele = M0-Top-5 in
  **20/20** Splits, Zielanteil 0.183–0.205.
- **Breiten:** d = 128 (Studie: 4 Köpfe × 32, d_mlp 512) und **d = 512** (4 Köpfe × 128, d_mlp 2048; ≈ 3.3 M statt 0.23 M Parameter).
  Sonst identisch (Preset arch25k, AdamW lr 1e-3, wd 1, Full Batch, Init-Skala s/√d je Matrix wie im Modellcode). Derselbe Split und
  derselbe Init-Seed für beide Breiten; W_E ist bei der breiten Variante eine andere Zufallsmatrix (andere Form).
- **Code:** `width_train.py` (schlankes Skript nach dem Muster von EXP-048 `intadd_train.py`; `freq_ban.py` bleibt unberührt).
- **K / Messgröße:** DFT-Leistung von W_E (Zeilen 0..112) bei Schritt 2000, k = 1..56.

| | |
|---|---|
| **Fragestellung** | Gibt ein konstruierter Split auch bei 4× Breite vor, welche Frequenzen in W_E entstehen? |
| **H49** | Δ̄_pow(d = 512) > 0 |
| **Primärgröße** | Δ_pow,i = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] im breiten Netz (wie [[experiments/EXP-048-intadd-steering/README|EXP-048]]; an EXP-016 kalibriert: 8.4, 10/10) |
| **Test** | einseitiger Vorzeichen-Permutationstest über die gültigen Seeds (exakt, 2^n) |
| **Gültig** | alle vier Läufe eines Seeds `completed`, 2000 Schritte, cuda, Split-Hash = Inhalt der .npy, d_model laut result.json wie verlangt; < 8 gültige Seeds: *nicht auswertbar* |
| **Entscheidung** | *steuerbar*: Δ̄_pow > 0, p < 0.05 · *richtungsgleich, n. s.*: Δ̄_pow > 0, p ≥ 0.05 · *widerspricht*: Δ̄_pow ≤ 0 |
| **Sekundär (nur berichtet)** | Δ_pow bei d = 128 (GPU-Replikation von EXP-016 an frischen Seeds); gepaarte Differenz Δ_pow(512) − Δ_pow(128) mit Vorzeichen-Test (beschreibend); Top-5-Δ je Breite; effektive Zahl genutzter Frequenzen exp(Entropie des Leistungsanteils) je Breite; Train-/Test-Genauigkeit, gen-Schritt |
| **Erwartung** | Δ̄_pow(512) > 0, eher kleiner als bei d = 128, weil ein breites Netz mehr Frequenzen zugleich halten kann |
| **Was dagegen spräche** | Δ̄_pow(512) ≤ 0: K2 ist eine Eigenheit knapper Modelle (Auswahl durch Knappheit) |
| **Grenzen** | Nur eine größere Breite, keine Tiefe (der Modellcode kennt nur eine Schicht). Bei gleicher lr ist das breite Netz anders parametrisiert (Standard-Init, kein μP); eine Änderung kann auch an der effektiven Lernrate liegen. 2000 Schritte: Auswahl vor der Endlösung |
| **Budget** | 40 Läufe à 2000 Schritte auf der GPU; die breiten Läufe sind ≈ 14× größer, auf der RX 7900 XT trotzdem klein (Full Batch 3831 × 3 Token). Schätzung ≤ 5 min pro Lauf, zusammen ≲ 60 min bei J = 4 |

## Befehle

```
python lab/experiments/EXP-049-width-steering/make_split.py --seed I      # reine Rechnung, erledigt (170–179)
sh lab/experiments/EXP-049-width-steering/queue.sh J                      # Selbsttest, Smoke je Breite, 40 Läufe, Auswertung
python lab/tools/guarded_run.py -- python lab/experiments/EXP-049-width-steering/analyze.py
```

## Nachtrag (Sitzung 13, 2026-09-26 20:20 Berlin, gemessen; vor jedem Lauf): nicht-endliche Läufe ungültig

Eine unabhängige Prüfung (Claude-Subagent, EXP-049) fand: Ein divergierter Lauf (NaN in W_E) wäre bisher als gültig gezählt worden und hätte still ein falsches K oder sogar das Urteil *widerspricht* mit p = 0 erzeugt (`one_sided_p` mit NaN gibt 0.0). `analyze.py` wertet einen Lauf mit nicht-endlichem Spektrum bzw. W_E jetzt als **ungültig** (zählt gegen die Mindestzahl gültiger Seeds). Urteilsregeln sonst unverändert.

*Weitere Einschränkung aus derselben Prüfung:* Bei Standard-Init hat W_E je Frequenz etwa gleich viel Init-Leistung, unabhängig von d, während Adam-Schritte je Gewicht breitenunabhängig sind. Die gelernte Leistung wächst also etwa mit d, und das breite Netz ist weniger von Init-Rauschen verdünnt. Das hebt Δ_pow(512) mechanisch an und wirkt gegen die Erwartung „kleiner bei 512“. Ein *größeres* Δ_pow bei 512 widerlegt die Knappheitsidee deshalb nicht. Das Primärurteil (Vorzeichen bei d = 512, Log-Verhältnisse im selben Netz, skaleninvariant) ist davon nicht betroffen. J stammt aus dem Durchsatztest mit d = 128; das betrifft nur die Laufzeit.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen (Regel 18c, Sitzung 13, 20:54 Berlin)

**Art:** Pilot/Exploration für Paket A. Bestätigung nur im reservierten Block (Seeds 1000–1099, [[FINDINGS]] „Programm“) nach eingefrorenem Analysemanifest.
**Gesehen:** EXP-016-Kalibrierung von Δ_pow gesehen; Splits der Seeds 170–179 offline (Ziele = M0-Top-5). Keine Läufe mit d_model 512 gesehen.

## Ergebnis (Sitzung 20, 2026-09-27, Läufe 03:13–03:22 Berlin, GPU nach bestandenem GPU-001)

Befehl: `python lab/tools/night_program.py` (Stufe EXP-049); Logs `lab/runner/logs/night_20260927T005025_010314Z/EXP-049_*`, Zahlen `summary.json`. 40 Läufe, device cuda, Commits b9107dc/5e4dcae (dazwischen nur EXP-055-Code und Dokumente, Trainer unverändert).

- **Primär (d = 512): Δ̄_pow 7.82, 10/10 positiv, p 0.00098 → *steuerbar*.**
- Sekundär: d = 128 (GPU-Replikation von EXP-016 an frischen Seeds 170–179): Δ̄_pow 8.66, 10/10, p 0.00098 (EXP-016: 8.4). Gepaarte Differenz 512 − 128: −0.83
  (beschreibender Vorzeichentest p 0.003, also etwas kleiner bei 512, wie vorab erwartet. Die Einschränkung aus der Prüfung wirkte eher dagegen). Top-5-Δ 8.1 (128) / 9.3 (512).
  Effektive Frequenzzahl 8.1 / 10.9. Test-Genauigkeit 1.00 / 1.00.
- *Lesart:* K2 ist keine Eigenheit knapper Modelle. Das 4× breitere Netz nutzt etwas mehr Frequenzen, wird aber genauso stark gesteuert. Pilot, keine Bestätigung. Nur Breite, keine Tiefe.

---
id: R7-registrierung-entwurf
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, lab/paper]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-078-two-layer-steering/README|EXP-078]]", "[[confirm/P4_REGISTRATION_DRAFT|P4]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[paper/STATUS]]"]
---
# R7-Bestätigung: K2 im 2-Schicht-Transformer (ENTWURF Fassung 2, nicht eingefroren, Code ungetestet)

Zurück zu [[paper/STATUS]] · [[FINDINGS]] Grenze 3 („keine tiefere Architektur bestätigt“), Programm **A** (Verallgemeinerung, Regel 15c) · Pilot: [[experiments/EXP-078-two-layer-steering/README|EXP-078]].
Entwurf Sitzung 33 (2026-09-27, Fenster zu), **vor jedem EXP-078- und R7-Lauf**. Code: `lab/tools/confirm_r7.py` (Muster `confirm_p4.py`, gemeinsames `bound_block`).

## Warum

Die erste Gutachterfrage an das Paper lautet „nur eine Schicht?“. EXP-078 prüft das heute Nacht als Pilot an den bekannten P1-Seeds 1000–1009. Fällt der Pilot positiv aus, braucht das Paper eine Bestätigung an frischen Seeds, sonst bleibt „2 Schichten“ ein Pilot. R7 legt diese Bestätigung **jetzt** fest, bevor irgendein 2-Schicht-Ergebnis gesehen ist. Nur die Fallzahl hängt vom Piloten ab, und zwar über eine hier festgelegte Regel.

## Tor (vorab; **aufgehoben in Fassung 2**, siehe unten)

R7 wird **nur** eingefroren, wenn EXP-078 die vorab festgelegte Lesart *„Steuerung überträgt sich auf zwei Schichten (Pilot)“* ergibt (Δ̄ ≥ 1 und p < 0.05). Bei *keine Steuerung* entfällt R7; das Paper berichtet die Grenze. Bei *unklar* entfällt R7 ebenfalls, und es gibt keinen Nachtrag am Piloten (Regel 15b).

## Aufbau

| Punkt | Festlegung |
|---|---|
| Hypothese H7 | Konstruierte Splits steuern die W_E-Frequenzen auch im 2-Schicht-Transformer: Δ_pow bei Schritt 2000 > 0, mit Mindesteffekt 1 (wie P1) |
| Modell | `two_layer.py` aus EXP-078 (Rezept der Studie, zwei Attention+MLP-Blöcke, d 128, 4 Köpfe, MLP 512), Trainer `train2l.py` (schlanker Trainer `repro/train.py` mit getauschter Modellfabrik), AdamW lr 1e-3, wd 1, Vollbatch, add 113 |
| Splits | P1-Konstruktion (`confirm_splits.build`, ε = 2), **Versuchs-ID 10** (eigene Zufallsströme; 1–9 und 98 sind vergeben), Arme F/G mit gleicher Init je Seed |
| Einheiten | Seeds **2900 … 2900 + n − 1** (Block 2900–2929 reserviert, vorher ungenutzt; geprüft Sitzung 33 an allen Registrierungen, READMEs und dem JOURNAL) |
| n | aus dem Piloten nach der Regel `n_rule` (unten); erlaubt 10/15/20/25/30 |
| Läufe | 2L: 2n × 10 000 Schritte (primär 2000, sekundär 10 000); 1L-Vergleich: 2n × 2000 Schritte mit dem schlanken Trainer, gleiche Seeds und Splits. GPU, `--threads 1` |
| **Primär** | Δ_pow(2L) bei 2000: exakter einseitiger Vorzeichen-Permutationstest über n Seeds **und** 95-%-Bootstrap-KI. *Bestätigt* nur bei p < 0.05 **und** KI-Untergrenze ≥ 1. Eine Hypothese, keine Familienkorrektur |
| Nicht auswertbar | ein fehlender, ungebundener oder defekter 2L-Lauf (falsches Feld, falscher Split, fehlendes Spektrum, nicht endlich) → ganzes Urteil *nicht auswertbar* |
| Sekundär (nur berichtet) | Δ_pow(2L) bei 10 000; gepaarte Differenz Δ_pow(2L) − Δ_pow(1L) bei 2000 (gleiche Seeds, Splits und W_E-Init); Zahl der Einheiten mit beiden 2L-Armen generalisiert |
| Budget | 2L ≈ 0.06 s/Schritt bei 10 parallel (Schätzung EXP-078; wird dort gemessen). n = 15: 30 × 10 000 → ≈ 30 min; 1L ≈ 2 min |

**Regel für n (vorab):** Aus den Pilotwerten Δ_pow(2000) von EXP-078: angenommener Effekt = **halber** Pilotmittelwert (Winner's Curse, Seeds bekannt), Streuung = Pilot-SD. Gewählt wird das kleinste n ∈ {10, 15, 20, 25, 30}, dessen simulierte Power (400 Normalziehungen) für das KI-Kriterium ≥ 0.8 ist. Erreicht kein n die 0.8, gilt n = 30. Das ist ein Surrogat: Der Vorzeichentest wird nicht mitsimuliert, weil er bei einer KI-Untergrenze ≥ 1 > 0 praktisch immer erfüllt ist. Befehl: `python lab/tools/confirm_r7.py --n-rule lab/experiments/EXP-078-two-layer-steering/summary.json` (reine Rechnung auf der Zusammenfassung).

## Einfrieren (Reihenfolge, frühestens nach EXP-078)

1. EXP-078 auswerten; Lesart muss *überträgt* sein (Tor).
2. `--n-rule` rechnen, `N_UNITS` in `confirm_r7.py` setzen (einzige Codeänderung), Codex-Prüfung (Regel 18c).
3. `guarded_run.py -- python lab/tools/confirm_r7.py --selftest` (grün).
4. Manifest `lab/confirm/R7_manifest.json` = `REGISTERED` + `"python"` (GPU-Interpreter) + `"seeds"` (2900 … 2900 + n − 1) + `"registration"` + `"code_sha256"` aus `--hash-code`; committen, Commit-ID ins Feld `commit`, erneut committen.
5. `--splits`, dann `python lab/tools/confirm_r7.py --jobs lab/confirm/R7_manifest.json > lab/confirm/R7_jobs.txt` (ohne Wächter, reiner Druckmodus); Smoke = erste Jobzeile allein über `parallel_queue.py`, `--analyze` nur als Ladertest; dann der Block über `parallel_queue.py --workers 10`, dann `--analyze`.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

Keine 2-Schicht-Läufe. Gesehen sind P1 (1 Schicht, add 113: Maß, Schritt 2000, ε = 2, Mindesteffekt 1 übernommen), die Piloten EXP-049 (Breite) und EXP-045 (MLP), beide steuerbar. Der EXP-078-Pilot bestimmt nur das Tor und n, beides nach der Regel oben.

## Grenzen (vorab)

Nur add 113; nur W_E (Frequenzen in Schicht 2 nicht gemessen); ohne LayerNorm wie die Studie; kein Datenwechsel, also K4 in zwei Schichten weiter offen. Der schlanke Trainer ist erst nach seiner Gleichwertigkeitsprüfung (Nacht 27./28., [[paper/repro/README]]) zu verwenden. Ein Fehlschlag dort stoppt R7.

## Technische Änderung für R7 (Sitzung 33)

`lab/paper/repro/train.py` schreibt jetzt `"status": "completed"` in die result.json, weil `bound_block` nur so markierte Läufe bindet. Die Datei gehört zu keinem eingefrorenen Block (geprüft: kein `code_sha256` nennt sie). `train2l.py` übernimmt das Feld, weil es die result.json nur ergänzt.

## Fassung 2 (Sitzung 33, 22:34 Berlin gemessen, vor jedem EXP-078- und R7-Lauf): Codex-Prüfung eingearbeitet

Codex-Prüfung [[confirm/R7_codex_review_s33.txt]]: 1 Blocker, 4 Major. Alle habe ich am Code nachgeprüft und alle übernommen. **Diese Fassung ersetzt die widersprechenden Stellen oben.**

1. **Blocker (übernommen):** `confirm_p1.sign_flip_p` ist nur bis n = 20 exakt, darüber Monte Carlo. Die Registrierung verspricht einen exakten Test. → **n ∈ {10, 15, 20}**, und `confirm_r7.exact_sign_flip_p` zählt alle 2^n Vorzeichen vollständig ab. Der Selbsttest vergleicht das mit `confirm_p1` bei n = 5/10/15 und prüft p = 2^−20 bei n = 20.
2. **Major (übernommen):** Die n-Regel simulierte nur das KI-Kriterium, und meine Begründung dafür war falsch. Codex' Gegenbeispiel: n = 10 mit vier sehr großen positiven und sechs kleinen negativen Werten hat eine KI-Untergrenze > 1, aber exakt p = 1/16. Es steht jetzt als Fall im Selbsttest. → Die Regel simuliert das **echte Doppelkriterium** (exakter Vorzeichentest und Bootstrap mit 10 000 Ziehungen wie in der Auswertung), mit **1000** äußeren Simulationen statt 400. Sonst bleibt sie gleich (halber Pilotmittelwert, Pilot-SD, kleinstes n mit Power ≥ 0.8, sonst das größte, jetzt 20).
3. **Major (übernommen):** Pilot-Zusammenfassung und n waren nicht gebunden. → `--n-rule` prüft die EXP-078-Zusammenfassung (10 gültige Einheiten, Seeds 1000–1009, endliche Werte, keine Probleme) und gibt einen Block `"pilot"` aus: Pfad, sha256, Lesart, Mittel, SD, `n_units`. Der Block kommt ins Manifest. `--splits` und `--analyze` rechnen ihn aus der Datei neu und verlangen Gleichheit mit dem Manifest und mit `N_UNITS`. `EXP-078/analyze.py` steht in der Code-Hash-Liste.
4. **Major (übernommen):** Der schlanke Trainer hielt nicht fest, welche Bytes er gelesen hat. → `repro/train.py` liest jede Indexdatei einmal als Bytes, speichert deren sha256 (`input_sha256`) und lädt aus genau diesen Bytes. Die Auswertung verlangt, dass der Hash dem registrierten Split entspricht, und prüft den Split-Pfad im `argv` jetzt exakt statt nur über den Dateinamen.
5. **Major (übernommen): kein Tor mehr, symmetrisches Design.** R7 wird eingefroren, sobald EXP-078 mit allen 10 Einheiten gültig gelaufen ist, **unabhängig von seiner Lesart**. So bekommt auch ein negativer oder unklarer Pilot eine Prüfung an frischen Seeds. Dazu kommt eine zweite registrierte Lesart: **Bootstrap-KI-Obergrenze < 0.5 → „keine Steuerung von Belang bestätigt“** (Äquivalenzsinn; 0.5 = Grenze „keine Steuerung“ des Piloten). **Schritt:** Primär bleibt 2000 wie in P1, damit gleiche Schrittzahlen verglichen werden. Die Aussage im Paper gilt deshalb ausdrücklich nur „bei gleicher Schrittzahl“. 10 000 bleibt sekundär und kann H7 nicht bestätigen; eine Steuerung, die erst dort auftritt, würde als Beobachtung berichtet.

**Einfrieren (ersetzt die Liste oben):** (1) EXP-078 läuft vollständig (10/10 gültig). (2) `python lab/tools/confirm_r7.py --n-rule lab/experiments/EXP-078-two-layer-steering/summary.json` (reine Rechnung auf der committeten Zusammenfassung; mit n = 20 ≈ Minuten) → `N_UNITS` im Code setzen. (3) Selbsttest über den Wächter (grün). (4) Manifest = `REGISTERED` + `"python"` + `"seeds"` (2900 … 2900 + n − 1) + `"pilot"` (Ausgabe von 2) + `"registration"` + `"code_sha256"`; committen, Commit-ID eintragen, erneut committen. (5) `--splits`, `--jobs` ohne Wächter, Smoke mit der ersten Jobzeile, Block, `--analyze`. Eine Codex-Nachprüfung der geänderten Punkte vor dem Einfrieren (Regel 18c).

---
id: EXP-078
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[experiments/EXP-049-width-steering/README|EXP-049]]", "[[confirm/P4_REGISTRATION_DRAFT|P4]]", "[[paper/STATUS]]", "[[JOURNAL]]"]
---
# EXP-078: Steuert die Split-Zusammensetzung auch in einem 2-Schicht-Transformer die gelernten Frequenzen? (PILOT)

Zurück zu [[LAB]] · [[FINDINGS]]: Grenze 3 („keine tiefere Architektur bestätigt“), Programm **A** (Verallgemeinerung, Regel 15c) · Paper: Gutachterfrage „nur eine Schicht?“ ([[paper/STATUS]] a/b).
Festgelegt 2026-09-27, Sitzung 26, **vor jedem EXP-078-Lauf** (Läufe frühestens ab 00:00). **Pilot/Exploration**, 10 bekannte Seeds, kein Bestätigungsurteil.

## Frage und Konkurrenzmodelle

K2 ist für den 1-Schicht-Transformer bestätigt (P1), dazu Piloten für 4× Breite (EXP-049) und ein MLP (EXP-045). Tiefe ist ungeprüft.
- **(überträgt sich)** Die Paarmaske wirkt über den ersten W_E-Gradienten (Theorie erster Ordnung, [[paper/draft]] §5); eine zweite Schicht ändert den Weg vom Ausgang zu W_E, nicht die Paarmaske → Δ_pow deutlich > 0.
- **(verschwindet)** Mit zwei Schichten wählen die Frequenzen andere Mechanismen (z. B. die zweite Schicht rechnet mit Frequenzen, die W_E nur weiterreicht; Init-Lotterie in mehr Parametern) → Δ_pow ≈ 0.

## Aufbau

- **Modell** (`two_layer.py`, neu, laboreigen; der Studiencode bleibt unverändert): Rezept der Studie (ohne LayerNorm, ReLU-MLP, kausale Attention, Vorhersage an „=“), zwei Attention+MLP-Blöcke,
  d_model 128, 4 Köpfe, MLP 512. **Init:** W_E, W_pos, Schicht 1 und W_U werden in derselben Reihenfolge wie im 1-Schicht-Modell gezogen und sind bei gleichem Seed **identisch** mit dem P1-Lauf
  (Selbsttest prüft das); Schicht 2 danach. So ist je Seed ein gepaarter Vergleich mit dem eingefrorenen P1-Wert möglich.
- **Trainer** `train2l.py`: der schlanke Trainer `lab/paper/repro/train.py` mit ausgetauschter Modellfabrik (sonst identisch: AdamW lr 1e-3, wd 1, Vollbatch, arch25k), kein Wechsel.
  Achtung: `repro/train.py` ist bis zur Gleichwertigkeitsprüfung (heute Nacht) ungetestet; EXP-078 erst danach starten.
- **Splits:** die eingefrorenen P1-Splits add 113 (Versuch 1, ε = 2), Seeds **1000–1009** (bekannt, daher Pilot), Arme F und G. 20 Läufe à 10 000 Schritte, GPU, 1 Thread (`jobs.txt`).
- **Maß:** Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] der W_E-Leistung (wie P1).

| | |
|---|---|
| **Primär** | Δ_pow bei Schritt 2000 (wie P1), Mittel über 10 Seeds, einseitiger exakter Vorzeichentest, Bootstrap-KI |
| **Lesart vorab** | Δ̄ ≥ 1 und p < 0.05 → *Steuerung überträgt sich auf zwei Schichten (Pilot)* · Δ̄ < 0.5 oder p ≥ 0.2 → *keine Steuerung in zwei Schichten (Pilot)* · sonst *unklar* · < 8 gültige Seeds → *nicht auswertbar* |
| **Sekundär (nur berichtet)** | Δ_pow bei 10 000; gepaarte Differenz 2 Schichten − 1 Schicht bei 2000 (P1-Wert desselben Seeds, gleiche W_E-Init und gleiche Splits); Testgenauigkeit und Generalisierungsschritt je Arm |
| **Gültig** | result.json mit Seed, 10 000 Schritten, Gerät cuda, Modellkennung EXP-078; Spektren bei 2000 und 10 000 endlich und positiv |
| **Was dagegen spräche** | Δ̄ ≈ 0 bei 2000: Die Steuerung wäre an die 1-Schicht-Architektur gebunden; das wäre für das Paper eine wichtige Grenze und käme so hinein |
| **Grenzen** | Pilot, bekannte Seeds, 10 Einheiten; nur add 113; nur W_E (Frequenzen in Schicht 2 nicht gemessen); ohne LayerNorm wie die Studie; kein Datenwechsel (K4 in zwei Schichten bleibt offen) |
| **Budget** | 20 × 10 000 Schritte; geschätzt ≈ 0.06 s/Schritt bei 10 parallel (doppelte Tiefe gegenüber ≈ 0.03 für 1 Schicht) → ≈ 20 min |

## Literatur (Suche 2026-09-27, Sitzung 26, WebSearch)

„grokking modular addition two-layer transformer which Fourier frequencies learned depend on training subset data selection“: Treffer zu Fourier-Merkmalen in 2-Schicht-Netzen und zur Init-Lotterie
(He et al. 2026a, arXiv 2602.16849), Spektren je Kopf und Schicht (arXiv 2606.17399, schon in [[paper/related_work]]); keine Datensteuerung. Kein Neuheitsanspruch: EXP-078 prüft die
Reichweite von K2, nicht eine neue Frage.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

P1-Ergebnisse dieser Seeds (1-Schicht-Δ_pow; Seed 1000: 5.45); Wahl von 10 000 Schritten nach EXP-049/EXP-045 (Endzustand nach dem Grokking). Keine 2-Schicht-Läufe gesehen.

## Befehle (ab 00:00, nach bestandener Gleichwertigkeit von `repro/train.py`)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-078-two-layer-steering/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-078-two-layer-steering/jobs.txt --workers 10
python lab/tools/guarded_run.py -- python lab/experiments/EXP-078-two-layer-steering/analyze.py
```

## Nachtrag a (15:34 Berlin, gemessen; vor jedem Lauf): Codeprüfung und Lesart

Claude-Prüfagent (nur lesend): **keine Blocker** (Modelltausch über den Modulnamen wirkt, Init-Gleichheit stimmt, Vorwärtsrechnung, Spektren bei 2000/10 000, Paarung mit P1, Jobzeilen). Übernommen: (1) **Lesart:** *keine Steuerung* nur bei Δ̄ < 0.5; p ≥ 0.2 allein ergibt *unklar* (vorher hätte ein großer, streuender Mittelwert „keine“ geheißen); (2) Herkunftsprüfung je Arm (Split-Datei in der result.json muss zu Seed und Arm passen); (3) veraltete Dateien: result.json muss jünger sein als spectra.npy; (4) `train2l.py` prüft Optionen über argparse statt exakter Zeichenketten; (5) Selbsttest ruft `make_dataset` wie der Trainer auf. Hinweis: In der result.json beschreiben `trainer` und `config` den schlanken Trainer bzw. das 1-Schicht-Preset; maßgeblich für das Modell ist das Feld `model`.

## Nachtrag b (15:55 Berlin, gemessen; vor jedem Lauf): Vorhersage der Theorie erster Ordnung

Die Herleitung in [[paper/draft]] §5.2 braucht nur (i) nahezu gleichverteilte Ausgaben bei der Init und (ii) für den Transformer einen *gemeinsamen Pfad* (J_L ≈ J_R), weil die fast gleichmäßige Attention beide Positionen in denselben Wert-/Ausgabepfad mischt. Beides gilt bei der Init auch mit zwei Schichten (jede Schicht mischt gleichmäßig; die Tiefe ändert die Jacobi-Matrizen, nicht ihre Gleichheit für beide Operanden). **Vorhersage:** Der erste W_E-Gradient folgt auch mit zwei Schichten dem kohärenten Maskenspektrum M0c; die P1-Splits sind darin zielangereichert (Anteil 0.189, Sitzung 25) → Δ_pow bei 2000 deutlich > 0. Ein Ergebnis *keine Steuerung* würde also nicht die erste Ordnung widerlegen, sondern zeigen, dass mit zwei Schichten spätere Dynamik (nach dem ersten Schritt) die Wahl überschreibt. Lesart und Kriterien oben unverändert.

## Nachtrag c (Sitzung 33, zwischen 22:34 und 22:36 Berlin gemessen; vor jedem Lauf): Trainer ergänzt, Bestätigung R7 festgelegt

- `lab/paper/repro/train.py` (von `train2l.py` genutzt) schreibt jetzt zusätzlich `"status": "completed"` und `"input_sha256"` (sha256 der gelesenen Split-Bytes) in die result.json. Training und Ausgaben sonst unverändert (die Datei wird einmal als Bytes gelesen und aus diesen Bytes geladen). Grund: Bindung und Herkunftsprüfung in [[confirm/R7_REGISTRATION_DRAFT|R7]]. Ungetestet bis zur Gleichwertigkeitsprüfung heute Nacht.
- **R7** (K2 in zwei Schichten an frischen Seeds 2900–2929) ist vor diesem Piloten festgelegt. Der Pilot bestimmt nur n, über eine feste Regel, und zwar **unabhängig von seiner Lesart** (Fassung 2 nach Codex). Deshalb muss `summary.json` dieses Piloten nach der Auswertung unverändert committet werden; R7 prüft ihren Hash.

## Nachtrag (Sitzung 34, 23:14 Berlin gemessen, vor jedem EXP-078-Lauf)

Anlass: unabhängige Prüfung der Bestätigung [[confirm/R7_REGISTRATION_DRAFT|R7]]. Bisher warf `analyze.py` eine Einheit ganz hinaus, wenn nur das Spektrum bei 10 000 fehlte oder nicht endlich war; dann wäre `n_valid` < 10 und R7 nie einfrierbar, obwohl der primäre Schritt 2000 in Ordnung ist. **Geändert:** Nur Schritt 2000 zählt für die Gültigkeit einer Einheit. Ein Fehler bei 10 000 setzt `D10000 = None` und steht unter `problems_secondary_10000`; die Sekundärgröße wird über die übrigen Einheiten berichtet. Lesart, Schwellen und Primärgröße bleiben unverändert. Abgestürzte oder fehlende Jobs dürfen **vor der ersten Auswertung** unverändert neu gestartet werden. Die `summary.json` wird im selben Commit wie das Log ihres Auswertungslaufs committet (R7 Fassung 3). Code ungetestet bis zum Selbsttest im Fenster.

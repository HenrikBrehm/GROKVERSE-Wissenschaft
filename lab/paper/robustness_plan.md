---
id: robustness-plan
status: entwurf
datum: 2026-09-27
tags: [lab/paper, exp/vorbereitet]
verwandt: ["[[paper/STATUS]]", "[[FINDINGS]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[confirm/N29_REGISTRATION|N29]]"]
---
# Robustheitsplan (Regel 19a): gelten K2 und K4c über Lernrate, Weight Decay und Trainingsanteil?

Zurück zu [[paper/STATUS]]. Entwurf Sitzung 24 (2026-09-27), **noch keine Registrierung**; wird vor jedem Lauf als eigene Registrierung mit eingefrorenem Manifest festgelegt.

- **Warum:** Gutachter fragen sofort, ob die Befunde nur bei lr 1e-3, wd 1.0, train_frac 0.3 gelten. Ein Ergebnis „gilt nur in einem Bereich“ ist ein Befund und kommt so ins Paper.
- **Technische Voraussetzung:** `freq_ban.py` hat heute kein `--lr`, `--weight-decay`, `--train-frac` (nur `--lr-scale` für die ersten 250 Schritte). Die drei Optionen müssen als späte Argumente
  (Fingerabdruck nur bei Abweichung vom Standard, wie `LATE_ARGS`) in den gemeinsamen Trainer, `confirm_splits` muss den Trainingsanteil durchreichen → **Codex-Prüfung Pflicht** (Regel 18c).
- **Registrierungsentwurf:** [[confirm/R1_REGISTRATION_DRAFT|R1]] (Sitzung 24).
- **Familie R1 (K2, Repräsentation):** P1-Maß Δ_pow bei Schritt 2000, add 113, Einheiten = Seed mit F/G-Paar wie P1. Zellen: lr ∈ {0.5e-3, 2e-3}, wd ∈ {0.3, 3.0}, train_frac ∈ {0.2, 0.5}
  (je eine Abweichung vom Standard, sonst Standard) = 6 Zellen. Je Zelle einseitiger Test Δ_pow > Mindesteffekt 1 (wie P1), Holm über 6. **Stichprobe:** P1-Streuung (SD ≈ 1.1 bei Mittel 8.2) → n = 10
  je Zelle genügt bei ähnlichen Effekten reichlich; wegen möglicher Abschwächung n = 15. 6 × 15 × 2 = 180 Läufe à 2000 Schritte (GPU ≈ 40 s) ≈ 20 min.
- **Familie R2 (K4c, Persistenz/Funktion):** N29-Protokoll (Wechsel bei 25 und 50, 4000 Schritte danach, Ablationskontrast), nur die zwei Zellen, die Gutachter am ehesten fragen: lr 2e-3 und wd 0.3.
  Vorhersage aus dem Amplitudenmodell H40 (falls EXP-040 es stützt): bei doppelter Lernrate verschiebt sich der Umschlagpunkt auf etwa halbe Schrittzahl. Deshalb Wechselzeiten je Zelle skaliert
  (lr 2e-3: t ∈ {12, 25}) oder fest (t ∈ {25, 50}); Entscheidung nach EXP-040. n = 20 je Zelle (wie N29), Holm über die Familie.
- **Stand Trainer (Sitzung 24):** `--lr`, `--weight-decay`, `--train-frac` eingebaut (Fingerabdruck/Run-ID nur bei Angabe, Run-ID mit exakter `repr`-Zahl), Codex-Prüfung
  `codex_review_hp_s24.txt`: zwei Blocker übernommen (nicht injektive Zahlformatierung; leere Splits). **Noch offen:** `confirm_splits` erzeugt Splits fest mit 0.3 und `confirm_p1` reicht keine
  Hyperparameter an die Jobzeilen weiter → für die train_frac-Zellen Split-Konstruktion und Job-Erzeugung erweitern (eigenes Werkzeug `confirm_r1.py`), dann erneut Codex.
- **Seeds:** neuer Block, z. B. 2400–2599 (vor jeder Nutzung in FINDINGS_DETAILS reservieren).
- **Reihenfolge:** Trainer-Optionen + Tests + Codex → R1 registrieren → Nacht 28./29.09. → R2 nach EXP-040.
- **Nachtrag Sitzung 25 (Seeds, vor jeder Nutzung):** Der Vorschlag „2400–2599“ oben war keine Reservierung. Tatsächlich reserviert in [[FINDINGS_DETAILS]]: **2360–2419 P4**, **2420–2509 R1** (wie `confirm_r1.py`, `SEED_MIN = 2420`, 6 × 15). R2 bekommt einen eigenen Block ab 2510.
- **Nachtrag Sitzung 26 (15:20, vor jedem R2-Lauf):** R2 registriert als Entwurf [[confirm/R2_REGISTRATION_DRAFT|R2]] mit `lab/tools/confirm_r2.py`, ohne auf EXP-040 zu warten: lr 2e-3 mit t ∈ {12, 25, 50} (H2 bei t = 12 liegt unter Schritt- und Λ-Uhr im Umstiegsbereich; t = 25 nur sekundär für die Uhrenfrage), wd 0.3 mit t ∈ {25, 50}; Holm über 4; n = 30 (Seeds 2510–2539) statt 20, begründet mit der N29-Streuung (Power 0.88 bei halbiertem Abstand über der Mindestdifferenz).

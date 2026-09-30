---
id: L0b
status: entwurf
datum: 2026-09-30
tags: [lab/confirm, exp/vorbereitet]
---
# L0b: Menge gegen feste Reihenfolge bei langen Epochen (B = 16), Bestätigung

Zurück: [[LAB]] · [[FINDINGS]] · Pilot [[experiments/EXP-106-l0-b16-long-epochs/README|EXP-106]] · Vorgänger [[confirm/L0_REGISTRATION_DRAFT|L0]] (K2 unter i.i.d.-Minibatch B 256/64, bestätigt; dort „kein H3“, Konflikt als eigene Registrierung L0b vorgesehen) · [[NOVEL_DIRECTIONS]] N52 · LeDoux 2026 (arXiv 2603.25047)

**Stand:** Entwurf, Sitzung 63 (2026-09-30, 21:29 Berlin gemessen). Nicht eingefroren. Code `lab/tools/confirm_l0b.py` (Selbsttest grün), Stichprobengröße `lab/confirm/L0b_power_s63.py` → `L0b_power_s63.json`. **Überarbeitet nach der unabhängigen Prüfung (ab 21:41, vor dem Einfrieren):** δ 0.05 → 0.02, H3 als Nicht-Unterlegenheit statt „> 1“, n 64 → 70, o bei Schritt 10 000 beschreibend, Zensur-Richtungen und Deckeneffekt beschreibend, Zufallsströme genauer beschrieben (JOURNAL S63).

## Bezug zu FINDINGS

Programm A (Split-Steuerung unabhängig replizieren) und der wichtigste Gutachter-Einwand der Woche (Regel 20b): LeDoux 2026 schreibt, dieselbe Frequenz entstehe „regardless of … training set composition“, bei sehr langen Epochen und fester Reihenfolge. Unser L0 hat K2 unter i.i.d.-Minibatch bestätigt, der Konflikt war bei B 256/64 aber „nicht prüfbar“ (die Reihenfolge wirkte dort nicht). Im Piloten EXP-106 (B = 16, 240 Schritte je Epoche, wd 0.1) wirkte sie: auf Zufallssplits, nicht auf konstruierten. L0b prüft genau diese Regime-Aussage an frischen Seeds. Jeder Ausgang kommt so ins Paper (§6, Regel 20b).

## Aufbau (einzufrieren)

- Aufgabe add 113. Je Seed die EXP-100-Konstruktion; **eigene Zufallsströme** `SeedSequence([100300, seed, Zweck])` nur für Zielziehung und R (Testmenge, Phasen und Schlüssel kommen wie in L0/EXP-100 aus `overlap_split`, Salz 53001 je Seed – frisch, weil die Seeds frisch sind). F/G wie P1/EXP-053 (ω = 0, kalibriertes ε), Zielmengen ohne O = {11, 12, 22, 23, 34, 45} (Frequenzen der stride-Reihenfolge a mod 10), Zweck 0; ein gleich großer Zufallssplit R aus demselben Pool (Zweck 1); gemeinsame Testmenge.
- Arme (alle AdamW lr 10⁻³, β 0.9/0.98, **weight decay 0.1**, **Batch 16**, 30 000 Schritte, `--stop-after-gen 30000`, GPU, `--threads 1`, Trainer `freq_ban.py` unverändert):
  `iid16w` (i.i.d.-Reihenfolge) und `stride16w` (feste stride-Reihenfolge), je auf F, G und R → 6 Läufe je Seed.
- **Seeds 3730–3799 (n = 70)**, frisch (per grep über lab/: 3730–3799 in keiner Jobzeile und keinem Manifest, 30.09.; in der L0-Registrierung für L0b reserviert).
- Laufzeit: Pilot ≈ 4–5 min je Lauf bei 10 GPU-Prozessen → 420 Läufe ≈ 4 h bei 8 Workern; Dienst-Jobdatei mit `gpu_gb=0.75`.

## Messgrößen (je Lauf, Endstand Schritt 30 000)

W_E-Gruppenpotenz (EXP-043-Basis). o = Anteil der Potenz auf O. Alle Hypothesen betreffen den **Endstand**; o bei Schritt 10 000 wird beschreibend berichtet (eine vorübergehende Prägung durch die Reihenfolge wäre am Ende sonst unsichtbar). Δ_pow wie P1 (log-Verhältnisse eigener gegen fremder Ziele, F/G-Paar). t_gen = erster Schritt mit Testgenauigkeit ≥ 0.95 (Trainer-Übergänge, primär); nie erreicht → zensiert bei 30 000 (kein technischer Fehler).

## Familie (Holm über H1–H4, α = 0.05)

Bestätigt = Holm-p < 0.05 **und** Bootstrap-Regel (95-%-Perzentil-KI über Seeds, 10 000, rng 21).

| | Aussage | Statistik je Seed | Test | KI-Regel |
|---|---|---|---|---|
| H1 | Die Reihenfolge wirkt, wo die Menge wenig vorgibt | o(R, stride) − o(R, iid) | einseitiger t, Mittel > 0 | untere Grenze > 0 |
| H2 | Die Menge gewinnt auf konstruierten Splits (keine Verschiebung) | Mittel über F/G von o(stride) − o(iid) | TOST, Äquivalenzgrenze δ = 0.02 (p = Maximum der zwei einseitigen t) | 95-%-KI ganz in (−0.02, 0.02) (strenger als das übliche 90-%-KI des TOST) |
| H3 | Die Reihenfolge schwächt die Steuerung nicht wesentlich | Δ_pow(stride) − Δ_pow(iid) | Nicht-Unterlegenheit, einseitiger t, Mittel > −2 | untere Grenze > −2 |
| H4 | Die Reihenfolge kostet auf konstruierten Splits Zeit | Mittel über F/G von log₂ t_gen(stride)/t_gen(iid) | einseitiger t, Mittel > 0 | untere Grenze > 0 |

**Begründung der Grenzen (vor dem Einfrieren):** δ = 0.02 ist ein Achtel der Pilotwirkung auf R (0.155) und ≈ 1.5 Pilot-SD auf F/G (0.013); der Grundwert von o auf F/G liegt bei ≈ 0.013, δ erlaubt also höchstens etwa eine Verdopplung bis Verdreifachung des O-Anteils (die erste Fassung mit δ = 0.05 hätte ein Fünffaches zugelassen; Einwand der Prüfung). Die H3-Grenze 2 ist ≈ 20 % der Pilotsteuerung Δ_pow(iid) = 9.2; der Pilotunterschied war −0.6 [−1.41, 0.12]. **Deutung je Ausgang (vorab):** H1 + H2 bestätigt → „Die Reihenfolge verschiebt die Frequenzen auf Zufallssplits, auf konstruierten Splits nicht über ±0.02 hinaus; dort gewinnt die Menge den Konflikt (Endstand)“ (passt zu LeDoux §6.4). H1 nicht, H2 bestätigt → „Menge gewinnt; eine Reihenfolge-Wirkung auf Zufallssplits nicht bestätigt“. H2 nicht bestätigt → keine Aussage „Menge gewinnt“ (Richtung des F/G-Unterschieds wird berichtet). H3 und H4 werden unabhängig davon berichtet (Steuerung unter der Reihenfolge nicht wesentlich schwächer; Zeitkosten). Zensur in H4: ein nur im stride-Arm zensierter Lauf drückt x nach unten (konservativ), ein nur im iid-Arm zensierter nach oben; beide Zahlen werden berichtet.

**Stichprobengröße:** `L0b_power_s63.py` (Normalmodell mit halbem Piloteffekt, 1.5-facher Pilot-SD, jeder Test bei α/4, 4000 Wiederholungen): n80 = 63 (H1), 17 (H2, TOST mit δ 0.02 und dem Pilotmittel 0.004), 18 (H3, Nicht-Unterlegenheit mit dem Pilotunterschied −0.6), 33 (H4) → Regel ergibt 64; **n = 70** (alle freien Seeds, weil H1 knapp ist und die Pilotwerte auf R zweigipflig sind: Seeds mit hohem o(R, iid) zeigen ≈ 0, Spearman −0.62 im Piloten; erste Fassung: n80 63/10/10/33).

**Gültigkeit:** Jeder technische Fehler (fehlt, defekt, nicht gebunden, falsche Batch/Reihenfolge/Optimierer, fehlendes Minibatch-Ereignis, nicht endliche Potenz, Δ_pow nicht endlich) → ganzer Block „nicht auswertbar“ (wie L0). Reine Infrastrukturfehler (Absturz, HIP-Startfehler, Dienst-Abbruch) dürfen vor `--analyze` mit identischer Jobzeile wiederholt werden. Ein Lauf, der nie generalisiert, ist kein technischer Fehler (zensiert in H4; zählt in H1–H3 mit seinem Endspektrum).

**Beschreibend (kein Test):** Δ_pow(iid16w) mit KI, o je Arm und Split am Ende und bei Schritt 10 000, Anteil der Läufe mit Spitze in O, Zahl nie generalisierter Läufe je Arm und Split und einseitig zensierter Paare, Spearman von o(R, iid) gegen x_H1 (Deckeneffekt).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- **EXP-106** (Seeds 3700–3707, alle Arme und Splits, ausgewertet und nachgerechnet): beeinflusst die Form von H1–H4, δ, die H3-Grenze, n (Power aus seiner Streuung), Budget 30 000, B = 16, wd 0.1 (dort als einzige lernende B16-Einstellung gefunden). Seine Konflikt-Lesart war „nicht prüfbar“ (Reihenfolge-Wirkung vorab an F/G oder ≥ 75 % Spitzen auf R gebunden); L0b fragt deshalb direkt nach der R-Verschiebung (H1) und der Äquivalenz auf F/G (H2).
- **EXP-100** (Seeds 3700–3707, B 256/64, B16-Sonde) und **L0** (3720–3729, B 256/64, bestätigt): Konstruktion, O, Trainer-Optionen.
- **EXP-107/108/N54b** (Festlegungsfenster unter Minibatch): Einordnung (bei B = 16 ist eine Epoche länger als das Festlegungsfenster, N52).
- Keine L0b-Seeds gesehen.

## Ablauf

1. Unabhängige Code- und Designprüfung (Agent, nur lesend), Punkte einarbeiten.
2. Manifest `lab/confirm/L0b_manifest.json` (REGISTERED + python + registration + code_sha256), committen, Commit-ID eintragen, committen (eingefroren).
3. `python lab/tools/confirm_l0b.py --splits lab/confirm/L0b_manifest.json`; Splits committen.
4. Smoke: ein voller Lauf (Seed 3730, F, iid16w) durch `--run`, dann Lader-Prüfung (`one_run`) – zählt als Teil des Blocks (identische Jobzeile, gebunden).
5. Jobdatei über den Dienst (`--jobs`, Kopfzeile `#! workers=8 job_minutes=120 gpu_gb=0.75`; reine Infrastrukturfehler: identische Zeile wiederholen; ein divergierter Lauf ist technisch und macht den Block „nicht auswertbar“ – Risiko bei 420 Läufen bewusst in Kauf genommen), Auswertung `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/tools/confirm_l0b.py --analyze lab/confirm/L0b_manifest.json`, unabhängige Nachrechnung.

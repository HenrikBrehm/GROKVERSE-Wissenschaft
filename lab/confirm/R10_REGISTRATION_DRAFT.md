---
id: R10
status: entwurf
datum: 2026-09-28
tags: [confirm/entwurf, neu/kandidat]
---
# R10-Bestätigung (Entwurf): Braucht die frühe Festlegung neu ausgewertete Gradienten entlang des Wegs?

Zurück: [[LAB]] · [[FINDINGS]] (Antwort auf die offene Frage nach EXP-093/094) · Pilot [[experiments/EXP-095-gradient-feedback/README|EXP-095]] · Vorgänger [[experiments/EXP-094-evaluations-vs-window/README|EXP-094]] · [[confirm/R9_REGISTRATION_DRAFT|R9]] · [[NOVEL_DIRECTIONS]] N48.

**Status:** Fassung 1 mit Code, Sitzung 42 (2026-09-28, 17:00 Berlin gemessen). `lab/tools/confirm_r10.py` (Selbsttest grün über den Wächter, 16:58), **nicht eingefroren**. Vor dem Einfrieren: unabhängige Prüfung von Design und Code (Codex ohne Guthaben → Claude-Agent, nur lesend), dann Einfrieren und Rechnen in der Nacht 28./29.09.

## Hypothesen (Familie, Holm über 3, α = 0.05)

Protokoll wie EXP-095 (add 113, ω = 0-Splits nach EXP-053-Bau aus dem Seed, Wechsel A → B und B → A bei t, danach 2000 Schritte Standard; π gegen reine Läufe, EXP-056-Definition). Alle Zellen Λ = 24.
- **H1 (Auswertungen):** e₈ = π(n24) − π(g8) > 0, also 24 Adam-Schritte mit 24 gegen 3 Gradientenauswertungen. Einseitiger gepaarter t-Test; bestätigt = Holm-p < 0.05 **und** 95-%-Bootstrap-KI-Untergrenze > 0. Pilot: +0.141, SD 0.16.
- **H2 (kein Zusatzeffekt des groben Adam-Schritts):** r₈ = π(g8) − π(c8b) liegt in ±0.05 (TOST, p = größeres der beiden einseitigen t-Test-p, unter Holm). Pilot: +0.000, SD 0.075.
- **H3 (Anfangsgradient allein):** e₂₄ = π(n24) − π(g24) > 0; wie H1. Pilot: +0.187, SD 0.163.
- **Beschreibend:** e₂₄ − e₈ (Pilot +0.046, SD 0.20, nicht getestet), Zielanteil f und Norm N der W_E-Bewegung beim Wechsel je Zelle.
- **Lesart:** alle drei → „Auswertungen-Befund bestätigt“, sonst Liste der bestätigten.
- **Was die Bestätigung heißt und was nicht:** Die Festlegung bis Λ = 24 hängt an der Zahl der Gradientenauswertungen bei festen Adam-Schritten, und der grobe Adam-Schritt fügt bei 3 Auswertungen nichts hinzu. Offen bleiben die Ursache (Selbstverstärkung der Ziele gegen Korrektur der veralteten Richtung) und die Trennung von Anzahl und Abstand der Auswertungen.

## Umfang, n

Zellen je Seed: rein A/B, n24, g8 (`--pre-switch-grad-every 8`), g24 (`… 24`), c8b (`--lr-scale 8 --pre-switch-betas 0.2,0.84`, t = 3) → 10 Läufe. g4 aus dem Piloten entfällt (keine Hypothese). **n = 48, Seeds 3500–3547** (frisch: Dateisuche 28.09. 16:58 ohne Treffer; Treffer für 3500/3525/3535 sind Schrittzahlen bzw. eine UUID). 48 × 10 = **480 GPU-Läufe** (≈ 45–60 min mit 8 Workern).
**Power** (Normalnäherung, Holm über 3, 2000 Wiederholungen, Sitzung 42): halber Piloteffekt (e₈ 0.07, e₂₄ 0.094; r₈ wahr 0) bei Pilot-SD: H1 0.92, H2 1.00, H3 0.99; bei 1.5-facher SD: 0.61 / 0.77 / 0.78 (n = 60: 0.71 / 0.88 / 0.87). Voller Piloteffekt ≈ 1. Die KI-Regel ist bei H1/H3 kaum strenger als der Test. **Grenze:** bei 1.5-facher SD und halbem Effekt unter 80 %; bewusst in Kauf genommen (Budget einer Nacht neben anderen Blöcken).

## Verbindliche Einzelheiten (wie im Code)

- π wie EXP-056 aus der W_E-Gruppenleistung am Ende gegen die reinen Läufe des Seeds; f und N aus den Schnappschüssen bei t und 0 (EXP-092-Selektivität).
- **Gültigkeit:** jeder Lauf über den gemeinsamen Lader (Seed, Gerät, Schritte, Split-/Test-/Wechselhash, lr 1e-3, wd 1, train_frac 0.3, β 0.9/0.98 nach dem Wechsel, `lr_scale`, `pre_switch_betas`, Schnappschüsse bei t, 0 und am Ende) und die Bindung; β-Wechsel-Ereignis wahr (c8b); **Gradientenplan wie registriert** (`pre_switch_grad_every` = k und Auswertungsschritte 1, 1 + k, … im Ereignis; bei k = 1 kein Ereignis). Ein technischer Ausfall → *nicht auswertbar*. Seeds mit L(A) − L(B) < 2 fallen heraus (gezählt); mehr als 8 von 48 → *nicht auswertbar*.
- **Einfrieren:** wie R9. Manifest `lab/confirm/R10_manifest.json` = `REGISTERED` + `python` (absoluter venv-Pfad) + `registration` + `code_sha256` (`--hash-code`), committen, Commit-ID in `commit`, erneut committen; `--splits`; `python lab/tools/confirm_r10.py --jobs lab/confirm/R10_manifest.json > lab/confirm/R10_jobs.txt` (ohne Wächter); Smoke = erste Jobzeile + je eine g8-, g24- und c8b-Zeile (`R10_smoke.txt`); dann Block mit 8 Workern; `--analyze` über den Wächter mit `PYTHONIOENCODING=utf-8`.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-095 (Richtung, Effektgrößen und SD aller drei Hypothesen, Wahl von k = 8/24 und Äquivalenzgrenze ±0.05 aus der Pilot-KI von r₈ ±0.035), EXP-094 (c8b-Zelle, d8), EXP-093 (Λ = 24), R9 (β′-Regel, Blockaufbau). Keine Seeds aus diesen Blöcken.

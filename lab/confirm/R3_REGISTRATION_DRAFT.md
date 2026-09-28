---
id: R3-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung, lab/paper, exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[confirm/N29_REGISTRATION|N29]]", "[[confirm/R2_REGISTRATION_DRAFT|R2]]", "[[experiments/EXP-039-lr-clock/README|EXP-039]]", "[[experiments/EXP-040-we-init-scale/README|EXP-040]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[paper/STATUS]]", "[[JOURNAL]]"]
---
# R3-Bestätigung: Tickt die Festlegung in aufsummierter Lernrate (Λ) oder in Schritten? Registrierungsentwurf (Sitzung 26)

Zurück zu [[FINDINGS]] („Größte offene Frage“: Was macht die frühe Wahl fest?) · Vorlage [[confirm/N29_REGISTRATION|N29]] (K4c, bestätigt) · Pilot [[experiments/EXP-039-lr-clock/README|EXP-039]] (***unklar***).
Entwurf 2026-09-27, Sitzung 26, **vor jedem R3-Lauf**. Code `lab/tools/confirm_r3.py` (ungetestet bis zum nächsten Fenster).

## Anlass

N29 zeigt einen Umschlag zwischen einem Wechsel nach 25 und nach 50 Schritten (Standard-Lernrate 1e-3). Zwei Uhren sagen für eine andere Lernrate *vor* dem Wechsel Verschiedenes voraus:
- **Λ-Uhr:** Die Festlegung hängt an der aufsummierten Lernrate Λ = Σ lr (in Einheiten von 1e-3: Λ = c · t). Das passt zum Amplitudenbild (unter Adam wachsen die Zielamplituden ≈ linear in Λ;
  [[experiments/EXP-040-we-init-scale/README|EXP-040]] H40) und zu EXP-059 („Momentum = Vorschritte“).
- **Schrittuhr:** Die Festlegung hängt an der Zahl der Schritte (z. B. über Adams Momentenhorizonte), unabhängig von der Lernrate.
  *Konkreter Kandidat (Sitzung 26, Rechnung ohne Läufe):* Der Horizont des zweiten Moments ist 1/(1 − β₂) = **50 Schritte** (β₂ = 0.98 im Preset); die Bias-Korrektur-Masse 1 − β₂ᵗ ist 0.40 bei t = 25 und 0.64 bei t = 50. Dass das Umschlagfenster (25, 50] genau darunter liegt, macht eine β₂-gebundene Schrittuhr zu einem ernsthaften Konkurrenten.
EXP-039 (Pilot, 4 bekannte Seeds, Dominanzmaß d) fand Λ in 5/8 Zellen → ***unklar***. R2 kann die Frage nicht klären, weil dort die Lernrate auch nach dem Wechsel verändert ist (Codex s26).

## Aufbau

- **Protokoll:** genau wie N29 (ω = 0, EXP-053-Splits über `overlap_split.build`, beide Richtungen, 4000 Schritte nach dem Wechsel, `--stop-after-gen` ≥ Schritte, `--save-model`, Ablation der
  5 alten bzw. 5 neuen Zielfrequenzen aus W_E[:113], Genauigkeit auf der zurückgehaltenen Testmenge, je Seed Mittel über beide Richtungen).
- **Eingriff:** `freq_ban.py --lr-scale c` (EXP-039-Option): Lernrate c · 1e-3 in den Schritten 1 … t auf dem ersten Split, **ab dem Wechsel die Standard-Lernrate** (Code: `on_first` und
  `step <= LR_SCALE_UNTIL = 250`; der Selbsttest prüft, dass beides im eingefrorenen Trainer steht). Das Nachtraining ist damit in allen Zellen gleich spezifiziert (Split, Lernrate, Budget), abgesehen vom getragenen Modell- und Optimiererzustand.

| Zelle | c | t | Λ (in 1e-3-Schritten) | Λ-Uhr sagt | Schrittuhr sagt |
|---|---|---|---|---|---|
| lrs2 | 2 | 25 | 50 (wie Standard t = 50) | **Festhalten** | Umstieg (wie Standard t = 25) |
| lrs05 | 0.5 | 50 | 25 (wie Standard t = 25) | **Umstieg** | Festhalten (wie Standard t = 50) |

- **Primäre Familie (Holm über 2, einseitiger t-Test, 95-%-Bootstrap-KI; „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0), Vorhersagen der Λ-Uhr:**
  - **HL_hold** (lrs2, t = 25): (acc_neu − acc_alt) − 0.3 > 0;
  - **HL_switch** (lrs05, t = 50): (acc_alt − acc_neu) − 0.3 > 0.
  - ***„Λ-Uhr bestätigt“*** nur, wenn beide bestätigt sind. Sonst ***„Λ-Uhr nicht bestätigt“*** (das ist keine Bestätigung der Schrittuhr).
- **Sekundär, ohne Urteil:** die gespiegelten Kontraste der Schrittuhr (Umstieg bei lrs2@25, Festhalten bei lrs05@50) mit KI; Lesart vorab: beide KI-Untergrenzen über 0 → *passt zur Schrittuhr*,
  sonst *passt nicht zur Schrittuhr*. Ein Ergebnis dazwischen (keine Uhr bestätigt) spricht für eine Mischung oder für eine Größe, die weder Λ noch Schritte ist; das wird so berichtet.
- **Stichprobe und Ausfälle:** primär alle Seeds, auch nicht generalisierte (wie N29); jeder technische Ausfall → *nicht auswertbar*; generalisierte Teilmenge nur beschreibend, ohne p-Werte.
- **Stichprobengröße aus der Pilotstreuung (N29):** Umstieg 0.603 (SD 0.240), Festhalten 0.903 (SD 0.124). Normalnäherung, einseitig, α = 0.05/2: bei vollem Effekt Power ≈ 1; bei halbiertem
  Abstand über der Mindestdifferenz (Umstieg 0.45) n = 20 → 0.80, n = 25 → 0.88. **Gewählt n = 20** (Seeds **2540–2559**, reserviert in [[FINDINGS_DETAILS]], nie benutzt): 80 Läufe à t + 4000 Schritte,
  GPU, 1 Thread; nach N29 ≈ 17 min mit 7 Arbeitern.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** N29 (Maß, Mindestdifferenz 0.3, Budget, Streuung); EXP-039 (Seeds 30–34; Idee und Faktor 2 bzw. 0.5); EXP-059 (π-Kurve,
  Seeds 400–409); R2-Entwurf und Codex-Einwand (Anlass, keine Daten). Keine Läufe dieser Seeds.
- **Weight Decay ist über Λ angeglichen (Rechnung):** Der Zerfallsfaktor vor dem Wechsel ist (1 − 0.002)²⁵ = 0.95118 bei lrs2@25 und (1 − 0.001)⁵⁰ = 0.95121 beim Standard bei 50, bzw. (1 − 0.0005)⁵⁰ = 0.97530 bei lrs05@50 und (1 − 0.001)²⁵ = 0.97530 beim Standard bei 25. Der Decay-Anteil folgt also derselben Uhr wie die Gradientenschritte.
- **Grenzen:** eine Aufgabe (add 113), eine Architektur, ω = 0; c ändert mit der Lernrate auch den Weight-Decay-Schritt (AdamW entkoppelt: lr · wd) und die Größe der Adam-Schritte, nicht die
  Momentenhorizonte; „Λ“ ist deshalb eine Sammelgröße (Lernrate × Schritte), kein Mechanismus. Zwei Zellen, keine Kurve.
- **Familie:** eigene (nur R3).
- **Vor dem Einfrieren:** Selbsttest im Fenster; Codex-Prüfung (Regel 18c); Manifest mit Code-Hashes und Commit; Smoke durch den eingefrorenen Lader.

```
python lab/tools/guarded_run.py -- python lab/tools/confirm_r3.py --selftest
python lab/tools/confirm_r3.py --hash-code                      # -> code_sha256 ins Manifest
# Manifest lab/confirm/R3_manifest.json = REGISTERED + python + registration + code_sha256; committen, Commit-ID in "commit", erneut committen
python lab/tools/confirm_r3.py --splits lab/confirm/R3_manifest.json
python lab/tools/confirm_r3.py --jobs lab/confirm/R3_manifest.json > lab/confirm/R3_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/R3_jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/tools/confirm_r3.py --analyze lab/confirm/R3_manifest.json
```

## Codex-Prüfung (Sitzung 26, Ergebnis vor 15:41, `R3_codex_review_s26.txt`, vor jedem Lauf)

Keine Blocker. Bestätigt: `--lr-scale` wirkt genau in den Schritten 1 … t, ab t + 1 Standard-Lernrate, kein Reset; Run-IDs, Vorzeichen, Joborder, Holm über 2, Power-Zahlen, keine Lücke in `CODE_FILES` (Modul-Selbsttest bleibt wie bei R2 nicht vollständig). Übernommen: (1) „Nachtraining gleich“ → „gleich spezifiziert, abgesehen vom getragenen Zustand“; (2) **weitere Gegenerklärungen**, die das Zwei-Zellen-Muster der Λ-Uhr ohne einen wörtlichen Λ-Mechanismus erzeugen können: Adams Bias-Korrektur und schrittabhängige Momente, Überschießen bzw. Nichtlinearität durch größere frühe Schritte. Ein Ergebnis *Λ-Uhr bestätigt* heißt deshalb nur: Die Festlegung skaliert in diesen zwei Zellen wie Λ, nicht, dass Λ der Mechanismus ist; (3) die Ausgabe von `confirm_r3.py` sagt jetzt ausdrücklich, dass *nicht bestätigt* keine Bestätigung der Schrittuhr ist.

- **Eingefroren (Sitzung 37, 2026-09-28, Berlin):** Selbsttest grün (Sitzung 37), Codex-Prüfung Sitzung 26 ohne Blocker und eingearbeitet (oben). Manifest `lab/confirm/R3_manifest.json` (Entwurf ohne Notiz + `code_sha256`), Commit-ID im Feld `commit`. Bereits gesehene Daten: wie oben; kein Lauf mit den R3-Seeds vor dem Einfrieren.

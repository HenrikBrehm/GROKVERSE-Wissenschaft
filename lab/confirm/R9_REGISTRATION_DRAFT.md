---
id: R9
status: abgeschlossen
datum: 2026-09-28
tags: [confirm/abgeschlossen, befund/positiv, neu/kandidat]
---
# R9-Bestätigung (Entwurf): Tickt die frühe Festlegung in Λ, wenn Adams β-Fenster in Λ gemessen werden?

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage) · Piloten [[experiments/EXP-089-lambda-fixed-steps/README|EXP-089]], [[experiments/EXP-090-beta-window-lambda/README|EXP-090]], [[experiments/EXP-081-optimizer-clock/README|EXP-081]] · [[confirm/R3_REGISTRATION_DRAFT|R3]] · [[NOVEL_DIRECTIONS]] N48.

**Status:** Fassung 1 mit Code, Sitzung 40 (2026-09-28, 12:10 Berlin gemessen; die frühere Angabe „≈ 12:12“ war geschätzt). `lab/tools/confirm_r9.py` (Selbsttest grün 12:10), **nicht eingefroren**. Vor dem Einfrieren: Code `confirm_r9.py` nach dem Muster von `confirm_r3.py` (Manifest, Code-Hashes, Lader, Smoke), unabhängige Prüfung von Design und Auswertung, Seeds reservieren.

## Hypothesen (Familie, Holm über 3, α = 0.05)

Protokoll wie EXP-090 (add 113, ω = 0-Splits nach EXP-053-Bau mit eigenem Seed-Strom, Wechsel A → B und B → A bei t, danach 2000 Schritte Standard; π gegen reine Läufe; `--lr-scale c` in den Schritten 1 … t; `--pre-switch-betas` mit β′ = 1 − c(1 − β)).
- **H1 (Richtung, c = 0.25, Λ = 25):** e₁ = π(lr × 0.25, t = 100) − π(dieselbe Zelle mit β′ = 0.975/0.995) > 0. Einseitiger gepaarter t-Test, Mindesteffekt 0.05 (bestätigt = Holm-p < 0.05 und KI-Untergrenze > 0.05). Pilot: +0.16, SD 0.14.
- **H2 (Äquivalenz, c = 0.25):** d₁ = π(lr × 0.25, t = 100, β′) − π(Standard, t = 25) liegt in ±0.1 (TOST: p = größeres der beiden einseitigen t-Test-p, unter Holm; siehe Fassung 2). Pilot: +0.002, SD 0.05.
- **H3 (zweite Stufe, c = 2, Λ = 30):** e₂ = π(lr × 2, t = 15, β′ = 0.8/0.96) − π(lr × 2, t = 15, Standard-β) > 0 (H-β: bei c = 2 sind die Standardfenster in Λ doppelt so lang → weniger Festlegung; β′ gleicht aus). Pilot [[experiments/EXP-091-beta-window-c2/README|EXP-091]] (bekannte Seeds 3260–3269): +0.049 [0.023, 0.078], SD 0.048, 10/10. **Test gegen 0** (kein Mindesteffekt; 0.03 wäre bei halbem Piloteffekt zu streng); Power bei n = 24 und halbem Effekt ≈ 0.8.
- **Beschreibend:** d₂ = π(c = 2, β′) − π(Standard, t = 30); Trennung beim Wechsel (zählerfreie Lesart); t_eq.

## Umfang, n

Zellen je Seed: rein A/B, Standard t = 25 und t = 30, (0.25, 100), (0.25, 100, β′), (2, 15), (2, 15, β′) → 14 Läufe. **n = 24** (Normalnäherung bei halbem Piloteffekt für H1: Power ≈ 0.88; H2 bei 1.5-facher Pilot-SD ≈ 1.0; H3 offen) → 336 GPU-Läufe, ≈ 35–40 min bei 8 Workern.

## Offene Punkte vor dem Einfrieren

1. c = 2: t = 15 ergibt Λ = 30; `--lr-scale` wirkt bis Schritt 250 nur auf dem ersten Split (passt). β′ = 0.8/0.96 bei lr 2e-3 stabil: **erledigt** (EXP-091, 10/10, Ereignis wahr).
2. Zählerunterschied nach dem Wechsel (EXP-090 Nachtrag a): betrifft H2 und d₂, nicht H1/H3 (Paarung innerhalb derselben c-Stufe). In der Registrierung so nennen; zählerfreie Lesart beschreibend.
3. Seeds: reservierter Block (Fassung 2: 3300–3335); Splits über den EXP-053-Strom (SALT 53001, nach Seed), unbedenklich, weil die Seeds frisch sind.
4. **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-091 (c = 2: Richtung, SD, Wahl von t = 15 und β′ 0.8/0.96, Test gegen 0), EXP-089/090 (Effektgrößen, SD, Wahl von Λ = 25, t = 100, β′-Regel, Äquivalenzgrenze ±0.1), EXP-081 (Richtung bei β₁), R3 (c = 2 und 0.5 als Stufen). Keine Seeds aus diesen Blöcken.

## Fassung 1 (Sitzung 40, 12:10): verbindliche Einzelheiten, wie im Code

- **Seeds 3300–3323** (24, frisch: Dateisuche 28.09. ohne Treffer; hiermit reserviert). Splits: EXP-053-Bau aus dem Seed (`ov.build(s, 0, eps)`), Dateien `lab/confirm/r9_splits/`, beim Auswerten deterministisch nachgebaut und verglichen.
- **Zellen** (je A → B und B → A, danach 2000 Schritte Standard-Lernrate und -β): n25, n30 (Standard), l100 (lr × 0.25, t = 100), l100b (dazu β′ 0.975/0.995), c2 (lr × 2, t = 15), c2b (dazu β′ 0.8/0.96); reine A/B-Läufe 2000 Schritte. 24 × 14 = **336 GPU-Läufe**.
- **π** wie EXP-056 aus der W_E-Gruppenleistung am Ende, gegen die reinen Läufe des Seeds; Trennung beim Wechsel aus dem Schnappschuss bei t (beschreibend).
- **H1:** einseitiger t-Test auf e₁ − 0.05 > 0; bestätigt = Holm-p < 0.05 **und** 95-%-Bootstrap-KI-Untergrenze von e₁ > 0.05. **H2:** TOST, p = Maximum der beiden einseitigen t-Tests (d₁ + 0.1 > 0, 0.1 − d₁ > 0); bestätigt = Holm-p < 0.05. **H3:** einseitiger t-Test auf e₂ > 0; bestätigt = Holm-p < 0.05 **und** KI-Untergrenze > 0. Holm über H1–H3. Lesart: alle drei → „Fenster-Regel bestätigt“, sonst Liste der bestätigten.
- **Gültigkeit:** jeder Lauf über den gemeinsamen Lader (Seed, Gerät, Schritte, Split-/Test-/Wechselhash, lr 1e-3, wd 1, train_frac 0.3, β 0.9/0.98 nach dem Wechsel, `lr_scale`, `pre_switch_betas`, Schnappschüsse bei t und am Ende) und die Bindung (unverändert vor/nach dem Laden); β-Wechsel-Ereignis wahr. Ein technischer Ausfall → *nicht auswertbar*. Seeds mit L(A) − L(B) < 2 fallen heraus (gezählt); mehr als 4 → *nicht auswertbar*.
- **Zählerunterschied** nach dem Wechsel (t = 100/15 gegen 25/30) betrifft H2 und d₂, nicht H1/H3; beschreibend die zählerfreie Lesart r über die Trennung beim Wechsel.
- **Einfrieren:** Manifest `lab/confirm/R9_manifest.json` = `REGISTERED` + `python` (absoluter venv-Pfad) + `registration` + `code_sha256` (`--hash-code`), committen, Commit-ID in `commit`, erneut committen; `--splits`; `--jobs` ohne Wächter in `R9_jobs.txt`; Smoke = erste Jobzeile + eine l100b- und eine c2b-Zeile; dann Block mit 8 Workern; `--analyze` über den Wächter mit `PYTHONIOENCODING=utf-8`.

## Fassung 2 (Sitzung 40, 12:25 Berlin gemessen; nach der Prüfung vor dem Einfrieren, vor jedem R9-Lauf): verbindlich, ersetzt Abweichendes oben

Unabhängige Prüfung (Claude-Agent, nur lesend; Codex ohne Guthaben): **kein Code-Blocker.** Run-IDs, Lader-Konfiguration (an sechs echten Pilotläufen mit `load_run` geprüft: alle ok), Schnappschüsse, Bindung und Statistik (Richtungen, TOST, Holm) stimmen. Übernommen, selbst nachgerechnet:
1. **H1 gegen 0 statt gegen 0.05 (Major):** Die Power-Angabe „≈ 0.88“ galt einem Test gegen 0 ohne Holm und KI-Regel; mit Mindesteffekt 0.05 wäre die Power bei halbem Piloteffekt ≈ 0.12 (Prüfer-Simulation). **Neu:** H1 = einseitiger t-Test auf e₁ > 0, bestätigt = Holm-p < 0.05 **und** 95-%-Bootstrap-KI-Untergrenze > 0. Ob die KI-Untergrenze über 0.05 liegt, wird beschreibend berichtet.
2. **n = 36** (Seeds **3300–3335**, frisch: Dateisuche 12:24 ohne Treffer). Eigene Simulation (Holm über 3, KI-Regel, Normalnäherung; 1500 Wiederholungen): halber Piloteffekt (e₁ 0.08, e₂ 0.025) bei Pilot-SD: Power H1 0.93, H3 0.88; bei 1.5-facher SD 0.64 / 0.56; voller Piloteffekt ≈ 1.0. (n = 24 hätte 0.81/0.74 bzw. 0.49/0.42 ergeben.) 36 × 14 = **504 GPU-Läufe**.
3. **Ausschlussgrenze:** mehr als 6 von 36 Seeds mit L(A) − L(B) < 2 → *nicht auswertbar* (vorher 4 von 24, gleiche Quote).
4. **H2 bleibt primär, mit enger Lesart:** Nach dem Wechsel steht der Adam-Zähler bei 100 (l100b) statt 25 (n25); v̂ nimmt neue Gradienten danach mit ≈ 0.023 statt ≈ 0.049 auf. Eine bestätigte Äquivalenz heißt deshalb „äquivalent trotz verschiedenem Zähler“, nicht „Λ erklärt alles“. Vorab genannte zählerfreie Prüfung: r_sep (Trennung beim Wechsel), beschreibend.
5. **Kleinigkeiten:** Lesart-Text im Code korrigiert („nicht bestätigt“ statt leerem „teilweise:“; Selbsttest prüft jetzt alle drei Fälle); H2-Text ohne KI-Formulierung; Seed-Strom richtig benannt; offener Punkt 1 erledigt.

## Ergebnis (Sitzung 40, 2026-09-28; Block 12:23–13:10 Berlin, 504/504 gebunden; `--analyze` am eingefrorenen Manifest 8b22879a über den Wächter)

36/36 Seeds, 0 technische Ausfälle, 0 ausgeschlossen (L(A) − L(B) ≥ 2 überall). Ein Lauf (Seed 3322, n25 A→B) scheiterte im ersten Durchgang technisch an einem Windows-Dateizugriff beim Umbenennen von `result.json` (WinError 5); der unfertige Rest wurde von der Blocklogik als `.stale_…` beiseitegelegt und der Lauf im zweiten Durchgang derselben Jobliste neu gerechnet und gebunden.
- **H1 bestätigt:** e₁ = π(l100) − π(l100b) = **+0.161** [0.132, 0.192], SD 0.093, **36/36** > 0, Holm-p 3·10⁻¹². KI-Untergrenze auch über 0.05 (beschreibend).
- **H2 bestätigt:** d₁ = π(l100b) − π(n25) = **+0.015** [0.005, 0.027], SD 0.035, TOST Holm-p 3·10⁻¹⁶ (Äquivalenz ±0.1). Ein kleiner positiver Rest (KI ohne 0) passt zum vorab genannten Zählerunterschied; zählerfreie Lesart r_sep = 0.06.
- **H3 bestätigt:** e₂ = π(c2b) − π(c2) = **+0.057** [0.042, 0.073], SD 0.048, **34/36**, Holm-p 1.5·10⁻⁸.
- **Beschreibend:** d₂ = π(c2b) − π(n30) = −0.007 [−0.021, 0.009]. Trennung beim Wechsel: n25 0.034, l100 0.052, l100b 0.035; n30 0.047, c2 0.039, c2b 0.046.
**Registrierte Lesart: „Fenster-Regel bestätigt (H1, H2, H3)“.** Bei Λ = 25 (lr × 0.25) und Λ = 30 (lr × 2) folgt die frühe Festlegung der aufsummierten Lernrate, sobald Adams β-Fenster ebenfalls in Λ gemessen werden (β′ = 1 − c(1 − β)); mit Standard-β weicht sie in beiden Richtungen ab, wie die in Schritten zählende β₁-Verzögerung vorhersagt. **Grenzen:** add 113, eine Architektur, Vollbatch, zwei (c, Λ)-Paare; H2 heißt „äquivalent innerhalb ±0.1 trotz verschiedenem Zähler nach dem Wechsel“ (kleiner Rest +0.015); Mechanismus (warum eine kürzere Verzögerung selektiver macht) offen.

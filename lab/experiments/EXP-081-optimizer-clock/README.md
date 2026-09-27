---
id: EXP-081
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-081: Welche Uhr legt die Frequenzwahl fest? β₁ und β₂ als Hebel (Pilot, Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage: Was macht die frühe Wahl fest?) · [[NOVEL_DIRECTIONS]] N37, N38 · Vorläufer [[experiments/EXP-059-momentum-exposure/README|EXP-059]] ·
Konkurrenz zu [[confirm/R3_REGISTRATION_DRAFT|R3]] (Λ gegen Schritte) · [[JOURNAL]] Sitzung 27.

**Status:** Entwurf, Sitzung 27 (16:21 Berlin, gemessen), vor jedem Lauf. **Kein Code.** Braucht Trainer-Optionen `--beta1/--beta2` in `freq_ban.py` (gemeinsamer Trainer → Codex-Pflicht, Regel 18c),
die **erst nach dem Einfrieren der Nachtblöcke vom 28.09.** eingebaut werden dürfen (die Manifeste hashen den Trainer). **Start frühestens nach dem R3-Ergebnis**; bestätigt R3 die Λ-Uhr klar, wird das Design
vor dem Lauf neu bewertet (der β₁-Arm bleibt dann trotzdem informativ, der β₂-Arm wird unwahrscheinlicher).

## Konkurrenzmodelle und Vorhersagen (vorab, numpy-Rechnung `EXP-059-momentum-exposure/clock_predictions.py`)

Kennzahl: **t₅₀** = Wechselschritt, bei dem π (Mittel beider Richtungen, EXP-059-Definition) 0.5 kreuzt (lineare Interpolation im t-Gitter). Referenz (β₁, β₂) = (0.9, 0.98): EXP-059 ≈ 33.

| Zelle (β₁, β₂) | Verschiebungsuhr (Λ + Momentum-Schwanz) | β₂-Horizont (N37) | reine Schrittuhr |
|---|---|---|---|
| (0.8, 0.98) | später, Δt₅₀ ≈ +5 (Schwanz 4.0 statt 8.7) | 0 | 0 |
| (0.95, 0.98) | früher, Δt₅₀ ≈ −6 bis −7 (Schwanz 16.0) | 0 | 0 |
| (0.9, 0.95) | 0 | Faktor 0.4 → t₅₀ ≈ 13 | 0 |
| (0.9, 0.995) | 0 | Faktor 4 → t₅₀ ≈ 130 | 0 |

Grundlage der ersten Spalte: Vor dem Wechsel bewegt bias-korrigiertes Adam bei gleichbleibendem Gradienten ≈ 1 Update je Schritt, fast unabhängig von β₁/β₂; nur der Schwanz nach dem Wechsel ändert sich
(Skalarmodell, Koordinaten ≠ Fourier-Richtungen; post hoc gestützt nur bei t = 25–35, N38).

## Versuch (Entwurf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Verschiebt sich das Festlegungsfenster mit β₁ (Verschiebungsuhr), mit β₂ (Horizont) oder gar nicht (Schrittuhr)? |
| **Protokoll** | wie EXP-059/N28: add 113, EXP-053-Splits ω = 0, Wechsel A → B und B → A bei t, danach 2000 Schritte, GPU, 1 Thread; π gegen reine A-/B-Läufe **derselben β-Zelle** (β ändert auch die Endpunkte) |
| **Zellen** | die vier oben plus Referenz (0.9, 0.98) |
| **t-Gitter** | {10, 20, 30, 40, 55, 80, 130} in allen Zellen (deckt alle Vorhersagen ab) |
| **Seeds** | 830–839 (frisch, Pilot; vorher nirgends genutzt, geprüft 16:21) |
| **Umfang** | 5 × 7 × 2 × 10 = 700 Wechselläufe + 5 × 2 × 10 = 100 reine Läufe ≈ 800 Läufe à ≈ 2000–2130 Schritte; bei 4 GPU-Prozessen grob 3 h (Durchsatz vorher messen) |
| **Primär (Exploration)** | je Seed Δt₅₀ = t₅₀(Zelle) − t₅₀(Referenz), gepaart; Vorzeichentest je Zelle; kein Urteil mit Bestätigungscharakter |
| **Lesart vorab** | *Verschiebungsuhr gestützt:* Δt₅₀(0.95, ·) < −3 und Δt₅₀(0.8, ·) > +2 (je ≥ 8/10 Seeds), β₂-Zellen \|Median Δ\| < 10. *β₂-Horizont gestützt:* Δt₅₀(·, 0.995) > +40 und Δt₅₀(·, 0.95) < −10 (je ≥ 8/10), β₁-Zellen \|Median Δ\| < 3. *Schrittuhr gestützt:* alle \|Median Δ\| < 3. Sonst *gemischt/unklar*. Nicht gekreuzt im Gitter → zensiert, berichtet |
| **Was dagegen spräche** | Muster, das keines der drei trifft (z. B. beide β wirken) → keine einfache Optimierer-Uhr (N37/N38 verworfen oder beide teilweise) |
| **Grenzen** | β verändert nicht nur die Uhr, sondern auch den Verlauf vor dem Wechsel (Glättung, Stabilität; β₂ = 0.95 kann instabil sein) → Instabilität je Zelle berichten (NaN, Genauigkeit der reinen Läufe); eine Aufgabe; grobes Gitter; 10 Seeds = Pilot |
| **Abbruch** | NaN/Divergenz in > 2 Seeds einer Zelle → Zelle *nicht auswertbar* |
| **Bereits gesehene Daten** | EXP-059 (Seeds 400–409: π-Kurve, Momentum-Verschiebung), N28/N29 (Fenster 25–50), EXP-039 (Λ-Uhr besser, Pilot). Beeinflusst: Wahl von β₁ als Hebel, Gitter, Referenz-t₅₀ |

## Ziel in FINDINGS

Größte offene Frage („Was macht die frühe Wahl fest?“). Entscheidet zwischen drei explizit benannten Konkurrenzmodellen (Regel 18c).

## Nächste Schritte

1. Nach der Nacht 27./28.: `--beta1/--beta2` in `freq_ban.py` (Standard = Preset, alte Run-IDs unverändert, Fingerprint nur bei Abweichung, wie `--lr`), Test, Codex-Prüfung.
2. Nach R3: Design neu bewerten, `jobs.txt` und `analyze.py` (t₅₀-Interpolation, Lesart oben) schreiben, Codex-Prüfung der Auswertung.

## Nachtrag a (Sitzung 27, 16:25 Berlin, gemessen, vor jedem Lauf und vor jedem Code): Design nach unabhängiger Prüfung ersetzt

Ein Prüfagent (nur Lesen) hat den Entwurf angegriffen. Ich habe jeden Punkt selbst nachvollzogen (Nachrechnung mit `clock_predictions.pre_and_tail`).
- **Blocker 1 (übernommen): Der β₁-Arm über t₅₀ ist zu schwach.** Δt₅₀ ≈ +5/−6 liegt unter dem Gitterabstand; bei π-SD 0.1–0.2 je Seed ergäbe die Lesart „≥ 8/10“ meist *unklar*, auch wenn die Verschiebungsuhr stimmt (Fehlerklasse EXP-080).
- **Blocker 2 (übernommen): Der β₂-Horizont hat im Modell keinen Mechanismus.** Bias-korrigiertes v̂ ist ab Schritt 1 unverzerrt (Skript: Vorlauf = 25.00 für jedes β). Die Skalierung mit 1/(1 − β₂) ist eine Skalierungs**hypothese ohne Mechanismus** (N37 entsprechend umbenannt).
- **S1 (übernommen):** Auch die Verschiebungsuhr sagt einen β₂-Effekt voraus: Schwanz bei t = 33 für β₂ = 0.95 **10.8–12.4** statt 8.9 (r = 0.5 … 0), für 0.995 9.8–10.2. Vorzeichen wie N37, aber ≈ 2–3 statt ≈ 20 Schritte.
- **S2 (übernommen als Messung):** β wirkt auch nach dem Wechsel (Überschreibrate). Die Aufteilung „β nur vor / nur nach dem Wechsel“ braucht konsistente Bias-Korrektur beim Umschalten (Trainer-Eingriff, Codex) → als Option für einen zweiten Schritt, nicht im ersten Piloten.
- **S3/S4:** Gitter und Lesart überflüssig durch das neue Design (feste t statt t₅₀).
- **Klein:** Gültigkeit L(A) − L(B) ≥ 2 je Zelle aus EXP-059 übernehmen; Smoke je β-Zelle (Stabilität β₂ = 0.95 bei wd 1) vor dem Einfrieren; `analyze.py` samt Lesart vor jedem Lauf festlegen.

### Neues Design (ersetzt die Tabelle „Versuch“ oben; Seeds 830–839 bleiben)

**Teil A, β₁ über den Momentum-Schwanz (direkter N38-Test):** β₁ ∈ {0.8, 0.9, 0.95} (β₂ = 0.98), je normal und m-Löschen (`--reset-optim-part m`) bei **t = 25**. Vorhersage N38: Der Abfall Δπ = π_normal − π_m wächst mit dem Schwanz,
**≈ 4.0–4.5 / 8.7–10.8 / 16–24 Schritte** (β₁ = 0.8 / 0.9 / 0.95, r = 1 … 0) mal die lokale Steigung von π. Primär (Exploration): Rangordnung Δπ(0.8) < Δπ(0.9) < Δπ(0.95), gepaart je Seed, Seitenvergleich 0.95 gegen 0.8
(einseitiger Vorzeichentest, 10 Seeds). *Gegen N38 spräche:* kein Anstieg oder Δπ(0.95) ≤ Δπ(0.8). Grenze: β₁ ändert auch die Steigung von π (eigene π_normal-Kurve je β₁ bei t = 20/25/30 als Umrechnung, beschreibend).

**Teil B, β₂ bei festem t (Skalierungshypothese N37 gegen Verschiebungsuhr):** β₂ ∈ {0.95, 0.98, 0.995} (β₁ = 0.9), normal, **t ∈ {25, 33, 45}**. Vorhersagen bei t = 33 (Referenzkurve EXP-059: π(33) ≈ 0.49):
N37 → π(0.95) nahe 1 (wie t ≈ 82 der Referenz), π(0.995) nahe 0 (wie t ≈ 8); Verschiebungsuhr → Abweichung von der Referenzzelle höchstens wie ≈ 2–3 Schritte (≈ ±0.1); Schrittuhr → keine.
Primär: gepaarte Differenz π(β₂) − π(0.98) bei t = 33 je Zelle mit Bootstrap-KI; Lesart vorab: **N37 gestützt**, wenn π(0.95) − π(0.98) > +0.3 **und** π(0.995) − π(0.98) < −0.3; **N37 verworfen**, wenn beide KI in [−0.15, +0.15] liegen; sonst *unklar*. t = 25/45 beschreibend.

**Beide Teile:** π gegen reine A-/B-Läufe derselben β-Zelle; `--log-update-norms` bis zum Wechsel in allen Zellen (gemessene Verschiebung statt Modell, Sekundär: fallen alle Zellen auf eine Kurve π(gemessene Verschiebung + Schwanz)?). Gültigkeit wie EXP-059.
**Umfang:** A: 3 × 2 × 2 × 10 = 120 (+ π_normal bei t = 20/30: 3 × 2 × 2 × 10 = 120) ; B: 3 × 3 × 2 × 10 = 180 (Referenzzelle teilt Läufe mit A bei t = 25); reine Läufe 5 Zellen × 2 × 10 = 100. **≈ 500 Läufe**, nach EXP-059-Durchsatz (200 Läufe ≈ 20 min mit 8 Arbeitern) ≈ 1 h.
**Unverändert:** kein Code bis nach dem Einfrieren der Nachtblöcke; `--beta1/--beta2` mit Codex; Start nach R3; `analyze.py` vor jedem Lauf.

**Stichprobe Teil A (Sitzung 27, 16:36, gemessen; Simulation aus EXP-059, bekannte Seeds):** Abfall π_normal − π_m bei t = 25 und β₁ = 0.9: Mittel 0.186, SD 0.098 (10 Seeds); Steigung π(20 → 30) 0.0195 je Schritt. Vorhergesagte Abfälle
(Schwanz × Steigung): β₁ = 0.8 → 0.078–0.088, β₁ = 0.95 → 0.31–0.47; zur Kontrolle β₁ = 0.9 → 0.17–0.21 (gemessen 0.186). Power des einseitigen Vorzeichentests (≥ 9/10) für Δπ(0.95) − Δπ(0.8) > 0 bei gleicher SD je Zelle, unabhängig
(konservativ): **0.93–1.00** → 10 Seeds reichen für den Piloten. Annahmen: lineare Steigung, gleiche Streuung in allen β₁-Zellen.
**Hinweis Sitzung 28 (Exploration, gesehene Seeds):** Das Nullsetzen des ersten Moments senkt den Energieanteil der alten Ziele, nicht ihre innere Rangfolge ([[JOURNAL]] Sitzung 28, Zyklus 19). Die hier gesuchte Uhr betrifft also die *Menge*; für π als Kennzahl ändert das nichts, eine Rangmessung wäre kein geeigneter Zusatzendpunkt.

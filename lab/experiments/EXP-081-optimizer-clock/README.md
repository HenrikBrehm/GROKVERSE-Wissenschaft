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

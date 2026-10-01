---
id: EXP-137
status: abgeschlossen
datum: 2026-10-01
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
verwandt: ["[[experiments/EXP-136-large-modulus/README|EXP-136]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-137: Steuert die Trainingsmenge bei größerem Modulus auch mit weniger Daten, wenn das Netz noch generalisiert? (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds × F/G je Zelle), keine Bestätigung.** Folge von [[experiments/EXP-136-large-modulus/README|EXP-136]]; Kandidat [[NOVEL_DIRECTIONS]] N63.

**Bezug zu FINDINGS:** K2 (Programm A, Regel 15c/20b). EXP-136 zeigte K2 bei add 211/307 mit 30 % Daten; mit 3831 Paaren (8.6 % / 4.1 %) generalisierte kein Lauf in 20 000 Schritten, die Frage „Steuerung bei geringer Datendichte“ blieb daher unbeantwortbar. LeDoux 2026 (arXiv 2603.25047) berichtet bei p = 9973 und 0.3 % Daten, die Frequenz entstehe unabhängig von der Zusammensetzung der Trainingsmenge. Dieser Pilot sucht zwischen 4–9 % und 30 % die Dichte, bei der das Netz noch generalisiert, und misst dort die Steuerung **nach** der Generalisierung. Begründung gegen Regel 15b (kein automatischer Mini-Versuch): Das ist der stärkste offene Gutachter-Einwand (Regel 20b), und die GPU würde sonst nach EXP-128/129 leer laufen (Regel 20i).

## Vorab (Sitzung 67, 2026-10-01, 05:45 Berlin gemessen; vor jedem Blocklauf)

- **Frage:** Geben die konstruierten Splits (EXP-043, ε = 2) die gelernten Frequenzen bei add p = 211 und 307 auch mit 10 %, 15 % und 20 % Daten vor, gemessen nach der Generalisierung?
- **Hypothese:** ja, in allen Zellen, in denen generalisiert wird; Δ_pow kleiner bei weniger Daten (Maskensignal kleiner).
- **Konkurrenzmodell (LeDoux-Lesart):** Mit abnehmender Dichte legt etwas anderes als die Menge die Frequenzen fest → |Δ_pow| ≤ 1 nach der Generalisierung bei kleinen Anteilen.
- **Aufbau:** unveränderter Trainer `freq_ban.py` (1 Schicht, AdamW lr 1e-3, wd 1, Vollbatch, GPU), Test = Komplement. Seeds 13700–13702 (neu), je Zelle F und G mit disjunkten Zielen; nur `TRAIN_FRAC` von `make_split.py` wird überschrieben (wie EXP-136). Höchstens 30 000 Schritte, Stopp 2000 Schritte nach der Generalisierung, W_E-Schnappschüsse bei 50, 250, 500 und alle 1000 Schritte. 2 p × 3 Anteile × 3 Seeds × 2 Arme = 36 Läufe.
- **Messgröße (primär):** Δ_pow (wie P1/EXP-136) am ersten gemeinsamen Schnappschuss ≥ max(gen_F, gen_G) + 1000; ein Seed zählt nur, wenn beide Arme generalisieren (`first_crossing_step` des primären Generalisierungsübergangs).
  *Geändert ≈ 05:46 (zwischen den Messungen 05:45 und 05:47), vor jedem Blockergebnis:* Ein gemeinsamer Schritt ≥ max(gen) + 1000 existiert nicht, wenn ein Arm mehr als 1000 Schritte früher generalisiert (er stoppt bei seinem gen + 2000). Deshalb wird jeder Arm am ersten eigenen Schnappschuss ≥ eigenes gen + 1000 gelesen; Δ_pow ist eine Summe zweier Log-Verhältnisse innerhalb je eines Laufs, die Arme dürfen also an verschiedenen Schritten gelesen werden.
- **Lesart je Zelle (`analyze.py`, vor jedem Blocklauf geschrieben):** < 2 auswertbare Seeds → „kein Lernen im Budget“; sonst unter den auswertbaren: alle Δ_pow > 1 → „steuert“; mindestens die Hälfte |Δ_pow| ≤ 1 → „bricht“; sonst „unklar“.
- **Nachtrag nach der unabhängigen Codeprüfung (Sitzung 67, Lesart 05:54 gemessen festgelegt, Code 05:55; vor jedem Blockergebnis – zu diesem Zeitpunkt 4 Läufe gestartet, keiner fertig, nichts gelesen; der Prüfer sah nur Status/Schritt/Testgenauigkeit ≤ 0.011 der laufenden Läufe):**
  - *Kalibrierte Zellenlesart (HIGH der Prüfung, an EXP-136 nachgeprüft):* Die Placebo-SD von Δ_pow war in EXP-136 bei auswendig lernenden Netzen 0.11–0.15, bei generalisierten aber 1.21–1.91 – die Schwelle 1 ist nach der Generalisierung also unkalibriert. Je auswertbarem Seed: Placebo-Δ_pow für 2000 zufällige disjunkte Fünfermengen außerhalb F ∪ G an denselben zwei Spektren; q99/q90 = 99-/90-%-Quantil von |Placebo|. „steuert“: alle auswertbaren Seeds Δ_pow > q99; „nicht unterscheidbar“: mindestens die Hälfte Δ_pow ≤ q90; sonst „unklar“. **Die Gesamtlesart je p nutzt ab jetzt die kalibrierte Zellenlesart** („bricht“ dort → „nicht unterscheidbar“); die Schwelle-1-Lesart wird daneben berichtet.
  - *Neue Kategorie:* ≥ 2 Seeds mit beiden Armen generalisiert, aber < 2 auswertbar (z. B. gen > 29 000, Ladeproblem) → „nicht auswertbar“ statt „kein Lernen im Budget“.
  - *Beschreibend ergänzt (MEDIUM):* Δ_pow am letzten Schnappschuss vor der eigenen Generalisierung je Arm („dpow_pre“, Abdruck der Auswendiglernphase; Masken-Δ ist hier schon 1.09–2.45) zum Vergleich mit dpow_post; Spearman zusätzlich je p (die gepoolte Zahl misst vor allem Unterschiede zwischen Zellen).
  - Selbsttest modelliert jetzt den echten Stopp je Arm (gen + 2000), gen > 29 000, einen nie generalisierenden Arm und großes Placebo-Rauschen.
- **Gesamtlesart je p (Pilot, beschreibend über die Anteile):** alle auswertbaren Zellen „steuert“ und kleinster auswertbarer Anteil ≤ 15 % → „K2 hält bei p mit weniger Daten“; kleinste auswertbare Zelle „bricht“, f20 „steuert“ → „Steuerung schwindet mit der Dichte“; keine auswertbare Zelle → „kein Lernen im Budget“; sonst „beschreibend“.
- **Beschreibend:** Δ_pow bei 2000 (wie EXP-136), Generalisierungsschritte, End-Genauigkeit, Top-5-Überlappung, Mittel je Zelle (steigt Δ_pow mit dem Anteil?).
- **Vorhersage erster Ordnung (vorab, `make_jobs.py --mask` → `mask_prediction_s67.json`, kein Lauf):** Masken-Δ je Seed: p 211 f10 1.09–1.24, f15 1.61–1.63, f20 1.95–2.07; p 307 f10 1.45–1.50, f15 1.98–2.02, f20 2.41–2.45. Vorhersage (beschreibend): Δ_pow nach Generalisierung steigt je p mit dem Anteil; Spearman(Masken-Δ, Δ_pow) > 0. Vorsicht aus der EXP-136-Prüfung: Dort kam die Korrelation fast nur aus dem Gegensatz generalisiert/auswendig (innerhalb der 30-%-Zellen −0.26); hier zählen nur generalisierte Seeds, die Prüfung ist also strenger.
- **Was dagegen spräche:** |Δ_pow| ≤ 1 nach der Generalisierung in mindestens der Hälfte der Seeds einer Zelle.
- **Budget/Abbruch:** gemessen p = 211, 10 %: 0.069 s/Schritt unter Last (Lader-Test); p = 307, 30 % in EXP-136: 0.13–0.16 s/Schritt. Schlimmster Fall (kein Lauf generalisiert) ≈ 35–75 min je Lauf; 5 Worker, `gpu_gb=1.5`, harte Grenze 120 min je Lauf. Ein abgebrochener oder nicht generalisierter Lauf beweist nicht, dass Generalisierung unmöglich ist.
- **Grenzen:** eine Architektur, ein Optimierer; p ≤ 307, Anteile ≥ 10 % (weit weg von LeDoux' 0.3 %); Paarzahl und Anteil gekoppelt; Seeds über additive Salze wie EXP-043/136 (Pilot; eine Bestätigung bräuchte getrennte Ströme, Astra 5); Einbettungsenergie, keine Ablation.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** (1) EXP-136 (alle Ergebnisse): Wahl der Anteile 10/15/20 % zwischen „nie generalisiert“ (4–9 %) und „schnell generalisiert“ (30 %, gen 150–575), Budget 30 000 statt 20 000, Primärmessung nach der Generalisierung statt bei 2000. (2) Lader-Test nach dem Schreiben der Lesarten (`raw_loadtest/`, 1000 Schritte): Seed 13700, p = 211, 10 %, nur Arm F: bis 1000 nicht generalisiert, Top-5 am Ende = eigene Ziele, 0.069 s/Schritt. Δ_pow wurde nicht berechnet (nur ein Arm). Der Block wiederholt diesen Lauf.

## Befehle

```
python lab/experiments/EXP-137-modulus-density/make_jobs.py > lab/queue/staging/48_exp137_density.jobs && mv lab/queue/staging/48_exp137_density.jobs lab/queue/inbox/
python lab/experiments/EXP-137-modulus-density/make_jobs.py --check
python lab/experiments/EXP-137-modulus-density/make_jobs.py --mask
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-137-modulus-density/analyze.py [--selftest]
```

## Ergebnis

**Ausgewertet Sitzung 67 (01.10., 07:29 Berlin gemessen; Dienst 36/36, keine Fehler). Gesamtlesart (placebo-kalibriert): p 211 und p 307 je „K2 hält bei p mit weniger Daten“.** Pilot, 3 Seeds je Zelle.

| p | Anteil | Zelle (kalibriert / Schwelle 1) | Δ_pow nach Generalisierung je Seed | Placebo-q99 | Δ_pow vor gen | gen-Schritte (F, G) |
|---|---|---|---|---|---|---|
| 211 | 10 % | kein Lernen im Budget | – (0/6 generalisiert; Test bis 0.84) | – | – | – |
| 211 | 15 % | steuert / steuert | 11.11 / 10.55 / 10.90 | 4.26 / 5.81 / 4.83 | 7.63 / 6.85 / 6.63 | 10700/4425, 3700/4250, 3125/5275 |
| 211 | 20 % | steuert / steuert | 11.77 / 10.30 / 10.93 | 4.42 / 4.90 / 3.86 | 6.04 / 5.41 / 5.52 | 1225/550, 650/550, 525/550 |
| 307 | 10 % | steuert / steuert | 8.18 / 10.86 / 10.39 | 3.80 / 5.69 / 4.80 | 6.33 / 7.69 / 7.70 | 6300/8850, 6125/8175, 9100/11500 |
| 307 | 15 % | steuert / steuert | 9.30 / 10.52 / 8.93 | 3.48 / 4.98 / 4.92 | 6.13 / 5.33 / 5.36 | ≈ 500 |
| 307 | 20 % | steuert / steuert | 9.19 / 11.82 / 9.02 | 4.32 / 4.33 / 4.79 | 4.03 / 1.42 / 1.42 | ≈ 200–325 |

- **Hauptbefund (Pilot):** Wo das Netz bei größerem p mit weniger Daten noch generalisiert (bis 10 % bei 307, bis 15 % bei 211), steuert die Split-Konstruktion die Frequenzen auch nach der Generalisierung deutlich (Δ_pow 8.2–11.8, jeweils über dem Placebo-99-%-Quantil). Top-5 nach Generalisierung: 3–5 eigene Ziele je Arm.
- **Vorhersage erster Ordnung trifft nicht:** Δ_pow steigt nach der Generalisierung nicht mit dem Anteil (Mittel je Zelle 9.6–11.0), Spearman(Masken-Δ, Δ_pow) −0.10 (n = 15), je p 0.03 / −0.12. Die Masken-Ordnung aus EXP-136 (0.85) war also, wie die Prüfung vermutete, vor allem der Gegensatz generalisiert/auswendig; nach der Generalisierung sättigt Δ_pow.
- **Beschreibend:** Am letzten Schnappschuss vor der eigenen Generalisierung (25–850 Schritte davor) war Δ_pow schon 5.3–7.7 – dort stieg die Testgenauigkeit meist schon (0.44–0.93), es sind also *keine* reinen Auswendiglern-Netze (Korrektur nach der Prüfung; der Name „dpow_pre = Abdruck der Auswendiglernphase“ im Vorab-Text trifft nicht zu); bei 307 f20 war dieser Schnappschuss Schritt 50 (vor dem Anpassen, 1.4–4.0). Nicht placebo-geeicht.
- **Paarzahl statt Anteil?** 307 mit 10 % = 9425 Paare generalisiert, 211 mit 10 % = 4452 Paare nicht (und EXP-136: 3831 Paare nie) – passt eher zu einer Mindest-Paarzahl als zu einem Mindestanteil; nicht getrennt.
- **Einordnung zu LeDoux:** Die Steuerung reicht bis zur Grenze, an der in unserem Budget überhaupt generalisiert wird; über 0.3 % / p = 9973 sagt der Pilot nichts.
- **Paper:** Absatz in Anhang A.2 (draft §3.11, nach EXP-136), Grenze (ii) ergänzt; unabhängige Nachrechnung und Textprüfung laufen.
- **Folge (offen, nicht eingereiht):** Bestätigungsblock bei p = 307, 10 % (≥ 10 frische Seeds, SeedSequence, eingefroren, Placebo-Lesart) – wenn das Paper die Verallgemeinerung über p als Ergebnis tragen soll.

*Nachrechnung und Textprüfung (Sitzung 67, 07:32 gemessen; Claude-Agent, eigener numpy-Code, 20 000 Placebo-Ziehungen):* alle Δ_pow-Werte, Lesarten und Spearman bestätigt; Placebo-q99 je nach Ziehung 3.4–5.7 statt 3.5–5.8 (kein Urteil ändert sich, kleinster Abstand 8.18 gegen ≈ 3.8). Übernommen: HIGH „memorizing networks … just before generalization“ falsch (siehe oben), MEDIUM „did not rise“ → „no consistent trend“, LOW Grenze (ii) „down to“ und Placebo statt „well above“, Hinweis „nur Einbettungsenergie“. Abweichung von der Vorlage: Anhang-Absatz länger als ein Satz (keine neue Kernaussage, kein Abstract).

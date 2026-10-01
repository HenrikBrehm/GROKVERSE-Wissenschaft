---
id: EXP-136
status: abgeschlossen
datum: 2026-10-01
tags: [exp/abgeschlossen, befund/unklar, neu/kandidat]
verwandt: ["[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[confirm/L0_REGISTRATION_DRAFT|L0]]", "[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-136: Steuert die Trainingsmenge die Frequenzwahl auch bei größerem Modulus und kleinem Datenanteil? (Pilot)

Zurück zu [[LAB]]. **Exploration (3 Seeds × F/G je Zelle), keine Bestätigung.** Kandidat [[NOVEL_DIRECTIONS]] N63.

**Bezug zu FINDINGS:** K2 (Programm A, Regel 15c) ist bei p = 97 und 113 bestätigt (P1, [[experiments/EXP-043-generalize-steering/README|EXP-043]]), immer mit 30 % Daten. LeDoux 2026 (arXiv 2603.25047) schreibt, bei p = 9973 und 0.3 % Daten entstehe dieselbe Frequenz „regardless of initialization or training set composition“. Unsere Arbeiten decken weder großes p noch kleinen Datenanteil ab – der naheliegende Gutachter-Einwand nach L0/L0b. Dieser Pilot geht zwei Schritte in diese Richtung.

## Vorab (Sitzung 65, 2026-10-01, 00:51 Berlin gemessen; vor jedem Lauf des Blocks)

- **Frage:** Gibt die Split-Konstruktion (EXP-043, ε = 2) die gelernten Frequenzen auch bei add p = 211 und 307 vor, und zwar (hi) bei 30 % Daten und (lo) bei gleich vielen Trainingspaaren wie add 113 (3831 Paare = 8.6 % bzw. 4.1 %)?
- **Hypothese:** ja in allen vier Zellen; bei „lo“ schwächer (die Maske trägt weniger Zielanteil: 0.07–0.08 bzw. 0.045–0.048 gegen 0.14–0.16 bei „hi“; Top-5 der Maske = Ziele in allen 24 Splits, `make_jobs.py --check`).
- **Konkurrenzmodell (LeDoux-Lesart):** Bei großem p / wenig Daten legt etwas anderes als die Menge die Frequenzen fest → |Δ_pow| ≤ 1.
- **Aufbau:** unveränderter Trainer `freq_ban.py` (Standard-Transformer, AdamW lr 1e-3, wd 1, Vollbatch, GPU), Test = Komplement. Seeds 13600–13602 (neu), je Zelle F und G mit disjunkten Zielen; nur die Modulkonstante `TRAIN_FRAC` von `make_split.py` wird für „lo“ überschrieben. 20 000 Schritte höchstens, Stopp 2000 Schritte nach der Generalisierung, W_E-Schnappschüsse bei 50, 250, 500, 1000, 2000, 5000, 10 000, 20 000.
- **Messgröße (primär):** Δ_pow (wie P1) der W_E-Gruppenleistung bei Schritt 2000 zwischen F- und G-Lauf eines Seeds.
- **Lesart je Zelle (`analyze.py`, vor jedem Lauf geschrieben):** Δ_pow(2000) > 1 in 3/3 → „steuert“; |Δ_pow(2000)| ≤ 1 in ≥ 2/3 → „bricht“; sonst „unklar“; < 3 gültige Seeds → „nicht auswertbar“. Beschreibend: Δ_pow am letzten Schnappschuss, Top-5-Überlappung, Generalisierungsschritt, End-Genauigkeit.
- **Zweitlesart (nach der unabhängigen Codeprüfung, ≈ 00:53 (Zeit nachträglich aus der Messung 00:54 eingegrenzt), vor jedem Blocklauf; gekennzeichnet, ändert die Primärlesart nicht):** dieselbe Regel auf Δ_pow am letzten Schnappschuss („verdict_end“), zusammen mit der Zahl nie generalisierter Läufe je Zelle. Grund (Prüfer): Bei wenig Daten kann der Wert bei Schritt 2000 aus der Auswendiglern-Phase stammen; ein „bricht“ bei 2000 hieße dann nicht „Steuerung braucht Datendichte“. Die Gesamtlesart „Steuerung braucht Datendichte“ wird nur vergeben, wenn auch „verdict_end“ bei „lo“ nicht „steuert“.
- **Gesamtlesart:** alle vier „steuert“ → „K2 hält bei größerem p, auch mit wenig Daten“ (dann Bestätigungsblock mit ≥ 10 frischen Seeds erwägen); „hi“ steuert, „lo“ bricht → „Steuerung braucht Datendichte“ (ein Befund für die Grenzen, passt zu LeDoux' Regime); „hi“ bricht → K2 hängt an kleinem p. Sonst beschreibend.
- **Was dagegen spräche:** |Δ_pow| ≤ 1 bei 2000 in mindestens zwei Seeds einer Zelle.
- **Budget/Abbruch:** gemessen (unter Last, neben L0b): p = 307 hi 0.149 s/Schritt (Stopp nach ≈ 2200 Schritten ≈ 6 min, 1.35 GB), p = 307 lo 0.046 s/Schritt, p = 211 lo 0.038 s/Schritt (20 000 Schritte ≈ 13–15 min); 24 Läufe, 4 Worker, `gpu_gb=1.5`, harte Grenze 90 min je Lauf.
- **Grenzen:** eine Architektur und ein Optimierer; p = 307 ist weit von LeDoux' 9973; der Datenanteil ist mit der Zahl der Paare gekoppelt (lo hält die Paarzahl fest, nicht den Anteil); Seeds über additive Salze wie EXP-043 (Astra 5: für einen Piloten hingenommen, eine Bestätigung braucht getrennte Ströme).
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** (1) Smoke p = 307 hi, Seed 13600, F, 200 Schritte: Generalisierung schon nach 175 Schritten (bei großem p und 30 % kaum Grokking-Verzögerung) → deshalb die zweite Achse „lo“ ergänzt. (2) Smoke p = 307 lo, 300 Schritte (nur Tempo). (3) Lader-Test (nach dem Schreiben der Lesarten, `raw_loadtest/`, 2000 Schritte): Seed 13600, p = 211 lo, F und G: Δ_pow(2000) = 1.24, Top-5 = eigene Ziele in beiden Armen, Test 0.003 (noch keine Generalisierung). Dieser Seed ist damit teilweise gesehen; die Lesart wurde danach nicht geändert. Der Block-Lauf (20 000-Schritt-Budget, anderes Verzeichnis) wiederholt ihn.

- **Rauschkalibrierung (beschreibend, 01:00, am schon gesehenen Lader-Test-Seed; ändert keine Lesart):** Δ_pow für 2000 zufällige disjunkte Placebo-Fünfermengen außerhalb F ∪ G in denselben Läufen (p = 211, 3831 Paare, Schritt 2000): Mittel 0.00, SD 0.14, 99 %-Quantil |Δ_pow| 0.34; echter Wert 1.24. Die Schwelle 1 liegt also ≈ 7 SD über dem Placebo-Rauschen (konservativ). `analyze.py` gibt die Placebo-SD je Seed beschreibend mit aus.

- **Vorhersage erster Ordnung (vorab, 02:00, `mask_prediction_s65.py`, kein Lauf):** Masken-Δ (Formel von Δ_pow auf dem Maskenspektrum der Splits) je Seed: p = 211 hi 2.53–2.61, lo 0.98–1.04; p = 307 hi 3.16–3.22, lo 0.64–0.80. Vorhersage (beschreibend, kein Urteil): (1) Δ_pow(2000) ist je p bei „lo“ kleiner als bei „hi“; (2) über die 12 Seed-Zellen ist die Spearman-Korrelation von Masken-Δ und Δ_pow(2000) positiv. Ein Widerspruch hieße: Die Theorie erster Ordnung ordnet die Stärke der Steuerung in diesem Regime nicht.

## Befehle

```
python lab/experiments/EXP-136-large-modulus/make_jobs.py > lab/queue/staging/45zzz_exp136_modulus.jobs && mv lab/queue/staging/45zzz_exp136_modulus.jobs lab/queue/inbox/
python lab/experiments/EXP-136-large-modulus/make_jobs.py --check
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-136-large-modulus/analyze.py [--selftest]
```

## Codeprüfung (Sitzung 65, ≈ 00:53, unabhängiger Claude-Agent, nur lesend)

Keine Blocker. Geprüft: Zuordnung der Läufe über den Split-Dateinamen, exakte `train_frac`-Rundreise, keine Run-ID-Kollisionen (hi/lo, andere Versuche), Schnappschuss bei 2000 immer vorhanden (Stopp frühestens bei gen + 2000), `group_power`/Δ_pow wie EXP-043/P1, Lesarten wie im README. Übernommen: Zweitlesart am letzten Schnappschuss + Zahl nie generalisierter Läufe (MEDIUM 1/2), Top-5 mit Gleichstandsregel wie EXP-043 (LOW 6). Verworfen (ohne Wirkung): Laufzeit der Dateisuche, `None`-Schutz für `train_frac` (Feld immer gesetzt).

## Ergebnis

**Ausgewertet Sitzung 66 (01.10., 05:31 Berlin gemessen; Dienst 24/24, keine Fehler). Gesamtlesart: keines der drei vorab benannten Muster → „beschreibend“** (Pilot, 3 Seeds je Zelle).

| p | Daten | Δ_pow(2000) je Seed | Zelle | Δ_pow am Ende | Zweitlesart | nie generalisiert |
|---|---|---|---|---|---|---|
| 211 | 30 % | 9.86 / 9.52 / 11.07 | steuert | gleich | steuert | 0/6 |
| 211 | 3831 Paare | 1.24 / 1.37 / 1.39 | steuert | 1.61 / 1.77 / 1.64 | steuert | **6/6** |
| 307 | 30 % | 10.41 / 8.49 / 12.35 | steuert | gleich | steuert | 0/6 |
| 307 | 3831 Paare | 0.73 / 0.82 / 0.86 | bricht | 0.62 / 0.74 / 0.87 | bricht | **6/6** |

- **Bei 30 % Daten hält K2 bei größerem p deutlich** (Δ_pow 8.5–12.4, alle Läufe generalisieren).
- **Mit wenig Daten generalisiert kein Lauf** innerhalb von 20 000 Schritten (beide p, 12/12). Die Δ_pow-Werte dort beschreiben also die Repräsentation eines auswendig lernenden Netzes, nicht einer gelernten Rechenregel; die vorab bedachte Lesart „Steuerung braucht Datendichte“ ist deshalb nicht vergeben (sie hätte auch bei p 211 „bricht“ verlangt). Ein abgebrochener bzw. nicht generalisierter Lauf beweist nicht, dass Generalisierung hier unmöglich ist (längeres Budget nicht geprüft).
- **Vorhersage erster Ordnung (vorab, S65) trifft:** lo < hi bei beiden p; Spearman(Masken-Δ, Δ_pow(2000)) = 0.85 (n = 12 Seed-Zellen). Die Stärke der Neigung folgt dem Frequenzsignal der Maske (Masken-Δ p 211 lo 0.98–1.04 → Δ_pow 1.2–1.4; p 307 lo 0.64–0.80 → 0.7–0.9).
- **Einordnung zu LeDoux:** Bei wenig Daten fehlt in unserem Budget schon die Generalisierung; über LeDoux' Regime (p = 9973, 0.3 %) sagt der Pilot nichts. Was er zeigt: Die Datensteuerung ist nicht auf p ≤ 113 beschränkt, und ihre Stärke skaliert mit dem Signal der Maske.
- **Nächster Schritt (offen, nicht eingereiht):** Paper nach [[paper/EXP136_DEUTUNGEN]] (Fall „sonst beschreibend“; Satz für Anhang/Grenze (ii)) mit unabhängiger Textprüfung. Folgeversuch nach BACKLOG Punkt 3: „hi steuert“ → Bestätigungsblock bei p = 211/307, 30 % (≥ 10 frische Seeds) erwägen; für „lo“ zuerst ein Budget, in dem überhaupt generalisiert wird (z. B. 4× Paare oder längeres Training), sonst bleibt die Frage unbeantwortbar.

Paper-Sätze je Ausgang vorab: [[paper/EXP136_DEUTUNGEN]].

*Nachtrag Sitzung 67 (05:47 Berlin; unabhängige Textprüfung des Anhangsatzes, Claude-Agent, nur lesend):* Alle Zahlen bestätigt. Einschränkung zur Vorhersage erster Ordnung: Spearman 0.85 entsteht fast nur aus dem Gegensatz „generalisiert (30 %) / auswendig (3831 Paare)“; innerhalb der sechs 30-%-Zellen ist die Rangkorrelation −0.26, innerhalb der sechs lo-Zellen 1.0. Die Masken-Δ ordnen die generalisierten Läufe also nicht. Folgeversuch, der nur generalisierte Läufe vergleicht: [[experiments/EXP-137-modulus-density/README|EXP-137]] (10/15/20 % Daten, beim Dienst). Paper: Satz in Anhang A (draft §3.11) mit dieser Einschränkung.

---
id: EXP-073
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[experiments/EXP-067-exclusion-part/README|EXP-067]]", "[[experiments/EXP-071-ov-lead-predicts/README|EXP-071]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-073: Welcher Netzteil trägt die Zeitabhängigkeit der Festlegung? Teilweises Zurückspulen beim Datenwechsel (PILOT)

Zurück zu [[LAB]] · [[FINDINGS]] „Größte offene Frage“ (Programm B: was macht die frühe Wahl fest, wenn keine gemessene Zustandsgröße den Zeitverlauf besser erklärt als die Schrittzahl?).
Festgelegt 2026-09-27, Sitzung 24, **vor jedem EXP-073-Lauf** (außerhalb des Fensters; Läufe ab 00:00). **Pilot**, bekannte Seeds 400–409 (EXP-056-Splits, ω = 0), kein Urteil.

- **Idee (neues Werkzeug `--rewind-at-switch X --rewind-from R` in `freq_ban.py`):** Beim Wechsel bei t = 50 wird ein Teil X des Netzes, **samt seinem AdamW-Zustand**, auf seinen eigenen Zustand nach
  Schritt R = 25 zurückgesetzt; alle anderen Teile behalten ihren Stand von t = 50. So hat X nur 25 A-Schritte „gesehen“, der Rest 50. Anders als die Resets auf die Init (N29b/N29c, EXP-067) ist das
  eine gleich große Zeitdosis statt einer maximalen Störung; es fragt direkt nach der **Zeitabhängigkeit** zwischen 25 und 50.
- **Eingebaute Korrektheitsprüfung:** X = alles („all“) muss den Lauf mit Wechsel bei 25 reproduzieren (konstante Lernrate, kein Zeitplan; der Trainer-Test `test_rewind` prüft das bitgleich auf der CPU).
- **Arme** (je A→B und B→A, danach 2000 Schritte auf dem zweiten Split, `--save-model`, GPU, 1 Thread): ref25, ref50, rwall, rwwe (nur W_E), rwattn (W_Q, W_K, W_V, W_O), rwvo (W_V, W_O),
  rwrest (alles außer W_E, auch W_pos, MLP, W_U). 7 Arme × 10 Seeds × 2 Richtungen = 140 Läufe.
- **Maß:** π wie EXP-056/059 (Anteil der ersten Wahl im logarithmischen Energieverhältnis der End-W_E, Mittel beider Richtungen). Je Seed q_X = (π_X − π_25)/(π_50 − π_25):
  q ≈ 0 heißt „das Zurückspulen von X allein nimmt die ganze Festigkeit der 25 Zusatzschritte weg“, q ≈ 1 heißt „X spielt für die Zeitabhängigkeit keine Rolle“.
- **Konkurrenzmodelle** (vorher benannt): (1) der Amplitudenvorsprung in W_E; (2) der Zustand des übrigen Netzes, v. a. des Wertepfads (passt zu N29b/c); (3) multiplikatives Wachstum über den Pfad
  W_E·W_V·W_O (beide nötig); (4) Redundanz (jeder Teil allein hält).
- **Lesart vorab** (Median-q über gültige Seeds, Schwellen 0.3 / 0.7). *Nach Codex (s24, vor jedem Lauf) als Rückspul-Empfindlichkeit formuliert, nicht als „Träger“:* Ein Chimären-Netz ist beim
  Wechsel nicht aufeinander abgestimmt, das Ergebnis lokalisiert also keinen Speicherort.
  q_we ≤ 0.3 und q_rest ≥ 0.7 → *empfindlich nur für W_E-Rückspulen* (stützt 1); q_rest ≤ 0.3 und q_we ≥ 0.7 → *empfindlich nur für Rest-Rückspulen* (stützt 2);
  beide ≤ 0.3 → *empfindlich für beide* (stützt 3); beide ≥ 0.7 → *unempfindlich für beide einzeln* (stützt 4); sonst *gemischt*. Beschreibend: q_attn, q_vo; Loss-Sprung auf dem neuen Split durch das
  Zurückspulen selbst (Trainer-Ereignis `diag_before`/`diag_after`), damit eine reine Störwirkung erkennbar ist.
- **Zweitgröße Funktion (beschreibend, vor jedem Lauf ergänzt, Sitzung 24):** je Arm R = Mittel beider Richtungen von (Genauigkeit ohne die NEUEN Ziele in W_E − Genauigkeit ohne die ALTEN),
  gemeinsame EXP-056-Testmenge, `function()` aus EXP-067; R > 0 heißt „stärker auf die alte Wahl angewiesen“. Kein Urteil (Modelle nach 2000 Schritten nicht immer generalisiert).
- **Gültigkeit:** je Seed alle 14 Läufe über den gemeinsamen Lader ok, Rewind vom Trainer geprüft (`events.rewind_at_switch.check`), L(A) − L(B) ≥ 2, π_50 − π_25 ≥ 0.2; ≥ 8 gültige Seeds.
  **Technisch ungültig**, wenn |π_rwall − π_25| > 0.05 in einer Richtung (A→B oder B→A getrennt, Codex s24) eines gültigen Seeds (dann misst das Werkzeug nicht, was es soll).
- **Bereits gesehene Daten:** π(t) aus EXP-059 an denselben Seeds (π_25 ≈ 0.30, π_50 ≈ 1.05); Resets auf die Init (EXP-067, N29b, N29c): Attention-/Wertepfad-Reset hebt die Wirkung auf, MLP-Reset kaum.
  Davon beeinflusst: Wahl der Arme attn/vo. Es gibt noch keine Beobachtung zu einem Zurückspulen auf einen Zwischenzustand.
- **Dagegen spräche / Grenzen:** Ein Chimären-Netz ist beim Wechsel nicht aufeinander abgestimmt (Teile aus verschiedenen Zeitpunkten); ein großer Sprung im Loss direkt nach dem Wechsel wäre eine
  Störung, die über die Zeitdosis hinaus wirkt (`train_acc_after` wird aufgezeichnet). π ist ein Spektralmaß (Energie), keine Nutzung; Modelle sind für eine spätere Funktionsauswertung gespeichert.
  Pilot mit 10 bekannten Seeds; ein klares Muster wäre an frischen Seeds zu bestätigen.
- **Neuheit (vorläufig):** „teilweises Zurückspulen einzelner Netzteile samt Optimiererzustand auf einen früheren Trainingszeitpunkt“, um die Zeitabhängigkeit einer Festlegung zu lokalisieren; Suche
  vom 27.09. (Sitzung 24, [[NOVEL_DIRECTIONS]] N33): Modul-Zurückspulen selbst ist bekannt (Chatterji et al. 2019, am fertigen Netz ohne Weitertraining); die Anwendung beim Datenwechsel samt
  Optimiererzustand und Weitertraining nicht gefunden. Neue Anwendung eines bekannten Werkzeugs.
- **Budget:** 140 Läufe à 2025–2050 Schritte, GPU 8 parallel, EXP-059-Erfahrung (200 Läufe ≈ 20 min) → ≈ 15 min. Abbruch bei NaN oder wenn `test_rewind` scheitert.

## Codex-Prüfung (Sitzung 24, vor jedem Lauf; `codex_review_s24.txt`)

Vier Blocker gemeldet, alle selbst geprüft und übernommen: (1) der Test `test_rewind` hatte keine Testmenge (Wechselläufe brauchen `--test-file`) → EXP-056-Splits mit gemeinsamer Testmenge, eindeutige
Treffer; (2) Ban-/Shrink-Bedingungen würden nicht zurückgespult → `--rewind-at-switch` nur mit `--condition baseline`; (3) Chimären-Störung → Lesarten als Empfindlichkeit, Loss/Genauigkeit auf neuem und
altem Split vor und nach dem Zurückspulen im Trainer-Ereignis; (4) Gleichheitsprüfung rwall = ref25 je Richtung statt gemittelt. Bestätigt ohne Änderung: Zeitpunkt des Schnappschusses, Wiederherstellen
des AdamW-Zustands (alle Tensoren geklont, Gerät bleibt), Fingerabdruck-Kompatibilität, 140 eindeutige Jobs, π-Normierung. Die Trainer-Änderung ist bis zum Test im Fenster **ungetestet**. Nachprüfung der vier Korrekturen durch Codex (Sitzung 24, `codex_recheck_s24.txt`): keine verbleibenden Blocker, keine neuen Fehler.

```
python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py
python lab/tools/parallel_queue.py lab/experiments/EXP-073-part-rewind/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-073-part-rewind/analyze.py
```

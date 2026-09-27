---
id: P2e-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[confirm/P2d_REGISTRATION|P2d]]", "[[experiments/EXP-066-p2d-other-tasks/README|EXP-066]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# P2e-Bestätigung (P2d-Maß bei mul 113 und add 97): Registrierung (Sitzung 23). **ENTWURF**

Zurück zu [[FINDINGS]] (Programm A, „K2-Funktion (P2d)“; Regel 15c: Verallgemeinerung) · Pilot [[experiments/EXP-066-p2d-other-tasks/README|EXP-066]] · Vorgänger [[confirm/P2d_REGISTRATION|P2d]] (add 113, bestätigt).

- **Aussage P2e (je Aufgabe):** In Modellen mit konstruiertem Split senkt ein Parameterschritt gleicher Norm entlang der **eigenen Zielfrequenzen** in den Zahlenzeilen von W_E (Gruppenordnung) den
  mittleren Logit-Abstand stärker als derselbe Schritt entlang gleich großer Kontrollmengen. Aussage über eine lokale endliche Störung (δ = 2 % von ‖X‖, keine Ableitung), nur W_E, eine Perturbationsform (wie P2d); Mittel über alle 20 Seeds nach 8000 Schritten.
- **Aufgaben:** **mul 113** (Zeilen g^i, g = 3, Frequenzen über Z_112) und **add 97** (Frequenzen über Z_97). D₅₉ nicht (anderes Maß nötig).
- **Modelle:** frische Seeds **2270–2289** (n = 20 je Aufgabe), je Arm F und G, `confirm_splits.build` mit Versuchs-ID **5**, eps 2.0,
  `--steps 8000 --stop-after-gen 8000 --save-model`, GPU, 1 Thread. 80 Läufe.
- **Maß:** wie EXP-066 (P2d im Gruppenbasis-Format): u_S = P_S X / ‖P_S X‖, X' = X − δ·u_S, drop_S = Logit-Abstand vorher − nachher auf den Paaren in keinem der beiden Splits.
  4 Kontrollmengen je Arm aus 1..(n−1)//2 ohne eigene, fremde Ziele und fold(2k) der eigenen (RNG [5, Aufgabe, p, Seed, Arm]).
  **Primär je Aufgabe:** D_s = Mittel über beide Arme von (drop_eigen − Mittel drop_Kontrolle). Einseitiger t-Test (Mittel > 0), 95-%-Bootstrap-KI.
- **Familie:** {mul 113, add 97}, Holm. Eine nicht auswertbare Aufgabe zählt als p = 1 (schlimmster Fall).
- **Urteil je Aufgabe:** Jeder technische Ausfall (auch Lade- oder Rechenfehler) → *nicht auswertbar*; sonst **„bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0.05** (Logit-Einheiten),
  sonst *nicht bestätigt*. **Primär zählen alle 20 Seeds** (wie N29; ein Genauigkeitsfilter wäre ergebnisabhängig). Wie viele Modelle generalisiert haben (≥ 0.9 in beiden Armen), wird berichtet,
  dazu beschreibend, ohne Urteil, D nur an diesen Seeds.
- **Stichprobe:** Pilot EXP-066 (P1-Modelle, 2000 Schritte): mul 113 D = 0.159 ± 0.031 (n = 43), add 97 D = 0.218 ± 0.067 (n = 26). Falls Effekt und Streuung sich auf 8000 Schritte übertragen, liegt die KI-Untergrenze bei n = 20 deutlich über 0.05 (grob 0.14 bzw. 0.18).
- **Warum 8000 Schritte:** Bei 2000 Schritten waren 24/50 add-97-Modelle unter 0.9 (EXP-066). Die Läufe sind kurz (≈ 33 s je 2000 Schritte auf der GPU allein).
  Eine längere Laufzeit ändert möglicherweise die Größe von D; das ist in Kauf genommen und wird so berichtet. Da alle Seeds zählen, hängt das Urteil nicht davon ab, wie viele generalisieren.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** add 113: P2c/P2d/EXP-065 (Maß, δ, Kontrollen); mul 113 und add 97: EXP-066 an den P1-Modellen (Seeds 1000–1049, Richtung und Größe von D;
  daraus Schrittzahl 8000 und Mindestgröße 0.05 wie P2d). Seeds 2270–2289 wurden vorher nie benutzt; Versuchs-ID 5 erzeugt eigene Splits und Ziele.
- **Grenzen:** zwei zyklische Aufgaben (nach Umbenennung beide Z_n), eine Architektur, eine Dosis, eine lokale endliche Störung, u_S amplitudengewichtet (Frequenzidentität und gelernte Norm nicht getrennt).
- **Vor dem Einfrieren:** Codex-Prüfung (Regel 18c); ein echter Job bis zum Ende durch den eingefrorenen Lader; Manifest mit Code-Hashes und Commit.
- Code: `lab/tools/confirm_p2e.py` (Selbsttest ok, Sitzung 23, 09:49; nach Codex geändert, Selbsttest mit Semantik- und Import-Prüfung erneut ok), Maß-Funktionen aus `lab/experiments/EXP-066-p2d-other-tasks/analyze.py` (im Code-Hash).

```
python lab/tools/confirm_p2e.py --splits lab/confirm/P2e_manifest.json
python lab/tools/confirm_p2e.py --jobs lab/confirm/P2e_manifest.json > lab/confirm/P2e_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/P2e_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_p2e.py --analyze lab/confirm/P2e_manifest.json
```

## Codex-Prüfung (Sitzung 23, Ergebnis vor 10:00 Berlin)

Keine Fehler in der Übertragung (Log-Ordnung g = 3, Zeile 0 ausgenommen, Etiketten, Testmenge, Nyquist ausgeschlossen, Versuchs-ID-5-Ströme, Run-IDs, Holm mit Platzhalter). Übernommen, selbst geprüft:
(1) Lade- und Rechenfehler werden als technischer Ausfall erfasst statt die Auswertung abzubrechen; (2) + (3) primär alle Seeds statt Genauigkeitsfilter mit 80 %-Regel (auch Konsistenz mit N29);
(4) „erster Ordnung“ → „lokale endliche Störung“, Power-Aussage bedingt formuliert; (5) Selbsttest prüft Log-Ordnung, Projektion bei n = 112 (k = 55), Kontrollpool ohne Nyquist und alle geladenen lab-Module gegen die Hash-Liste.

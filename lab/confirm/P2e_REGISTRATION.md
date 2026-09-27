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
  mittleren Logit-Abstand stärker als derselbe Schritt entlang gleich großer Kontrollmengen. Lokale Aussage (δ = 2 % von ‖X‖), nur W_E, eine Perturbationsform (wie P2d).
- **Aufgaben:** **mul 113** (Zeilen g^i, g = 3, Frequenzen über Z_112) und **add 97** (Frequenzen über Z_97). D₅₉ nicht (anderes Maß nötig).
- **Modelle:** frische Seeds **2270–2289** (n = 20 je Aufgabe), je Arm F und G, `confirm_splits.build` mit Versuchs-ID **5**, eps 2.0,
  `--steps 8000 --stop-after-gen 8000 --save-model`, GPU, 1 Thread. 80 Läufe.
- **Maß:** wie EXP-066 (P2d im Gruppenbasis-Format): u_S = P_S X / ‖P_S X‖, X' = X − δ·u_S, drop_S = Logit-Abstand vorher − nachher auf den Paaren in keinem der beiden Splits.
  4 Kontrollmengen je Arm aus 1..(n−1)//2 ohne eigene, fremde Ziele und fold(2k) der eigenen (RNG [5, Aufgabe, p, Seed, Arm]).
  **Primär je Aufgabe:** D_s = Mittel über beide Arme von (drop_eigen − Mittel drop_Kontrolle). Einseitiger t-Test (Mittel > 0), 95-%-Bootstrap-KI.
- **Familie:** {mul 113, add 97}, Holm. Eine nicht auswertbare Aufgabe zählt als p = 1 (schlimmster Fall).
- **Urteil je Aufgabe:** Jeder technische Ausfall → *nicht auswertbar*; < 80 % geeignet (Basis-Genauigkeit ≥ 0.9 in beiden Armen, also < 16/20) → *nicht auswertbar*;
  sonst **„bestätigt“ = Holm-p < 0.05 und KI-Untergrenze ≥ 0.05** (Logit-Einheiten), sonst *nicht bestätigt*. D aller nicht-technischen Seeds wird beschreibend mitberichtet.
- **Stichprobe:** Pilot EXP-066 (P1-Modelle, 2000 Schritte): mul 113 D = 0.159 ± 0.031 (n = 43), add 97 D = 0.218 ± 0.067 (n = 26). Bei n = 20 liegt die erwartete KI-Untergrenze weit über 0.05.
- **Warum 8000 Schritte:** Bei 2000 Schritten waren 24/50 add-97-Modelle unter 0.9 (EXP-066). Die Läufe sind kurz (≈ 33 s je 2000 Schritte auf der GPU allein).
  Eine längere Laufzeit ändert möglicherweise die Größe von D; das ist in Kauf genommen und wird so berichtet.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** add 113: P2c/P2d/EXP-065 (Maß, δ, Kontrollen); mul 113 und add 97: EXP-066 an den P1-Modellen (Seeds 1000–1049, Richtung und Größe von D;
  daraus Schrittzahl 8000 und Mindestgröße 0.05 wie P2d). Seeds 2270–2289 wurden vorher nie benutzt; Versuchs-ID 5 erzeugt eigene Splits und Ziele.
- **Grenzen:** zwei zyklische Aufgaben (nach Umbenennung beide Z_n), eine Architektur, eine Dosis, lokale Größe erster Ordnung, u_S amplitudengewichtet (Frequenzidentität und gelernte Norm nicht getrennt).
- **Vor dem Einfrieren:** Codex-Prüfung (Regel 18c); ein echter Job bis zum Ende durch den eingefrorenen Lader; Manifest mit Code-Hashes und Commit.
- Code: `lab/tools/confirm_p2e.py` (Selbsttest ok, Sitzung 23, 09:49), Maß-Funktionen aus `lab/experiments/EXP-066-p2d-other-tasks/analyze.py` (im Code-Hash).

```
python lab/tools/confirm_p2e.py --splits lab/confirm/P2e_manifest.json
python lab/tools/confirm_p2e.py --jobs lab/confirm/P2e_manifest.json > lab/confirm/P2e_jobs.txt
python lab/tools/parallel_queue.py lab/confirm/P2e_jobs.txt --workers 7
python lab/tools/guarded_run.py -- python lab/tools/confirm_p2e.py --analyze lab/confirm/P2e_manifest.json
```

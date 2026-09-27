---
id: EXP-066
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv]
verwandt: ["[[FINDINGS]]", "[[confirm/P2d_REGISTRATION|P2d]]", "[[experiments/EXP-065-p2d-pilot/README|EXP-065]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-066: Gilt der P2d-Befund auch bei mul 113 und add 97? (EXPLORATION, keine neuen Läufe)

Zurück zu [[LAB]] · [[FINDINGS]] Programm A („K2-Funktion (P2d)“, offene Frage: gilt das in anderen Aufgaben?) · Vorbild [[experiments/EXP-065-p2d-pilot/README|EXP-065]].
Festgelegt 2026-09-27 (Sitzung 23), **vor der Rechnung**. **Exploration/Pilot**: Sie dient nur der Planung einer Bestätigung an frischen Seeds und liefert kein Urteil.

- **Modelle:** die gebundenen P1-Modelle (Manifest 733e829, 2000 Schritte, GPU) für **mul 113** und **add 97**, Seeds 1000–1049, Arme F und G. Geladen über den P1-Lader und die P1-Bindung
  (Hash → Laden → Hash, `bound_bytes`). Die Spektren dieser Modelle sind aus P1 bekannt, das Maß wurde an ihnen noch nie berechnet.
- **Maß (P2d, übertragen):** Zahlenzeilen von W_E in Gruppenordnung (add 97: a = 0..96; mul 113: g^i, i = 0..111, g = 3; Zeile 0 bei mul unverändert). Für eine Frequenzmenge S:
  u_S = P_S X / ‖P_S X‖ (P_S = Projektion auf cos/sin der Frequenzen in S über Z_n), X' = X − δ·u_S mit δ = 0.02·‖X‖ für alle Mengen gleich.
  drop_S = mittlerer Logit-Abstand (richtige Klasse minus beste falsche) vorher − nachher, auf den Paaren in keinem der beiden Splits.
  Kontrollen: 4 Mengen à 5 Frequenzen aus 1..(n−1)//2 ohne eigene Ziele, fremde Ziele und fold(2k) der eigenen (wie EXP-051), RNG [66, Aufgabe, Seed, Arm].
  **D_s = Mittel über beide Arme von (drop_eigen − Mittel drop_Kontrolle).**
- **Eignung:** Basis-Genauigkeit ≥ 0.9 in beiden Armen; berichtet werden auch die übrigen Seeds.
- **Frage für die Planung:** Ist D > 0 in (fast) allen Seeds beider Aufgaben, in ähnlicher Größe wie bei add 113 (P2d: 0.250 [0.229, 0.270])? Streuung → Stichprobe der Bestätigung.
  **Was dagegen spräche:** D ≈ 0 oder uneinheitlich in einer Aufgabe. Dann gilt die P2d-Aussage dort nicht in dieser Form, und das wird genauso berichtet.
- **Grenzen:** bekannte Modelle, 2000 statt 4000 Schritte, eine Dosis, lokale Größe erster Ordnung, u_S amplitudengewichtet (wie P2d). D₅₉ (Irreps statt Frequenzen) folgt getrennt.
- **Budget:** 200 Modelle, nur Vorwärtsrechnungen auf der CPU, wenige Minuten.

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-066-p2d-other-tasks/analyze.py
```

## Ergebnis (Sitzung 23, Rechnung 09:45–09:48 Berlin, gemessen; `summary.json`): Exploration

Alle 200 Modelle geladen und gebunden (0 technische Ausfälle). D = Mittel über beide Arme von (Abfall eigen − Mittel Abfall Kontrolle), Logit-Einheiten, δ = 2 % von ‖X‖:

| Aufgabe | geeignet (Basis ≥ 0.9) | D̄ (geeignete) | 95-%-KI | > 0 | Median Abfall eigen / Kontrolle | alle 50 Seeds: D̄, > 0 |
|---|---|---|---|---|---|---|
| mul 113 | 43/50 | **0.159** (SD 0.031, Min 0.125) | [0.150, 0.168] | 43/43 | 0.148 / 0.0006 | 0.160, 50/50 |
| add 97 | 26/50 | **0.218** (SD 0.067, Min 0.137) | [0.194, 0.243] | 26/26 | 0.170 / −0.003 | 0.190, 50/50 |
| *add 113 (P2d, frisch, 4000 Schritte)* | *20/20* | *0.250* | *[0.229, 0.270]* | *20/20* | | |

- **Lesart (Exploration):** Die stärkere Margin-Reaktion entlang der gesteuerten Frequenzen zeigt sich bei mul 113 und add 97 in jedem Modell, etwas kleiner als bei add 113.
  Viele add-97-Modelle waren nach 2000 Schritten noch nicht generalisiert (24/50 unter 0.9); D ist dort trotzdem positiv.
- **Grenzen:** bekannte P1-Modelle, 2000 Schritte, Maß von add 113 übernommen (nicht neu optimiert), eine Dosis, lokale Größe, amplitudengewichtete Richtung.
- **Für die Bestätigung:** Effekt groß und einheitlich (SD 0.03–0.07). Mit 20 frischen Seeds je Aufgabe und 4000 Schritten ist jede sinnvolle Mindestgröße (z. B. 0.05) sicher prüfbar.
  Nächster Schritt: Registrierung „P2e“ (mul 113, add 97; Holm über beide), wie P2d eingefroren. D₅₉ braucht ein Irrep-Maß und kommt getrennt.

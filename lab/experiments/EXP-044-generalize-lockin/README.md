---
id: EXP-044
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-020-data-switch/README|EXP-020]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[experiments/EXP-041-imprint/README|EXP-041]]", "[[BEFUND-festlegung]]", "[[FINDINGS]]"]
---
# EXP-044: Frühe Festlegung (K4) bei anderen Aufgaben, mit fast vollständigem Datenwechsel

**Status:** vorbereitet, **nicht ausgeführt**, Code ungetestet. Definition fixiert 2026-09-26 19:22 Berlin (Sitzung 11), vor jedem
Lauf und vor jedem Ergebnis von EXP-043. Ziel in [[FINDINGS]]: K4 außerhalb von Addition mod 113 (größte offene Frage).
**Bedingt:** läuft nur für die Aufgaben, die in [[experiments/EXP-043-generalize-steering/README|EXP-043]] *steuerbar* sind (ohne
Steuerung ist ein Wechsel F → G nicht lesbar; die Queue prüft das selbst). GPU, nach bestandenem GPU-001.

## Idee

[[experiments/EXP-020-data-switch/README|EXP-020]] fand bei Addition mod 113: Nach 25–50 Schritten auf F überwiegen die F-Frequenzen,
obwohl danach 2000 Schritte auf G folgen. Zwei Grenzen (Sitzung 10): eine Aufgabe, und F/G teilten ≈ 73 % der Paare. EXP-044 prüft
beides zugleich: Aufgaben add 97 / mul 113 (EXP-043-Konstruktion in Gruppenkoordinaten) und **unabhängig gezogene** F und G
(Überlappung 37–39 %, gemessen: mul 113 1411–1456 von 3831, add 97 1054–1097 von 2823; der Wechsel tauscht also ≈ 62 % der Paare).

| | |
|---|---|
| **Fragestellung** | Legt sich das Netz auch bei add 97 / mul 113 und fast vollständigem Datenwechsel früh auf die F-Frequenzen fest? |
| **H44** | d(150) > 0: Nach 150 Schritten F und 2000 Schritten G enthält K mehr F- als G-Ziele |
| **Design** | Je Aufgabe Seeds 80–89; gemeinsame Testmenge T* (20 %); Läufe: nur F (2000), nur G (2000), Wechsel bei t ∈ {25, 50, 150} (t Schritte F, dann genau 2000 G, gleiches G-Budget wie EXP-020 Nachtrag a) |
| **K** | Top-5 der W_E-Leistung in der Gruppenbasis (wie EXP-043) am letzten Schritt; d = \|K ∩ F\| − \|K ∩ G\| |
| **Gültig** | alle 5 Läufe `completed` auf `cuda`, Hashes passen, und die Konstruktion steuert in diesem Seed: d(nur F) > 0, d(nur G) < 0 |
| **Test** | Vorzeichentest über gültige Seeds auf d(150) (Gleichstände weg), einseitig; Holm über die gelaufenen Aufgaben |
| **Urteil je Aufgabe** | *festgelegt*: mittleres d(150) > 0 und Holm-signifikant · *richtungsgleich, n. s.* · *widerspricht*: mittleres d(150) ≤ 0 · < 8 gültige Seeds: *nicht auswertbar* |
| **Warum t = 150 primär** | Bei EXP-020 war K ab t = 150 exakt „nur F“; der härtere Wechsel (62 % statt 27 % neue Paare) soll nicht an einem zu frühen Gitterpunkt scheitern. t = 25 und 50 sind sekundär (Intervall der Festlegung, beschreibend) |
| **Sekundär** | mittleres d(t) für t = 25/50/150; wie oft t = 150 vor der Memorisierung liegt (erster Schritt mit Train-Acc ≥ 0.99 in „nur F“); Genauigkeiten auf G\F beim Wechsel; Test-Acc auf T* |
| **Erwartung** | *festgelegt* bei add 97 (wie EXP-020, trotz härterem Wechsel); mul 113 offen |
| **Was dagegen spräche** | d(150) ≤ 0: Das Netz folgt den neuen Daten; dann war die Festlegung aus EXP-020 an den Teilwechsel oder an Addition mod 113 gebunden. Beides wird in [[FINDINGS]] als Grenze von K4 eingetragen |
| **Grenzen** | K = W_E-Top-5 (nicht funktional); ein Gitterpunkt primär; „vor der Memorisierung“ nur beschreibend; Adam-Zustand läuft über den Wechsel weiter (wie EXP-020) |
| **Budget** | je Aufgabe 10 × (2000 + 2000 + 2025 + 2050 + 2150) ≈ 102 000 GPU-Schritte, J parallel |

## Befehle

```
python lab/experiments/EXP-044-generalize-lockin/make_splits.py --task mul --p 113     # und --task add --p 97 (erzeugt)
sh lab/experiments/EXP-044-generalize-lockin/queue.sh J      # liest EXP-043 summary.json, Smoke, Läufe, Auswertung
python lab/tools/guarded_run.py -- python lab/experiments/EXP-044-generalize-lockin/analyze.py
```

## Nachtrag Sitzung 12 (2026-09-26 ~19:55 Berlin, nach Codex, **vor jedem Lauf**)

Codex-Prüfung `EXP-043-generalize-steering/codex_review_s12_2026-09-26.txt` (2 Blocker, 1 hoch, 2 mittel, 3 niedrig), übernommen:
Queues scheitern nicht mehr „offen“ (Ablehnung des Wächters rc 3 in parallelen Läufen stoppt alles, andere Fehler werden gezählt,
die Queue endet dann mit rc 1 „done WITH FAILURES“); GPU-001-Durchsatz zählt eine Stufe J nur, wenn alle J Läufe fertig sind, die
Hauptqueue verlangt Regression, Gleichwertigkeit und Durchsatz bestanden; `freq_ban.py --force` löscht den alten `result.json`;
Auswertungen werten fehlende/abgebrochene Läufe als ungültig statt abzustürzen; EXP-044 prüft den Test-Hash und rechnet Holm
über **alle gelaufenen** Aufgaben (wie hier vorab festgelegt, der Code wich ab). Diagnose-Schrittnummern in GPU-001 korrigiert.
Nicht geändert: `config.device` bleibt „cpu“ (maßgeblich ist das Feld `device` oben im result.json; alle Auswertungen nutzen es);
Seed 70/99 wurden früher schon benutzt, aber bei anderem p bzw. anderer Architektur, also andere Init (Einschränkung notiert).
Urteilsregeln unverändert.

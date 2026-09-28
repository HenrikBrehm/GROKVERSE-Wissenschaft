---
id: EXP-099
status: zurückgestellt
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]  # zurückgestellt nach Regel 20a
---
# EXP-099: Bestimmt Adams Koordinatenbasis, welche Frequenzen die frühe Bewegung wählt? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage: Warum ist die frühe Bewegung frequenzselektiv?) · [[NOVEL_DIRECTIONS]] N49 · Vorgänger [[experiments/EXP-095-gradient-feedback/README|EXP-095]] (Nachtrag b/c), [[experiments/EXP-097-sign-vs-staleness/README|EXP-097]]

**Festgelegt vor jedem EXP-099-Lauf** (Sitzung 43, 2026-09-28, Fenster zu; `design.py`, `analyze.py`, Trainer-Patch `trainer_wef.patch`; alles ungetestet bis 29.09. 00:00).

## Frage und konkurrierende Vorhersagen

AdamW normiert elementweise in der Token-Basis von W_E. Bei einem wenig veränderlichen Gradienten ist das fast ein Vorzeichenschritt, und die Vorzeichenbildung entlang der Token-Achse streut Energie auf Nicht-Ziel-Frequenzen (EXP-095 Nachtrag b/c). **Eingriff:** Derselbe Trainer, dieselbe Init, dieselben Daten, aber AdamW arbeitet auf den DFT-Koordinaten C = Bᵀ·W_E[:p] (B die feste orthonormale reelle DFT-Basis). Funktional ist das Modell identisch, nur die Geometrie des Optimierers ändert sich (eine Rotation; entkoppelter Weight Decay ist rotationsinvariant).
- **V1 (Streuung):** Ohne Streuung durch die Token-Vorzeichen ist die frühe Bewegung selektiver: f(n24F) > f(n24).
- **V2 (Angleichung):** In DFT-Koordinaten gleicht Adam die Schrittgrößen der Frequenzen an (Vorzeichen je Frequenzkoeffizient). Die vom Split bevorzugten Frequenzen, die den größten Gradienten haben, wachsen nicht mehr schneller: f(n24F) < f(n24), und die Datensteuerung der reinen Läufe wird schwächer.

## Aufbau

Wie EXP-095 (add 113, ω = 0-Splitpaare nach EXP-053, Wechsel A → B und B → A bei t = 24, danach 2000 Schritte mit demselben Optimierer; GPU). **Seeds 3680–3695** (frisch; Dateisuche 28.09. ohne Treffer). Reine A/B-Läufe in beiden Parametrisierungen (tok, four). Zellen: **n24** (Token-Adam, frisch), **g24** (Token-Adam, nur Anfangsgradient), **n24F** (Fourier-Adam, frisch), **g24F** (Fourier-Adam, nur Anfangsgradient). 12 Läufe je Seed, **192 GPU-Läufe** (≈ 20 min mit 8 Workern).

## Lesarten (verbindlich, im Code)

Gepaarte Bootstrap-KIs über technisch gültige Seeds (10 000, rng 99):
- **Q1 (primär, frühe Selektivität):** Δf = f(n24F) − f(n24). KI-Untergrenze > 0 → **„V1 (Streuung)“**; KI-Obergrenze < 0 → **„V2 (Angleichung)“**; sonst „unentschieden“.
- **Q2 (Datensteuerung der reinen Läufe):** ΔS = S(four) − S(tok), S = L(A) − L(B). KI > 0 → „Steuerung stärker“, KI < 0 → „Steuerung schwächer“ (stützt V2), sonst „unentschieden“.
- < 10 technisch gültige Seeds → beide *nicht auswertbar*.
- **Beschreibend:** π je Zelle gegen die reinen Läufe derselben Parametrisierung (nur Seeds mit S ≥ 2 in beiden), Δπ(n24), e24 in beiden Parametrisierungen (schrumpft der g24-Nachteil unter Fourier-Adam, wie V1 erwartet?), Anzahl Seeds mit S < 2 je Parametrisierung.
- **Keine Erwartung festgelegt**; beide Vorhersagen sind vorab begründet. Die Post-hoc-Hinweise (EXP-095 Nachtrag b/c; R9, JOURNAL Sitzung 43) sprechen für V1, die Rechnung zur Angleichung für V2.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-095 (Nachträge a–c), R9 post hoc (Vorzeichenanteil q; toleranzabhängig), EXP-057 (leerer Adam-Zustand senkt π: deshalb läuft der Fourier-Arm durchgehend mit Fourier-Adam, kein Wechsel des Optimierers). Keine Seeds aus diesen Blöcken.

## Reihenfolge und Befehle (ab 00:00; erst NACH EXP-097, weil der Patch auf dessen Patch aufsetzt)

```
# Voraussetzung: trainer_psu.patch aus EXP-097 ist angewendet, getestet und committet
git apply lab/experiments/EXP-099-fourier-adam/trainer_wef.patch
python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py   # 10 Tests grün (neu: we_fourier_adam)
git add lab/experiments/EXP-001-freq-ban/freq_ban.py lab/tests/test_freq_ban_fingerprint.py; git commit
python lab/tools/guarded_run.py -- python lab/experiments/EXP-099-fourier-adam/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-099-fourier-adam/smoke.txt --workers 3
python lab/tools/guarded_run.py -- python lab/experiments/EXP-099-fourier-adam/analyze.py --smoke-check
python lab/tools/parallel_queue.py lab/experiments/EXP-099-fourier-adam/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-099-fourier-adam/analyze.py
```
Splits, `jobs.txt`, `smoke.txt` sind schon erzeugt (`design.py`, reines numpy). Scheitert ein Test: Patch zurücknehmen, Fehler im JOURNAL, EXP-099 nicht starten.

## Statische Prüfung (Sitzung 43, 19:15) und Status

**Zurückgestellt nach Regel 20a** (Wochenplan: keine Mechanismus-Detailversuche). **Vor jedem Start zu beheben (MAJOR):** Mit vollem Batch und fast konstantem Gradienten ist Adams frühe Bewegung in *jeder* Basis ein Vorzeichenschritt. In DFT-Koordinaten bewegt sich damit jeder Koeffizient um ±lr, und die Leistung je Frequenz ist nahezu gleichverteilt (numpy-Beispiel des Prüfers: Zielanteil 0.054 = Gleichverteilung, egal wie stark der Gradient auf den Zielen liegt). „V2“ ist damit fast konstruktionsbedingt, und g24F ist exakt gleichverteilt. Ein V2-Ergebnis sagt nichts darüber, ob die Token-Streuung (V1) existiert. **Korrektur:** einen rotationsinvarianten Arm ergänzen (linear normierte Schritte wie EXP-097 `normgd`, lr·g/rms(g) ist in beiden Basen gleich): f(normgd) − f(tok) misst die Streuung, f(normgd) − f(four) die Angleichung. Oder die Gleichverteilungsvorhersage für n24F vorab festlegen. Q2 (S bei 2000) ist mit der Lerngeschwindigkeit verwechselt → Generalisierungsschritt, Train-Genauigkeit und S bei 250 beschreibend ergänzen. Kleinere Punkte: `max_coord_dev` prüft nur die Orthonormalität von B (besser: Bᵀ·W_E[:p] gegen C vor dem Schritt); der Test erkennt eine fehlende `W_E.grad = None`-Zeile nicht. Code des Patches sonst ohne Befund (alle erlaubten Pfade geprüft).

## Ergebnis

*(noch nicht ausgeführt)*

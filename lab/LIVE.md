---
tags: [lab/live]
---
# LIVE: Laborsitzung 42: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-28 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 18:11 Berlin
- **Run-Fenster:** heute bis 18:00 (Wächter), ab 29.09. wieder 00:00–13:00.

## Gerade

**Sitzung beendet.** Keine Läufe aktiv. Heute: **EXP-095**: Die frühe Festlegung braucht frische Gradienten unterwegs. Mit nur 3 Auswertungen in den ersten 24 Schritten legt das Modell so schwach fest wie mit 3 großen Schritten; mit nur dem Anfangsgradienten bewegen sich vor allem die falschen Frequenzen zu stark. **Reproduktionspaket vollständig** (alle neun Skripte exakt). Bestätigung **R10** eingefroren, 268/480 gerechnet. EXP-096 (andere Aufgaben) vorbereitet. Nächster geplanter Start laut runner-state.json: **19:34 Berlin** (Läufe erst ab 00:00).

## Als Nächstes

Nacht: R10 fertigrechnen und auswerten, dann EXP-096.

## Verlauf dieser Sitzung

- 18:11 Sitzung beendet (Abschlussbericht im JOURNAL).
- 18:10 EXP-096 statisch geprüft, vier kleine Korrekturen.
- 18:02 EXP-096 vorbereitet (add 97 / mul 113).
- 17:58 Post hoc: ohne Auffrischung wachsen die Nicht-Ziele ×1.48; bei seltener Auffrischung wachsen die Ziele weniger.
- 17:52 Wächter stoppt R10 regulär (268/480, 0 Fehler).
- 17:36 Repro **mul 113 exakt** → Paket vollständig.
- 17:26 Repro mul 113: 2. technischer Fehler („No HIP GPUs“), dritter Versuch mit weniger Last.
- 17:20 Repro **P2e reproduziert** (Abweichung ≤ 9·10⁻⁸).
- 17:15 R10-Block gestartet (4 Worker).
- 17:14 R10 eingefroren (7b583bdb), Smoke 5/5, Laderprüfung ok.
- 17:11 Prüfung vor dem Einfrieren: kein Code-Fehler; ein wichtiger Vorbehalt (Adams Zähler nach dem Wechsel) eingearbeitet.
- 17:00 R10-Registrierung und Code (n = 48; Power 0.92/1.00/0.99 bei halbem Effekt).
- 16:58 Paper-Absatz zu EXP-095 geprüft: Zahlen stimmen; drei Formulierungen vorsichtiger („Rückkopplung“ war nur vermutet).
- 16:49 Repro **k2 add 97 bitgenau**; k2 mul 113 technisch gescheitert (GPU unter Last), wird neu gerechnet.
- 16:54 **EXP-095: „Auswertungen zählen“** (e8 = +0.14, g8 = c8b genau; nur Anfangsgradient: π 0.10 statt 0.28).
- 16:32 Repro **K4b bitgenau** (N28, 30 Seeds).

- 16:25 EXP-095: ≈ 60/192 Läufe fertig, keine Fehler; Repro k4b läuft (langsamer, GPU geteilt). Literatur zu N48 dokumentiert.
- 16:13 EXP-095-Block gestartet (Smoke 3/3 ok vorher).
- 16:12 Unabhängige Prüfung der Trainer-Option: keine Blocker, zwei kleine Hinweise ohne Handlungsbedarf.
- 16:10 EXP-095 festgelegt (README, design, analyze; Selbsttest grün).
- 16:06 Trainer-Option `--pre-switch-grad-every` gebaut, Test zuerst geschrieben, alle 8 Trainer-Tests grün.
- 16:02 Repro-Kette (Rest) gestartet.
- 16:00 Start: kein STOP, keine Prozesse, Fenster bis 18:00.

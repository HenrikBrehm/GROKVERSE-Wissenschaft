---
id: P3-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-056-overlap-persistence/README|EXP-056]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[JOURNAL]]"]
---
# P3-Bestätigung (Persistenz, Paket B): Skelett (Sitzung 21, 2026-09-27 04:53 Berlin). **NICHT festgelegt**

Zurück zu [[FINDINGS]]. Die Hypothese und die Stichprobe hängen am Piloten [[experiments/EXP-056-overlap-persistence/README|EXP-056]]. Dieses Skelett legt nur fest, was
**unabhängig vom Pilotausgang** gilt. Alles andere wird erst nach dem Piloten entschieden und dann als „bereits gesehen“ vermerkt.

- **Seeds:** 1050–1099 (reserviert, nie benutzt), Split-Ströme wie EXP-053 (`SeedSequence`), aber mit einem **anderen Salz** als EXP-056, damit kein Pilot-Split wiederkehrt.
- **Konstruktion:** EXP-053 `overlap_split` (gleiche Steuerstärke je Stufe), gemeinsame Testmenge je Seed; Wechsel bei t = 25; Budget 2000 Schritte nach dem Wechsel; GPU.
- **Maß:** π wie EXP-056 (log-Verhältnis der Zielleistung in W_E, normiert zwischen den reinen Läufen), in beiden Richtungen gemittelt.
- **Kandidaten für die Kernaussage (Auswahl nach EXP-056, vor jedem P3-Lauf):**
  (a) *Festlegung ohne geteilte Daten:* π(ω = 0) > Mindesteffekt (eine Persistenz, die ohne gemeinsame Paare entsteht, kann nur im Netz liegen);
  (b) *Überlappung trägt:* Steigung von π über ω > 0.
- **Familie:** Holm im ungünstigsten Fall über P1–P3 wie P1/P2; P3 ersetzt dort den Platzhalter p = 1.
- **Einfrieren:** eigener Manifest-Commit mit Code-Hashes (derselbe Mechanismus wie P1: `confirm_p1.py --run`-Bindung), Codex-Prüfung vorher (Regel 18c).

## Entwurf der Festlegung (Sitzung 21, 05:01 Berlin, nach EXP-056; noch nicht eingefroren)

- **Aussage P3:** Nach nur 25 Schritten auf einem konstruierten Split A hält das Netz einen Teil der A-Frequenzwahl gegen 2000 Schritte auf einem Split B mit
  **null geteilten Paaren** fest, und zwar deutlich mehr, als eine passive Gewichtsspur der 25 Schritte erklären kann. (Richtung: Festlegung im Netz, Konkurrenzmodell (i).)
- **Primär:** je Seed D_s = π_s(ω = 0) − π_Spur,s(c = 1). π wie EXP-056 (beide Richtungen gemittelt); π_Spur mit der Rechnung aus EXP-056 „Post hoc“ mit c = 1 (obere Grenze, kein Zerfall).
  Einseitiger t-Test D̄ > 0; Holm im ungünstigsten Fall über P1–P3 (3p). **„bestätigt“ = alle 30 Seeds gültig, Holm-p < 0.05 und untere Grenze des 95-%-Bootstrap-KI von D̄ ≥ 0.05.**
- **Seeds:** 1050–1079 (30; 1080–1099 bleiben reserviert). Splits: EXP-053 `overlap_split.build` (gleicher Salz-Strom, Seeds disjunkt zu Kalibrierung 900–909 und Pilot 400–409), ε aus `calibration.json`.
- **Läufe je Seed:** ω = 0: nur A, nur B, A→B, B→A (t = 25, danach 2000). Sekundär ω = 0.4 mit denselben vier Armen (Δπ = π(0.4) − π(0) beschreibend mit KI; keine Entscheidung). 240 Läufe, GPU, 1 Thread.
- **Gültig:** alle Läufe der Stufe ok (gemeinsamer Lader + Bindung an den eingefrorenen Code wie P1), L(A) > L(B). Fehlt ein Seed für ω = 0: *nicht auswertbar*.
- **Stichprobe:** Pilot EXP-056 (bereits gesehen, post hoc): D̄ = 0.25, SD 0.14, d_z 1.8 (n = 10). Bootstrap-Power für „KI-Untergrenze ≥ 0.1“ war bei n = 30 und 60 % Effekt nur 0.56.
  Deshalb ist der Mindesteffekt 0.05 über der großzügigen Spurgrenze: Bei 60 % Effekt liegt die Untergrenze dann erwartet bei ≈ 0.10.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-020, EXP-044 (Wechselzeitpunkt t = 25), EXP-056 samt Spur-Rechnung (Wahl der Aussage (a) statt der Steigung,
  Maß D, Mindesteffekt, n), EXP-038 (Deutung). Seeds 1050–1099 wurden nie benutzt.
- **Umsetzung (geplant):** eigenes Modul `lab/tools/confirm_p3.py` mit eigenem Manifest `lab/confirm/P3_manifest.json`, eigener Code-Hash-Liste, eigenem Rohordner und eigenen
  Bindungen. Der P1-Code wird **nicht** geändert, weil der laufende P1-Block an seine Hashes gebunden ist. Die Laufverzeichnisse werden exakt aus dem Befehl bestimmt (die
  Wechselläufe enthalten den Stamm beider Splits). Codex-Prüfung vor dem Einfrieren.

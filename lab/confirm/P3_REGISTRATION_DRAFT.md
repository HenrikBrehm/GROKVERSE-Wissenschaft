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

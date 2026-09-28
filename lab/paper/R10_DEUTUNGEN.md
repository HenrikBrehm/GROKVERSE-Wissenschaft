---
id: r10-deutungen
status: vorab
datum: 2026-09-28
tags: [lab/paper]
verwandt: ["[[confirm/R10_REGISTRATION_DRAFT]]", "[[paper/draft_short]]", "[[paper/L0_DEUTUNGEN]]", "[[experiments/EXP-095-gradient-feedback/README|EXP-095]]"]
---
# R10: Deutungssätze je Ausgang, VOR dem Ergebnis festgelegt (Sitzung 45, 21:57 Berlin)

Zurück: [[paper/STATUS]] · Registrierung: [[confirm/R10_REGISTRATION_DRAFT|R10]] (eingefroren 7b583bdb). Zum Zeitpunkt dieser Notiz sind 268/480 Läufe gebunden, **kein Ergebnis angesehen**. Ort im Paper: Anhang D („Uhr der Festlegung“), nicht im Haupttext (Regel 20a). Nach der Auswertung nur Zahlen einsetzen; jede Abweichung vom Wortlaut im JOURNAL begründen.

**Feste Einschränkungen, gelten für jeden Ausgang (aus Fassung 2 der Registrierung und EXP-095 Nachtrag b):**
- H1/H3 messen „weniger Gradientenauswertungen unter Adam“. Das umfasst die fast vorzeichenartigen Schritte bei eingefrorenem Gradienten, die größere Bewegung und den Adam-Zustand beim Wechsel. Sie trennen **nicht** „frische Richtungsinformation“ von „Vorzeichenabstieg“ (post hoc erklärt Binarisieren ≈ 56 % der Zielanteil-Lücke im Piloten). Kein Satz im Paper darf sagen, die Festlegung „brauche Rückkopplung“ im Sinn einer Richtungsinformation.
- H2 eng: „g8 und c8b äquivalent innerhalb ±0.05 trotz verschiedenem Adam-Zähler nach dem Wechsel“, nicht „der grobe Schritt fügt nichts hinzu“.
- Eine Aufgabe (add 113), eine Architektur, Pilotseeds sind keine Bestätigung.

| Ausgang | Satz (Englisch, Anhang D) |
|---|---|
| H1, H2, H3 bestätigt | “With 24 Adam steps held fixed, fewer gradient evaluations along the path gave weaker persistence (e₈ = … [… , …], e₂₄ = … [… , …]; n = 48), and coarsening to 3 evaluations was equivalent within ±0.05 to 3 large steps despite the different Adam counter after the switch (r₈ = …). This is a property of Adam with stale gradients, which includes near-sign steps; it does not isolate fresh directional information.” |
| H1 und H3 bestätigt, H2 nicht | wie oben, zweiter Halbsatz ersetzt durch: “Equivalence of 3 evaluations and 3 large steps was not shown (r₈ = … [… , …]); the counter difference after the switch confounds this contrast.” |
| nur H3 bestätigt | “Only the extreme contrast held: with a single gradient evaluation, persistence was lower (e₂₄ = …); three evaluations were not distinguishable from 24 (e₈ = … [… , …]). The pilot effect for three evaluations did not replicate at the registered threshold.” |
| nur H2 bestätigt / keine | “The pilot finding that the lock-in needs re-evaluated gradients (EXP-095) did not replicate on 48 fresh seeds (e₈ = … [… , …], e₂₄ = … [… , …]). We report the pilot as not confirmed.” Kein Umdeuten zu „Richtung stimmt“. |
| H1 bestätigt, H3 nicht | unerwartet (H3 ist der stärkere Kontrast im Piloten): Zahlen berichten, Satz „inconsistent pattern; not interpreted“, Ursache im JOURNAL prüfen (Technik vor Inhalt). |

**Technisch nicht auswertbar** (Ausfälle über der Registrierungsgrenze, Code-Tor verweigert): so berichten, keine Teilauswertung als Befund.

---
id: N28-registrierung
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]", "[[experiments/EXP-058-optim-part/README|EXP-058]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[confirm/P3_REGISTRATION_DRAFT|P3]]", "[[confirm/P2b_REGISTRATION|P2b]]", "[[JOURNAL]]"]
---
# N28-Bestätigung (Programm B, Mechanismus der Persistenz): Registrierung (Sitzung 22). **ENTWURF, nicht eingefroren**

Zurück zu [[FINDINGS]] · Piloten [[experiments/EXP-058-optim-part/README|EXP-058]], [[experiments/EXP-059-momentum-exposure/README|EXP-059]] · [[NOVEL_DIRECTIONS]] N28 · Familie mit [[confirm/P2b_REGISTRATION|P2b]].

- **Aufbau (wie P3, ω = 0):** frische Seeds **2200–2229** (n = 30), EXP-053-Splits (paar-disjunkt, gleiche Steuerstärke), add 113, GPU, `--threads 1`.
  Je Seed: nur A, nur B (2000 Schritte); A→B und B→A mit Wechsel bei t und danach 2000 Schritten für die Arme
  **normal@25** (AdamW-Zustand bleibt), **m@25** (`--reset-optim-part m`: exp_avg beim Wechsel auf 0, exp_avg_sq und Schrittzähler bleiben), **m@35** und **normal@50** (beschreibend).
  Alle mit `--log-update-norms 10`. 10 Läufe je Seed, 300 Läufe.
- **Maß:** π wie P3/EXP-056 (Mittel von π_AB und π_BA aus dem Log-Energieverhältnis der A- gegen B-Ziele in W_E am Ende). Seed gültig: alle 10 Läufe gebunden und geladen,
  Reset im Lauf geprüft, L(A) − L(B) ≥ 2.
- **H1:** Δ_m = π_normal@25 − π_m@25 > 0 (Löschen nur des ersten Moments senkt die Persistenz). Mindesteffekt 0.05.
- **H2 (nach EXP-059, Nichtunterlegenheit):** π_m@35 − π_normal@25 > −0.05. Zehn zusätzliche gewöhnliche A-Schritte mit gelöschtem m erreichen mindestens die Persistenz des normalen
  Wechsels bei 25 (Marge 0.05). Geprüft als X = π_m@35 − π_normal@25 + 0.05 > 0 mit Mindesteffekt 0 (KI-Untergrenze ≥ 0). **Lesart:** H1 und H2 zusammen heißen, dass das
  Momentum beim Wechsel wie verlängerte A-Exposition wirkt (Konkurrenzmodell M2 aus EXP-059), nicht wie ein eigenes Gedächtnis.
  Pilot EXP-059: D = +0.059, SD 0.062, also X̄ ≈ 0.11 (n = 10); bei n = 30 praktisch sichere Power.
- **Beschreibend:** π_normal@50 (EXP-059: 1.05, d. h. nach 50 A-Schritten volle Festlegung gegen 2000 B-Schritte), Verschiebung δ, frühe Update-Normen.
- **Test:** je Hypothese einseitiger t-Test, Holm in der Familie Sitzung 22 {N28-H1, N28-H2, P2b} (P2b als p = 1), 95-%-Bootstrap-KI.
  „bestätigt“ = alle 30 Seeds gültig, Holm-p < 0.05 und KI-Untergrenze ≥ Mindesteffekt. Fehlt ein Seed: *nicht auswertbar*.
- **Stichprobe:** EXP-058: Δ_m 0.186, SD 0.098 (n = 10, bekannte Seeds). Bei n = 30 liegt die erwartete KI-Untergrenze bei ≈ 0.15, weit über 0.05; die Power für H1 ist praktisch 1.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-056/057/058/059 an den Seeds 400–409 (Wahl der Arme, t = 25/35, Mindesteffekt, n). P3-Daten (Seeds 1050–1079).
  Vor der Registrierung wurde kein Lauf mit Seeds 2200–2229 gemacht.
- **Herkunft und Ausfälle (Codex-Punkte aus der P2b-Prüfung, übertragen):** Splits werden in der Auswertung aus `overlap_split.build` neu gebaut und müssen exakt übereinstimmen,
  sonst ist die Bestätigung ungültig. Jeder fehlende oder defekte Lauf macht den Seed ungültig, und „bestätigt“ verlangt alle 30 Seeds. Gebunden werden nur Läufe mit Status „completed“.
- **Technik:** `lab/tools/confirm_n28.py` auf `lab/tools/bound_block.py`. Selbsttest ok, ungetestet am echten Lauf.

---
id: N28-registrierung
status: eingefroren
datum: 2026-09-27
tags: [lab/bestaetigung]
verwandt: ["[[FINDINGS]]", "[[NOVEL_DIRECTIONS]]", "[[experiments/EXP-058-optim-part/README|EXP-058]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[confirm/P3_REGISTRATION_DRAFT|P3]]", "[[confirm/P2b_REGISTRATION|P2b]]", "[[JOURNAL]]"]
---
# N28-Bestätigung (Programm B, Mechanismus der Persistenz): Registrierung (Sitzung 22). **EINGEFROREN**

Zurück zu [[FINDINGS]] · Piloten [[experiments/EXP-058-optim-part/README|EXP-058]], [[experiments/EXP-059-momentum-exposure/README|EXP-059]] · [[NOVEL_DIRECTIONS]] N28 · Familie mit [[confirm/P2b_REGISTRATION|P2b]].

- **Aufbau (wie P3, ω = 0):** frische Seeds **2200–2229** (n = 30), EXP-053-Splits (paar-disjunkt, gleiche Steuerstärke), add 113, GPU, `--threads 1`.
  Je Seed: nur A, nur B (2000 Schritte); A→B und B→A mit Wechsel bei t und danach 2000 Schritten für die Arme
  **normal@25** (AdamW-Zustand bleibt), **m@25** (`--reset-optim-part m`: exp_avg beim Wechsel auf 0, exp_avg_sq und Schrittzähler bleiben), **m@35** und **normal@50** (beschreibend).
  Alle mit `--log-update-norms 10`. 10 Läufe je Seed, 300 Läufe.
- **Maß:** π wie P3/EXP-056 (Mittel von π_AB und π_BA aus dem Log-Energieverhältnis der A- gegen B-Ziele in W_E am Ende). Seed gültig: alle 10 Läufe gebunden und geladen,
  Reset im Lauf geprüft, L(A) − L(B) ≥ 2.
- **H1:** Δ_m = π_normal@25 − π_m@25 > 0.05 (Löschen nur des ersten Moments senkt die Persistenz um mehr als 0.05). Geprüft als Y = Δ_m − 0.05 > 0 (t-Test und Holm auf Y, KI-Untergrenze von Y ≥ 0).
- **H2 (nach EXP-059, Nichtunterlegenheit):** π_m@35 − π_normal@25 > −0.05. Zehn zusätzliche gewöhnliche A-Schritte mit gelöschtem m erreichen mindestens die Persistenz des normalen
  Wechsels bei 25 (Marge 0.05). Geprüft als X = π_m@35 − π_normal@25 + 0.05 > 0 mit Mindesteffekt 0 (KI-Untergrenze ≥ 0). **Lesart (enger nach Codex):** H1 und H2 zusammen heißen: Das Löschen von m senkt
  die Persistenz, und zehn zusätzliche gewöhnliche A-Schritte gleichen das innerhalb der Marge aus. Das ist **vereinbar mit** verlängerter Exposition (M2) und durch sie ersetzbar,
  schließt aber einen optimiererspezifischen Mechanismus nicht aus.
  Pilot EXP-059: D = +0.059, SD 0.062, also X̄ ≈ 0.11 (n = 10); bei n = 30 praktisch sichere Power.
- **Beschreibend (einzige weitere Ausgabe):** π je Arm, darunter π_normal@50 (EXP-059: 1.05, d. h. volle Festlegung nach 50 A-Schritten). δ und Update-Normen werden nicht ausgewertet (Codex: im Code nicht festgelegt, zu wenige Arme für eine δ-Kurve).
- **Test:** je Hypothese einseitiger t-Test auf die Kontrastgröße mit eingebauter Marge (Y bzw. X), Holm in der Familie Sitzung 22 {N28-H1, N28-H2, P2b} (P2b als p = 1), 95-%-Bootstrap-KI.
  „bestätigt“ = alle 30 Seeds gültig, Holm-p < 0.05 und KI-Untergrenze der Kontrastgröße ≥ 0. Fehlt ein Seed: *nicht auswertbar*.
- **Stichprobe:** EXP-058: Δ_m 0.186, SD 0.098 (n = 10, bekannte Seeds). Bei n = 30 liegt die erwartete KI-Untergrenze bei ≈ 0.15, weit über 0.05; die Power für H1 ist praktisch 1.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** EXP-056/057/058/059 an den Seeds 400–409 (Wahl der Arme, t = 25/35, Mindesteffekt, n). P3-Daten (Seeds 1050–1079).
  Vor der Registrierung wurde kein Lauf mit Seeds 2200–2229 gemacht.
- **Herkunft und Ausfälle (Codex-Punkte aus der P2b-Prüfung, übertragen):** Splits werden in der Auswertung aus `overlap_split.build` neu gebaut und müssen exakt übereinstimmen,
  sonst ist die Bestätigung ungültig. Jeder fehlende oder defekte Lauf macht den Seed ungültig, und „bestätigt“ verlangt alle 30 Seeds. Gebunden werden nur Läufe mit Status „completed“.
- **Technik:** `lab/tools/confirm_n28.py` auf `lab/tools/bound_block.py`. Selbsttest ok, ungetestet am echten Lauf.

## Codex-Prüfung (Sitzung 22, gegen 089faa0), übernommen

Blocker: H1 wurde mit Holm auf Δ > 0 geprüft, die Marge 0.05 stand nur im KI-Tor. Jetzt trägt die getestete Größe die Marge (Y = Δ_m − 0.05), wie bei H2. Hoch: Die Lesart war zu stark;
jetzt „vereinbar mit / ersetzbar durch verlängerte Exposition“. Mittel: δ und Update-Normen waren versprochen, aber nicht festgelegt, und sind gestrichen. P2b-Korrekturen von Codex als erledigt bestätigt;
die P2b-Power-Empfindlichkeit bleibt ein offen berichtetes, bewusst hingenommenes Risiko.

## EINGEFROREN (Sitzung 22, 2026-09-27, 07:31–07:34 Berlin, gemessen)

Manifest `lab/confirm/N28_manifest.json`, **Manifest-Commit fa154bd** (Commit-Feld in 888c2d9), Code-Hashes über `confirm_n28.py`, `bound_block.py`, Trainer und Helfer.
Splits und Jobliste in 37448f6; die Herkunftsprüfung (`split_mismatch`) ist an den geschriebenen Dateien für alle Seeds bestanden. Vor dem Einfrieren wurde kein Lauf mit diesen Seeds gemacht.
Ein Job der Liste lief um 07:33 als Smoke (Seed 2200, A→B, m@25): Exit 0, 5 Dateien gebunden. Er zählt als regulärer Lauf des Blocks.
Start des Blocks 07:34 (GPU, `parallel_queue.py lab/confirm/N28_jobs.txt --workers 5`, parallel zum anderen Block der Familie).

## ERGEBNIS (Sitzung 22, Block 07:33–08:31, Auswertung 08:31 Berlin; `lab/confirm/N28_summary.json`): H1 und H2 ***bestätigt***

300/300 Läufe gebunden, 30/30 Seeds gültig, Herkunft aller Splits geprüft.
- **H1 bestätigt:** Y = Δ_m − 0.05 im Mittel 0.101 (95-%-KI [0.077, 0.126]), Holm-p 2·10⁻⁸, 29/30 > 0. Also Δ_m = π_normal@25 − π_m@25 ≈ 0.15 (π 0.340 gegen 0.189).
- **H2 bestätigt:** X = π_m@35 − π_normal@25 + 0.05 im Mittel 0.120 (KI [0.090, 0.152]), Holm-p 3·10⁻⁸, 29/30 > 0. π_m@35 = 0.410 ≥ π_normal@25 = 0.340.
- **Beschreibend:** π_normal@50 = 0.998 (volle Festlegung nach 50 Schritten auch an frischen Seeds).
- **Vorab festgelegte Vorhersage (2bdfdaf, außerhalb der Familie):** ***zwei Regime bestätigt*** — V1 Koexistenz bei t = 25 in 29/30 (a25 2.24 > b25 0.36), V2 Ausschluss bei t = 50 in 30/30
  (b50 − b25 im Mittel 3.44; b50 = 3.80). `lab/confirm/N28_regimes_summary.json`.
- Die Familie Sitzung 22 wurde mit P2b/P2c als p = 1 (ungünstigster Fall) ausgewertet; das Urteil hängt davon nicht ab.

---
id: EXP-013
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-012-init-gradient/README|EXP-012]]", "[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]"]
---
# EXP-013: Lock-in-Kurve der ersten 300 Schritte (explorativ)

**Status:** vorbereitet, Definition fixiert 2026-09-26 ~03:20 Berlin (Sitzung 4). **Rein explorativ und
beschreibend**, kein Hypothesentest mit Entscheidungsregel.

**Auslöser:** [[experiments/EXP-012-init-gradient/README|EXP-012]] Phase 1: Der erste Gradient (r̄ 0.30) sagt K
besser voraus als die Init (0.375), aber bei Schritt 250 ist K schon fast vollständig im Spektrum (Seed 10).
Wann genau zwischen 0 und 250 wird K ablesbar, und läuft das Gradientenspektrum dem Gewichtsspektrum voraus?

| | |
|---|---|
| **Seeds** | 0–9 (gespeicherte Läufe, K = `k_final` bei 25k aus EXP-009); Seed 10 als Übereinstimmungsprüfung mit der EXP-003d-Baseline |
| **Lauf** | identisch zum Training (`arch25k`, AdamW, Full-Batch, 4 Threads), nur 300 Schritte, kein Eingriff |
| **Messung pro Schritt t ∈ {0, 1, 2, 3, 5, 10, 15, 25, 50, 75, 100, 150, 200, 250, 300}** | r̄_E(t): Rang von K im Leistungsspektrum von W_E[:p] nach t Schritten · r̄_G(t): Rang von K im Leistungsspektrum des Gradienten an W_E[:p] bei Schritt t · ov_E(t), ov_G(t): Überlappung der Top-5 mit K |
| **Beschreibende Erwartung** | r̄_G(t) < r̄_E(t) für kleine t (Gradient läuft voraus); ov_E(250) ≥ 3 im Median |
| **Gültigkeit** | Init bitgleich mit `ckpt_step000000.pt`; für Seed 10 muss W_E-Spektrum bei 250 mit `spectra.npy` der EXP-003d-Baseline übereinstimmen (rtol 1e-4) |
| **Budget** | 11 × 300 Schritte × 0.13 s ≈ 7 min, ein Job, nach den Paar-Läufen der Sitzung |

---
id: P4-registrierung-entwurf
status: entwurf
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, lab/paper]
verwandt: ["[[paper/STATUS]]", "[[FINDINGS]]", "[[experiments/EXP-045-mlp-steering/README|EXP-045]]", "[[experiments/EXP-048-intadd-steering/README|EXP-048]]", "[[experiments/EXP-049-width-steering/README|EXP-049]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]"]
---
# P4-Bestätigung (Regel 19b): K2 in der MLP-Architektur, bei 4× Breite und für nicht-modulare Addition. **ENTWURF, nicht eingefroren, kein Code**

Zurück zu [[paper/STATUS]]. Entwurf Sitzung 24 (2026-09-27), vor jedem P4-Lauf. Ziel: die drei Piloten (je 10 bekannte Seeds, alle *steuerbar*, p ≈ 0.001) an frischen Seeds bestätigen,
damit sie im Paper als Ergebnisse statt als Piloten stehen können.

- **Familie (Holm über 3):** H4a MLP (`--arch mlp`, add 113), H4b Breite d = 512 (add 113), H4c Integer-Addition a + b (EXP-048-Konstruktion, trendbereinigtes Maß).
- **Maß:** Δ_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] der W_E-Leistung (wie P1 bzw. EXP-048/049), einseitiger t-Test über Seeds, 95-%-Bootstrap-KI.
  Zeitpunkt: 2000 Schritte (H4b, H4c wie die Piloten); H4a: der Pilot maß Top-5 bei 10 000 Schritten, hier Δ_pow bei 2000 **und** 10 000 (primär 10 000, damit der Endzustand nach dem Grokking zählt).
- **Mindesteffekt:** Δ_pow ≥ 1 (wie P1). **Urteil je Hypothese:** Holm-p < 0.05 und KI-Untergrenze ≥ 1 → bestätigt; technischer Ausfall → nicht auswertbar (zählt mit p = 1).
- **Stichprobe aus Pilotstreuung (nachgerechnet Sitzung 24 aus den Pilot-`rows`):** MLP Top-5-Δ 7.9 ± 0.57 (Δ_pow im Piloten nicht berechnet), d = 512 Δ_pow 7.82 ± 1.60 (Minimum 5.29),
  Integer-Addition Δ_pow 2.23 ± 0.27 (Minimum 1.95), je n = 10 (SD mit ddof 1). Gegen den Mindesteffekt 1 standardisierte Abstände ≈ 4.3 (Breite) bzw. 4.6 (Integer); einseitig, α = 0.05/3 (Holm, schlimmster Fall),
  Power ≈ 1 schon bei n = 10. **Gewählt n = 15 je Bedingung** als Reserve gegen eine Abschwächung an frischen Seeds und für die MLP-Umstellung auf Δ_pow. 3 × 15 × 2 = 90 Läufe (MLP bis 10 000 Schritte).
- **Seeds:** frischer Block (z. B. 2360–2419), Versuchs-ID 7, vor jeder Nutzung in [[FINDINGS_DETAILS]] reservieren.
- **Code (fehlt):** `lab/tools/confirm_p4.py` nach dem Muster `confirm_p2e.py` (Bindung, Manifest, Selbsttest mit End-zu-End-Maß), Split-Konstruktion aus `confirm_splits` (add 113) bzw. EXP-048
  `make_split` mit neuen Strömen; Codex-Prüfung vor dem Einfrieren (Regel 18c). GPU-Budget ≈ 40 min.
- **Bereits gesehene Daten:** die drei Piloten (Seeds 90–99, 160–169, 170–179); davon beeinflusst: Maß, Zeitpunkte, Wahl der drei Bedingungen.

## Technische Bestandsaufnahme für `confirm_p4.py` (Sitzung 24, 14:1x, nur gelesen)

| Bedingung | Trainer | Run-ID | Splits | Maß im Piloten |
|---|---|---|---|---|
| H4a MLP | `freq_ban.py --arch mlp` (Fingerabdruck, Sperre, `--save-model`) | `EXP-045_baseline_seed<s>_thr1_<stem>_mlp_devcuda` | EXP-043-Konstruktion → hier `confirm_splits.build` (add 113) mit neuer Versuchs-ID | Top-5-Δ bei 10 000 |
| H4b d = 512 | `lab/experiments/EXP-049-width-steering/width_train.py --d-model 512` (eigener schlanker Trainer, trainer_guard) | `EXP-049_d512_seed<s>_<stem>_dev<dev>` | EXP-049 `make_split.py` → hier `confirm_splits.build` (add 113) | Δ_pow bei 2000 |
| H4c Integer-Addition | `lab/experiments/EXP-048-intadd-steering/intadd_train.py` (eigener Trainer, Ausgabe 225) | `EXP-048_seed<s>_<stem>_dev<dev>` | EXP-048 `make_split.py` (eigene Ströme `SeedSequence([48001, seed, arm, purpose])`, Ziele aus 6..56) → Ströme um eine Versuchs-ID erweitern, ohne die Pilotdatei zu ändern | trendbereinigtes Δ_pow bei 2000 (EXP-048 Nachtrag a) |

Offene Punkte: Das trendbereinigte Maß aus EXP-048 `analyze.py` wiederverwenden (Datei in die Hash-Liste); für H4a Δ_pow statt Top-5 als Primärgröße (vorab so festgelegt); alle Arme GPU.


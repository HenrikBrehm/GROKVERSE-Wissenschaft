---
id: P4-registrierung-entwurf
status: abgeschlossen
datum: 2026-09-27
tags: [lab/bestaetigung, exp/abgeschlossen, befund/positiv, lab/paper]
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

## Technische Bestandsaufnahme für `confirm_p4.py` (Sitzung 24, 14:10, nur gelesen)

| Bedingung | Trainer | Run-ID | Splits | Maß im Piloten |
|---|---|---|---|---|
| H4a MLP | `freq_ban.py --arch mlp` (Fingerabdruck, Sperre, `--save-model`) | `EXP-045_baseline_seed<s>_thr1_<stem>_mlp_devcuda` | EXP-043-Konstruktion → hier `confirm_splits.build` (add 113) mit neuer Versuchs-ID | Top-5-Δ bei 10 000 |
| H4b d = 512 | `lab/experiments/EXP-049-width-steering/width_train.py --d-model 512` (eigener schlanker Trainer, trainer_guard) | `EXP-049_d512_seed<s>_<stem>_dev<dev>` | EXP-049 `make_split.py` → hier `confirm_splits.build` (add 113) | Δ_pow bei 2000 |
| H4c Integer-Addition | `lab/experiments/EXP-048-intadd-steering/intadd_train.py` (eigener Trainer, Ausgabe 225) | `EXP-048_seed<s>_<stem>_dev<dev>` | EXP-048 `make_split.py` (eigene Ströme `SeedSequence([48001, seed, arm, purpose])`, Ziele aus 6..56) → Ströme um eine Versuchs-ID erweitern, ohne die Pilotdatei zu ändern | trendbereinigtes Δ_pow bei 2000 (EXP-048 Nachtrag a) |

Offene Punkte: Das trendbereinigte Maß aus EXP-048 `analyze.py` wiederverwenden (Datei in die Hash-Liste); für H4a Δ_pow statt Top-5 als Primärgröße (vorab so festgelegt); alle Arme GPU.

## Nachtrag Sitzung 25 (2026-09-27, ≈ 14:24 Berlin gemessen, vor jedem P4-Lauf): Code geschrieben, Pilot-Δ_pow der MLP nachgerechnet

- **Code:** `lab/tools/confirm_p4.py` (Muster `confirm_r1.py`/`bound_block.py`: Manifest-Bindung, Code-Hashes aller drei Trainer, Sperre gegen Überschreiben der Splits,
  deterministischer Nachbau der Splits vor der Auswertung, gemeinsamer Ergebnislader). **Ungetestet** (Selbsttest erst im Fenster ab 00:00), Codex-Prüfung vor dem Einfrieren.
- **Splits:** mlp und d512: P1-Konstruktion `confirm_splits.build` mit Versuchs-ID 7 (add 113, ε = 2); intadd: EXP-048-Konstruktion mit Strömen
  `SeedSequence([48001, 7, Seed, Arm, Zweck])` (Pilot: `[48001, Seed, Arm, Zweck]`); der Selbsttest prüft, dass die Funktion mit dem Pilotstrom die Pilot-Splits exakt nachbaut.
- **Seeds:** **2360–2419** reserviert (Block), davon 3 × 15 = 45 genutzt, je Bedingung disjunkt; genaue Liste im Manifest. Versuchs-ID 7.
- **Läufe:** 90 (mlp 30 × 10 000 Schritte mit `--stop-after-gen 100000`, d512 30 × 2000, intadd 30 × 2000), alle GPU, `--threads 1`.
- **Pilot-Δ_pow der MLP (post hoc aus den gespeicherten EXP-045-Spektren, Seeds 90–99, Sitzung 25):** bei 10 000 Schritten 7.68 ± 2.51 (Minimum 3.49, 10/10 > 1), bei 2000
  Schritten 2.45 ± 0.15. Standardisierter Abstand zum Mindesteffekt bei 10 000: (7.68 − 1)/2.51 = 2.7 → Power bei n = 15, einseitig α = 0.05/3, praktisch 1. n = 15 bleibt.
- **Sekundär (nur berichtet):** mlp Δ_pow bei 2000; intadd Δ_pow am rohen Spektrum und lineares R²; Median der Test-Genauigkeit, Anzahl generalisierter Arme.

- **Codex-Prüfung Sitzung 25 ([[confirm/P4_codex_review_s25.txt]]), umgesetzt vor dem Einfrieren:** *Blocker:* Oben steht „einseitiger t-Test“, der Code rechnet wie P1 den **exakten
  einseitigen Vorzeichen-Permutationstest** (2^15 Vorzeichen). **Registriert wird der exakte Vorzeichentest** (wie P1: unter H0 ist Δ_pow je Seed symmetrisch um 0, weil F und G nur
  vertauschte Rollen haben; keine Normalverteilungsannahme); die Angabe „t-Test“ oben ist damit ersetzt. Der Code prüft p = 1/2^15 für 15 positive Werte. *Kleinere Punkte:* Kopfzeile
  „kein Code“ und „Code (fehlt)“ sind durch diesen Nachtrag überholt; `--save-model` (Tabelle, H4a) wird **nicht** gesetzt, P4 braucht kein Modell (width/intadd kennen die Option
  nicht); die Sperre gegen Überschreiben prüft jetzt `.npy` und `.json` vorab; der Selbsttest vergleicht Pilot- und P4-Strom am selben Seed. Nicht umgesetzt: ein synthetischer
  Ergebnisordner je Trainer im Selbsttest (die echten Pilot-Ergebnisfelder wurden von mir und Codex gegen `Expect` geprüft; der Smoke vor dem Block prüft den Lader an einem echten Lauf).

- **Eingefroren (Sitzung 37, 2026-09-28, Berlin):** Selbsttest grün (Sitzung 37), Codex-Prüfung Sitzung 25 umgesetzt (oben). Manifest `lab/confirm/P4_manifest.json` (Entwurf ohne Notiz + `code_sha256`), Commit-ID im Feld `commit`. Das C3-Code-Tor liegt vor diesem Commit. Bereits gesehene Daten: wie oben (Piloten EXP-045/048/049); kein Lauf mit den P4-Seeds vor dem Einfrieren.

## Ergebnis (Sitzung 38, 2026-09-28, 06:21 Berlin gemessen; Block 90/90 ok, GPU, 05:55–06:19; `--analyze` über den Wächter, `P4_summary.json`, Log `P4_block_s38.log`/`P4_analyze_s38.log`)

**Alle drei Hypothesen *bestätigt*** (Holm über 3, je n = 15, 0 technische Ausfälle, je 15/15 positiv, Holm-p 9.2·10⁻⁵ = kleinster möglicher Wert des Tests):
- **H4a MLP** (geteiltes Embedding, Δ_pow bei 10 000): **8.89** [7.86, 9.84]; bei 2000 (sekundär) 2.35; 30/30 Arme generalisiert (Median-Test 1.0).
- **H4b Transformer d = 512** (Δ_pow bei 2000): **7.84** [7.23, 8.38]; 30/30 Arme generalisiert.
- **H4c Integer-Addition** (trendbereinigtes Δ_pow bei 2000): **2.35** [2.05, 2.72]; roh (sekundär) 2.24. **Keiner** der 30 Arme generalisiert (Median-Test 0.26): Die Steuerung der W_E-Frequenzen gilt hier ohne Generalisierung innerhalb von 2000 Schritten.
Alle KI-Untergrenzen liegen weit über dem Mindesteffekt 1; die Piloten (MLP 7.68 bei 10 000, Breite und Integer ≈ 2.2–2.5 laut Pilot) haben sich übertragen.
**C3** (eigene Familie, an denselben Läufen, Tor vor dem Manifest): Die Zielrangfolge in W_E bei 2000 folgt dem Maskenspektrum, S = **0.30** [0.20, 0.40], p = 5·10⁻⁶, bereinigt 0.30 [0.19, 0.40] → ***bestätigt*** (MLP 0.27, d512 0.31, Integer 0.32; Init-Korrelation beschreibend 0.17; `C3_summary.json`).

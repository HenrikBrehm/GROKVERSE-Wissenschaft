---
id: C4-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/A, programm/C]
verwandt: ["[[FINDINGS]]", "[[confirm/P2f_REGISTRATION|P2f]]", "[[confirm/C1_REGISTRATION|C1]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# C4: Folgt bei D₅₉ die Rangfolge der Ziel-Irreps auch nach dem Grokking dem Masken-Spektrum? (Programm A/C)

Zurück zu [[FINDINGS]] · Datenquelle: [[confirm/P2f_REGISTRATION|P2f]] (frische Seeds 2340–2359, 12 000 Schritte, noch **kein** Lauf, Manifest noch nicht eingefroren). Registriert Sitzung 28, 2026-09-27,
Statistik wie [[confirm/C1_REGISTRATION|C1]] Fassung 2b (Codex-geprüft; gleiche Aggregation mit einer Zelle). Gilt mit dem Commit dieser Datei und dem Code-Tor `C4_manifest.json`.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- P1 D₅₉ (50 Seeds, Schritt 2000, vor dem Grokking): mittlere Rangkorrelation je Arm (Masken-Spektrum M0, Irrep-Energie) 0.43 (`P1_posthoc_within.json`).
- Pilot EXP-072 (Seeds 1000–1004 = P1-Splits, 20 000 Schritte; Test ≥ 0.9 im Median bei 4575 Schritten): 0.56 (Schritt 250) … 0.58 (10 000) … 0.48 (20 000), positiv in 8–10 von 10 Armen (`EXP072_posthoc_time.json`).
- **Davon beeinflusst:** Zeitpunkt 12 000 (P2f-Ende, nach dem Grokking), Prädiktor M0 (für D₅₉ gibt es kein kohärentes Gegenstück), Mindesteffekt 0.10.

## Aussage C4 (eng)

Bei D₅₉ (Ein-Schicht-Transformer) folgt **bei Schritt 12 000** die Rangfolge der fünf vorgegebenen Ziel-Irreps in der W_E-Energie der Rangfolge ihrer Energie im
Masken-Spektrum des Splits, auch nach Bereinigung um den Irrep-Index und den Init-Rang. Korrelation, kein Mechanismus. Ob die Läufe dann generalisiert haben, ist **keine Bedingung**; die Zahl der generalisierten Arme (`generalization_step` ≤ 12 000) wird beschreibend berichtet, und nur wenn die Mehrheit generalisiert hat, wird das Ergebnis im Paper als „nach dem Grokking“ bezeichnet.

## Daten, Maß, Test (fest)

- **Daten:** alle 40 P2f-Läufe über die P2f-Bindung (hash → load → hash, Split-Bytes gebunden), Irrep-Spektrum (`spectra.npy`) bei Schritt 12 000 und Schritt 0.
- **Maß, Einheit, Statistik, Schwellen:** wie C1 Fassung 2b, eine Zelle: Spearman je Arm; Einheit Seed (Mittel F/G, beide gültig; Bindungen → Arm technisch); bestätigt = Vorzeichen-Permutation
  p < 0.05 **und** Bootstrap-KI-Untergrenze ≥ 0.10 **und** KI-Untergrenze des bereinigten Koeffizienten (Maske | Irrep-Index, Init) > 0; nicht auswertbar mit weniger als 10 von 20 Seeds.
  Eigene Familie (eine Hypothese), nicht in der P2f-Familie; P2f selbst (Funktionsmaß, S1) bleibt unverändert.
- **Power (grob):** Pilot ≈ 0.5, SD je Seed ≈ 0.3 angenommen → n = 20: SE ≈ 0.07, erwartete Untergrenze ≈ 0.36; bei halbem Effekt ≈ 0.11 (knapp).
- **Was dagegen spräche:** Mittel ≤ 0, Untergrenze < 0.10 oder bereinigter Koeffizient nicht > 0.

## Umsetzung und Code-Tor

`lab/confirm/C4_analyze.py` (nutzt `C1_analyze.aggregate`, `rank_tools.py`); Hashes in `C4_manifest.json`; letzter Commit von Tor und Registrierung muss ein Vorfahr des P2f-Manifest-Commits sein.
Selbsttest (nur im Fenster): reproduziert den EXP-072-Wert bei Schritt 10 000 (0.58) über dieselbe Blockfunktion. **Ungetestet.** Wird P2f geändert, muss C4 neu registriert werden.

## Codex-Prüfung (Sitzung 28, `C4_codex_review_s28.txt`)

Kein Blocker. Übernommen: MAJOR (Aussage „nach dem Grokking der meisten Läufe“ ungeprüft) → Aussage auf Schritt 12 000 beschränkt, Generalisierung beschreibend berichtet (siehe oben). MINOR (Selbsttest umgeht Lader und Bindung) als bekannte Grenze dokumentiert: Die Ladekette prüft der Pflicht-Smoke von P2f, Ladefehler zählen als technisch. Bestätigt: Schritt 0/12 000 im Spektrum, gleiche Irrep-Indizierung wie `mask_power` und die Ziele, `Expect` passt zum P2f-Lauf, Aggregation mit einer Zelle.

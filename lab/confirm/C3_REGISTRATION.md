---
id: C3-registrierung
status: registriert
datum: 2026-09-27
tags: [lab/bestaetigung, exp/vorbereitet, programm/A, programm/C]
verwandt: ["[[FINDINGS]]", "[[confirm/P4_REGISTRATION_DRAFT|P4]]", "[[confirm/C1_REGISTRATION|C1]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# C3: Ordnet das Masken-Spektrum die Ziele auch im MLP, bei 4× Breite und bei nicht-modularer Addition? (Programm A/C, Verallgemeinerung von C1)

Zurück zu [[FINDINGS]] · Datenquelle: [[confirm/P4_REGISTRATION_DRAFT|P4]] (frische Seeds aus 2360–2419, noch **kein** Lauf, Manifest noch nicht eingefroren). Registriert Sitzung 28, 2026-09-27,
mit derselben Statistik wie [[confirm/C1_REGISTRATION|C1]] Fassung 2b (Codex-geprüft; die Punkte gelten sinngemäß). Gilt mit dem Commit dieser Datei und dem Code-Tor `C3_manifest.json`.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

- Piloten (je 10 Seeds, für K2 gesehen, für die Rangfolge nicht): `lab/confirm/A_posthoc_within.py` → `A_posthoc_within.json`: mittlere Rangkorrelation je Arm bei Schritt 2000 zwischen Masken-Spektrum
  und W_E-Energie der Ziele: 4× Breite (d512) M0c 0.30 (p 0.009), M0 0.31, Init −0.01; d128-Kontrolle M0c 0.31; Integer-Addition (eigenes M0) 0.29 trendbereinigt / 0.36 roh, Init 0.11–0.12;
  MLP (`EXP045_posthoc_within.py`) M0c 0.60, M0 0.46, Init nicht gerechnet; bei 10 000 Schritten verblasst (0.17/0.20).
- **Davon beeinflusst:** Schritt 2000 für alle drei Bedingungen (beim MLP ist 10 000 der P4-Primärzeitpunkt, dort ist die Ordnung verblasst → hier bewusst 2000, Wahl nach Ansicht der Piloten);
  Prädiktor M0c für MLP und d512 (beim MLP besser als M0, entgegen der Theorie-Vorhersage 2), eigenes M0 für die Integer-Addition (kein kohärentes Gegenstück implementiert).

## Aussage C3 (eng)

Im gleich gewichteten Mittel über drei Bedingungen (MLP mit geteiltem Embedding, Transformer mit d = 512, Integer-Addition a + b) folgt die Rangfolge der fünf vorgegebenen Ziele in der W_E-Energie
nach 2000 Schritten der Rangfolge ihrer Energie im Masken-Spektrum des Splits, auch nach Bereinigung um k und den Init-Rang. Keine Aussage je Bedingung (beschreibend berichtet); Korrelation, kein Mechanismus.

## Daten, Maß, Test (fest)

- **Daten:** alle 90 P4-Läufe über den eingefrorenen P4-Lader (`confirm_p4.spectra`): Energie bei Schritt 2000 (MLP: `secondary`, d512: `primary`, Integer: `primary` = trendbereinigte DFT von W_E, wie P4);
  Schritt 0 über einen zweiten vollständigen Ladevorgang desselben Laufs (`spectra.npy`). Fehlt Schritt 0 oder gibt es Bindungen → Arm technisch.
  **Integer-Addition (Codex s28):** Die Init-Kontrolle ist dort das **rohe** Spektrum bei Schritt 0 (der Trainer speichert W_E bei Schritt 0 nicht), die Zielgröße ist trendbereinigt. Das ist eine bewusst andere Kontrolle; „bereinigt um den Init-Rang“ heißt für diese Bedingung „um den rohen Init-Rang“. Eine trendbereinigte Init-Kontrolle ist nicht möglich und wird nicht behauptet.
- **Maß, Einheit, Statistik, Schwellen:** wie C1 Fassung 2b (Spearman je Arm; Einheit Seed = Mittel F/G, beide gültig; gleich gewichtetes Mittel der Bedingungsmittel; bestätigt = Vorzeichen-Permutation p < 0.05
  **und** geschichtete Bootstrap-KI-Untergrenze ≥ 0.10 **und** KI-Untergrenze des bereinigten Koeffizienten (Maske | k, Init) > 0; nicht auswertbar, wenn eine Bedingung < 10 von 15 Seeds hat).
  Code: `C1_analyze.aggregate`. Eigene Familie (eine Hypothese), nicht in der P4-Holm-Familie.
- **Power (grob):** Pilotmittel 0.30–0.60 → gleich gewichtet ≈ 0.4; bei SD je Seed ≈ 0.3 und n = 45 SE ≈ 0.045 → erwartete Untergrenze ≈ 0.3; bei halbiertem Effekt ≈ 0.11 (knapp). Das Risiko eines „nicht bestätigt“ bei halbem Effekt ist damit real und wird so berichtet.
- **Beschreibend:** Bedingungsmittel, mittlere Init-Korrelation, fehlende Seeds mit Schranke (ρ = −1).
- **Was dagegen spräche:** Mittel ≤ 0, Untergrenze < 0.10 oder bereinigter Koeffizient nicht > 0.

## Umsetzung und Code-Tor

`lab/confirm/C3_analyze.py` (nutzt `C1_analyze.aggregate`, `rank_tools.py`, `P1_posthoc_within.py`); Hashes in `C3_manifest.json`; letzter Commit von Tor und Registrierung muss ein Vorfahr des P4-Manifest-Commits sein.
Selbsttest (nur im Fenster): Masken-Spektren je Bedingung, Pilotwert der Integer-Addition (0.36) reproduziert. Wird P4 geändert (Seeds, Schritte, Bedingungen), muss C3 neu registriert werden. **Ungetestet.**

## Codex-Prüfung (Sitzung 28, `C3_codex_review_s28.txt`)

Kein Blocker. Übernommen: MAJOR (rohe Init-Kontrolle bei trendbereinigter Zielgröße) als ausdrücklich andere Kontrolle registriert und die Deutung eingeengt, statt den Trainer zu ändern (P4-Code ist Codex-geprüft; eine Trainer-Änderung vor dem Einfrieren wäre ein neuer Prüfpunkt). MINOR: Selbsttest prüft zusätzlich den trendbereinigten Pilotwert (0.285). Bestätigt von Codex: alle Trainer speichern Schritt 0 und 2000, `secondary` = Schritt 2000 beim MLP, gleiche k-Indizierung, `dataclasses.replace` gültig.

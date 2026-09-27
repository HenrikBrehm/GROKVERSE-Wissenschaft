---
id: R4
status: entwurf
datum: 2026-09-27
tags: [lab/confirm, programm/A, paper, exp/vorbereitet]
---
# R4: Formt ein gewöhnlicher Zufallssplit die gelernten Frequenzen? (gekreuztes Init × Split-Design): Registrierungsentwurf

Zurück: [[LAB]] · [[FINDINGS]] (Programm A, K2) · [[paper/STATUS]] · Pilot: [[experiments/EXP-014-split-vs-init/README|EXP-014]] · Vorgänger (Assoziation): [[experiments/EXP-015-mask-spectrum/README|EXP-015]] · [[JOURNAL]] Sitzung 30.

**Status:** Entwurf, Sitzung 30 (2026-09-27, vor 18:35 Berlin, gemessen), **vor jedem R4-Lauf und vor dem EXP-014-Pilot**. Code `lab/tools/confirm_r4.py`, **ungetestet**. Nicht eingefroren: vor dem Einfrieren Selbsttest im Fenster und Codex-Prüfung (Regel 18c, „vor Einfrieren eines Programms“), danach Manifest mit Commit-ID.

## Warum

Gutachter-Einwand O1 zum [[paper/draft]]: Alle bestätigten Steuerbefunde (K2) nutzen **konstruierte** Splits (Gewichte 0.05–3). Offen ist, ob schon ein **gewöhnlicher** 30-%-Zufallssplit mitbestimmt, welche der gleich guten Frequenzen ein Netz lernt. EXP-015 zeigt dafür nur eine Assoziation, bei der Split und Init aus gleich geseedeten Generatoren stammen; EXP-014 (heute Nacht, CPU) ist ein Pilot mit 5 Einheiten (kleinstes p = 1/32). R4 ist die ausreichend große Bestätigung mit unabhängigen Zufallsströmen.

## Aufbau

- add 113, 1-Schicht-Transformer (arch25k), AdamW lr 1e-3, wd 1, 30 % der Paare (3831), `freq_ban.py --split-file`, Test = Komplement (Standard), GPU, `--threads 1`, 2000 Schritte, `--stop-after-gen 2000`, Spektren bei 250, 1000, 2000.
- **Einheit u** (n_u Einheiten): zwei Inits (Seeds 2600 + 2u, 2601 + 2u) × zwei Zufallssplits (s1, s2) = 4 Läufe, alle Kombinationen. Splits: `numpy.random.default_rng(SeedSequence([R4_TAG, u, j]))`, gleichverteilte Auswahl von 3831 der 12 769 Paare, ohne Bezug zu Frequenzen; kein Split wird mit einem Init-Seed gezogen (Regel 18a6).
- **Maß:** W_E-Leistungsspektrum (k = 1..56, `spectra.npy`) bei Schritt 2000. Ähnlichkeit sim(x, y) = Spearman über die 56 Frequenzen.
  Je Einheit: S_split = Mittel der zwei Paare mit gleichem Split und verschiedener Init; S_init = Mittel der zwei Paare mit gleicher Init und verschiedenem Split; S_none = Mittel der zwei Paare ohne Gemeinsamkeit.
- **Hypothesen (Holm über 2, einseitig, t-Test auf Δ − MDE, 95-%-Bootstrap-KI; „bestätigt“ = Holm-p < 0.05 und KI-Untergrenze von Δ − MDE ≥ 0):**
  - **H1 (Hauptfrage):** Δ_split = S_split − S_none > MDE. Ein Zufallssplit formt das gelernte Spektrum über den Zufall hinaus.
  - **H2:** Δ_init = S_init − S_none > MDE. Die Init formt es (Vergleichsgröße zu H1; erwartet nach He et al. 2026a und EXP-009).
- **MDE = 0.05** (Spearman-Differenz; kleinster Effekt, der im Paper als „formt mit“ berichtet würde).
- **Beschreibend (kein Urteil):** Δ_split − Δ_init mit KI (welcher Faktor stärker ist); dasselbe bei 250 und 1000 Schritten; Top-5-Überlappung als Gegenprobe; Anteil generalisierter Läufe (Test ≥ 0.9 bei 2000).
- **Stichprobe (fest):** n_u = 40 Einheiten (160 Läufe; Init-Seeds 2600–2679 reserviert). Keine Anpassung nach dem Pilot. `lab/confirm/R4_pilot_n.py` berichtet nach EXP-014 nur beschreibend die erwartete Power für einen wahren Effekt Δ_split = 0.10 (0.05 über MDE, α = 0.025 einseitig, Holm-Ungünstigstfall); liegt sie unter 80 %, wird R4 im Paper als gering gepowert für diese Effektgröße gekennzeichnet. (Ein erster Entwurf mit Wahl n = 30/40 nach dem Pilot wurde vor jedem Lauf verworfen: unnötiger Freiheitsgrad.)
- **Gültigkeit:** Alle 4 Läufe einer Einheit gebunden, geladen (gemeinsamer Lader), Spektren bei 250/1000/2000 endlich, Split-Hash = Split-Datei. Fehlt ein Lauf oder ist er defekt: ganzes R4 *nicht auswertbar* (wie N29/R3).
- **Budget:** 160 Läufe × 2000 Schritte, GPU ≈ 0.03 s/Schritt bei 10 parallel → ≈ 35 min.

## Was dagegen spräche

- H1 nicht bestätigt, KI von Δ_split eng um 0: Ein gewöhnlicher Zufallssplit formt die Frequenzwahl (bei 2000 Schritten) nicht messbar mit; die Steuerung braucht konstruierte Paarstruktur. Das wäre ein eigener Befund fürs Paper (Abgrenzung zu EXP-015, dann Seed-Kopplung als Erklärung der Assoziation).
- H2 nicht bestätigt: widerspräche EXP-009/He et al.; eher Messproblem, im JOURNAL prüfen, nicht umdeuten.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-015 (Seeds 0–19, Assoziation Maske ↔ Frequenzen, Seed-Kopplung), EXP-014 Gradient-Vorschau (Seeds 0–9, erster Gradient folgt dem Split: ρ 0.34 gegen −0.01), EXP-009 (Init-Spektrum sagt Frequenzen voraus). Beeinflusst: Wahl des Designs (gekreuzt), Spearman als kontinuierliches Maß, einseitige Richtung, Schritt 2000 (wie P1). Kein Lauf mit Seeds 2600–2679, kein R4-Split existiert. Der EXP-014-Pilot ändert an R4 nichts (nur Power-Bericht).

## Grenzen (vorab)

Eine Aufgabe (add 113), eine Architektur, eine Optimierer-Einstellung; Spearman über alle 56 Frequenzen gewichtet schwache Frequenzen mit; „formt mit“ ist nicht „entscheidet allein“; kein Eingriff in den Mechanismus.

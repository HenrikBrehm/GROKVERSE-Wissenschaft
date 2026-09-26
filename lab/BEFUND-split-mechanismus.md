---
id: BEFUND-split-mechanismus
status: explorativ
datum: 2026-09-26
tags: [befund/positiv, befund/unklar, neu/kandidat]
verwandt: ["[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-019-coherent-mask/README|EXP-019]]", "[[experiments/EXP-021-harmonic-misses/README|EXP-021]]", "[[NOVEL_DIRECTIONS]]"]
---
# Befund: Wie der Trainingssplit die Frequenzen auswählt (Stand Sitzung 5)

Zurück zu [[LAB]] · Details im [[JOURNAL]] (Sitzung 5, Zyklen 4–16). **Fast alles hier ist post hoc und explorativ.**
Vorab festgelegt und bestätigt ist nur, was ausdrücklich so markiert ist.

## Was bestätigt ist (vorab festgelegt, frische Seeds)

- Das Masken-Spektrum M0 des Trainingssplits sagt die Rangfolge der gelernten W_E-Frequenzen voraus (Assoziation,
  [[experiments/EXP-015-mask-spectrum/README|EXP-015]], Seeds 10–17).
- Der erste Gradient an W_E sagt sie besser voraus als das Init-Spektrum ([[experiments/EXP-012-init-gradient/README|EXP-012]]).

## Mechanismus (Sitzung 5, post hoc, nach einem Codex-Angriff präzisiert)

1. **Beobachtung:** Das „kohärente“ Masken-Spektrum M0c (linke und rechte Eingabeposition vor dem Betragsquadrat
   addiert) beschreibt die Leistung des tatsächlichen ersten Gradienten besser als M0: ρ 0.77 gegen 0.57 (G0 über 3 Inits,
   10/10 Seeds).
2. **Direkt gemessen:** Zerlegt man den ersten Gradienten in den Beitrag der linken und der rechten Position, heben sich
   die Kreuzterme über alle Frequenzen **näherungsweise** auf (mittlere Kohärenz 0.01), **frequenzweise** folgen sie aber
   dem Kreuzterm der Maske M0c − M0 (ρ 0.50, 18/18 Seeds positiv; Kontrolle mit fremder Maske −0.09, nur Seeds 0–9).
3. **Geschlossene Form (numerisch exakt geprüft):** M0c(k) = 4 Σ_c |N̂(k, c)|² cos²(θ), θ = arg N̂(k, c) + πkc/p,
   M0 = 2 Σ_c |N̂|². Der Kreuzterm M0c − M0 = 2 Σ_c |N̂|² cos(2θ) misst, wie **spiegelsymmetrisch** (gleichphasig) das
   Paarmuster jeder Antidiagonale ist, also die Kommutations-**Symmetrie**: Für symmetrische Splits ist er maximal
   (= M0, also M0c = 2·M0), für Zufallssplits im Mittel ≈ 0. (Korrigiert nach Codex-Prüfung; vorher fälschlich
   „Asymmetrie“.)
4. **Architektur-Kontrast (Vorhersage vor der Rechnung, für den ersten Gradienten bestätigt, explorativ):** In der MLP mit
   gemeinsamem Embedding laufen die beiden Operanden durch verschiedene Hälften von W_in; dort folgt der Kreuzterm der
   Maske nicht (ρ 0.05), und M0 beschreibt den ersten Gradienten besser als M0c (0.37 gegen 0.24, 9/10 Seeds, p ≈ 0.003).
   Für die **finalen** Frequenzen ist der Unterschied nur beschreibend: r̄ 0.323 (M0) gegen 0.351 (M0c), 6/10 Seeds,
   p ≈ 0.21. Eine MLP-Konfiguration, 10 vorhandene Seeds. Im Transformer ist es umgekehrt.
5. **Eingriff (in silico, Vorhersage vorher):** Bekommt Position 1 im ersten Gradienten eine eigene Wertematrix W_V′,
   verschwindet die Interferenz (ρ 0.47 → −0.03; eigene W_O′: 0.07). Ursache ist also der geteilte Wertepfad der
   Attention. Nur für den ersten Gradienten gezeigt, nicht für die finale Wahl.
6. Ob M0c auch die **finalen** Frequenzen besser vorhersagt, ist offen: post hoc richtungsgleich, nicht signifikant;
   Bestätigung vorab festgelegt in [[experiments/EXP-019-coherent-mask/README|EXP-019]].

## Konstruierte Splits: frühe Prägung, spätere Verdrängung durch 2k (EXP-016, unvollständige Vorschau)

**Vorschau auf 6 von 10 Seeds (10–15, je Arm F und G), unter der vorab festgelegten Mindestzahl von 8; EXP-016 ist noch
nicht auswertbar.** F und G teilen je Seed die Init, die 12 Läufe sind also nicht unabhängig.
- Früh prägen die Daten die Frequenzen auf: W_E-Top-5 = Zielmenge bei Schritt 250 in 12/12 Läufen (frühester gemeinsamer
  Messpunkt); bei Schritt 50 nur in einem einzigen Smoke-Lauf gesehen.
- Bis Schritt 2000 werden einzelne Ziele verdrängt, und zwar die **früh schwächsten** (14/14 auf Rang 4–5 bei Schritt 250).
  Beschreibend, ohne Ursachenzuschreibung: Unter den verdrängten Zielen stehen viele auch in der Maske (M0) weit hinten
  (Rang 4–5 in 10/14) und etwas weniger im Init-Spektrum (9/14, p ≈ 0.06).
- Alle 14 verdrängenden Frequenzen sind **zweite Harmonische fold(2k)** einer Zielfrequenz desselben Arms (Muster erst beim
  Lesen gefunden; Bestätigung vorab festgelegt in [[experiments/EXP-021-harmonic-misses/README|EXP-021]]).

## Was die 2k-Komponenten sind (Studienmodelle, Seeds 0–9, gemischtes Bild)

- Auch unter Zufallssplits enthält die W_E-Top-5 gehäuft (k, 2k)-Paare, die ausgangsseitigen Schlüsselfrequenzen der
  Studie (Regel `nanda`, W_L) aber nicht.
- Ablation: Die schwächeren 2k-Glieder sind in 8/8 Paaren das unwichtigste Top-5-Glied, aber nicht bedeutungslos.
- Phasenkopplung ψ = 2φ (Oberwelle einer gemeinsamen Wellenform) nur in 3/10 Paaren deutlich.
- Sie erreichen die Top-5 meist erst nach dem Grokking (5/8 Paare).
- **Einordnung:** „nachrangige, teils phasengekoppelte 2k-Komponente“; die Deutung „reine Oberwelle“ ist nicht belegt.

## Negativ (ebenfalls Sitzung 5)

- Zwischen der natürlichen Konzentration des Masken-Spektrums eines Zufallssplits und der Grokking-Zeit wurde **kein
  belastbarer Zusammenhang** nachgewiesen (Transformer Seeds 0–9: ρ −0.40, p 0.25, in der vermuteten Richtung; MLP ρ +0.15;
  Baselines 10–17 ρ +0.02; sehr enger Wertebereich 0.1015–0.1088).
- Eine oberwellen-bereinigte K bringt **keine statistisch belastbare Verbesserung** (M0c r̄ 0.254 → 0.254, p 0.48;
  M0 0.294 → 0.292).
- Die Fehlgriffe in EXP-016 liegen weder in M0c noch im Init-Spektrum vorn.

## Einordnung in die Literatur (vorläufig)

Die Idee „die Trainingsstichprobe erzeugt Frequenzen, die das Netz zuerst lernt“ ist in anderer Form bekannt
(Zhou, Zhang, Xu 2024, Frequency Principle, Regression/Parität/MNIST). Auch bei festem Split variiert die Frequenzwahl mit
der Init (GitHub-Nachbau von Nanda et al.). Nicht gefunden (Suche vom 2026-09-26): die Z_p-Masken-Statistik M0/M0c, ihre
Positions-Interferenz und die kausale Steuerung durch konstruierte Splits. Siehe [[NOVEL_DIRECTIONS]] N3, N6, N8.

## Offene Tests (vorbereitet, nicht ausgeführt)

[[experiments/EXP-014-split-vs-init/README|EXP-014]] (Split × Init gekreuzt) ·
[[experiments/EXP-018-split-speed/README|EXP-018]] (beschleunigt Konzentration das Grokking?) ·
[[experiments/EXP-019-coherent-mask/README|EXP-019]] · [[experiments/EXP-020-data-switch/README|EXP-020]]
(kausale Festlegungszeit) · [[experiments/EXP-021-harmonic-misses/README|EXP-021]] ·
[[experiments/EXP-022-single-frequency/README|EXP-022]] (Ein-Frequenz-Lösung per Datenauswahl?)
